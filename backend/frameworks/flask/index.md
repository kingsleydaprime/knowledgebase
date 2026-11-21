---
subject: false
---

# Flask (Python Backends)

## What Flask is

**Flask is a small Python web framework that gives you routing and very little else.** You add a database, validation and structure yourself, usually through extensions. It is easy to start with and grows in whatever direction you push it.

**Concurrency model: WSGI, blocking.** One request per worker thread or process.

## Lessons so far

1. [[backend/frameworks/flask/01-flask|Flask]]

This subject has fewer than three lessons, so `subject: false` keeps it off the platform until more are written.

## What to know
- **Use the application factory from the start**, or your tests can't configure the app.
- **`request` is a context-local proxy, not a global.** That is why it raises "working outside of request context" in a background thread.
- **Its strongest remaining case is server-rendered HTML and small services.** For a new JSON API, [[backend/frameworks/fastapi/index|FastAPI]] usually wins.

**Read this first:** [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime & Concurrency Models]], then [[languages/06-python/12-concurrency-and-the-gil|the GIL note]]. The split between WSGI (blocking) and ASGI (async) decides how a Python framework scales, how you deploy it, and which libraries you can use.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Flask way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Flask is and a first app**: WSGI, `@app.route`, and the application factory — written in part: [[backend/frameworks/flask/01-flask|Flask]]
2. **Routing and views**: methods, converters, `jsonify`, blueprints — written in part: [[backend/frameworks/flask/01-flask|Flask]]
3. **Request hooks**: `before_request`, `after_request`, teardown, WSGI middleware
4. **Structure**: a blueprint per feature, the factory, extensions set up in one place — written in part: [[backend/frameworks/flask/01-flask|Flask]]
5. **Context locals and wiring**: `request`, `g`, `current_app`, and why background threads raise — written in part: [[backend/frameworks/flask/01-flask|Flask]]
6. **Validation**: marshmallow or Pydantic, because Flask gives you none
7. **Errors**: `abort`, `errorhandler`, JSON error bodies
8. **Data**: Flask-SQLAlchemy, Flask-Migrate, a session per request
9. **Auth**: Flask-Login sessions, JWTs, role checks
10. **Security and cross-cutting**: Flask-CORS, security headers with Talisman, Flask-Limiter, uploads
11. **Testing**: `app.test_client()`, fixtures built from the factory
12. **Production**: config objects, gunicorn workers, logging, and when Flask is still the right choice — written in part: [[backend/frameworks/flask/01-flask|Flask]]

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/fastapi/index|FastAPI]] · [[backend/frameworks/django/index|Django]] — the other two Python options
- [[backend/frameworks/express/index|Express]] — the same minimalist trade in JavaScript
- [[languages/06-python/index|Python]]

## About this subject

Built August 2026. `[reference]`: there is no Python backend in [[projects/index|projects/]] yet, so the judgements here are read rather than earned. Until November 2026 FastAPI, Django and Flask shared one subject, "Python Backends". Choosing between them is now in [[backend/frameworks/index|the frameworks index]].
