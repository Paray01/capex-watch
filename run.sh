#!/bin/bash
# Capex Cycle Watch — scheduled refresh. Run by the LaunchAgent
# com.nik.capex-watch, and safe to run by hand at any time.
cd "$(dirname "$0")" || exit 1

# The cloud routine keeps the manual sensor assessments and any code fixes in
# the repository. Pull them before reading, but never let a network hiccup or a
# dirty tree stop the local refresh.
git pull --rebase --autostash --quiet 2>/dev/null || true

# The Mac keeps its own Rule 01 clock; the tracked history.json belongs to the
# cloud routine. Same code, two histories, nothing to merge.
export CAPEX_HISTORY=history-local.json

# SEC EDGAR requires a deliverable contact address in the User-Agent. It lives
# in contact.env, which is git-ignored — this repository is public.
[ -f contact.env ] && . ./contact.env

{
  printf '%s  ' "$(date '+%Y-%m-%d %H:%M')"
  /usr/bin/python3 fetch.py 2>&1
} >> log.txt

# A board nobody opens is not a watch. Notify only when something actually
# changed state — silence is the normal, correct outcome most days.
if [ -s alert.txt ]; then
  # alert.txt has no trailing newline, so wc -l is one short of the line count.
  COUNT=$(( $(wc -l < alert.txt) + 1 ))
  BODY=$(head -3 alert.txt | tr '\n' ' ')
  /usr/bin/osascript -e "display notification \"${BODY//\"/\'}\" with title \"Capex Cycle Watch\" subtitle \"$COUNT change(s) on the board\"" 2>/dev/null
fi

# Keep the log to the last 400 runs.
tail -n 400 log.txt > log.tmp && mv log.tmp log.txt
