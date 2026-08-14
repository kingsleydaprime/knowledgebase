# Python Backends — scaffold

No course written yet. The shape, for when there is one:

| Framework | Model | Character |
|---|---|---|
| **FastAPI** | ASGI, **async** | type hints drive validation (Pydantic) and OpenAPI generation. The modern default |
| **Django** | WSGI blocking (ASGI optional) | batteries-included: ORM, admin, auth. Opinionated, by-layer |
| **Flask** | WSGI blocking | minimal, like Express |

## The thing to know
**WSGI is blocking, ASGI is async, and mixing them is where the bugs are.** A blocking call inside an async FastAPI handler blocks the event loop exactly like [[backend/frameworks/javascript/01-node-runtime/README|Node]] — use `def` (FastAPI runs it in a threadpool) rather than `async def` if the work is blocking. Getting this backwards is *the* FastAPI performance bug. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

Python also appears in this vault under [[ai-ml/00-foundations/04-python-and-data-tools/README|ai-ml/00-foundations]] for the data-tooling side.

## Related
- [[backend/frameworks/README|frameworks/]]
