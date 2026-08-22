# Capex Cycle Watch

Sixteen sensors for one question: **is the AI build-out still being paid for by the money it earns?**

Eight sensors read themselves from public sources. Eight need a human, and say so on the page. The dashboard is a single HTML file; the thresholds, the confirmation rule and the cluster scoring all live in `fetch.py`, so there is exactly one implementation of the rules.

Not one price on the board is a stock price. Equities move on expectations; the physical and financial plumbing moves on commitments, and commitments turn first.

## Sources

All three are free and need no API key.

| Source | Feeds |
|---|---|
| SEC EDGAR XBRL | capex, operating cash flow and revenue per quarter for MSFT, AMZN, GOOGL, META, ORCL, NVDA |
| FRED | high-yield credit spread, semiconductor PPI, CPI for personal computers, semiconductor production |
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
| Cloud routine | Mon and Thu, 05:00 UTC | researches the eight manual sensors, rescores offline, republishes the artifact |

**The cloud agent cannot fetch.** Its sandbox routes outbound HTTPS through a policy-enforcing proxy that refuses `data.sec.gov`, `fred.stlouisfed.org` and `console.vast.ai` alike — every request comes back `403 Forbidden` at the tunnel. That is why the Mac is the only fetcher and publishes its readings here, and why `fetch.py --rescore` exists: it recomputes states, verdict and alerts from the committed `data.js` plus the current `manual.json` without touching the network.

The Mac pulls before each run, so manual-sensor updates from the cloud reach it within twelve hours. Only the Mac writes `data.js` and `history.json`; only the cloud writes `manual.json`. Nothing has to be merged.

## The connection map

The page's centrepiece is a canvas force-graph of the same sixteen readings, joined by twenty arrows that encode which one influences which — spending pushes chip prices, chip prices reach shop prices, dearer devices sell less, weaker income makes the spending harder to justify, and the spending falls. The four groups settle onto a ring in the order influence travels, so the feedback loop reads as a loop.

Bubbles are draggable, sized by how central a reading is to the argument, coloured by state, and a reading that has turned pulses. Travelling dots along each edge show the direction of influence. No library: sixteen bodies, twenty springs and a repulsion pass, drawn on a 2D canvas. `prefers-reduced-motion` settles the layout in one go and draws it static.

## The reading rules

An indicator list without rules of interpretation fires every quarter, and after the third false alarm nobody looks at it. Four of the six rules are enforced in code:

1. **Two readings** — a move counts only once it has held about thirty days. `fetch.py` snapshots every state daily and scores each sensor at the milder of today and thirty days ago.
2. **Two clusters** — stages escalate on how many of the four clusters have turned, never on how many sensors have. Memory, GPUs, fabs and lead times all measure the same tightness; four reds inside one cluster is one signal wearing four hats.
3. **Units, never revenue** — price rises hide volume collapse. The consumer price index used is one that normally *falls*, so flat is already pressure.
4. **Current generation only** — a rental price carries information only for the accelerator people are actually buying. Last year's silicon getting cheap is the value cascade working.
5. **Ask why, not just whether** — capex cut for lack of demand is the signal; capex cut for lack of power, permits or chips is the opposite. Human judgement.
6. **Downgrade with the same discipline** — one reassuring quarter does not clear a red cluster. Human judgement.

## Files

| | |
|---|---|
| `fetch.py` | fetches, scores, writes `data.js`, raises alerts |
| `index.html` | the dashboard — displays the verdict, does not compute it |
| `manual.json` | the eight sensors with no machine-readable feed, each with its own `asof` date |
| `make_artifact.py` | builds a self-contained copy for publishing |
| `run.sh` | the scheduled wrapper: pull, fetch, notify, trim the log |

Standard library only. No dependencies, no build step.
