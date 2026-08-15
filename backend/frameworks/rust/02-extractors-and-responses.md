# Extractors and Responses

**[Intermediate]** — Request parsing expressed entirely in the type system. This is what Rust web frameworks do that others structurally can't.

## Extractors

An extractor is a type that knows how to build itself from a request. Put it in a handler's parameter list and Axum runs it before your code.

```rust
async fn create_user(
    State(db): State<Pool>,                 // shared application state
    Path(id): Path<u64>,                    // /users/{id}, PARSED to u64
    Query(params): Query<Filters>,          // ?limit=10&sort=name, deserialised
    headers: HeaderMap,
    Json(payload): Json<CreateUser>,        // body — must be LAST
) -> Result<Json<User>, AppError> {
    ...
}
```

By the time the first line of your function runs, the path segment is a `u64`, the query string is a struct, and the body is validated JSON. **Anything that failed to parse never reached you** — it was rejected with an appropriate status automatically.

This is ["parse, don't validate"](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) enforced by the compiler: illegal states are unrepresentable in the handler body because the extractor couldn't produce them.

Compare with [[backend/frameworks/go/01-net-http-in-depth|Go]], where a handler starts with `r.PathValue("id")` returning a string you then parse, check, and error on by hand — three or four lines per parameter, repeated in every handler, each one a place to forget the check.

### The order rule

> **Body-consuming extractors (`Json`, `Form`, `String`, `Bytes`, `Request`) must be the LAST parameter.**

The body is an async stream that can only be consumed once. Extractors run left to right; anything after the one that consumed the body couldn't run. The type system enforces this via `FromRequest` (consumes) vs `FromRequestParts` (doesn't), and getting it wrong produces a confusing trait error — one of the cases where `#[axum::debug_handler]` earns its place.

### The built-in set

```rust
Path<T>            // path params — tuple or struct
Query<T>           // query string via serde
Json<T>            // JSON body
Form<T>            // urlencoded body
State<T>           // application state
Extension<T>       // per-request data inserted by middleware
HeaderMap          // all headers
TypedHeader<T>     // typed, from axum-extra: TypedHeader<Authorization<Bearer>>
Multipart          // file uploads
WebSocketUpgrade
ConnectInfo<SocketAddr>
Request            // the raw thing
String / Bytes     // raw body
Option<T>          // T, or None if extraction failed
Result<T, T::Rejection>   // T, or the rejection — for custom error handling
```

`Option<T>` and `Result<T, R>` are how you make an extractor non-fatal:

```rust
async fn handler(
    user: Option<AuthUser>,                  // None if no valid token, instead of 401
    Result(payload): Result<Json<Body>, JsonRejection>,   // handle the parse error yourself
) { ... }
```

## Custom extractors

Where this pays off. Authentication becomes a **type**:

```rust
struct AuthUser { id: u64, roles: Vec<Role> }

impl<S> FromRequestParts<S> for AuthUser
where S: Send + Sync
{
    type Rejection = AppError;

    async fn from_request_parts(parts: &mut Parts, _: &S) -> Result<Self, Self::Rejection> {
        let token = parts.headers
            .get(header::AUTHORIZATION)
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.strip_prefix("Bearer "))
            .ok_or(AppError::Unauthorized)?;

        let claims = verify_jwt(token).map_err(|_| AppError::Unauthorized)?;
        Ok(AuthUser { id: claims.sub, roles: claims.roles })
    }
}
```

```rust
async fn get_profile(user: AuthUser) -> Json<Profile> {
    // If this line runs, the user is authenticated. Guaranteed by the signature.
}
```

> **A handler taking `AuthUser` cannot be called unauthenticated.** Not "shouldn't" — *cannot*. There's no path into the function body that skips the extractor.

That's structurally different from a middleware that sets `req.user` and a handler that reads it — the middleware might not be registered on that route, and the handler still compiles. Here, forgetting the auth means the parameter isn't there, and then you have no user to use.

Push it further and the roles go into the type too:

```rust
struct AdminUser(AuthUser);      // extractor rejects unless roles contain Admin

async fn delete_everything(_: AdminUser) { }   // unreachable without admin
```

**This is the strongest argument for Rust on the web.** Authorisation bugs are a top-3 cause of real breaches, and they're usually "this endpoint forgot the check". Here the check is a function parameter, and forgetting it is a compile error.

## Responses

The mirror image: anything implementing `IntoResponse` can be returned.

```rust
async fn h1() -> &'static str                          // 200, text/plain
async fn h2() -> String
async fn h3() -> Json<User>                            // 200, application/json
async fn h4() -> StatusCode                            // just a status
async fn h5() -> (StatusCode, Json<User>)              // status + body
async fn h6() -> (StatusCode, HeaderMap, Json<User>)   // status + headers + body
async fn h7() -> Result<Json<User>, AppError>          // both arms must be IntoResponse
async fn h8() -> impl IntoResponse                     // when the type is awkward to name
async fn h9() -> Redirect
```

Tuples compose: `(StatusCode, impl IntoResponse)` prepends a status, `(HeaderMap, ...)` adds headers.

`impl IntoResponse` is convenient and costs you something — the concrete type is erased, so returning different response types from different branches still fails. `Response` (via `.into_response()`) is the fix:

```rust
async fn handler() -> Response {
    if cond { Json(user).into_response() } else { StatusCode::NOT_FOUND.into_response() }
}
```

## Errors as responses

The pattern that ties it together — implement `IntoResponse` on your error type once, then every handler can use `?`:

```rust
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("not found")]
    NotFound,
    #[error("invalid input: {0}")]
    Validation(String),
    #[error(transparent)]
    Internal(#[from] anyhow::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, msg) = match self {
            AppError::NotFound      => (StatusCode::NOT_FOUND, self.to_string()),
            AppError::Validation(_) => (StatusCode::BAD_REQUEST, self.to_string()),
            AppError::Internal(ref e) => {
                tracing::error!("internal error: {e:?}");             // log the detail
                (StatusCode::INTERNAL_SERVER_ERROR, "internal error".into())  // don't leak
            }
        };
        (status, Json(json!({ "error": msg }))).into_response()
    }
}
```

```rust
async fn get_user(State(db): State<Pool>, Path(id): Path<u64>) -> Result<Json<User>, AppError> {
    let user = db.find_user(id).await?          // sqlx::Error -> anyhow -> AppError
        .ok_or(AppError::NotFound)?;
    Ok(Json(user))
}
```

One place maps errors to statuses, and `?` handles propagation with automatic conversion via `From`. This is Spring's `@ControllerAdvice` and Nest's exception filters — **checked by the compiler, with no reflection**. → [[languages/03-rust/08-error-handling-in-practice|Error Handling in Practice]]

The two rules hold as everywhere: **log internal detail, return generic**.

## State

```rust
#[derive(Clone)]
struct AppState {
    db: PgPool,                     // already Arc internally, cheap to clone
    config: Arc<Config>,
}

let app = Router::new()
    .route("/users", get(list_users))
    .with_state(state);

async fn list_users(State(state): State<AppState>) -> Json<Vec<User>> {
    let users = sqlx::query_as!(User, "SELECT * FROM users").fetch_all(&state.db).await?;
    Json(users)
}
```

**State must be `Clone`** — it's cloned per request. Wrap expensive things in `Arc` so the clone is a refcount bump. `PgPool` is already internally `Arc`, so cloning it is cheap by design.

For sub-state, implement `FromRef`:

```rust
impl FromRef<AppState> for PgPool {
    fn from_ref(s: &AppState) -> PgPool { s.db.clone() }
}

async fn h(State(db): State<PgPool>) { }    // extract just the pool
```

That keeps handlers depending on the narrowest thing they need, which makes them easier to test.

**`State` over `Extension`.** `Extension<T>` is type-erased and fails at *runtime* if the layer wasn't added; `State` is checked at compile time. Extension is for things middleware inserts per request (like `AuthUser`), not for application state.

## Validation

Extractors give you type validation; business validation needs a crate:

```rust
#[derive(Deserialize, Validate)]
struct CreateUser {
    #[validate(email)]
    email: String,
    #[validate(range(min = 0, max = 130))]
    age: u8,
}

async fn create(Json(payload): Json<CreateUser>) -> Result<StatusCode, AppError> {
    payload.validate().map_err(|e| AppError::Validation(e.to_string()))?;
    ...
}
```

Or wrap it in a custom extractor so validation happens before the handler — the `axum-valid` crate does exactly that, and it's the more idiomatic shape:

```rust
async fn create(ValidatedJson(payload): ValidatedJson<CreateUser>) -> ... { }
```

---

## Related
- [[backend/frameworks/rust/01-axum-and-the-tower-stack|Axum and the Tower Stack]] — where extractors run
- [[backend/frameworks/rust/03-state-and-shared-data|State and Shared Data]] — `Arc`, and what happens under concurrency
- [[languages/03-rust/08-error-handling-in-practice|Rust: Error Handling]] — `thiserror` and `anyhow`
- [[backend/05-auth/02-authorization|Authorization]] — what the type system is enforcing here
- [[backend/frameworks/rust/README|Rust backends]]
