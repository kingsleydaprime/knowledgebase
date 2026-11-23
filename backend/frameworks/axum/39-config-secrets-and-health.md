---
id: 17894e58-47b1-456a-ba65-9cd465997312
---

# Config, Secrets and Health

**Production config is every setting a program needs, read once when it starts and checked together; secrets are the settings that must never be seen; and health checks are how a program tells the machines around it whether it's alive and whether it should get traffic.**

## Before you start
<!-- bite: c0a9d3b2-9f64-493a-adcf-4e13319ad770 -->

You should have finished [[backend/frameworks/axum/38-async-pitfalls-in-production|lesson 38]]. This lesson leans on lesson 12 (`JWT_SECRET`), lesson 14 (`ALLOWED_ORIGINS`, `BEHIND_PROXY`) and observability part 1 (`telemetry::init`).

After this lesson you will be able to:

1. Read every setting once, at start, and report every problem together.
2. Keep secrets out of logs with a type, and out of the environment with `_FILE`.
3. Answer `/livez` and `/readyz`, and say why they're different.
4. Stop politely: on the signal Docker really sends, after telling the load balancer first.
5. Check a program's health in an image with no shell.
6. Decide honestly whether Rust was the right choice for this service.

## Where we stopped
<!-- bite: 573e3cf8-43f0-4c6b-86d4-bfb0b3bd9a2d -->

Look at how the API got its settings until now: `env("PUBLIC_URL")?` in one place, `std::env::var("GRPC_ADDR").unwrap_or_else(...)` in another, `Keys::from_env()` inside the auth module, and the address it listens on, `127.0.0.1:8080`, written into `main`. Three problems hide in that:

1. **The first missing setting stops the program.** Fix it, start again, and the next missing one stops it. Five missing settings, five tries.
2. **Secrets are ordinary strings.** One `tracing::info!(?settings)` and the Paystack key is in the logs.
3. **`127.0.0.1` inside a container is the container itself.** Nothing outside could ever reach the API. It worked on the laptop only because everything ran on the laptop.

## The kid version
<!-- bite: b5f4c9f5-6f95-47c6-b3d1-542f71b304e8 -->

Before opening, Mama walks round the stall with a list: gas, rice, oil, plates, change. If three things are missing she wants to know all three now, not find the gas missing at noon and the change missing at one.

She keeps the cash box key on a string round her neck, not on the counter where anyone can see it.

And there's a board by the counter: "open" or "back soon". When she needs to close, she turns it to "back soon" first, finishes serving the people already waiting, and only then puts the pots away.

The list is config, checked at start. The key round her neck is a secret. The board is the health check, and turning it before closing is draining.

**Where the picture stops working.** Customers can see Mama. A load balancer can only ask a question, every couple of seconds, and believe the answer. So the program must answer honestly, including "not right now".

## Terms used in this lesson
<!-- bite: b69d8a44-5750-470d-b9b5-d25b91a56115 -->

1. **Config**: This is the settings a program reads from outside its code: addresses, URLs, keys, limits.
2. **Secret**: This is a setting that grants power if seen: a password, an API key, a signing secret.
3. **Liveness**: This is "is the process alive and answering at all?". If not, restart it.
4. **Readiness**: This is "should this copy get traffic right now?". If not, send traffic elsewhere, but don't restart it.
5. **Draining**: This is saying "not ready" while still finishing the work already in hand, before stopping.
6. **SIGTERM**: This is the signal that politely asks a program to stop. `docker stop`, Kubernetes and systemd all send it.

## Step 1: every setting, checked once
<!-- bite: 0c3b4cc0-9b1c-4cd4-8e69-9837ae4fe08f -->

`src/config.rs` reads everything through one small `Reader` that writes problems down instead of stopping:

```rust
/// Reads settings through `lookup` (the real environment in `main`, a map in tests), and writes
/// down every problem instead of stopping at the first.
pub struct Reader<F> {
    lookup: F,
    problems: Vec<String>,
}

impl<F: Fn(&str) -> Option<String>> Reader<F> {
    pub fn new(lookup: F) -> Self {
        Reader { lookup, problems: Vec::new() }
    }

    fn get(&self, name: &str) -> Option<String> {
        (self.lookup)(name).filter(|v| !v.trim().is_empty())
    }

    pub fn required(&mut self, name: &str) -> String {
        self.get(name).unwrap_or_else(|| {
            self.problems.push(format!("{name} is not set"));
            String::new()
        })
    }

    pub fn optional(&self, name: &str, default: &str) -> String {
        self.get(name).unwrap_or_else(|| default.to_owned())
    }

    /// `NAME`, or the contents of the file `NAME_FILE` names: how Docker and Kubernetes hand secrets
    /// to a program, so they're never in the environment, where `docker inspect` would show them.
    pub fn secret(&mut self, name: &str) -> Secret {
        if let Some(value) = self.get(name) {
            return Secret(value);
        }
        let file_var = format!("{name}_FILE");
        match self.get(&file_var) {
            Some(path) => match std::fs::read_to_string(&path) {
                Ok(text) => Secret(text.trim_end().to_owned()),
                Err(e) => {
                    self.problems.push(format!("{file_var}: can't read {path}: {e}"));
                    Secret(String::new())
                }
            },
            None => {
                self.problems.push(format!("{name} (or {file_var}) is not set"));
                Secret(String::new())
            }
        }
    }

    /// A setting read and turned into `T`, or a problem written down. `None` if it was missing or bad.
    pub fn parse<T: FromStr>(&mut self, name: &str, value: String) -> Option<T>
    where
        T::Err: fmt::Display,
    {
        if value.is_empty() {
            return None; // already written down as missing
        }
        value.parse().map_err(|e| self.problems.push(format!("{name} is not valid: {e}"))).ok()
    }

    pub fn problem(&mut self, text: impl Into<String>) {
        self.problems.push(text.into());
    }

    pub fn finish(self) -> Result<(), ConfigError> {
        if self.problems.is_empty() { Ok(()) } else { Err(ConfigError(self.problems)) }
    }
}
```

1. **`lookup`** is the environment in `main` and a `HashMap` in tests, like Go's `getenv` parameter in the net/http version. Tests never change the real environment (in Rust 2024, `std::env::set_var` is `unsafe`, because other threads may be reading it).
2. **`required`, `optional`, `parse`** each write a problem down and carry on, with an empty value or `None`.
3. **`finish`** turns the list into one error, or nothing.

The settings themselves:

```rust
/// The API's settings.
#[derive(Debug)]
pub struct Settings {
    pub database_url: Secret,
    pub cache_redis_url: String,
    pub limits_redis_url: String,
    pub jwt_secret: Secret,
    pub staff_key: Secret,
    pub paystack_secret_key: Secret,
    pub paystack_base_url: String,
    pub public_url: reqwest::Url,
    pub upload_dir: String,
    /// `production` turns off GraphQL introspection and gRPC reflection.
    pub app_env: String,
    /// Where the public HTTP server listens. `0.0.0.0:8080` in a container, so others can reach it.
    pub listen_addr: SocketAddr,
    pub grpc_addr: SocketAddr,
    pub metrics_addr: SocketAddr,
    pub auth_issuer: String,
    pub auth_jwks_url: reqwest::Url,
    /// `notifications=keys/notifications-public.pem,...`
    pub service_keys: Vec<(String, String)>,
    /// How long to keep answering, saying "not ready", after being told to stop.
    pub shutdown_drain: std::time::Duration,
}

impl Settings {
    pub fn from_env() -> Result<Self, ConfigError> {
        Settings::read(|name| std::env::var(name).ok())
    }
```

and the error, which lists everything at once:

```rust
/// Everything wrong with the settings, all at once.
#[derive(Debug, thiserror::Error)]
#[error("the settings have {} problem(s):\n  {}", .0.len(), .0.join("\n  "))]
pub struct ConfigError(pub Vec<String>);
```

`main` now starts:

```rust
let telemetry = telemetry::init("api", "mama_put=info,tower_http=info")?;
// Every setting, read and checked once: every problem is reported now, together.
let settings = Settings::from_env()?;
```

and everything after uses `settings.public_url`, `settings.listen_addr` and so on. `LISTEN_ADDR` defaults to `127.0.0.1:8080` for the laptop; lesson 40's Compose file sets `0.0.0.0:8080`, "every network this container has", so Caddy can reach it.

The test, from the same file:

```rust
    #[test]
    fn every_problem_at_once() {
        let err = from(&[("JWT_SECRET", "short"), ("LISTEN_ADDR", "everywhere")]).unwrap_err();
        let text = err.to_string();
        for expected in [
            "DATABASE_URL (or DATABASE_URL_FILE) is not set",
            "CACHE_REDIS_URL is not set",
            "JWT_SECRET must be at least 32 bytes",
            "LISTEN_ADDR is not valid",
            "SERVICE_KEYS is not set",
        ] {
            assert!(text.contains(expected), "missing {expected:?} in:\n{text}");
        }
        assert!(text.starts_with("the settings have 11 problem(s):"), "{text}");
    }
```

## Step 2: secrets that can't leak
<!-- bite: f48fc038-84f5-41f9-a670-1cbf5e085539 -->

```rust
/// A setting that must never be printed: `{:?}` shows `Secret(…)`, never the value.
#[derive(Clone)]
pub struct Secret(String);

impl Secret {
    pub fn new(value: impl Into<String>) -> Self {
        Secret(value.into())
    }

    /// The value itself, for the one place that needs it.
    pub fn expose(&self) -> &str {
        &self.0
    }
}

impl fmt::Debug for Secret {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("Secret(…)")
    }
}
```

`Settings` derives `Debug`, so `tracing::info!(?settings)` is safe: every secret in it prints as `Secret(…)`. To use one you must call `.expose()`, which is easy to find in a review. It's observability part 1's `Contact` trick, for keys.

### `_FILE`: secrets as files

Environment variables aren't secret. `docker inspect` shows them, they're copied into child processes, and crash reporters love to collect them. Docker and Kubernetes can instead put each secret in a **file** inside the container, at `/run/secrets/<name>`, readable only by the program. So every secret can also be given as a path:

```rust
    /// `NAME`, or the contents of the file `NAME_FILE` names: how Docker and Kubernetes hand secrets
    /// to a program, so they're never in the environment, where `docker inspect` would show them.
    pub fn secret(&mut self, name: &str) -> Secret {
        if let Some(value) = self.get(name) {
            return Secret(value);
        }
        let file_var = format!("{name}_FILE");
        match self.get(&file_var) {
            Some(path) => match std::fs::read_to_string(&path) {
                Ok(text) => Secret(text.trim_end().to_owned()),
                Err(e) => {
                    self.problems.push(format!("{file_var}: can't read {path}: {e}"));
                    Secret(String::new())
                }
            },
            None => {
                self.problems.push(format!("{name} (or {file_var}) is not set"));
                Secret(String::new())
            }
        }
    }
```

`JWT_SECRET=…` on the laptop; `JWT_SECRET_FILE=/run/secrets/jwt_secret` in Compose. `trim_end` drops the newline that every editor adds at the end of a file, which would otherwise become part of the secret.

## Step 3: two health checks
<!-- bite: f87627d6-0914-40b9-928c-bac0f0d23b92 -->

`src/http/health.rs`:

```rust
#[derive(Clone)]
pub struct Health {
    pool: PgPool,
    draining: Arc<AtomicBool>,
}

impl Health {
    pub fn new(pool: PgPool) -> Self {
        Health { pool, draining: Arc::default() }
    }

    /// From now on, `/readyz` says no: whoever sends us traffic stops, before we stop.
    pub fn start_draining(&self) {
        self.draining.store(true, Ordering::SeqCst);
    }
}

/// `GET /livez` and `GET /readyz`.
pub fn health_router<S: Clone + Send + Sync + 'static>(health: Health) -> Router<S> {
    Router::new().route("/livez", get(livez)).route("/readyz", get(readyz)).with_state(health)
}

/// Alive: the process is running and answering. Nothing else is checked, so a slow database never
/// makes Docker restart a program that's fine.
async fn livez() -> &'static str {
    "ok"
}

/// Ready: the database answers within a second, and we're not shutting down.
async fn readyz(State(health): State<Health>) -> (StatusCode, &'static str) {
    if health.draining.load(Ordering::SeqCst) {
        return (StatusCode::SERVICE_UNAVAILABLE, "stopping");
    }
    let ping = tokio::time::timeout(Duration::from_secs(1), sqlx::query("SELECT 1").execute(&health.pool)).await;
    match ping {
        Ok(Ok(_)) => (StatusCode::OK, "ready"),
        _ => (StatusCode::SERVICE_UNAVAILABLE, "the database isn't answering"),
    }
}
```

**Why two?** They lead to different actions. If **liveness** fails, Docker restarts the container. If **readiness** fails, the load balancer stops sending it requests, and nothing is restarted. Put the database check in liveness, and a database hiccup restarts every copy of the API at once, which makes the outage worse and fixes nothing. So `/livez` only proves the process answers, and `/readyz` checks what it needs to do useful work.

The database ping has a 1-second timeout of its own: a health check that hangs is worse than one that says no.

## Step 4: stopping politely
<!-- bite: 4e616167-397d-45c3-95de-3f9a62f1a9f7 -->

Two things changed in how every program stops.

**The right signal.** Until now, each program stopped on `tokio::signal::ctrl_c()`. That's SIGINT, what a terminal sends. `docker stop` sends **SIGTERM**. Outside Docker, SIGTERM's default is to kill the program at once, with no graceful shutdown. Inside Docker it's worse: the program is process 1 in its container, and Linux ignores any signal process 1 hasn't asked for. So SIGTERM did nothing, Docker waited its 10 seconds, and then killed the program hard, mid-request. `telemetry` now has:

```rust
/// Finishes when the program is asked to stop: Ctrl+C in a terminal, or SIGTERM, which is what
/// `docker stop`, Kubernetes and systemd send. Waiting only for Ctrl+C means a container ignores
/// the polite request, and is killed mid-request ten seconds later.
pub async fn shutdown_signal() {
    let ctrl_c = async { tokio::signal::ctrl_c().await.expect("can't listen for Ctrl+C") };
    #[cfg(unix)]
    let terminate = async {
        let mut term = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate()).expect("can't listen for SIGTERM");
        term.recv().await;
    };
    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();
    tokio::select! {
        _ = ctrl_c => tracing::info!(signal = "ctrl-c", "stopping"),
        _ = terminate => tracing::info!(signal = "SIGTERM", "stopping"),
    }
}
```

and all three programs use `telemetry::shutdown_signal()` everywhere they used `ctrl_c`. On the laptop, `kill -TERM` now gives:

```text
{"level":"INFO","fields":{"message":"stopping","signal":"SIGTERM"},"target":"telemetry"}
```

and the API is gone 54 ms later.

**Draining.** When it's told to stop, the API first turns `/readyz` to 503, keeps serving for `SHUTDOWN_DRAIN_SECONDS` while the load balancer (Caddy, in lesson 40) notices, and only then stops taking connections and lets the ones in progress finish. In `main.rs`:

```rust
    // Told to stop: say "not ready" first, keep answering for the drain time while the load balancer
    // notices, then stop taking connections and let the ones in progress finish.
    let drain = settings.shutdown_drain;
    let stopping = async move {
        telemetry::shutdown_signal().await;
        health.start_draining();
        tokio::time::sleep(drain).await;
    };
    axum::serve(listener, app).with_graceful_shutdown(stopping).await?;
```

Compose's `stop_grace_period: 20s` gives that time: 5 seconds of draining, then up to 15 for requests in progress.

## Step 5: a health check with no tools
<!-- bite: f1136de0-6cab-4170-a2fa-cbcf47d7493c -->

Lesson 40's image has no shell and no `curl` (on purpose: nothing for an attacker to use). So the program checks itself:

```rust
/// Asks this machine's API whether it's ready: exits 0 if so, 1 if not. For Docker's health check.
async fn healthcheck() -> Result<(), Box<dyn std::error::Error>> {
    let port = std::env::var("LISTEN_ADDR").ok().and_then(|a| a.rsplit(':').next().map(str::to_owned)).unwrap_or_else(|| "8080".into());
    let client = reqwest::Client::builder().timeout(Duration::from_secs(2)).build()?;
    let answer = client.get(format!("http://127.0.0.1:{port}/readyz")).send().await?;
    if !answer.status().is_success() {
        return Err(format!("not ready: {}", answer.status()).into());
    }
    Ok(())
}
```

and `main` begins:

```rust
// `mama-put healthcheck`: the image has no shell and no curl, so the program checks itself.
if std::env::args().nth(1).as_deref() == Some("healthcheck") {
    return healthcheck().await;
}
```

Returning `Err` from `main` exits with code 1, which Docker reads as "unhealthy". Compose runs it every 10 seconds: `test: ["CMD", "/usr/local/bin/mama-put", "healthcheck"]`.

## Step 6: should this have been Rust?
<!-- bite: d32ca842-e891-40d5-b758-274bc5b34184 -->

An honest look, after 39 lessons. What Rust bought Mama Put:

1. **Mistakes caught before running.** sqlx checks every query against the real schema while compiling; a workspace boundary is enforced by Cargo; `Send` errors catch locks held across awaits.
2. **Small, fast, cheap programs.** Each program is one file in a tiny image, starts in milliseconds, and uses little memory.
3. **No garbage-collector pauses**, so request times are steady.

What it cost:

1. **Compile times.** Minutes for a clean build here, and much more in Docker (lesson 40).
2. **A steeper path.** Lifetimes, `Send`, async traits, pinned futures: every lesson had a "The Rust in this lesson" list for a reason.
3. **A smaller library world** for some jobs: we wrote our own circuit breaker and our own JWKS cache, where Go had libraries.

For a food stall's API, Go or Node would have been fine, and quicker to write. Rust earns its place where steady speed, low cost per request, or strong guarantees really matter: payments at scale, a busy real-time service, anything that must not fall over. Choose it for those, not for fashion.

## The Rust in this lesson
<!-- bite: e9494330-cb69-47d5-ba08-d97a335f4b2b -->

1. **A generic struct over a closure**, `Reader<F: Fn(&str) -> Option<String>>`: the environment in `main`, a map in tests.
2. **`#[error("… {}", .0.len(), .0.join(…))]`**: a `thiserror` message built from the error's own fields.
3. **`T: FromStr` with `T::Err: Display`**: one `parse` for addresses, URLs and numbers.
4. **`#[cfg(unix)]`**: code compiled only on Unix-like systems, where SIGTERM exists.
5. **`tokio::signal::unix::signal(SignalKind::terminate())`**: a stream of SIGTERMs; `.recv().await` waits for the next.
6. **`Arc<AtomicBool>`** with `store` and `load`: a flag shared by tasks without a lock.
7. **`std::env::args().nth(1)`**: the first argument after the program's name.

## Your project so far
<!-- bite: d98a6ad7-b9fa-4c71-a63e-b41abdea9380 -->

```text
mama-put/
├── src/
│   ├── config.rs                 ← NEW: Settings, Reader, Secret, _FILE, tests
│   ├── http/health.rs            ← NEW: /livez, /readyz, draining
│   ├── lib.rs                    ← AppState.health; the health routes
│   └── main.rs                   ← Settings::from_env; LISTEN_ADDR; draining; `healthcheck`
├── src/bin/worker.rs             ← telemetry::shutdown_signal
├── notifications/src/main.rs     ← telemetry::shutdown_signal
├── telemetry/src/lib.rs          ← shutdown_signal: Ctrl+C or SIGTERM
└── tests/common/mod.rs           ← Health in the test app
```

## Common mistakes
<!-- bite: cd1061c7-ae85-4f1b-85d4-843d0f4c59ec -->

1. **Reading settings deep inside the code.** A missing one is found when that code first runs, maybe at 2am. Read them all at start.
2. **Stopping at the first bad setting.** Report them all.
3. **Secrets as plain strings.** One debug log leaks them. A `Secret` type.
4. **Secrets in environment variables in production.** Files, with `_FILE`.
5. **Listening on `127.0.0.1` in a container.** Nothing outside the container can reach it.
6. **One health check for everything.** A database blip restarts every copy. Liveness and readiness are different questions.
7. **Waiting only for Ctrl+C.** Containers get SIGTERM.
8. **Stopping without draining.** Requests sent in the last second fail.

## Check your understanding
<!-- bite: 58f517b8-5212-4da1-8ec1-9ee4d058822d -->

1. Why read every setting at start, and why report every problem together?
2. What does `Secret`'s `Debug` protect against, and what does `_FILE` protect against?
3. The database is unreachable for 30 seconds. What should `/livez` and `/readyz` say, and why?
4. What happened to the API in Docker when it only listened for Ctrl+C?
5. Why does the API keep serving for a few seconds after it's told to stop?

<details>
<summary>Answers, after your attempt</summary>

1. So a missing or bad setting is found the moment the program starts, not when some rarely-run code first needs it, and so all of them can be fixed in one go instead of one per restart.
2. `Debug` keeps secrets out of logs, even when a whole `Settings` is logged by mistake. `_FILE` keeps them out of the environment, where `docker inspect`, child processes and crash reports can see them.
3. `/livez` says ok (the process is fine; restarting it would help nothing); `/readyz` says 503 (it can't do useful work, so the load balancer should send requests elsewhere).
4. `docker stop` sent SIGTERM; as process 1, the API ignored it; Docker waited 10 seconds and then killed it hard, cutting off any requests in progress.
5. So the load balancer has time to see `/readyz` turn 503 and stop sending new requests; only then does the API stop taking connections, so nothing sent in that moment fails.

</details>

## Practice
<!-- bite: 5e764082-dcd7-4860-9a05-81457e0408d0 -->

1. Move the worker and notifications to their own `Settings`, with `_FILE` for their secrets.
2. Add a test that `/readyz` turns 503 after `start_draining`.
3. Start the API with half its settings missing, and read the error. Then do it again with `JWT_SECRET_FILE` pointing at a file that doesn't exist.

**Done when** the API reports every missing setting at once, prints secrets as `Secret(…)`, answers `/livez` and `/readyz`, drains before stopping, stops on SIGTERM, and `mama-put healthcheck` exits 0 when it's ready.

## Before moving on
<!-- bite: bb28aeb2-7b41-436a-b925-673f42e799b4 -->

Each program now reads its settings safely, says honestly whether it's ready, and stops politely. Next, they leave the laptop: each one packed into a small image, and the whole system, databases and all, started with one command.

## Related
<!-- bite: 9252b5b1-b4d0-468f-8012-a418a0c097fa -->

- [[backend/frameworks/axum/40-docker|Next: Docker]]
- [[backend/frameworks/net-http/28-production-config-and-docker|The same lesson in net/http]] — `errors.Join` for settings, and a `Secret` type with `LogValue`
- [[backend/frameworks/axum/14-security|Security]] — the settings this lesson now reads in one place

## About this lesson
<!-- bite: a61c97aa-a040-4c9e-9925-a9c676d78786 -->

**Level:** Advanced. Lesson 39 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later and Tokio 1. Covers reading every setting once with all problems reported together, testable settings through a lookup function, a `Secret` type whose `Debug` hides it, secrets from files with `_FILE`, listening on every interface in a container, liveness versus readiness, draining before stopping, SIGTERM and why process 1 ignores signals it didn't ask for, a self-checking `healthcheck` command for images with no shell, and whether Rust was the right choice. The code was compiled and the SIGTERM stop timed on a laptop; the remaining checks are listed to run later.
