---
id: 21efb445-ce52-4705-b21c-84b065762857
---

# Python for Data

Python for data means using Python to load, clean, study and chart data.

## What Python for data is
<!-- bite: e811954d-2e67-4975-b7a0-0d959a09451f -->

Python for data is the way people use the Python programming language to load, clean, study and chart data. Python itself is not fast, but the tools built on it hand the heavy work to faster code underneath. Most data and AI work you hear about, from sales reports to the models behind chat apps, starts with a Python script like the ones in this lesson.

Next: why Python, the environment, and the idioms you will see in every data script.

## Why Python for data at all
<!-- bite: a138a61f-c060-4b7e-a323-8e070a790945 -->

Python is slow, but the data stack doesn't run *in* Python — NumPy/pandas/PyTorch are thin Python wrappers over optimized C/Fortran/CUDA. You write readable Python; the heavy loops execute in compiled code. So the skill isn't "write fast Python," it's "**push work down into the library's vectorized operations**" instead of looping in Python ([[machine-learning/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] is where this clicks). The ecosystem — not the language — is the reason it won data.

## The environment
<!-- bite: 455f4309-892d-415a-a0cb-706ec6f1d495 -->

- **Jupyter notebooks** — the default for exploration: run code in cells, keep state between them, see output (and plots) inline. Great for iterative data work; bad for anything that needs version control, testing, or reuse (cells run out of order cause "works on my machine" ghosts). Rule of thumb: **explore in a notebook, move reusable code to `.py` modules.**
- **Virtual environments** — isolate each project's dependencies. `python -m venv .venv && source .venv/bin/activate`, then `pip install`. **conda** is the data-world alternative that also manages non-Python deps (CUDA, system libs) — worth it for GPU/scientific setups. Never install into system Python.
- **The GPU headache** — deep-learning installs must match CUDA versions between the driver, the toolkit, and PyTorch/TF. The single most common setup failure; follow the framework's exact install command for your CUDA version rather than a plain `pip install`.

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy pandas matplotlib seaborn scikit-learn jupyter
jupyter lab                       # or use the VS Code / Cursor notebook UI
```

## The idioms that show up everywhere: comprehensions and slicing
<!-- bite: 4882000c-b2e3-4ff7-b6b1-32d26794d749 -->

These Python features are rare-ish in Java but constant in data code — internalize them:

**List/dict comprehensions** — the Pythonic transform-a-collection:

```python
squares = [x**2 for x in nums]                     # map
evens   = [x for x in nums if x % 2 == 0]          # filter
lookup  = {row["id"]: row for row in rows}          # dict comprehension
```

**Slicing** — `seq[start:stop:step]`, and it's everywhere (NumPy/pandas extend it heavily):

```python
xs[1:4]      # elements 1,2,3
xs[::-1]     # reversed
xs[-3:]      # last three
```

## More idioms: unpacking, small gotchas and typing
<!-- bite: 12498c7c-9619-4f14-8ca3-60a97996a55e -->

A few more Python habits you will see in almost every data script.

**Tuple unpacking / multiple assignment**:

```python
a, b = b, a                    # swap
for i, val in enumerate(xs):   # index + value
mean, std = compute_stats(x)   # unpack a returned tuple
```

**f-strings** for output, `zip` for parallel iteration, `*args/**kwargs`, and **truthiness** (empty containers are falsy: `if not df.empty`). Also: Python is **0-indexed**, `range(n)` is `0..n-1`, and `/` is float division while `//` is integer — small gotchas from other languages.

**Everything is an object, dynamic typing** — no compile step catches type errors; they surface at runtime. Type hints (`def f(x: int) -> float:`) are optional and *not enforced* (they're for tooling/readers), which surprises people coming from static languages. In data code you lean on quick iteration + inspection over the compiler.

## The workflow mindset
<!-- bite: 497477aa-57d0-4871-aafe-007cbe267507 -->

Data work is **interactive and inspect-as-you-go**, unlike compile-run-debug app development. You load a slice, look at it (`.head()`, `.shape`, `.dtypes`), transform, look again — a tight loop. Embracing that (rather than writing a big script and running it once) is the biggest adjustment from software engineering, and it's exactly what [[data-science/04-exploratory-data-analysis|EDA]] formalizes.

## Check your understanding
<!-- bite: 53bcd53d-34e6-46e6-a228-b319276762c1 -->

Try each one before you open the answer.

1. <!-- q: mcq id="490e392a" -->
   Python is slow. Why is it still the main language for data work?

   - [ ] Because it compiles to machine code
   - [x] Because libraries like NumPy and pandas do the heavy work in fast compiled code underneath
   - [ ] Because data scripts are always small

   <details><summary>Answer</summary>

   The heavy loops run in compiled C, Fortran or CUDA inside the libraries. Python is the readable glue. The skill is pushing work down into the library's vectorized operations.

   </details>

2. <!-- q: gap id="1b824b20" answers="[2, 3, 4]|[2,3,4]" -->
   Fill in the gap. `xs = [1, 2, 3, 4, 5]`, so `xs[1:4]` is ___.

   <details><summary>Answer</summary>

   `[2, 3, 4]`. The slice starts at index 1 and stops before index 4, and Python counts from 0.

   </details>

3. <!-- q: exact id="b2341c06" answer="3" accept="three" -->
   What does `7 // 2` give in Python?

   <details><summary>Answer</summary>

   3. `//` is integer division. `7 / 2` would give 3.5, because `/` is always float division.

   </details>

4. <!-- q: mcq id="a75df479" -->
   What is the recommended way to use Jupyter notebooks?

   - [ ] Write all your production code in them
   - [x] Explore in a notebook, then move reusable code into `.py` modules
   - [ ] Avoid them completely

   <details><summary>Answer</summary>

   Explore in the notebook, move reusable code to modules. Notebooks are great for looking at data, but cells run out of order cause "works on my machine" problems, and they are hard to test and version.

   </details>

5. <!-- q: open id="f3999d75" -->
   Why should every project get its own virtual environment instead of installing into system Python?

   <details><summary>Answer</summary>

   It keeps each project's dependencies separate, so one project's versions can't break another's or the system's own Python. You can also recreate the exact setup elsewhere.

   </details>

## Related
<!-- bite: 7b976390-b0d9-4523-95b7-34be5a4aecc3 -->
- [[machine-learning/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] — where "push work into the library" becomes concrete
- [[machine-learning/01-foundations-of-ml/02-the-ml-toolkit|The ML Toolkit]] — the full stack and why each piece exists

## About this lesson
<!-- bite: 346ca65e-9602-44e4-acc6-af49bfbdfadb -->

**Level:** reference / practice. **Covers:** written for someone who already codes. Not Python-the-language basics (you have those from other languages) — the *data-work* idioms and environment that trip people up coming from Java/JS.
