# Gin (Go Backends)

## What Gin is

**Gin is the most popular web framework for Go. It gives you routing, request binding and validation, and its own context type.** Your handlers take a `*gin.Context` instead of the standard `http.ResponseWriter` and `*http.Request`. You get a lot of helpers, but your code belongs to Gin.

## Lessons so far

1. [[backend/frameworks/gin/01-gin|Gin]]

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Gin way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Gin is and a first server**: `gin.Default()`, `*gin.Context`, and the lock-in trade — written in part: [[backend/frameworks/gin/01-gin|Gin]]
2. **Routing**: groups, `c.Param`, `c.Query` — written in part: [[backend/frameworks/gin/01-gin|Gin]]
3. **Middleware**: `gin.HandlerFunc`, `c.Next`, `c.Abort`
4. **Structure**: a route group per feature, handlers kept thin
5. **Wiring**: dependencies through structs and closures, and why `c.Set` isn't DI
6. **Validation**: `ShouldBind*` and `binding` tags — written in part: [[backend/frameworks/gin/01-gin|Gin]]
7. **Errors**: `c.Error`, an error middleware, `AbortWithStatusJSON`
8. **Data**: GORM or sqlc behind a repository
9. **Auth**: JWT middleware and role checks
10. **Security and cross-cutting**: `gin-contrib/cors`, rate limiting, `c.FormFile` uploads
11. **Testing**: `httptest` with `gin.TestMode`
12. **Production**: release mode, trusted proxies and `ClientIP`, graceful shutdown through `http.Server`

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/chi/index|Chi]] — the stdlib-compatible alternative, and the full comparison
- [[backend/frameworks/net-http/index|net/http]] — what Gin sits on
- [[languages/02-go/index|The Go course]]

## About this subject

`[reference]`. Until November 2026 Chi and Gin were one lesson inside the Go subject, which is now [[backend/frameworks/net-http/index|net/http]].
