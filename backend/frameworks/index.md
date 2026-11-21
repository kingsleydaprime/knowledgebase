---
subject_group: true
---

# frameworks/ — Ways of Building a Backend

## What this folder is

**A framework is the code you build a backend on top of, and this folder gives each framework its own subject.** Each subject teaches the whole [[backend/index|backend course]] (a first server, routing, middleware, structure, validation, errors, data, auth, security, testing and production) the way that framework does it. So you can learn the backend in Express, or in Django, or in Axum, from start to finish.

The course itself (sections 01–07) teaches the ideas that are true everywhere. Read it alongside whichever framework you pick.

## The map

| Language | Subjects | Concurrency model |
|---|---|---|
| **JavaScript / TypeScript** | [[backend/frameworks/node/index\|Node.js]] · [[backend/frameworks/express/index\|Express]] · [[backend/frameworks/nestjs/index\|NestJS]] | event loop |
| **Python** | [[backend/frameworks/fastapi/index\|FastAPI]] · [[backend/frameworks/django/index\|Django]] · [[backend/frameworks/flask/index\|Flask]] | WSGI blocking or ASGI async |
| **Java** | [[backend/frameworks/spring-boot/index\|Spring Boot]] | thread-per-request → virtual threads (21+) |
| **C#** | [[backend/frameworks/aspnet-core/index\|ASP.NET Core]] | async on a thread pool |
| **Go** | [[backend/frameworks/net-http/index\|net/http]] · [[backend/frameworks/chi/index\|Chi]] · [[backend/frameworks/gin/index\|Gin]] | goroutines |
| **Rust** | [[backend/frameworks/axum/index\|Axum]] · [[backend/frameworks/actix-web/index\|Actix Web]] | async on tokio |
| **C++** | [[backend/frameworks/drogon/index\|Drogon]] · [[backend/frameworks/crow/index\|Crow]] · [[backend/frameworks/boost-beast/index\|Boost.Beast]] | async event loop (asio) |
| **C** | [[backend/frameworks/c-sockets/index\|Sockets and epoll]] · [[backend/frameworks/libmicrohttpd/index\|libmicrohttpd]] · [[backend/frameworks/kore/index\|Kore]] · [[backend/frameworks/civetweb/index\|civetweb]] · [[backend/frameworks/ulfius/index\|Ulfius]] | whatever you build, usually `epoll` |

Every subject has a **lesson plan** in its index: twelve stops that follow the backend course, named in that framework's own terms.

The lessons that are true of a whole language, not one framework, live with the language's base framework. Go's database and testing lessons are in net/http, Rust's async pitfalls are in Axum, C++'s JSON lesson is in Drogon, and C's safe-parsing lesson is in Sockets and epoll. The other frameworks of that language link to them.

## Read this first

Before any framework: [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime & Concurrency Models]].

Frameworks look like twenty different things to learn. They're mostly **three concurrency models wearing different vocabularies**, and the model determines far more than the syntax does — how you scale it, how you tune it, what breaks under load, and why the API is shaped the way it is.

Once you know the model, a new framework is a weekend, not a term.

## The same concepts, per stack

The course's vocabulary, translated. This table is most of what "learning a new framework" actually is:

| Course concept | Express | NestJS | Spring Boot | FastAPI | ASP.NET Core | Axum |
|---|---|---|---|---|---|---|
| **Controller** | route handler | `@Controller` | `@RestController` | path operation | `MapGet` / action | handler fn |
| **Service** | (your own) | `@Injectable` | `@Service` | (your own) | registered in DI | (your own) |
| **Repository** | (your own) | `@Injectable` + ORM | `@Repository` | (your own) | `DbContext` | (your own) |
| **Middleware** | `app.use` | middleware / interceptors / guards | filters / interceptors | dependencies + middleware | `app.Use…` | `tower` layers |
| **DI** | manual | built-in container | built-in container | `Depends()` | **built in** | manual / state |
| **Validation** | manual (zod) | `class-validator` + pipe | Bean Validation | Pydantic | DataAnnotations / FluentValidation | `serde` + validator |
| **Errors → status** | error middleware | exception filters | `@ControllerAdvice` | exception handlers | `ProblemDetails` | `IntoResponse` |

Notice how much is "(your own)" in the minimal frameworks — **Express and Axum give you a router and get out of the way**; Nest and Spring give you a container and opinions. That's the actual axis on which these differ, and it's a team-size decision more than a technical one: opinionated frameworks pay off when many people touch the codebase, and cost you when three people want to move fast.

## Choosing within a language

**Python.** These three sit at different points on one axis: how much the framework decides for you. Django decides nearly everything, Flask almost nothing, and FastAPI decides the request boundary and nothing else.

| | FastAPI | Django | Flask |
|---|---|---|---|
| **Model** | ASGI, **async** | WSGI (ASGI partial) | WSGI, **sync** |
| **Batteries** | validation + DI + docs | **everything** | routing only |
| **ORM** | none (SQLAlchemy) | **built in** | none (extension) |
| **Migrations** | Alembic | **built in, excellent** | Flask-Migrate |
| **Admin UI** | none | **its killer feature** | extension |
| **Validation** | **Pydantic, automatic** | Forms / DRF serializers | your choice |
| **OpenAPI** | **free** | DRF, or add-on | add-on |

FastAPI for a new JSON API, especially I/O-heavy or ML-serving. Django for a full product with users, an admin and a database. Flask for server-rendered HTML, small services, or an existing Flask codebase.

**JavaScript.** Node.js on its own if you want to see what the frameworks do for you. Express when you want a router and freedom. NestJS when many people touch the code and you want the structure decided.

**Go.** Start with net/http, add Chi when route groups start hurting (nothing else changes), and pick Gin when you want binding and validation built in and accept the lock-in → [[backend/frameworks/chi/01-chi|Chi]].

**Rust.** Axum is the default because of the `tower` ecosystem. Actix Web is just as mature → [[backend/frameworks/actix-web/index|Actix Web]].

**C++ and C.** Drogon for a real application, Crow or civetweb for embedding something small, Beast or libmicrohttpd when you want control → [[backend/frameworks/drogon/01-drogon|Drogon and the C++ Landscape]] · [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]].

## How to add a framework here

1. Make a folder named after the framework, with an `index.md` titled "Tool (Language Backends)".
2. Open the index with what the framework is, in plain words, then its concurrency model.
3. Copy the twelve-stop lesson plan and rename each stop in the framework's own terms.

**Don't restate the course.** If you find yourself explaining what a repository is, that belongs in [[backend/03-structuring-a-backend/index|03-structuring-a-backend]]. A framework lesson shows how *this* framework does it, what it names it, and where it bites.

## Across all of them

**[[backend/frameworks/cross-language-recipes|Cross-Language Recipes]]** — the same production concerns implemented side by side in Node, Go, Rust, Python, C# and Java: middleware, rate limiting, JWT verification, CORS and headers, **graceful shutdown**, structured logging, and what each stack gives you free.

**The concept table above translates vocabulary; that page translates code.**

## Related
- [[backend/index|Backend course]] · [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime & Concurrency Models]]
- [[backend/interview/index|Backend interview prep]] — built from a real Node interview
