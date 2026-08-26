# Regular Expressions

> **[Intermediate]** · The `re` module, the syntax worth memorising, and the performance cliff that has taken down real websites.

Named in the [roadmap.sh Python track](https://roadmap.sh/python) and previously a one-line mention in this course. Regex is a language in its own right → [[foundations/theory-of-computation/03-regular-languages|regular languages]] explains what it can and cannot express, and [[build-your-own-shit/09-your-own-regex-engine|build your own regex engine]] builds one.

## Always use raw strings

```python
import re
re.search(r"\d+", text)        # ✓ raw string
re.search("\d+", text)         # ✗ Python parses \d first — a DeprecationWarning today
```

`r"..."` stops Python interpreting backslashes so the regex engine sees them. **Use it for every pattern, without thinking about it.**

## The syntax worth knowing

| | Matches |
|---|---|
| `.` | any char except newline |
| `\d` `\w` `\s` | digit, word char, whitespace |
| `\D` `\W` `\S` | the negations |
| `[abc]` `[^abc]` | set, negated set |
| `[a-z]` | range |
| `*` `+` `?` | 0+, 1+, 0 or 1 |
| `{n}` `{n,m}` | exactly n, between n and m |
| `^` `$` | start, end (of string, or line with `re.M`) |
| `\b` | **word boundary** |
| `(...)` | capturing group |
| `(?:...)` | **non-capturing** group |
| `(?P<name>...)` | **named** group |
| `\|` | alternation |
| `(?=...)` `(?!...)` | lookahead, negative lookahead |

**`\b` is the one beginners miss.** `r"cat"` matches inside "concatenate"; `r"\bcat\b"` doesn't.

## The functions

```python
re.search(p, s)      # first match anywhere → Match or None
re.match(p, s)       # match at the START only  ← not "does it match"
re.fullmatch(p, s)   # the WHOLE string must match ← usually what validation wants
re.findall(p, s)     # list of all matches (or of groups, if the pattern has any)
re.finditer(p, s)    # iterator of Match objects — better for large input
re.sub(p, repl, s)   # replace
re.split(p, s)       # split on a pattern
```

**`re.match` does not mean "does this match".** It anchors at position 0 only, and using it for validation accepts `"12345abc"` for a digits pattern. **Use `re.fullmatch`.**

**`findall` changes its return type when the pattern has groups** — it returns the groups, not the whole matches. Surprising, documented, and a frequent bug. `finditer` is predictable.

## Groups

```python
m = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})", "2026-08-22")
m.group()            # '2026-08'  — the whole match
m.group("year")      # '2026'
m.groupdict()        # {'year': '2026', 'month': '08'}
m.span()             # (0, 7)
```

**Name your groups** once there's more than one. `m.group(3)` is unreadable and breaks when someone inserts a group.

**Use `(?:...)` when you group for structure but don't need the capture** — it's clearer and marginally faster.

## Compile when reusing

```python
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)

for line in huge_file:
    if EMAIL.fullmatch(line): ...
```

`re` caches compiled patterns, so this is about clarity more than speed — a module-level constant names the pattern and keeps it out of the loop.

**Flags:** `re.I` ignorecase, `re.M` multiline (`^`/`$` per line), `re.S` dotall (`.` matches newline), `re.X` verbose — which is how you make a long pattern readable:

```python
DATE = re.compile(r"""
    (?P<year>\d{4})  -     # year
    (?P<month>\d{2}) -     # month
    (?P<day>\d{2})         # day
""", re.X)
```

## Catastrophic backtracking

**The part with real consequences.** Python's `re` is a backtracking engine, so certain patterns take exponential time on inputs that *nearly* match:

```python
re.match(r"(a+)+$", "a" * 30 + "b")     # effectively hangs
```

Nested quantifiers (`(a+)+`, `(a*)*`, `(\s|\w)+`) give the engine exponentially many ways to split the input, and it tries all of them before failing.

**This is a real denial-of-service class — ReDoS** — and it has caused documented multi-hour outages at Cloudflare and Stack Overflow, both from a regex in production. If your pattern touches user input, this is a security property, not a performance note → [[cybersecurity/06-attacks-and-threats/README|attacks]].

**Defences:**
- Avoid nested quantifiers; make alternations unambiguous
- Anchor patterns (`^...$`) so failure is detected early
- Cap input length before matching
- Use the third-party `regex` module, which supports a timeout, or `re2` (Google's), which is linear-time by construction because it refuses backreferences

## When not to use regex

**The instinct to reach for it is usually wrong**, and the alternatives are faster *and* more readable:

```python
"error" in line                       # not re.search
line.startswith("GET ")               # not ^GET
line.split(",")                       # not a regex split
Path(f).suffix == ".csv"              # not a filename pattern
```

**Never parse HTML, XML or JSON with regex.** They're nested structures; regex describes regular languages, which by definition cannot count nesting depth → [[foundations/theory-of-computation/04-context-free-languages|context-free languages]]. Use a parser: `lxml`, `BeautifulSoup`, `json`.

**And for real formats, prefer the real library.** Email addresses, URLs and dates all have specifications far messier than any pattern you'll write — an RFC-5322-compliant email regex is thousands of characters and still wrong. Validate by *sending* the email.

## The pragmatic rule

**If the pattern needs a comment to be understood, and it isn't in `re.X` form, it's too clever.** A three-line loop that a colleague can read at 3 a.m. beats a 90-character pattern that nobody dares change.

## Related
- [[foundations/theory-of-computation/03-regular-languages|regular languages]] — what regex provably can't do
- [[build-your-own-shit/09-your-own-regex-engine|build your own regex engine]] — where this stops being reading
- [[devops/01-linux/16-sed-and-awk|sed and awk]] — regex at the shell
- [[cybersecurity/06-attacks-and-threats/README|attacks and threats]] — ReDoS

*Source: [reference] — from the `re` documentation; roadmap.sh-cross-referenced.*
