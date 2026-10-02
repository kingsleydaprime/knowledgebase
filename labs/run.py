"""Run the vault's labs and check the lessons still show the code that runs.

Each lab lives beside its lesson — <lesson folder>/labs/<language>/ — with a lab.json:

    {
      "lesson": "concepts/04-best-practices/01-clean-code.md",
      "setup":  [["npm", "ci", "--silent"]],   optional; runs once, when node_modules/ is missing
      "run":    [["node", "--test"]],          every command must exit 0
      "embedded": ["after.mjs"]                files that must appear verbatim in the lesson
    }

Usage, from the vault root:
    python3 labs/run.py                                    run every lab in the vault
    python3 labs/run.py dependency-injection-and-wiring    run every language of one lesson
    python3 labs/run.py solid-principles/rust layers-controllers-services-repositories/go   single labs
    python3 labs/run.py --drift-only    only check lessons against lab files (fast, offline)
    python3 labs/run.py --sync LESSON/LANG   after editing a lab file, copy it into the lesson's code block
                                        (the block whose first two lines match the file's)
"""
import json, pathlib, re, subprocess, sys, time

LABS = pathlib.Path(__file__).resolve().parent
VAULT = LABS.parent
SKIP_DIRS = {"node_modules", "quartz", ".git", "target", ".obsidian"}


def drift(lab: pathlib.Path, spec: dict) -> list[str]:
    """Files listed in `embedded` whose exact content is no longer in the lesson."""
    lesson = (VAULT / spec["lesson"]).read_text()
    return [f for f in spec.get("embedded", []) if (lab / f).read_text().strip() not in lesson]


def sync(lab: pathlib.Path, spec: dict) -> list[str]:
    """Replace each embedded file's code block in the lesson with the file's current content.
    A block is matched by its first two lines, which must appear in exactly one block."""
    lesson_path = VAULT / spec["lesson"]
    lesson = lesson_path.read_text()
    notes = []
    for name in spec.get("embedded", []):
        content = (lab / name).read_text().strip()
        if content in lesson:
            continue
        first = content.splitlines()[:2]
        blocks = [m for m in re.finditer(r"```[^\n]*\n(.*?)\n```", lesson, re.S) if m.group(1).splitlines()[:2] == first]
        if len(blocks) != 1:
            notes.append(f"{name}: {len(blocks)} blocks start with {first!r}; fix by hand")
            continue
        m = blocks[0]
        lesson = lesson[: m.start(1)] + content + lesson[m.end(1):]
        notes.append(f"{name}: synced")
    lesson_path.write_text(lesson)
    return notes


def run(lab: pathlib.Path, spec: dict) -> str | None:
    """Run setup (if needed) and every command. Returns an error description, or None."""
    if spec.get("setup") and not (lab / "node_modules").exists():
        for cmd in spec["setup"]:
            done = subprocess.run(cmd, cwd=lab, capture_output=True, text=True)
            if done.returncode:
                return f"setup `{' '.join(cmd)}` failed:\n{done.stdout}{done.stderr}"
    for cmd in spec["run"]:
        done = subprocess.run(cmd, cwd=lab, capture_output=True, text=True)
        if done.returncode:
            return f"`{' '.join(cmd)}` exited {done.returncode}:\n{done.stdout[-3000:]}{done.stderr[-3000:]}"
    return None


def lesson_of(lab: pathlib.Path) -> str:
    """<lesson folder>/labs/<language>: the lesson's folder name without its number."""
    return re.sub(r"^\d+-", "", lab.parent.parent.name)


def name_of(lab: pathlib.Path) -> str:
    return f"{lesson_of(lab)}/{lab.name}"


def find_labs() -> list[pathlib.Path]:
    found = []
    for spec in VAULT.rglob("lab.json"):
        if SKIP_DIRS.isdisjoint(spec.relative_to(VAULT).parts) and spec.parent.parent.name == "labs":
            found.append(spec.parent)
    return sorted(found, key=name_of)


def selected(labs: list[pathlib.Path], args: list[str]) -> list[pathlib.Path]:
    """An argument names a whole lesson ("layers") or one lab ("layers/go")."""
    return [l for l in labs if not args or name_of(l) in args or lesson_of(l) in args]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    drift_only = "--drift-only" in sys.argv
    every = find_labs()
    if "--sync" in sys.argv:
        for lab in selected(every, args) if args else []:
            for note in sync(lab, json.loads((lab / "lab.json").read_text())):
                print(f"{name_of(lab)}: {note}")
        return 0
    labs = selected(every, args)
    if args:
        known = {name_of(l) for l in every} | {lesson_of(l) for l in every}
        missing = set(args) - known
        if missing:
            print(f"no such lab: {', '.join(sorted(missing))}")
            return 2

    failures = 0
    for lab in labs:
        spec = json.loads((lab / "lab.json").read_text())
        start = time.monotonic()
        problems = []
        stale = drift(lab, spec)
        if stale:
            problems.append(f"lesson {spec['lesson']} no longer matches: {', '.join(stale)}")
        if not drift_only:
            error = run(lab, spec)
            if error:
                problems.append(error)
        took = f"{time.monotonic() - start:5.1f}s"
        if problems:
            failures += 1
            print(f"FAIL  {name_of(lab):45} {took}")
            for p in problems:
                print("      " + p.replace("\n", "\n      "))
        else:
            print(f"ok    {name_of(lab):45} {took}")

    print(f"\n{len(labs) - failures}/{len(labs)} labs passed" + (" (drift check only)" if drift_only else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
