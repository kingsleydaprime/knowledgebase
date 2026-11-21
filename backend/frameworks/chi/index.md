# Chi (Go Backends)

## What Chi is

**Chi is a small router for Go that adds route groups and shared middleware to the standard library, and changes nothing else.** Its handlers and middleware are ordinary `net/http` types. So you can add Chi to a stdlib server, or take it out again, without rewriting a single handler.

## Lessons so far

1. [[backend/frameworks/chi/01-chi|Chi]]

**Because Chi is `net/http`**, most of the plan below uses the same tools as [[backend/frameworks/net-http/index|net/http]]. Its lessons focus on what Chi changes: grouping, its middleware package, and loading shared data once per route group.

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Chi way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Chi is**: what a router still adds after Go 1.22, and how Chi stays `net/http` compatible — written in part: [[backend/frameworks/chi/01-chi|Chi]]
2. **Routing**: `r.Route`, `r.Group`, URL params, mounting sub-routers — written in part: [[backend/frameworks/chi/01-chi|Chi]]
3. **Middleware**: Chi's `middleware` package: RequestID, RealIP, Recoverer, Timeout, `WrapResponseWriter`
4. **Structure**: a router per feature, mounted in `main`
5. **Wiring**: handlers as methods on a struct that holds their dependencies
6. **Validation**: binding and rendering with `go-chi/render`, or a validator
7. **Errors**: one error renderer for the whole router
8. **Data**: loading a resource once with context middleware, `database/sql` underneath
9. **Auth**: `jwtauth` and auth per route group
10. **Security and cross-cutting**: `go-chi/cors`, `httprate`, throttling
11. **Testing**: `httptest` against a Chi router
12. **Production**: timeouts, shutdown and observability, and how to swap Chi out later

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/net-http/index|net/http]] — what Chi wraps
- [[backend/frameworks/gin/index|Gin]] — the batteries-included alternative
- [[languages/02-go/index|The Go course]]

## About this subject

`[reference]`. Until November 2026 Chi and Gin were one lesson inside the Go subject, which is now [[backend/frameworks/net-http/index|net/http]].
