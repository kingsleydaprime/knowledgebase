---
id: 704e4f63-2487-4132-95b2-bb5c55407469
---

# Testing

**Testing a backend means writing code that checks the backend keeps its promises: that a rule holds, that a route refuses who it should, that a retried order happens once. You run it on every change, so a promise that breaks is caught by you, in seconds, not by a customer, at lunch.** In Rust, an Axum `Router` is a Tower service, so a test can send it a request and read the response with no network and no port. With sqlx giving each test its own database, a test can check the *whole app* exactly as a phone would use it, and still run in milliseconds.

## Before you start
<!-- bite: 9b377f7c-8cc3-4802-9262-ac2edc0d5397 -->

You should have:

1. Finished [[backend/frameworks/axum/15-idempotency|lesson 15]], so `cargo test` runs 25 tests and passes.
2. Read [[backend/07-practices/index|Practices]] if you want the general ideas about kinds of tests first. Not required.

After this lesson you will be able to:

1. Choose what to test at each level: a function, a service on a database, the whole app.
2. Write integration tests in `tests/`, using only the library's public API.
3. Build one `TestApp` that every whole-app test shares, with the clock under the test's control.
4. Send requests through the whole router with `oneshot`, and check problem responses in one line.
5. Test the permission table route by route, and race requests at once.
6. Make sure a test can fail, and say what makes a test worth trusting.

## What to install
<!-- bite: 5ab414e6-d9bd-48b9-94b5-5208c3c5bd33 -->

```bash
cargo add --dev futures
```

**`--dev`** adds it to `[dev-dependencies]`: crates used only by tests and examples, never compiled into the real program. **`futures`** gives `join_all`, to run many requests at once (step 6).

## Where we stopped
<!-- bite: 70c17658-2083-424d-96ec-b1493c9ec18f -->

There are 25 tests, and they grew one lesson at a time. Some test a function (`camel_case`, the policy), some a service on a real database (the last plate), two test the whole app with `oneshot` (the docs, the sunset). Each whole-app test built its own `AppState` by hand, and after lessons 12 to 15 that's twelve fields. Nothing checks, through the actual routes, that Ada gets a 403 on the kitchen's routes, that a reused refresh token ends her sessions, or that a retried order is the same order.

## The kid version
<!-- bite: a4198271-390b-4ada-81a5-d18e47c03782 -->

Mama doesn't taste every grain of rice. She tastes the stew at the end of cooking, because that's what customers eat. But she also checks the salt before it goes in, because a whole pot of salty stew is expensive to throw away.

Tests are the same. A few small checks of the ingredients (unit tests: is `camel_case` right? is the policy right?). And a good number of tastes of the finished stew (whole-app tests: does a customer ordering the last plate get it?). Not one or the other: both, each for what it's best at.

**Where the picture stops working.** Mama can only taste the stew once it's cooked, and then it's eaten. Our tests cook a fresh pot each time, in a fresh kitchen (a new database), in a few milliseconds, as many times as we like.

## Terms used in this lesson
<!-- bite: 28733a5f-e573-4b51-85fa-065cccca8ae8 -->

1. **Unit test**: This is a test of one small piece on its own, like a function. Fast and exact, but it can't show that the pieces work together.
2. **Integration test**: This is a test of pieces working together. In Rust, it also means a test in the `tests/` folder, which is compiled as a separate crate and sees only the library's public API.
3. **Whole-app test**: This is our name for a test that sends a real HTTP request through every layer of the router and checks the response, as a client would see it.
4. **Test harness**: This is the shared code tests use to set things up and check results, here `TestApp` and its helpers.
5. **Flaky test**: This is a test that sometimes passes and sometimes fails with no change to the code. A flaky test teaches people to ignore failures.
6. **Mutation check**: This is breaking the code on purpose to see that a test fails. A test that still passes was never testing anything.

## Step 1: which tests, how many
<!-- bite: c1b1799d-00a3-4d3d-9791-3a785ce0903c -->

Every level of test has a job it does best.

| Level | Example | Good at | Bad at |
|---|---|---|---|
| **Unit** | `ImageKind::sniff`, the policy, `camel_case` | exact cases, edge cases, speed | anything about how the pieces join |
| **Service on a database** | the last plate, refresh reuse | the SQL and the rules together | HTTP: status codes, headers, extractors |
| **Whole app** | "Ada gets 403 on `POST /v2/menu`" | what clients actually see | pinning down *which* piece broke |

The usual advice is a pyramid: many unit tests, fewer service tests, fewest whole-app tests, because whole-app tests used to be slow. In Axum they aren't. `oneshot` needs no network, and `#[sqlx::test]` makes a database in milliseconds. So Mama Put leans on whole-app tests for every promise a client depends on, and keeps unit tests for logic with many cases. Lesson 16's test run shows the cost: 16 whole-app tests, each with a fresh database, in about 20 seconds.

## Step 2: what `cargo test` gives you
<!-- bite: bfdc27b3-beaa-4ac4-ac00-fd66a92ec4b1 -->

You've used most of it already:

1. **`#[test]`** for plain functions, **`#[tokio::test]`** for async ones, **`#[sqlx::test]`** for async ones that get a fresh database.
2. **Tests in `src/`, in `#[cfg(test)] mod tests`**, can see private items. That's where unit tests go.
3. **Tests in `tests/`** are separate crates. Each file is its own test program, and it can only use what `lib.rs` makes `pub`, exactly like `main.rs`. That's where whole-app tests go: if the test can do it, a real program can too.
4. **Tests run at the same time**, on several threads. They must not share anything that changes: no shared database, no shared files, no fixed port. sqlx's fresh database per test is what makes that easy here.
5. **`cargo test name`** runs only tests whose names contain `name`; **`cargo test --test permissions`** runs one file in `tests/`.

## Step 3: one `TestApp` for every whole-app test
<!-- bite: 4f91d0b9-5d5a-4476-bb8c-456088d3288c -->

`tests/common/mod.rs` is the harness. It's `common/mod.rs`, not `common.rs`, on purpose: Cargo treats every `.rs` file directly in `tests/` as a test program, but a folder is just a module the test files can share with `mod common;`.

```rust
/// The real app, on the test's own database, with the clock stopped at noon in Lagos,
/// so the shop is open whatever time the tests run.
pub struct TestApp {
    pub router: Router,
    pub pool: PgPool,
}

/// How a `TestApp` differs from the real thing, when a test needs it to.
pub struct Settings {
    pub now: &'static str,
    pub logins_per_burst: u32,
}

impl Default for Settings {
    fn default() -> Self {
        Settings { now: "2026-11-21T11:00:00Z", logins_per_burst: 1000 } // 11:00 UTC is noon in Lagos
    }
}
```

`TestApp::with` builds the real `AppState`, field by field, exactly as `main` does, with three differences:

```rust
    pub fn with(pool: PgPool, settings: Settings) -> TestApp {
        let clock = Clock::fixed(settings.now.parse().unwrap());
        let keys = Keys::new(b"a test secret that is long enough!!").unwrap();
        let menu = MenuService::new(Arc::new(PgMenuStore::new(pool.clone())));
        let orders = OrderService::new(Arc::new(PgOrderStore::new(pool.clone())), menu.clone(), clock.clone()).unwrap();
        let state = AppState {
            menu,
            orders,
            staff_key: StaffKey::new(STAFF_KEY),
            v1: Deprecation {
                version: "v1",
                deprecated_at: "2026-12-01T00:00:00Z".parse().unwrap(),
                sunset_at: "2027-06-01T00:00:00Z".parse().unwrap(),
                guide: "https://mamaput.example/docs/moving-to-v2",
                clock: clock.clone(),
            },
            // Tokens are checked against the real clock, so they're signed with it too.
            auth: AuthService::new(PgAuthStore::new(pool.clone()), keys.clone(), Clock::system()),
            idempotency: Idempotency { store: IdempotencyStore::new(pool.clone()), keys: keys.clone() },
            keys,
            http: HttpConfig { allowed_origins: vec!["http://localhost:5173".parse().unwrap()], behind_proxy: false },
            photos: Photos::new(std::env::temp_dir()),
            login_limiter: RateLimiter::new(settings.logins_per_burst, Duration::from_secs(60), false),
        };
        TestApp { router: mama_put::app(state), pool }
    }
```

1. **The clock is stopped.** Without this, the order tests would pass at noon and fail after 9pm, when lesson 5's shop-hours rule kicks in. A test that depends on when you run it is flaky. Lesson 5 made the clock a dependency for exactly this moment. The default is noon in Lagos; a test that wants night says so (step 5).
2. **The auth clock is the real one.** jsonwebtoken checks a token's expiry against the computer's real time. A token signed "at" a stopped time in the past would already be expired. So the one place that signs tokens uses the real clock.
3. **The login limit is huge by default**, so a test that logs in ten users isn't rate-limited. The rate-limit test asks for a small one.

Every whole-app test starts with `TestApp::new(pool)`. When `AppState` gains a field in lesson 17, there's one place to add it.

### Talking to it

```rust
    pub fn get(&self, path: &str) -> Call<'_> {
        self.call(Method::GET, path)
    }
```

(and `post`, `patch` and `delete`.) A `Call` builds one request, a step at a time:

```rust
impl Call<'_> {
    pub fn json(mut self, body: Value) -> Self {
        self.request = self.request.header(header::CONTENT_TYPE, "application/json");
        self.body = Body::from(body.to_string());
        self
    }

    pub fn bearer(mut self, token: &str) -> Self {
        self.request = self.request.header(header::AUTHORIZATION, format!("Bearer {token}"));
        self
    }
```

```rust
    /// Sends it through the whole app: every layer, every extractor, no network.
    pub async fn send(self) -> Reply {
        let response = self.app.router.clone().oneshot(self.request.body(self.body).unwrap()).await.unwrap();
        let status = response.status();
        let headers = response.headers().clone();
        let bytes = to_bytes(response.into_body(), usize::MAX).await.unwrap();
        let body = serde_json::from_slice(&bytes).unwrap_or(Value::Null);
        Reply { status, headers, body }
    }
}
```

1. **Each method takes `mut self` and returns `Self`**: the **builder** pattern. `app.post("/v2/orders").bearer(&ada).json(...).send()` reads like a sentence.
2. **`Call<'_>`** holds a borrowed `&TestApp`; `'_` lets Rust work out how long.
3. **`self.app.router.clone().oneshot(...)`**: `oneshot` uses the router up, and cloning a `Router` is cheap (its routes are shared), so each call gets its own.
4. **`json!({...})`** from serde_json writes JSON inline in Rust, which makes tests read like the requests they send.

And the reply, with the check every error test needs:

```rust
    /// Checks this is a problem response with this status and code, the way lesson 7 promised.
    #[track_caller]
    pub fn assert_problem(&self, status: StatusCode, code: &str) {
        assert_eq!(self.status, status, "status, for {}", self.body);
        assert_eq!(self.headers[header::CONTENT_TYPE], "application/problem+json");
        assert_eq!(self.code(), code, "code, for {}", self.body);
        assert!(self.body["requestId"].as_str().is_some_and(|id| !id.is_empty()), "every problem has a request id");
    }
```

One line in a test now checks the status, the content type, the error code *and* that a request id is there. Every refusal in the app is held to lesson 7's shape. **`#[track_caller]`** makes a failure report the line in the *test* that called `assert_problem`, not a line inside the helper, so you see which check failed.

Two more helpers set up the world:

```rust
    /// Signs up, sets the role straight in the database, and logs in. Returns an access token.
    pub async fn user(&self, email: &str, role: &str) -> String {
        let made = self.post("/v2/auth/signup").json(json!({"email": email, "name": "Test", "password": PASSWORD})).send().await;
        assert_eq!(made.status, StatusCode::CREATED, "signing up {email}: {}", made.body);
        sqlx::query!("UPDATE users SET role = $2 WHERE email = $1", email, role).execute(&self.pool).await.unwrap();
        let login = self.post("/v2/auth/login").json(json!({"email": email, "password": PASSWORD})).send().await;
        login.body["data"]["accessToken"].as_str().unwrap().to_owned()
    }
```

`user` signs up *through the API* (so sign-up is tested on every run), but sets the role straight in the database, the same way the first admin is made in real life. `dish` inserts a dish with SQL, because how a dish was made isn't what most tests are about.

**Set up through the database, check through the API.** Setting up with SQL is fast and exact. Checking through the API means the test sees what a client sees.

## Step 4: the auth promises
<!-- bite: e96049bf-aa55-4429-8474-a1c6e996838e -->

`tests/auth.rs`:

```rust
#[sqlx::test]
async fn wrong_password_and_no_account_look_the_same(pool: PgPool) {
    let app = TestApp::new(pool);
    app.user("ada@example.com", "customer").await;

    let wrong = app.post("/v2/auth/login").json(json!({"email": "ada@example.com", "password": "not it at all"})).send().await;
    let nobody = app.post("/v2/auth/login").json(json!({"email": "bayo@example.com", "password": PASSWORD})).send().await;
    wrong.assert_problem(StatusCode::UNAUTHORIZED, "invalid-credentials");
    nobody.assert_problem(StatusCode::UNAUTHORIZED, "invalid-credentials");
    assert_eq!(wrong.body["detail"], nobody.body["detail"]);
}
```

That's lesson 12's "don't tell an attacker which emails exist", as a test: the two answers must be identical. The others check sign-up and `/me` (and that no `passwordHash` ever appears), the 401 for no token or a bad one, and the stolen refresh token:

```rust
    let adas_phone = app.post("/v2/auth/refresh").json(json!({"refreshToken": stolen})).send().await;
    assert_eq!(adas_phone.status, StatusCode::OK);
    let thief = app.post("/v2/auth/refresh").json(json!({"refreshToken": stolen})).send().await;
    thief.assert_problem(StatusCode::UNAUTHORIZED, "refresh-reused");

    let new_one = adas_phone.body["data"]["refreshToken"].as_str().unwrap();
    app.post("/v2/auth/refresh").json(json!({"refreshToken": new_one})).send().await.assert_problem(StatusCode::UNAUTHORIZED, "invalid-refresh");
```

Lesson 12 tested this in the service. This tests it as a phone and a thief would see it, through the routes, the JSON and the problem codes.

## Step 5: a table of permissions
<!-- bite: 1a634a53-4b78-4591-aaa2-92fc290a2694 -->

Lesson 13's policy has a unit test for every cell of the table. But the table is only half the story: a route could forget its `Can<...>`, or take the wrong one. So the table is checked again, through the real routes, in `tests/permissions.rs`:

```rust
    // (method, path, body, what each of nobody / customer / staff / admin gets)
    let routes = [
        ("POST", "/v2/menu".to_string(), json!({"name": "Akara", "price": {"amount": 50000, "currency": "NGN"}}), [401, 403, 201, 201]),
        ("PATCH", format!("/v2/menu/{dish}"), json!({"portionsLeft": 30}), [401, 403, 200, 200]),
        ("GET", "/v2/orders".to_string(), json!(null), [401, 200, 200, 200]),
        ("PATCH", "/v2/admin/users/1/role".to_string(), json!({"role": "customer"}), [401, 403, 403, 200]),
    ];
```

Each row is a route, and the four numbers are what nobody, a customer, staff and an admin should get. The loop sends every route as every role and compares:

```rust
            let got = call.send().await;
            assert_eq!(got.status.as_u16(), want, "{who:?} {method} {path}: {}", got.body);
```

Sixteen checks from four lines of table. Adding a route means adding a row, and a reviewer can read the row and ask Mama "is that right?".

**And it can fail.** I broke the policy on purpose, letting customers change the menu (`Action::MenuWrite => true`), and ran it:

```text
thread 'every_role_on_every_protected_route' panicked at tests/permissions.rs:58:13:
assertion `left == right` failed: Customer POST /v2/menu: {"data":{"id":2,"name":"Akara",...}}
  left: 201
 right: 403
```

It names the cell. That's a **mutation check**, and it's worth doing for every test that guards something important: break the code, watch the test fail, put the code back. A test you've never seen fail might not be testing what you think.

The same file checks ownership through the routes: Ada reads her order (200), Bayo gets a 404 problem for it, the cook gets 200, and Bayo's list is empty.

## Step 6: orders, and things at the same time
<!-- bite: fd6ca385-5959-4370-a7a7-e2bc71b50b65 -->

`tests/orders.rs` checks the price comes from the menu (and that sending `"total": 1` is refused), and the shop's hours, with a `TestApp` whose clock says night:

```rust
#[sqlx::test]
async fn the_shop_is_closed_at_night(pool: PgPool) {
    let app = TestApp::with(pool, Settings { now: "2026-11-21T21:30:00Z", ..Settings::default() }); // 22:30 in Lagos
    let ada = app.user("ada@example.com", "customer").await;
    let dish = app.dish("Jollof rice", 1500, 40).await;

    app.post("/v2/orders").bearer(&ada).json(json!({"dishId": dish, "quantity": 1})).send().await.assert_problem(StatusCode::CONFLICT, "shop-closed");
}
```

`..Settings::default()` keeps every other setting. This test passes at any hour of any day, because the time is part of the test.

The last plate, through the whole app, with ten customers at once:

```rust
#[sqlx::test]
async fn ten_customers_one_last_plate(pool: PgPool) {
    let app = TestApp::new(pool);
    let dish = app.dish("Jollof rice", 1500, 1).await;
    let mut customers = Vec::new();
    for i in 0..10 {
        customers.push(app.user(&format!("customer{i}@example.com"), "customer").await);
    }

    let orders = customers.iter().map(|token| app.post("/v2/orders").bearer(token).json(json!({"dishId": dish, "quantity": 1})).send());
    // All ten at once: `join_all` polls them together, so their requests really overlap.
    let replies = join_all(orders).await;
    let won = replies.iter().filter(|r| r.status == StatusCode::CREATED).count();
    assert_eq!(won, 1);
    assert!(replies.iter().filter(|r| r.status != StatusCode::CREATED).all(|r| r.code() == "not-enough-portions"));
}
```

**`join_all`** takes many futures and waits for all of them, driving them together. While one request waits for Postgres, the others make progress, so the ten guarded `UPDATE`s really do arrive together. (Lesson 8 used `tokio::spawn`; that needs each task to own its data, and `send` borrows the app. `join_all` runs them on the test's own task, so borrowing is fine.)

And lesson 15's promise:

```rust
    let first = order().send().await;
    let retry = order().send().await;
    assert_eq!(first.status, StatusCode::CREATED);
    assert_eq!(retry.status, StatusCode::CREATED);
    assert_eq!(retry.headers["idempotent-replayed"], "true");
    assert_eq!(first.body, retry.body);

    let left = sqlx::query_scalar!("SELECT portions_left FROM dishes WHERE id = $1", dish).fetch_one(&app.pool).await.unwrap();
    assert_eq!(left, 3, "two plates taken, once");
```

Checked from both sides: what the client sees (the same body, marked as a replay) and what really happened (two plates taken, not four).

## Step 7: security and versions
<!-- bite: c3c1458a-d1d8-438a-a5a3-d2c57e793f68 -->

`tests/security.rs` checks that the security headers are on every response, including a 404 from the fallback:

```rust
    for reply in [app.get("/v2/menu").send().await, app.get("/nowhere").send().await] {
        assert_eq!(reply.headers["x-content-type-options"], "nosniff");
        assert_eq!(reply.headers["x-frame-options"], "DENY");
        assert_eq!(reply.headers["content-security-policy"], "default-src 'none'; frame-ancestors 'none'");
    }
```

and that CORS answers our web app and not evil.example, and that the fourth login guess is a 429 with `Retry-After`, even when it claims a different `X-Forwarded-For`.

`tests/versions.rs` checks one dish's two shapes (₦200.50 is `200` in v1 and `20050` kobo in v2; v1 has `Sunset`, v2 doesn't), that v1 still takes orders without a login and still accepts the staff key while v2 refuses it, and that after the sunset every v1 path is gone:

```rust
#[sqlx::test]
async fn after_the_sunset_v1_is_gone(pool: PgPool) {
    let app = TestApp::with(pool, Settings { now: "2027-06-02T11:00:00Z", ..Settings::default() });
    app.get("/v1/menu").send().await.assert_problem(StatusCode::GONE, "version-retired");
    app.get("/menu").send().await.assert_problem(StatusCode::GONE, "version-retired");
    assert_eq!(app.get("/v2/menu").send().await.status, StatusCode::OK);
}
```

A test from June 2027, run today.

## Step 8: what makes tests trustworthy
<!-- bite: 57402183-0c6a-4a36-85d6-cd08ba0b4ec2 -->

```bash
cargo test
```

```text
     Running unittests src/lib.rs
test result: ok. 25 passed; 0 failed; ...
     Running tests/auth.rs
test result: ok. 4 passed; 0 failed; ...
     Running tests/orders.rs
test result: ok. 4 passed; 0 failed; ...
     Running tests/permissions.rs
test result: ok. 2 passed; 0 failed; ...
     Running tests/security.rs
test result: ok. 3 passed; 0 failed; ...
     Running tests/versions.rs
test result: ok. 3 passed; 0 failed; ...
```

41 tests. Five habits keep them worth running:

1. **Every test owns its world.** Its own database, its own app, its own clock. Nothing one test does can change another's result.
2. **Time is an input.** Never `Timestamp::now()` in a rule; always the clock. A test about 10pm says "it's 10pm".
3. **Test promises, not code.** "A customer gets 403 on `POST /v2/menu`" survives any rewrite of how the check is done. "`Can::from_request_parts` calls `allows`" breaks the moment you improve it.
4. **Watch each important test fail once.** The mutation check from step 5.
5. **A failure says what broke.** `"Customer POST /v2/menu"` in the assertion message, the body printed beside the status, `#[track_caller]` on helpers. You should rarely need a debugger to read a failing test.

And three things these tests don't do, on purpose: they don't check log lines (lesson 37 has better tools), they don't measure speed (lesson 37 again), and they don't hit real Paystack (lesson 17 fakes it, the way lesson 5 faked the clock). **`cargo llvm-cov`** (`cargo install cargo-llvm-cov`) shows which lines no test ever runs; it's a good way to find a rule nobody tests, and a bad target to chase to 100%.

## The Rust in this lesson
<!-- bite: 0b431ec9-3ef0-4742-a6b4-c63449868ad4 -->

1. **`[dev-dependencies]`**, with `cargo add --dev`.
2. **The `tests/` folder**: each file a separate crate using only the public API; **`tests/common/mod.rs`** for shared code, with `mod common;`.
3. **`#![allow(dead_code)]`** at the top of a module: each test file uses different helpers, and that's fine.
4. **The builder pattern**: methods taking `mut self` and returning `Self`.
5. **A struct borrowing another, `Call<'a>`**, written `Call<'_>` where Rust can work it out.
6. **`Default` for test settings, and `..Settings::default()`**.
7. **`serde_json::json!`** and indexing a `Value`, `body["data"]["email"]`.
8. **`#[track_caller]`**: report a failure at the caller's line.
9. **`futures::future::join_all`**: drive many futures together.
10. **`cargo test --test name`** and **`cargo test filter`**.

## Your project so far
<!-- bite: 8b19edba-de97-4079-8a59-fad69967afa0 -->

```text
mama-put/
├── Cargo.toml             ← [dev-dependencies] futures
└── tests/
    ├── common/
    │   └── mod.rs         ← TestApp (real AppState, fixed clock, Settings), Call, Reply, assert_problem, user, dish
    ├── auth.rs            ← 4: sign up and /me, identical login failures, 401s, stolen refresh token
    ├── permissions.rs     ← 2: the role table on every protected route; someone else's order is 404
    ├── orders.rs          ← 4: priced by the menu, closed at night, ten customers one plate, a retry is the same order
    ├── security.rs        ← 3: headers on everything, CORS, the login limit
    └── versions.rs        ← 3: two shapes, v1's orders and staff key, v1 gone after the sunset
```

## Common mistakes
<!-- bite: 1ec24bd5-0c95-4305-b2df-61871ad6d328 -->

1. **Tests that share a database.** They pass alone and fail together. One database per test.
2. **Tests that read the real clock.** They pass by day and fail by night. Make time an input.
3. **Only unit tests.** Every piece works, and the route forgot its `Can<...>`. Test promises through the routes.
4. **Only whole-app tests.** A table of 40 edge cases for `camel_case` is clearer, and faster, as a unit test.
5. **Building `AppState` by hand in every test.** Twelve fields, copied, drifting. One `TestApp`.
6. **Setting up through the API when it isn't the point.** Slow, and a sign-up bug fails every test at once. Set up with SQL; check with the API.
7. **Never seeing a test fail.** It might be checking nothing. Break the code once.
8. **Assertion messages that say nothing.** `assertion failed` at line 58 of a loop. Say which case.

## Check your understanding
<!-- bite: 30ffb9b7-507e-4f48-96e7-cdbe19856114 -->

1. What is each level of test (unit, service on a database, whole app) best at, and why can Mama Put lean on whole-app tests more than the usual pyramid suggests?
2. What's different about a test in `tests/` compared with one in `src/`?
3. Why does `TestApp` stop the clock at noon in Lagos, but sign tokens with the real clock?
4. What does `assert_problem` check, and what does `#[track_caller]` change about a failure?
5. Why set up dishes and roles with SQL, but check results through the API?
6. Lesson 13 already tests every cell of the policy. Why test the table again through the routes?
7. Why does the last-plate test use `join_all`, and why not `tokio::spawn` like lesson 8?
8. What is a mutation check, and what did the one in this lesson show?

<details>
<summary>Answers, after your attempt</summary>

1. Unit tests are best at exact and edge cases of one piece, fast; service tests at the rules and the SQL together; whole-app tests at what clients actually see, through every layer. Mama Put can lean on whole-app tests because `oneshot` needs no network and `#[sqlx::test]` makes a database in milliseconds, so they're cheap.
2. A test in `tests/` is compiled as a separate crate and can only use what `lib.rs` makes public, like `main.rs`. A test in `src/` is a child module and can see private items. So `tests/` proves things through the public front door.
3. The clock is stopped so the shop-hours rule gives the same answer whenever the tests run; a test about the time must choose the time. Tokens use the real clock because jsonwebtoken checks expiry against the computer's real time, and a token signed at a stopped time in the past would already be expired.
4. The status, the `application/problem+json` content type, the error code, and that a request id is present: lesson 7's whole promise about errors, in one line. `#[track_caller]` makes a failure report the line in the test that called it, not a line inside the helper.
5. Setting up with SQL is fast, exact, and doesn't depend on other routes working, so a bug in one route doesn't fail every test. Checking through the API means the test sees exactly what a client sees.
6. Because the unit test only proves `allows` is right. A route could still forget its `Can<...>`, take the wrong permission, or a layer could get in the way. The route table proves each real route enforces the policy.
7. To make the ten requests really overlap: `join_all` drives them together, so while one waits for Postgres the others proceed. `tokio::spawn` needs each task to own what it uses, and `send` borrows the `TestApp`; `join_all` runs them on the test's own task, where borrowing is fine.
8. Breaking the code on purpose to check that a test fails. Letting customers change the menu made the permissions test fail, naming `Customer POST /v2/menu`, 201 instead of 403, which proves that test really guards that rule.

</details>

## Practice
<!-- bite: 45c8f215-e1cb-4a18-83b0-2d7f6a2b4ed4 -->

1. Move lesson 11's docs test and lesson 10's sunset test into `tests/`, using `TestApp`, and delete their hand-built `AppState`s.
2. Add rows to the permissions table for `PATCH /v2/orders/{id}/status` and `DELETE /v2/menu/{id}`. What does a customer get for each?
3. Write a whole-app test for photo uploads: a real PNG gets a `photoUrl`, and HTML named `.jpg` gets `not-an-image`. (Build the multipart body by hand, or add `reqwest`'s `multipart` as a dev-dependency.)
4. Do a mutation check on lesson 15: remove the `ON CONFLICT` from the order `INSERT`. Which tests fail, and which one should?
5. Run `cargo llvm-cov --html` and find one rule no test runs. Write the test.

**Done when** every whole-app test uses one `TestApp` with a stopped clock and its own database, the auth, permissions, orders, security and versions promises from lessons 10 to 15 are each tested through the real routes, the permission table covers every protected route and role, you've watched at least one important test fail on purpose, and `cargo test` runs 41 tests and passes.

## Before moving on
<!-- bite: 69900f28-dd70-41d8-a74b-67d5e3a134cf -->

That's Part 3 done. Mama Put knows who's calling and what they may do, defends itself, makes retries safe, and now *proves* all of it on every change: 41 tests, each in its own fresh world, most of them talking to the app exactly as a phone would.

Next is Part 4, what real products need, starting with the money. Next lesson: payments and webhooks, with Paystack checkout in kobo, receiving and verifying Paystack's webhooks, and sending signed webhooks of our own. And now that there's a harness, every new promise comes with its test.

## Related
<!-- bite: 8023687a-96ca-417b-b4c5-1678305d05f0 -->

- [[backend/frameworks/axum/17-payments-and-webhooks|Next: Payments and Webhooks]]
- [[backend/frameworks/net-http/16-testing|The same lesson in net/http]] — `httptest`, a fake store, and integration tests on a real database
- [[backend/07-practices/index|Practices]] — testing, and other habits of working software
- [[backend/frameworks/axum/05-state-and-dependency-injection|State and Dependency Injection]] — why the clock could be stopped at all

## About this lesson
<!-- bite: e28cf5ef-5430-407f-acf2-eb331d09b752 -->

**Level:** Intermediate → Advanced. Lesson 16 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, sqlx 0.9 and futures 0.3. Covers what unit, service and whole-app tests are each best at and why `oneshot` and `#[sqlx::test]` make whole-app tests cheap, the `tests/` folder and `tests/common/mod.rs`, a `TestApp` building the real `AppState` with a stopped clock and adjustable `Settings`, a builder for requests and an `assert_problem` with `#[track_caller]`, setting up with SQL and checking through the API, auth promises through the routes, a role-by-route permission table, ten concurrent orders with `join_all`, idempotency checked from both sides, security headers, CORS and the rate limit, version shapes and the sunset with a future clock, a mutation check, and what makes tests trustworthy.
