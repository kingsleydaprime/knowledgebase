# Flask (Python Backend)

## What Flask is

**Flask is a small Python web framework that gives you routing and very little else.** You add a database, validation and structure yourself, usually through extensions. It is easy to start with and grows in whatever direction you push it.

**Concurrency model: WSGI, blocking.** One request per worker thread or process.

## Lessons so far

1. [[backend/frameworks/flask/01-flask|01 — Flask]]

## What to know
- **Use the application factory from the start**, or your tests can't configure the app.
- **`request` is a context-local proxy, not a global.** That is why it raises "working outside of request context" in a background thread.
- **Its strongest remaining case is server-rendered HTML and small services.** For a new JSON API, [[backend/frameworks/fastapi/index|FastAPI]] usually wins.

**Read this first:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime & Concurrency Models]], then [[languages/06-python/12-concurrency-and-the-gil|the GIL note]]. The split between WSGI (blocking) and ASGI (async) decides how a Python framework scales, how you deploy it, and which libraries you can use.

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Flask way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **01 — What Flask is and a first app**: WSGI, `@app.route`, and the application factory — written in part: [[backend/frameworks/flask/01-flask|Flask]]
2. **02 — Routing and views**: methods, converters, `jsonify`, blueprints — written in part: [[backend/frameworks/flask/01-flask|Flask]]
3. **03 — Request hooks**: `before_request`, `after_request`, teardown, WSGI middleware
4. **04 — Structure**: a blueprint per feature, the factory, extensions set up in one place — written in part: [[backend/frameworks/flask/01-flask|Flask]]
5. **05 — Context locals and wiring**: `request`, `g`, `current_app`, and why background threads raise — written in part: [[backend/frameworks/flask/01-flask|Flask]]
6. **06 — Input validation**: marshmallow or Pydantic, because Flask gives you none
7. **07 — Errors and structured responses**: `abort`, `errorhandler`, JSON error bodies, and one response shape for success and failure
8. **08 — Data**: Flask-SQLAlchemy, Flask-Migrate, a session per request

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with query parsing with Pydantic and SQLAlchemy `limit`/`offset` and keyset pagination
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with a blueprint per version, or header-based routing
11. **11 — API docs**: generating OpenAPI docs with flask-smorest or APIFlask

**Part 3: who can do what**

12. **12 — Authentication**: Flask-Login sessions, JWTs, role checks
13. **13 — Authorization**: roles and owning your own orders, with decorators that check roles and ownership
14. **14 — Security**: Flask-CORS, security headers with Talisman, Flask-Limiter, uploads
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: `app.test_client()`, fixtures built from the factory

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with Celery or RQ
19. **19 — Caching**: caching hot reads with Flask-Caching on Redis, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with Flask-SocketIO or server-sent events

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with Strawberry with Flask, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with grpcio
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with the official Python SDK as a separate ASGI app next to Flask, since MCP over HTTP is async
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over RabbitMQ or Redis streams, the outbox pattern
26. **26 — Calling other services safely**: requests or httpx with timeouts and retries, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with structured logging and OpenTelemetry
28. **28 — Production config and Docker**: config objects, gunicorn workers, logging, and when Flask is still the right choice; Docker with gunicorn, Docker Compose for the whole system — written in part: [[backend/frameworks/flask/01-flask|Flask]]
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/fastapi/index|FastAPI]] · [[backend/frameworks/django/index|Django]] — the other two Python options
- [[backend/frameworks/express/index|Express]] — the same minimalist trade in JavaScript
- [[languages/06-python/index|Python]]

## About this subject

Built August 2026. `[reference]`: there is no Python backend in [[projects/index|projects/]] yet, so the judgements here are read rather than earned. Until November 2026 FastAPI, Django and Flask shared one subject, "Python Backends". Choosing between them is now in [[backend/frameworks/index|the frameworks index]].
