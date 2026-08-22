# Python

The language and its core ecosystem. **Not the data stack** — that lives in [[ai-ml/00-foundations/04-python-and-data-tools/README|ai-ml/00-foundations]] — and **not the web frameworks**, which live in [[backend/frameworks/python/README|backend/frameworks/python/]] per [[languages/README|the rule]].

**~12,600 words across 14 notes.** Built August 2026. `[reference]`.

> **The one idea:** Python trades machine time for programmer time, and **every quirk in this course is that trade showing through.** Names bind to objects (so assignment aliases), types are checked at runtime (so errors reach production), and one lock protects the interpreter (so threads don't parallelise). Knowing *why* turns a list of gotchas into one model.

## Why this exists

[[languages/README|languages/README]] listed "Python at depth" as a track that would slot in *if notes got written*. They hadn't been — despite Python appearing throughout the vault: the [[ai-ml/README|entire ML domain]] is written in it, [[devops/README|devops]] assumes it for automation, and [[foundations/programming-fundamentals/README|programming fundamentals]] uses it for most examples.

**So the vault taught Python-the-tool everywhere and Python-the-language nowhere.** This closes that.

## Reading order

**01–04 are the model and are worth reading in order.** 05–11 are the language's features and can be dipped into. 12–14 are the runtime, and assume the rest.

1. [[languages/06-python/01-why-python-and-the-toolchain|Why Python, and the Toolchain]] — **[Beginner]** — what it's for, versions, and **virtual environments, which is where beginners lose days**
2. [[languages/06-python/02-the-data-model|The Data Model]] — **[Beginner → Intermediate]** — names bind to objects; `is` vs `==`, copying, truthiness, and **the mutable default argument**
3. [[languages/06-python/03-built-in-types-and-collections|Built-in Types and Collections]] — **[Beginner]** — str/list/dict/set costs, comprehensions, and **the `collections` types that are usually the better answer**
4. [[languages/06-python/04-functions-and-scope|Functions and Scope]] — **[Beginner → Intermediate]** — `*args`/`**kwargs`, LEGB, closures, and **the late-binding trap**
5. [[languages/06-python/05-classes-and-the-object-model|Classes and the Object Model]] — **[Intermediate]** — dunder methods as protocols, properties, dataclasses, the MRO
6. [[languages/06-python/06-iterators-generators-and-comprehensions|Iterators, Generators and Laziness]] — **[Intermediate]** — the protocol behind every `for`, and **processing a file bigger than RAM**
7. [[languages/06-python/07-decorators-and-context-managers|Decorators and Context Managers]] — **[Intermediate]** — the two idioms every real codebase uses
8. [[languages/06-python/08-typing-and-type-hints|Typing and Type Hints]] — **[Intermediate]** — gradual typing, `Protocol`, narrowing, **and how to adopt it without a revolt**
9. [[languages/06-python/09-errors-and-exceptions|Errors and Exceptions]] — **[Intermediate]** — EAFP, the hierarchy, chaining, **and why `except: pass` is the worst line in Python**
10. [[languages/06-python/10-modules-packages-and-imports|Modules, Packages and Imports]] — **[Intermediate]** — how resolution works, circular imports, and **why `src/` layout**
11. [[languages/06-python/11-the-standard-library|The Standard Library]] — **[Intermediate]** — what's already there, and what's been superseded
12. [[languages/06-python/12-concurrency-and-the-gil|Concurrency and the GIL]] — **[Advanced]** — why threads don't speed up computation, choosing between the three models, **and PEP 703**
13. [[languages/06-python/13-testing-and-tooling|Testing and Tooling]] — **[Intermediate]** — pytest, fixtures, `parametrize`, ruff, and the pre-commit/CI split
14. [[languages/06-python/14-performance-and-the-runtime|Performance and the Runtime]] — **[Advanced]** — why it's slow, and **the ordered list of what to try**

## The things worth carrying

1. **Assignment binds a name; it never copies.** Whether you notice depends only on whether the object is mutable → [[languages/06-python/02-the-data-model|02]]
2. **Default arguments are evaluated once, at definition.** Hence `def f(x, acc=[])` is broken → [[languages/06-python/02-the-data-model|02]]
3. **`is` is for `None`, `True`, `False` and nothing else** → [[languages/06-python/02-the-data-model|02]]
4. **`x in list` is O(n); `x in set` is O(1).** Inside a loop that's the whole performance story → [[languages/06-python/03-built-in-types-and-collections|03]]
5. **`Counter`, `defaultdict` and `deque` remove most hand-written dictionary and queue code** → [[languages/06-python/03-built-in-types-and-collections|03]]
6. **Assigning to a name anywhere in a function makes it local everywhere in that function** → [[languages/06-python/04-functions-and-scope|04]]
7. **Closures capture the variable, not its value** → [[languages/06-python/04-functions-and-scope|04]]
8. **Behaviour is opted into by implementing dunder methods, not by declaring an interface.** Always define `__repr__` → [[languages/06-python/05-classes-and-the-object-model|05]]
9. **Properties are why Python has no getters and setters** — you can convert an attribute later without breaking callers → [[languages/06-python/05-classes-and-the-object-model|05]]
10. **A generator is consumed once.** The commonest generator bug, and it shows up as an empty result far from the cause → [[languages/06-python/06-iterators-generators-and-comprehensions|06]]
11. **`@functools.wraps` or your tracebacks all say `wrapper`** → [[languages/06-python/07-decorators-and-context-managers|07]]
12. **Type hints are ignored at runtime.** Validate at the boundary anyway → [[languages/06-python/08-typing-and-type-hints|08]]
13. **EAFP beats LBYL because the check-then-act version has a race** → [[languages/06-python/09-errors-and-exceptions|09]]
14. **`raise ... from e`**, and **`log.exception()`** inside a handler → [[languages/06-python/09-errors-and-exceptions|09]]
15. **A circular import is a design signal**, not a syntax problem → [[languages/06-python/10-modules-packages-and-imports|10]]
16. **`secrets`, never `random`, for anything an attacker would like to guess** → [[languages/06-python/11-the-standard-library|11]]
17. **The GIL is released during I/O.** Threads are useless for computation and excellent for waiting → [[languages/06-python/12-concurrency-and-the-gil|12]]
18. **One blocking call freezes the entire event loop** → [[languages/06-python/12-concurrency-and-the-gil|12]]
19. **`parametrize` is the highest-return pytest feature** — it makes edge cases cheap enough to actually write → [[languages/06-python/13-testing-and-tooling|13]]
20. **Coverage measures what ran, not what was checked** → [[languages/06-python/13-testing-and-tooling|13]]
21. **Fix the algorithm, then the I/O, then vectorise. Measure between each** → [[languages/06-python/14-performance-and-the-runtime|14]]

## Where this connects

| | |
|---|---|
| [[backend/frameworks/python/README\|backend/frameworks/python/]] | FastAPI, Django, Flask — **the frameworks, per the languages/ rule** |
| [[ai-ml/00-foundations/04-python-and-data-tools/README\|Python for data]] | NumPy, pandas, matplotlib — the numeric stack |
| [[foundations/programming-fundamentals/README\|programming fundamentals]] | **If this is your first language, start there** |
| [[devops/01-linux/12-bash-scripting\|bash scripting]] | When a shell script should have been Python |
| [[languages/02-go/README\|Go]] · [[languages/03-rust/README\|Rust]] | The other end of the trade — types and concurrency enforced |
| [[foundations/compilers/README\|compilers]] | What "bytecode on a VM" means |

## The honest note

**`[reference]`, but less so than most of this vault** — Python is the language I actually reach for, and the [[ai-ml/README|ML domain]] and assorted automation are written in it. What's read-not-lived is specifically: the free-threaded build, PyPy, Cython/PyO3, and `multiprocessing` at any real scale.

**What would close the gap:**

1. **Reproduce the mutable-default and late-binding traps in a REPL.** Two minutes, and notes 02 and 04 stop being warnings and become memories
2. **Profile something real** with `cProfile`, then `line_profiler` on the hot function. **Then fix it and measure again.** Note 14 is worthless without the second measurement
3. **Take one loop and vectorise it** with NumPy. Time both. The 10–100× is the claim; verify it
4. **Add `mypy` to one existing module** and count what it finds. That number is the argument for note 08
5. **Write a decorator with arguments** from scratch, without copying. Three levels of nesting is the part that doesn't stick from reading
6. **Benchmark `threading` vs `multiprocessing`** on one CPU-bound and one I/O-bound task. Note 12's table, verified in ten minutes

**What's missing:** metaclasses and descriptors (deliberately — rarely needed, frequently misused), `async` generators and `asyncio` at depth, packaging *as a publisher* (building and uploading to PyPI), C-extension authoring, and exercises.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[languages/README|languages/]] — the domain index
- [[backend/frameworks/python/README|Python backends]]
- [[BUILD-PLAN|Build Plan]]
