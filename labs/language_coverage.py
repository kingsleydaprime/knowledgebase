"""List every lesson whose code is in only one language, and whether it has an
"other languages" companion yet. Rewrites the tracker block in LANGUAGE-COVERAGE.md.
Run from the vault root: python3 labs/language_coverage.py

A companion is any lesson that says "A companion to [[<lesson path>|...]]" near its top.
Order of work: SWE 101 core, 102 core, 103 core, then optional, then everything else by area."""
import collections, pathlib, re

OUT = pathlib.Path("LANGUAGE-COVERAGE.md")
START, END = "<!-- COVERAGE:START -->", "<!-- COVERAGE:END -->"
LANG = {"js": "TS/JS", "javascript": "TS/JS", "ts": "TS/JS", "typescript": "TS/JS", "tsx": "TS/JS", "jsx": "TS/JS",
        "python": "Python", "py": "Python", "go": "Go", "java": "Java", "rust": "Rust", "rs": "Rust",
        "c": "C", "cpp": "C++", "c++": "C++", "csharp": "C#", "cs": "C#", "kotlin": "Kotlin"}
# Language courses are about one language by design; journals and projects record real work.
SKIP = ("quartz", "node_modules", "labs", "projects", "journals", "blog", "learning", "languages",
        "dsa/neetcode-150", "templates", "sources")
COURSES = ["learning/swe-101/index.md", "learning/swe-102/index.md", "learning/swe-103/index.md"]

def course_order():
    """lesson path -> (rank, label) from the SWE courses' Learn lines."""
    order = {}
    for rank_base, course in enumerate(COURSES):
        text = pathlib.Path(course).read_text()
        name = course.split("/")[1].upper().replace("-", " ")
        for kind, line in re.findall(r"^- \*\*Learn \((core|optional)\):\*\*(.*)$", text, re.M):
            for link in re.findall(r"\[\[([^\]|#]+)", line):
                rank = (0 if kind == "core" else 3) + rank_base
                order.setdefault(link + ".md", (rank, f"{name} {kind}"))
    return order

def main():
    lessons, companions = [], {}
    for p in pathlib.Path(".").rglob("*.md"):
        s = str(p)
        if s.startswith(SKIP) or "/interview" in s or s.endswith("-qb.md") or p.name == "projects.md":
            continue
        if "labs" in p.parts or "node_modules" in p.parts:     # lab code beside a lesson
            continue
        if p.name == "index.md" and not (p.parent / "labs").exists() and not list(p.parent.glob("in-*.md")):
            continue                                            # a folder index, not a lesson folder
        text = p.read_text(errors="ignore")
        head = text[:1500]
        m = re.search(r"A companion to \[\[([^\]|#]+)", head)
        if m:
            companions[m.group(1) + ".md"] = s
            continue
        langs = {LANG[f.lower()] for f in re.findall(r"^```([\w+#-]*)", text, re.M) if f.lower() in LANG}
        if len(langs) == 1:
            lessons.append((s, langs.pop()))

    order = course_order()
    rows = sorted(lessons, key=lambda r: (order.get(r[0], (9, ""))[0], r[0]))
    done = sum(r[0] in companions for r in rows)
    by_area = collections.Counter(r[0].split("/")[0] for r in rows)

    out = [START, "", f"**{done} of {len(rows)} single-language lessons have a companion.**", "",
           "By area: " + " · ".join(f"{a} {n}" for a, n in by_area.most_common()), "",
           "| Priority | Lesson | Written in | Companion |", "|---|---|---|---|"]
    for path, lang in rows:
        stem = path[:-3]
        comp = companions.get(path)
        comp_cell = f"[[{comp[:-3]}\\|✅]]" if comp else "—"
        out.append(f"| {order.get(path, (9, 'other'))[1]} | [[{stem}\\|{stem}]] | {lang} | {comp_cell} |")
    out += ["", END]
    doc = OUT.read_text()
    OUT.write_text(re.sub(re.escape(START) + r".*?" + re.escape(END), "\n".join(out), doc, flags=re.S))
    print(f"{done}/{len(rows)} single-language lessons have a companion")

if __name__ == "__main__":
    main()
