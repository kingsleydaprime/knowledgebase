# FastAPI (Python Backends)

## What FastAPI is

**FastAPI is a Python framework for building JSON APIs, where your type hints become the rules.** You write a function with typed parameters, and FastAPI uses those types to read the request, check it, and write the API docs. Because one set of types does all three jobs, they can't drift apart.

**Concurrency model: ASGI, async.** One event loop runs `async def` handlers, and plain `def` handlers run in a thread pool.

## Lessons so far

1. [[backend/frameworks/fastapi/01-fastapi|FastAPI]]

## What to know
- **`async def` with a blocking call inside freezes every concurrent request.** Use plain `def` and let the thread pool handle it.
- **Pydantic parses rather than validates.** This is where type hints stop being advice and start being enforced.
- **It gives you no service layer.** The layering is yours → [[backend/03-structuring-a-backend/index|structuring a backend]].

**Read this first:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime & Concurrency Models]], then [[languages/06-python/12-concurrency-and-the-gil|the GIL note]]. The split between WSGI (blocking) and ASGI (async) decides how a Python framework scales, how you deploy it, and which libraries you can use.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the FastAPI way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What FastAPI is and a first app**: ASGI, uvicorn, path operations, and the docs page you get for free — written in part: [[backend/frameworks/fastapi/01-fastapi|FastAPI]]
2. **Routing**: path and query params from type hints, `APIRouter`, response models
3. **Middleware and the request lifecycle**: Starlette middleware, and when a dependency is the better tool
4. **Structuring a FastAPI project**: a router per feature, and the service layer FastAPI won't give you
5. **Dependencies**: `Depends()`, yield dependencies, overriding them in tests — written in part: [[backend/frameworks/fastapi/01-fastapi|FastAPI]]
6. **Validation**: Pydantic models, parse-don't-validate, custom validators — written in part: [[backend/frameworks/fastapi/01-fastapi|FastAPI]]
7. **Errors**: `HTTPException`, exception handlers, one shape for every error body
8. **Data**: SQLAlchemy 2.0, a session per request, Alembic migrations
9. **Auth**: the OAuth2 password flow, JWTs, `Security()` scopes
10. **Security and cross-cutting**: CORS middleware, rate limiting, `UploadFile`, background tasks
11. **Testing**: `TestClient` and httpx, dependency overrides, a real test database
12. **Production**: `async def` versus `def` and the blocking bug, pydantic-settings, workers, logging, Docker — written in part: [[backend/frameworks/fastapi/01-fastapi|FastAPI]]

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/django/index|Django]] · [[backend/frameworks/flask/index|Flask]] — the other two Python options
- [[languages/06-python/index|Python]] — the language
- [[ai-ml/03-ai-engineer/index|AI engineer]] — why FastAPI dominates model serving

## About this subject

Built August 2026. `[reference]`: there is no Python backend in [[projects/index|projects/]] yet, so the judgements here are read rather than earned. Until November 2026 FastAPI, Django and Flask shared one subject, "Python Backends". Choosing between them is now in [[backend/frameworks/index|the frameworks index]].
