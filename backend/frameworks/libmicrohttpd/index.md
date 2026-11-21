---
subject: false
---

# libmicrohttpd (C Backends)

## What libmicrohttpd is

**libmicrohttpd is a small GNU library that adds an HTTP server to a C program.** You give it one callback, and it calls that for every request. It is the usual choice when a program that already exists needs a web interface, because it can run inside the event loop you already have.

## Lessons so far

1. [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]

This subject has fewer than three lessons, so `subject: false` keeps it off the platform until more are written.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the libmicrohttpd way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What libmicrohttpd is and a first server**: one callback for everything — written in part: [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]
2. **Routing**: dispatching on URL and method yourself
3. **Reading the body**: the `con_cls` state machine, the post processor — written in part: [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]
4. **Threading modes**: thread per connection, a pool, or driving it from your own loop — written in part: [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]
5. **Structure**: a handler table and per-request state
6. **Validation and JSON**: parsing input with a JSON library, checking every field
7. **Errors and response memory**: status codes, and the memory modes that decide who frees what — written in part: [[backend/frameworks/libmicrohttpd/01-libmicrohttpd|libmicrohttpd]]
8. **Data**: libpq from inside a handler
9. **Auth and TLS**: the basic and digest auth helpers, TLS with GnuTLS
10. **Limits**: connection limits, timeouts, memory limits
11. **Testing**: curl-driven tests, ASan
12. **Production**: hardening, and a reverse proxy in front

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side
- [[languages/04-c/index|The C course]]
- [[backend/frameworks/ulfius/index|Ulfius]] — routing and JSON on top of libmicrohttpd

## About this subject

`[reference]`. Until November 2026 this was one section inside the C subject, which is now [[backend/frameworks/c-sockets/index|Sockets and epoll]]. Read that subject's [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] lesson before shipping any C server.
