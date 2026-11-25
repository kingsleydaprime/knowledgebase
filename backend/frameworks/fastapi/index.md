# FastAPI (Python Backend)

## What FastAPI is

**FastAPI is a Python framework for building JSON APIs, where your type hints become the rules.** You write a function with typed parameters, and FastAPI uses those types to read the request, check it, and write the API docs. Because one set of types does all three jobs, they can't drift apart.

**Concurrency model: ASGI, async.** One event loop runs `async def` handlers, and plain `def` handlers run in a thread pool.

## Lessons so far

1. [[backend/frameworks/fastapi/01-fastapi|01 — FastAPI]]

## What to know
- **`async def` with a blocking call inside freezes every concurrent request.** Use plain `def` and let the thread pool handle it.
- **Pydantic parses rather than validates.** This is where type hints stop being advice and start being enforced.
- **It gives you no service layer.** The layering is yours → [[backend/03-structuring-a-backend/index|structuring a backend]].

**Read this first:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime & Concurrency Models]], then [[languages/06-python/12-concurrency-and-the-gil|the GIL note]]. The split between WSGI (blocking) and ASGI (async) decides how a Python framework scales, how you deploy it, and which libraries you can use.

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the FastAPI way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **01 — What FastAPI is and a first app**: ASGI, uvicorn, path operations, and the docs page you get for free — written in part: [[backend/frameworks/fastapi/01-fastapi|FastAPI]]
2. **02 — Routing**: path and query params from type hints, `APIRouter`, response models
3. **03 — Middleware and the request lifecycle**: Starlette middleware, and when a dependency is the better tool
4. **04 — Structuring a FastAPI project**: a router per feature, and the service layer FastAPI won't give you
5. **05 — Dependencies**: `Depends()`, yield dependencies, overriding them in tests — written in part: [[backend/frameworks/fastapi/01-fastapi|FastAPI]]
6. **06 — Input validation**: Pydantic models, parse-don't-validate, custom validators — written in part: [[backend/frameworks/fastapi/01-fastapi|FastAPI]]
7. **07 — Errors and structured responses**: `HTTPException`, exception handlers, one shape for every error body, and one response shape for success and failure
8. **08 — Data**: SQLAlchemy 2.0, a session per request, Alembic migrations

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with `Query()` parameters and a reusable `Depends()` paginator
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with versioned `APIRouter`s and header-based dependencies
11. **11 — API docs**: generating OpenAPI docs with the OpenAPI schema FastAPI generates, and tuning it

**Part 3: who can do what**

12. **12 — Authentication**: the OAuth2 password flow, JWTs, `Security()` scopes
13. **13 — Authorization**: roles and owning your own orders, with dependencies that check permissions and ownership
14. **14 — Security**: CORS middleware, rate limiting, `UploadFile`, background tasks
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: `TestClient` and httpx, dependency overrides, a real test database

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with arq or Celery
19. **19 — Caching**: caching hot reads with redis-py, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with FastAPI WebSockets

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with Strawberry on FastAPI, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with grpcio and grpcio-tools
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with the official Python SDK's FastMCP, mounted in FastAPI
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over FastStream on RabbitMQ or Redis, the outbox pattern
26. **26 — Calling other services safely**: httpx with timeouts and tenacity retries, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with structlog and OpenTelemetry instrumentation
28. **28 — Production config and Docker**: `async def` versus `def` and the blocking bug, pydantic-settings, workers, logging, Docker; Docker with uvicorn workers, Docker Compose for the whole system — written in part: [[backend/frameworks/fastapi/01-fastapi|FastAPI]]
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/django/index|Django]] · [[backend/frameworks/flask/index|Flask]] — the other two Python options
- [[languages/06-python/index|Python]] — the language
- [[ai-engineering/index|AI engineer]] — why FastAPI dominates model serving

## About this subject

Built August 2026. `[reference]`: there is no Python backend in projects/ yet, so the judgements here are read rather than earned. Until November 2026 FastAPI, Django and Flask shared one subject, "Python Backends". Choosing between them is now in [[backend/frameworks/index|the frameworks index]].
