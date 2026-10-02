"""Turn a lesson file into a lesson folder, so labs and a companion can live beside it.

    python3 labs/make_lesson_folder.py ai-ml/03-ai-engineer/02-how-llms-work.md

moves   ai-ml/03-ai-engineer/02-how-llms-work.md
to      ai-ml/03-ai-engineer/02-how-llms-work/index.md
and rewrites every wikilink to it across the vault — full-path links ([[ai-ml/…/02-how-llms-work|…]])
and bare-name links ([[02-how-llms-work]]) — to point at …/02-how-llms-work/index.
Run from the vault root. Prints what it changed; does nothing if the folder already exists.
"""
import pathlib
import re
import sys

SKIP = {"node_modules", "quartz", ".git", ".obsidian", "target"}


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".md"):
        print(__doc__)
        return 2
    lesson = pathlib.Path(sys.argv[1])
    stem = str(lesson)[:-3]
    folder = pathlib.Path(stem)
    if not lesson.exists():
        print(f"no such lesson: {lesson}")
        return 1
    if folder.exists():
        print(f"already a folder: {folder}/")
        return 1

    folder.mkdir()
    lesson.rename(folder / "index.md")

    full = re.compile(r"\[\[" + re.escape(stem) + r"(?=[|\]#\\])")
    bare = re.compile(r"\[\[" + re.escape(folder.name) + r"(?=[|\]#\\])")
    changed = []
    for p in pathlib.Path(".").rglob("*.md"):
        if SKIP & set(p.parts):
            continue
        text = p.read_text(errors="ignore")
        new = bare.sub(f"[[{stem}/index", full.sub(f"[[{stem}/index", text))
        if new != text:
            p.write_text(new)
            changed.append(str(p))
    print(f"moved {lesson} -> {folder}/index.md; rewrote links in {len(changed)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
