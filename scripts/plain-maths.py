#!/usr/bin/env python3
"""List maths written as plain text instead of formatted maths.

Lessons should write maths as $P_b$, $n^2$, $q_0$, not as P_b, n^2, `P_b`
or q₀, and not with chat-style \\( \\) delimiters. This finds the plain-text cases so they can be fixed.

What it skips: frontmatter, fenced code blocks, $...$ and $$...$$ maths,
image alt text and link targets (alt text can't render maths), HTML
comments, and code spans that look like real code (snake_case names,
calls, paths).

Usage:
    python3 scripts/plain-maths.py                 # whole vault, summary per file
    python3 scripts/plain-maths.py mechatronics    # one folder or file
    python3 scripts/plain-maths.py -v mechatronics # every hit with its line
    python3 scripts/plain-maths.py --unicode       # also list q₀, n², ẋ (they
                                                   # display fine, so off by default)
Exit code is 1 when anything is found, so it can gate a review.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_FILES = {"BUILD-PLAN.md", "COURSE-STANDARD.md"}
# terms that look like maths but are names: W^X (write xor execute), and
# mechatronics tutorial sheets named T_4, T_5, T_6 in the UNILAG source
NOT_MATHS = re.compile(r"\bW\^X\b|\bT_\d\b")
SKIP_DIRS = {".agents", "quartz", "quartz-plugins", "node_modules", ".git", "templates",
             "journals", "projects", "sources", "tools", "kanban", "scripts"}

# a short symbol with a subscript: x_d, P_b, V_in, σ_max, d_{r}
SUB = re.compile(r"(?<![\w\\/.$-])([A-Za-zΑ-Ωα-ω]{1,2}|[A-Za-zΑ-Ωα-ω]\d?)_(\{[^}\s]{1,8}\}|[A-Za-z0-9]{1,4})(?![\w(/.])")
# a power: n^2, 2^n, x^{-1}, (a+b)^2
SUP = re.compile(r"(?<![\w\\$])[A-Za-z0-9)\]]\^(\{[^}\s]{1,10}\}|-?[A-Za-z0-9]{1,3})(?!\w)")
# Unicode super/subscripts and dotted letters used as maths
UNI = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿⁱᵀ₀₁₂₃₄₅₆₇₈₉₊₋ᵢⱼₖₙₘₜₓ]|[a-zA-Z]̇")
# chat-style maths delimiters \(x\): Quartz and EruditeMe only render $x$
PAREN = re.compile(r"\\\((.{1,80}?)\\\)")
# a code span whose whole content is maths-looking: `P_b`, `n^2`, `x_d = 3`
CODE_MATHS = re.compile(r"^[A-Za-zΑ-Ωα-ω](_[A-Za-z0-9]{1,4}|\^[A-Za-z0-9]{1,3})( ?[=<>+\-*/] ?[\w.^ ]{1,12})?$")
# words that look like SUB but are names: PWR_FLAG etc. (all-caps both sides)
CAPS_NAME = re.compile(r"^[A-Z0-9]+_[A-Z0-9]{2,}$")
WORD_NAME = re.compile(r"^(is|to|in|of|on|at|id|no|ok|fn|by|my|do|go|up|re|py|os|db|io)_", re.I)


def name_like(t):
    return bool(CAPS_NAME.match(t) or WORD_NAME.match(t))

MASKS = [
    re.compile(r"<!--.*?-->"),
    re.compile(r"\$\$.*?\$\$"),
    re.compile(r"(?<!\\)\$[^$\n]+?(?<!\\)\$"),
    re.compile(r"!\[[^\]]*\]\([^)]*\)"),   # images: alt text can't hold maths
    re.compile(r"!\[\[[^\]]*\]\]"),
    re.compile(r"\]\([^)]*\)"),             # link targets
    re.compile(r"\[\[[^\]|]*"),             # wikilink targets
    re.compile(r"https?://\S+"),
    re.compile(r"<[^>]+>"),                 # html tags and attributes
    re.compile(r'\w+="[^"]*"'),             # quiz attributes like accept="..."
    NOT_MATHS,
]


def scan(path: Path):
    hits = []
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    in_fence = in_front = in_display = False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if i == 1 and s == "---":
            in_front = True
            continue
        if in_front:
            if s == "---":
                in_front = False
            continue
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if s == "$$" or (s.startswith("$$") and s.count("$$") == 1) or (s.endswith("$$") and s.count("$$") == 1 and in_display):
            in_display = not in_display
            continue
        if in_display:
            continue
        work = line
        found = [("paren", mo.group(0)) for mo in PAREN.finditer(re.sub(r"`[^`]*`", "", line))]
        for m in MASKS:
            work = m.sub(lambda mo: " " * len(mo.group(0)), work)
        # code spans: flag only the ones that are pure maths, then blank them
        for mo in re.finditer(r"`([^`]+)`", work):
            if CODE_MATHS.match(mo.group(1).strip()) and not name_like(mo.group(1).strip()):
                found.append(("code", mo.group(0)))
        work = re.sub(r"`[^`]+`", lambda mo: " " * len(mo.group(0)), work)
        for mo in SUB.finditer(work):
            if not name_like(mo.group(0)):
                found.append(("sub", mo.group(0)))
        for mo in SUP.finditer(work):
            found.append(("pow", mo.group(0)))
        if UNICODE:
            for mo in UNI.finditer(work):
                found.append(("uni", mo.group(0)))
        if found:
            hits.append((i, found, line))
    return hits


UNICODE = False


def main(argv):
    global UNICODE
    verbose = "-v" in argv
    UNICODE = "--unicode" in argv
    args = [a for a in argv if not a.startswith("-")]
    targets = [ROOT / a for a in args] or [ROOT]
    files = []
    for t in targets:
        if t.is_file():
            files.append(t)
        else:
            for p in sorted(t.rglob("*.md")):
                if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts) and p.name not in SKIP_FILES:
                    files.append(p)
    total = 0
    rows = []
    for f in files:
        hits = scan(f)
        if hits:
            n = sum(len(h[1]) for h in hits)
            total += n
            rows.append((n, f, hits))
    for n, f, hits in sorted(rows, key=lambda r: -r[0]):
        print(f"{n:4d}  {f.relative_to(ROOT)}")
        if verbose:
            for i, found, line in hits:
                print(f"      {i}: {' '.join(t for _, t in found)}   | {line.strip()[:110]}")
    print(f"\n{total} plain-text maths in {len(rows)} files")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
