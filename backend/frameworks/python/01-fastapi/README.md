# FastAPI

> **[Intermediate]** · ASGI, type hints as the schema, `Depends()` as the DI container — and the one performance bug everybody ships.

**The modern default for a new Python API**, and its central idea is unusual: **your type hints are the runtime contract.** Annotations aren't documentation here — they drive parsing, validation, serialisation and the OpenAPI schema.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserIn(BaseModel):
    name: str
    email: str
    age: int | None = None

@app.post("/users", response_model=UserOut, status_code=201)
async def create_user(user: UserIn):
    return await service.create(user)
```

From that, with no further code: the body is parsed and validated, a 422 with per-field errors is returned on bad input, the response is filtered to `UserOut`'s fields, and `/docs` serves interactive OpenAPI documentation.

**This is why it displaced Flask for APIs.** In Flask, that's `request.get_json()`, manual validation, manual error responses and a hand-maintained schema — four things that drift apart. Here they're one declaration → [[languages/06-python/08-typing-and-type-hints|typing]].

## The concepts, translated

| Course concept | FastAPI |
|---|---|
| **Controller** | a path operation function (`@app.get`) |
| **Router** | `APIRouter`, included with a prefix |
| **DI** | `Depends()` |
| **Validation** | Pydantic models |
| **Middleware** | `@app.middleware("http")`, or ASGI middleware |
| **Errors → status** | `HTTPException`, `@app.exception_handler` |
| **Service / repository** | **your own** — the framework has no opinion |

That last row matters: FastAPI gives you a router, validation and DI, and **nothing about how to structure an application**. Layering is yours to impose → [[backend/03-structuring-a-backend/README|structuring a backend]].

## `Depends()`

Dependency injection with no container and no registration — a dependency is any callable:

```python
from fastapi import Depends, HTTPException

async def get_db():
    async with SessionLocal() as session:
        yield session                 # teardown after the response

async def current_user(token: str = Depends(oauth2_scheme),
                       db=Depends(get_db)) -> User:
    user = await db.get_user_by_token(token)
    if not user:
        raise HTTPException(401, "invalid credentials")
    return user

@app.get("/me")
async def me(user: User = Depends(current_user)):
    return user
```

Dependencies nest, and results are **cached per request** — ten dependencies each needing `get_db` share one session. `yield` makes them context managers, so cleanup is guaranteed → [[languages/06-python/07-decorators-and-context-managers|context managers]].

**It's the framework's best idea.** Auth, database sessions, pagination, feature flags and tenant resolution all become composable, individually testable functions — and `app.dependency_overrides[get_db] = fake_db` replaces any of them in tests without patching.

## The bug everybody ships

```python
@app.get("/users")
async def list_users():
    return requests.get(URL).json()      # ✗ BLOCKING inside async
```

FastAPI runs on ASGI with a single-threaded event loop. **A blocking call inside `async def` freezes every concurrent request in the process** — not just this one. Under load the symptom is throughput collapsing to serial, with no error.

**The rule, and it is genuinely the most important thing on this page:**

- **`async def`** — only if everything inside is awaited (`httpx`, `asyncpg`, async SQLAlchemy)
- **`def`** — if anything blocks. **FastAPI runs plain `def` handlers in a threadpool automatically**, which is correct and safe

**A synchronous `def` handler is not a compromise — it's the right answer when your libraries are synchronous.** The mistake is writing `async def` because it looks modern and then calling `requests` inside it.

If you must block inside `async`:

```python
await asyncio.to_thread(blocking_call, arg)
```

→ [[languages/06-python/12-concurrency-and-the-gil|concurrency and the GIL]] and [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]].

## Pydantic

The validation library FastAPI is built on, and useful independently. **v2's core is written in Rust** and is roughly 5–20× faster than v1 — a real consideration when validating large payloads.

```python
from pydantic import BaseModel, Field, field_validator

class Order(BaseModel):
    quantity: int = Field(gt=0, le=100)
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalise(cls, v: str) -> str:
        return v.lower().strip()
```

**Pydantic parses rather than merely validating** — it coerces `"5"` to `5` where sensible and gives you a typed object afterwards, so downstream code doesn't re-check. This is the *parse, don't validate* idea, and it's why the annotation gap in note 08 (hints are unenforced at runtime) closes exactly at the API boundary.

`pydantic-settings` does the same for environment variables, which is the cleanest config story in Python → [[devops/09-secret-management/README|secrets]].

## Running it

```bash
uvicorn app.main:app --reload                          # dev
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4   # prod
```

**Uvicorn** is the ASGI server; **Gunicorn** supervises N worker processes. Workers give you multiple event loops and sidestep the GIL for CPU work → one per core is the usual starting point. `--reload` is dev-only.

## What it does badly, honestly

**No ORM, no admin, no auth, no migrations.** You assemble SQLAlchemy + Alembic + a security library yourself. That's freedom if you want it and weeks of work if you wanted Django.

**Async correctness is on you.** Nothing warns you about the blocking bug above.

**The DI system is request-scoped only** — no singletons or app-scoped lifecycle beyond `lifespan`, so wiring long-lived resources is manual.

**Background tasks are in-process.** `BackgroundTasks` dies with the worker; anything that must survive needs Celery, Dramatiq or a queue → [[architecture/02-building-blocks/README|building blocks]].

## Related
- [[backend/frameworks/python/02-django/README|Django]] — the opposite trade
- [[backend/frameworks/python/README|Python backends]] — the comparison
- [[languages/06-python/12-concurrency-and-the-gil|concurrency and the GIL]] — why the blocking rule exists
- [[backend/02-api-design/01-apis-and-rest|APIs and REST]] — what you're building
- [[backend/03-structuring-a-backend/README|structuring a backend]] — the layering FastAPI won't give you

*Source: [reference] — from the FastAPI, Pydantic and Starlette documentation.*
