---
id: cf2584ff-1436-470f-8fad-51ebbb38dad0
---

# Authentication

**Authentication means finding out who is making a request: a customer proves they're Ada, once, with a password, and from then on every request carries proof that it's still Ada.** In Rust and Axum, the proof is checked by an **extractor**, `AuthUser`. A handler that takes an `AuthUser` can't run for anyone who isn't logged in, because the request is refused before the handler starts. Forgetting the check isn't a bug you can write: the compiler won't build a handler that uses the user without asking for one.

## Before you start
<!-- bite: 581f263f-11cb-4736-9819-6535dc1041c4 -->

You should have:

1. Finished [[backend/frameworks/axum/11-api-docs|lesson 11]], so v2 is documented and the docs test passes.
2. Read [[backend/05-auth/index|Authentication and Authorization]] if you want the ideas first: hashing, sessions and tokens. Not required.

After this lesson you will be able to:

1. Store passwords with argon2id, off the async threads, so even a stolen database gives away no passwords.
2. Choose between sessions and tokens, and say what each costs.
3. Sign and check short-lived JWTs, closing the holes they're known for.
4. Build sign-up, log-in, refresh and log-out, with refresh tokens that work once and catch thieves.
5. Write an `AuthUser` extractor, and make "v2 needs a login to order" a type.

## What to install
<!-- bite: f14772a6-529a-4314-b991-f10dc330db1b -->

```bash
cargo add argon2 sha2 hex getrandom
cargo add jsonwebtoken --no-default-features --features rust_crypto
```

1. **`argon2`** hashes passwords with argon2id, the algorithm OWASP recommends, and writes the result in the standard text format.
2. **`jsonwebtoken`** signs and checks JWTs. Version 12 makes you choose the cryptography underneath it; `rust_crypto` is the pure-Rust choice.
3. **`sha2`** and **`hex`** hash refresh tokens before they're stored.
4. **`getrandom`** asks the operating system for random bytes, for refresh tokens.

And one more secret, in `.env`:

```text
JWT_SECRET=local-only-secret-change-me-0123456789abcdef
```

In production it must be at least 32 truly random bytes: `openssl rand -base64 32` makes one.

## Where we stopped
<!-- bite: 6ccd8afe-028b-4b16-8d3c-d61d327e3984 -->

There are no customers, only requests. The kitchen shares one staff key between everyone. And anyone can order anything, and read any order by guessing its number. A phone app can't show "my orders", because the API has no idea whose they are.

## The kid version
<!-- bite: 1717e63e-18de-4cfd-af9b-e1d1e2a66dcc -->

At a party, you show your ticket at the gate once. The bouncer checks it properly, against the guest list, and puts a wristband on you. From then on, every bar just glances at the wristband. Nobody phones the gate.

The wristband expires at midnight. If you're staying all weekend, you also get a card. At midnight you take the card back to the gate, and they swap it for a new card and a new wristband. Each card works once.

The wristband is an **access token**. The card is a **refresh token**.

**Where the picture stops working.** A wristband can be copied. So ours lasts 15 minutes, not until midnight, and a card that comes back to the gate a second time means somebody copied it, so the gate cancels every card that person has.

## Terms used in this lesson
<!-- bite: d3d1a242-6a60-4766-bf91-fe9419276f5f -->

1. **Authentication**: This is finding out who someone is. **Authorization** (lesson 13) is deciding what they may do.
2. **Password hash**: This is the result of putting a password through a deliberately slow, one-way function. It can check a password, but can't be turned back into one.
3. **Salt**: This is random bytes mixed into each password before hashing, so the same password hashes differently for every user.
4. **argon2id**: This is the password hash OWASP recommends, made slow and memory-hungry on purpose.
5. **Session**: This is a random id stored on the server, sent by the client on every request. The server looks it up.
6. **JWT**: This stands for **JSON Web Token**. It carries facts ("user 42, customer, until 3:15pm") and a signature, so the server can check it without looking anything up.
7. **Access token**: This is a short-lived token sent with every request, in the `Authorization: Bearer ...` header.
8. **Refresh token**: This is a long-lived, single-use token used only to get a new access token.
9. **Identity**: This is our name for "who is calling": a user id and a role, read from the access token.

## Step 1: never store passwords
<!-- bite: a343e8e9-45d7-4d18-bd01-80c363efef9c -->

If the `users` table ever leaks (a backup left public, an SQL injection somewhere, a careless employee), every password in it leaks too. And people reuse passwords, so Ada's Mama Put password is probably her email password.

So we store a **hash**. And not just any hash: a *slow* one, made for passwords. Fast hashes like SHA-256 are built to run billions of times a second, which is exactly what an attacker guessing passwords wants. **argon2id** is deliberately slow and memory-hungry, so each guess costs real time and real memory, and it mixes in a random salt, so a table of pre-computed hashes is useless.

`src/auth/password.rs`:

```rust
//! Passwords are never stored. A slow, salted hash of each one is.

use std::sync::LazyLock;

use argon2::{
    Argon2,
    password_hash::{PasswordHasher, PasswordVerifier, phc::PasswordHash},
};

/// argon2id with OWASP's settings (19 MiB, 2 passes, 1 lane), which are the crate's defaults.
/// Returns the PHC string: `$argon2id$v=19$m=19456,t=2,p=1$<salt>$<hash>`.
pub async fn hash(password: String) -> Result<String, argon2::password_hash::Error> {
    // Deliberately slow work: off the async threads, so other requests keep moving.
    tokio::task::spawn_blocking(move || Ok(Argon2::default().hash_password(password.as_bytes())?.to_string()))
        .await
        .expect("the hashing task doesn't panic")
}

/// True if `password` matches the stored hash. Uses the settings stored inside the hash.
pub async fn verify(password: String, stored: String) -> bool {
    tokio::task::spawn_blocking(move || {
        PasswordHash::new(&stored).is_ok_and(|parsed| Argon2::default().verify_password(password.as_bytes(), &parsed).is_ok())
    })
    .await
    .expect("the checking task doesn't panic")
}
```

1. **`Argon2::default()`** is argon2id with 19 MiB of memory, 2 passes and 1 lane: exactly OWASP's recommended minimum. The crate chose well, so we don't override it.
2. **`hash_password`** makes a fresh random salt, hashes, and gives back a **PHC string**: one line of text with the algorithm, its version, the settings, the salt and the result. `verify_password` reads the settings back out of that string, so if we raise the memory one day, old hashes still say what *they* were made with.
3. **`spawn_blocking`** is the most important line here. Hashing takes tens of milliseconds of solid CPU work, and an `async fn` that does solid work holds a Tokio worker thread the whole time. Tokio has one worker per CPU core; a few logins at once and nothing else gets served. `spawn_blocking` runs the closure on Tokio's separate pool of threads made for blocking work, and the request `.await`s it. (The old [[backend/frameworks/axum/04-async-pitfalls|Async Pitfalls]] note is all about this.)
4. **`move ||`** gives the closure its own copy of `password`: the blocking thread may outlive the borrow, so it must own what it uses. That's why `hash` takes a `String`, not a `&str`.

From a real sign-up, the start of what Postgres stores:

```text
$argon2id$v=19$m=19456,t=2,p=1$0...
```

**Why only 19 MiB?** Because it's *per login, at the same time*. Twenty logins at once at 64 MiB each is 1.3 GB, the whole of a small server. 19 MiB still makes guessing very expensive, and lesson 14 rate-limits the login route, so nobody can make us hash all day.

### Checking a missing account takes as long as a wrong password

At the bottom of `password.rs`:

```rust
/// A real hash of nothing in particular, checked when the email isn't found,
/// so "no such account" takes as long as "wrong password" and can't be told apart by timing.
pub static DUMMY_HASH: LazyLock<String> = LazyLock::new(|| {
    Argon2::default().hash_password(b"not anyone's password").expect("hashing a constant works").to_string()
});
```

If a missing email answered instantly and a wrong password took 50 ms, an attacker could find out which emails have accounts, just by timing. So a missing account checks this dummy hash anyway. **`LazyLock`** makes it once, the first time it's needed, and keeps it.

Two tests, at the bottom of the file:

```rust
    #[tokio::test]
    async fn a_hash_checks_its_own_password_and_no_other() {
        let stored = hash("correct horse battery staple".into()).await.unwrap();
        assert!(stored.starts_with("$argon2id$v=19$m=19456,t=2,p=1$"));
        assert!(verify("correct horse battery staple".into(), stored.clone()).await);
        assert!(!verify("correct horse battery stapler".into(), stored).await);
    }

    #[tokio::test]
    async fn the_same_password_hashes_differently_each_time() {
        let a = hash("jollof".into()).await.unwrap();
        let b = hash("jollof".into()).await.unwrap();
        assert_ne!(a, b); // a fresh random salt every time
    }
```

## Step 2: sessions or tokens?
<!-- bite: 25a87da8-cb3e-45a1-bca7-a81a1cbd4fe2 -->

**Sessions** store a random id in a table; the client sends it on every request, and the server looks it up. Logging out deletes the row, and it's gone at once. The cost: a database trip on every request, and every service that wants to know who's calling has to reach that table.

**Tokens** (JWTs) carry the facts and a signature. Any service with the key can check one with no lookup. The cost: you can't take one back. A stolen token works until it expires.

Mama Put's main client is a phone app, and lesson 29 adds a second service. So we use tokens, and fix their weakness by keeping them **short-lived**: an access token lasts 15 minutes. To avoid logging in every 15 minutes, the app also gets a **refresh token**, which we *do* store, so we can cancel it. That pair, a short JWT plus a stored, cancellable refresh token, gives most of the benefits of both.

## Step 3: the tables
<!-- bite: c9c64c7a-c8fd-4c05-8767-6ce5c90f3bdf -->

`migrations/0005_users_and_tokens.sql`:

```sql
CREATE TABLE users (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email         text NOT NULL,
  name          text NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
  password_hash text NOT NULL,
  role          text NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'staff', 'admin')),
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- Ada@Example.com and ada@example.com are the same person.
CREATE UNIQUE INDEX users_email_idx ON users (lower(email));

CREATE TABLE refresh_tokens (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     bigint NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  token_hash  text NOT NULL UNIQUE,   -- a hash: a leaked table holds no usable tokens
  expires_at  timestamptz NOT NULL,
  used_at     timestamptz,
  revoked_at  timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX refresh_tokens_user_id_idx ON refresh_tokens (user_id);

-- Orders belong to whoever placed them. Old orders, and v1's, have no customer.
ALTER TABLE orders ADD COLUMN customer_id bigint REFERENCES users (id);
CREATE INDEX orders_customer_id_idx ON orders (customer_id);
```

The same tables as the Go and Express versions. The unique index is on `lower(email)`, so the same email in different capitals can't be two accounts. `refresh_tokens` stores a **hash** of each token, like passwords: a leaked table holds nothing usable. `orders.customer_id` can be `NULL`, for old orders and for v1's (step 8).

`sqlx migrate run`.

## Step 4: who is calling
<!-- bite: d01b70b1-0254-4d86-9f40-a7f8a4294757 -->

A new feature module, `src/auth/`, with `pub mod auth;` in `lib.rs`. `src/auth/model.rs`:

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize, sqlx::Type, ToSchema)]
#[serde(rename_all = "lowercase")]
#[sqlx(type_name = "text", rename_all = "lowercase")]
pub enum Role {
    Customer,
    Staff,
    Admin,
}

/// Who is calling: worked out from the access token on every request, without a database trip.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Identity {
    pub user_id: i64,
    pub role: Role,
}

#[derive(Clone, Debug)]
pub struct User {
    pub id: i64,
    pub email: String,
    pub name: String,
    pub role: Role,
}
```

`User` has no `password_hash`. The store returns the hash only to the one function that checks passwords, wrapped in a type of its own (step 6), so it can't end up in a response by accident.

## Step 5: signing and checking access tokens
<!-- bite: c2e28817-c9f8-4639-aed4-48bf81db8123 -->

`src/auth/tokens.rs`:

```rust
/// How long an access token works. Short, because it can't be cancelled.
pub const ACCESS_SECONDS: i64 = 15 * 60;

/// What's inside an access token. Anyone can read it (it's only signed, not secret); nobody can change it.
#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    /// The user's id, as text: JWT's "subject".
    sub: String,
    role: Role,
    iat: i64,
    exp: i64,
}

/// The secret that signs access tokens. Cheap to clone; never printed.
#[derive(Clone)]
pub struct Keys(Arc<KeysInner>);

struct KeysInner {
    encoding: EncodingKey,
    decoding: DecodingKey,
    validation: Validation,
}

impl Keys {
    pub fn new(secret: &[u8]) -> Result<Self, jsonwebtoken::errors::Error> {
        // Only HS256 is accepted. A token that says it uses another algorithm (or "none") is refused.
        let mut validation = Validation::new(Algorithm::HS256);
        validation.set_required_spec_claims(&["exp", "sub"]);
        Ok(Keys(Arc::new(KeysInner {
            encoding: EncodingKey::from_secret(secret)?,
            decoding: DecodingKey::from_secret(secret)?,
            validation,
        })))
    }
```

A JWT is three pieces of base64 joined by dots: a header (`{"alg":"HS256"}`), the claims, and a signature over both. **HS256** signs with a shared secret: whoever has `JWT_SECRET` can make tokens and check them.

1. **The claims are readable by anyone.** Paste a token into jwt.io and you'll see `{"sub":"1","role":"customer",...}`. Never put anything secret in a JWT. What the signature gives is that nobody can *change* it.
2. **`Validation::new(Algorithm::HS256)`** pins the algorithm. The classic JWT attack is a token whose header says `"alg": "none"` (no signature at all) or a different algorithm, hoping the server believes the header. Ours only accepts HS256, whatever the token says.
3. **`set_required_spec_claims(&["exp", "sub"])`**: a token without an expiry or a subject is refused. `exp` is checked against the clock automatically (with a minute of leeway for clocks that disagree slightly).
4. **`Keys` wraps an `Arc`**, like `StaffKey`, and has no `Debug`, so it can't be printed into a log.

Issuing and checking:

```rust
    pub fn issue_access(&self, who: Identity, now: Timestamp) -> String {
        let claims = Claims {
            sub: who.user_id.to_string(),
            role: who.role,
            iat: now.as_second(),
            exp: now.as_second() + ACCESS_SECONDS,
        };
        encode(&Header::new(Algorithm::HS256), &claims, &self.0.encoding).expect("signing our own claims works")
    }

    /// The identity in a token, if the signature is ours and it hasn't expired.
    pub fn check_access(&self, token: &str) -> Option<Identity> {
        let data = decode::<Claims>(token, &self.0.decoding, &self.0.validation).ok()?;
        Some(Identity { user_id: data.claims.sub.parse().ok()?, role: data.claims.role })
    }
```

`check_access` returns an `Option` on purpose: a bad signature, an expired token and nonsense are all "no", and the caller shouldn't treat them differently. `from_env` reads `JWT_SECRET` and refuses anything shorter than 32 bytes.

Four tests in the same file make the guarantees concrete:

```rust
    #[test]
    fn a_changed_token_is_refused() {
        let token = keys().issue_access(Identity { user_id: 42, role: Role::Customer }, Timestamp::now());
        // Swap the payload for one that says "admin", keeping the old signature.
        let parts: Vec<&str> = token.split('.').collect();
        let admin = URL_SAFE_NO_PAD.encode(br#"{"sub":"42","role":"admin","iat":0,"exp":9999999999}"#);
        let forged = format!("{}.{}.{}", parts[0], admin, parts[2]);
        assert_eq!(keys().check_access(&forged), None);
    }
```

That's the attack a customer would actually try: make themselves admin. The signature no longer matches the claims, so it's refused. The others check a round trip, an expired token, and a token signed by somebody else's secret. (`br#"..."#` is a raw byte string: bytes, with quotes inside, no escaping.)

### Refresh tokens

```rust
/// A new refresh token: 32 random bytes, as URL-safe text. Only its hash is stored.
pub fn new_refresh_token() -> String {
    let mut bytes = [0u8; 32];
    getrandom::fill(&mut bytes).expect("the operating system gives random bytes");
    URL_SAFE_NO_PAD.encode(bytes)
}

/// What's stored for a refresh token. SHA-256 is enough here: the token is random, so there's nothing to guess.
pub fn hash_refresh_token(token: &str) -> String {
    hex::encode(Sha256::digest(token.as_bytes()))
}
```

Refresh tokens aren't JWTs. They're just 32 random bytes, a number too big to guess, and the server looks them up. Why SHA-256 here, when lesson 1 said fast hashes are bad for passwords? Because a password is something a person chose, from a small space of likely guesses. A refresh token is 256 random bits: nobody can guess it, however fast the hash, so the hash only has to stop a leaked table being used directly.

## Step 6: the store and the service
<!-- bite: 155324db-ac28-4fb5-9d68-9b25cf999352 -->

`src/auth/store.rs` has no trait, unlike the menu's and orders' stores:

```rust
/// Users and refresh tokens in PostgreSQL. No trait: there's no second kind of store in sight,
/// and `#[sqlx::test]` tests this one for real. Add the trait the day a second one appears.
#[derive(Clone)]
pub struct PgAuthStore {
    pool: PgPool,
}

/// A user, with the hash only the login check may see.
pub struct UserWithHash {
    pub user: User,
    pub password_hash: String,
}
```

Lesson 5 put stores behind traits so they could be swapped. Lesson 8 then showed tests can use a real database just as well. For a new store with one implementation, a trait would be a promise nobody needs yet. That's a judgement call, and saying it out loud in the code is better than leaving the reader to wonder.

The one query worth slowing down for:

```rust
    /// Marks a refresh token used, if it's still good, and says whose it was. One statement, so two
    /// requests with the same token can't both succeed: the second finds `used_at` already set.
    pub async fn use_refresh(&self, token_hash: &str) -> Result<Option<i64>, StoreError> {
        let user_id = sqlx::query_scalar!(
            "UPDATE refresh_tokens SET used_at = now()
             WHERE token_hash = $1 AND used_at IS NULL AND revoked_at IS NULL AND expires_at > now()
             RETURNING user_id",
            token_hash
        )
        .fetch_optional(&self.pool)
        .await?;
        Ok(user_id)
    }
```

It's lesson 8's last plate again: look and take in one guarded statement. And `now() + interval '30 days'` in `add_refresh` lets Postgres do the date maths, so Rust never handles a `timestamptz` (sqlx has no jiff support, lesson 8).

The rest of the store is `create_user`, `find_by_email` (with `lower(email) = lower($1)`, to match the index), `find`, `add_refresh`, `owner_of_used`, `revoke` and `revoke_all`. `StoreError` gains `is_unique_violation()`, beside lesson 8's foreign-key check, for "that email is taken".

### The service

`src/auth/service.rs`:

```rust
#[derive(Debug, thiserror::Error)]
pub enum AuthError {
    #[error("there's already an account with that email")]
    EmailTaken,
    #[error("that email and password don't match an account")]
    InvalidCredentials,
    #[error("that refresh token isn't valid; log in again")]
    InvalidRefresh,
    #[error("that refresh token was already used, so every session for this account has been ended; log in again")]
    RefreshReused,
    #[error("there's no account {0}")]
    NoSuchUser(i64),
    #[error("password hashing failed: {0}")]
    Hashing(String),
    #[error(transparent)]
    Store(#[from] StoreError),
}
```

**`InvalidCredentials` doesn't say which was wrong.** "No such email" would tell an attacker which emails have accounts. One message for both, and the same time for both.

```rust
    pub async fn log_in(&self, email: &str, password: String) -> Result<Tokens, AuthError> {
        let Some(found) = self.store.find_by_email(email.trim()).await? else {
            // Check a dummy hash anyway, so a missing account takes as long as a wrong password.
            password::verify(password, password::DUMMY_HASH.clone()).await;
            return Err(AuthError::InvalidCredentials);
        };
        if !password::verify(password, found.password_hash).await {
            return Err(AuthError::InvalidCredentials);
        }
        self.issue(Identity { user_id: found.user.id, role: found.user.role }).await
    }

    /// Swaps a refresh token for a new pair. Each refresh token works once.
    pub async fn refresh(&self, refresh_token: &str) -> Result<Tokens, AuthError> {
        let hash = tokens::hash_refresh_token(refresh_token);
        if let Some(user_id) = self.store.use_refresh(&hash).await? {
            let user = self.store.find(user_id).await?.ok_or(AuthError::NoSuchUser(user_id))?;
            return self.issue(Identity { user_id, role: user.role }).await;
        }
        // Not usable. If it was used before, someone has a copy: end every session for that account.
        if let Some(user_id) = self.store.owner_of_used(&hash).await? {
            tracing::warn!(user_id, "a used refresh token came back; revoking every session");
            self.store.revoke_all(user_id).await?;
            return Err(AuthError::RefreshReused);
        }
        Err(AuthError::InvalidRefresh)
    }
```

**Refresh tokens rotate.** Every refresh uses up the old token and gives a new one. So if a thief copies Ada's refresh token, one of two things happens: the thief uses it first, and then Ada's phone sends it and finds it used; or Ada's phone uses it first, and then the thief does. Either way, *a used token comes back*. We can't tell which of them is the thief, so we end every session for the account. Ada logs in again; the thief has nothing. The role is read fresh from the database on every refresh, so a promotion (lesson 13) reaches the token within 15 minutes.

`issue` makes a refresh token, stores its hash, and signs an access token with the clock from lesson 5. `sign_up` hashes the password and turns a unique violation into `EmailTaken`.

Two `#[sqlx::test]`s check the flow end to end, including the theft:

```rust
    #[sqlx::test]
    async fn a_refresh_token_works_once_and_a_reused_one_ends_everything(pool: PgPool) {
        let auth = service(pool);
        auth.sign_up("ada@example.com", "Ada", "correct horse battery".into()).await.unwrap();
        let first = auth.log_in("ada@example.com", "correct horse battery".into()).await.unwrap();

        let second = auth.refresh(&first.refresh).await.unwrap(); // Ada's phone refreshes
        // A thief replays the old token: refused, and Ada's new token stops working too.
        assert!(matches!(auth.refresh(&first.refresh).await, Err(AuthError::RefreshReused)));
        assert!(matches!(auth.refresh(&second.refresh).await, Err(AuthError::InvalidRefresh)));
    }
```

## Step 7: the user, as an extractor
<!-- bite: 58935cbf-18f4-43fb-8644-1c43613497de -->

Here's the promise from the [[backend/frameworks/axum/index|Axum index]], kept. `src/auth/extract.rs`:

```rust
/// A logged-in user. A handler that takes one can't run for anyone else:
/// without a valid `Authorization: Bearer <token>`, the request is refused before the handler starts.
#[derive(Clone, Copy, Debug)]
pub struct AuthUser(pub Identity);

impl<S> FromRequestParts<S> for AuthUser
where
    S: Send + Sync,
    Keys: FromRef<S>,
{
    type Rejection = ApiError;

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let token = parts
            .headers
            .get(header::AUTHORIZATION)
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.strip_prefix("Bearer "))
            .ok_or_else(|| unauthenticated("Send an access token: `Authorization: Bearer <token>`."))?;
        let identity = Keys::from_ref(state)
            .check_access(token)
            .ok_or_else(|| unauthenticated("That access token isn't valid, or it has expired. Refresh it."))?;
        Ok(AuthUser(identity))
    }
}
```

1. **`Keys: FromRef<S>`**: the extractor finds the signing key in the app state, the way `State<MenuService>` finds the menu. `AppState` gets two fields, `auth: AuthService` and `keys: Keys`, and `#[derive(FromRef)]` does the rest.
2. **No database trip.** The token is checked with the key alone. That's the whole point of a JWT.
3. **A missing or bad token is a 401** with lesson 7's problem shape, code `unauthenticated`.

Now compare two ways of writing a handler that needs a user. In many frameworks, a middleware puts the user in the request, and the handler fetches it: `let user = req.user()`. Forget the middleware on one route, and `user` is empty, or the check is skipped. With an extractor:

```rust
async fn me(State(auth): State<AuthService>, AuthUser(who): AuthUser) -> Result<Data<UserV2>, ApiError> {
    Ok(Data(auth.me(who).await?.into()))
}
```

`who` exists only if the token was valid. There is no way into the function's body without it. Authorization bugs, "this endpoint forgot the check", are one of the most common causes of real breaches. Here, forgetting the check means not writing `AuthUser` in the arguments, and then there's no `who` to use, so the code that needs it doesn't compile.

## Step 8: the routes, and v2 needs a login to order
<!-- bite: a162a6ba-b034-4fe9-b7aa-3fcd9bd18ef2 -->

`src/auth/handlers.rs` serves five routes, v2 only (accounts are new; there's no v1 of them):

```rust
pub fn router<S>() -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    AuthService: FromRef<S>,
    Keys: FromRef<S>,
{
    Router::new()
        .route("/auth/signup", post(sign_up))
        .route("/auth/login", post(log_in))
        .route("/auth/refresh", post(refresh))
        .route("/auth/logout", post(log_out))
        .route("/auth/me", get(me))
}
```

merged into the v2 router in `app` with `.merge(auth::router())`. The wire types are the usual: `SignUp` with `#[validate(email(...))]` and a password of 12 to 128 characters (long beats clever, and 128 caps how much we'll hash), `LogIn`, `RefreshToken`, and `TokensV2` going out:

```rust
#[derive(Serialize, ToSchema)]
#[serde(rename_all = "camelCase")]
pub struct TokensV2 {
    access_token: String,
    refresh_token: String,
    token_type: &'static str,
    /// Seconds until the access token stops working.
    expires_in: i64,
}
```

### Who may order: a type per version

Placing an order is where v1 and v2 differ. Requiring a login in v1 would be a **breaking change**: every v1 app in customers' pockets would stop being able to order, and v1 is frozen until its sunset. So v1 keeps taking orders from anyone, with no customer, and v2 needs a login.

That difference goes where lesson 10 put the others: in the version's trait. A new file, `src/version.rs`, holds what every version says about itself. `V1` and `V2` move here, with the prefix, and `MenuVersion` and `OrderVersion` both build on it (`pub trait MenuVersion: ApiVersion`):

```rust
/// What every API version says about itself. `MenuVersion` and `OrderVersion` build on it.
pub trait ApiVersion: Send + Sync + 'static {
    /// Where this version's routes live: `/v1` or `/v2`.
    const PREFIX: &'static str;
    /// Who may place an order: anyone at all (v1), or a logged-in customer (v2).
    /// It's an extractor, so a v2 order can't be placed without a login: the handler never runs.
    type Customer: Customer + Send;
}

/// The person placing an order, if we know who they are.
pub trait Customer {
    fn customer_id(&self) -> Option<i64>;
}

impl ApiVersion for V1 {
    const PREFIX: &'static str = "/v1";
    type Customer = Anyone;
}

impl ApiVersion for V2 {
    const PREFIX: &'static str = "/v2";
    type Customer = AuthUser;
}
```

`Anyone` is an extractor that never refuses:

```rust
/// v1's customer: nobody in particular. Never refuses.
pub struct Anyone;

impl<S: Send + Sync> FromRequestParts<S> for Anyone {
    type Rejection = Infallible;

    async fn from_request_parts(_: &mut Parts, _: &S) -> Result<Self, Self::Rejection> {
        Ok(Anyone)
    }
}
```

**`Infallible`** is the standard library's type for "this can't happen": an enum with no variants, so no value of it can exist. As a rejection, it says, in the type, that `Anyone` always succeeds.

And `place` asks for the version's customer:

```rust
async fn place<V: OrderVersion>(
    State(orders): State<OrderService>,
    customer: V::Customer,
    ValidatedJson(new): ValidatedJson<NewOrder>,
) -> Result<impl IntoResponse, ApiError> {
    let order = orders.place(new, customer.customer_id()).await?;
```

with one more line in the orders router's `where`, `V::Customer: FromRequestParts<S>`, promising Axum that whatever the version's customer type is, it can be extracted. For `place::<V2>`, `customer` is an `AuthUser`: no token, no order, and the handler never runs. For `place::<V1>`, it's `Anyone`. Same handler, and the rule is in the types.

The service and store pass `customer_id` through to the `INSERT`, and `Order` gains `customer_id: Option<i64>`. In docs.rs, a `bearer` security scheme joins `staff_key` (`HttpBuilder::new().scheme(HttpAuthScheme::Bearer).bearer_format("JWT")`), `place_order` gains `security(("bearer" = []))` and a 401, and the five auth routes are described, so the docs test now checks 14 operations.

### Wiring

In `main`:

```rust
    let keys = Keys::from_env()?;
```

```rust
    let auth = AuthService::new(PgAuthStore::new(pool), keys.clone(), Clock::system());
```

and `auth` and `keys` go into `AppState`.

## Trying it
<!-- bite: 5f002fd6-5377-4fa2-a7c7-8bf4036fe6af -->

From a run of this lesson's code:

```bash
curl -s -X POST localhost:8080/v2/auth/signup -H 'content-type: application/json' \
  -d '{"email":"ada@example.com","name":"Ada","password":"short"}'
# 400 ..."errors":[{"field":"password","message":"must be 12 to 128 characters"}]

curl -s -X POST localhost:8080/v2/auth/signup -H 'content-type: application/json' \
  -d '{"email":"ada@example.com","name":"Ada","password":"correct horse battery"}'
# 201 {"data":{"id":1,"email":"ada@example.com","name":"Ada","role":"customer"}}

curl -s -X POST localhost:8080/v2/auth/login -H 'content-type: application/json' \
  -d '{"email":"Ada@Example.com","password":"correct horse battery"}'
# {"data":{"accessToken":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwicm9sZSI6ImN1c3RvbWVyIi...",
#          "refreshToken":"oyllwT9jFEGby3GCWaZQ497CB4IpSFCsnUm8bUaX_LE","tokenType":"Bearer","expiresIn":900}}
```

(`Ada@Example.com` worked: same account, any capitals.) With the access token:

```bash
curl -s localhost:8080/v2/auth/me -H "authorization: Bearer $ACCESS"
# {"data":{"id":1,"email":"ada@example.com","name":"Ada","role":"customer"}}

curl -s -X POST localhost:8080/v2/orders -H 'content-type: application/json' -d '{"dishId":2,"quantity":1}'
# 401 {"type":".../problems/unauthenticated","title":"Log in first",...}

curl -s -X POST localhost:8080/v2/orders -H 'content-type: application/json' -H "authorization: Bearer $ACCESS" \
  -d '{"dishId":2,"quantity":1}'
# 201 {"data":{"id":6,"dishId":2,"quantity":1,"total":{"amount":120000,"currency":"NGN"},"status":"pending"}}

curl -s -X POST localhost:8080/v1/orders -H 'content-type: application/json' -d '{"dishId":2,"quantity":1}'
# 201 {"data":{"id":7,...}}      ← v1 still lets anyone order
```

and in the database, order 6 has `customer_id` 1, and order 7 has none. Then the theft:

```bash
curl -s -X POST localhost:8080/v2/auth/refresh -H 'content-type: application/json' -d "{\"refreshToken\":\"$REFRESH\"}"
# 200, a new pair
curl -s -X POST localhost:8080/v2/auth/refresh -H 'content-type: application/json' -d "{\"refreshToken\":\"$REFRESH\"}"
# 401 {"code":"refresh-reused","detail":"that refresh token was already used, so every session for this account has been ended; log in again",...}
```

```text
WARN request{method=POST path="/v2/auth/refresh" ...}: mama_put::auth::service: a used refresh token came back; revoking every session user_id=1
```

`cargo test` runs 20 now: the password, token and service tests are new.

## The Rust in this lesson
<!-- bite: ff370840-47af-4da5-8400-3bfcedb22500 -->

1. **`tokio::task::spawn_blocking(move || ...)`**: run slow, blocking work on Tokio's blocking threads, and `.await` the result.
2. **`std::sync::LazyLock`**: a value made once, the first time it's used.
3. **`Option::is_ok_and` on a `Result`**: `true` if it's `Ok` and the value passes a test.
4. **An extractor that reads state, with `Keys: FromRef<S>` and `Keys::from_ref(state)`**.
5. **`str::strip_prefix("Bearer ")`**: the rest of the text if it starts with that, else `None`.
6. **`std::convert::Infallible`**: a type with no values, for "can't fail".
7. **An associated type that's an extractor, `type Customer: Customer + Send`**, and the bound **`V::Customer: FromRequestParts<S>`** in the router.
8. **Supertraits across files, `pub trait MenuVersion: ApiVersion`**.
9. **`[0u8; 32]`**: an array of 32 zero bytes, filled in place by `getrandom::fill(&mut bytes)`.
10. **Raw byte strings, `br#"..."#`**.
11. **`#[validate(email(...))]`**, and two validators on one field.
12. **`jsonwebtoken`'s `encode`, `decode` and `Validation`**, with the algorithm pinned.

## Your project so far
<!-- bite: f1764d9c-d00b-4637-8ab7-37651c507e33 -->

```text
mama-put/
├── .env                   ← + JWT_SECRET
├── Cargo.toml             ← + argon2, jsonwebtoken (rust_crypto), sha2, hex, getrandom
├── migrations/
│   └── 0005_users_and_tokens.sql   ← users, refresh_tokens, orders.customer_id
└── src/
    ├── main.rs            ← Keys::from_env, AuthService
    ├── lib.rs             ← + pub mod auth, version; AppState.auth and .keys; auth routes in v2
    ├── version.rs         ← ApiVersion (PREFIX, Customer), V1, V2, Customer, Anyone
    ├── db.rs              ← + is_unique_violation
    ├── docs.rs            ← + bearer scheme, five auth routes; the test checks 14
    ├── auth/
    │   ├── mod.rs
    │   ├── model.rs       ← Role, Identity, User
    │   ├── password.rs    ← hash and verify with argon2id on spawn_blocking; DUMMY_HASH; 2 tests
    │   ├── tokens.rs      ← Keys (HS256 pinned), access tokens, refresh tokens and their hash; 4 tests
    │   ├── store.rs       ← PgAuthStore: users, use_refresh in one guarded UPDATE, revoke_all
    │   ├── service.rs     ← AuthError, AuthService: sign up, log in, rotating refresh with reuse detection; 2 tests
    │   ├── extract.rs     ← AuthUser
    │   └── handlers.rs    ← /auth/signup, login, refresh, logout, me
    ├── menu/versions.rs   ← MenuVersion: ApiVersion
    └── orders/
        ├── versions.rs    ← OrderVersion: ApiVersion
        ├── handlers.rs    ← place takes V::Customer
        └── ...            ← customer_id through service and store
```

## Common mistakes
<!-- bite: 51bbd056-e597-48ab-93b6-e335145af03f -->

1. **Storing passwords, or hashing them with SHA-256.** Use a slow password hash: argon2id.
2. **Hashing on an async thread.** One login stalls a worker for tens of milliseconds. `spawn_blocking`.
3. **Different answers, or different timings, for "no such email" and "wrong password".** You've built an account finder.
4. **Trusting the JWT header's algorithm.** Pin it, so `"alg": "none"` is refused.
5. **Secrets in JWT claims.** Anyone can read them. Only ids and roles.
6. **Long-lived access tokens.** They can't be cancelled. Keep them short and refresh.
7. **Refresh tokens that work more than once.** A stolen one works forever. Rotate, and treat a reused one as theft.
8. **Storing refresh tokens as they are.** Store their hash, like passwords.
9. **A middleware that "attaches the user" and handlers that might forget to look.** Make the user an extractor; then there's nothing to forget.
10. **Requiring a login on a frozen version.** It's a breaking change. v1 stays open until its sunset.

## Check your understanding
<!-- bite: a8aa2a60-5781-4fd4-bc12-7e9eefcfef12 -->

1. Why argon2id and not SHA-256 for passwords, and why is SHA-256 fine for refresh tokens?
2. What would go wrong if `hash` ran argon2 directly in the `async fn`, without `spawn_blocking`?
3. Why does logging in with an unknown email still check a hash?
4. Anyone can read a JWT's claims. What stops a customer changing `"role":"customer"` to `"admin"`?
5. Why 15 minutes for access tokens, and what makes that bearable for the customer?
6. A refresh token comes back that was already used. Why end every session for that account, not just refuse that token?
7. Why can't a handler that takes `AuthUser` run for someone who isn't logged in?
8. How do v1 and v2 differ on placing orders, and where in the code does the difference live?

<details>
<summary>Answers, after your attempt</summary>

1. Passwords come from a small space of likely guesses, so a fast hash lets an attacker try billions a second; argon2id is slow and memory-hungry on purpose, and salted. A refresh token is 256 random bits, which can't be guessed however fast the hash is, so a fast hash only has to stop a leaked table being used directly.
2. Hashing is tens of milliseconds of solid CPU work. In an `async fn`, it holds one of Tokio's worker threads (one per core) the whole time, so a few logins at once would stop the server answering anything else.
3. So a missing account takes as long as a wrong password. If it answered instantly, timing the answers would tell an attacker which emails have accounts.
4. The signature. It's made from the header and claims with `JWT_SECRET`; change the claims and the signature no longer matches, and `check_access` refuses it. Only someone with the secret can make a valid token.
5. Because an access token can't be cancelled, a stolen one should stop working soon. The refresh token makes it bearable: the app swaps it for a new pair without asking the customer to log in.
6. Because a used token coming back means someone has a copy, and we can't tell whether the request is from Ada or the thief. Ending every session is the only way to be sure the thief is out; Ada just logs in again.
7. Because Axum runs the extractor before the handler. If there's no valid token, `AuthUser::from_request_parts` returns a 401 and the handler is never called; and inside the handler, the user only exists as the `AuthUser` argument.
8. v1 lets anyone order, with no customer; v2 needs a login. The difference is the `Customer` associated type in `ApiVersion`: `Anyone` for `V1`, `AuthUser` for `V2`. The `place` handler takes `V::Customer`, so each version's copy extracts its own.

</details>

## Practice
<!-- bite: 89bd8040-523a-4fe9-b601-b6535d2a69ef -->

1. Add `PATCH /v2/auth/me` to change your name, and `POST /v2/auth/change-password`, which needs the current password and revokes every refresh token afterwards, so other phones are logged out.
2. Make the 401 responses carry `WWW-Authenticate: Bearer`, which the HTTP standard asks for. Where would that header be added, given lesson 7's `write_problems`?
3. Delete expired and used refresh tokens older than 30 days: a SQL statement, and where you'd run it (lesson 18 has the answer).
4. Write a `#[sqlx::test]` that places a v2 order through the whole app with `oneshot`, with and without a token.
5. Time `POST /v2/auth/login` for an email that exists with the wrong password, and for one that doesn't. Are they within a few milliseconds of each other?

**Done when** passwords are stored only as argon2id hashes made on blocking threads, sign-up, log-in, refresh and log-out work, access tokens expire after 15 minutes and can't be forged, a reused refresh token ends every session, `GET /v2/auth/me` needs a token, v2 orders need a login and belong to the customer while v1 orders don't, and `cargo test` passes.

## Before moving on
<!-- bite: 3a0550a9-8d62-4cc3-8a23-b68d555a2990 -->

Mama Put knows who's calling now. Passwords are hashed the way the people who study attacks recommend, tokens are short and can't be forged, a stolen refresh token gives itself away, and "this needs a login" is a type, so it can't be forgotten.

But knowing *who* someone is doesn't say what they *may do*. Ada is logged in, so she can call `GET /v2/orders/7`, which is Bayo's order. And the kitchen still shares one staff key. Next lesson: authorization, with roles, a policy written down in one place, and permissions as extractors too.

## Related
<!-- bite: 04c206fd-b455-47f8-b6f8-5b1fd5a2f616 -->

- [[backend/frameworks/axum/13-authorization|Next: Authorization]]
- [[backend/frameworks/net-http/12-authentication|The same lesson in net/http]] — argon2 by hand, golang-jwt, and a user in the context
- [[backend/05-auth/index|Authentication and Authorization]] — the ideas, across languages
- [[backend/frameworks/axum/04-async-pitfalls|Async Pitfalls]] — why slow work goes on `spawn_blocking`

## About this lesson
<!-- bite: 643dc479-badb-4c39-b0a5-d447e4c402ad -->

**Level:** Advanced. Lesson 12 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8, argon2 0.6, jsonwebtoken 12 and sqlx 0.9. Covers argon2id with OWASP's settings as PHC strings, hashing on `spawn_blocking`, equal timing for unknown accounts with a dummy hash, sessions versus tokens, HS256 JWTs with the algorithm pinned and required claims, why claims are readable but not changeable, random refresh tokens stored as SHA-256 hashes, rotation with reuse detection that revokes every session, a single guarded `UPDATE` for using a token, a store without a trait and why, an `AuthUser` extractor reading `Keys` from state, an `ApiVersion` trait whose `Customer` associated type makes v2 orders need a login while v1's don't, `Infallible`, and documenting bearer security.
