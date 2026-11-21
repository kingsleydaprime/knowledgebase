# Spring Boot (Java Backends)

## What Spring Boot is

**Spring Boot is the framework most Java companies use to build web servers and APIs.** It gives you a lot ready-made: routing, database access, security and configuration.

**Doing backend work in Java? Start here.** This is the Spring Boot material, and it's the deepest framework section in the vault — ~3,000 words distilled from a real Spring Boot payment sandbox, not from documentation.

**Concurrency model: thread-per-request.** Spring MVC on a servlet container gives every request its own OS thread — simple to reason about, expensive at scale. From Java 21, **virtual threads** turn it into green threads *without a code change*, which is the biggest thing to happen to Java backends in a decade. Spring **WebFlux** is the event-loop/reactive alternative, and Loom has largely removed the reason to reach for it: you can now get the scalability without the reactive programming model. → [[backend/01-foundations/04-runtime-and-concurrency-models/index|runtime & concurrency models]]

## Lessons so far

1. [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]] — **[Intermediate]** — what the framework actually does for you, dependency injection, controller/service/store layering, validation, `ResponseEntity`, `HandlerInterceptor`, `@Async` offloading, `@Scheduled` jobs, and a retry state machine
2. [[backend/frameworks/spring-boot/02-web-frameworks|The Java Web Landscape]] — **[reference]** — Quarkus, Micronaut, Javalin, Play: what each optimises for, and why the GraalVM native-image push exists
3. [[backend/frameworks/spring-boot/03-api-design-and-documentation|API Design & Documentation]] — **[Intermediate]** — `RestTemplate` for outbound calls, the config-resolution/fallback pattern, business codes over raw HTTP status, and OpenAPI/springdoc

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

This subject teaches the whole [[backend/index|backend course]] the Spring Boot way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Spring Boot is and a first app**: starters, auto-configuration, the embedded server — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
2. **Controllers**: `@RestController`, request mappings, `ResponseEntity` — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
3. **The request pipeline**: servlet filters and `HandlerInterceptor` — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
4. **Structure**: controller, service and repository layers, packages by feature — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
5. **Dependency injection**: the container, constructor injection, bean scopes — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
6. **Validation**: Bean Validation, `@Valid`, custom constraints, enum shims — written in part: [[backend/frameworks/spring-boot/03-api-design-and-documentation|API Design & Documentation]]
7. **Errors**: `@ControllerAdvice`, `ProblemDetail`, business codes over raw status — written in part: [[backend/frameworks/spring-boot/03-api-design-and-documentation|API Design & Documentation]]
8. **Data**: Spring Data JPA, `@Transactional`, Flyway migrations
9. **Auth**: the Spring Security filter chain, a JWT resource server, method security
10. **Cross-cutting**: CORS, rate limiting, `@Async`, `@Scheduled`, outbound calls — written in part: [[backend/frameworks/spring-boot/01-spring-boot|Spring Boot & Scheduling]]
11. **Testing**: `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest`, Testcontainers
12. **Production**: profiles and config, Actuator, virtual threads, OpenAPI with springdoc, and the wider Java landscape — written in part: [[backend/frameworks/spring-boot/02-web-frameworks|Web Frameworks]]

## Related
- [[backend/frameworks/index|frameworks/]] — the same concepts across every stack
- [[backend/03-structuring-a-backend/index|Structuring a Backend]] — the layering Spring's annotations name
- [[languages/01-java/index|Java course]] — the language underneath
- [[languages/01-java/interview/03-spring-persistence-and-systems|Spring interview prep]]
- [[projects/direct-debit-sandbox-java/learning/02-spring-boot-basics|direct-debit-sandbox]] — the project this material came from
