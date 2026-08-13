# record-id-generator-java — Learning Notes

High-throughput record ID generation: CSV in, RabbitMQ in the middle, MySQL out. **The most systems-flavoured project in the vault** — concurrency, messaging, idempotency, and performance tuning all showed up here for real, which makes it the best interview material you have for a [[PRIMETECHIE|Rank III]] / low-latency conversation.

## Reading order

1. [[projects/record-id-generator-java/learning/01-java-fundamentals|01 — Java Fundamentals]] → general: [[languages/01-java/01-language/README|languages/01-java/01-language]]
2. [[projects/record-id-generator-java/learning/02-build-tools-and-architecture|02 — Build Tools & Architecture]] → [[languages/01-java/03-tooling/01-build-tools|build tools]]
3. [[projects/record-id-generator-java/learning/03-lombok-and-configuration|03 — Lombok & Configuration]] → [[languages/01-java/03-tooling/03-lombok-and-builders|lombok & builders]]
4. [[projects/record-id-generator-java/learning/04-database-mysql-flyway|04 — MySQL & Flyway]] → [[databases/mysql-reference|MySQL reference]], [[databases/interview/01-sql-modelling-and-internals|db interview]]
5. [[projects/record-id-generator-java/learning/05-rabbitmq-messaging|05 — RabbitMQ Messaging]] → [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|messaging]], [[architecture/02-building-blocks/04-messaging-and-async|messaging & async]]
6. [[projects/record-id-generator-java/learning/06-concurrency-and-threads|06 — Concurrency & Threads]] → [[languages/01-java/02-jvm-and-concurrency/02-concurrency|concurrency]] ⭐
7. [[projects/record-id-generator-java/learning/07-id-generation-and-idempotency|07 — ID Generation & Idempotency]] → [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|id generation]] ⭐
8. [[projects/record-id-generator-java/learning/08-csv-parsing-and-data-quality|08 — CSV Parsing & Data Quality]]
9. [[projects/record-id-generator-java/learning/09-logging-and-observability|09 — Logging & Observability]] → [[devops/10-observability/README|observability]]
10. [[projects/record-id-generator-java/learning/10-docker-and-performance-tuning|10 — Docker & Performance Tuning]] → [[languages/01-java/06-applied-systems/04-docker-for-java-apps|docker for java]]

⭐ = the two that carry the most interview weight.

## Interview
[[projects/record-id-generator-java/interview/README|interview/]] — this material as questions.

## Related
- [[projects/README|All projects and the domains they exercise]] · [[languages/01-java/interview/README|Java interview prep]]
- [[project-ideas|Project Ideas]] — JMH benchmarks and a GC tuning study on this pipeline are listed 🟡 reps
