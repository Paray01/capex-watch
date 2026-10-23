# Capex Cycle Watch

Seventeen sensors for one question: **is the AI build-out still being paid for by the money it earns?** And five more for the one beside it: **is the money around it panicking?**

Thirteen sensors read themselves from public sources. Nine need a human, and say so on the page. The dashboard is a single HTML file; the thresholds, the confirmation rule and the cluster scoring all live in `fetch.py`, so there is exactly one implementation of the rules.

Not one price on the board is a stock price. Equities move on expectations; the physical and financial plumbing moves on commitments, and commitments turn first.

## Sources

All three are free and need no API key.

| Source | Feeds |
|---|---|
| SEC EDGAR XBRL | capex, operating cash flow and revenue per quarter for MSFT, AMZN, GOOGL, META, ORCL, NVDA |
| FRED | high-yield and CCC-and-below credit spreads, semiconductor PPI, CPI for personal computers, semiconductor production, VIX, Chicago Fed financial conditions, 10-year real yield, Sahm rule, corporate equity value and GDP |
| Vast.ai | live GPU rental market — median price and offer depth per accelerator |

EDGAR returns **403** unless the `User-Agent` carries a deliverable contact address. A URL and a `users.noreply.github.com` address were both tested and both refused. The address therefore comes from the environment and is never committed:

```bash
export CAPEX_CONTACT="you@example.com"
python3 fetch.py
```

Without it, `fetch.py` fails loudly rather than silently dropping the four filing-derived sensors.

## Where to read it

| | |
|---|---|
| Live web copy | https://paray01.github.io/capex-watch/ — GitHub Pages, updated whenever the Mac pushes |
| Local copy | `index.html` in this folder |
| Shareable snapshot | published as a claude.ai artifact by the cloud routine |

## Running it

```bash
python3 fetch.py          # rewrites data.js, ~15 seconds
open index.html           # the dashboard reads data.js beside it
python3 make_artifact.py  # a self-contained copy for publishing
```

`index.html` loads `data.js` with a `<script src>` rather than `fetch()`, so it works straight off the filesystem with no web server.

## Two runners, one repository

| | Runs | Does |
|---|---|---|
| Mac (`run.sh`, LaunchAgent) | 08:15 and 19:15 local | fetches all three sources, notifies on state changes, commits `data.js` and `history.json` |
| Cloud routine | Mon and Thu, 05:00 UTC | researches the nine manual sensors, rescores offline, republishes the artifact |

**The cloud agent cannot fetch.** Its sandbox routes outbound HTTPS through a policy-enforcing proxy that refuses `data.sec.gov`, `fred.stlouisfed.org` and `console.vast.ai` alike — every request comes back `403 Forbidden` at the tunnel. That is why the Mac is the only fetcher and publishes its readings here, and why `fetch.py --rescore` exists: it recomputes states, verdict and alerts from the committed `data.js` plus the current `manual.json` without touching the network.

The Mac pulls before each run, so manual-sensor updates from the cloud reach it within twelve hours. Only the Mac writes `data.js` and `history.json`; only the cloud writes `manual.json`. Nothing has to be merged.

## The connection map

The page's centrepiece is a canvas force-graph of the same twenty-two readings, joined by twenty-nine arrows that encode which one influences which — spending pushes chip prices, chip prices reach shop prices, dearer devices sell less, weaker income makes the spending harder to justify, and the spending falls. The four cycle groups settle onto a ring in the order influence travels, so the feedback loop reads as a loop; the market group sits in the middle, because it touches every part of it.

Bubbles are draggable, sized by how central a reading is to the argument, coloured by state, and a reading that has turned pulses. Travelling dots along each edge show the direction of influence. No library: twenty-two bodies, twenty-nine springs and a repulsion pass, drawn on a 2D canvas. `prefers-reduced-motion` settles the layout in one go and draws it static.

## The six headline numbers

The page opens on six readings, and each one is a button: tapping it draws the series the reading is scored from, with its own thresholds as dashed lines. The three filing-derived numbers plot one point per quarter, each a trailing twelve months and a median of the five buyers, three years back. The two price indices plot the change against the same month a year earlier, five years back. The credit spread plots the level in basis points over about six months of trading days.

`fetch.py` emits both the series and the threshold lines, so the chart cannot disagree with the verdict — the page still only draws what it is given. A threshold too far outside the data to fit on the scale is named in words under the chart rather than flattening the line: the credit spread sits near 270bp and its thresholds are 450 and 600.

## The reading rules

An indicator list without rules of interpretation fires every quarter, and after the third false alarm nobody looks at it. Four of the six rules are enforced in code:

1. **Two readings** — a move counts only once it has held about thirty days, in either direction. `fetch.py` snapshots every state daily; a move counts once every saved reading since it began agrees with today and the first of them is 28 days old, and until then the sensor scores at its value before the move. (Until 2026-10-23 it took the milder of today and thirty days ago, which let an easing count at once and contradicted rule 6.)
2. **Two clusters** — stages escalate on how many of the four cycle clusters have turned, never on how many sensors have. Memory, GPUs, fabs and lead times all measure the same tightness; four reds inside one cluster is one signal wearing four hats.
3. **Units, never revenue** — price rises hide volume collapse. The consumer price index used is one that normally *falls*, so flat is already pressure.
4. **Current generation only** — a rental price carries information only for the accelerator people are actually buying. Last year's silicon getting cheap is the value cascade working.
5. **Ask why, not just whether** — capex cut for lack of demand is the signal; capex cut for lack of power, permits or chips is the opposite. Human judgement.
6. **Downgrade with the same discipline** — one reassuring quarter does not clear a red cluster. Enforced by rule 1 since 2026-10-23.

**The market around it (cluster E).** Five automatic readings — CCC-and-below spread (E1), VIX five-day average (E2), Chicago Fed financial conditions (E3), 10-year real yield (E4), Sahm rule (E5) — scored with the same cluster rule but reported beside the stage, never folded into it, and read on the day rather than after a month. The stage answers whether the AI build is turning; this answers whether a fall would land on a calm or a nervous market. A crash is where the two meet. Added after October 2026, when the AI shares fell hard, the CCC spread rose 398bp in six months to 1,307bp and real yields rose 84bp, while every cycle sensor and the broad high-yield spread stayed where they were. Stock-market value against GDP sits beside the board as unscored context: valuation sets how far a fall can go, not when it starts.

## Files

| | |
|---|---|
| `fetch.py` | fetches, scores, writes `data.js`, raises alerts |
| `index.html` | the dashboard — displays the verdict, does not compute it |
| `manual.json` | the nine sensors with no machine-readable feed, each with its own `asof` date |
| `make_artifact.py` | builds a self-contained copy for publishing |
| `run.sh` | the scheduled wrapper: pull, fetch, notify, trim the log |

Standard library only. No dependencies, no build step.
