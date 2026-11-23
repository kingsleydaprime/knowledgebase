---
id: abec9d0b-5c26-419f-8367-77233fb1fe43
---

# MCP in Production 1: Logging In

**Running an MCP server in production means letting an AI assistant act for a real person, and this first part is about the start of that: the assistant logs in as the person with OAuth, and we check its token to the last claim.**

## Before you start
<!-- bite: 32312644-330d-4877-b497-6170f913be6e -->

You should have finished [[backend/frameworks/axum/23-mcp-server|lesson 23]], so `cargo test` runs 83 tests. This part leans on lesson 12 (jsonwebtoken, with the algorithm pinned) and lesson 13 (the `Identity` every service takes).

This topic is big, so it comes in five parts:

1. **Logging in**: how an assistant gets a token for Bayo, and how we check it.
2. **The door and the person's permissions**: the check in front of `/mcp`, and scopes on top of lesson 13's policy.
3. **Quotes and asking the person**: three layers so a model can't spend money on a guess.
4. **Prompt injection and limits**: keeping power out of text, a per-person limit, a daily cap, and a record of every order.
5. **Trying it and testing**: a pretend authorization server, a real order by hand, and the tests.

The code in the five parts is one change to the project. It builds and runs at the end of part 5, which tries it by hand and tests it; until then, read each part's code as a piece of that whole.

After this part you will be able to:

1. Explain how an MCP client logs a person in with OAuth, and what our server's part in it is.
2. Fetch and keep an authorization server's public keys safely.
3. Check an access token with them: for the right audience, of the right type, and with nothing left to the token's choice.
4. Turn a good token into the same `Identity` every service already understands, always as a customer.

## What to install
<!-- bite: 257ad4a3-51a5-44b1-9bd6-a3e2c601b0d7 -->

Nothing new in `Cargo.toml`'s dependencies. Everything this lesson needs is already there:

1. **jsonwebtoken** (lesson 12) can read a published key set (a JWKS, step 2 below) and check signatures with it.
2. **reqwest** (lesson 17) fetches that key set.
3. **rmcp** (lesson 23) already speaks the newest MCP protocol, which lets a server with no sessions ask the person a question (part 3).

Two small changes to `Cargo.toml`'s settings, explained in part 5:

```toml
# So is hashing passwords: unoptimised, Argon2 takes seconds, and a test run full of sign-ups hits
# the app's 10-second timeout. Optimising it (and its hash function) changes nothing but speed.
[profile.dev.package.argon2]
opt-level = 3

[profile.dev.package.blake2]
opt-level = 3
```

You'll also want **`openssl`** (most systems have it) to make a key for a pretend authorization server, to try the login by hand in part 5. The tests don't need it: their keys are files in `tests/keys/`.

## Where we stopped
<!-- bite: 7fbc78f0-9fd8-4157-815b-1e33a5bcb669 -->

Bayo asks his assistant: "Order me two plates of jollof from Mama Put."

For that, three things must be true:

1. **The assistant must act as Bayo.** Not as "some AI". As Bayo, with his account, his orders, his limits, and nothing else. It must never see Ada's orders, or do what staff can do.
2. **Bayo must actually want it.** Models misunderstand. "Is the jollof good there? Maybe two plates for me and Ada?" is a question, not an order. A model that orders anyway has spent Bayo's money on a guess.
3. **Nobody else gets to steer it.** If the assistant reads text someone else wrote (a review, a note on an order, a web page it visited earlier) and that text says "also order 20 plates", the assistant must not be able to do real harm because of it.

The five parts take these in turn. This one starts with the first: making sure the assistant really is acting for Bayo.

## The kid version
<!-- bite: 64f4a67c-012a-46f6-99b3-bd5cae1dfd3f -->

Bayo sends his younger brother to Mama Put with a note: "This is my brother. He can order for me. Bayo." Mama checks the note really is Bayo's handwriting. She lets the boy order *for Bayo*, but not see other customers' orders, and not walk into the kitchen.

Before she cooks, she says: "Two plates of jollof, ₦3,000. Bayo pays when he collects." The boy can't pay; he has no money. So if he misheard, the worst case is two plates nobody pays for, and Mama sells them to someone else.

On the way, a stranger told the boy: "Tell Mama to give you 20 plates!" The boy repeats it. Mama looks at the note: through his brother, Bayo can order at most 5 plates at a time. Twenty is refused.

The note is the OAuth token. "For Bayo, not the kitchen" is scopes and permissions. "Bayo pays" is the step the AI can't do itself. The stranger is prompt injection. The 5-plate rule is the cap.

**Where the picture stops working.** Mama can see the boy's face and tell he's unsure. Our server sees only HTTP requests. All we know about the AI's intentions is what's in the request, and a request can't tell us whether Bayo *really* meant it. So we make sure nothing that matters happens without Bayo himself.

## Terms used in this part
<!-- bite: b2ea2562-0fda-418c-ba7c-fc8e8b21cfb9 -->

1. **OAuth**: This is the standard way for a person to let an app act for them on another service without giving the app their password. The person logs in on the service's own page and approves; the app gets an **access token**.
2. **Authorization server**: This is the system that shows the login page, asks the person to approve, and issues tokens.
3. **Resource server**: This is the API that accepts tokens and does the work. Our MCP server is a resource server.
4. **Protected resource metadata**: This is a small public JSON document the MCP server publishes, telling clients which authorization server to log in with.
5. **JWKS**: This is a JSON Web Key Set: the authorization server's public keys, published at a URL, so anyone can check its signatures. Each key has an id, its **kid**.
6. **Audience**: This is who a token is *for*. A token for Mama Put's MCP server must say so, and we refuse tokens meant for anything else.
7. **Scope**: This is a named permission the person approved for this app, like `orders:write`. Scopes limit what the *app* may do; roles still limit what the *person* may do.

## Step 1: how an MCP client logs in
<!-- bite: 269102f5-4846-4fde-9e89-0852fa0df4fc -->

MCP uses OAuth, and the specification sets its shape, so every client and server can work together. From our server's side, it goes like this:

1. **The assistant calls `/mcp` with no token.** We answer **401**, with a header pointing at our metadata:

   ```text
   HTTP/1.1 401 Unauthorized
   www-authenticate: Bearer resource_metadata="https://api.mamaput.ng/.well-known/oauth-protected-resource/mcp"
   ```

2. **The client reads our protected resource metadata**, which names the authorization server:

   ```json
   {
     "resource": "https://api.mamaput.ng/mcp",
     "authorization_servers": ["https://auth.mamaput.ng"],
     "scopes_supported": ["orders:read", "orders:write"],
     "bearer_methods_supported": ["header"]
   }
   ```

3. **The client sends Bayo to the authorization server's login page**, in his browser. He logs in to Mama Put (on Mama Put's page, never the assistant's) and sees: "*Bayo's Assistant* wants to: see your orders, place orders for you." He approves.
4. **The client gets an access token**, with its **audience** set to our MCP server's address, `https://api.mamaput.ng/mcp`. (The client asked for that by sending a `resource` parameter during the login. That's part of the spec, so a token can't be taken from one MCP server and used at another.)
5. **Every call to `/mcp` now carries `Authorization: Bearer <token>`**, and we check it.

Those middle steps are the client's job and the authorization server's. Ours is to publish the metadata, answer 401 correctly, and **check every token properly**.

The metadata's address follows its standard (RFC 9728): for a resource at `/mcp`, it's `/.well-known/oauth-protected-resource/mcp`, with the resource's path added on the end. Clients find it from the `WWW-Authenticate` header first, and from that standard address if the header is missing.

**Who runs the authorization server?** It's a big job: login pages, consent screens, registering clients, PKCE, refresh tokens, rotating keys. Lesson 12's login is not one: it gives tokens to *our own* apps, which we trust; an authorization server gives tokens to *other people's* apps, which we don't. Two sensible choices:

1. **A hosted identity provider** that supports what the MCP spec asks for. Many do now. Our users log in through it, and we link its id for them to our `users` table.
2. **An open-source authorization server** you run yourself (Keycloak is a common one), with the same linking.

What you should **not** do is write your own OAuth server from scratch for this. The spec is public, and rmcp even has the client side, but a homemade authorization server is a lot of security-critical code to own, for a food stall.

Either way, from our server's point of view the token is a **JWT** signed by the authorization server, and we check it with the public keys it publishes as a JWKS.

## Step 2: the authorization server's keys
<!-- bite: 10014249-87b8-4b85-b19a-5c65796a8f3a -->

Checking a token has two parts: getting the authorization server's keys, and checking a token with them. Both live in `src/mcp/oauth.rs`.

A JWKS looks like this (one EC key, shortened):

```json
{"keys":[{"kty":"EC","crv":"P-256","kid":"dev-1","alg":"ES256","x":"f83O…","y":"x_FE…"}]}
```

Every token says in its header which key signed it (`"kid": "dev-1"`). So we keep the keys in a map from kid to key, and fetch the set again when a token names a kid we haven't seen. That's how the authorization server can change keys without us restarting:

```rust
/// The authorization server's public keys, by key id ("kid"): fetched from its JWKS address, kept,
/// and fetched again when a token names a key we haven't seen, so it can change keys without us restarting.
#[derive(Clone)]
pub struct KeySet(Arc<KeySetInner>);

struct KeySetInner {
    /// Where the keys are published. `None`: a fixed set, for tests.
    url: Option<reqwest::Url>,
    client: reqwest::Client,
    keys: RwLock<HashMap<String, (DecodingKey, Algorithm)>>,
    last_fetch: Mutex<Option<Fetch>>,
}

struct Fetch {
    at: Instant,
    worked: bool,
}

/// However many unknown key ids arrive, fetch at most this often. Otherwise anyone could make us
/// download the keys on every request, just by sending made-up ids.
const REFETCH_AFTER: Duration = Duration::from_secs(60);

enum KeyError {
    /// No key with that id, even after looking again.
    Unknown,
    /// We couldn't reach the authorization server to look.
    Unreachable,
}

impl KeySet {
    /// Keys from `url`, fetched the first time a token needs one. `client` must have a timeout.
    pub fn fetched_from(url: reqwest::Url, client: reqwest::Client) -> Self {
        KeySet::build(Some(url), client, HashMap::new())
    }

    /// These keys and no others. For tests.
    pub fn fixed(set: &JwkSet) -> Self {
        KeySet::build(None, reqwest::Client::new(), usable(set))
    }

    fn build(url: Option<reqwest::Url>, client: reqwest::Client, keys: HashMap<String, (DecodingKey, Algorithm)>) -> Self {
        KeySet(Arc::new(KeySetInner { url, client, keys: RwLock::new(keys), last_fetch: Mutex::new(None) }))
    }

    async fn key(&self, kid: &str) -> Result<(DecodingKey, Algorithm), KeyError> {
        if let Some(found) = self.0.keys.read().await.get(kid) {
            return Ok(found.clone());
        }
        let Some(url) = &self.0.url else { return Err(KeyError::Unknown) };

        // One fetch at a time. Whoever was waiting may find the key already there.
        let mut last = self.0.last_fetch.lock().await;
        if let Some(found) = self.0.keys.read().await.get(kid) {
            return Ok(found.clone());
        }
        if let Some(fetch) = &*last
            && fetch.at.elapsed() < REFETCH_AFTER
        {
            return Err(if fetch.worked { KeyError::Unknown } else { KeyError::Unreachable });
        }

        let fetched = self.0.client.get(url.clone()).send().await.and_then(|r| r.error_for_status());
        let set = match fetched {
            Ok(response) => response.json::<JwkSet>().await,
            Err(e) => Err(e),
        };
        *last = Some(Fetch { at: Instant::now(), worked: set.is_ok() });
        let set = set.map_err(|e| {
            tracing::error!(cause = %e, %url, "can't fetch the authorization server's keys");
            KeyError::Unreachable
        })?;
        let keys = usable(&set);
        let found = keys.get(kid).cloned();
        *self.0.keys.write().await = keys;
        found.ok_or(KeyError::Unknown)
    }
}

/// The keys we'll check signatures with: each with an id, for signing, with an algorithm we accept.
fn usable(set: &JwkSet) -> HashMap<String, (DecodingKey, Algorithm)> {
    set.keys
        .iter()
        .filter_map(|jwk| {
            let kid = jwk.common.key_id.clone()?;
            if matches!(jwk.common.public_key_use, Some(PublicKeyUse::Encryption)) {
                return None;
            }
            // Our list, not whatever the key set offers.
            let algorithm = match jwk.common.key_algorithm? {
                KeyAlgorithm::ES256 => Algorithm::ES256,
                KeyAlgorithm::RS256 => Algorithm::RS256,
                _ => return None,
            };
            Some((kid, (DecodingKey::from_jwk(jwk).ok()?, algorithm)))
        })
        .collect()
}
```

Read `key` slowly; each line stops a real problem:

1. **The fast path is a read lock and a map lookup.** Almost every request ends there. `RwLock` lets any number of requests read at once.
2. **One fetch at a time.** If fifty requests arrive with a new kid at once, they queue on the `Mutex`, the first one fetches, and the other forty-nine find the key already there when it's their turn. Lesson 19's cache did the same with its per-key lines.
3. **At most one fetch a minute.** Without `REFETCH_AFTER`, anyone could make us download the keys on every request by sending tokens with made-up kids. Within the minute, an unknown kid is just an invalid token.
4. **"Unknown" and "unreachable" are different answers.** If the last fetch *failed*, we say so (`Unreachable`), and the request gets a 503, not a 401. A 401 would tell the client its token is bad, and it might send Bayo off to log in again, when really it's our problem.
5. **`usable` picks the keys, by our rules.** Only keys with a kid, only signing keys, and only the two algorithms we accept. jsonwebtoken's `DecodingKey::from_jwk` turns each into a key it can check with. The algorithm comes from *our* list, matched against the key, never from the token.

`reqwest::Client` comes from `main`, with a 5-second timeout. A slow authorization server mustn't hold every MCP call for ever.

## Step 3: checking the token
<!-- bite: 4a49f5f2-c5e3-4afb-8a0b-c5d334ebc2a0 -->

```rust
/// Checks access tokens: from our authorization server, for exactly this MCP server, for someone we know.
#[derive(Clone)]
pub struct TokenCheck {
    pub keys: KeySet,
    /// The authorization server, as it names itself in tokens: `https://auth.mamaput.ng`.
    pub issuer: String,
    /// This MCP server's address: tokens must be issued for exactly this.
    pub resource: String,
    pub users: PgAuthStore,
}

/// The claims we read. `exp`, `iss` and `aud` are checked by jsonwebtoken itself.
#[derive(Deserialize)]
struct AccessClaims {
    /// The person, as the authorization server knows them.
    sub: String,
    /// What they let this assistant do, space-separated: `orders:read orders:write`.
    #[serde(default)]
    scope: String,
    /// Which assistant: every access token has one (RFC 9068).
    client_id: String,
}

#[derive(Debug, PartialEq)]
pub enum TokenError {
    /// Anything wrong with the token. We never say what.
    Invalid,
    /// Our problem, not the token's: try again later.
    CantCheck,
}

impl TokenCheck {
    pub async fn verify(&self, token: &str) -> Result<Caller, TokenError> {
        let header = decode_header(token).map_err(|_| TokenError::Invalid)?;
        // An access token, not an ID token or some other JWT from the same server (RFC 9068).
        let typ = header.typ.as_deref().unwrap_or("").to_ascii_lowercase();
        if typ != "at+jwt" && typ != "application/at+jwt" {
            return Err(TokenError::Invalid);
        }
        let kid = header.kid.ok_or(TokenError::Invalid)?;
        let (key, algorithm) = self.keys.key(&kid).await.map_err(|e| match e {
            KeyError::Unknown => TokenError::Invalid,
            KeyError::Unreachable => TokenError::CantCheck,
        })?;

        // The key decides the algorithm, never the token. A token whose header says another one is refused.
        let mut validation = Validation::new(algorithm);
        validation.set_issuer(&[&self.issuer]);
        validation.set_audience(&[&self.resource]);
        validation.set_required_spec_claims(&["exp", "iss", "aud", "sub"]);
        validation.leeway = 30; // seconds of difference allowed between the two servers' clocks
        let claims = decode::<AccessClaims>(token, &key, &validation).map_err(|_| TokenError::Invalid)?.claims;

        let user = self.users.find_by_external_subject(&claims.sub).await.map_err(|e| {
            tracing::error!(cause = %e, "mcp token: user lookup failed");
            TokenError::CantCheck
        })?;
        // A good token for an account we don't have (or no longer have) is no good here.
        let user = user.ok_or(TokenError::Invalid)?;

        Ok(Caller {
            // Whatever their role, an assistant only ever acts as a customer.
            who: Identity { user_id: user.id, role: Role::Customer },
            client: claims.client_id,
            scopes: claims.scope.split_whitespace().map(str::to_owned).collect(),
        })
    }
}
```

It's lesson 12's check again, with every rule pinned, and each one stops a real attack:

1. **`typ` must be `at+jwt`.** The standard for JWT access tokens (RFC 9068) says the header marks them so. An authorization server signs other JWTs too, like the *ID token* a website gets when you "log in with…". With the same key. This line stops one of those being used as an access token.
2. **The signature, with the key its kid names.** Anyone can write a JWT; only the authorization server can sign one.
3. **`Validation::new(algorithm)`, with the algorithm the key gave us.** jsonwebtoken refuses a token whose header names any other. Never let the token choose its own algorithm (lesson 12's `alg: none` story).
4. **`set_issuer`**: the token came from *our* authorization server, not another one that happens to use JWTs.
5. **`set_audience(&[&self.resource])`**: the token was issued **for this MCP server**. This is the check most often forgotten. Without it, a token Bayo gave some other app, from the same authorization server, would work here too.
6. **`set_required_spec_claims`**: a token without `exp`, `iss`, `aud` or `sub` is refused, not trusted. Expiry is checked against the real clock, with 30 seconds of leeway for the two servers' clocks to differ.
7. **`client_id` is required.** RFC 9068 says every access token has one. We'll record it on every order the assistant places.
8. **The person still exists here.** A good token for an account we've deleted, or never linked, must not work.

Notice the two different failures. Anything wrong with the token itself is **`TokenError::Invalid`**, and nothing more specific. The door in part 2 turns that into one 401 that never says which check failed: "audience mismatch" or "expired at 12:41" would tell an attacker which part to work on. A database failure or an unreachable key server is **`CantCheck`**: really our problem, logged, and a 503.

`find_by_external_subject` looks the person up by the authorization server's id for them, its `sub`, stored in a new column. `migrations/0012_mcp.sql` starts:

```sql
-- Lesson 24: AI assistants acting for customers.

-- Who each person is at the authorization server ("sub"), set when they first log in through it.
ALTER TABLE users ADD COLUMN external_subject text UNIQUE;

-- Where each order came from, and which assistant placed it.
ALTER TABLE orders
  ADD COLUMN placed_via text NOT NULL DEFAULT 'app' CHECK (placed_via IN ('app', 'graphql', 'mcp')),
  ADD COLUMN placed_by_client text;
```

The link is made when the person first logs in through the authorization server. If you link by email instead, only do it when the authorization server says the email is **verified** (`email_verified: true`). Otherwise anyone who signs up there with Bayo's email address becomes Bayo here. (`placed_via` is for part 4.)

## Step 4: always a customer
<!-- bite: cc82e824-9fae-490f-8a68-74a07c0fde8b -->

Look at the end of `verify` again, where the `Caller` is made:

```rust
who: Identity { user_id: user.id, role: Role::Customer },
```

**The role is always `Customer`.** Even if a staff member connects an assistant, it acts only as a customer. There are no kitchen or admin tools here at all, and if one were added by mistake, lesson 13's policy would refuse it, because the `Identity` it's given is a customer's. An AI with staff powers is a blast radius we don't need. (Part 5's tests connect staff member Chidi's assistant and check it can't see Ada's order, which Chidi can see in the app.)

## The Rust in this part
<!-- bite: 5bfdfe5c-badd-48cb-b893-6724727de8c1 -->

1. **`tokio::sync::RwLock` and `Mutex` together**: many readers of the key map at once, and one fetcher at a time. Both are async locks, safe to hold across an `.await` (the fetch).
2. **Checking twice around a lock**: look, take the lock, look again. Whoever waited may find the work already done.
3. **`if let … && …`** (let chains, Rust 2024): `if let Some(fetch) = &*last && fetch.at.elapsed() < REFETCH_AFTER` tests a pattern and a condition in one `if`.
4. **`filter_map` with `?` inside a closure**: each `?` on an `Option` skips that key, so `usable` reads as a list of rules.
5. **`Validation::new(algorithm)`**: jsonwebtoken's settings, built for each token from the key's algorithm, with `set_issuer`, `set_audience` and `set_required_spec_claims`.
6. **`#[serde(default)]` on one field**: `scope` may be missing from a token, and then it's an empty string; `client_id` has no default, so a token without one doesn't decode at all.

## Your project so far
<!-- bite: d3cdaa2a-d168-4349-8863-2e948fc62985 -->

```text
mama-put/
├── migrations/
│   └── 0012_mcp.sql              ← NEW: users.external_subject (the rest of this file comes in parts 3 and 4)
└── src/
    ├── auth/store.rs             ← find_by_external_subject
    └── mcp/
        └── oauth.rs              ← NEW: KeySet, TokenCheck, TokenError (Scope and Caller come in part 2)
```

## Common mistakes
<!-- bite: 8a1dbbd5-fb3f-444d-a3ad-4d3cb66db258 -->

1. **Writing your own authorization server.** Use a hosted or established one; your job is to check its tokens.
2. **Forgetting the audience check.** Then any token from the same authorization server, meant for any app, works on your server.
3. **Taking the algorithm from the token.** Take it from the key, from your own list.
4. **Accepting any JWT the authorization server signed.** Check `typ` is `at+jwt`, so an ID token isn't an access token.
5. **Fetching the keys whenever a kid is unknown.** Anyone can send made-up kids. Fetch at most once a minute, one fetch at a time.
6. **Linking people by an email the authorization server hasn't verified.** Then whoever signs up there with Bayo's address becomes Bayo here.
7. **Giving the assistant the person's full role.** Staff and admins act as customers through MCP.

## Check your understanding
<!-- bite: 45502ea1-d655-40de-99d5-469fb6ca2c68 -->

1. In the login flow, which parts are our server's job, and which are the client's and the authorization server's?
2. Bayo gave a "Recipes" app a token from the same authorization server. Which check stops it working on our MCP server?
3. Why does `KeySet` remember whether its last fetch worked, and what does each answer become?
4. Why does `verify` check the `typ` header?
5. A cook connects their assistant. What can it do, and why?

<details>
<summary>Answers, after your attempt</summary>

1. Ours: publish the protected resource metadata, answer 401 with the header that points to it, and check every token. The client finds the authorization server, sends the person to its login page, and gets the token; the authorization server shows the login and consent, and signs the token.
2. The audience check, `set_audience(&[&self.resource])`. The Recipes app's token says it's for the Recipes app, not `https://api.mamaput.ng/mcp`, so it's refused.
3. So it can tell "no such key" from "couldn't look". Within a minute of a fetch that worked, an unknown kid is an invalid token (401). Within a minute of a fetch that failed, it's `Unreachable` (503), because the token may be fine and the problem is ours.
4. The authorization server signs other JWTs with the same key, like ID tokens. `at+jwt` marks an access token (RFC 9068), so an ID token can't be used as one.
5. Only what a customer can do, for their own account: `verify` always sets the role to `Customer`. Lesson 13's services would refuse a staff action, because the identity they get is a customer's.

</details>

## Practice
<!-- bite: 0c5c60ab-7434-4298-a892-647f88089bbc -->

1. Write the link step: when a token's `sub` isn't known yet, but the token also has `email` and `email_verified: true`, and that email matches a user, set their `external_subject` once. Where should it run, in `verify` or somewhere else? Write down why.
2. Add RS256 tokens to your mental model: what would change in `usable` and `verify` if the authorization server used RSA keys? (Nothing in `verify`: find out why.)

**Done when** you can explain each line of `KeySet::key` and `TokenCheck::verify`, and why each check is there. The code runs and is tested in part 5.

## Before moving on
<!-- bite: 29dc2cd8-f543-4711-8324-bd59ac42c43f -->

We can now tell a real token from everything else, and turn it into Bayo, as a customer. But nothing calls `verify` yet, and the tools don't know who they're acting for. Part 2 builds the door in front of `/mcp` that runs the check on every request, hands the person to the tools, and adds the second question after "who is this?": "what did they let this assistant do?"

## Related
<!-- bite: 89513fdb-0f68-4632-ac65-91e0e4650a7a -->

- [[backend/frameworks/axum/25-mcp-in-production-2|Next: MCP in Production 2: The Door and the Person's Permissions]]
- [[backend/frameworks/net-http/24-mcp-in-production|The same topic in net/http]] — keyfunc for the keys, and the SDK's bearer middleware
- [[backend/frameworks/axum/12-authentication|Authentication]] — jsonwebtoken with the algorithm pinned
- [[backend/frameworks/axum/13-authorization|Authorization]] — the `Identity` the services take

## About this lesson
<!-- bite: 5249f7a0-479a-4c2c-92b2-1814b412d69d -->

**Level:** Advanced. Part 1 of 5 on MCP in production, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), rmcp 3.11 and jsonwebtoken 12. Covers the MCP OAuth flow and protected resource metadata at its RFC 9728 address, why not to write your own authorization server, fetching and caching a JWKS safely (one fetch at a time, at most once a minute, "unknown" versus "unreachable"), checking access tokens with the algorithm from the key and the type, issuer, audience and expiry pinned, one answer for every bad token, linking people by the authorization server's id, and acting only as a customer.
