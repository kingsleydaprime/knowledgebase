---
subject: false
---

# Actix Web (Rust Backends)

## What Actix Web is

**Actix Web is a fast, mature framework for building web servers in Rust.** It is the main alternative to Axum. It has its own middleware system and gives each CPU core its own worker with its own state.

## Lessons so far

1. [[backend/frameworks/actix-web/01-actix-web|Actix Web]]

This subject has fewer than three lessons, so `subject: false` keeps it off the platform until more are written.

## Actix Web next to Axum

| | Axum | Actix Web |
|---|---|---|
| Middleware | `tower` — shared ecosystem | its own |
| Routing | function calls | attribute macros |
| Ecosystem reuse | high | lower |
| Model | shared state | thread-per-core |

[[backend/frameworks/axum/index|Axum]] is the usual default, mostly because of `tower`. Actix is mature, marginally faster, and a fine choice. Its async rules are the same → [[backend/frameworks/axum/04-async-pitfalls|Async Pitfalls]].

## Lesson plan

This subject teaches the whole [[backend/index|backend course]] the Actix Web way. Each lesson below is one stop on that path. A link means a lesson already covers it, at least in part; the rest are still to write.

1. **What Actix Web is and a first server**: `HttpServer`, `App`, and how it differs from Axum — written in part: [[backend/frameworks/actix-web/01-actix-web|Actix Web]]
2. **Routing**: attribute macros, `web::resource`, scopes
3. **Middleware**: `wrap`, `wrap_fn`, and the `Transform` trait
4. **Structure**: a `configure` function per feature
5. **State**: `web::Data`, and state per worker in a thread-per-core model
6. **Validation**: `web::Json<T>`, extractor config, validation crates
7. **Errors**: the `ResponseError` trait
8. **Data**: sqlx with Actix, and `web::block` for blocking work
9. **Auth**: `FromRequest` extractors for auth, sessions and identity
10. **Security and cross-cutting**: `actix-cors`, rate limiting with `actix-governor`, multipart uploads
11. **Testing**: `actix_web::test`
12. **Production**: worker count, graceful shutdown, tracing

## Related
- [[backend/frameworks/index|All frameworks]]
- [[backend/frameworks/axum/index|Axum]] — the other main Rust option
- [[languages/03-rust/index|The Rust course]]

## About this subject

`[reference]`. Until November 2026 Actix Web was one section inside the Rust subject, which is now [[backend/frameworks/axum/index|Axum]].
