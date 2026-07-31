# 02 — Building Blocks

The reusable components every large system is assembled from. Learn these and most system designs become "arrange the right blocks." Part of the [[architecture/README|Architecture course]].

1. [[architecture/02-building-blocks/01-load-balancing-and-proxies|Load Balancing & Proxies]] — **[Intermediate]** — L4/L7 load balancing, algorithms, reverse proxy, API gateway, CDN
2. [[architecture/02-building-blocks/02-caching|Caching]] — **[Intermediate]** — the cache strategies (cache-aside/write-through/write-behind), where to cache, eviction, and invalidation
3. [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — **[Intermediate → Advanced]** — SQL vs NoSQL, replication, sharding, indexing, denormalization
4. [[architecture/02-building-blocks/04-messaging-and-async|Messaging & Async]] — **[Intermediate]** — message queues, pub/sub, event-driven design, back-pressure, queue-based load leveling
5. [[architecture/02-building-blocks/05-communication|Communication]] — **[Intermediate]** — REST vs gRPC vs GraphQL, sync vs async, and the protocols underneath

## Related
- [[architecture/01-system-design-fundamentals/README|Fundamentals]] — the tradeoffs these blocks navigate
- [[architecture/03-architectural-patterns/README|Architectural Patterns]] — arranging these blocks into whole architectures
- [[languages/01-java/06-applied-systems/01-messaging-with-rabbitmq|Messaging with RabbitMQ (Java)]] — a building block built in real code
