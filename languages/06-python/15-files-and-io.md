---
id: 3cdfc50f-338e-413f-a5bb-dee760196b0a
---

# Files and I/O

> **[Beginner → Intermediate]** · Reading and writing without corrupting data — encodings, modes, atomic writes, and the bytes/text boundary.

Named as a gap by this course's own README and confirmed by the [roadmap.sh Python track](https://roadmap.sh/python) (`file-handling`, `glob`).

## Always use `with`
<!-- bite: 5674c25c-2dd2-4692-8aeb-516a3a588d97 -->

```python
with open("data.txt") as f:
    content = f.read()
# closed here, exception or not
```

Without it you leak file handles — and a process has a limit (`ulimit -n`, often 1024). A long-running service that leaks handles dies with `OSError: Too many open files` hours after the actual bug → [[languages/06-python/07-decorators-and-context-managers|context managers]].

## Modes, and the one that destroys data
<!-- bite: d97cc4c0-2c53-49ac-9232-ef259e582037 -->

| Mode | Does | Missing file |
|---|---|---|
| `"r"` | read (default) | `FileNotFoundError` |
| `"w"` | write — **truncates to zero first** | creates |
| `"a"` | append | creates |
| `"x"` | **exclusive** create | creates; errors if it *exists* |
| `"r+"` | read and write | error |
| `+"b"` | binary — gives `bytes` | |

**`open(path, "w")` empties the file the moment it succeeds**, before you write anything. If your program then crashes, the original is gone. That's the most common way to lose data with Python, and the fix is the atomic write below.

**`"x"` is underused** — it's how you avoid a race between "does this exist?" and "create it", the same TOCTOU issue as [[languages/06-python/09-errors-and-exceptions|EAFP]].

## Encoding — always state it
<!-- bite: 55a71d80-e9d5-4dc2-b77c-43e3dc0410bb -->

```python
open("data.txt", encoding="utf-8")        # ✓ always
open("data.txt")                          # ✗ platform-dependent default
```

Without `encoding=`, Python uses the platform default — UTF-8 on modern Linux/macOS, but historically cp1252 on Windows. **The result is code that works on your laptop and raises `UnicodeDecodeError` in production**, or worse, silently mangles non-ASCII characters. Nigerian names, accented characters, emoji, currency symbols — all break.

(Python 3.15 moves toward UTF-8 as the default; `encoding=` is still the honest thing to write.)

Handling imperfect input:

```python
open(p, encoding="utf-8", errors="replace")   # bad bytes → U+FFFD
open(p, encoding="utf-8", errors="ignore")    # bad bytes dropped — data loss, be sure
open(p, newline="")                           # required for the csv module
```

## Text vs binary
<!-- bite: 362300df-c760-458c-a397-3bba7b11ec31 -->

**Text mode** decodes bytes to `str` and translates line endings. **Binary mode** gives raw `bytes`.

```python
with open("img.png", "rb") as f:
    header = f.read(8)          # bytes

with open("out.bin", "wb") as f:
    f.write(b"\x89PNG")
```

**Anything not text opens in binary**: images, PDFs, archives, protocol buffers, hashes. Opening a PNG in text mode corrupts it — the encoding layer mutates bytes that were never characters.

## Reading large files
<!-- bite: 20807228-7e70-43b4-994d-2487ca690302 -->

```python
with open("50gb.log") as f:
    for line in f:              # ✓ lazy — one line in memory
        process(line)
```

**A file object is already an iterator over lines.** `f.read()` and `f.readlines()` both load everything → [[languages/06-python/06-iterators-generators-and-comprehensions|generators]].

Fixed-size chunks, for binary:

```python
while chunk := f.read(64 * 1024):     # walrus operator
    hasher.update(chunk)
```

## pathlib, for everything else
<!-- bite: fbd5d8de-32e8-4f25-8525-08342e49a2cc -->

```python
from pathlib import Path

p = Path("data") / "raw" / "input.csv"
p.read_text(encoding="utf-8")
p.write_text(content, encoding="utf-8")
p.read_bytes(); p.write_bytes(data)

p.exists(); p.is_file(); p.is_dir()
p.stat().st_size; p.stat().st_mtime
p.suffix; p.stem; p.name; p.parent
p.mkdir(parents=True, exist_ok=True)
p.unlink(missing_ok=True)
p.rename(other); p.resolve()
```

**Globbing:**

```python
list(Path("data").glob("*.csv"))          # one level
list(Path("data").rglob("*.py"))          # recursive
list(Path(".").glob("**/*.json"))         # same as rglob
```

`glob` returns a generator — wrap in `list()` if you need it twice.

## Writing safely — the atomic pattern
<!-- bite: 5acbb6d7-3bf5-4469-ad54-8000d82f563e -->

The problem: a crash, a power cut, or a full disk mid-write leaves a **truncated file**, and the original is already gone. Readers see corruption.

```python
import os, tempfile
from pathlib import Path

def atomic_write(path: Path, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent)     # same filesystem — required
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())        # force to disk, not just the OS cache
        os.replace(tmp, path)           # ATOMIC rename on POSIX and Windows
    except BaseException:
        os.unlink(tmp)
        raise
```

**`os.replace` is atomic**: readers see either the old file or the new one, never a half-written one. The temp file must be on the *same filesystem*, or the rename becomes a copy and loses atomicity.

**This is exactly what databases do** — write elsewhere, flush, then atomically swap → [[databases/10-durability-and-recovery|durability and recovery]]. Any config file, cache or state file your program owns deserves this.

## Structured formats
<!-- bite: cd6c3492-7fb1-4659-800b-6e7e9081902e -->

```python
import json, csv

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

with open("out.csv", "w", newline="", encoding="utf-8") as f:    # newline="" matters
    w = csv.DictWriter(f, fieldnames=["name", "total"])
    w.writeheader()
    w.writerows(rows)
```

**`newline=""` is not optional for `csv`** — without it you get blank rows between records on Windows, because both Python and the csv module translate line endings.

**Never parse CSV by `line.split(",")`.** Quoted fields containing commas, embedded newlines and escaped quotes are all legal, and the `csv` module handles them.

## Temporary files and directories
<!-- bite: 352aa570-4982-4ef7-8b91-b1d406c0668f -->

```python
import tempfile

with tempfile.TemporaryDirectory() as d:
    work = Path(d) / "scratch.txt"
    ...
# directory and contents removed here, even on exception
```

**Never build a temp path by hand** in `/tmp` — it's a symlink-attack and collision surface → [[cybersecurity/06-attacks-and-threats/index|attacks]].

## Paths from users are dangerous
<!-- bite: 6d989e02-afda-43d5-a3ac-dfb3464946b1 -->

```python
target = (base / user_input).resolve()
if not target.is_relative_to(base.resolve()):     # 3.9+
    raise ValueError("path traversal attempt")
```

`user_input` of `../../etc/passwd` escapes your directory. **Path traversal is a top-tier web vulnerability**, and the defence is to resolve and then verify containment → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding/index|input validation]].

## Related
<!-- bite: 04367b21-478a-40ac-a38f-1c0dcd10bf8a -->
- [[languages/06-python/11-the-standard-library|the standard library]] — `pathlib`, `json`, `csv` in context
- [[languages/06-python/17-asyncio-in-depth|asyncio]] — why async file I/O barely exists
- [[os/07-filesystems-and-storage|filesystems and storage]] — what `fsync` actually does
- [[os/08-io-models|I/O models]] — blocking, non-blocking, io_uring

*Source: [reference] — from the Python docs; roadmap.sh-cross-referenced.*
