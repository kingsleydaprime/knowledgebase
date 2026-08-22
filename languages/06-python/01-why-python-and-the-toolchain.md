# Why Python, and the Toolchain

> **[Beginner]** · What Python is for, what it's bad at, and the environment/packaging story that causes more pain than the language does.

Python's pitch is **programmer time over machine time**. It is one of the slowest mainstream languages at raw execution and one of the fastest to write, read and change. Every design decision follows from that trade, and so does every complaint about it.

**Where it wins:** data and ML (an ecosystem nothing else comes close to), scripting and automation, glue between systems, backends where I/O dominates, scientific computing, anything where the bottleneck is understanding the problem rather than executing the solution.

**Where it doesn't:** CPU-bound work in pure Python, hard latency requirements, memory-constrained environments, mobile, and — honestly — large codebases without type hints and discipline, because a dynamic language lets errors reach runtime that [[languages/03-rust/README|Rust]] or [[languages/01-java/README|Java]] would refuse to compile.

**The tell that this is a real trade, not a weakness:** NumPy, pandas and PyTorch are Python interfaces over C, C++, Fortran and CUDA. Python is the *steering* language; the numeric work happens in compiled code → [[languages/06-python/14-performance-and-the-runtime|note 14]]. Used that way, "Python is slow" is close to irrelevant.

## The implementations

**CPython** is the reference implementation and what you almost certainly have. Written in C, compiles source to bytecode, runs it on a stack machine. When people say "Python", they mean this.

Others worth knowing exist: **PyPy** (a JIT, often several times faster on pure-Python workloads), **MicroPython** (microcontrollers → [[hardware/README|hardware]]), and **Jython**/**IronPython** (JVM/.NET, largely historical).

## Versions

Python 2 is dead — if you meet it, it's a migration job, not a choice. Within Python 3, versions matter more than beginners expect because each release brings real syntax and real performance:

| Version | Brought |
|---|---|
| 3.6 | f-strings — the single nicest quality-of-life change |
| 3.8 | the walrus operator `:=`, positional-only params |
| 3.10 | **structural pattern matching** (`match`), better error messages |
| 3.11 | **~25% faster** across the board, exception groups |
| 3.12 | cleaner generic syntax, per-interpreter GIL groundwork |
| 3.13 | **experimental free-threaded build (no GIL)** and a basic JIT |

**Target the oldest version you must support, and know what you're giving up.** → [[languages/06-python/12-concurrency-and-the-gil|note 12]] on why the free-threaded build matters more than it sounds.

## Virtual environments — the concept to get right immediately

**This is where beginners lose days**, and the underlying idea is simple.

By default `pip install` puts packages in a **single system-wide location**. Two projects needing different versions of the same library therefore conflict, and the second install silently breaks the first.

A **virtual environment** is a directory containing its own interpreter link and its own `site-packages`. Activate it and `python` and `pip` resolve to that directory instead of the system.

```bash
python3 -m venv .venv          # create it (a .venv/ directory appears)
source .venv/bin/activate      # activate — prompt changes to show it
pip install requests
deactivate                     # leave
```

**Rules that save the days:**

- **One venv per project.** Always. There is no project small enough to skip it
- **Never `sudo pip install`.** You're modifying the interpreter your OS depends on. On some distributions this genuinely breaks system tooling
- **`.venv/` goes in `.gitignore`.** It's build output, not source
- **The lockfile is what's shared**, not the environment

## Packaging, and why it has a reputation

Python's packaging story is genuinely worse than Go's or Rust's, for a historical reason: `pip` and `setuptools` predate the modern consensus, and everything since has been additive rather than replacing.

**The current state, in one table:**

| Tool | What it is | Use it when |
|---|---|---|
| **pip** + **venv** | The built-in baseline | Always available, zero setup |
| **uv** | Rust-written pip/venv replacement | **The current recommendation** — 10–100× faster, resolves and locks properly |
| **Poetry** | Dependency management + packaging | Established, good lockfiles, slower |
| **conda** | Package *and* environment manager, non-Python deps too | Scientific stacks with C/CUDA/Fortran dependencies |
| **pipx** | Installs CLI tools in isolated envs | Anything you run as a command, not import |

**`pyproject.toml` is the modern, standardised project file** (PEP 518/621), and it replaced the `setup.py`/`setup.cfg`/`requirements.txt` sprawl:

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["requests>=2.31", "pydantic>=2.0"]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]
```

**The distinction that matters and gets missed:** `pyproject.toml` declares *ranges you accept*; a **lockfile** records *exact versions you resolved*, transitively, with hashes. An application wants both — the lockfile is what makes a deploy reproducible. A library ships only the ranges, because pinning a library's dependencies makes it unusable alongside anything else.

## The REPL

Python's interactive prompt is a genuine part of the workflow, not a toy:

```
>>> import pathlib
>>> pathlib.Path(".").glob("*.md")
<generator object ...>          # ← tells you it's lazy, before you're confused later
>>> help(str.split)
```

`python3 -i script.py` runs a script and **drops you into a REPL with its state still loaded** — frequently faster than adding print statements. → [[foundations/programming-fundamentals/03-where-code-gets-written|where code gets written]].

## The philosophy, and where it bends

`import this` prints the Zen of Python. The lines that actually shape the language:

- *Explicit is better than implicit* — why there's no `this`, and `self` is a real parameter
- *There should be one — and preferably only one — obvious way to do it* — the deliberate contrast with Perl and, increasingly, an aspiration rather than a description
- *Readability counts* — why significant indentation is enforced and not merely conventional

The word for code that follows the community's grain is **Pythonic**, and it's a real standard: a loop over `range(len(items))` is *correct* and will be flagged in review, because `enumerate` exists. Most of this course is about which idioms those are.

## Related
- [[languages/06-python/02-the-data-model|the data model]] — the idea everything else follows from
- [[languages/06-python/13-testing-and-tooling|testing and tooling]] — ruff, mypy, pytest
- [[languages/06-python/14-performance-and-the-runtime|performance]] — what CPython is actually doing
- [[foundations/programming-fundamentals/README|programming fundamentals]] — if this is your first language
- [[ai-ml/00-foundations/04-python-and-data-tools/README|Python for data]] — the numeric stack, elsewhere in this vault

*Source: [reference] — from the official docs, PEPs, and the packaging ecosystem's own guidance.*
