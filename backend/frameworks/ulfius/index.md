# Ulfius (C Backends)

## What Ulfius is

**Ulfius is a C framework for building REST APIs, built on top of libmicrohttpd.** It adds the parts that library leaves out: routes with path parameters, JSON, and a chain of callbacks that works like middleware. It is the closest thing C has to a normal REST framework.

## Lessons so far

1. [[backend/frameworks/ulfius/01-ulfius|Ulfius]]

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Ulfius way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Ulfius is and a first endpoint**: routing and JSON on top of libmicrohttpd — written in part: [[backend/frameworks/ulfius/01-ulfius|Ulfius]]
2. **Routing**: endpoints, prefixes, URL params — written in part: [[backend/frameworks/ulfius/01-ulfius|Ulfius]]
3. **Callback chains**: priorities and `U_CALLBACK_CONTINUE`, used like middleware — written in part: [[backend/frameworks/ulfius/01-ulfius|Ulfius]]
4. **Structure**: an endpoint file per feature
5. **Shared data**: `user_data` in place of DI
6. **Validation and JSON**: Jansson, checking every field
7. **Errors**: status codes and error bodies
8. **Data**: Hoel, the same author's database library
9. **Auth**: an auth callback, JWTs
10. **Security and cross-cutting**: CORS, uploads, WebSockets
11. **Testing**: Ulfius's client functions in tests
12. **Production**: TLS, hardening, a reverse proxy

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side
- [[languages/04-c/index|The C course]]
- [[backend/frameworks/libmicrohttpd/index|libmicrohttpd]] — what Ulfius is built on

## About this subject

`[reference]`. Until November 2026 this was one section inside the C subject, which is now [[backend/frameworks/c-sockets/index|Sockets and epoll]]. Read that subject's [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] lesson before shipping any C server.
