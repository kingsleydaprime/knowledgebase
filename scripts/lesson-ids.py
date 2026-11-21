"""Give every lesson in the vault a permanent `id` in its frontmatter, give every
`##` section of every lesson a permanent bite id, and check that the ids stay
permanent. EruditeMe stores progress against these ids, so a lesson can be renamed
or turned into a folder, and a heading reworded, without losing anyone's progress.

    python3 scripts/lesson-ids.py           # check only; exits 1 on a problem
    python3 scripts/lesson-ids.py --assign  # add ids to lessons and bites missing one
    python3 scripts/lesson-ids.py --list    # print every file it counts as a lesson

What counts as a lesson (see COURSE-STANDARD.md, "Subjects, lessons, bites..."):
  - It sits inside a subject: a top-level folder with an index.md that isn't in
    NOT_SUBJECTS below.
  - Its name starts with a two-digit number, like `02-line-drawing.md`. For a lesson
    that is a folder, the folder's name does, and the lesson is its `index.md`.
  - It is a leaf. A numbered folder that holds other numbered files or folders is a
    section of the subject, and its index.md is a section index, not a lesson.
  - It isn't under `labs/` or `interview/` (interview banks), isn't a companion (`in-other-languages.md`), and its name
    doesn't match NOT_LESSON (question banks, solutions, formula sheets).
  - To leave out any other file, put `lesson: false` in its frontmatter.
Courses and study plans are never touched: they only link to lessons.

A bite id is an HTML comment on the line directly under its `##` heading:

    ## Why loose coupling is easier to change
    <!-- bite: 3f1c...-uuid -->

Obsidian and Quartz don't show the comment. Move the comment with the section if
you move the section; delete it with the section if you delete the section.

The registry (lesson-ids.json at the vault root) maps each lesson id to its lesson's
current path, and each bite id to "<path>#<heading>". It is how the check notices an
id that disappeared. A lesson id that disappears is a problem (a lesson was deleted,
or its frontmatter was overwritten); one the platform should stop showing on purpose
goes under "retired" instead of being deleted. A bite id that disappears is only a
warning, because deleting or merging sections is normal editing; --assign drops it
from the registry. A lesson whose file still exists but no longer counts as a lesson
(the rule changed, or it got `lesson: false`) is a warning too, and --assign moves
it to "retired" along with dropping its bites, so the registry always equals --list.

Run from the vault root."""
import json, pathlib, re, sys, uuid

REGISTRY = pathlib.Path("lesson-ids.json")
NOT_SUBJECTS = {"learning", "projects", "sources", "research", "tools", "journals", "kanban",
                "notes", "templates", "labs", "blog-drafts", "build-your-own-shit",
                "quartz", "quartz-plugins"}
NUMBERED = re.compile(r"^\d{2}-")
NOT_LESSON = re.compile(r"(question-bank|-qb|solutions|formula-sheet)", re.I)
OPT_OUT = re.compile(r"^lesson:\s*false\s*$", re.M)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
ID_LINE = re.compile(r"^id:\s*(\S+)\s*$", re.M)
BITE_MARK = re.compile(r"^<!-- bite: (\S+) -->\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
SKIP_DIRS = ("node_modules", ".git", "quartz")


def subjects() -> list[pathlib.Path]:
    return sorted(d for d in pathlib.Path(".").iterdir()
                  if d.is_dir() and (d / "index.md").exists()
                  and d.name not in NOT_SUBJECTS and not d.name.startswith("."))


def has_numbered_children(folder: pathlib.Path) -> bool:
    return any(NUMBERED.match(c.name) and (c.is_dir() or c.suffix == ".md") for c in folder.iterdir())


def is_lesson(path: pathlib.Path) -> bool:
    if "labs" in path.parts or "interview" in path.parts or path.name.startswith("in-") or NOT_LESSON.search(str(path)):
        return False
    if path.name == "index.md":
        folder = path.parent
        if not NUMBERED.match(folder.name) or has_numbered_children(folder):
            return False
    elif not NUMBERED.match(path.name):
        return False
    fm = FRONTMATTER.match(path.read_text(errors="ignore"))
    return not (fm and OPT_OUT.search(fm.group(1)))


def all_lessons() -> list[pathlib.Path]:
    """Every lesson in every subject, in path order."""
    return [md for subject in subjects() for md in sorted(subject.rglob("*.md")) if is_lesson(md)]


def read_id(text: str) -> str | None:
    fm = FRONTMATTER.match(text)
    m = fm and ID_LINE.search(fm.group(1))
    return m.group(1) if m else None


def with_id(text: str, lesson_id: str) -> str:
    """The same text with `id:` added as the first frontmatter field."""
    if FRONTMATTER.match(text):
        return text.replace("---\n", f"---\nid: {lesson_id}\n", 1)
    return f"---\nid: {lesson_id}\n---\n\n{text}"


def bites(text: str, assign: bool) -> tuple[str, list[tuple[str | None, str]]]:
    """Walk the `##` headings outside code fences. Returns the (possibly updated)
    text and one (bite id or None, heading) pair per section, in order."""
    lines = text.split("\n")
    out, found, in_fence = [], [], False
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            heading = line[3:].strip()
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            mark = BITE_MARK.match(nxt)
            if mark:
                found.append((mark.group(1), heading))
                out.append(nxt)
                i += 1
            elif assign:
                bite_id = str(uuid.uuid4())
                out.append(f"<!-- bite: {bite_id} -->")
                found.append((bite_id, heading))
            else:
                found.append((None, heading))
        i += 1
    return "\n".join(out), found


def valid_uuid(value: str) -> bool:
    try:
        return str(uuid.UUID(value)) == value
    except ValueError:
        return False


def main() -> int:
    assign = "--assign" in sys.argv[1:]
    if "--list" in sys.argv[1:]:
        for path in all_lessons():
            print(path)
        return 0
    registry = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {}
    registry.setdefault("lessons", {})
    registry.setdefault("retired", {})
    registry.setdefault("bites", {})
    problems: list[str] = []
    warnings: list[str] = []

    # Every lesson id and bite id anywhere in the vault, so a copied file's or a
    # copied section's duplicate id is caught even if the copy isn't in a course yet.
    owners: dict[str, list[str]] = {}
    bite_owners: dict[str, list[str]] = {}
    for md in pathlib.Path(".").rglob("*.md"):
        if any(part in SKIP_DIRS for part in md.parts):
            continue
        text = md.read_text(errors="ignore")
        lesson_id = read_id(text)
        if lesson_id:
            owners.setdefault(lesson_id, []).append(str(md))
        for bite_id, heading in bites(text, assign=False)[1]:
            if bite_id:
                bite_owners.setdefault(bite_id, []).append(f"{md}#{heading}")

    added = added_bites = 0
    lessons_seen: set[str] = set()
    for path in all_lessons():
        text = path.read_text()
        lesson_id = read_id(text)
        if lesson_id is None:
            if not assign:
                problems.append(f"no id: {path}  (run with --assign)")
            else:
                lesson_id = str(uuid.uuid4())
                text = with_id(text, lesson_id)
                owners[lesson_id] = [str(path)]
                added += 1
        elif not valid_uuid(lesson_id):
            problems.append(f"id is not a lowercase UUID: {path}: {lesson_id}")
        if lesson_id:
            registry["lessons"][lesson_id] = str(path)
            lessons_seen.add(str(path))

        new_text, sections = bites(text, assign)
        missing = [h for b, h in sections if b is None]
        if missing:
            problems.append(f"{len(missing)} sections without a bite id: {path}  (run with --assign)")
        for bite_id, heading in sections:
            if bite_id is None:
                continue
            if not valid_uuid(bite_id):
                problems.append(f"bite id is not a lowercase UUID: {path}#{heading}: {bite_id}")
            if bite_id not in bite_owners:
                bite_owners[bite_id] = [f"{path}#{heading}"]
                added_bites += 1
            registry["bites"][bite_id] = f"{path}#{heading}"
        if new_text != path.read_text():
            path.write_text(new_text)

    for lesson_id, paths in owners.items():
        if len(paths) > 1:
            problems.append(f"duplicate id {lesson_id}: " + ", ".join(sorted(paths)))
        elif lesson_id in registry["lessons"]:
            registry["lessons"][lesson_id] = paths[0]  # follows a lesson that moved

    for lesson_id, path in registry["lessons"].items():
        if lesson_id not in owners and lesson_id not in registry["retired"]:
            problems.append(f"id disappeared: {lesson_id} (was {path}). Restore it, "
                            "or move it under \"retired\" if the lesson is gone on purpose")

    for bite_id, places in bite_owners.items():
        if len(places) > 1:
            problems.append(f"duplicate bite id {bite_id}: " + ", ".join(sorted(places))
                            + "  (delete the copied comment and run with --assign)")
        elif bite_id in registry["bites"]:
            registry["bites"][bite_id] = places[0]  # follows a section that moved or was renamed

    for bite_id in list(registry["bites"]):
        if bite_id not in bite_owners:
            warnings.append(f"bite id disappeared: {bite_id} (was {registry['bites'][bite_id]})")
            if assign:
                del registry["bites"][bite_id]

    # A registered lesson whose file still exists but no longer counts as a lesson
    # (the rule changed, or it got `lesson: false`) is retired: hidden, history kept.
    for lesson_id, path in list(registry["lessons"].items()):
        if lesson_id in owners and path not in lessons_seen and lesson_id not in registry["retired"]:
            if assign:
                registry["retired"][lesson_id] = f"{path} (no longer a lesson)"
                del registry["lessons"][lesson_id]
            else:
                warnings.append(f"no longer a lesson: {path} (--assign retires it)")
    current = {p for p in registry["lessons"].values()}
    for bite_id, place in list(registry["bites"].items()):
        if place.split("#", 1)[0] not in current and assign:
            del registry["bites"][bite_id]  # bites only count inside current lessons

    registry["lessons"] = dict(sorted(registry["lessons"].items(), key=lambda kv: kv[1]))
    registry["bites"] = dict(sorted(registry["bites"].items(), key=lambda kv: kv[1]))
    if assign or not problems:
        REGISTRY.write_text(json.dumps(registry, indent=2) + "\n")

    for p in problems:
        print(p)
    for w in warnings:
        print("warning:", w)
    print(f"{len(registry['lessons'])} lessons with ids ({added} added), "
          f"{len(registry['bites'])} bites with ids ({added_bites} added), "
          f"{len(problems)} problems, {len(warnings)} warnings")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
