"""Find bites that are too long to read on EruditeMe without scrolling, and lessons
whose first bite isn't an intro.

    python3 scripts/long-bites.py                      # every subject
    python3 scripts/long-bites.py machine-learning     # one subject (or any path prefix)
    python3 scripts/long-bites.py machine-learning -v  # also list the bites that fit

A bite is one `##` section of a lesson (see COURSE-STANDARD.md, "Bite"). EruditeMe
cuts bites the same way this script does (eruditeme src/content/parse.ts):
  - text between `# Title` and the first `##` is the lesson's intro, and it is shown
    on top of the FIRST bite, so a long intro makes the first bite long;
  - sections in SKIPPED below never become bites;
  - ```quiz blocks are pulled out into separate quiz cards, so they don't count.

How "too long" is measured: the script estimates how many lines of screen each bite
takes at the reading width on a laptop (about 88 characters per line). Paragraphs
wrap, list items wrap, code lines are smaller, a picture or diagram counts as a
block of lines. From a screenshot, about 14 lines of text fill one screen. The
numbers are estimates: use them to find the long bites, then check in the app.

It also checks the first bite. The first bite should be the intro: what the lesson's
thing is, in plain words, before any detail. The script flags:
  - INTRO  the text above the first `##` is more than about two lines (it lands on
           top of the first bite; keep it to one sentence and put the rest in a
           `## What <thing> is` section);
  - HIDDEN a skipped section (like "Before you start") has `###` headings in it,
           which usually means teaching content the app never shows.
And it prints the first bite's heading for each flagged lesson, so you can see at a
glance whether it is an intro.

Exit code is 0 even when it finds things: this is a to-do list, not a check.
Run from the vault root."""

import importlib.util
import math
import pathlib
import re
import sys

# Reuse the exact lesson rules from lesson-ids.py, so both scripts agree on what a
# lesson is.
_spec = importlib.util.spec_from_file_location("lesson_ids", pathlib.Path(__file__).with_name("lesson-ids.py"))
lesson_ids = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lesson_ids)

# Same list as eruditeme src/content/constants.ts SKIPPED_BITE_HEADINGS.
SKIPPED = {"related", "about this course", "about this lesson", "before moving on",
           "before you start", "further reading", "sources", "references", "see also", "next"}

SCREEN = 14        # lines of text that fit on one screen
TOO_LONG = 18      # past this it's a clear scroll, not a borderline one
CHARS_PER_LINE = 88

FENCE = re.compile(r"^\s*(```|~~~)\s*(\S*)")
BITE_MARK = re.compile(r"^<!-- bite: \S+ -->\s*$")
LIST_ITEM = re.compile(r"^\s*([-*+]|\d+[.)])\s+")


def clean_heading(h: str) -> str:
    h = re.sub(r"[*_`]", "", h).strip()
    h = re.sub(r"^(§?\d+(\.\d+)*\.?)\s+", "", h)
    return h.lower()


def visible(text: str) -> str:
    """Roughly the text a reader sees: no link targets, html tags or markdown marks."""
    text = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"[*_`]", "", text)


def wrapped(text: str, width: int = CHARS_PER_LINE) -> int:
    return max(1, math.ceil(len(visible(text).strip()) / width))


def screen_lines(markdown: str) -> float:
    """Estimate how many lines of screen a piece of markdown takes."""
    lines = markdown.split("\n")
    total = 0.0
    para: list[str] = []
    in_details = False

    def flush():
        nonlocal para, total
        if para:
            total += wrapped(" ".join(para)) + 0.6
            para = []

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        fence = FENCE.match(line)
        if fence:
            flush()
            mark, lang = fence.group(1), fence.group(2).lower()
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(mark):
                body.append(lines[i])
                i += 1
            if lang == "quiz":
                pass                                  # its own card in the app
            elif lang == "mermaid":
                total += 9                            # a diagram is about this tall
            else:
                total += sum(max(1, math.ceil(len(b) / 95)) for b in body) * 0.65 + 1.2
            i += 1
            continue
        if in_details:                                # closed answer: only summary shows
            if "</details>" in s:
                in_details = False
            i += 1
            continue
        if s.startswith("<details"):
            flush()
            total += 1.4
            if "</details>" not in s:
                in_details = True
            i += 1
            continue
        if not s or BITE_MARK.match(s):
            flush()
        elif s.startswith("#"):
            flush()
            total += 1.8
        elif s.startswith("|"):
            flush()
            if not re.match(r"^\|[\s:|-]+\|$", s):
                total += 1.2
        elif s.startswith("![") or s.startswith("<img") or s.startswith("<svg"):
            flush()
            total += 8
        elif LIST_ITEM.match(line):
            flush()
            # gather wrapped continuation lines of this item
            item = [s]
            while i + 1 < len(lines) and lines[i + 1].startswith("  ") and not LIST_ITEM.match(lines[i + 1]) \
                    and lines[i + 1].strip():
                i += 1
                item.append(lines[i].strip())
            total += wrapped(" ".join(item), CHARS_PER_LINE - 4) + 0.25
        else:
            para.append(s.lstrip("> "))
        i += 1
    flush()
    return total


def split(text: str):
    """Return (intro, [(heading, body)]) the way EruditeMe does."""
    m = lesson_ids.FRONTMATTER.match(text)
    if m:
        text = text[m.end():]
    intro: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    in_fence = False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            sections.append((line[3:].strip(), []))
            continue
        (sections[-1][1] if sections else intro).append(line)
    intro_md = "\n".join(l for l in intro if not l.startswith("# "))
    return intro_md, [(h, "\n".join(b)) for h, b in sections]


def check(path: pathlib.Path):
    intro, sections = split(path.read_text())
    intro_lines = screen_lines(intro)
    flags, bites, first = [], [], None
    for heading, body in sections:
        if clean_heading(heading) in SKIPPED:
            if re.search(r"^###\s", body, re.M):
                flags.append(f"HIDDEN  '{heading}' has ### sections the app never shows")
            continue
        size = screen_lines(body)
        if first is None:
            first = heading
            size += intro_lines
        bites.append((heading, size))
    if intro_lines > 3.5:
        flags.append(f"INTRO   {intro_lines:.0f} lines above the first ## (sits on top of the first bite)")
    return first, bites, flags


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    verbose = "-v" in sys.argv
    prefix = args[0].rstrip("/") if args else ""
    lessons = [p for p in lesson_ids.all_lessons() if str(p).startswith(prefix)]

    n_long = n_border = n_lessons = 0
    for path in lessons:
        first, bites, flags = check(path)
        long = [(h, s) for h, s in bites if s > SCREEN]
        if not long and not flags and not verbose:
            continue
        n_lessons += 1
        print(f"\n{path}   (first bite: {first})")
        for f in flags:
            print(f"  {f}")
        for h, s in bites:
            if s > TOO_LONG:
                mark, n_long = "LONG  ", n_long + 1
            elif s > SCREEN:
                mark, n_border = "BORDER", n_border + 1
            elif verbose:
                mark = "ok    "
            else:
                continue
            print(f"  {mark}  {s:5.1f}  {h}")
    print(f"\n{len(lessons)} lessons checked; {n_lessons} listed; "
          f"{n_long} long bites (> {TOO_LONG} lines), {n_border} borderline ({SCREEN}-{TOO_LONG}). "
          f"One screen is about {SCREEN} lines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
