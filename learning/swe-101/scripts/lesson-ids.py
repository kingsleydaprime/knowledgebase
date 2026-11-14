"""Give every lesson the SWE courses link to a permanent `id` in its frontmatter,
and check that the ids stay permanent. I Sabi stores progress against these ids,
so a lesson can be renamed or turned into a folder without losing anyone's progress.

    python3 learning/swe-101/scripts/lesson-ids.py           # check only; exits 1 on a problem
    python3 learning/swe-101/scripts/lesson-ids.py --assign  # add ids to lessons missing one

The registry (learning/lesson-ids.json) maps each id to its lesson's current path.
It is how the check notices an id that disappeared: a lesson was deleted, or its
frontmatter was overwritten. An id the platform should stop showing on purpose goes
under "retired" instead of being deleted from the registry.

Run from the vault root."""
import json, pathlib, re, sys, uuid

COURSES = ["learning/swe-101/index.md", "learning/swe-102/index.md", "learning/swe-103/index.md"]
REGISTRY = pathlib.Path("learning/lesson-ids.json")
LEARN_LINE = re.compile(r"^- \*\*Learn \((?:core|optional)\):\*\*(.*)$", re.M)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
ID_LINE = re.compile(r"^id:\s*(\S+)\s*$", re.M)


def course_lessons() -> list[pathlib.Path]:
    """The lessons the courses' Learn lanes link to, in course order, without duplicates."""
    found, seen = [], set()
    for course_path in COURSES:
        course = pathlib.Path(course_path)
        if not course.exists():
            continue
        for line in LEARN_LINE.findall(course.read_text()):
            for link in re.findall(r"\[\[([^\]|#]+)", line):
                path = pathlib.Path(link.strip() + ".md")
                if link in seen or not path.exists() or link.startswith(("dsa/", "learning/")):
                    continue
                seen.add(link)
                found.append(path)
    return found


def read_id(text: str) -> str | None:
    fm = FRONTMATTER.match(text)
    m = fm and ID_LINE.search(fm.group(1))
    return m.group(1) if m else None


def with_id(text: str, lesson_id: str) -> str:
    """The same text with `id:` added as the first frontmatter field."""
    if FRONTMATTER.match(text):
        return text.replace("---\n", f"---\nid: {lesson_id}\n", 1)
    return f"---\nid: {lesson_id}\n---\n\n{text}"


def valid_uuid(value: str) -> bool:
    try:
        return str(uuid.UUID(value)) == value
    except ValueError:
        return False


def main() -> int:
    assign = "--assign" in sys.argv[1:]
    registry = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {"lessons": {}, "retired": {}}
    problems: list[str] = []

    # Every id anywhere in the vault, so a copied file's duplicate id is caught
    # even if the copy isn't in a course yet.
    owners: dict[str, list[str]] = {}
    for md in pathlib.Path(".").rglob("*.md"):
        if any(part in ("node_modules", ".git", "quartz") for part in md.parts):
            continue
        lesson_id = read_id(md.read_text(errors="ignore"))
        if lesson_id:
            owners.setdefault(lesson_id, []).append(str(md))

    added = 0
    for path in course_lessons():
        text = path.read_text()
        lesson_id = read_id(text)
        if lesson_id is None:
            if not assign:
                problems.append(f"no id: {path}  (run with --assign)")
                continue
            lesson_id = str(uuid.uuid4())
            path.write_text(with_id(text, lesson_id))
            owners[lesson_id] = [str(path)]
            added += 1
        elif not valid_uuid(lesson_id):
            problems.append(f"id is not a lowercase UUID: {path}: {lesson_id}")
        registry["lessons"][lesson_id] = str(path)

    for lesson_id, paths in owners.items():
        if len(paths) > 1:
            problems.append(f"duplicate id {lesson_id}: " + ", ".join(sorted(paths)))
        elif lesson_id in registry["lessons"]:
            registry["lessons"][lesson_id] = paths[0]  # follows a lesson that moved

    for lesson_id, path in registry["lessons"].items():
        if lesson_id not in owners and lesson_id not in registry["retired"]:
            problems.append(f"id disappeared: {lesson_id} (was {path}). Restore it, "
                            "or move it under \"retired\" if the lesson is gone on purpose")

    registry["lessons"] = dict(sorted(registry["lessons"].items(), key=lambda kv: kv[1]))
    if assign or not problems:
        REGISTRY.write_text(json.dumps(registry, indent=2) + "\n")

    for p in problems:
        print(p)
    print(f"{len(registry['lessons'])} lessons with ids, {added} added, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
