# frameworks/ — Ways of Building a Backend

**Sections 01–07 are the course. This folder is the implementations.** Everything here is "how *this* stack does what the course already explained" — so read the course first and these become short.

Deliberately **not numbered**: there's no reading order. Pick the one you're using.

## The map

| Language | Frameworks | Concurrency model | Status |
|---|---|---|---|
| **[[backend/frameworks/javascript/README\|JavaScript / TypeScript]]** | Node runtime, Express, NestJS | **event loop** | built out — Nest reference is substantial |
| **[[backend/frameworks/java/README\|Java]]** | Spring Boot | thread-per-request → **virtual threads** (21+) | built out — **moved here** from `languages/01-java/` |
| **[[backend/frameworks/cpp/README\|C++]]** | Drogon, Crow, oat++, Beast | **async event loop** (asio) | **built out** — 5 notes |
| **[[backend/frameworks/python/README\|Python]]** | FastAPI, Django, Flask | mixed — **WSGI blocking vs ASGI async** | **built out** — folder shape, 3 notes |
| **[[backend/frameworks/csharp/README\|C#]]** | ASP.NET Core (Minimal APIs, MVC) | **async, thread pool** | **built out** — flat notes, 4 |
| **[[backend/frameworks/c/README\|C]]** | libmicrohttpd, Kore, civetweb | **you build it** — usually an `epoll` loop | **built out** — 4 notes |
| **[[backend/frameworks/go/README\|Go]]** | net/http, Chi, Gin | **goroutines** (green threads) | **built out** — 6 notes |
| **[[backend/frameworks/rust/README\|Rust]]** | Axum, Actix Web | **async/tokio** | **built out** — 6 notes |

**Every language here is now built out.** *(The go/rust/c/cpp rows read `scaffold` until Aug 2026 — a stale label; they were written in Phase 1.4 and the table was never updated. Corrected, and noted here because an index that lies about its own contents is worse than one that's incomplete.)*

## Read this first

Before any framework: [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]].

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

## Two shapes, and which to use

This folder contains both layouts, deliberately:

**A folder per framework** — when a language has **several co-equal frameworks** that are genuinely separate subjects. [[backend/frameworks/javascript/README|javascript/]] is this: the Node runtime, Express and Nest each need their own treatment, because Express middleware and Nest interceptors are different topics, not two spellings of one.

**Flat notes by concern** — when a language has **one dominant choice plus alternatives**, and the material is shared across all of them. [[backend/frameworks/java/README|java/]], [[backend/frameworks/go/README|go/]], [[backend/frameworks/rust/README|rust/]], [[backend/frameworks/c/README|c/]] and [[backend/frameworks/cpp/README|cpp/]] are this. Go's middleware note applies identically to the stdlib, Chi and Gin; the database and testing notes are framework-independent entirely. Splitting them per framework would leave one folder with five notes and two with one each.

> **The test: could you write a note about this framework that wouldn't apply to its siblings?** If yes, give it a folder. If no, the material is really about the *language's* approach, and it belongs in flat notes by concern.

`python/` took the folder shape when it was written (Aug 2026) — Django, Flask and FastAPI are genuinely co-equal, and each passes the test above emphatically: Django's admin and migrations, FastAPI's `Depends()` and Pydantic, and Flask's context locals are three unrelated subjects, none of which says anything about the other two.

## How to add a framework here

Keep it to what the course *doesn't* already cover:
- Which concurrency model, and what that implies operationally
- How it names the course concepts (the table above)
- Its idioms and conventions
- Its specific gotchas
- What it does badly, honestly

**Don't restate the course.** If you find yourself explaining what a repository is, that belongs in [[backend/03-structuring-a-backend/README|03-structuring-a-backend]] instead.

## Across all of them

**[[backend/frameworks/cross-language-recipes|Cross-Language Recipes]]** — the same production concerns implemented side by side in Node, Go, Rust, Python, C# and Java: middleware, rate limiting, JWT verification, CORS and headers, **graceful shutdown**, structured logging, and what each stack gives you free.

**The concept table above translates vocabulary; that page translates code.**

## Related
- [[backend/README|Backend course]] · [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]]
- [[backend/interview/README|Backend interview prep]] — built from a real Node interview
