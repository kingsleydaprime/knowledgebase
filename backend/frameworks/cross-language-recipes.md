# Cross-Language Recipes

> **[Intermediate]** · The same production backend concerns, implemented side by side in **Node, Go, Rust, Python, C# and Java.**

**The point of this folder is comparison** → [[backend/frameworks/README|frameworks]]. The concept table there translates *vocabulary*; this translates *code*.

**Use it two ways:** to build the same real backend in a language you don't know yet, or to check that the thing you do reflexively in Node has an equivalent elsewhere — because it always does, and it's rarely called the same thing.

**Concepts first.** Each section links to the [[backend/06-cross-cutting/README|cross-cutting note]] that explains *why*; this is the *how*.

---

## 1. Middleware — the shared shape

**Every stack has the same onion.** Only the spelling differs.

```js
// Node / Express
app.use(async (req, res, next) => { const t = Date.now(); await next(); log(Date.now() - t); });
```
```go
// Go — a handler that wraps a handler. The whole idea, with no framework.
func Logging(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}
```
```rust
// Rust / Axum — tower layers
let app = Router::new().route("/", get(handler))
    .layer(TraceLayer::new_for_http())
    .layer(TimeoutLayer::new(Duration::from_secs(10)));
```
```python
# Python / FastAPI
@app.middleware("http")
async def timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    logger.info("%s took %.3fs", request.url.path, time.perf_counter() - start)
    return response
```
```csharp
// C# / ASP.NET Core
app.Use(async (ctx, next) => { var sw = Stopwatch.StartNew(); await next(ctx); log(sw.Elapsed); });
```
```java
// Java / Spring — OncePerRequestFilter, or an interceptor
```

**Go's version is worth staring at.** `func(http.Handler) http.Handler` is the entire middleware concept with no framework, no registration and no magic — and it's why Go backends need so little framework → [[backend/frameworks/go/02-middleware-as-composition|Go middleware]].

**Order is behaviour in all six.** Auth before authorization, error handling outermost.

---

## 2. Rate limiting → [[backend/06-cross-cutting/04-rate-limiting|the concepts]]

**Reminder: in-process is per-instance.** Four replicas means 4× your limit. Use shared state unless you have exactly one instance.

| Stack | In-process | Distributed |
|---|---|---|
| **Node** | `express-rate-limit` | `rate-limit-redis` store |
| **Go** | `golang.org/x/time/rate` (token bucket, stdlib-adjacent) | `redis_rate` |
| **Rust** | `tower-governor` | `governor` + Redis |
| **Python** | `slowapi` | `slowapi` + Redis backend |
| **C#** | **`AddRateLimiter`** — built in since .NET 7 | + a distributed store |
| **Java** | Bucket4j, Resilience4j | Bucket4j + Redis/Hazelcast |

```csharp
// C# — built in, four algorithms available
builder.Services.AddRateLimiter(o => o.AddTokenBucketLimiter("api", opt => {
    opt.TokenLimit = 100; opt.TokensPerPeriod = 10;
    opt.ReplenishmentPeriod = TimeSpan.FromSeconds(1);
}));
```
```go
// Go — token bucket per key, stdlib-quality
limiter := rate.NewLimiter(rate.Limit(10), 100)   // 10/sec, burst 100
if !limiter.Allow() { http.Error(w, "rate limited", http.StatusTooManyRequests); return }
```

**Return the headers in every stack** — `Retry-After` and `RateLimit-*`. Most libraries won't unless you ask.

---

## 3. Auth: verifying a JWT → [[backend/05-auth/README|the concepts]]

**The five checks that matter, in every language:** signature, `exp`, `iss`, `aud`, and **algorithm pinning**.

| Stack | Library |
|---|---|
| **Node** | `jose` (prefer over `jsonwebtoken`) |
| **Go** | `golang-jwt/jwt/v5` |
| **Rust** | `jsonwebtoken` |
| **Python** | `pyjwt`, or `python-jose` |
| **C#** | `Microsoft.AspNetCore.Authentication.JwtBearer` — built in |
| **Java** | Spring Security OAuth2 Resource Server |

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o => {
        o.Authority = "https://issuer.example.com";
        o.TokenValidationParameters = new() {
            ValidateIssuer = true, ValidateAudience = true,
            ValidateLifetime = true, ValidateIssuerSigningKey = true };
    });
```
```go
token, err := jwt.Parse(raw, func(t *jwt.Token) (any, error) {
    if _, ok := t.Method.(*jwt.SigningMethodRSA); !ok {   // ← PIN THE ALGORITHM
        return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
    }
    return publicKey, nil
}, jwt.WithIssuer(iss), jwt.WithAudience(aud), jwt.WithExpirationRequired())
```

**The algorithm-confusion attack is why that check exists.** A token with `"alg": "none"`, or one signed with HMAC using your *public* key as the secret, is accepted by any library that trusts the header. **Pin the expected algorithm; never let the token choose** → [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]].

**Hashing passwords** — never a general-purpose hash. **Argon2id** where available, bcrypt otherwise: `argon2` (Node/Python/Rust/Go), `BCrypt.Net`, Spring Security's `PasswordEncoder`.

---

## 4. Security headers and CORS → [[backend/06-cross-cutting/06-security-headers-and-cors|the concepts]]

| Stack | Headers | CORS |
|---|---|---|
| **Node** | `helmet` | `cors` |
| **Go** | Write them; or `unrolled/secure` | `rs/cors` |
| **Rust** | `tower-http` `SetResponseHeaderLayer` | `tower-http` `CorsLayer` |
| **Python** | `secure` | `CORSMiddleware` (built in) |
| **C#** | Middleware, or the proxy | `AddCors` (built in) |
| **Java** | Spring Security defaults are good | `@CrossOrigin` / config |

```python
app.add_middleware(CORSMiddleware,
    allow_origins=["https://app.example.com"],   # ← never ["*"] with credentials
    allow_credentials=True,
    allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])
```

**`*` plus credentials is rejected by browsers in every stack.** Echo a validated origin from an allowlist — and **never reflect the `Origin` header unchecked**, which is the vulnerability that looks like a fix.

---

## 5. Graceful shutdown

**The one everybody skips**, and the reason deploys drop requests.

**On SIGTERM: stop accepting new connections, finish in-flight requests, close pools, exit.** Without it, every rolling deploy 502s a handful of users.

```go
srv := &http.Server{Addr: ":8080", Handler: mux}
go func() { srv.ListenAndServe() }()
<-ctx.Done()                                    // SIGTERM
shutdownCtx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
defer cancel()
srv.Shutdown(shutdownCtx)                       // stop accepting, drain in-flight
```
```js
process.on("SIGTERM", () => server.close(() => { pool.end(); process.exit(0); }));
```
```csharp
// ASP.NET Core does this for you — but your background work must honour the token
builder.Services.Configure<HostOptions>(o => o.ShutdownTimeout = TimeSpan.FromSeconds(15));
```

**Kubernetes sends SIGTERM, waits `terminationGracePeriodSeconds`, then SIGKILL.** Your drain timeout must be *shorter* than that grace period, or you're killed mid-request anyway → [[devops/05-orchestration/README|orchestration]].

**And remove yourself from the load balancer first** — fail readiness immediately on SIGTERM, keep serving for a few seconds, *then* drain. Otherwise traffic is still being routed to you while you shut down.

---

## 6. Structured logging → [[devops/10-observability/README|observability]]

**Fields, not interpolated strings**, in every stack:

```go
slog.Info("order created", "order_id", id, "customer_id", cust)   // stdlib since 1.21
```
```python
logger.info("order created", extra={"order_id": id})              # + structlog
```
```csharp
logger.LogInformation("Order {OrderId} created for {CustomerId}", id, cust);
```
```rust
tracing::info!(order_id = %id, customer_id = %cust, "order created");
```
```js
logger.info({ orderId: id, customerId: cust }, "order created");  // pino
```

**`OrderId` stays queryable.** An interpolated string is only greppable — and it formats even when the level is disabled, which costs you on a hot path.

**Propagate a trace ID through everything**, and return it in error bodies → [[backend/06-cross-cutting/03-error-handling|note 03]]. OpenTelemetry has an SDK for all six.

---

## 7. What each stack gives you free

| | Node/Express | Go stdlib | Rust/Axum | FastAPI | ASP.NET Core | Spring Boot |
|---|---|---|---|---|---|---|
| **DI** | ✗ | ✗ | ✗ | `Depends()` | **✓ built in** | **✓ built in** |
| **Validation** | ✗ (zod) | ✗ | serde + validator | **✓ Pydantic** | DataAnnotations | Bean Validation |
| **Rate limiting** | ✗ | ✗ | tower-governor | ✗ | **✓ built in** | ✗ |
| **OpenAPI** | ✗ | ✗ | utoipa | **✓ derived** | ✓ generated | springdoc |
| **Graceful shutdown** | manual | manual | ✓ | via server | **✓** | **✓** |
| **Structured logging** | pino | **✓ slog** | tracing | ✗ | **✓** | ✓ |

**The pattern: Express and Go stdlib give you almost nothing and get out of the way; ASP.NET Core and Spring give you almost everything and have opinions.** Neither is better — **it's a team-size decision**, and the cost of the minimal ones is that every project reassembles the same six libraries slightly differently → [[backend/frameworks/README|frameworks]].

---

## Building the same thing six times

**If you want the reps rather than the reference**, the exercise is: one endpoint, in each language, with **validation, JWT auth, rate limiting, security headers, structured logging, graceful shutdown and one integration test.**

**Expect a weekend for the first, a day for the second, and an evening thereafter** — because after two you're translating vocabulary, not learning concepts. **That convergence is the actual lesson of this page.**

## Related
- [[backend/06-cross-cutting/README|cross-cutting concerns]] — the *why* for every section here
- [[backend/frameworks/README|frameworks/]] — the concept translation table
- [[backend/05-auth/README|auth]] · [[cybersecurity/04-web-security/README|web security]]

*Source: [reference] — written Aug 2026 from each framework's own documentation.*
