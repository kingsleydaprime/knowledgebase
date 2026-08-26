"""Regenerate the Contents block in 04-scheme-of-work.md from the weeks below it.
Run after editing any week; the TOC is derived, never hand-maintained."""
import re, pathlib

SRC = pathlib.Path("learning/swe-101/04-scheme-of-work.md")
START, END = "<!-- CONTENTS:START -->", "<!-- CONTENTS:END -->"

BLOCKS = [  # (first week, last week, block name)
    (1, 1, "Introduction"), (2, 4, "Software design"), (5, 8, "Architecture & system design"),
    (9, 11, "Databases"), (12, 15, "Networking & the web"), (16, 17, "Security"),
    (18, 19, "Backend consolidation"), (20, 23, "AI engineering"), (24, 24, "Testing & quality"),
    (25, 25, "DevOps & delivery"), (26, 29, "Concurrency & distributed systems"),
    (30, 30, "Review"), (31, 99, "The CS spine"),
]

s = SRC.read_text()
weeks = []
for block in re.split(r"^# Week ", s, flags=re.M)[1:]:
    head = block.split("\n", 1)[0]
    num = int(re.match(r"(\d+)", head).group(1))
    title = head.split("—", 1)[1].strip() if "—" in head else head
    topics = [(n, re.sub(r"\s*→\s*\[\[.*$", "", t).strip().rstrip("."))
              for n, t in re.findall(r"^- \*\*(\d+\.\d+)\*\*\s*(.+)$", block, re.M)]
    dsa = re.search(r"^\*\*DSA:\*\*\s*(.+)$", block, re.M)
    weeks.append((num, title, topics, re.sub(r"\s*→\s*\[\[.*$", "", dsa.group(1)).strip() if dsa else None))

out = [START, ""]
for lo, hi, name in BLOCKS:
    ws = [w for w in weeks if lo <= w[0] <= hi]
    if not ws: continue
    span = f"Week {lo}" if lo == hi else (f"Weeks {lo}–{hi}" if hi != 99 else f"Week {lo}+")
    out.append(f"**{span} · {name}**\n")
    for num, title, topics, dsa in ws:
        out.append(f"- **{num} — {title}**" + (f"  ·  *{dsa}*" if dsa else ""))
        for n, t in topics:
            out.append(f"    - `{n}` {t}")
    out.append("")
out.append(f"*{sum(len(w[2]) for w in weeks)} topics across {len(weeks)} weeks. "
           "Generated from the weeks below — regenerate rather than hand-edit.*")
out += ["", END]

block = "\n".join(out)
if START in s:                      # already present — replace in place.
    # NB: check for the MARKER, not for `new == s`. A no-op regeneration leaves
    # the string identical, and treating that as "first run" inserts a duplicate.
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), block, s, flags=re.S)
else:                               # first run — insert before Week 1
    marker = "\n---\n\n# Week 1 "
    header = ("\n---\n\n## Contents\n\n"
              "**This doubles as the notebook index.** The header says *week number = notebook "
              "section number* and *index on pages 1\u20134* \u2014 this is what goes on those pages. "
              "Topic `13.4` here is page-marked 13.4 in the book.\n\n"
              "**Generated, not hand-written** \u2014 run "
              "`python3 learning/swe-101/scripts/generate-contents.py` after editing any week. "
              "Edit a week, regenerate, never both.\n\n")
    new = s.replace(marker, header + block + marker, 1)
SRC.write_text(new)
print(f"TOC: {sum(len(w[2]) for w in weeks)} topics across {len(weeks)} weeks")
