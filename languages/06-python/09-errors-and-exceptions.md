---
id: 1a964a6c-9604-490e-9899-098d5980eac8
---

# Errors and Exceptions

Python uses exceptions for control flow far more readily than most languages, and this is a deliberate cultural difference rather than an accident.

## LBYL and EAFP
<!-- bite: a626edc1-0f79-4fe1-b54a-af96307a351b -->

**Look Before You Leap** — check first:

```python
if os.path.exists(path):
    with open(path) as f: ...       # ✗ the file can vanish between the two lines
```

**Easier to Ask Forgiveness than Permission** — try it and handle failure:

```python
try:
    with open(path) as f: ...
except FileNotFoundError:
    ...
```

**EAFP is the Pythonic default**, for two solid reasons rather than taste:

**It has no race condition.** The LBYL version above is a TOCTOU bug — time-of-check to time-of-use. Between `exists()` and `open()`, another process can delete the file. In a security context this class of bug is exploitable → [[cybersecurity/06-attacks-and-threats/index|attacks]].

**It's faster in the common case.** No check on the success path; you pay only when it fails.

## The hierarchy
<!-- bite: 728b19f0-4136-47ce-ba18-5d153cf74b7c -->

```
BaseException
 ├── SystemExit, KeyboardInterrupt, GeneratorExit   ← NOT subclasses of Exception
 └── Exception
      ├── ArithmeticError → ZeroDivisionError
      ├── LookupError → IndexError, KeyError
      ├── OSError → FileNotFoundError, PermissionError, TimeoutError
      ├── ValueError, TypeError, AttributeError, NameError
      └── RuntimeError, StopIteration, ...
```

**`KeyboardInterrupt` and `SystemExit` deliberately sit outside `Exception`** so that `except Exception:` doesn't catch them — otherwise Ctrl+C wouldn't work and `sys.exit()` could be swallowed. This is exactly why you catch `Exception`, never `BaseException`.

Catching a base class catches its children, so `except OSError` covers `FileNotFoundError` and `PermissionError` both.

## Handling
<!-- bite: 8f6976c3-6d9a-47d4-8b09-433d87b237cc -->

```python
try:
    result = risky()
except (ValueError, TypeError) as e:     # several, one handler
    log.warning("bad input: %s", e)
    raise                                 # re-raise, preserving the traceback
except KeyError as e:
    raise ConfigError(f"missing key {e}") from e     # chain: preserves the cause
else:
    commit(result)                        # runs only if NO exception
finally:
    cleanup()                             # runs always
```

Four clauses, and two are underused:

**`else`** holds the code that should run on success. Keeping it out of `try` means you don't accidentally catch an exception raised by *that* code rather than by `risky()` — a real and hard-to-spot bug.

**`finally` always runs** — including on `return` and on an exception propagating. It's what `with` is built on → [[languages/06-python/07-decorators-and-context-managers|note 07]].

**`raise ... from e` chains exceptions**, so the traceback shows *"The above exception was the direct cause of the following"*. Without it you lose the original cause, which is usually the useful half.

## What not to do
<!-- bite: b77da8c4-7092-4e01-8c99-bf7edbbf8669 -->

```python
try:
    do_something()
except:                          # ✗ bare except — catches KeyboardInterrupt too
    pass                         # ✗ and silently discards everything
```

**This is the worst line in Python.** It catches every error including your own typos (`NameError`, `AttributeError`), discards the evidence, and continues in an unknown state. The bug then surfaces somewhere unrelated with no trace of where it came from.

If you genuinely must continue:

```python
try:
    do_something()
except Exception:
    log.exception("do_something failed")     # logs the FULL traceback
```

**`log.exception()` inside a handler records the traceback automatically.** It is the difference between a debuggable incident and a mystery.

**Catch narrowly.** `except Exception` at the top of a request handler or a worker loop is legitimate — it stops one bad request killing the process. Anywhere else it's usually hiding something.

## Custom exceptions
<!-- bite: 3048f24d-2f2e-448a-9e64-552053ec2ba3 -->

```python
class AppError(Exception):
    """Base for everything this application raises."""

class ValidationError(AppError):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"{field}: {message}")
```

**A single base class per application is worth doing on day one.** It lets callers write `except AppError` to mean "something *we* raised" as distinct from "something broke", and it costs one line.

Carry structured data as attributes (`self.field`), not just a formatted string — the string is for humans, the attributes are for the code that has to decide what to do.

## Reading a traceback
<!-- bite: a8466d1d-75fe-4a69-98e6-24d21cf93405 -->

```
Traceback (most recent call last):
  File "app.py", line 42, in main
    process(data)
  File "processor.py", line 17, in process
    return items[key]
KeyError: 'user_id'
```

**"Most recent call last" means read from the bottom.** The last frame is where it broke; the ones above are how you got there.

In a long traceback, most frames are library code — **find the deepest frame that is yours.** That's nearly always where the actual mistake is → [[programming-fundamentals/10-errors-and-debugging|debugging]].

## Exceptions and control flow
<!-- bite: 3ae60f7f-db0c-4e8e-b7f1-afd6d70be09d -->

`StopIteration` ends every `for` loop → [[languages/06-python/06-iterators-generators-and-comprehensions|note 06]]. `KeyError` drives `dict.get`. This is normal here in a way it isn't in Go or Rust, where errors are values → [[languages/02-go/05-errors|Go errors]] and [[languages/03-rust/index|Rust's `Result`]].

**The trade:** exceptions keep the happy path clean and make it easy to *forget* a failure mode, since nothing forces you to handle it. Returned errors are noisier and impossible to ignore silently. Neither is right; know which one you're in.

**Exception groups** (3.11+) let one operation raise several at once — mostly relevant to concurrent code, where several tasks fail together:

```python
except* ValueError as eg: ...
```

## Related
<!-- bite: b5499da2-6a1b-4b45-9ddb-286ae086538e -->
- [[languages/06-python/07-decorators-and-context-managers|context managers]] — `finally`, packaged
- [[programming-fundamentals/10-errors-and-debugging|errors and debugging]] — the language-agnostic version
- [[languages/02-go/05-errors|errors in Go]] — the errors-as-values contrast
- [[backend/06-cross-cutting/index|cross-cutting concerns]] — error handling at an API boundary

## About this lesson
<!-- bite: c0cc0f6c-60d3-40aa-ab1a-394cc0f6cf83 -->

**Level:** Intermediate. **Covers:** EAFP, the exception hierarchy, and why `except Exception: pass` is the worst line you can write.

*Source: [reference] — from the Python tutorial and language reference.*
