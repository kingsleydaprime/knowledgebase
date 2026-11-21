---
id: bbc34816-ce4b-454f-b7bd-1c9439bee68c
---

# The Standard Library

Python ships a large standard library, and a real part of writing good Python is **knowing what's already there.** The failure mode isn't ignorance of syntax, it's hand-rolling something the stdlib does correctly.

## `pathlib` — always, over `os.path`
<!-- bite: 77730b13-4193-4b66-8fad-2186b1e9d918 -->

```python
from pathlib import Path

p = Path("data") / "raw" / "input.csv"     # the / operator joins, cross-platform
p.exists(); p.is_file(); p.suffix; p.stem; p.parent
p.read_text(); p.write_text(content)        # open/read/close in one call
p.mkdir(parents=True, exist_ok=True)
list(p.parent.glob("*.csv"))
list(Path(".").rglob("*.py"))               # recursive
```

**`pathlib` replaces `os.path` entirely** for new code — paths are objects with methods, not strings you `os.path.join`. It's what I reach for in every script in this vault.

## `datetime` — and the timezone rule
<!-- bite: 449353dc-f88b-467e-a591-c3644617051c -->

```python
from datetime import datetime, timezone, timedelta

datetime.now(timezone.utc)              # ✓ timezone-AWARE
datetime.now()                          # ✗ naive — no timezone attached
datetime.now(timezone.utc) + timedelta(days=7)
```

**The rule that prevents an entire bug class: store and compute in UTC, convert to local only for display.** A *naive* datetime (no tzinfo) is ambiguous, and comparing naive to aware raises `TypeError`.

`zoneinfo` (3.9+) gives you the IANA database without a dependency:

```python
from zoneinfo import ZoneInfo
datetime.now(ZoneInfo("Africa/Lagos"))
```

Use it rather than fixed UTC offsets — offsets don't know about daylight saving, and "UTC+1" is a different thing from "Europe/London".

## `json`
<!-- bite: 43c7c52f-2f79-4b7e-8727-beac6597ec52 -->

```python
import json
data = json.loads(text)                  # string  → Python
text = json.dumps(data, indent=2)        # Python → string
data = json.load(file_obj)               # note: load/dump take file objects
```

`json.dumps` fails on `datetime`, `Decimal`, `set` and your own classes — pass `default=str` for a quick fix, or a custom encoder for a real one. For anything with a schema, validate rather than trusting: `pydantic` → [[backend/frameworks/fastapi/01-fastapi|FastAPI]].

## `collections`, `itertools`, `functools`
<!-- bite: eede9f10-6f9c-41b1-bb32-9157e224f1ea -->

Covered in [[languages/06-python/03-built-in-types-and-collections|note 03]] and [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]]. The `functools` highlights:

```python
from functools import cache, lru_cache, partial, reduce, wraps, singledispatch

@cache                                   # memoise → note 07
partial(func, arg1)                      # pre-fill arguments; returns a new callable
reduce(operator.add, items)              # fold — usually sum()/math.prod() is clearer
```

## `dataclasses` and `enum`
<!-- bite: 0852e40a-eba3-4289-a056-221fdc215576 -->

```python
from enum import Enum, auto, StrEnum

class Status(StrEnum):                   # 3.11+; compares equal to its string value
    ACTIVE = "active"
    SUSPENDED = "suspended"
```

**Use an enum instead of magic strings.** Typos become `AttributeError` at the point of the mistake instead of a silent comparison that's always `False` — which is the kind of bug that survives code review.

## `subprocess`
<!-- bite: 2044fd4b-43dc-4401-b47d-27e56021ef19 -->

```python
import subprocess

result = subprocess.run(
    ["git", "status", "--short"],        # ✓ a LIST, not a string
    capture_output=True, text=True, check=True,
)
print(result.stdout)
```

Three things that matter:

- **Pass a list, not a string.** `shell=True` with interpolated input is command injection → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input validation]]
- **`check=True`** raises on a non-zero exit. Without it, failures are silent
- **`text=True`** gives you `str` instead of `bytes`

## `logging`
<!-- bite: cf6186d4-9193-4060-abec-36fca2b17040 -->

```python
import logging
log = logging.getLogger(__name__)        # ✓ per-module logger

log.info("processing %s items", count)   # lazy — %s formatted only if emitted
log.exception("failed")                  # inside except: includes the traceback
```

**Use `logging`, not `print`, for anything long-lived.** You get levels, timestamps, module names, and routing to files or a collector without changing call sites → [[devops/07-observability/index|observability]].

**Use `%s` placeholders rather than f-strings in log calls.** With an f-string the message is built even when the level is disabled; with placeholders it isn't. On a hot path that's real cost.

**Configure once, at the entry point** — never in a library module, which would hijack the application's configuration.

## `argparse`
<!-- bite: b724dbf5-e0a2-479f-ab7b-2443c572b89f -->

```python
import argparse
p = argparse.ArgumentParser(description="Process files.")
p.add_argument("input", type=Path)
p.add_argument("-v", "--verbose", action="store_true")
args = p.parse_args()
```

Free `--help`, type conversion and validation. For anything bigger, `click` or `typer` (third-party) are nicer, but `argparse` needs no dependency.

## The rest, by problem
<!-- bite: dc78a9bd-36ef-41ae-8b94-3802ef04cecb -->

| Need | Module |
|---|---|
| CSV | `csv` |
| SQL, zero setup | `sqlite3` → [[databases/index\|databases]] |
| Hashing, HMAC | `hashlib`, `hmac`, `secrets` |
| **Tokens, passwords** | **`secrets`** — never `random` |
| Regular expressions | `re` |
| Temp files/dirs | `tempfile` |
| Zip/tar | `zipfile`, `tarfile` |
| Config files | `configparser`, `tomllib` (3.11+, read-only) |
| Decimal money | `decimal` → [[mathematics/07-applied-and-computational/01-numerical-methods/02-floating-point-and-error\|floating point]] |
| Concurrency | `threading`, `asyncio`, `multiprocessing`, `concurrent.futures` → note 12 |
| Timing/profiling | `time.perf_counter`, `timeit`, `cProfile` → note 14 |
| Tests | `unittest` (but use `pytest`) → note 13 |

**`secrets` vs `random` is a security bug waiting to happen.** `random` is a Mersenne Twister — fast, reproducible, and **predictable from a few outputs**. Use `secrets` for tokens, passwords, session IDs and anything an attacker benefits from guessing → [[cybersecurity/05-cryptography/index|cryptography]].

## What's not in the box
<!-- bite: 07530115-d50a-4624-a983-d97ec5348d87 -->

Notably: HTTP clients (`urllib` exists and is unpleasant — use `requests` or `httpx`), a good CLI framework, an ORM, and anything numeric. The community defaults are so standard they're effectively part of the language.

**The stdlib also has genuinely dated corners.** Prefer `pathlib` over `os.path`, `subprocess.run` over `os.system`, `secrets` over `random` for anything sensitive, and `zoneinfo` over `pytz`.

## Related
<!-- bite: 4abdb43b-49fd-4251-bd00-2e5ad43d9228 -->
- [[languages/06-python/12-concurrency-and-the-gil|concurrency]] — `asyncio` and friends
- [[languages/06-python/13-testing-and-tooling|testing and tooling]] — the third-party layer
- [[devops/01-linux/12-bash-scripting|bash scripting]] — when a shell script should have been Python
- [[ai-ml/00-foundations/04-python-and-data-tools/index|Python for data]] — the numeric stack

## About this lesson
<!-- bite: 9664a42e-0e3e-41bd-9ee3-a64997ffb50c -->

**Level:** Intermediate. **Covers:** "Batteries included" — the modules worth knowing by name, and the ones that have been superseded.

*Source: [reference] — from the Python standard library documentation.*
