"""List acronyms and notation used in lessons but missing from glossary.json.

Every acronym needs an entry, because the abbreviations plugin can only explain a term it
knows. Run from the vault root:

    python3 quartz-plugins/abbreviations/check.py                   # every lesson the SWE courses link to
    python3 quartz-plugins/abbreviations/check.py path/to/lesson.md  # specific files

Exits 1 if anything is missing, printing the term and the files that use it.
Code blocks, inline code, links and compiler error codes (E0599, CS8509) are ignored.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
GLOSSARY = json.loads((HERE / "glossary.json").read_text())
COURSES = ["learning/swe-101/index.md", "learning/swe-102/index.md", "learning/swe-103/index.md"]

# Upper-case acronyms (SLO, OAuth-style mixed case is not caught) and percentile notation (p99).
TERM = re.compile(r"\b(?:[A-Z][A-Z0-9]{1,6}|p\d{2,3})\b")
ERROR_CODE = re.compile(r"[A-Z]{1,3}\d{3,}")
# Language and standard names that look like acronyms but are names, not abbreviations.
NOT_ACRONYMS = {"ID", "C11", "C17", "C23", "C99", "ASP", "NET", "OK", "II", "NVIDIA",
                "NOT", "ONLY", "ALL", "NO", "AND", "OR", "WILL", "MUST"}  # emphasis, not acronyms


def lessons_from_courses() -> list[pathlib.Path]:
    paths = []
    for course in COURSES:
        text = pathlib.Path(course).read_text()
        for link in re.findall(r"\[\[([^\]|#]+)", text):
            p = pathlib.Path(link + ".md")
            if p.exists() and not link.startswith(("learning/", "dsa/")) and p not in paths:
                paths.append(p)
                if p.name == "index.md":                     # a lesson folder: include its companions
                    paths += [c for c in sorted(p.parent.glob("*.md")) if c not in paths]
    return paths


def prose(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)   # code blocks
    text = re.sub(r"``.*?``|`[^`]*`", "", text)          # inline code
    text = re.sub(r"\[\[[^\]]*\]\]", "", text)           # wikilinks
    text = re.sub(r"\]\([^)]*\)", "]", text)             # markdown link targets
    return re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)  # maths


def main() -> int:
    files = [pathlib.Path(a) for a in sys.argv[1:]] or lessons_from_courses()
    missing: dict[str, list[str]] = {}
    for f in files:
        for term in set(TERM.findall(prose(f.read_text()))):
            if term in GLOSSARY or term in NOT_ACRONYMS or ERROR_CODE.fullmatch(term):
                continue
            missing.setdefault(term, []).append(str(f))
    for term, where in sorted(missing.items()):
        print(f"{term}: {', '.join(sorted(where)[:3])}{' …' if len(where) > 3 else ''}")
    print(f"\n{len(files)} files checked, {len(missing)} terms missing from glossary.json")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
