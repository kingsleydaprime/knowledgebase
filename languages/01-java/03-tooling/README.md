# 03 — Tooling

Everything around the code: building it, wiring it together, testing it, and seeing what it's doing in production. Part of the [[languages/01-java/README|Java course]].

1. [[languages/01-java/03-tooling/01-build-tools|Build Tools]] — Maven vs Gradle vs Bazel, the Gradle wrapper, dependency management, project structure conventions
2. [[languages/01-java/03-tooling/02-dependency-injection|Dependency Injection]] — inversion of control, constructor vs field injection, and how Spring's container implements it
3. [[languages/01-java/03-tooling/03-lombok-and-builders|Lombok & Builders]] — killing boilerplate with `@Data`/`@Builder`/`@Slf4j`, DTOs, the builder pattern (and how records now overlap it — see [[languages/01-java/01-language/07-modern-java|Modern Java]])
4. [[languages/01-java/03-tooling/04-testing|Testing]] — JUnit 5 and Mockito in depth, plus the TestNG / Cucumber / REST Assured / JMeter landscape
5. [[languages/01-java/03-tooling/05-logging-and-observability|Logging & Observability]] — SLF4J as the facade, Logback / Log4j2 / tinylog as implementations, the log-table pattern, throughput/latency metrics

## Related
- [[languages/01-java/05-web-and-api/README|Web & API]] — where DI and these tools get applied
- [[languages/01-java/README|Java course index]]
