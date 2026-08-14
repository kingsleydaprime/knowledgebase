# Java Backends — see languages/01-java

**Spring Boot lives in [[languages/01-java/05-web-and-api/README|languages/01-java/05-web-and-api]]**, alongside the JVM, concurrency, tooling, and persistence material it depends on. It is not duplicated here — duplicating it would recreate exactly the split this course was restructured to remove.

- [[languages/01-java/05-web-and-api/01-spring-boot|Spring Boot]] · [[languages/01-java/05-web-and-api/03-api-design-and-documentation|API design & docs]] · [[languages/01-java/04-persistence/README|persistence]]

## Concurrency model
Classically **thread-per-request** (Spring MVC on a servlet container), with **virtual threads** from Java 21 turning it into green threads without a code change. Spring **WebFlux** is the event-loop/reactive alternative — and Loom has largely removed the reason to reach for it, since you can now get the scalability without the reactive programming model. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

## Related
- [[backend/frameworks/README|frameworks/]] · [[languages/01-java/interview/03-spring-persistence-and-systems|Spring interview prep]]
