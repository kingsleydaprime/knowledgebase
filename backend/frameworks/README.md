# frameworks/ — Ways of Building a Backend

**Sections 01–07 are the course. This folder is the implementations.** Everything here is "how *this* stack does what the course already explained" — so read the course first and these become short.

Deliberately **not numbered**: there's no reading order. Pick the one you're using.

## The map

| Language | Frameworks | Concurrency model | Status |
|---|---|---|---|
| **[[backend/frameworks/javascript/README\|JavaScript / TypeScript]]** | Node runtime, Express, NestJS | **event loop** | built out — Nest reference is substantial |
| **[[backend/frameworks/java/README\|Java]]** | Spring Boot | thread-per-request → **virtual threads** (21+) | built out — **moved here** from `languages/01-java/` |
| **[[backend/frameworks/cpp/README\|C++]]** | Drogon, Crow, oat++, Beast | **async event loop** (asio) | scaffold |
| **[[backend/frameworks/python/README\|Python]]** | FastAPI, Django, Flask | mixed — WSGI blocking vs ASGI async | scaffold |
| **[[backend/frameworks/c/README\|C]]** | libmicrohttpd, Kore, civetweb | **you build it** — usually an `epoll` loop | scaffold |
| **[[backend/frameworks/go/README\|Go]]** | net/http, Chi, Gin | **goroutines** (green threads) | scaffold |
| **[[backend/frameworks/rust/README\|Rust]]** | Axum, Actix Web | **async/tokio** | scaffold |

**Scaffold means scaffold** — a README with the shape and the things worth knowing, no written course yet. The vault's convention is to say so rather than imply depth that isn't there.

## Read this first

Before any framework: [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]].

Frameworks look like twenty different things to learn. They're mostly **three concurrency models wearing different vocabularies**, and the model determines far more than the syntax does — how you scale it, how you tune it, what breaks under load, and why the API is shaped the way it is.

Once you know the model, a new framework is a weekend, not a term.

## The same concepts, per stack

The course's vocabulary, translated. This table is most of what "learning a new framework" actually is:

| Course concept | Express | NestJS | Spring Boot | FastAPI | Axum |
|---|---|---|---|---|---|
| **Controller** | route handler | `@Controller` | `@RestController` | path operation | handler fn |
| **Service** | (your own) | `@Injectable` | `@Service` | (your own) | (your own) |
| **Repository** | (your own) | `@Injectable` + ORM | `@Repository` | (your own) | (your own) |
| **Middleware** | `app.use` | middleware / interceptors / guards | filters / interceptors | dependencies + middleware | `tower` layers |
| **DI** | manual | built-in container | built-in container | `Depends()` | manual / state |
| **Validation** | manual (zod) | `class-validator` + pipe | Bean Validation | Pydantic | `serde` + validator |
| **Errors → status** | error middleware | exception filters | `@ControllerAdvice` | exception handlers | `IntoResponse` |

Notice how much is "(your own)" in the minimal frameworks — **Express and Axum give you a router and get out of the way**; Nest and Spring give you a container and opinions. That's the actual axis on which these differ, and it's a team-size decision more than a technical one: opinionated frameworks pay off when many people touch the codebase, and cost you when three people want to move fast.

## How to add a framework here

Keep it to what the course *doesn't* already cover:
- Which concurrency model, and what that implies operationally
- How it names the course concepts (the table above)
- Its idioms and conventions
- Its specific gotchas
- What it does badly, honestly

**Don't restate the course.** If you find yourself explaining what a repository is, that belongs in [[backend/03-structuring-a-backend/README|03-structuring-a-backend]] instead.

## Related
- [[backend/README|Backend course]] · [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]]
- [[backend/interview/README|Backend interview prep]] — built from a real Node interview
