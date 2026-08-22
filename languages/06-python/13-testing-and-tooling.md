# Testing and Tooling

> **[Intermediate]** · pytest, and the four-tool setup that makes a dynamic language safe to change.

Python gives you very little for free at compile time. **The tooling is what replaces it**, and a codebase without it is genuinely harder to change than an equivalent one in a compiled language.

## pytest

The standard, despite `unittest` being in the stdlib. The reason is visible immediately:

```python
# unittest
class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

# pytest
def test_add():
    assert add(2, 3) == 5
```

Plain functions, plain `assert`. pytest rewrites the assert statement so failures still show you both sides:

```
E       assert 6 == 5
E        +  where 6 = add(2, 3)
```

### Fixtures

Dependency injection for tests. A fixture is set-up (and tear-down) that tests request **by naming it as a parameter**:

```python
import pytest

@pytest.fixture
def db():
    conn = create_test_db()
    yield conn                 # the test runs here
    conn.close()               # teardown, even if the test fails

def test_user_creation(db):    # ← requesting it by name
    db.insert(User("Ada"))
    assert db.count() == 1
```

Scopes control how often it's built: `function` (default), `class`, `module`, `session`. An expensive fixture — a container, a database — wants `session` scope; anything mutable that tests could pollute wants `function`.

Shared fixtures go in **`conftest.py`**, and are available to every test in that directory and below, with no import.

### Parametrising

```python
@pytest.mark.parametrize("value,expected", [
    (0, "zero"), (1, "one"), (-1, "negative"), (10**9, "large"),
])
def test_describe(value, expected):
    assert describe(value) == expected
```

**Four tests, reported separately, one function.** This is the single highest-return pytest feature — it makes covering edge cases cheap enough that you actually do it → [[foundations/programming-fundamentals/10-errors-and-debugging|test the edges]].

### The rest of the daily kit

```python
with pytest.raises(ValueError, match="must be positive"):
    withdraw(-5)

@pytest.mark.slow                     # custom marker; run with -m "not slow"
def test_full_pipeline(): ...

def test_uses_tmp(tmp_path):          # built-in: a real temp directory, cleaned up
    (tmp_path / "f.txt").write_text("hi")

def test_output(capsys):              # built-in: capture stdout/stderr
    ...
```

```bash
pytest                    # everything
pytest -x                 # stop at the first failure
pytest -k "user"          # only tests matching "user"
pytest --lf               # only what failed last run — the tightest loop
pytest -q --tb=short      # quiet, short tracebacks
```

**`pytest --lf` is the one to remember.** Fix, rerun only the failures, repeat.

### Mocking

```python
from unittest.mock import patch, MagicMock

@patch("myapp.services.send_email")
def test_signup(mock_send):
    signup("ada@example.com")
    mock_send.assert_called_once_with("ada@example.com")
```

**Patch where the name is *used*, not where it's defined.** `@patch("myapp.services.send_email")` — not `@patch("myapp.email.send_email")` — because `from ... import` already bound a separate reference in the consuming module. This trips up nearly everyone once.

**Mock sparingly.** Each mock encodes an assumption about a collaborator, and a suite full of them passes while the system is broken. Prefer real objects, fakes, or a test database; mock at the true boundaries — network, time, randomness, paid APIs.

## The tooling

**`ruff`** — linter and formatter, written in Rust, and it has effectively replaced flake8, isort, pyupgrade and (increasingly) black:

```bash
ruff check --fix .        # lint, autofixing what it can
ruff format .             # format
```

It's fast enough (10–100×) to run on every save, which is what makes it actually get used.

**`mypy`** or **`pyright`** — static type checking → [[languages/06-python/08-typing-and-type-hints|note 08]].

**`pytest-cov`** — coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

**Coverage measures what ran, not what was checked.** A test with no assertions gives full coverage of the code it touches. Treat it as a *finder of untested regions*, never as a quality target — the moment it becomes a target, people write tests that execute code and assert nothing.

Everything configured in one place:

```toml
[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"

[tool.mypy]
python_version = "3.12"
warn_return_any = true
```

## Pre-commit and CI

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks: [{id: ruff, args: [--fix]}, {id: ruff-format}]
```

```bash
pip install pre-commit && pre-commit install
```

**Hooks must be fast** — lint and format on staged files, seconds not minutes. The full test suite belongs in [[devops/06-ci-cd/README|CI]] on push. A slow hook trains people to use `--no-verify`, which defeats it entirely.

`pre-commit` is the language-agnostic framework; the Node equivalent is Husky. Both exist because a script dropped in `.git/hooks/` isn't version-controlled and doesn't survive a clone.

## What to test

The value isn't uniform, and the ordering is:

1. **Business logic and calculations** — highest value, easiest to test
2. **Edge cases** — empty, zero, one, huge, negative, `None`, malformed. `parametrize` makes this cheap
3. **Bug fixes** — write the failing test *first*, then fix. It's the only way to know the fix works and the only defence against regression
4. **Integration points** — the seams where your code meets a database or an API

Low value: getters, framework behaviour, and anything whose test is a restatement of the implementation.

**In a dynamically typed language, tests carry load a compiler carries elsewhere.** A rename in Java breaks the build; in Python it breaks at runtime, in whatever code path hits it, possibly in production. Types and tests are how you get that back → [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]].

## Related
- [[languages/06-python/08-typing-and-type-hints|typing]] — the other half of the safety net
- [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]] — the concepts
- [[devops/06-ci-cd/README|CI/CD]] — where this runs automatically
- [[languages/06-python/01-why-python-and-the-toolchain|the toolchain]] — venvs and pyproject.toml

*Source: [reference] — from the pytest and ruff documentation.*
