# Backend

## What a backend is

**The backend is the part of an app that runs on a server, out of sight: it stores the data, applies the rules, and answers requests from the app you see.**

When you log in to a banking app, the screen you tap is the **frontend**. When you press "Send money", the app sends a message (a **request**) over the internet to the bank's **backend**. The backend checks that it's really you, checks you have enough money, updates both accounts in the database, and sends back an answer (a **response**): "Transfer successful". The frontend then shows you that message.

The backend exists because some things can't be trusted to the user's device. Anyone can tamper with an app on their own phone, so the rules that matter, such as "you can't spend money you don't have", must be checked on a server you control.

This course teaches the ideas that are true whichever language or framework you use. The [[backend/frameworks/index|frameworks]] section then shows how to do them in JavaScript, Java, Python, C#, Go and Rust.

## What you'll be able to do

By the end you will be able to:
- explain what happens from the moment a request reaches a server until the response goes back;
- design an **API**, the set of requests your backend accepts and what it answers;
- organise backend code so it stays easy to change as it grows;
- use a database safely from your code;
- handle logging in and permissions: who you are, and what you're allowed to do;
- deal with the things every feature needs, such as checking input, handling errors and limiting abuse;
- test a backend and check how it copes with heavy use.

## Where to start

Read the sections in order. Section 03 is the heart of the course.

**Before you start:** you should be able to write basic code ([[programming-fundamentals/index|Programming Fundamentals]]). Knowing a little about [[networking/index|how the internet works]] and [[databases/00-your-first-sql|basic SQL]] helps.

### 01. Foundations

1. [[backend/01-foundations/01-what-a-backend-is|What a Backend Actually Is]]: the backend's four jobs, and the one rule behind all of them: never trust the user's device.
2. [[backend/01-foundations/02-http-servers|HTTP Servers]]: how a request physically reaches your server, and how the server answers.
3. [[backend/01-foundations/03-the-request-lifecycle/index|The Request Lifecycle]]: every step a request goes through inside your server, and how to work out which step a bug is in.
4. [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime and Concurrency Models]]: the three ways servers handle many users at once. It explains why frameworks behave differently, so read it before choosing one.

### 02. API Design

5. [[backend/02-api-design/01-apis-and-rest|APIs and REST]]: designing the requests your backend accepts and the answers it gives. Once other apps depend on it, it's hard to change.

### 03. Structuring a Backend (the heart of the course)

6. [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|Layers: Controllers, Services, Repositories]]: splitting code into three jobs: receiving requests, applying business rules, and talking to the database.
7. [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|By Layer vs by Feature]]: two ways of arranging folders, and which keeps changes easier.
8. [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|Dependency Injection and Wiring]]: handing each piece of code the tools it needs instead of letting it create them, which makes testing much easier.
9. [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index|Hexagonal and Clean Architecture]]: keeping your business rules separate from databases and frameworks, and what that costs.
10. [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|Modular Monolith to Services]]: when, and whether, to split one app into several.

### 04. Data and Persistence

11. [[backend/04-data-and-persistence/01-databases-in-the-backend|Databases in the Backend]]: using a database from your code: keeping changes all-or-nothing, handling two users editing at once, connection limits, and the most common performance mistake.

### 05. Auth

12. [[backend/05-auth/01-authentication-flows|Authentication Flows]]: checking who someone is: passwords, sessions and tokens.
13. [[backend/05-auth/02-authorization|Authorization]]: checking what someone is allowed to do.
14. [[backend/05-auth/03-oauth-provider-integrations|OAuth Provider Integrations]]: "Sign in with Google" and similar.

### 06. Things Every Feature Needs

15. [[backend/06-cross-cutting/01-validation-and-dtos|Validation and DTOs]]: checking incoming data before using it.
16. [[backend/06-cross-cutting/02-configuration-and-secrets|Configuration and Secrets]]: settings and passwords that shouldn't be written into the code.
17. [[backend/06-cross-cutting/03-error-handling|Error Handling]]: failing clearly and safely, without leaking internal details.
18. [[backend/06-cross-cutting/04-rate-limiting|Rate Limiting]]: stopping one user from overwhelming your server.
19. [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]]: making sure a request sent twice (say, after a bad connection) doesn't charge someone twice.
20. [[backend/06-cross-cutting/06-security-headers-and-cors|Security Headers and CORS]]: browser rules that protect users, and how to allow other websites to call your API.
21. [[backend/06-cross-cutting/07-file-uploads|File Uploads]]: accepting files from users safely.

Caching, monitoring and background jobs are taught in [[architecture/02-building-blocks/index|Architecture: building blocks]] and [[devops/07-observability/index|DevOps: observability]].

### 07. Practices

22. [[backend/07-practices/01-backend-best-practices/index|Backend Best Practices]]: habits that keep a backend healthy.
23. [[backend/07-practices/02-testing-a-backend|Testing a Backend]]: checking your backend works, automatically.
24. [[backend/07-practices/03-load-and-performance-testing|Load and Performance Testing]]: finding out how your backend copes with many users before real users find out.

## Frameworks: the whole course, in one framework

Every framework is its own subject, and each one teaches this whole course its own way, from a first server to production. They aren't in a reading order; pick the one you use. **Read note 4 (Runtime and Concurrency Models) first:** frameworks look like twenty different things to learn, but they're really three ways of handling many users, with different names. The [[backend/frameworks/index|frameworks index]] helps you choose.

- JavaScript and TypeScript: [[backend/frameworks/node/index|Node.js]], [[backend/frameworks/express/index|Express]], [[backend/frameworks/nestjs/index|NestJS]].
- Python: [[backend/frameworks/fastapi/index|FastAPI]], [[backend/frameworks/django/index|Django]], [[backend/frameworks/flask/index|Flask]].
- Java: [[backend/frameworks/spring-boot/index|Spring Boot]].
- C#: [[backend/frameworks/aspnet-core/index|ASP.NET Core]].
- Go: [[backend/frameworks/net-http/index|net/http]], [[backend/frameworks/chi/index|Chi]], [[backend/frameworks/gin/index|Gin]].
- Rust: [[backend/frameworks/axum/index|Axum]], [[backend/frameworks/actix-web/index|Actix Web]].
- C++: [[backend/frameworks/drogon/index|Drogon]], [[backend/frameworks/crow/index|Crow]], [[backend/frameworks/boost-beast/index|Boost.Beast]].
- C: [[backend/frameworks/c-sockets/index|Sockets and epoll]] (no framework), [[backend/frameworks/libmicrohttpd/index|libmicrohttpd]], [[backend/frameworks/kore/index|Kore]], [[backend/frameworks/civetweb/index|civetweb]], [[backend/frameworks/ulfius/index|Ulfius]].
- [[backend/frameworks/cross-language-recipes|Cross-Language Recipes]]: rate limiting, login tokens, CORS, shutting down cleanly and logging, in six languages side by side.

## Practice

- [[backend/projects|Projects]]: hands-on tasks, from easy (🟢) to hard (🔴), each with a clear "done when".
- [[backend/interview/index|Backend interview prep]]: built from a real interview. [[backend/interview/01-production-debugging|Production Debugging]] covers finding why a live system is slow or failing, and [[backend/interview/02-node-runtime-and-api|Node Runtime and API]] covers Node-specific questions.

## Key ideas to remember

1. **Never trust the client.** Anything from the user's device can be faked, so check everything that matters on the server. → [[backend/01-foundations/01-what-a-backend-is|What a Backend Is]]
2. **Keep receiving requests, business rules and database code apart.** When they're mixed, every change touches everything. → [[backend/03-structuring-a-backend/01-layers-controllers-services-repositories/index|Layers]]
3. **Frameworks differ mainly in how they handle many users at once.** Understand the three models and every framework becomes easier. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|Runtime and Concurrency Models]]
4. **Assume every request might arrive twice,** and make sure that's harmless. → [[backend/06-cross-cutting/05-idempotency-and-retries|Idempotency and Retries]]

## Related

- [[frontend/index|Frontend]]: the other half of the app.
- [[databases/index|Databases]]: where the backend's data lives.
- [[architecture/index|Architecture]]: the same questions at the scale of whole systems.
- [[devops/index|DevOps]]: getting a backend onto servers and keeping it running.
- [[concepts/index|Concepts]]: ideas that apply to all code, like clean code and design patterns.

---

## About this course

- **How it's organised:** sections 01–07 are true in any language. How one framework does something goes in `frameworks/<language>/`. Ideas that apply beyond backends go in [[concepts/index|Concepts]], and notes from real projects go in [[projects/index|Projects]].
- **History:** restructured in August 2026. Before that, the ideas lived in a separate `concepts/01-backend/` folder and this one held only framework notes.
