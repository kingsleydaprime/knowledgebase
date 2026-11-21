# NestJS (TypeScript Backend)

## What NestJS is

**NestJS is a TypeScript framework for building backends on Node.js, and it decides a lot for you.** It comes with modules, decorators and a container that wires your classes together. The controller, service and repository layers that Express leaves to you are built in as convention.

## Lessons so far

1. [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]

## What to know
- **It's Angular's architecture for the backend** — modules, providers, decorator-based DI.
- **The request pipeline is explicit**: middleware → guards → interceptors → pipes → handler → interceptors → exception filters. That maps almost exactly onto [[backend/01-foundations/03-the-request-lifecycle/index|the request lifecycle]].
- **Validation decorators are inert without a `ValidationPipe`** — the classic "my validation isn't running" bug. Set `whitelist: true` so clients can't smuggle extra fields.
- **`forwardRef()` is a smell**, not a fix — a circular dependency is a design problem. → [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring/index|DI]]
- It still runs on Express (or Fastify) underneath, so the [[backend/frameworks/node/index|Node runtime]] rules all still apply.

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the NestJS way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What NestJS is and a first app**: the CLI, `main.ts`, modules, and why it looks like Angular — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
2. **Controllers and routing**: decorators, params, DTOs in and responses out — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
3. **The request pipeline**: middleware → guards → interceptors → pipes → handler → exception filters — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
4. **Modules and structure**: feature modules, what to export, `@Global()`, monorepos — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
5. **Providers and DI**: `@Injectable`, scopes, custom providers, why `forwardRef()` is a smell — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
6. **Input validation**: DTOs, class-validator, `ValidationPipe` with `whitelist: true` — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
7. **Errors and structured responses**: built-in HTTP exceptions, exception filters, Prisma errors to status codes, and one response shape for success and failure — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
8. **Data**: a Prisma module and service, transactions, database design patterns — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with a pagination DTO and Prisma's `skip`/`take` and cursors
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with Nest's built-in URI, header and media-type versioning
11. **API docs**: generating OpenAPI docs with `@nestjs/swagger`

**Part 3: who can do what**

12. **Authentication**: Passport strategies, `AuthGuard`, roles with `Reflector` and custom decorators — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
13. **Authorization**: roles and owning your own orders, with guards, `Reflector` and CASL policies
14. **Security**: CORS, Helmet, the throttler, body limits, file uploads — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: `Test.createTestingModule`, unit, integration and e2e tests — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with `@nestjs/bullmq`
19. **Caching**: caching hot reads with `CacheModule` with Redis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with `@nestjs/websockets` gateways

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with `@nestjs/graphql` code-first resolvers, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with `@nestjs/microservices` gRPC transport
23. **Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with the official TypeScript SDK inside a Nest module
24. **MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **Splitting out a microservice**: a separate notifications service, events over `@nestjs/microservices` transports, the outbox pattern
26. **Calling other services safely**: `HttpModule` with timeouts and retries, circuit breakers, service-to-service auth

**Part 7: production**

27. **Observability**: logs, request IDs across services, metrics and tracing with `nestjs-pino`, Terminus health checks and OpenTelemetry
28. **Production config and Docker**: config validation, health checks, graceful shutdown; Docker and a multi-stage build, Docker Compose for the whole system — written in part: [[backend/frameworks/nestjs/01-nestjs-reference|NestJS Personal Reference]]
29. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/node/index|Node.js]] · [[backend/frameworks/express/index|Express]] — what Nest sits on
- [[backend/frameworks/spring-boot/index|Spring Boot]] — the same container-and-opinions trade in Java
- [[projects/arete/learning/backend/01-fundamentals-and-nestjs|arete: NestJS in a real project]] · [[projects/nextvibe/learning/backend/01-core|nextvibe]]

## About this subject

The one lesson so far is a 6,600-word personal reference that covers every stop on the plan. Writing this subject means cutting it into the twelve lessons. Until November 2026 NestJS shared a subject with Node.js and Express.
