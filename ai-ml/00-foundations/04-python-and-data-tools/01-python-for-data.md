# Python for Data

**[reference / practice]** — written for someone who already codes. Not Python-the-language basics (you have those from other languages) — the *data-work* idioms and environment that trip people up coming from Java/JS.

## Why Python for data at all

Python is slow, but the data stack doesn't run *in* Python — NumPy/pandas/PyTorch are thin Python wrappers over optimized C/Fortran/CUDA. You write readable Python; the heavy loops execute in compiled code. So the skill isn't "write fast Python," it's "**push work down into the library's vectorized operations**" instead of looping in Python ([[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] is where this clicks). The ecosystem — not the language — is the reason it won data.

## The environment

- **Jupyter notebooks** — the default for exploration: run code in cells, keep state between them, see output (and plots) inline. Great for iterative data work; bad for anything that needs version control, testing, or reuse (cells run out of order cause "works on my machine" ghosts). Rule of thumb: **explore in a notebook, move reusable code to `.py` modules.**
- **Virtual environments** — isolate each project's dependencies. `python -m venv .venv && source .venv/bin/activate`, then `pip install`. **conda** is the data-world alternative that also manages non-Python deps (CUDA, system libs) — worth it for GPU/scientific setups. Never install into system Python.
- **The GPU headache** — deep-learning installs must match CUDA versions between the driver, the toolkit, and PyTorch/TF. The single most common setup failure; follow the framework's exact install command for your CUDA version rather than a plain `pip install`.

```bash
python -m venv .venv && source .venv/bin/activate
pip install numpy pandas matplotlib seaborn scikit-learn jupyter
jupyter lab                       # or use the VS Code / Cursor notebook UI
```

## The idioms that show up everywhere

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

**Tuple unpacking / multiple assignment**:

```python
a, b = b, a                    # swap
for i, val in enumerate(xs):   # index + value
mean, std = compute_stats(x)   # unpack a returned tuple
```

**f-strings** for output, `zip` for parallel iteration, `*args/**kwargs`, and **truthiness** (empty containers are falsy: `if not df.empty`). Also: Python is **0-indexed**, `range(n)` is `0..n-1`, and `/` is float division while `//` is integer — small gotchas from other languages.

**Everything is an object, dynamic typing** — no compile step catches type errors; they surface at runtime. Type hints (`def f(x: int) -> float:`) are optional and *not enforced* (they're for tooling/readers), which surprises people coming from static languages. In data code you lean on quick iteration + inspection over the compiler.

## The workflow mindset

Data work is **interactive and inspect-as-you-go**, unlike compile-run-debug app development. You load a slice, look at it (`.head()`, `.shape`, `.dtypes`), transform, look again — a tight loop. Embracing that (rather than writing a big script and running it once) is the biggest adjustment from software engineering, and it's exactly what [[ai-ml/01-data-scientist/04-exploratory-data-analysis|EDA]] formalizes.

## Related
- [[ai-ml/00-foundations/04-python-and-data-tools/02-numpy|NumPy]] — where "push work into the library" becomes concrete
- [[ai-ml/02-ml-engineer/01-foundations-of-ml/02-the-ml-toolkit|The ML Toolkit]] — the full stack and why each piece exists
