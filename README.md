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

## Running it

```bash
python3 fetch.py          # rewrites data.js, ~15 seconds
open index.html           # the dashboard reads data.js beside it
python3 make_artifact.py  # a self-contained copy for publishing
```

`index.html` loads `data.js` with a `<script src>` rather than `fetch()`, so it works straight off the filesystem with no web server.

## Two runners, one repository

| | Runs | Owns |
|---|---|---|
| Mac (`run.sh`, LaunchAgent twice daily) | 08:15 and 19:15 local | `history-local.json`, macOS notifications on state changes |
| Cloud routine (Mon and Thu) | 05:00 UTC | tracked `history.json`, `manual.json`, the published artifact |

Both read the same sources and apply the same code. They keep separate history files so neither has to merge a JSON file it did not write; the Mac pulls before each run to pick up manual-sensor updates and code fixes.

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
