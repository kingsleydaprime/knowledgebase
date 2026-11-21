---
id: f5969b3a-1620-444d-b9f8-228f9e1f111a
---

# Modules, Packages and Imports

A module is a single Python file you can use from other files, a package is a folder of modules, and an import is the line that brings one into your code. Every `import` at the top of a Python script depends on these rules. Knowing how Python finds what you import saves you from confusing errors as a project grows.

## The vocabulary
<!-- bite: 915c27ee-31f2-4ae0-a5ed-c788de9719aa -->

- **Module** — one `.py` file
- **Package** — a directory of modules (with `__init__.py`, conventionally)
- **`__init__.py`** — runs when the package is imported. Often empty; that's fine and normal

```python
import json                          # whole module
import numpy as np                   # aliased
from pathlib import Path             # one name from it
from mypackage.utils import helper   # from a package
```

**Avoid `from module import *`.** It dumps unknown names into your namespace, shadows things silently, and makes it impossible to tell where a name came from. Linters flag it.

## How resolution works
<!-- bite: 80c002ba-12d7-4204-bd45-a6c7abe5fd38 -->

`import foo` searches `sys.path` **in order**:

1. The directory of the script being run (or the cwd for the REPL)
2. `PYTHONPATH`, if set
3. The standard library
4. `site-packages` (your venv)

**The first entry causes the classic beginner failure.** Name a file `random.py` or `json.py` in your project directory and it *shadows the standard library module* — your own file is found first, and the error message is baffling. Same for a stray `email.py` or `string.py`.

**Modules are cached in `sys.modules` and execute exactly once per process.** Import the same module from ten places and its top-level code runs once. This is why:

- Module-level code is effectively a singleton — the standard way to do one
- Editing a module mid-REPL-session doesn't take effect without `importlib.reload`
- Expensive work at module level slows every import of it, everywhere

## `if __name__ == "__main__":`
<!-- bite: d6d62e82-7f40-4160-b06a-48aa24a6b22c -->

```python
def main(): ...

if __name__ == "__main__":
    main()
```

`__name__` is `"__main__"` when the file is *run*, and the module's name when it's *imported*. So this block runs the script's behaviour on execution and stays quiet on import.

**Without it, importing your script executes it** — which is exactly what happens when a test file imports the module under test and suddenly your CLI runs. It also matters for `multiprocessing` on Windows and macOS, where child processes re-import the main module and will otherwise fork infinitely.

## Absolute and relative imports
<!-- bite: b404d2bc-3813-4870-8933-b0fbffa12f1d -->

```python
from mypackage.utils import helper       # absolute — preferred
from .utils import helper                # relative: same package
from ..core import thing                 # relative: parent package
```

**Prefer absolute imports.** They're unambiguous and don't break when a file moves. Relative imports are reasonable *within* a self-contained package, and they only work inside a package — a relative import in a directly-executed script raises `ImportError: attempted relative import with no known parent package`.

**The fix for that error is almost always `python -m package.module` rather than `python package/module.py`.** `-m` runs it with the package context set up.

## Circular imports
<!-- bite: c364e984-f51f-432d-be11-7f830364d334 -->

Two modules importing each other:

```python
# a.py
from b import thing_b
# b.py
from a import thing_a       # ImportError: cannot import name 'thing_a'
```

**Why:** importing `a` starts executing it, which imports `b`, which imports `a` — already in `sys.modules` but only **half-executed**, so `thing_a` doesn't exist yet.

Fixes, best first:

**Restructure.** A cycle is nearly always a design signal: the two modules share a concept that wants extracting into a third they both import. This is the real fix.

**Import inside the function**, deferring it to call time:

```python
def process():
    from b import thing_b       # runs when called, by which point b is loaded
```

**Import the module, not the name:**

```python
import b                        # binds the module object
def process(): return b.thing_b()   # attribute looked up at call time
```

**`if TYPE_CHECKING:`** for imports needed only by annotations — the checker sees them, the runtime doesn't:

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from b import ThingB

def f(x: "ThingB") -> None: ...
```

## Project layout
<!-- bite: 99b23f0c-a21c-41cb-91a3-19f8ef8b41ea -->

The `src/` layout, which is the current recommendation:

```text
my-project/
├── pyproject.toml
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
└── tests/
    └── test_core.py
```

**Why `src/` rather than the package at the top level:** with a top-level package, the project root is on `sys.path` when you run tests, so your tests import the *source directory* — which can pass while the actual installed package is broken (a missing file in the manifest, a bad `__init__`). With `src/`, tests can only import what's genuinely installed (`pip install -e .`), so you test what you ship.

**`__init__.py` as a public API** — re-export so callers get a stable surface:

```python
# src/mypackage/__init__.py
from mypackage.core import Engine, run
__all__ = ["Engine", "run"]
```

Now `from mypackage import Engine` works regardless of where `Engine` actually lives, and you can move it later without breaking anyone. `__all__` also defines what `import *` would take, and signals intent to readers and linters.

**Keep `__init__.py` cheap.** Heavy imports there are paid by everyone who touches any part of the package — a common cause of slow CLI startup.

## Related
<!-- bite: a7a9a325-f071-44b7-823c-fae64a6bd416 -->
- [[languages/06-python/01-why-python-and-the-toolchain|the toolchain]] — venvs and `pyproject.toml`
- [[languages/06-python/13-testing-and-tooling|testing]] — why layout and test imports interact
- [[languages/06-python/08-typing-and-type-hints|typing]] — `TYPE_CHECKING`
- [[backend/03-structuring-a-backend/index|structuring a backend]] — layout at application scale

## About this lesson
<!-- bite: e02f2692-1066-44df-9e8f-a26bfb83d087 -->

**Level:** Intermediate. **Covers:** How `import` actually resolves, why circular imports happen, and the project layout that avoids most import pain.

*Source: [reference] — from the Python import system docs and the Packaging User Guide.*
