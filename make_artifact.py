#!/usr/bin/env python3
"""
Build artifact.html — a self-contained snapshot of the dashboard for publishing
to claude.ai, where it can be opened on a phone or shared.

The published page cannot fetch anything: the claude.ai artifact sandbox blocks
requests to every external host, and none of the three data sources send CORS
headers anyway. So the snapshot carries its data inline and is only as fresh as
the run of fetch.py that preceded it. The live copy is index.html on this Mac.

Usage:  python3 fetch.py && python3 make_artifact.py
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

html = open(os.path.join(HERE, "index.html")).read()
data = open(os.path.join(HERE, "data.js")).read()

# The artifact host supplies its own document skeleton, so hand it body content
# with the <title> and <link>s kept.
head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
head = re.sub(r'<meta[^>]*>', "", head)
out = head.strip() + "\n" + body

out = out.replace('<script src="data.js"></script>', "<script>\n" + data + "\n</script>")
out = out.replace("<p class=\"eyebrow\">Live instrument panel</p>",
                  "<p class=\"eyebrow\">Snapshot &middot; the live copy runs locally</p>")
out = out.replace(
    '<p><b>Refreshing.</b> A scheduled job runs <code>fetch.py</code> daily and rewrites '
    '<code>data.js</code>; reload this page to see it. To run it by hand: <code>python3 fetch.py</code> '
    'in this folder. The manual sensors live in <code>manual.json</code> and grey out after 45 days.</p>',
    '<p><b>This page is a snapshot.</b> It carries the readings inline, frozen at the timestamp above. '
    'A published page cannot reach any of these sources — the sandbox blocks external requests, and none '
    'of the three APIs send CORS headers. The self-updating copy is <code>capex-watch/index.html</code>, '
    'refreshed twice daily by a scheduled job on the Mac that built this.</p>')

path = os.path.join(HERE, "artifact.html")
with open(path, "w") as f:
    f.write(out)
print(f"wrote {path} ({len(out):,} bytes)")
