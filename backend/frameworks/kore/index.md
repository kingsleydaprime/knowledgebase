---
subject: false
---

# Kore (C Backends)

## What Kore is

**Kore is a full web framework for C, built around security.** Routing, TLS, WebSockets and PostgreSQL support are built in. Its worker processes run with the least power possible, so if an attacker breaks one, the damage stays small.

## Lessons so far

1. [[backend/frameworks/kore/01-kore|Kore]]

This subject has fewer than three lessons, so `subject: false` keeps it off the platform until more are written.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Kore way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Kore is and a first app**: a handler, a config file, and privilege separation — written in part: [[backend/frameworks/kore/01-kore|Kore]]
2. **Routing and config**: routes, regex params, methods
3. **Hooks**: parent and worker hooks
4. **Structure**: the `kodev` project layout
5. **Validation**: Kore's built-in parameter validators
6. **JSON**: Kore's JSON API
7. **Errors**: status codes and failure paths in handlers
8. **Data**: async PostgreSQL queries with `kore_pgsql`
9. **Auth**: Kore's authentication blocks
10. **Security**: privilege separation, `seccomp`, TLS by default — written in part: [[backend/frameworks/kore/01-kore|Kore]]
11. **Background work**: tasks and WebSockets
12. **Testing and production**: building with `kodev`, deploying a Kore binary

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/c-sockets/03-choosing-a-c-framework|Choosing a C Framework]] — every C option side by side
- [[languages/04-c/index|The C course]]

## About this subject

`[reference]`. Until November 2026 this was one section inside the C subject, which is now [[backend/frameworks/c-sockets/index|Sockets and epoll]]. Read that subject's [[backend/frameworks/c-sockets/02-parsing-http-safely|Parsing HTTP Safely]] lesson before shipping any C server.
