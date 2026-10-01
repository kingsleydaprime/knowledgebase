"""Run the vault's labs and check the lessons still show the code that runs.

Each folder in labs/ with a lab.json is one lab:

    {
      "lesson": "concepts/04-best-practices/01-clean-code.md",
      "setup":  [["npm", "ci", "--silent"]],   optional; runs once, when node_modules/ is missing
      "run":    [["node", "--test"]],          every command must exit 0
      "embedded": ["after.mjs"]                files that must appear verbatim in the lesson
    }

Usage, from the vault root:
    python3 labs/run.py                 run every lab
    python3 labs/run.py layers solid    run the named labs
    python3 labs/run.py --drift-only    only check lessons against lab files (fast, offline)
"""
import json, pathlib, subprocess, sys, time

LABS = pathlib.Path(__file__).resolve().parent
VAULT = LABS.parent


def drift(lab: pathlib.Path, spec: dict) -> list[str]:
    """Files listed in `embedded` whose exact content is no longer in the lesson."""
    lesson = (VAULT / spec["lesson"]).read_text()
    return [f for f in spec.get("embedded", []) if (lab / f).read_text().strip() not in lesson]


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


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    drift_only = "--drift-only" in sys.argv
    labs = sorted(p.parent for p in LABS.glob("*/lab.json"))
    if args:
        labs = [l for l in labs if l.name in args]
        missing = set(args) - {l.name for l in labs}
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
            print(f"FAIL  {lab.name:40} {took}")
            for p in problems:
                print("      " + p.replace("\n", "\n      "))
        else:
            print(f"ok    {lab.name:40} {took}")

    print(f"\n{len(labs) - failures}/{len(labs)} labs passed" + (" (drift check only)" if drift_only else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
