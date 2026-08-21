#!/usr/bin/env python3
"""
Capex Cycle Watch — data fetcher.

Pulls the automatable sensors from three free, key-less public sources:

  SEC EDGAR (data.sec.gov)   capex, operating cash flow, revenue per company
  FRED      (stlouisfed.org) credit spreads, semiconductor PPI, consumer hardware CPI
  Vast.ai   (console.vast.ai) live GPU rental market: price and depth

Writes data.js (consumed by index.html via <script src>, so the dashboard works
from file:// without a web server) and appends a daily row to history.json so
sources without their own history — the GPU market — build a trend over time.

Standard library only. No API keys, no pip install.
"""

import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
# The Mac fetches and owns history.json and data.js; the cloud routine only
# rescores what it finds. One history, one writer, nothing to merge.
HISTORY_FILE = os.environ.get("CAPEX_HISTORY", "history.json")
# SEC EDGAR refuses requests (403) unless the User-Agent carries a deliverable
# contact address — a URL or a noreply address is not enough, both were tested.
# The address therefore comes from the environment and is never committed: it
# is set in run.sh on the Mac and in the cloud routine's configuration.
CONTACT = os.environ.get("CAPEX_CONTACT", "").strip()
UA = f"capex-watch/1.0 ({CONTACT})" if CONTACT else "capex-watch/1.0"
TODAY = datetime.now(timezone.utc).date().isoformat()

# EDGAR asks for a descriptive User-Agent and <=10 req/s. We use far less.
COMPANIES = [
    ("MSFT",  789019, "Microsoft"),
    ("AMZN", 1018724, "Amazon"),
    ("GOOGL", 1652044, "Alphabet"),
    ("META", 1326801, "Meta"),
    ("ORCL", 1341439, "Oracle"),
    ("NVDA", 1045810, "Nvidia"),
]
# Filers move between XBRL tags over the years — Amazon's capex and Nvidia's
# revenue both changed tag. Each concept is therefore a candidate list, and the
# tag with the most recent quarterly data point wins.
TAGS_CAPEX = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsToAcquireProductiveAssets",
    "PaymentsToAcquirePropertyPlantAndEquipmentExcludingCapitalizedInterest",
]
TAGS_OCF = [
    "NetCashProvidedByUsedInOperatingActivities",
    "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
]
TAGS_REV = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
]

FRED_SERIES = {
    # High Yield Option-Adjusted Spread — credit stress, daily.
    "hy_oas": "BAMLH0A0HYM2",
    # PPI: semiconductor and related device manufacturing — component price pressure.
    "semi_ppi": "PCU3344133441",
    # CPI: personal computers and peripheral equipment — where the squeeze reaches a household.
    "pc_cpi": "CUSR0000SEEE01",
    # Industrial production: semiconductors and electronic components — physical capacity.
    "semi_ip": "IPG3344S",
}

# Current-generation accelerators. Last-generation prices are deliberately excluded:
# cheap old silicon is the value cascade working, not demand failing (Rule 04).
GPUS_CURRENT = ["H200", "B200", "H100 SXM"]


# --------------------------------------------------------------------------
# plumbing
# --------------------------------------------------------------------------

def get(url, headers=None, tries=3, timeout=60):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:                              # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))
    raise RuntimeError("unreachable")


def days(a, b):
    return (datetime.fromisoformat(b).date() - datetime.fromisoformat(a).date()).days


def pct(new, old):
    if old in (None, 0) or new is None:
        return None
    return (new - old) / abs(old) * 100.0


# --------------------------------------------------------------------------
# EDGAR
# --------------------------------------------------------------------------

def quarterly(facts):
    """
    Turn EDGAR duration facts into a discrete quarterly series.

    Cash-flow items in 10-Qs are usually year-to-date, so a Q3 filing carries a
    nine-month number. Anything longer than a quarter is differenced against the
    longest earlier period that shares its start date.
    """
    periods = {}
    for f in facts:
        s, e, v = f.get("start"), f.get("end"), f.get("val")
        if not s or not e or v is None:
            continue
        # Later filings restate: keep the most recently accepted value.
        key = (s, e)
        prev = periods.get(key)
        if prev is None or f.get("accn", "") > prev.get("accn", ""):
            periods[key] = f

    out = {}
    for (s, e), f in periods.items():
        d = days(s, e)
        if 80 <= d <= 100:                                   # already a quarter
            out[e] = f["val"]
        elif d > 100:                                        # year-to-date: difference it
            earlier = [(ee, ff) for (ss, ee), ff in periods.items()
                       if ss == s and ee < e and 80 <= days(ss, ee)]
            if not earlier:
                continue
            ee, ff = max(earlier, key=lambda x: x[0])
            if 80 <= days(ee, e) <= 100:
                out.setdefault(e, f["val"] - ff["val"])
    return [(e, out[e]) for e in sorted(out)]


def concept(cik, tags):
    """Best quarterly series across candidate tags — most recent data point wins."""
    best, best_tag = [], None
    for tag in tags:
        url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{tag}.json"
        try:
            d = json.loads(get(url, tries=2))
        except Exception:                                    # noqa: BLE001
            continue                                          # tag not used by this filer
        time.sleep(0.2)
        q = quarterly(d.get("units", {}).get("USD", []))
        if q and (not best or q[-1][0] > best[-1][0]):
            best, best_tag = q, tag
    return best, best_tag


def ttm(series, back=0):
    """Trailing twelve months ending `back` quarters ago."""
    end = len(series) - back
    if end < 4:
        return None
    return sum(v for _, v in series[end - 4:end])


def edgar():
    if not CONTACT:
        raise RuntimeError(
            "CAPEX_CONTACT is not set. SEC EDGAR returns 403 without a contact "
            "address in the User-Agent, so the four filing-derived sensors "
            "(A1, A2, A3, D3) cannot be read. Set CAPEX_CONTACT to an email "
            "address before running.")
    rows = []
    for ticker, cik, name in COMPANIES:
        try:
            capex, t_capex = concept(cik, TAGS_CAPEX)
            ocf, _ = concept(cik, TAGS_OCF)
            rev, t_rev = concept(cik, TAGS_REV)
            time.sleep(0.3)                                  # be polite to EDGAR
        except Exception as e:                               # noqa: BLE001
            rows.append({"ticker": ticker, "name": name, "error": str(e)})
            continue

        c0, c4 = ttm(capex), ttm(capex, 4)
        o0, o4 = ttm(ocf), ttm(ocf, 4)
        r0, r4 = ttm(rev), ttm(rev, 4)
        c1, o1 = ttm(capex, 1), ttm(ocf, 1)

        asof = capex[-1][0] if capex else None
        # A filer whose newest quarter is more than two quarters old has not been
        # parsed correctly, whatever the reason. Better to drop it from the
        # medians than to let a 2017 number vote on 2026.
        stale = (not asof) or days(asof, TODAY) > 200

        rows.append({
            "ticker": ticker,
            "name": name,
            "asof": asof,
            "stale": stale,
            "tags": {"capex": t_capex, "revenue": t_rev},
            "capex_ttm": c0,
            "ocf_ttm": o0,
            "rev_ttm": r0,
            # A2 — the funding ratio. Absolute capex rises until the very top;
            # the share of it the business itself pays for turns earlier.
            "capex_ocf": (c0 / o0 * 100) if c0 and o0 else None,
            "capex_ocf_prev": (c1 / o1 * 100) if c1 and o1 else None,
            "capex_growth": pct(c0, c4),
            "rev_growth": pct(r0, r4),
            # D3 — the coverage gap, at company level, for the last three
            # quarters, so the "three consecutive quarters" rule can be tested
            # rather than asserted. Total revenue is a proxy for AI revenue and
            # overstates the gap: the non-AI business dilutes the growth rate.
            "coverage_gap": (pct(c0, c4) - pct(r0, r4)) if (c0 and c4 and r0 and r4) else None,
            "coverage_gap_hist": [
                (pct(ttm(capex, b), ttm(capex, b + 4)) - pct(ttm(rev, b), ttm(rev, b + 4)))
                if (ttm(capex, b) and ttm(capex, b + 4) and ttm(rev, b) and ttm(rev, b + 4))
                else None
                for b in (0, 1, 2)
            ],
            "rev_q": [{"end": e, "val": v} for e, v in rev[-9:]],
            "capex_q": [{"end": e, "val": v} for e, v in capex[-9:]],
        })
    return rows


# --------------------------------------------------------------------------
# FRED
# --------------------------------------------------------------------------

def fred(series_id):
    csv = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}")
    pts = []
    for line in csv.splitlines()[1:]:
        parts = line.split(",")
        if len(parts) < 2:
            continue
        d, v = parts[0], parts[1].strip()
        if v in (".", ""):
            continue
        try:
            pts.append({"d": d, "v": float(v)})
        except ValueError:
            continue
    return pts


def at_offset(pts, n):
    """Value n observations back from the end."""
    return pts[-1 - n]["v"] if len(pts) > n else None


def fred_all():
    out = {}
    for key, sid in FRED_SERIES.items():
        try:
            pts = fred(sid)
        except Exception as e:                               # noqa: BLE001
            out[key] = {"error": str(e), "series": sid}
            continue
        latest = pts[-1] if pts else None
        # Monthly series: 12 observations back is a year. Daily: ~252.
        step = 252 if key == "hy_oas" else 12
        half = 126 if key == "hy_oas" else 6
        out[key] = {
            "series": sid,
            "latest": latest,
            "yoy": pct(latest["v"], at_offset(pts, step)) if latest else None,
            "chg_6m": pct(latest["v"], at_offset(pts, half)) if latest else None,
            "abs_6m": (latest["v"] - at_offset(pts, half)) if latest and at_offset(pts, half) else None,
            "spark": [p["v"] for p in pts[-60:]],
            "spark_dates": [p["d"] for p in pts[-60:]],
            "n": len(pts),
        }
    return out


# --------------------------------------------------------------------------
# Vast.ai — live GPU rental market
# --------------------------------------------------------------------------

def vast(gpu):
    q = {"gpu_name": {"eq": gpu}, "rentable": {"eq": True},
         "num_gpus": {"eq": 1}, "order": [["dph_total", "asc"]], "limit": 200}
    url = "https://console.vast.ai/api/v0/bundles/?" + urllib.parse.urlencode({"q": json.dumps(q)})
    d = json.loads(get(url))
    offers = d.get("offers", [])
    prices = sorted(o["dph_total"] for o in offers if o.get("dph_total"))
    if not prices:
        return None
    return {
        "gpu": gpu,
        "offers": len(prices),
        "median": round(statistics.median(prices), 4),
        "p25": round(prices[len(prices) // 4], 4),
        "min": round(prices[0], 4),
    }


def gpu_market():
    out = []
    for g in GPUS_CURRENT:
        try:
            r = vast(g)
            if r:
                out.append(r)
        except Exception:                                     # noqa: BLE001
            continue
        time.sleep(0.3)
    return out


# --------------------------------------------------------------------------
# history — so the GPU market builds a trend of its own
# --------------------------------------------------------------------------

def load_history():
    try:
        with open(os.path.join(HERE, HISTORY_FILE)) as f:
            return json.load(f)
    except Exception:                                         # noqa: BLE001
        return []


def update_history(gpus, fredd, states=None):
    path = os.path.join(HERE, HISTORY_FILE)
    try:
        with open(path) as f:
            hist = json.load(f)
    except Exception:                                         # noqa: BLE001
        hist = []
    hist = [h for h in hist if h.get("date") != TODAY]
    hist.append({
        "date": TODAY,
        "gpu": {g["gpu"]: {"median": g["median"], "offers": g["offers"]} for g in gpus},
        "hy_oas": (fredd.get("hy_oas", {}).get("latest") or {}).get("v"),
        # Daily snapshot of every sensor state, so Rule 01 — a move counts only
        # once it has held for two readings — can be applied without anyone
        # having to remember to press a button.
        "states": states or {},
    })
    hist = hist[-800:]
    with open(path, "w") as f:
        json.dump(hist, f, indent=1)
    return hist


def gpu_trend(hist, gpu, back_days):
    """Change in median price and in offer depth, `back_days` ago vs now."""
    if not hist:
        return None
    now = hist[-1]
    if gpu not in now.get("gpu", {}):
        return None
    target = None
    for h in reversed(hist[:-1]):
        if days(h["date"], now["date"]) >= back_days and gpu in h.get("gpu", {}):
            target = h
            break
    if not target:
        return None
    return {
        "days": days(target["date"], now["date"]),
        "price": pct(now["gpu"][gpu]["median"], target["gpu"][gpu]["median"]),
        "offers": pct(now["gpu"][gpu]["offers"], target["gpu"][gpu]["offers"]),
    }


# --------------------------------------------------------------------------
# scoring — thresholds live here, in one place
# 0 = calm, 1 = watch, 2 = turning, None = no reading
# --------------------------------------------------------------------------

def score(companies, f, gpus, hist):
    s = {}

    # A2 — capex as a share of operating cash flow, across the five buyers.
    ratios = [c["capex_ocf"] for c in companies
              if c.get("capex_ocf") and not c.get("stale") and c["ticker"] != "NVDA"]
    prevs = [c["capex_ocf_prev"] for c in companies
             if c.get("capex_ocf_prev") and not c.get("stale") and c["ticker"] != "NVDA"]
    if ratios:
        med = statistics.median(ratios)
        medp = statistics.median(prevs) if prevs else None
        st = 0
        if med > 100 and medp and medp > 100:
            st = 2                                            # borrowed for two quarters running
        elif med >= 60:
            st = 1
        s["A2"] = {"state": st, "value": round(med, 1), "unit": "%",
                   "detail": f"median of {len(ratios)} hyperscalers, trailing twelve months"}

    # A1 — capex growth. Guidance itself is not machine-readable; realised
    # trailing-twelve-month growth is, and it is what guidance eventually becomes.
    gr = [c["capex_growth"] for c in companies
          if c.get("capex_growth") is not None and not c.get("stale") and c["ticker"] != "NVDA"]
    if gr:
        med = statistics.median(gr)
        st = 0 if med > 10 else (1 if med > -5 else 2)
        s["A1"] = {"state": st, "value": round(med, 1), "unit": "% YoY",
                   "detail": "median realised capex growth, trailing twelve months"}

    # A3 — Nvidia revenue, sequential.
    nv = next((c for c in companies if c["ticker"] == "NVDA"), None)
    if nv and not nv.get("stale") and len(nv.get("rev_q", [])) >= 3:
        q = [x["val"] for x in nv["rev_q"]]
        g1 = pct(q[-1], q[-2])
        g2 = pct(q[-2], q[-3])
        st = 2 if g1 is not None and g1 < 0 else (1 if (g1 is not None and g2 is not None and g1 < g2 and g1 < 5) else 0)
        s["A3"] = {"state": st, "value": round(g1, 1) if g1 is not None else None, "unit": "% QoQ",
                   "detail": f"prior quarter {round(g2,1) if g2 is not None else '—'}% — total revenue, the data-centre split needs the release itself"}

    # D3 — the coverage gap.
    gaps = [c["coverage_gap"] for c in companies
            if c.get("coverage_gap") is not None and not c.get("stale") and c["ticker"] != "NVDA"]
    if gaps:
        med = statistics.median(gaps)
        # Three-quarter persistence, tested rather than asserted: the gap must
        # have cleared the threshold in each of the last three quarters.
        persist = []
        for b in range(3):
            g = [c["coverage_gap_hist"][b] for c in companies
                 if not c.get("stale") and c["ticker"] != "NVDA"
                 and c.get("coverage_gap_hist") and c["coverage_gap_hist"][b] is not None]
            persist.append(statistics.median(g) if g else None)
        # Threshold raised from the card's +30pp because total revenue stands in
        # for AI revenue here and inflates the gap.
        red = all(p is not None and p > 50 for p in persist)
        st = 2 if red else (0 if med <= 0 else 1)
        s["D3"] = {"state": st, "value": round(med, 1), "unit": "pp",
                   "detail": "median capex growth minus total revenue growth, trailing twelve months. "
                             "Prior two quarters: "
                             + ", ".join(f"{round(p,1)}pp" if p is not None else "—" for p in persist[1:])
                             + ". A proxy — total revenue dilutes AI revenue, so the true AI-level gap is smaller."}

    # C2 — credit. Level and six-month direction, in basis points.
    hy = f.get("hy_oas", {})
    if hy.get("latest"):
        lvl = hy["latest"]["v"]
        chg = (hy.get("abs_6m") or 0) * 100
        st = 0
        if lvl > 6.0 or chg > 150:
            st = 2
        elif lvl > 4.5 or chg > 50:
            st = 1
        s["C2"] = {"state": st, "value": round(lvl * 100), "unit": "bp",
                   "detail": f"US high-yield spread, {'+' if chg>=0 else ''}{round(chg)}bp over six months"}

    # B1 — the live GPU rental market: price and depth together.
    if gpus:
        lead = gpus[0]
        t30 = gpu_trend(hist, lead["gpu"], 30)
        if t30 is None:
            st, detail = None, f"{len(hist)} day(s) of history — a trend needs about a month"
            val = lead["median"]
        else:
            p, o = t30["price"], t30["offers"]
            st = 0
            if p < -25 and o > 0:
                st = 2                                        # cheaper while capacity grows
            elif p < -10:
                st = 1
            val = lead["median"]
            detail = f"{round(p,1)}% price and {round(o,1)}% supply depth over {t30['days']} days"
        s["B1"] = {"state": st, "value": val, "unit": f"$/hr {lead['gpu']}", "detail": detail}

    # D2 — consumer hardware prices. This index normally falls a few per cent a
    # year through quality adjustment, so flat is already pressure and rising is
    # the demand-destruction point.
    pcc = f.get("pc_cpi", {})
    if pcc.get("yoy") is not None:
        y = pcc["yoy"]
        st = 0 if y < 0 else (1 if y < 5 else 2)
        s["D2"] = {"state": st, "value": round(y, 1), "unit": "% YoY",
                   "detail": "CPI, personal computers and peripherals — this series normally declines"}

    # B4 — component price pressure, and the roll-over that ends it.
    pp = f.get("semi_ppi", {})
    if pp.get("yoy") is not None:
        y, m6 = pp["yoy"], pp.get("chg_6m")
        st = 0
        if y > 10 and m6 is not None and m6 < -2:
            st = 2                                            # squeeze rolling over
        elif y > 10:
            st = 1
        s["B4"] = {"state": st, "value": round(y, 1), "unit": "% YoY",
                   "detail": f"PPI semiconductors, six-month change {round(m6,1) if m6 is not None else '—'}% — a proxy; spot DRAM leads it"}

    return s


# --------------------------------------------------------------------------
# verdict — the reading rules, in one place
#
# These live here rather than in the page so there is exactly one
# implementation. The dashboard displays the verdict; it does not compute it.
# --------------------------------------------------------------------------

CLUSTER_MAP = [
    ("A", "Demand", ["A1", "A2", "A3", "A4"]),
    ("B", "Physical supply", ["B1", "B2", "B3", "B4"]),
    ("C", "Financing", ["C1", "C2", "C3", "C4"]),
    ("D", "The paying end", ["D1", "D2", "D3", "D4"]),
]
STAGE_NAMES = ["Expansion", "Friction", "Mismatch", "Reversal"]


def confirmed_states(states, hist):
    """
    Rule 01 — a move counts only once it has held about a month. Each sensor
    scores at the milder of today's reading and the reading ~30 days ago.
    """
    out, ready = {}, False
    past = None
    for h in reversed(hist[:-1]):
        if h.get("states") and days(h["date"], TODAY) >= 28:
            past, ready = h["states"], True
            break
    for sid, v in states.items():
        p = (past or {}).get(sid)
        out[sid] = min(v, p) if isinstance(p, int) else v
    return out, ready


def cluster_scores(states):
    """Rule 02 — a cluster turns on two reds, or one red plus two ambers."""
    out = []
    for _, _, ids in CLUSTER_MAP:
        vals = [states[i] for i in ids if i in states]
        if not vals:
            out.append(None)
            continue
        red = sum(1 for v in vals if v == 2)
        amber = sum(1 for v in vals if v == 1)
        out.append(2 if (red >= 2 or (red >= 1 and amber >= 2))
                   else 1 if (red >= 1 or amber >= 2) else 0)
    return out


def stage_from(scores):
    red = sum(1 for v in scores if v == 2)
    amber = sum(1 for v in scores if v == 1)
    stage = 3 if red >= 3 else 2 if red == 2 else 1 if (red == 1 or amber >= 3) else 0
    return stage, red, amber


def verdict(states, hist):
    conf, ready = confirmed_states(states, hist)
    cs = cluster_scores(conf)
    stage, red, amber = stage_from(cs)
    raw_stage, _, _ = stage_from(cluster_scores(states))
    return {
        "stage": stage,
        "stage_raw": raw_stage,
        "stage_name": STAGE_NAMES[stage],
        "clusters": [{"id": c, "name": n, "score": s}
                     for (c, n, _), s in zip(CLUSTER_MAP, cs)],
        "red": red,
        "amber": amber,
        "confirmed": conf,
        "confirmation_ready": ready,
        "history_days": len(hist),
    }


# --------------------------------------------------------------------------
# alerts — a board nobody opens is not a watch
# --------------------------------------------------------------------------

def alerts(states, prev_states, v, prev_stage, manual):
    """Everything worth interrupting someone for. Empty list is the normal case."""
    out = []
    if prev_stage is not None and v["stage"] != prev_stage:
        direction = "escalated to" if v["stage"] > prev_stage else "eased back to"
        out.append(f"STAGE {direction} 0{v['stage']+1} {v['stage_name']}")
    names = {"0": "calm", "1": "watch", "2": "turning"}
    for sid in sorted(states):
        old, new = prev_states.get(sid), states[sid]
        if isinstance(old, int) and old != new:
            arrow = "worsened" if new > old else "improved"
            out.append(f"{sid} {arrow}: {names[str(old)]} -> {names[str(new)]}")
    for k, m in manual.items():
        if k.startswith("_") or not isinstance(m, dict) or not m.get("asof"):
            continue
        if days(m["asof"], TODAY) > 45:
            out.append(f"{k} assessment is {days(m['asof'], TODAY)} days old — re-read it")
    return out


def load_previous():
    """Read back the last data.js. Used by --rescore, which never touches the network."""
    raw = open(os.path.join(HERE, "data.js")).read()
    raw = raw.split("window.CAPEX_DATA = ", 1)[1].split(";\nwindow.CAPEX_HISTORY")[0]
    return json.loads(raw)


def main():
    errors = []
    # --rescore recomputes states, verdict and alerts from the last fetch plus
    # the current manual.json, without a single network request. The cloud
    # routine runs in a sandbox whose egress proxy blocks all three data hosts,
    # so it rescores what the Mac fetched rather than fetching for itself.
    rescore = "--rescore" in sys.argv

    def guarded(fn, label, default):
        try:
            return fn()
        except Exception as e:                                # noqa: BLE001
            errors.append(f"{label}: {e}")
            return default

    if rescore:
        try:
            prev = load_previous()
        except Exception as e:                                # noqa: BLE001
            print(f"--rescore needs an existing data.js from a fetching run: {e}", file=sys.stderr)
            return 1
        companies, fredd, gpus = prev["companies"], prev["fred"], prev["gpus"]
        errors = list(prev.get("errors", []))
    else:
        companies = guarded(edgar, "sec-edgar", [])
        fredd = guarded(fred_all, "fred", {})
        gpus = guarded(gpu_market, "vast.ai", [])

    if rescore:
        hist = load_history()
    else:
        # First pass writes today's GPU prices so the trend used by B1 includes them.
        hist = update_history(gpus, fredd)
    auto = score(companies, fredd, gpus, hist)

    manual_path = os.path.join(HERE, "manual.json")
    try:
        with open(manual_path) as fh:
            manual = json.load(fh)
    except Exception:                                         # noqa: BLE001
        manual = {}

    states = {k: v["state"] for k, v in auto.items() if v.get("state") is not None}
    for k, v in manual.items():
        if not k.startswith("_") and isinstance(v, dict) and v.get("state") is not None:
            states[k] = v["state"]

    # Yesterday's picture, read before today's row overwrites it. A rescore
    # compares against today's own row instead: the point is to surface what the
    # manual edits just changed, not what happened overnight.
    if rescore:
        prev_row = hist[-1] if hist and hist[-1].get("states") else None
    else:
        prev_row = next((h for h in reversed(hist) if h["date"] != TODAY and h.get("states")), None)
    prev_states = (prev_row or {}).get("states", {})
    prev_stage = (prev_row or {}).get("stage")

    if not rescore:
        hist = update_history(gpus, fredd, states)
    v = verdict(states, hist)
    if hist:
        hist[-1]["states"] = states
        hist[-1]["stage"] = v["stage"]
    if not rescore:
        with open(os.path.join(HERE, HISTORY_FILE), "w") as fh:
            json.dump(hist, fh, indent=1)

    fired = alerts(states, prev_states, v, prev_stage, manual)
    with open(os.path.join(HERE, "alert.txt"), "w") as fh:
        fh.write("\n".join(fired))
    if fired:
        with open(os.path.join(HERE, "alerts.log"), "a") as fh:
            for line in fired:
                fh.write(f"{TODAY}  {line}\n")

    # Per-source failures are recorded inside fred/companies. Lift them to the
    # top level so the page's stamp shows a warning instead of rendering an
    # empty board that looks like a calm one. The published artifact did exactly
    # that once; hence this.
    for key, val in (fredd or {}).items():
        if isinstance(val, dict) and val.get("error"):
            errors.append(f"fred/{key}: {val['error']}")
    dead = [c["ticker"] for c in companies if c.get("stale") or c.get("error")]
    if dead:
        errors.append("sec-edgar: no usable filings for " + ", ".join(dead))
    if not gpus:
        errors.append("vast.ai: no GPU offers returned")
    if not auto:
        errors.append("NO AUTOMATIC SENSORS — the board is running on manual "
                      "assessments alone and must not be read as a verdict")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    payload = {
        "verdict": v,
        "alerts": fired,
        # A rescore did not generate new readings, so it keeps the original
        # stamp. Otherwise it dirties data.js in the cloud checkout for nothing,
        # and the page would claim data fresher than it is.
        "generated": prev["generated"] if rescore else now,
        "generated_date": prev["generated_date"] if rescore else TODAY,
        "auto": auto,
        "companies": companies,
        "fred": fredd,
        "gpus": gpus,
        "gpu_history": [{"date": h["date"], "gpu": h.get("gpu", {})} for h in hist[-120:]],
        # Context, not a scored sensor: the cross-check that tells you whether a
        # falling component price is demand dying or supply finally arriving.
        "context": {
            "semi_ip": fredd.get("semi_ip", {}),
            "gpu_all": gpus,
        },
        "manual": manual,
        "errors": errors,
    }

    # Two globals: the current reading, and the daily state snapshots the
    # dashboard needs to enforce Rule 01 without anyone pressing a button.
    state_hist = [{"date": h["date"], "states": h.get("states", {})}
                  for h in hist if h.get("states")]
    with open(os.path.join(HERE, "data.js"), "w") as fh:
        fh.write("window.CAPEX_DATA = ")
        json.dump(payload, fh, indent=1)
        fh.write(";\nwindow.CAPEX_HISTORY = ")
        json.dump(state_hist, fh, indent=1)
        fh.write(";\n")

    print(f"[{payload['generated']}]{' rescored ·' if rescore else ''} stage 0{v['stage'] + 1} {v['stage_name']} · "
          f"{len(auto)} automatic sensors, {len(companies)} filers, "
          f"{len(gpus)} GPU feeds, {len(errors)} errors"
          + (f" · {len(fired)} ALERT(S): " + "; ".join(fired) if fired else ""))
    for e in errors:
        print("  ! " + e, file=sys.stderr)
    # Exit non-zero when no automatic sensor could be read at all, so a caller
    # can refuse to publish rather than shipping an empty board.
    return 0 if auto else 2


if __name__ == "__main__":
    sys.exit(main())
