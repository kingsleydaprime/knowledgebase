# Django (Python Backend)

## What Django is

**Django is a Python framework for building full web applications, and it comes with nearly everything.** It has its own ORM for the database, migrations, user accounts, and an admin site generated from your models. You get a lot without writing it, and in return you build things the Django way.

**Concurrency model: WSGI, blocking,** with async support arriving piece by piece.

## Lessons so far

1. [[backend/frameworks/django/01-django|Django]]

## What to know
- **`select_related` / `prefetch_related`, or you have an N+1.** Watch the query count on every page you build.
- **Read generated migrations before applying them.** A rename detected as drop-and-create loses data.
- **Django's fat-model convention ties business logic to the database.** Productive when small, painful when large.
- **If you need a CRUD admin, the decision is already made.** Nothing in any ecosystem comes close.

**Read this first:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime & Concurrency Models]], then [[languages/06-python/12-concurrency-and-the-gil|the GIL note]]. The split between WSGI (blocking) and ASGI (async) decides how a Python framework scales, how you deploy it, and which libraries you can use.

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Django way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What Django is and a first project**: `startproject`, apps, settings, the request and response cycle — written in part: [[backend/frameworks/django/01-django|Django]]
2. **URLs and views**: `urls.py`, function and class-based views, DRF viewsets for APIs — written in part: [[backend/frameworks/django/01-django|Django]]
3. **Middleware**: the `MIDDLEWARE` list, why order matters, writing your own
4. **Structure**: apps as features, fat models, and when to add a service layer — written in part: [[backend/frameworks/django/01-django|Django]]
5. **Wiring**: settings and the app registry in place of DI, and where shared services go
6. **Input validation**: forms, model validation, DRF serializers
7. **Errors and structured responses**: `Http404`, the DRF exception handler, error pages, and one response shape for success and failure
8. **Data**: the ORM, migrations, the N+1 and `select_related`, `atomic` transactions — written in part: [[backend/frameworks/django/01-django|Django]]

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with DRF pagination classes, django-filter, `SearchFilter` and `OrderingFilter`
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with DRF's URL, namespace, header and query versioning
11. **API docs**: generating OpenAPI docs with drf-spectacular

**Part 3: who can do what**

12. **Authentication**: the user model, sessions, permissions and groups, token and JWT auth in DRF
13. **Authorization**: roles and owning your own orders, with DRF permission classes and object permissions
14. **Security**: CSRF, the security settings, CORS, throttling, file storage
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: `TestCase`, the test client, factories, pytest-django

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with Celery
19. **Caching**: caching hot reads with Django's cache framework on Redis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with Django Channels

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with Strawberry Django, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with grpcio with Django models
23. **Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with the official Python SDK's ASGI app, mounted beside Django
24. **MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **Splitting out a microservice**: a separate notifications service, events over Celery events or RabbitMQ, the outbox pattern
26. **Calling other services safely**: httpx with timeouts and retries, circuit breakers, service-to-service auth

**Part 7: production**

27. **Observability**: logs, request IDs across services, metrics and tracing with django-prometheus and OpenTelemetry
28. **Production config and Docker**: the admin, the `DEBUG=False` checklist, static files, gunicorn or ASGI, Celery for background jobs; Docker with gunicorn, `collectstatic` and migrations, Docker Compose for the whole system — written in part: [[backend/frameworks/django/01-django|Django]]
29. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/fastapi/index|FastAPI]] · [[backend/frameworks/flask/index|Flask]] — the other two Python options
- [[backend/frameworks/spring-boot/index|Spring Boot]] — the Java framework with the same batteries-included trade
- [[databases/index|Databases]] — what the ORM generates

## About this subject

Built August 2026. `[reference]`: there is no Python backend in [[projects/index|projects/]] yet, so the judgements here are read rather than earned. Until November 2026 FastAPI, Django and Flask shared one subject, "Python Backends". Choosing between them is now in [[backend/frameworks/index|the frameworks index]].
