---
subject: false
---

# Django (Python Backends)

## What Django is

**Django is a Python framework for building full web applications, and it comes with nearly everything.** It has its own ORM for the database, migrations, user accounts, and an admin site generated from your models. You get a lot without writing it, and in return you build things the Django way.

**Concurrency model: WSGI, blocking,** with async support arriving piece by piece.

## Lessons so far

1. [[backend/frameworks/django/01-django|Django]]

This subject has fewer than three lessons, so `subject: false` keeps it off the platform until more are written.

## What to know
- **`select_related` / `prefetch_related`, or you have an N+1.** Watch the query count on every page you build.
- **Read generated migrations before applying them.** A rename detected as drop-and-create loses data.
- **Django's fat-model convention ties business logic to the database.** Productive when small, painful when large.
- **If you need a CRUD admin, the decision is already made.** Nothing in any ecosystem comes close.

**Read this first:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime & Concurrency Models]], then [[languages/06-python/12-concurrency-and-the-gil|the GIL note]]. The split between WSGI (blocking) and ASGI (async) decides how a Python framework scales, how you deploy it, and which libraries you can use.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Django way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Django is and a first project**: `startproject`, apps, settings, the request and response cycle — written in part: [[backend/frameworks/django/01-django|Django]]
2. **URLs and views**: `urls.py`, function and class-based views, DRF viewsets for APIs — written in part: [[backend/frameworks/django/01-django|Django]]
3. **Middleware**: the `MIDDLEWARE` list, why order matters, writing your own
4. **Structure**: apps as features, fat models, and when to add a service layer — written in part: [[backend/frameworks/django/01-django|Django]]
5. **Wiring**: settings and the app registry in place of DI, and where shared services go
6. **Validation**: forms, model validation, DRF serializers
7. **Errors**: `Http404`, the DRF exception handler, error pages
8. **Data**: the ORM, migrations, the N+1 and `select_related`, `atomic` transactions — written in part: [[backend/frameworks/django/01-django|Django]]
9. **Auth**: the user model, sessions, permissions and groups, token and JWT auth in DRF
10. **Security and cross-cutting**: CSRF, the security settings, CORS, throttling, file storage
11. **Testing**: `TestCase`, the test client, factories, pytest-django
12. **Production**: the admin, the `DEBUG=False` checklist, static files, gunicorn or ASGI, Celery for background jobs — written in part: [[backend/frameworks/django/01-django|Django]]

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/fastapi/index|FastAPI]] · [[backend/frameworks/flask/index|Flask]] — the other two Python options
- [[backend/frameworks/spring-boot/index|Spring Boot]] — the Java framework with the same batteries-included trade
- [[databases/index|Databases]] — what the ORM generates

## About this subject

Built August 2026. `[reference]`: there is no Python backend in [[projects/index|projects/]] yet, so the judgements here are read rather than earned. Until November 2026 FastAPI, Django and Flask shared one subject, "Python Backends". Choosing between them is now in [[backend/frameworks/index|the frameworks index]].
