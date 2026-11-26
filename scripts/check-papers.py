"""Check a subject's checkpoint and mock-exam papers against the paper rules in
COURSE-STANDARD.md ("Testing a whole subject").

    python3 scripts/check-papers.py <subject>     # e.g. artificial-intelligence

For every file in the subject with `kind: exam` or `kind: checkpoint` it checks:
  - `minutes` is 5–600, and `choose` (if set) is less than the number of questions;
  - every question part (each `###` under a `## Question`, or the `## Question`
    itself when it has no parts) has a marker with an 8-hex id and whole-number marks
    from 1 to 100 on its first non-blank line;
  - ids are unique within the paper;
  - the instructions' "out of N marks" matches the marks (for `choose`, the best
    `choose` questions are assumed to carry equal marks, so N = choose × marks per question);
  - the instructions' "all N questions" matches the number of questions.
Prints one line per problem and exits 1 if there are any.
"""
import pathlib
import re
import sys

FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)
MARKER = re.compile(r'<!-- q: \w+ id="([0-9a-f]{8})" marks="(\d+)"')


def check(path: pathlib.Path) -> list[str]:
    text = path.read_text()
    fm = FM.match(text)
    meta = dict(re.findall(r"^(\w+):\s*(.+?)\s*$", fm.group(1), re.M)) if fm else {}
    if meta.get("kind") not in ("exam", "checkpoint") or meta.get("format") == "interview":
        return []  # mock interviews are checked by check-interviews.py
    problems = []
    lines = text.split("\n")
    questions = [i for i, l in enumerate(lines) if l.startswith("## Question")]
    per_question, ids = [], []
    for qi, start in enumerate(questions):
        end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
        parts = [i for i in range(start + 1, end) if lines[i].startswith("### ")] or [start]
        total = 0
        for p in parts:
            nxt = next((l for l in lines[p + 1:] if l.strip()), "")
            m = MARKER.match(nxt)
            if not m:
                problems.append(f"{path}: no marker with id and marks under '{lines[p]}'")
                continue
            ids.append(m.group(1))
            marks = int(m.group(2))
            if not 1 <= marks <= 100:
                problems.append(f"{path}: marks {marks} out of range under '{lines[p]}'")
            total += marks
        per_question.append(total)
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        problems.append(f"{path}: duplicate ids {sorted(dupes)}")
    minutes = int(meta.get("minutes", 0))
    if not 5 <= minutes <= 600:
        problems.append(f"{path}: minutes {minutes} not in 5–600")
    choose = int(meta["choose"]) if "choose" in meta else None
    if choose is not None and choose >= len(questions):
        problems.append(f"{path}: choose {choose} is not less than {len(questions)} questions")
    if choose is not None:
        # EruditeMe counts the learner's best N questions, so the most marks is the N biggest
        # (SSG 511 has a 35-mark compulsory Question 1 and 10-mark others).
        expected = sum(sorted(per_question, reverse=True)[:choose])
    else:
        expected = sum(per_question)
    stated = re.search(r"out of (\d+) marks", text)
    if stated and int(stated.group(1)) != expected:
        problems.append(f"{path}: says out of {stated.group(1)} marks, but the marks add up to {expected}")
    stated_q = re.search(r"all (\d+) questions", text)
    if stated_q and int(stated_q.group(1)) != len(questions):
        problems.append(f"{path}: says all {stated_q.group(1)} questions, but there are {len(questions)}")
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    subject = pathlib.Path(sys.argv[1])
    papers = problems = 0
    for md in sorted(subject.rglob("*.md")):
        found = check(md)
        if FM.match(md.read_text()) and re.search(r"^kind:\s*(exam|checkpoint)\s*$", FM.match(md.read_text()).group(1), re.M):
            papers += 1
        for p in found:
            print(p)
        problems += len(found)
    print(f"{papers} papers checked, {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
