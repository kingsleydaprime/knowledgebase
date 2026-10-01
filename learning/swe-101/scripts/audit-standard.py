"""Check every lesson the SWE courses link to against COURSE-STANDARD.md and
rewrite the tracker block in 06-lesson-quality.md. Run from the vault root after
converting a lesson; the tracker is derived, never hand-maintained."""
import re, pathlib

COURSES = ["learning/swe-101/index.md", "learning/swe-102/index.md", "learning/swe-103/index.md"]
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
# Only the Learn lanes are lessons; DSA lessons and problem files follow the DSA formats.
LEARN_LINE = re.compile(r"^- \*\*Learn \((core|optional)\):\*\*(.*)$", re.M)

rows, seen = [], set()
for course_path in COURSES:
    course = pathlib.Path(course_path)
    if not course.exists():
        continue
    name = course.parent.name.upper().replace("-", " ")
    for week in re.split(r"^### Week ", course.read_text(), flags=re.M)[1:]:
        num = week.split(" ", 1)[0]
        for kind, line in LEARN_LINE.findall(week):
            for link in re.findall(r"\[\[([^\]|#]+)", line):
                path = pathlib.Path(link + ".md")
                if link in seen or not path.exists() or link.startswith(("dsa/", "learning/")):
                    continue
                seen.add(link)
                if OWN_SHAPE.search(link):
                    rows.append((name, num, kind, "n/a", "keeps its own shape", link))
                    continue
                text = path.read_text()
                have = [n for n, rx in CHECKS if re.search(rx, text)]
                status = "✅ meets" if len(have) == len(CHECKS) else ("🟡 partial" if have else "⬜ not started")
                missing = ", ".join(n for n, _ in CHECKS if n not in have) or "—"
                rows.append((name, num, kind, status, missing, link))

def summary(kind):
    group = [r for r in rows if r[2] == kind and r[3] != "n/a"]
    return sum(r[3] == "✅ meets" for r in group), len(group)

core_done, core_all = summary("core")
opt_done, opt_all = summary("optional")
out = [START, "",
       f"**Core lessons: {core_done} of {core_all} meet the standard. Optional: {opt_done} of {opt_all}.**", "",
       "| Course | Week | Lane | Status | Missing | Lesson |", "|---|---|---|---|---|---|"]
out += [f"| {c} | {w} | {k} | {s} | {m} | [[{l}\\|{l.rsplit('/', 1)[-1]}]] |" for c, w, k, s, m, l in rows]
out += ["", END]

doc = OUT.read_text()
OUT.write_text(re.sub(re.escape(START) + r".*?" + re.escape(END), "\n".join(out), doc, flags=re.S))
print(f"core {core_done}/{core_all}, optional {opt_done}/{opt_all}")
