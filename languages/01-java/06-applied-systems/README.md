# 06 — Applied Systems

The project-grounded section: building an actual high-throughput data system, not just learning language features. This is where the domain earns its "real engineering" signal — every note here is distilled from a pipeline that moved millions of rows. Part of the [[languages/01-java/README|Java course]].

1. [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ]] — message brokers, Dead Letter Queues, backpressure/prefetch, competing consumers, per-consumer connections
2. [[languages/01-java/06-applied-systems/02-id-generation-and-idempotency|ID Generation & Idempotency]] — the birthday-paradox collision math, UUID v4/v7 / Snowflake / ULID tradeoffs, making a pipeline idempotent with a business-key hash
3. [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing & Performance]] — streaming vs chunking vs batch inserts, the JDBC `rewriteBatchedStatements` gotcha, MySQL bulk-load tuning, load-then-index
4. [[languages/01-java/06-applied-systems/04-docker-for-java-apps|Docker for Java Apps]] — multi-stage builds, dev compose, container file-descriptor/resource limits

## Related
- [[languages/01-java/02-jvm-and-concurrency/README|JVM & Concurrency]] — the concurrency primitives these systems are built from
- [[languages/01-java/04-persistence/01-jdbc-and-data-modeling|JDBC & Data Modeling]] — the persistence layer under the pipeline
- [[languages/01-java/README|Java course index]]
