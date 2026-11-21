---
id: 7b824aab-33e0-4d02-bc83-c7ceda5730db
---

# Actix Web

Actix Web is a framework for building web servers in Rust. It is the main alternative to Axum: just as fast, with its own middleware system and a thread-per-core design.

## An Actix Web server
<!-- bite: e7bc9f9a-600b-4e7a-989e-5619d84bae69 -->

The other major option:

```rust
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .app_data(web::Data::new(state.clone()))
            .service(get_user)
    })
    .bind(("0.0.0.0", 8080))?
    .run()
    .await
}

#[get("/users/{id}")]
async fn get_user(path: web::Path<u64>) -> impl Responder { ... }
```

| | Axum | Actix Web |
|---|---|---|
| Middleware | `tower` — shared ecosystem | its own |
| Routing | function calls | attribute macros or builder |
| Runtime | tokio | own (actix-rt, on tokio) |
| Per-worker state | shared | **thread-per-core**, state per worker |
| Ecosystem reuse | high | lower |

Actix is slightly faster in benchmarks and has a thread-per-core model that avoids some cross-thread synchronisation. Axum's `tower` compatibility means more reusable middleware and easier integration with `tonic` (gRPC) and other tower-based tooling.

**Axum is the current default recommendation**, largely for that ecosystem reason. Actix is mature, fast, and a perfectly good choice.

---

## Related
<!-- bite: 68ef00f3-cc0f-4936-b481-3a029c12c27a -->
- [[backend/frameworks/axum/01-axum-and-the-tower-stack|Axum and the Tower Stack]] — the other main option, and the `tower` ecosystem Actix doesn't share
- [[backend/frameworks/axum/04-async-pitfalls|Async Pitfalls]] — these apply to Actix too
- [[languages/03-rust/14-async-and-tokio|Rust: Async and Tokio]] — the runtime underneath
- [[backend/frameworks/actix-web/index|Actix Web]]

## About this lesson
<!-- bite: e3a98f98-8d19-48d6-aea1-ff1461c9258f -->

**Level:** Intermediate. **Covers:** What an Actix Web server looks like, and how it differs from Axum.
