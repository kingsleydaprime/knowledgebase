# Practice Exercises

> **[Beginner → Advanced]** · Eighteen exercises over the whole course. **Every one reproduces a real Python behaviour rather than describing it.**

The course's honest note named exercises as the remaining hole. This is it.

**Almost all of these are provable in a REPL or a ten-line script** — the point is to *see* the behaviour, because a gotcha you've reproduced is one you'll recognise at 2 a.m. and a gotcha you've read about is one you'll ship.

Solutions in [[languages/06-python/19-practice-exercises-solutions|note 19]]. **Try each first** — several are surprising, and the surprise is the mechanism.

**Setup:** Python 3.11+, a virtual environment, and `pip install pytest mypy ruff httpx` when you reach the parts that need them.

---

## Part A — The data model (notes 01–04)

**1. Break your own environment, then fix it.**
In one venv, `pip install "requests==2.28.0"`. In a second venv, install `requests==2.31.0`. Show both installed simultaneously and independently. Then run `pip list` in each and outside both.
**Done when:** you can explain what `activate` actually changed (hint: `which python`, `echo $PATH`) → [[languages/06-python/01-why-python-and-the-toolchain|note 01]].

**2. Make `is` lie to you.**
In an **interactive REPL** (this matters), enter `a = 257` and `b = 257` on separate lines, then `a is b`. Repeat with `256`. Now put the same four lines in a **script** and run it — you'll get a different answer. Finally, in the script, try `a = int("257"); b = int("257"); a is b`.
**Done when:** you have three different results from code that means the same thing, and can explain why the script differs from the REPL. **This is the exercise that should permanently stop you writing `is` for value comparison** → [[languages/06-python/02-the-data-model|note 02]].

**3. Catch the mutable default in the act.**
Write `def add(item, basket=[])`, call it three times, and print the result each time. Then print `add.__defaults__` and explain what you're looking at. Fix it.
**Done when:** you've seen the accumulating list *and* inspected the function object holding it → [[languages/06-python/02-the-data-model|note 02]].

**4. Defeat your own copy.**
Take `grid = [[1,2],[3,4]]`. Copy it three ways (`.copy()`, `list(grid)`, `grid[:]`), mutate an inner list, and show all three "copies" changed. Then fix it, and time `copy.deepcopy` on a 10,000-element nested structure.
**Done when:** you can state what shallow copies and why deep copying isn't the default → [[languages/06-python/02-the-data-model|note 02]].

**5. Trigger `UnboundLocalError` deliberately.**
Write a function that reads a module-level counter and increments it. Watch it fail *before printing anything*. Then fix it three ways: `global`, passing-and-returning, and a class.
**Done when:** you can explain why the error happens on the read, given the assignment is on the same line → [[languages/06-python/04-functions-and-scope|note 04]].

**6. Get `[2, 2, 2]` from a loop over `range(3)`.**
Build a list of lambdas in a comprehension that each return the loop variable. Call them all.
**Done when:** you've reproduced the late-binding result, fixed it with a default argument, and can say what the closure captured → [[languages/06-python/04-functions-and-scope|note 04]].

---

## Part B — Idioms (notes 05–08)

**7. Break a set with a bad class.**
Write a `Point` with `__eq__` comparing x and y, and **no** `__hash__`. Put one in a set. Then add `__hash__`, put two equal points in a set, and check the length.
**Done when:** you've seen the `TypeError`, know what Python did to `__hash__` when you defined `__eq__`, and the set of two equal points has length 1 → [[languages/06-python/05-classes-and-the-object-model|note 05]].

**8. Get Python to protect you, once.**
Write `@dataclass class Cart: items: list = []`. Run it.
**Done when:** you've read the error, and can say why the dataclass machinery can catch this when a plain `def` cannot → [[languages/06-python/05-classes-and-the-object-model|note 05]].

**9. Measure the memory difference laziness buys.**
Build `[x*x for x in range(5_000_000)]` and measure the process's memory. Do the same with a generator expression. Then `sum()` both.
**Done when:** you have two memory figures roughly three orders of magnitude apart and identical sums → [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]].

**10. Consume a generator twice.**
Write a function returning a generator of the lines in a file. Call `sum(1 for _ in gen)` then `list(gen)`.
**Done when:** the second returns empty, you understand why, and you've written a version where calling it twice works → [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]].

**11. Ruin a traceback, then repair it.**
Write a logging decorator **without** `@functools.wraps`. Decorate a function, raise inside it, and read the traceback and `func.__name__`. Add `@wraps` and compare.
**Done when:** you can point at exactly what changed in the traceback and in `help(func)` → [[languages/06-python/07-decorators-and-context-managers|note 07]].

**12. Write a context manager that survives an exception.**
Build a `@contextmanager` timer that prints elapsed time. Test it on a block that raises. Then remove the `try/finally` and test again.
**Done when:** you've seen the timing *not print* without `finally`, which is the whole reason the pattern exists → [[languages/06-python/07-decorators-and-context-managers|note 07]].

**13. Let a type checker find a real bug.**
Take any script of yours over ~100 lines. `pip install mypy`, run it, and count the findings. Fix the `None`-related ones.
**Done when:** you have a count, and at least one finding is a genuine bug rather than a missing annotation. **If mypy finds nothing, your script is too small** → [[languages/06-python/08-typing-and-type-hints|note 08]].

---

## Part C — Real Python (notes 09–17)

**14. Lose a file to `"w"`, then make it atomic.**
Write a script that opens a file with `"w"` and then raises before writing. Show the original is gone. Then implement the temp-file + `os.replace` pattern and repeat.
**Done when:** the naive version destroys data and yours doesn't → [[languages/06-python/15-files-and-io|note 15]].

**15. Build a circular import, then fix it three ways.**
Two modules importing a name from each other. Reproduce the `ImportError`. Fix it by (a) extracting a third module, (b) importing inside the function, (c) `import module` rather than `from module import name`.
**Done when:** you can say which fix you'd actually use and why the error message mentions a *partially initialised* module → [[languages/06-python/10-modules-packages-and-imports|note 10]].

**16. Hang your own program with a regex.**
Time `re.match(r"(a+)+$", "a" * n + "b")` for n = 15, 20, 25, 28.
**Done when:** you have four timings showing roughly doubling per step, and can explain why an *almost*-matching input is the worst case → [[languages/06-python/16-regular-expressions|note 16]].

**17. Prove the GIL exists, then defeat it.**
Write a CPU-bound function (a tight numeric loop). Run it: serially ×4, in 4 threads, and in 4 processes. Time all three. Then repeat with an **I/O-bound** function (`time.sleep(1)`).
**Done when:** you have six timings, and the threading result flips between the two workloads. **This is the single most valuable exercise here** → [[languages/06-python/12-concurrency-and-the-gil|note 12]].

**18. Make async actually concurrent, then break it.**
With `httpx.AsyncClient`, fetch 10 URLs with sequential `await`s and time it. Switch to `asyncio.gather` and time again. Then insert a single `time.sleep(2)` into one coroutine and observe the effect on the others.
**Done when:** you have three timings, and the blocking call demonstrably froze tasks that had nothing to do with it → [[languages/06-python/17-asyncio-in-depth|note 17]].

---

## Then

**Build something.** These are reps → [[foundations/programming-fundamentals/12-choosing-what-to-build-next|what to build next]].

## Related
- [[languages/06-python/19-practice-exercises-solutions|Solutions]] — after you've tried
- [[languages/06-python/README|the course]]
- [[learning/06-ai-as-sparring-partner|AI as sparring partner]]

*Source: [reference] — written Aug 2026 to close the gap this course's README named.*
