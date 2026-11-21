---
subject: false
---

# civetweb (C Backends)

## What civetweb is

**civetweb is a tiny web server for C that you add as one header and one source file.** It is what you reach for when a device or desktop app needs a small web page or API, and it is common in firmware.

## Lessons so far

1. [[backend/frameworks/civetweb/01-civetweb|civetweb]]

This subject has fewer than three lessons, so `subject: false` keeps it off the platform until more are written.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the civetweb way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What civetweb is and a first server**: one header and one source file, a thread pool — written in part: [[backend/frameworks/civetweb/01-civetweb|civetweb]]
2. **Request handlers**: `mg_set_request_handler` and routing
3. **Reading requests**: `mg_get_request_info`, reading the body
4. **Writing responses**: status, headers, `mg_printf`
5. **Structure**: a handler per resource, and user data
6. **Validation and JSON**: cJSON, checking every field
7. **Errors**: status codes and failure paths
8. **Data**: SQLite in an embedded app
9. **Auth and TLS**: digest auth, TLS
10. **WebSockets**: civetweb's WebSocket handlers
11. **Testing**: driving it from tests
12. **Embedding and production**: threads, options, running inside firmware

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side
- [[languages/04-c/index|The C course]]
- [[backend/frameworks/libmicrohttpd/index|libmicrohttpd]] — the other embedding option

## About this subject

`[reference]`. Until November 2026 this was one section inside the C subject, which is now [[backend/frameworks/c-sockets/index|Sockets and epoll]]. Read that subject's [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] lesson before shipping any C server.
