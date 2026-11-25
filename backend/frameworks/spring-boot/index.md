# Spring Boot (Java Backend)

## What Spring Boot is

**Spring Boot is the framework most Java companies use to build web servers and APIs.** It gives you a lot ready-made: routing, database access, security and configuration.

**Doing backend work in Java? Start here.** This is the Spring Boot material, and it's the deepest framework section in the vault — ~3,000 words distilled from a real Spring Boot payment sandbox, not from documentation.

**Concurrency model: thread-per-request.** Spring MVC on a servlet container gives every request its own OS thread — simple to reason about, expensive at scale. From Java 21, **virtual threads** turn it into green threads *without a code change*, which is the biggest thing to happen to Java backends in a decade. Spring **WebFlux** is the event-loop/reactive alternative, and Loom has largely removed the reason to reach for it: you can now get the scalability without the reactive programming model. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime & concurrency models]]

## Lessons so far

1. [[backend/frameworks/spring-boot/01-spring-boot|01 — Spring Boot & Scheduling]] — **[Intermediate]** — what the framework actually does for you, dependency injection, controller/service/store layering, validation, `ResponseEntity`, `HandlerInterceptor`, `@Async` offloading, `@Scheduled` jobs, and a retry state machine
2. [[backend/frameworks/spring-boot/02-web-frameworks|02 — The Java Web Landscape]] — **[reference]** — Quarkus, Micronaut, Javalin, Play: what each optimises for, and why the GraalVM native-image push exists
3. [[backend/frameworks/spring-boot/03-api-design-and-documentation|03 — API Design & Documentation]] — **[Intermediate]** — `RestTemplate` for outbound calls, the config-resolution/fallback pattern, business codes over raw HTTP status, and OpenAPI/springdoc

## Where this moved from, and why

These three notes **used to live in `languages/01-java/05-web-and-api/`**. They were **moved here, not copied** — there is exactly one copy of this material and it is this one.

The reason is a rule that now applies across the vault:

> **`languages/` teaches the language. `backend/frameworks/` teaches the frameworks built on it.**

So `languages/01-java/` keeps the JVM, concurrency, generics, collections, tooling and persistence — the things true of Java whether or not you ever serve an HTTP request. Spring Boot is a *web framework*, and it belongs next to Express, Nest, Axum and Gin, where you can compare them.

That comparison is the point. Spring's `@RestController` / `@Service` / `@Repository` and Nest's `@Controller` / `@Injectable` are the same idea with different spelling — which is obvious when they sit in one folder and invisible when they're filed under different languages. See the translation table in [[backend/frameworks/index|frameworks/]].

## What you still need from `languages/01-java/`

Spring Boot sits on top of Java, so the language material is a genuine prerequisite rather than a cross-reference:

- [[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection]] — the container concept, pulled out from under the framework
- [[languages/01-java/02-jvm-and-concurrency/index|JVM & Concurrency]] — what thread-per-request and virtual threads actually mean
- [[languages/01-java/04-persistence/index|Persistence]] — JDBC and JPA, the layer under `@Repository`
- [[languages/01-java/03-tooling/01-build-tools|Build Tools]] — Maven/Gradle, and how Spring Boot's plugin packages a fat jar
- [[languages/01-java/03-tooling/04-testing|Testing]] — `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest` slices

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the Spring Boot way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **01 — What Spring Boot is and a first app**: starters, auto-configuration, the embedded server — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
2. **02 — Controllers**: `@RestController`, request mappings, `ResponseEntity` — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
3. **03 — The request pipeline**: servlet filters and `HandlerInterceptor` — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
4. **04 — Structure**: controller, service and repository layers, packages by feature — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
5. **05 — Dependency injection**: the container, constructor injection, bean scopes — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
6. **06 — Input validation**: Bean Validation, `@Valid`, custom constraints, enum shims — written in part: [[backend/frameworks/spring-boot/03-api-design-and-documentation|API Design & Documentation]]
7. **07 — Errors and structured responses**: `@ControllerAdvice`, `ProblemDetail`, business codes over raw status, and one response shape for success and failure — written in part: [[backend/frameworks/spring-boot/03-api-design-and-documentation|API Design & Documentation]]
8. **08 — Data**: Spring Data JPA, `@Transactional`, Flyway migrations

**Part 2: designing the API properly**

9. **09 — Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with Spring Data `Pageable`, `Sort` and Specifications
10. **10 — Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with path, header and media-type versioning, including Spring Framework 7's built-in API versioning
11. **11 — API docs**: generating OpenAPI docs with springdoc-openapi

**Part 3: who can do what**

12. **12 — Authentication**: the Spring Security filter chain, a JWT resource server, method security
13. **13 — Authorization**: roles and owning your own orders, with Spring Security method security and `@PreAuthorize`
14. **14 — Security**: CORS, rate limiting, `@Async`, `@Scheduled`, outbound calls — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
15. **15 — Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **16 — Testing**: `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest`, Testcontainers

**Part 4: what real products need**

17. **17 — Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **18 — Background jobs and queues**: work the customer shouldn't wait for, with Spring AMQP queues and `@Scheduled` jobs
19. **19 — Caching**: caching hot reads with Spring Cache on Redis, and keeping the cache honest
20. **20 — Real-time updates**: a live kitchen screen with WebSocket with STOMP

**Part 5: other ways to talk**

21. **21 — GraphQL**: the same data as a GraphQL API with Spring for GraphQL, and when it beats REST
22. **22 — gRPC**: Protocol Buffers and a gRPC service with Spring gRPC
23. **23 — Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with Spring AI's MCP server starter
24. **24 — MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **25 — Splitting out a microservice**: a separate notifications service, events over Spring Cloud Stream on RabbitMQ or Kafka, the outbox pattern
26. **26 — Calling other services safely**: `RestClient` with Resilience4j, circuit breakers, service-to-service auth

**Part 7: production**

27. **27 — Observability**: logs, request IDs across services, metrics and tracing with Micrometer, Actuator and OpenTelemetry
28. **28 — Production config and Docker**: profiles and config, Actuator, virtual threads, OpenAPI with springdoc, and the wider Java landscape; a layered Docker image and Spring profiles, Docker Compose for the whole system — written in part: [[backend/frameworks/spring-boot/02-web-frameworks|Web Frameworks]]
29. **29 — CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|frameworks/]] — the same concepts across every stack
- [[backend/03-structuring-a-backend/index|Structuring a Backend]] — the layering Spring's annotations name
- [[languages/01-java/index|Java course]] — the language underneath
- [[languages/01-java/interview/03-spring-persistence-and-systems|Spring interview prep]]
- direct-debit-sandbox — the project this material came from
