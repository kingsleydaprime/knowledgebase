"""Check interview banks and mock interviews against the rules in COURSE-STANDARD.md
("Interviews: interview banks and mock interviews").

    python3 scripts/check-interviews.py backend          # one subject (or any folder)
    python3 scripts/check-interviews.py projects/arete   # a private project

It checks every .md file under the folder with `kind: interview-bank`, or with
`format: interview` on a `kind: checkpoint` or `kind: exam` paper:
  - the page has a lowercase uuid `id` in its frontmatter;
  - every question (each `###` in a bank, each `## Question N` in a mock) has an
    `interview` marker on its first non-blank line, with an 8-hex `id` unique in the
    page, `level` of beginner/intermediate/advanced, `hot` of 0/1/2 if given, and
    `pace` of 1–15 if given;
  - its <details> block has the four labels in order (**Strong answer covers:**,
    **Follow-up:**, **Detail worth adding:**, **Revise:**), each once;
  - "Strong answer covers" has 3 to 7 top-level bullets;
  - a mock has `minutes` from 5 to 600.
Prints one line per problem and exits 1 if there are any.
"""
import pathlib
import re
import sys

FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
MARKER = re.compile(r"^<!-- q: interview (.*?) -->\s*$")
ATTR = re.compile(r'(\w+)="([^"]*)"')
LABELS = ["**Strong answer covers:**", "**Follow-up:**", "**Detail worth adding:**", "**Revise:**"]
FENCE = re.compile(r"^\s*(```|~~~)")


def strip_code(lines: list[str]) -> list[str]:
    """Blank out fenced code, so a `#` or `- ` inside code isn't read as structure."""
    out, inside = [], False
    for line in lines:
        if FENCE.match(line):
            inside = not inside
            out.append("")
        else:
            out.append("" if inside else line)
    return out


def check_question(path, heading, body: list[str], ids: list[str]) -> list[str]:
    where = f"{path}: '{heading}'"
    problems = []
    first = next((l for l in body if l.strip()), "")
    m = MARKER.match(first)
    if not m:
        return [f"{where}: no interview marker on the first line"]
    attrs = dict(ATTR.findall(m.group(1)))
    qid = attrs.get("id", "")
    if not re.fullmatch(r"[0-9a-f]{8}", qid):
        problems.append(f"{where}: id {qid!r} is not 8 hex characters")
    ids.append(qid)
    if attrs.get("level") not in ("beginner", "intermediate", "advanced"):
        problems.append(f"{where}: level {attrs.get('level')!r} is not beginner/intermediate/advanced")
    if attrs.get("hot", "0") not in ("0", "1", "2"):
        problems.append(f"{where}: hot {attrs.get('hot')!r} is not 0, 1 or 2")
    if "pace" in attrs and not (attrs["pace"].isdigit() and 1 <= int(attrs["pace"]) <= 15):
        problems.append(f"{where}: pace {attrs['pace']!r} is not a whole number from 1 to 15")
    if "marks" in attrs:
        problems.append(f"{where}: interview questions have no marks attribute (the app counts them)")

    text = "\n".join(body)
    d = re.search(r"<details>(.*?)</details>", text, re.S)
    if not d:
        return problems + [f"{where}: no <details> block"]
    inner = d.group(1).split("\n")
    found = []
    for label in LABELS:
        rows = [i for i, l in enumerate(inner) if l.startswith(label)]
        if len(rows) != 1:
            problems.append(f"{where}: {label} appears {len(rows)} times, needs exactly 1")
        found.append(rows[0] if rows else None)
    if None not in found and found != sorted(found):
        problems.append(f"{where}: the four labels are out of order")
    if found[0] is not None and found[1] is not None and found[0] < found[1]:
        bullets = [l for l in inner[found[0] + 1:found[1]] if re.match(r"^[-*] ", l)]
        if not 3 <= len(bullets) <= 7:
            problems.append(f"{where}: {len(bullets)} checklist bullets, needs 3 to 7")
    return problems


def check(path: pathlib.Path) -> list[str]:
    text = path.read_text()
    fm = FM.match(text)
    meta = dict(re.findall(r"^(\w+):\s*(.+?)\s*$", fm.group(1), re.M)) if fm else {}
    bank = meta.get("kind") == "interview-bank"
    mock = meta.get("kind") in ("checkpoint", "exam") and meta.get("format") == "interview"
    if not (bank or mock):
        return []
    problems = []
    if not UUID.match(meta.get("id", "")):
        problems.append(f"{path}: frontmatter id is missing or not a lowercase uuid")
    if mock and not (meta.get("minutes", "").isdigit() and 5 <= int(meta["minutes"]) <= 600):
        problems.append(f"{path}: minutes {meta.get('minutes')!r} not in 5–600")

    lines = text.split("\n")
    plain = strip_code(lines)
    if bank:
        starts = [i for i, l in enumerate(plain) if l.startswith("### ")]
        is_end = lambda l: l.startswith("### ") or l.startswith("## ")
    else:
        starts = [i for i, l in enumerate(plain) if l.startswith("## Question")]
        is_end = lambda l: l.startswith("## ")
    if not starts:
        problems.append(f"{path}: no questions found")
    ids: list[str] = []
    for s in starts:
        e = next((j for j in range(s + 1, len(lines)) if is_end(plain[j])), len(lines))
        problems += check_question(path, lines[s].lstrip("# "), lines[s + 1:e], ids)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        problems.append(f"{path}: duplicate question ids {dupes}")
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = pathlib.Path(sys.argv[1])
    problems = [p for f in sorted(root.rglob("*.md")) for p in check(f)]
    for p in problems:
        print(p)
    checked = sum(1 for f in root.rglob("*.md") if FM.match(f.read_text()) and re.search(
        r"^kind:\s*interview-bank|^format:\s*interview", FM.match(f.read_text()).group(1), re.M))
    print(f"{checked} interview pages checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
