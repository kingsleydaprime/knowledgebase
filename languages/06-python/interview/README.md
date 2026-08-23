# Python — Interview Prep

From [[languages/06-python/README|the Python course]]. **Python interviews test the data model and the gotchas, not syntax** — and the questions cluster tightly, because the same handful of behaviours account for most real Python bugs.

## Files
1. [[languages/06-python/interview/01-the-python-round|The Python Round]] — mutable defaults, `is` vs `==`, the GIL, generators, decorators, EAFP, type hints, and why it's slow

## What this round is actually testing

**Whether you understand that names bind to objects.** Nearly every question above resolves to that one fact: the mutable default, the aliasing surprise, `is` vs `==`, why `global` behaves as it does. A candidate who has the model answers all of them; one who memorised the gotchas answers each in isolation and comes apart on the follow-up.

**The tell:** ask *why* the mutable default happens. "Because the default is evaluated once at definition" is correct. "Because `def` is an executable statement that builds a function object, and the default becomes an attribute of it" is the one that shows the model.

## Where the rest lives

| Round | Bank |
|---|---|
| Frameworks (FastAPI/Django/Flask) | [[backend/frameworks/python/README\|backend/frameworks/python/]] |
| Data stack (NumPy/pandas) | [[ai-ml/00-foundations/04-python-and-data-tools/README\|ai-ml]] |
| Algorithms | [[foundations/dsa/interview/README\|DSA interview prep]] |
| API/auth/testing, stack-agnostic | [[concepts/interview/README\|Concepts]] |

## Related
- [[languages/06-python/18-practice-exercises|Practice exercises]] — **do these before the interview**; every question above is reproducible in a REPL
- [[INTERVIEW|Interview Prep Index]]
