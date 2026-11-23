---
id: 718656e3-4904-4eb7-9ea0-38e5e6b5938c
---

# MCP in Production 5: Trying It and Testing

**The last part puts the MCP pieces together in `main`, places a real order by hand through a pretend authorization server, and tests every promise the first four parts made.**

## Before you start
<!-- bite: 206570af-23f8-4c70-a355-2bd2614663ff -->

You should have finished [[backend/frameworks/axum/27-mcp-in-production-4|part 4]]. Every piece is written: `TokenCheck`, the door, scopes, quotes and the question to the person, the limits and the record of where orders came from. You'll need `openssl` for a key, and Postgres and both Redis servers running, as since lesson 19.

After this part you will be able to:

1. Run a pretend authorization server for trying MCP logins on your own computer.
2. Call the MCP server by hand, with both the older protocol and 2026-07-28.
3. Test token checks, scopes, the whole order and the limits, with signed tokens and hosts that confirm, decline or can't ask.
4. Spot two ways a growing test suite can fail that have nothing to do with the code under test.

## Where we stopped
<!-- bite: e11b0014-923e-4237-bc70-96a6279ba649 -->

Four parts of code, and none of it has run yet. This part wires it into `main`, tries it, and tests it. Running it is also how the opening-hours check in part 3 came about: at 5 a.m. Lagos time, the first version gave a quote for a shop that was closed.

## Step 1: trying it by hand
<!-- bite: 84c6cce6-62c4-4d9f-98be-dbe7de513399 -->

To try the login by hand, you need an authorization server. `examples/dev_auth.rs` is a pretend one: it serves a JWKS made from a key file, and gives a token to anyone who asks. **Never deploy it.**

```rust
async fn token(State(dev): State<Arc<Dev>>, Query(ask): Query<Ask>) -> String {
    let now = jiff::Timestamp::now().as_second();
    let claims = json!({
        "iss": ISSUER, "aud": dev.resource, "sub": ask.sub, "scope": ask.scope,
        "client_id": "dev-assistant", "iat": now, "exp": now + 600,
    });
    let header = Header { typ: Some("at+jwt".into()), kid: Some(KID.into()), ..Header::new(Algorithm::ES256) };
    jsonwebtoken::encode(&header, &claims, &dev.key).expect("signing works")
}
```

Make it a key and start it, then add its addresses to `.env`:

```bash
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 \
  | openssl pkcs8 -topk8 -nocrypt -outform DER -out dev-auth-key.der
cargo run --example dev_auth -- dev-auth-key.der
```

```bash
AUTH_ISSUER=http://localhost:9000
AUTH_JWKS_URL=http://localhost:9000/jwks.json
```

`main` builds the MCP pieces in one function:

```rust
/// The MCP server, its token check and its limits. Assistants log people in at our authorization server
/// (AUTH_ISSUER); we check its tokens with the keys it publishes (AUTH_JWKS_URL). We don't run it here.
#[allow(clippy::too_many_arguments)]
fn mcp_server(
    pool: &sqlx::PgPool,
    public_url: &reqwest::Url,
    hosts: Vec<String>,
    limits: redis::aio::ConnectionManager,
    http: &HttpConfig,
    menu: &MenuService,
    orders: &OrderService,
    payments: &PaymentService,
) -> Result<mcp::Mcp, Box<dyn std::error::Error>> {
    let issuer = env("AUTH_ISSUER")?;
    let base = public_url.as_str().trim_end_matches('/');
    let resource = format!("{base}/mcp");
    // Fetching keys has its own short timeout: a slow authorization server mustn't hold every MCP call.
    let key_client = reqwest::Client::builder().timeout(Duration::from_secs(5)).build()?;
    let tokens = mcp::TokenCheck {
        keys: mcp::KeySet::fetched_from(env("AUTH_JWKS_URL")?.parse()?, key_client),
        issuer: issuer.clone(),
        resource: resource.clone(),
        users: PgAuthStore::new(pool.clone()),
    };
    // 60 tool calls a minute per person: plenty for a conversation, quickly hit by an assistant in a loop.
    let fallback = RateLimiter::new(60, Duration::from_secs(1), http.behind_proxy);
    let per_person = SharedLimit::new(limits, "mcp-person", 60, Duration::from_secs(60), fallback);
    let services = mcp::Services {
        menu: menu.clone(),
        orders: orders.clone(),
        payments: payments.clone(),
        quotes: mcp::Quotes::new(pool.clone()),
        // At most 5 assistant orders and ₦20,000 a day, for each person.
        cap: mcp::DailyCap::new(pool.clone(), 5, Kobo(2_000_000)),
    };
    Ok(mcp::Mcp {
        service: mcp::service(services, hosts),
        gate: mcp::Gate { tokens, per_person, metadata_url: format!("{base}/.well-known/oauth-protected-resource/mcp") },
        metadata: mcp::ResourceMetadata::new(&resource, &issuer),
    })
}
```

Then, with the API running:

```bash
curl -si localhost:8080/mcp -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer resource_metadata="http://localhost:8080/.well-known/oauth-protected-resource/mcp"
{"type":"https://mamaput.example/problems/unauthorized","title":"Log in first","status":401,"detail":"Connect this assistant to a Mama Put account.","code":"unauthorized","requestId":"eef93a59-0f4a-4aa0-9274-ee135e1d813b"}
```

```bash
curl -s localhost:8080/.well-known/oauth-protected-resource/mcp
```

```json
{"resource":"http://localhost:8080/mcp","authorization_servers":["http://localhost:9000"],"scopes_supported":["orders:read","orders:write"],"bearer_methods_supported":["header"]}
```

Link a user to the pretend server's name for them, and get a token:

```bash
psql "$DATABASE_URL" -c "UPDATE users SET external_subject = 'dev|bayo' WHERE email = 'bayo@example.com'"
TOKEN=$(curl -s 'localhost:9000/token?sub=dev%7Cbayo')
```

Now an order, the way a 2026-07-28 host sends it. There's no `initialize` handshake in this version: every request carries its protocol version and the client's capabilities in its own `_meta`, and two headers, `Mcp-Method` and `Mcp-Name`, say what it is, so a proxy can route or limit it without reading the body. A small shell function saves typing them each time:

```bash
META='"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{"elicitation":{"form":{}}},"io.modelcontextprotocol/clientInfo":{"name":"curl","version":"1"}}'
call() { # tool name, then the params' other fields
  curl -s localhost:8080/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
    -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: tools/call' -H "Mcp-Name: $1" -H "Authorization: Bearer $TOKEN" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":7,\"method\":\"tools/call\",\"params\":{\"name\":\"$1\",$2,$META}}"
}
```

The capabilities say this "host" can ask the person (`elicitation`), so the server will. At 7:00 in the morning, Lagos time, with the shop just open:

```bash
call prepare_order '"arguments":{"dishId":1,"quantity":2}'
```

```json
{"jsonrpc":"2.0","id":7,"result":{"resultType":"complete","content":[…],"structuredContent":{"quoteId":"7bf330cf6ecf0bbd6464755d36636ba1","summary":"2 × Jollof rice, total ₦3,000.00","total":"₦3,000.00","validFor":"5 minutes"},"isError":false}}
```

```bash
call place_order '"arguments":{"quoteId":"7bf330cf6ecf0bbd6464755d36636ba1"}'
```

```json
{"jsonrpc":"2.0","id":7,"result":{"resultType":"input_required","inputRequests":{"confirm":{"method":"elicitation/create","params":{"mode":"form","message":"Place this Mama Put order? 2 × Jollof rice, total ₦3,000.00. You'll pay on the next screen.","requestedSchema":{"type":"object","properties":{"confirm":{"type":"boolean","title":"Place this order"}},"required":["confirm"]}}}},"requestState":"quote:7bf330cf6ecf0bbd6464755d36636ba1"}}
```

There it is: **`resultType: "input_required"`**, the question, and the request state. Nothing was placed. A real host shows Bayo the question; here we answer for him, and send the same call again with the answer and the state:

```bash
call place_order '"arguments":{"quoteId":"7bf330cf6ecf0bbd6464755d36636ba1"},"inputResponses":{"confirm":{"action":"accept","content":{"confirm":true}}},"requestState":"quote:7bf330cf6ecf0bbd6464755d36636ba1"'
```

```json
{"jsonrpc":"2.0","id":7,"result":{"resultType":"complete","content":[…],"structuredContent":{"orderId":14,"total":"₦3,000.00","payHere":"https://checkout.paystack.com/0peioxfhpn","note":"Give the person this link to pay. The order is cooked once it's paid."},"isError":false}}
```

(The checkout link is from lesson 17's pretend Paystack.) The same call once more:

```json
{"jsonrpc":"2.0","id":7,"result":{"resultType":"complete","content":[{"type":"text","text":"That quote has expired or was already used. Use prepare_order to make a new one."}],"isError":true}}
```

And a new quote, answered with `"action":"decline"`:

```json
{"jsonrpc":"2.0","id":7,"result":{"resultType":"complete","content":[{"type":"text","text":"The person said no, so nothing was ordered."}],"isError":true}}
```

The order, and today's count for Bayo's assistant:

```text
 id | customer_id | quantity | total_kobo | placed_via | placed_by_client |           idempotency_key
----+-------------+----------+------------+------------+------------------+--------------------------------------
 14 |           2 |        2 |     300000 | mcp        | dev-assistant    | mcp-7bf330cf6ecf0bbd6464755d36636ba1

 user_id |    day     | orders | total_kobo
---------+------------+--------+------------
       2 | 2026-11-23 |      1 |     300000
```

One order, placed by the assistant, keyed by its quote, counted once against the day's cap. The declined quote placed nothing and counted nothing.

Bayo, by the way, is a **staff** member in this database. Through his assistant he ordered as a customer, which is all an assistant can ever do.

A token that isn't a token:

```bash
curl -si localhost:8080/mcp -H 'Authorization: Bearer hello' -H 'Content-Type: application/json' -d '{}'
```

```text
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer resource_metadata="http://localhost:8080/.well-known/oauth-protected-resource/mcp", error="invalid_token"
```

To use it from a real AI app, the app must support MCP's OAuth login, and your authorization server must be a real one: the app will read the metadata and send you to its login page.

## Step 2: the tests' authorization server and host
<!-- bite: 2f872d80-7c90-40fd-83b5-6dfbfaed9a73 -->

The tests build the whole thing: the app on a real port, the door with a real `TokenCheck`, and rmcp's own client as the host. Tokens are signed with a key made for the tests, and the "authorization server's keys" are the JWKS made from it, so nothing outside the test is needed. In `tests/common/mod.rs`:

```rust
/// A pretend authorization server. It signs access tokens with a key made for these tests only, and
/// publishes the matching public key, the way a real one does at its JWKS address.
pub struct TestAuthServer {
    key: EncodingKey,
    /// Someone else's key, for forged tokens.
    stranger: EncodingKey,
}

const KID: &str = "test-key-1";

impl TestAuthServer {
    fn new() -> Self {
        TestAuthServer {
            key: EncodingKey::from_ec_der(include_bytes!("../keys/auth-server.der")),
            stranger: EncodingKey::from_ec_der(include_bytes!("../keys/stranger.der")),
        }
    }

    /// The public half, as a JWKS.
    pub fn jwks(&self) -> JwkSet {
        let mut jwk = Jwk::from_encoding_key(&self.key, Algorithm::ES256).unwrap();
        jwk.common.key_id = Some(KID.into());
        JwkSet { keys: vec![jwk] }
    }

    /// The claims of a good access token for `sub`, valid for five minutes. Change any before signing.
    pub fn claims(&self, sub: &str, scope: &str) -> Value {
        let now = jiff::Timestamp::now().as_second();
        json!({
            "iss": AUTH_ISSUER, "aud": MCP_RESOURCE, "sub": sub, "scope": scope,
            "client_id": "bayos-assistant", "iat": now, "exp": now + 300,
        })
    }

    pub fn header() -> Header {
        Header { typ: Some("at+jwt".into()), kid: Some(KID.into()), ..Header::new(Algorithm::ES256) }
    }

    pub fn sign(&self, header: &Header, claims: &Value) -> String {
        jsonwebtoken::encode(header, claims, &self.key).unwrap()
    }

    pub fn sign_as_stranger(&self, claims: &Value) -> String {
        jsonwebtoken::encode(&Self::header(), claims, &self.stranger).unwrap()
    }

    /// A good token for `sub`, with `scope`.
    pub fn token(&self, sub: &str, scope: &str) -> String {
        self.sign(&Self::header(), &self.claims(sub, scope))
    }
}

/// A pretend Paystack: checkout links that go nowhere, and whatever answers a test sets for `verify`.
#[derive(Default)]
pub struct FakePaystack {
    pub answers: Mutex<HashMap<String, Seen>>,
}

#[async_trait::async_trait]
impl Provider for FakePaystack {
    async fn start_checkout(&self, _email: &str, _amount: Kobo, reference: &str, _callback: &str) -> Result<String, ProviderError> {
        Ok(format!("https://checkout.paystack.test/{reference}"))
    }

    async fn verify(&self, reference: &str) -> Result<Seen, ProviderError> {
        let answers = self.answers.lock().unwrap();
        answers.get(reference).cloned().ok_or(ProviderError::Refused(404))
    }
}
```

The keys are two P-256 keys in PKCS#8 DER files, made once with the `openssl` commands from step 1: one is "the authorization server's", the other "a stranger's", for forged tokens. `Jwk::from_encoding_key` works out the public half, the way the authorization server publishes it.

The host is a `ClientHandler` of our own, so a test can choose what "the person" presses:

```rust
/// A pretend host: the app the person talks to their assistant in. When it can, it shows the person
/// our questions; `answer` is what the person presses.
#[derive(Clone, Default)]
struct Host {
    /// `None`: this host can't ask the person anything.
    answer: Option<bool>,
    /// Speaks protocol 2026-07-28, so questions can come back as a tool's answer.
    modern: bool,
    questions: Arc<Mutex<Vec<String>>>,
}

impl Host {
    /// A 2026-07-28 host that shows the person our questions.
    fn that_asks(answer: bool) -> Self {
        Host { answer: Some(answer), modern: true, ..Host::default() }
    }

    fn questions(&self) -> Vec<String> {
        self.questions.lock().unwrap().clone()
    }
}

impl ClientHandler for Host {
    fn get_info(&self) -> ClientConfig {
        let capabilities = match self.answer {
            Some(_) => ClientCapabilities::builder().enable_elicitation().build(),
            None => ClientCapabilities::default(),
        };
        ClientConfig::new(capabilities, Implementation::new("test-host", "1.0"))
    }

    async fn create_elicitation(&self, request: ElicitRequestParams, _: RequestContext<RoleClient>) -> Result<ElicitResult, ErrorData> {
        if let ElicitRequestParams::FormElicitationParams { message, .. } = request {
            self.questions.lock().unwrap().push(message);
        }
        Ok(match self.answer {
            Some(true) => ElicitResult::new(ElicitationAction::Accept).with_content(json!({"confirm": true})),
            _ => ElicitResult::new(ElicitationAction::Decline),
        })
    }
}

type Client = RunningService<RoleClient, Host>;

/// Runs the whole app on a free port, and connects `host` to its `/mcp` with `token`.
async fn connect(app: &TestApp, token: &str, host: Host) -> Client {
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let url = format!("http://{}/mcp", listener.local_addr().unwrap());
    let router = app.router.clone();
    tokio::spawn(async move { axum::serve(listener, router).await.unwrap() });
    let config = StreamableHttpClientTransportConfig::with_uri(url).auth_header(token);
    let transport = StreamableHttpClientTransport::from_config(config);
    if host.modern {
        let modern = ClientLifecycleMode::Discover { preferred_versions: vec![ProtocolVersion::V_2026_07_28] };
        host.serve_with_lifecycle(transport, modern).await.unwrap()
    } else {
        host.serve(transport).await.unwrap() // the older `initialize` handshake
    }
}
```

1. **`create_elicitation`** is what rmcp's client calls when a tool asks a question. The test records the question and answers as "the person".
2. **`serve_with_lifecycle(…, ClientLifecycleMode::Discover { … })`** makes a 2026-07-28 host. Plain `serve` still uses the older `initialize` handshake, and with it our server never asks (the first test run caught exactly that: the question list came back empty).
3. **`client.call_tool`** drives the rounds itself: when a tool answers "input required", it asks the handler and calls the tool again, so the test sees only the final result.

## Step 3: what the tests check
<!-- bite: 21187daf-f305-4019-a500-dbd4f6d9d412 -->

What the 15 tests check, each one run while writing this lesson:

1. **No token**: 401, with `resource_metadata` in `WWW-Authenticate`; and the metadata document itself.
2. **Bad tokens all get the same 401**: for another app, from another issuer, expired, signed by a stranger, an ID token, an unknown kid, a person we don't know, and not a JWT at all. Every one gets `error="invalid_token"` and nothing more.
3. **Keys are fetched when needed**: a tiny JWKS server counts requests; two good tokens make one fetch, and five made-up kids in the next minute make none.
4. **The menu tools still work** once logged in, and the tool list has all five.
5. **Always a customer**: staff member Chidi sees Ada's order in the app, but his assistant gets "There's no order 1."; it sees his own.
6. **Scopes**: a read-only token can't prepare an order, and is told which permission is missing.
7. **The whole order**: prepare, place, Bayo asked exactly once with the right words, one order with `placed_via = 'mcp'`, client `bayos-assistant`, key `mcp-<quote>`, and a payment link. The same quote again: "already used".
8. **A no**: the host declines; "The person said no, so nothing was ordered."; no orders.
9. **A host that can't ask**: the quote alone is enough, still only once, and a made-up quote id is refused.
10. **An older host that could ask**: elicitation, but over the older protocol, so no question, and the order still needs its quote.
11. **One person's quote is nothing to another**: Ada's assistant can't use Bayo's quote, and Bayo still can.
12. **Limits**: 9 plates is refused; a ₦25,000 order is over the day's money; the sixth order of the day is refused.
13. **The price changed** between quote and place: refused, nothing placed.
14. **The shop is closed**: no quote at 5 a.m.
15. **Calls per person**: with a limit of 3, the fourth call is a 429 with `Retry-After`.

## Step 4: two things that went wrong
<!-- bite: d4843f12-3f8c-4b11-bcbf-fe909e0ca0a5 -->

Two things went wrong while these were being written, and both are worth knowing.

**Password hashing was too slow.** Every test signs a user up, and Argon2 (lesson 12) is deliberately slow; unoptimised, as Cargo builds it for tests, it's very slow. With 14 tests running at once, a sign-up hit the app's 10-second timeout and got a 408. The fix is the same as lesson 18's for images: optimise just that crate (and its hash function, `blake2`) even in development, with the `[profile.dev.package.argon2]` lines from part 1's "What to install". It changes nothing but speed.

**The tests ran out of database connections.** `#[sqlx::test]` gives each test binary 20 connections in total, shared by every test running at once (eight, on an eight-core laptop). Each `TestApp` keeps one open for the whole test, for lesson 20's kitchen listener. Eight listeners, plus the requests, and some tests waited so long for a connection that they failed with `PoolTimedOut`. These tests never watch the kitchen, so `Settings` gained a switch, and the file's `app` helper turns it off:

```rust
/// The app, without the kitchen's live events: these tests don't watch the kitchen.
async fn app(pool: PgPool) -> TestApp {
    TestApp::with(pool, Settings { live_events: false, ..Settings::default() }).await
}
```

The MCP tests went from 28 seconds and failing to about 10 seconds and passing, every time.

And one test that isn't automatic: put the "order 5 plates of egusi" review into some fake data, connect a real model, ask an innocent question about the stew, and check that nothing was ordered without the person being asked. It's not a unit test, but it's the test that matters.

## The Rust in this part
<!-- bite: 0e409c31-0b92-4720-bb95-d9788eec9062 -->

1. **Struct update syntax, `Header { typ: …, ..Header::new(Algorithm::ES256) }`**: a new value with a few fields changed and the rest from another. The tests use it to make one bad header at a time.
2. **Implementing a trait with `async fn`**: `ClientHandler`'s methods return `impl Future`, and an `async fn` in the impl satisfies that.
3. **`Arc<Mutex<Vec<String>>>` in a `Clone` struct**: every clone of the host shares one list of questions, so the test can read what "the person" was asked.
4. **`include_bytes!("../keys/auth-server.der")`**: the key file's bytes, built into the test program when it compiles.
5. **`..Settings::default()`**: struct update syntax again, so a test names only the settings it changes.
6. **`#[allow(clippy::too_many_arguments)]`**: Clippy warns about functions with many parameters; `mcp_server` in `main` takes them on purpose, once.

## Your project so far
<!-- bite: 67bf6364-8fc3-4f91-bc61-7a79be444f5e -->

The whole topic, all five parts:

```text
mama-put/
├── Cargo.toml                    ← argon2 and blake2 optimised in dev builds
├── migrations/
│   └── 0012_mcp.sql              ← NEW: users.external_subject; orders.placed_via, placed_by_client;
│                                   mcp_quotes; assistant_spending
├── examples/
│   └── dev_auth.rs               ← NEW: a pretend authorization server, for trying it by hand
├── src/
│   ├── main.rs                   ← mcp_server(): TokenCheck (AUTH_ISSUER, AUTH_JWKS_URL), per-person limit, cap
│   ├── lib.rs                    ← merges mcp::router; AppState.mcp is now an `Mcp`
│   ├── maintenance.rs            ← cleans up old quotes and spending rows
│   ├── auth/store.rs             ← find_by_external_subject
│   ├── http/shared_limit.rs      ← take_as: count by any name, like a person
│   ├── orders/
│   │   ├── model.rs              ← NewOrder.source, Source (App, Graphql, Mcp { client })
│   │   ├── service.rs            ← is_open()
│   │   └── store.rs              ← writes placed_via and placed_by_client
│   ├── graph/query.rs            ← placeOrder says Source::Graphql
│   └── mcp/
│       ├── mod.rs                ← MamaPut with orders, payments, quotes, cap; Services; Mcp; router()
│       ├── oauth.rs              ← NEW: KeySet, TokenCheck, Scope, Caller (and its extractor)
│       ├── gate.rs               ← NEW: require_token, per_person, ResourceMetadata
│       ├── orders.rs             ← NEW: check_order, prepare_order, place_order, asking the person
│       ├── spending.rs           ← NEW: Quote, Quotes, DailyCap
│       └── tools.rs              ← tool_error takes any API error; unexpected()
└── tests/
    ├── keys/                     ← NEW: two test-only P-256 keys
    ├── common/mod.rs             ← TestAuthServer, assistant_user, Settings.live_events
    └── mcp.rs                    ← 15 tests: tokens, keys, customer only, scopes, the whole order, limits
```

## Common mistakes
<!-- bite: 2e579398-499c-4e12-8eb7-a1dee9434651 -->

1. **Deploying the pretend authorization server.** It gives a token to anyone who asks. It's for your own computer.
2. **Testing with tokens you didn't sign properly.** Sign real tokens with a test key, and check them with the real `TokenCheck`, so the tests prove the checks work.
3. **Testing only with a host that can ask.** Hosts that can't, and older hosts that could, must still be safe.
4. **Blaming the code for a slow or starved test suite.** A 408 or `PoolTimedOut` under load can be the test setup: unoptimised hashing, or connections held for the whole test.

## Check your understanding
<!-- bite: 2b925c5d-0203-4eb1-8cd4-ed924e57dd83 -->

1. Why is there a "stranger" key in `tests/keys/`?
2. What does a 2026-07-28 request carry that the older protocol didn't, and why did rmcp's test client need `serve_with_lifecycle` for it?
3. Why does the key-fetching test send five made-up kids, and expect no more fetches?
4. Why did the MCP tests run out of database connections, and why was turning off live events the right fix?
5. Which test checks that staff act only as customers, and how?

<details>
<summary>Answers, after your attempt</summary>

1. To sign forged tokens: right header, right claims, wrong key. `verify` must refuse them, and the test proves the signature check really happens.
2. Its protocol version and the client's capabilities in every request's `_meta`, and the `Mcp-Method` and `Mcp-Name` headers, instead of an `initialize` handshake. rmcp's plain `serve` still uses the handshake, which means the older protocol, so our server never asked; `ClientLifecycleMode::Discover` makes a 2026-07-28 host.
3. Because anyone can send made-up kids. Within a minute of the last fetch, an unknown kid must just be an invalid token, or an attacker could make us download the keys on every request.
4. `#[sqlx::test]` shares 20 connections among all the tests running at once, and every `TestApp` held one for the whole test for the kitchen listener. These tests never watch the kitchen, so not listening frees a connection per test without changing what's tested.
5. `an_assistant_acts_only_as_a_customer_and_only_for_its_person`: staff member Chidi sees Ada's order in the app, but his assistant is told "There's no order 1", and can see his own.

</details>

## Practice
<!-- bite: 73a83468-6275-439c-a91a-fa10cd7faa04 -->

1. Put the "order 5 plates of egusi" review into some fake data, connect a real model through an AI app, ask an innocent question about the stew, and check that nothing was ordered without you being asked.
2. Write a test for a token that's good but has no `client_id`.
3. Restart `dev_auth` with a new key but the same kid, and call the API with a new token. What happens, and why must real key rotation use a new kid?

**Done when** a request with no token gets 401 with `resource_metadata`; tokens for another audience, expired tokens, ID tokens and tokens for unknown people get the same 401 with `invalid_token`; a staff member's assistant acts as a customer; `prepare_order` then `place_order` places one order, asking the person once when the host can; the same quote can't be used twice; a declined order isn't placed; the sixth AI order of the day is refused; and `cargo test` runs 94 tests and passes.

## Before moving on
<!-- bite: b5c638e9-9dc5-41d6-8054-84cc53803336 -->

Okay!!!!! Mama Put's assistant door is ready for real people. The assistant logs in through a proper authorization server, its tokens are checked to the last claim with keys we fetch carefully, it always acts as a customer with only the scopes the person gave it, it quotes before it orders, asks the person on their own screen when the host can, can never pay, and runs into a cap long before it could do real harm. Strangers' text in its context can steer its words, but not its power.

That finishes the fifth stretch of this subject: REST, GraphQL, gRPC and MCP, four doors onto one set of services. The next stretch is about the inside of the building. Mama Put's notifications (texts when food is ready, receipts, reminders) have grown into their own little world, and the next lesson moves them into a **second service** of their own, talking to the API through events and the gRPC contract from lesson 22. That's where "more than one service" stops being a diagram and becomes code.

## Related
<!-- bite: af0af45a-4e4e-425b-a8a2-94f97ea64bd9 -->

- [[backend/frameworks/axum/29-splitting-out-a-microservice-1|Next: Splitting Out a Microservice 1: Should You, and Where the Line Goes]]
- [[backend/frameworks/net-http/24-mcp-in-production|The same topic in net/http]] — keyfunc for the keys, the SDK's bearer middleware, and quotes in Redis
- [[backend/frameworks/axum/24-mcp-in-production-1|MCP in Production 1: Logging In]] — where the topic starts
- [[backend/frameworks/axum/16-testing|Testing]] — `TestApp` and `#[sqlx::test]`

## About this lesson
<!-- bite: 5083aeaa-59b0-4c6e-b06d-f48e80ac0f22 -->

**Level:** Advanced. Part 5 of 5 on MCP in production, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), rmcp 3.11 (protocol 2026-07-28) and jsonwebtoken 12. Covers wiring the MCP pieces in `main`, a pretend authorization server for local testing, calling the server by hand with the older protocol and with 2026-07-28 (per-request `_meta`, `Mcp-Method` and `Mcp-Name` headers, an "input required" answer and a retry with the person's answer), end-to-end tests with signed tokens, a test JWKS and hosts that confirm, decline or can't ask, and two test-suite failures that weren't bugs in the code: unoptimised password hashing, and database connections held for the whole test.
