# Python Backends

Three genuinely co-equal frameworks, which is why this takes the **folder shape** the [[backend/frameworks/README|frameworks index]] describes: FastAPI, Django and Flask are separate subjects, not three spellings of one.

**~2,650 words across 3 notes.** Built August 2026. `[reference]`. Replaces the scaffold that stood here.

> **The one idea:** these three sit at different points on **one axis — how much the framework decides for you.** Django decides nearly everything; Flask decides almost nothing; FastAPI decides the request boundary and nothing else. Every other difference follows.

## The three

| | [[backend/frameworks/python/01-fastapi/README\|FastAPI]] | [[backend/frameworks/python/02-django/README\|Django]] | [[backend/frameworks/python/03-flask/README\|Flask]] |
|---|---|---|---|
| **Model** | ASGI, **async** | WSGI (ASGI partial) | WSGI, **sync** |
| **Batteries** | validation + DI + docs | **everything** | routing only |
| **ORM** | none (SQLAlchemy) | **built in** | none (extension) |
| **Migrations** | Alembic | **built in, excellent** | Flask-Migrate |
| **Admin UI** | none | **its killer feature** | extension |
| **Validation** | **Pydantic, automatic** | Forms / DRF serializers | your choice |
| **OpenAPI** | **free** | DRF, or add-on | add-on |
| **Structure** | your problem | prescribed (apps) | your problem |
| **Learning curve** | gentle | steep, wide | gentle, then unbounded |

## Choosing

**FastAPI** — a new JSON API, especially I/O-heavy or ML-serving. The type-hints-as-contract model removes a whole category of drift between validation, docs and code.

**Django** — a full web application with users, an admin, a database and server-rendered pages. **If you need a CRUD admin interface, this decision is already made**; nothing else in any ecosystem comes close.

**Flask** — server-rendered HTML, small services, odd-shaped glue, or an existing Flask codebase.

**The honest default for a new API in 2026 is FastAPI**, and for a new full product with an admin it's Django. Flask's remaining strong case is templates and small things.

## Reading order

1. [[backend/frameworks/python/01-fastapi/README|FastAPI]] — **[Intermediate]** — type hints as the runtime contract, `Depends()`, Pydantic, **and the blocking-call bug everybody ships**
2. [[backend/frameworks/python/02-django/README|Django]] — **[Intermediate]** — apps, the ORM and migrations, the admin, DRF, **and the N+1 problem**
3. [[backend/frameworks/python/03-flask/README|Flask]] — **[Intermediate]** — blueprints, the application factory, **and the context locals that explain "working outside of request context"**

## The things worth carrying

1. **In FastAPI, `async def` with a blocking call inside freezes every concurrent request.** Use plain `def` and let the threadpool handle it → [[backend/frameworks/python/01-fastapi/README|FastAPI]]
2. **Pydantic parses rather than validates** — it's where type hints stop being advisory and become enforcement → [[backend/frameworks/python/01-fastapi/README|FastAPI]]
3. **`select_related` / `prefetch_related`, or you have an N+1.** Watch the query count on every page you build → [[backend/frameworks/python/02-django/README|Django]]
4. **Read generated migrations before applying** — a rename detected as drop-and-create is data loss → [[backend/frameworks/python/02-django/README|Django]]
5. **Django's fat-model convention couples domain logic to persistence.** Productive small, painful large → [[backend/frameworks/python/02-django/README|Django]]
6. **Use Flask's application factory from the start**, or your tests can't configure the app → [[backend/frameworks/python/03-flask/README|Flask]]
7. **`request` in Flask is a context-local proxy, not a global** — which is why background threads raise → [[backend/frameworks/python/03-flask/README|Flask]]
8. **None of the three gives you a service layer.** Layering is yours in all cases → [[backend/03-structuring-a-backend/README|structuring a backend]]

## Read this first

[[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]], then [[languages/06-python/12-concurrency-and-the-gil|the GIL note]]. **The WSGI/ASGI split is the single most consequential difference here**, and it decides how each of these scales, how you deploy it, and which libraries you're allowed to use.

## Where this connects

| | |
|---|---|
| [[languages/06-python/README\|languages/06-python/]] | **The language itself** — the other half of this, per [[languages/README\|the rule]] |
| [[backend/frameworks/javascript/02-express/README\|Express]] | Flask's analogue; the same minimalist trade |
| [[backend/frameworks/java/README\|Spring Boot]] | Django's analogue; batteries and a container |
| [[backend/03-structuring-a-backend/README\|structuring a backend]] | The layering none of these provide |
| [[databases/README\|databases]] | What the ORM generates, and why N+1 hurts |
| [[ai-ml/03-ai-engineer/README\|AI engineer]] | Why FastAPI dominates model serving |

## The honest note

**`[reference]`** — no Python backend in this vault's [[projects/README|projects/]]; the backend work here is Node/Nest and Java/Spring. **So the framework-shaped judgements are read, not earned**, and that's a real caveat on the "choosing" section above: the trade-offs are reported accurately, but I haven't personally hit the wall each one describes.

**What would close the gap:**

1. **Build the same small API three times** — one endpoint, one model, validation, tests. It's a weekend, and the comparison table becomes something you know rather than something you read
2. **Ship the blocking bug on purpose.** `async def` + `time.sleep(2)`, then load-test it with `hey` or `wrk`. Watch throughput collapse to serial. **Nothing else makes note 01's rule stick**
3. **Build a Django admin for something real.** The claim that it's the deciding feature is only checkable by using it
4. **Cause an N+1**, find it with `django-debug-toolbar`, fix it with `select_related`, and record the query counts

**What's missing:** deployment specifics (Docker, ASGI/WSGI server tuning, worker counts), Celery and background jobs, WebSockets and Django Channels, `django-ninja`, Litestar, auth implementation at depth, and testing each framework properly.

## Related
- [[backend/frameworks/README|frameworks/]] — the whole map
- [[backend/README|Backend course]] — the concepts these implement
- [[languages/06-python/README|Python]]
