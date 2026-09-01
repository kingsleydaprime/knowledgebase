# 05 — Web & API → moved to `backend/frameworks/java/`

**This section's notes were moved, not duplicated.** Spring Boot, the Java web-framework landscape, and API design/documentation now live at:

### → **[[backend/frameworks/java/README|backend/frameworks/java/]]**

- [[backend/frameworks/java/01-spring-boot|Spring Boot & Scheduling]] — DI, the controller/service/store layering, validation, `@Async`, `@Scheduled`, retry state machines
- [[backend/frameworks/java/02-web-frameworks|The Java Web Landscape]] — Quarkus, Micronaut, Javalin, Play **[reference]**
- [[backend/frameworks/java/03-api-design-and-documentation|API Design & Documentation]] — `RestTemplate`, config-resolution patterns, business codes, OpenAPI/springdoc

There is **one copy** of that material and it's the one linked above. Nothing was left behind here and nothing was cloned — this page is a signpost, not a stub.

## Why it moved

A rule that now holds across the vault:

> **`languages/` teaches the language. `backend/frameworks/` teaches the frameworks built on it.**

Java the language — the JVM, concurrency, generics, collections, tooling, persistence — stays in this course, because it's true whether or not you ever serve HTTP. Spring Boot is a web framework, and it's more useful sitting beside Express, NestJS, Axum and Gin than filed under the language it happens to be written in: that's the only arrangement where you can see that `@RestController`/`@Service` and Nest's `@Controller`/`@Injectable` are the same idea in different spelling.

The same rule puts Go's Gin and Rust's Axum in `backend/frameworks/` rather than in their language courses.

## If you're here for Java

You probably want one of these instead:

| You want | Go to |
|---|---|
| To build an HTTP service in Java | [[backend/frameworks/java/README\|backend/frameworks/java/]] |
| The DI concept, not Spring's version of it | [[languages/01-java/03-tooling/02-dependency-injection\|03-tooling/02-dependency-injection]] |
| Threads, virtual threads, the memory model | [[languages/01-java/02-jvm-and-concurrency/README\|02-jvm-and-concurrency/]] |
| JDBC, JPA, transactions | [[languages/01-java/04-persistence/README\|04-persistence/]] |
| The rest of the Java course | [[languages/01-java/README\|Java course index]] |

## Related
- [[backend/frameworks/java/README|backend/frameworks/java/]] — where this went
- [[backend/frameworks/README|frameworks/]] — every stack, compared
- [[languages/01-java/README|Java course index]]
