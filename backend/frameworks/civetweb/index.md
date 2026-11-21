# civetweb (C Backend)

## What civetweb is

**civetweb is a tiny web server for C that you add as one header and one source file.** It is what you reach for when a device or desktop app needs a small web page or API, and it is common in firmware.

## Lessons so far

1. [[backend/frameworks/civetweb/01-civetweb|civetweb]]

## Lesson plan

This subject builds **one production backend** from the first lesson to the last, the civetweb way: a food-ordering API with a well-designed REST interface, GraphQL, an MCP server for AI assistants, payments and webhooks, background jobs, a live kitchen screen and a second, separate service for notifications reached over gRPC and events, then tested, observed and deployed. Every lesson ends with the project's folder structure so far, and explains the language features it used. Each stop below is one lesson. A link means a lesson already covers it, at least in part; the rest are still to write.

**Part 1: the core backend**

1. **What civetweb is and a first server**: one header and one source file, a thread pool — written in part: [[backend/frameworks/civetweb/01-civetweb|civetweb]]
2. **Request handlers**: `mg_set_request_handler` and routing
3. **Reading requests**: `mg_get_request_info`, reading the body
4. **Writing responses**: status, headers, `mg_printf`
5. **Structure**: a handler per resource, and user data
6. **Input validation**: cJSON, checking every field
7. **Errors and structured responses**: status codes and failure paths, and one response shape for success and failure
8. **Data**: SQLite in an embedded app

**Part 2: designing the API properly**

9. **Pagination, filtering, searching, sorting and field selection**: offset and cursor pagination with parsing the query string with `mg_get_var`, keyset pagination
10. **Versioning**: every way to version an API, running v1 and v2 side by side, and deprecating one, with a handler prefix per version
11. **API docs**: generating OpenAPI docs with a hand-written OpenAPI file

**Part 3: who can do what**

12. **Authentication**: digest auth, TLS
13. **Authorization**: roles and owning your own orders, with permission checks per handler
14. **Security**: civetweb's WebSocket handlers
15. **Idempotency**: the `Idempotency-Key` header, so a retried request never happens twice
16. **Testing**: driving it from tests

**Part 4: what real products need**

17. **Payments and webhooks**: Paystack checkout, receiving and verifying webhooks, and sending signed webhooks of your own
18. **Background jobs and queues**: work the customer shouldn't wait for, with a worker thread
19. **Caching**: caching hot reads with hiredis, and keeping the cache honest
20. **Real-time updates**: a live kitchen screen with civetweb WebSockets

**Part 5: other ways to talk**

21. **GraphQL**: the same data as a GraphQL API with why GraphQL in C is rarely worth it, and when it beats REST
22. **gRPC**: Protocol Buffers and a gRPC service with protobuf-c and the gRPC core
23. **Building an MCP server**: the menu and orders as tools and resources an AI assistant can use, with JSON-RPC 2.0 over Streamable HTTP by hand
24. **MCP in production**: OAuth so the AI acts as the customer, the same permissions as every route, prompt injection, confirming before spending money, rate limits

**Part 6: more than one service**

25. **Splitting out a microservice**: a separate notifications service, events over NATS's C client, the outbox pattern
26. **Calling other services safely**: libcurl with timeouts, circuit breakers, service-to-service auth

**Part 7: production**

27. **Observability**: logs, request IDs across services, metrics and tracing with syslog and counters
28. **Production config and Docker**: threads, options, running inside firmware; a Docker image, or firmware, Docker Compose for the whole system
29. **CI and deployment**: CI running the tests, migrations on deploy, deploying to a real server, and rolling back

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side
- [[languages/04-c/index|The C course]]
- [[backend/frameworks/libmicrohttpd/index|libmicrohttpd]] — the other embedding option

## About this subject

`[reference]`. Until November 2026 this was one section inside the C subject, which is now [[backend/frameworks/c-sockets/index|Sockets and epoll]]. Read that subject's [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] lesson before shipping any C server.
