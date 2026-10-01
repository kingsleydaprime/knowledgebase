"""Check every lesson the scheme of work links to against COURSE-STANDARD.md and
rewrite the tracker block in 06-lesson-quality.md. Run from the vault root after
converting a lesson; the tracker is derived, never hand-maintained."""
import re, pathlib

SOW = pathlib.Path("learning/swe-101/04-scheme-of-work.md")
OUT = pathlib.Path("learning/swe-101/06-lesson-quality.md")
START, END = "<!-- AUDIT:START -->", "<!-- AUDIT:END -->"

# A marker is present when the lesson has the section the standard asks for.
CHECKS = [
    ("kid", r"(?im)^#+ .*kid version"),
    ("start", r"(?im)^## Before you start"),
    ("terms", r"(?im)^## Terms used"),
    ("checks", r"(?i)<details>"),
    ("practice", r"(?im)^## Practice"),
]
# References, interview banks and exercise sets keep their own shapes (see the standard).
OWN_SHAPE = re.compile(r"reference|interview|INTERVIEW|PRIMETECHIE|practice-exercises")

body = SOW.read_text().split("<!-- CONTENTS:END -->")[1]
rows, seen = [], set()
for week in re.split(r"^# Week ", body, flags=re.M)[1:]:
    num = week.split(" ", 1)[0]
    for link in re.findall(r"\[\[([^\]|#]+)", week):
        path = pathlib.Path(link + ".md")
        if link in seen or not path.exists() or link.endswith("/index") or link.startswith(("dsa/", "learning/")):
            continue
        seen.add(link)
        if OWN_SHAPE.search(link):
            rows.append((num, "n/a", "keeps its own shape", link))
            continue
        text = path.read_text()
        have = [name for name, rx in CHECKS if re.search(rx, text)]
        status = "✅ meets" if len(have) == len(CHECKS) else ("🟡 partial" if have else "⬜ not started")
        missing = ", ".join(n for n, _ in CHECKS if n not in have) or "—"
        rows.append((num, status, missing, link))

done = sum(r[1] == "✅ meets" for r in rows)
todo = sum(r[1] != "n/a" for r in rows)
out = [START, "", f"**{done} of {todo} lessons meet the standard.**", "",
       "| Week | Status | Missing | Lesson |", "|---|---|---|---|"]
out += [f"| {n} | {s} | {m} | [[{l}\\|{l.rsplit('/', 1)[-1]}]] |" for n, s, m, l in rows]
out += ["", END]

doc = OUT.read_text()
OUT.write_text(re.sub(re.escape(START) + r".*?" + re.escape(END), "\n".join(out), doc, flags=re.S))
print(f"{done}/{todo} lessons meet the standard")
