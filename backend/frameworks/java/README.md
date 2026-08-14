# Java Backends — Spring Boot

**Doing backend work in Java? Start here.** This is the Spring Boot material, and it's the deepest framework section in the vault — ~3,000 words distilled from a real Spring Boot payment sandbox, not from documentation.

**Concurrency model: thread-per-request.** Spring MVC on a servlet container gives every request its own OS thread — simple to reason about, expensive at scale. From Java 21, **virtual threads** turn it into green threads *without a code change*, which is the biggest thing to happen to Java backends in a decade. Spring **WebFlux** is the event-loop/reactive alternative, and Loom has largely removed the reason to reach for it: you can now get the scalability without the reactive programming model. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime & concurrency models]]

## Reading order

1. [[backend/frameworks/java/01-spring-boot|Spring Boot & Scheduling]] — **[Intermediate]** — what the framework actually does for you, dependency injection, controller/service/store layering, validation, `ResponseEntity`, `HandlerInterceptor`, `@Async` offloading, `@Scheduled` jobs, and a retry state machine
2. [[backend/frameworks/java/02-web-frameworks|The Java Web Landscape]] — **[reference]** — Quarkus, Micronaut, Javalin, Play: what each optimises for, and why the GraalVM native-image push exists
3. [[backend/frameworks/java/03-api-design-and-documentation|API Design & Documentation]] — **[Intermediate]** — `RestTemplate` for outbound calls, the config-resolution/fallback pattern, business codes over raw HTTP status, and OpenAPI/springdoc

## Where this moved from, and why

These three notes **used to live in `languages/01-java/05-web-and-api/`**. They were **moved here, not copied** — there is exactly one copy of this material and it is this one.

The reason is a rule that now applies across the vault:

> **`languages/` teaches the language. `backend/frameworks/` teaches the frameworks built on it.**

So `languages/01-java/` keeps the JVM, concurrency, generics, collections, tooling and persistence — the things true of Java whether or not you ever serve an HTTP request. Spring Boot is a *web framework*, and it belongs next to Express, Nest, Axum and Gin, where you can compare them.

That comparison is the point. Spring's `@RestController` / `@Service` / `@Repository` and Nest's `@Controller` / `@Injectable` are the same idea with different spelling — which is obvious when they sit in one folder and invisible when they're filed under different languages. See the translation table in [[backend/frameworks/README|frameworks/]].

## What you still need from `languages/01-java/`

Spring Boot sits on top of Java, so the language material is a genuine prerequisite rather than a cross-reference:

- [[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection]] — the container concept, pulled out from under the framework
- [[languages/01-java/02-jvm-and-concurrency/README|JVM & Concurrency]] — what thread-per-request and virtual threads actually mean
- [[languages/01-java/04-persistence/README|Persistence]] — JDBC and JPA, the layer under `@Repository`
- [[languages/01-java/03-tooling/01-build-tools|Build Tools]] — Maven/Gradle, and how Spring Boot's plugin packages a fat jar
- [[languages/01-java/03-tooling/04-testing|Testing]] — `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest` slices

## Related
- [[backend/frameworks/README|frameworks/]] — the same concepts across every stack
- [[backend/03-structuring-a-backend/README|Structuring a Backend]] — the layering Spring's annotations name
- [[languages/01-java/README|Java course]] — the language underneath
- [[languages/01-java/interview/03-spring-persistence-and-systems|Spring interview prep]]
- [[projects/direct-debit-sandbox-java/learning/02-spring-boot-basics|direct-debit-sandbox]] — the project this material came from
