#!/usr/bin/env python3
"""
Capex Cycle Watch — data fetcher.

Pulls the automatable sensors from three free, key-less public sources:

  SEC EDGAR (data.sec.gov)   capex, operating cash flow, revenue per company
  FRED      (stlouisfed.org) credit spreads, semiconductor PPI, consumer hardware CPI,
                             and the market around the cycle: weakest-borrower
                             spreads, volatility, financial conditions, real
                             yields, the recession signal, equity value vs GDP
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

# key: (FRED id, kind, observations per year). The kind decides what the chart
# carries: "bp" a spread level in basis points, "level" the value as published,
# "yoy" the change against a year earlier.
FRED_SERIES = {
    # High Yield Option-Adjusted Spread — credit stress, daily.
    "hy_oas": ("BAMLH0A0HYM2", "bp", 252),
    # PPI: semiconductor and related device manufacturing — component price pressure.
    "semi_ppi": ("PCU3344133441", "yoy", 12),
    # CPI: personal computers and peripheral equipment — where the squeeze reaches a household.
    "pc_cpi": ("CUSR0000SEEE01", "yoy", 12),
    # Industrial production: semiconductors and electronic components — physical capacity.
    "semi_ip": ("IPG3344S", "yoy", 12),
    # ---- cluster E, the market around the cycle ----
    # CCC-and-below spread. The builders that borrow against GPUs sit here; the
    # broad high-yield index averages them away. In October 2026 it stood at
    # 1,300bp while the broad index read a calm 327bp.
    "ccc_oas": ("BAMLH0A3HYC", "bp", 252),
    # VIX — what insurance against a falling market costs, daily.
    "vix": ("VIXCLS", "level", 252),
    # Chicago Fed National Financial Conditions Index, weekly. Zero is average,
    # positive is tighter than average.
    "nfci": ("NFCI", "level", 52),
    # 10-year real yield: what money costs after inflation, and so what a
    # forecast of income ten years out is worth today.
    "real10": ("DFII10", "level", 252),
    # Sahm rule, real-time: the recession signal from unemployment.
    "sahm": ("SAHMREALTIME", "level", 12),
    # Context, not scored: market value of corporate equities against GDP.
    "mktcap": ("NCBEILQ027S", "level", 4),
    "gdp": ("GDP", "level", 4),
}

# Current-generation accelerators. Last-generation prices are deliberately excluded:
# cheap old silicon is the value cascade working, not demand failing (Rule 04).
GPUS_CURRENT = ["H200", "B200", "H100 SXM"]
# Below this many listings across all models, a change in offer depth is a
# handful of hosts coming and going, not supply. The price still reads; the
# depth does not, and B1 cannot turn on it.
MIN_OFFERS = 8
# Quarters of history kept for the six headline numbers. Three years is
# enough to show where a reading came from without bloating data.js.
QHIST = 12
QUARTERLY_NOTE = ("one point per quarter, each a trailing twelve months, "
                  "median of the five buyers")


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


def median_series(companies, key):
    """
    The median of the five buyers at each quarterly offset, oldest point first.

    Aligned by offset rather than by calendar date, because Oracle keeps its own
    fiscal year — exactly how the current reading is built, one quarter at a time.
    Each point is dated by the newest filing that contributed to it.
    """
    out = []
    for b in range(QHIST):
        vals, ends = [], []
        for c in companies:
            if c.get("stale") or c["ticker"] == "NVDA":
                continue
            h, q = c.get(key) or [], c.get("q_ends") or []
            if b < len(h) and h[b] is not None:
                vals.append(h[b])
                if b < len(q) and q[b]:
                    ends.append(q[b])
        if vals and ends:
            out.append({"d": max(ends), "v": round(statistics.median(vals), 1)})
    out.reverse()
    return out


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
            # concept() reads a failed request as "tag not used", so one EDGAR
            # hiccup used to drop a filer's cash flow silently — Alphabet's on
            # 2026-10-16, leaving A2 a median of four. Worse, when the current
            # tag fails an old fallback tag wins: Oracle's revenue fell back to
            # "Revenues", which ends in 2022 and mixes in annual figures, and
            # turned its coverage gap from +154pp into +38pp (2026-10-29). So a
            # series is also retried when it trails capex by more than a quarter,
            # and dropped (and reported) if it still does: a missing figure
            # leaves the medians honest, a stale one does not.
            def lags(series):
                return bool(series and capex) and days(series[-1][0], capex[-1][0]) > 120
            for _ in range(2):
                if capex and ocf and rev and not lags(ocf) and not lags(rev):
                    break
                time.sleep(3)
                capex, t_capex = (capex, t_capex) if capex else concept(cik, TAGS_CAPEX)
                if not ocf or lags(ocf):
                    ocf = concept(cik, TAGS_OCF)[0]
                if not rev or lags(rev):
                    rev, t_rev = concept(cik, TAGS_REV)
            if lags(ocf):
                ocf = []
            if lags(rev):
                rev, t_rev = [], None
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
                for b in range(QHIST)
            ],
            # The same three readings one quarter at a time, so the page can
            # draw where each headline number came from. Index is quarters back.
            "capex_growth_hist": [pct(ttm(capex, b), ttm(capex, b + 4)) for b in range(QHIST)],
            "capex_ocf_hist": [
                (ttm(capex, b) / ttm(ocf, b) * 100) if (ttm(capex, b) and ttm(ocf, b)) else None
                for b in range(QHIST)
            ],
            "q_ends": [capex[-1 - b][0] if len(capex) > b else None for b in range(QHIST)],
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
    for key, (sid, kind, step) in FRED_SERIES.items():
        try:
            pts = fred(sid)
        except Exception as e:                               # noqa: BLE001
            out[key] = {"error": str(e), "series": sid}
            continue
        latest = pts[-1] if pts else None
        # `step` observations back is a year: 252 for daily, 52 weekly, 12 monthly.
        half, quarter = step // 2, step // 4
        # The chart carries the unit the headline number is quoted in, not the
        # raw index: a credit spread is read as a level in basis points, the
        # price indices as a change against a year earlier.
        if kind == "bp":
            chart = [{"d": p["d"], "v": round(p["v"] * 100)} for p in pts[-130:]]
        elif kind == "level":
            chart = [{"d": p["d"], "v": round(p["v"], 2)} for p in pts[-130:]]
        else:
            chart = []
            for i in range(step, len(pts)):
                y = pct(pts[i]["v"], pts[i - step]["v"])
                if y is not None:
                    chart.append({"d": pts[i]["d"], "v": round(y, 2)})
            chart = chart[-60:]
        out[key] = {
            "series": sid,
            "latest": latest,
            "yoy": pct(latest["v"], at_offset(pts, step)) if latest else None,
            "chg_6m": pct(latest["v"], at_offset(pts, half)) if latest else None,
            "abs_6m": (latest["v"] - at_offset(pts, half)) if latest and at_offset(pts, half) is not None else None,
            "abs_3m": (latest["v"] - at_offset(pts, quarter)) if latest and at_offset(pts, quarter) is not None else None,
            # A single day of a daily series is noise; markets are scored on a week.
            "avg5": round(statistics.mean(p["v"] for p in pts[-5:]), 2) if len(pts) >= 5 else None,
            "spark": [p["v"] for p in pts[-60:]],
            "spark_dates": [p["d"] for p in pts[-60:]],
            "chart": chart,
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
                   "detail": f"median of {len(ratios)} hyperscalers, trailing twelve months",
                   "series": median_series(companies, "capex_ocf_hist"),
                   "series_note": QUARTERLY_NOTE,
                   "guides": [{"v": 60, "label": "watch above 60%"},
                              {"v": 100, "label": "turning above 100%, two quarters running"}]}

    # A1 — capex growth. Guidance itself is not machine-readable; realised
    # trailing-twelve-month growth is, and it is what guidance eventually becomes.
    gr = [c["capex_growth"] for c in companies
          if c.get("capex_growth") is not None and not c.get("stale") and c["ticker"] != "NVDA"]
    if gr:
        med = statistics.median(gr)
        st = 0 if med > 10 else (1 if med > -5 else 2)
        s["A1"] = {"state": st, "value": round(med, 1), "unit": "% YoY",
                   "detail": "median realised capex growth, trailing twelve months",
                   "series": median_series(companies, "capex_growth_hist"),
                   "series_note": QUARTERLY_NOTE,
                   "guides": [{"v": 10, "label": "watch below +10%"},
                              {"v": -5, "label": "turning below -5%"}]}

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
                             + ". A proxy — total revenue dilutes AI revenue, so the true AI-level gap is smaller.",
                   "series": median_series(companies, "coverage_gap_hist"),
                   "series_note": QUARTERLY_NOTE,
                   "guides": [{"v": 0, "label": "calm at or below zero"},
                              {"v": 50, "label": "turning above 50pp in each of three quarters"}]}

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
                   "detail": f"US high-yield spread, {'+' if chg>=0 else ''}{round(chg)}bp over six months",
                   "series": hy.get("chart", []),
                   "series_note": "one point per trading day, about six months",
                   "guides": [{"v": 450, "label": "watch above 450bp"},
                              {"v": 600, "label": "turning above 600bp"}]}

    # B1 — the live GPU rental market: price and depth together. Read across
    # every current model that has a month of history, not just the first one
    # returned: the market is thin enough that a single model with four
    # listings swung the reading by itself, and whichever model happened to
    # come back first used to become the "lead".
    if gpus:
        lead = next((g for g in gpus if g["gpu"] == GPUS_CURRENT[0]), gpus[0])
        trends = [t for t in (gpu_trend(hist, g["gpu"], 30) for g in gpus)
                  if t and t["price"] is not None and t["offers"] is not None]
        listed = sum(g["offers"] for g in gpus)
        if not trends:
            st, detail = None, f"{len(hist)} day(s) of history — a trend needs about a month"
        else:
            p = statistics.median(t["price"] for t in trends)
            o = statistics.median(t["offers"] for t in trends)
            thin = listed < MIN_OFFERS
            st = 0
            if p < -25 and o > 0 and not thin:
                st = 2                                        # cheaper while capacity grows
            elif p < -10:
                st = 1
            detail = (f"median of {len(trends)} model(s): {round(p,1)}% price and {round(o,1)}% "
                      f"listings over ~{max(t['days'] for t in trends)} days")
            if thin:
                detail += (f". Only {listed} listings in all, too few to read supply depth, "
                           "so this reading cannot turn on its own")
        s["B1"] = {"state": st, "value": lead["median"], "unit": f"$/hr {lead['gpu']}", "detail": detail}

    # D2 — consumer hardware prices. This index normally falls a few per cent a
    # year through quality adjustment, so flat is already pressure and rising is
    # the demand-destruction point.
    pcc = f.get("pc_cpi", {})
    if pcc.get("yoy") is not None:
        y = pcc["yoy"]
        st = 0 if y < 0 else (1 if y < 5 else 2)
        s["D2"] = {"state": st, "value": round(y, 1), "unit": "% YoY",
                   "detail": "CPI, personal computers and peripherals — this series normally declines",
                   "series": pcc.get("chart", []),
                   "series_note": "one point per month, against the same month a year earlier",
                   "guides": [{"v": 0, "label": "watch above zero — this index normally falls"},
                              {"v": 5, "label": "turning above +5%"}]}

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
                   "detail": f"PPI semiconductors, six-month change {round(m6,1) if m6 is not None else '—'}% — a proxy; spot DRAM leads it",
                   "series": pp.get("chart", []),
                   "series_note": "one point per month, against the same month a year earlier",
                   "guides": [{"v": 10, "label": "watch above +10%"}]}

    # ---------------- cluster E: the market around the cycle ----------------
    # Not part of the cycle stage. The four clusters above ask whether the AI
    # build is turning; these ask whether the money around it is panicking.
    # The two come apart: a market can fall hard while the build holds
    # (October 2026), and a turning build does far more damage when the market
    # is already strained. Thresholds sit on past episodes, not on this week.
    # Scored on the day, without Rule 01's month: markets move in days.
    ccc = f.get("ccc_oas", {})
    if ccc.get("latest"):
        lvl = ccc["latest"]["v"] * 100
        chg = (ccc.get("abs_6m") or 0) * 100
        st = 2 if (lvl >= 1500 or chg >= 400) else 1 if (lvl >= 1000 or chg >= 150) else 0
        hy_now = round(hy["latest"]["v"] * 100) if hy.get("latest") else None
        s["E1"] = {"state": st, "value": round(lvl), "unit": "bp",
                   "detail": f"US CCC-and-below spread, {'+' if chg >= 0 else ''}{round(chg)}bp over six months"
                             + (f"; the broad high-yield index in C2 reads {hy_now}bp" if hy_now else ""),
                   "series": ccc.get("chart", []),
                   "series_note": "one point per trading day, about six months",
                   "guides": [{"v": 1000, "label": "watch above 1,000bp, or +150bp in six months"},
                              {"v": 1500, "label": "turning above 1,500bp, or +400bp in six months"}]}

    vx = f.get("vix", {})
    if vx.get("avg5") is not None:
        v5 = vx["avg5"]
        st = 2 if v5 >= 30 else 1 if v5 >= 20 else 0
        s["E2"] = {"state": st, "value": v5, "unit": "VIX",
                   "detail": f"VIX, five-day average; latest close {vx['latest']['v']} on {vx['latest']['d']}",
                   "series": vx.get("chart", []),
                   "series_note": "one point per trading day, about six months",
                   "guides": [{"v": 20, "label": "watch above 20"},
                              {"v": 30, "label": "turning above 30"}]}

    nf = f.get("nfci", {})
    if nf.get("latest"):
        lvl, c3 = nf["latest"]["v"], nf.get("abs_3m") or 0
        st = 2 if lvl >= 0 else 1 if (lvl >= -0.25 or c3 >= 0.25) else 0
        s["E3"] = {"state": st, "value": round(lvl, 2), "unit": "NFCI",
                   "detail": f"Chicago Fed financial conditions, {'+' if c3 >= 0 else ''}{round(c3, 2)} over three months. "
                             "Zero is average; below it money is easier to get than usual",
                   "series": nf.get("chart", []),
                   "series_note": "one point per week, about two and a half years",
                   "guides": [{"v": -0.25, "label": "watch above -0.25, or +0.25 in three months"},
                              {"v": 0, "label": "turning above zero: tighter than average"}]}

    ry = f.get("real10", {})
    if ry.get("latest"):
        lvl, chg = ry["latest"]["v"], (ry.get("abs_6m") or 0) * 100
        st = 2 if chg >= 100 else 1 if (chg >= 50 or lvl >= 2.5) else 0
        s["E4"] = {"state": st, "value": round(lvl, 2), "unit": "% real",
                   "detail": f"10-year real Treasury yield, {'+' if chg >= 0 else ''}{round(chg)}bp over six months. "
                             "Income expected years out is worth less today when this rises",
                   "series": ry.get("chart", []),
                   "series_note": "one point per trading day, about six months",
                   "guides": [{"v": 2.5, "label": "watch above 2.5%, or +50bp in six months"}]}

    sh = f.get("sahm", {})
    if sh.get("latest"):
        v = sh["latest"]["v"]
        st = 2 if v >= 0.5 else 1 if v >= 0.3 else 0
        s["E5"] = {"state": st, "value": round(v, 2), "unit": "Sahm",
                   "detail": f"Sahm rule, real-time, {sh['latest']['d'][:7]}: rise in the three-month unemployment average over its low of the past year",
                   "series": sh.get("chart", [])[-60:],
                   "series_note": "one point per month",
                   "guides": [{"v": 0.3, "label": "watch at 0.3"},
                              {"v": 0.5, "label": "turning at 0.5: every recession since 1970 crossed it"}]}

    return s


def valuation(f):
    """
    Context, not scored: the market value of US corporate equities against GDP.
    Valuation decides how far a fall can go, not when it starts — so it sits
    beside the board instead of on it.
    """
    mc, gd = f.get("mktcap", {}), f.get("gdp", {})
    if not (mc.get("chart") and gd.get("chart")):
        return {}
    g = {p["d"]: p["v"] for p in gd["chart"]}
    ser = [{"d": p["d"], "v": round(p["v"] / 1000 / g[p["d"]] * 100, 1)}
           for p in mc["chart"] if g.get(p["d"])]
    if not ser:
        return {}
    peak = max(ser[:-1], key=lambda p: p["v"]) if len(ser) > 1 else ser[-1]
    return {"latest": ser[-1], "prior_peak": peak, "series": ser[-60:]}


# --------------------------------------------------------------------------
# verdict — the reading rules, in one place
#
# These live here rather than in the page so there is exactly one
# implementation. The dashboard displays the verdict; it does not compute it.
# --------------------------------------------------------------------------

CLUSTER_MAP = [
    ("A", "Demand", ["A1", "A2", "A3", "A4"]),
    ("B", "Physical supply", ["B1", "B2", "B3", "B4"]),
    # C5 joined on 2026-10-23: vendors financing their own customers is the
    # one way the build can be paid for that none of C1-C4 sees.
    ("C", "Financing", ["C1", "C2", "C3", "C4", "C5"]),
    ("D", "The paying end", ["D1", "D2", "D3", "D4"]),
]
STAGE_NAMES = ["Expansion", "Friction", "Mismatch", "Reversal"]
# The market around the cycle. Scored with the same cluster rule, reported
# beside the stage and never folded into it: the stage answers whether the
# AI build is turning, this whether the money around it is panicking.
MARKET = ("E", "The market around it", ["E1", "E2", "E3", "E4", "E5"])
MARKET_IDS = set(MARKET[2])
MARKET_NAMES = ["Calm", "Strained", "Acute"]


def confirmed_states(states, hist):
    """
    Rules 01 and 06 — a move counts only once it has held about a month, in
    either direction. Until then a sensor keeps scoring at the reading it had
    before the move. This used to take the milder of today and thirty days
    ago, which let an easing count at once and broke Rule 06 ("one calm
    quarter does not clear a red cluster").

    "Held" is read off every saved day, not one sample a month back: a move
    counts once every reading since it began agrees with today and the first
    of them is at least 28 days old. Days without a reading are skipped.
    The market cluster is exempt; it moves in days and is read on the day.
    """
    rows = [h for h in hist if h.get("states") and h["date"] != TODAY]
    ready = bool(rows) and days(rows[0]["date"], TODAY) >= 28
    out = {}
    for sid, v in states.items():
        if sid in MARKET_IDS:
            out[sid] = v
            continue
        since, before = TODAY, None
        for h in reversed(rows):
            p = h["states"].get(sid)
            if p is None:
                continue
            if p == v:
                since = h["date"]
                continue
            before = p
            break
        out[sid] = v if (before is None or days(since, TODAY) >= 28) else before
    return out, ready


def cluster_score(states, ids):
    """Rule 02 — a cluster turns on two reds, or one red plus two ambers."""
    vals = [states[i] for i in ids if i in states]
    if not vals:
        return None
    red = sum(1 for v in vals if v == 2)
    amber = sum(1 for v in vals if v == 1)
    return (2 if (red >= 2 or (red >= 1 and amber >= 2))
            else 1 if (red >= 1 or amber >= 2) else 0)


def cluster_scores(states):
    return [cluster_score(states, ids) for _, _, ids in CLUSTER_MAP]


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
    m = cluster_score(states, MARKET[2])
    mids = MARKET[2]
    return {
        "market": {"id": MARKET[0], "name": MARKET[1], "score": m,
                   "level": MARKET_NAMES[m] if m is not None else None,
                   "watch": [i for i in mids if states.get(i) == 1],
                   "turning": [i for i in mids if states.get(i) == 2]},
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

def alerts(states, prev_states, v, prev_stage, manual, prev_market=None):
    """Everything worth interrupting someone for. Empty list is the normal case."""
    out = []
    if prev_stage is not None and v["stage"] != prev_stage:
        direction = "escalated to" if v["stage"] > prev_stage else "eased back to"
        out.append(f"STAGE {direction} 0{v['stage']+1} {v['stage_name']}")
    m = v["market"]["score"]
    if isinstance(prev_market, int) and m is not None and m != prev_market:
        direction = "rose to" if m > prev_market else "eased to"
        out.append(f"MARKET stress {direction} {MARKET_NAMES[m]}")
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
    # Built from the chart series, so before they are dropped below. A rescore
    # has no charts and carries the last fetch's figure through.
    valuation_ctx = valuation(fredd) or ((prev.get("context") or {}).get("valuation", {}) if rescore else {})

    # The per-quarter arrays behind the filing charts are working material for
    # median_series, not something the page reads — they leave with the medians
    # already computed. A rescore has no filings to rebuild them from, so it
    # carries the last fetch's chart through rather than dropping it.
    if rescore:
        for sid, prev_sensor in (prev.get("auto") or {}).items():
            if sid in auto and not auto[sid].get("series") and prev_sensor.get("series"):
                for k in ("series", "series_note", "guides"):
                    if prev_sensor.get(k):
                        auto[sid][k] = prev_sensor[k]
    for c in companies:
        for k in ("capex_growth_hist", "capex_ocf_hist", "q_ends"):
            c.pop(k, None)
        if c.get("coverage_gap_hist"):
            c["coverage_gap_hist"] = c["coverage_gap_hist"][:3]
    # Same for the FRED chart series: it now lives on the sensor that quotes it,
    # and storing it twice would double the file for nothing.
    for entry in fredd.values():
        if isinstance(entry, dict):
            entry.pop("chart", None)

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
    prev_market = (prev_row or {}).get("market")

    if not rescore:
        hist = update_history(gpus, fredd, states)
    v = verdict(states, hist)
    if hist:
        hist[-1]["states"] = states
        hist[-1]["stage"] = v["stage"]
        hist[-1]["market"] = v["market"]["score"]
    if not rescore:
        with open(os.path.join(HERE, HISTORY_FILE), "w") as fh:
            json.dump(hist, fh, indent=1)

    fired = alerts(states, prev_states, v, prev_stage, manual, prev_market)
    with open(os.path.join(HERE, "alert.txt"), "w") as fh:
        fh.write("\n".join(fired))
    if fired:
        # A second run on the same day compares against the same yesterday and
        # fires the same lines again; the log keeps each one once per day.
        log_path = os.path.join(HERE, "alerts.log")
        try:
            seen = set(open(log_path).read().splitlines())
        except OSError:
            seen = set()
        with open(log_path, "a") as fh:
            for line in fired:
                if f"{TODAY}  {line}" not in seen:
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
    # A filer with capex but no cash flow or revenue drops out of A2 or D3
    # without anything saying so. Say so.
    partial = [f"{c['ticker']} ({', '.join(k for k, f in (('cash flow', 'ocf_ttm'), ('revenue', 'rev_ttm')) if c.get(f) is None)})"
               for c in companies
               if not (c.get("stale") or c.get("error")) and (c.get("ocf_ttm") is None or c.get("rev_ttm") is None)]
    if partial and not rescore:
        errors.append("sec-edgar: incomplete figures for " + ", ".join(partial))
    if not gpus:
        errors.append("vast.ai: no GPU offers returned")
    elif len(gpus) < len(GPUS_CURRENT) and not rescore:
        missing = [g for g in GPUS_CURRENT if g not in {x["gpu"] for x in gpus}]
        errors.append(f"vast.ai: no offers for {', '.join(missing)} — B1 reads the remaining models")
    if not auto:
        errors.append("NO AUTOMATIC SENSORS — the board is running on manual "
                      "assessments alone and must not be read as a verdict")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # A rescore compares against today's own row, so it only sees what the
    # manual edits changed. It used to replace the page's alerts with that,
    # wiping what the fetch it is based on had found (E1 and C2 on 2026-10-28).
    # It adds to them instead.
    shown = fired
    if rescore:
        shown = list(prev.get("alerts") or [])
        shown += [a for a in fired if a not in shown]
    payload = {
        "verdict": v,
        "alerts": shown,
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
            "valuation": valuation_ctx,
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
          f"market {v['market']['level'] or '—'} · "
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
