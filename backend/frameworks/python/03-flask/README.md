# Flask

> **[Intermediate]** · The microframework — routing and templating, and everything else is your decision. Plus the context locals that make it feel like magic until they don't.

Flask is the **minimalist** end. It gives you routing, request/response objects, templating (Jinja2) and a development server. **No ORM, no validation, no auth, no admin, no project structure.**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/users")
def create_user():
    data = request.get_json()
    if not data.get("email"):
        return jsonify(error="email required"), 400
    user = service.create(data)
    return jsonify(user.to_dict()), 201
```

Note what's manual compared to [[backend/frameworks/python/01-fastapi/README|FastAPI]]: parsing, validation, the error shape, the status code, serialisation, and the API documentation, which doesn't exist. **That's the trade** — total control, and five things to maintain that a declaration would have given you.

| Course concept | Flask |
|---|---|
| **Controller** | a view function with `@app.route` |
| **Router** | `Blueprint`, registered with a prefix |
| **Middleware** | `@app.before_request` / `@app.after_request`, or WSGI middleware |
| **DI** | **none** — `g`, extensions, or your own |
| **Validation** | your choice (marshmallow, pydantic, manual) |
| **Errors → status** | `@app.errorhandler` |

## Blueprints

The only structural feature, and the thing that keeps a Flask app from becoming one file:

```python
orders = Blueprint("orders", __name__, url_prefix="/orders")

@orders.get("/<int:order_id>")
def get_order(order_id): ...

app.register_blueprint(orders)
```

Group by feature, register on the app. The **application factory** is the companion pattern, and it's what makes the app testable:

```python
def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or "config.Default")
    db.init_app(app)
    app.register_blueprint(orders)
    return app
```

**Use the factory from the start.** A module-level `app = Flask(__name__)` is created at import, so tests can't configure it differently and you end up monkey-patching. This is the most common structural mistake in Flask codebases.

## Context locals — the magic, explained

Flask's most distinctive design, and the source of its most confusing errors:

```python
from flask import request, g, current_app

@app.get("/whoami")
def whoami():
    return request.headers["User-Agent"]     # `request` is a global. Is it?
```

`request` looks like a module-level global shared across every concurrent request — which would be a catastrophic bug. It isn't. It's a **proxy** that resolves, on each access, to the request bound to *the current context* (thread or greenlet).

**So it's a global that isn't shared**, which is elegant and is also why you get:

```
RuntimeError: Working outside of request context
```

whenever you touch `request`, `g` or `current_app` from a background thread, a CLI command, a Celery task, or at import time. The fix is to push a context explicitly (`with app.app_context():`) or, better, **pass what you need as an argument** rather than reaching for the ambient global.

`g` is per-request scratch space; `current_app` is the app; `session` is the signed cookie.

## The extension ecosystem

Flask's answer to batteries: install what you need.

| Need | Extension |
|---|---|
| ORM | Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Auth sessions | Flask-Login |
| Validation | marshmallow / pydantic |
| API + OpenAPI | Flask-Smorest, or **switch to FastAPI** |
| Admin | Flask-Admin |
| CORS | Flask-CORS |

**Assembling these is real work**, and quality varies with maintenance. The upside is that every piece is replaceable; the downside is that no two Flask codebases look alike, so experience transfers less than it does in Django.

## WSGI, and what that means

Flask is **WSGI**: synchronous, one request per worker thread or process at a time.

```bash
gunicorn -w 4 "app:create_app()"                 # 4 worker processes
gunicorn -w 4 -k gevent "app:create_app()"       # greenlets, for I/O-heavy loads
```

**Concurrency comes from processes and threads, not an event loop.** Perfectly adequate for most applications — but a long external API call occupies a worker for its duration, so `workers × threads` is your hard ceiling on concurrent requests.

Flask 2.0 added `async def` views, but they run on an event loop *per request* inside a worker, so it doesn't give you asyncio's scaling. **If concurrency is the requirement, that's a reason to choose FastAPI**, not a thing to retrofit → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]].

## When Flask is still right

Its reputation has suffered as FastAPI took the API use case, but there are cases where it remains the better pick:

- **Server-rendered HTML with Jinja templates.** FastAPI can, but this is Flask's home ground
- **Small services and internal tools** where a dependency list of one is a feature
- **Odd shapes** — webhook receivers, proxies, glue — where a framework's opinions would be in the way
- **An existing Flask codebase.** Rewriting a working service to chase a framework is rarely the highest-value work available

**For a new JSON API with no legacy, FastAPI is the better default**, and this vault would say so plainly.

## Related
- [[backend/frameworks/python/01-fastapi/README|FastAPI]] — where new APIs should start
- [[backend/frameworks/python/02-django/README|Django]] — when you want the batteries
- [[backend/frameworks/javascript/02-express/README|Express]] — **the closest analogue in another language**
- [[backend/frameworks/python/README|Python backends]] — the comparison

*Source: [reference] — from the Flask documentation.*
