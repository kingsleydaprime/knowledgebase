---
id: 5a6656d2-d36f-4ea1-bd80-a88cb1677390
---

# MCP in Production 2: The Door and the Person's Permissions

**Every call to the MCP server now goes through a door that checks the token and hands the tools the person it's for, and every tool also asks whether the person let this assistant do what it's about to do.**

## Before you start
<!-- bite: 6a4c1a4b-a6cb-4937-868f-d25bd288670a -->

You should have finished [[backend/frameworks/axum/24-mcp-in-production-1|part 1]]: `KeySet` and `TokenCheck` exist, and `verify` turns a good token into a customer `Identity`. This part leans on lesson 7 (problem responses), lesson 12 (`AuthUser`, an extractor) and lesson 13 (the policy inside the services).

After this part you will be able to:

1. Put a token check in front of rmcp, as Axum middleware on a router of its own.
2. Answer a missing or bad token the way MCP clients expect.
3. Pass the person from the HTTP request to the tools, with an rmcp extractor of your own.
4. Check scopes in each tool, on top of the same permissions REST uses.

## Where we stopped
<!-- bite: d7d01769-1a3a-4e14-a094-6f5b9d846a72 -->

Part 1 made `TokenCheck::verify`: give it a token, and it says who the assistant is acting for, or that the token is no good. Two things are missing. Nothing runs it on each request, and the tools can't see its answer. And knowing *who* isn't enough: Bayo may have let one assistant read his orders and not place them.

## Step 1: the door in front of `/mcp`
<!-- bite: 41786096-e641-4984-9c09-64f4cab23f6d -->

`src/mcp/gate.rs` is the middleware that runs before rmcp ever sees a request:

```rust
/// What the door needs.
#[derive(Clone)]
pub struct Gate {
    pub tokens: TokenCheck,
    /// Tool calls per person, shared by every copy of the app.
    pub per_person: SharedLimit,
    /// `https://api.mamaput.ng/.well-known/oauth-protected-resource/mcp`
    pub metadata_url: String,
}

/// Middleware: no good token, no MCP. A good one becomes a `Caller` in the request's extensions.
pub(super) async fn require_token(State(gate): State<Gate>, mut req: Request, next: Next) -> Response {
    let Some(token) = bearer(req.headers()) else {
        return challenge(&gate, None);
    };
    match gate.tokens.verify(token).await {
        Ok(caller) => {
            req.extensions_mut().insert(caller);
            next.run(req).await
        }
        Err(TokenError::Invalid) => challenge(&gate, Some("invalid_token")),
        Err(TokenError::CantCheck) => {
            ApiError::new(StatusCode::SERVICE_UNAVAILABLE, "auth-unavailable", "Can't check tokens", "Try again in a moment.").into_response()
        }
    }
}

/// The token in `Authorization: Bearer <token>`. The word "Bearer" may come in any case.
fn bearer(headers: &HeaderMap) -> Option<&str> {
    let value = headers.get(header::AUTHORIZATION)?.to_str().ok()?;
    let (scheme, token) = value.split_once(' ')?;
    scheme.eq_ignore_ascii_case("bearer").then_some(token.trim())
}

/// 401, with the header that tells an MCP client where to find out how to log in.
fn challenge(gate: &Gate, error: Option<&str>) -> Response {
    let mut value = format!("Bearer resource_metadata=\"{}\"", gate.metadata_url);
    if let Some(error) = error {
        value.push_str(&format!(", error=\"{error}\""));
    }
    let mut response =
        ApiError::new(StatusCode::UNAUTHORIZED, "unauthorized", "Log in first", "Connect this assistant to a Mama Put account.").into_response();
    response.headers_mut().insert(header::WWW_AUTHENTICATE, HeaderValue::from_str(&value).expect("our URL is a valid header"));
    response
}
```

1. **No `Authorization` header: 401 with the `WWW-Authenticate` header from part 1**, so the client knows where to log in.
2. **A bad token: the same 401, plus `error="invalid_token"`.** That's the standard way (RFC 6750) to say "the token you sent is no good". It tells the client to get a new token, not which check failed.
3. **A good token becomes a `Caller` in the request's extensions**, like lesson 12's `AuthUser` but put there by middleware, because rmcp, not an Axum handler, runs next.
4. **"Bearer" in any case.** `Authorization: bearer …` is allowed by the HTTP standard, so `eq_ignore_ascii_case`.

And the 401 still goes through lesson 7's `write_problems`, which keeps the headers set further in: so the body is our usual problem JSON, and the `WWW-Authenticate` header survives.

## Step 2: mounting it
<!-- bite: eb60c721-5e2e-4250-a45d-c8ea58f3ecf7 -->

`src/mcp/mod.rs` now builds `/mcp` as a router of its own:

```rust
/// Everything `/mcp` needs: the server, the door in front of it, and the document that says where to log in.
#[derive(Clone)]
pub struct Mcp {
    pub service: McpService,
    pub gate: Gate,
    pub metadata: ResourceMetadata,
}

/// `/mcp` behind its token and per-person limit, and the public metadata beside it.
pub fn router<S: Clone + Send + Sync + 'static>(mcp: &Mcp) -> Router<S> {
    let gate = mcp.gate.clone();
    Router::new()
        .nest_service("/mcp", mcp.service.clone())
        // Outermost last: the token is checked first, then the person's limit.
        .layer(middleware::from_fn_with_state(gate.clone(), gate::per_person))
        .layer(middleware::from_fn_with_state(gate, gate::require_token))
        .route("/.well-known/oauth-protected-resource/mcp", get(gate::metadata).with_state(mcp.metadata.clone()))
}
```

And `lib.rs` merges it where `nest_service` used to be:

```rust
        // MCP: its own protocol (JSON-RPC), outside the versions, like GraphQL, with its own login.
        .merge(mcp::router(&state.mcp))
```

1. **`.layer` on this small router wraps only its routes**: `/mcp` gets the token check and the per-person limit, and nothing else in the app does. The app's own layers (request IDs, logs, CORS, the timeout, panics) still wrap everything, `/mcp` included.
2. **`.layer(a).layer(b)` puts `b` outside `a`.** So `require_token` runs first, and `per_person` (part 4) runs after it, when it knows who's calling.
3. **The metadata route is added after the layers**, so it isn't behind the token check. It has to be public: it's how a client with no token finds out where to get one. It holds no secrets, and it sets `Access-Control-Allow-Origin: *` so browser-based clients can read it.
4. **`.with_state(mcp.metadata.clone())` on the route itself**, so this one route has its own small state and the router can still merge into the app, whatever the app's state is.

In the Go version of this lesson, `/mcp` had to move off the main router, because Go's login middleware read every Bearer token as one of the app's own. Ours never had that problem: lesson 12 made login an *extractor*, `AuthUser`, that only routes asking for it run. Routes that don't ask never look at the header. So `/mcp` just gets its own two layers.

Now the whole MCP server needs a login, menu tools included. That's simpler, and it means every call has a person to rate-limit. If you also want a menu anyone's assistant can browse without logging in, serve lesson 23's read-only server at a second address, like `/mcp/public`, with no door.

**One rule the MCP spec states outright: never pass this token on.** If a tool needs to call another service (the notifications service in lesson 29, say), it uses *our* credentials for that service (lesson 33), never Bayo's MCP token. A token passed along lets every service it reaches act as Bayo wherever the token works, and its audience check stops meaning anything.

## Step 3: from the request to a tool
<!-- bite: f8f14819-2ed3-4e7a-9533-6f3a4fdfbb30 -->

The tools need the `Caller`. rmcp gives every tool the HTTP request's `Parts` (headers, extensions), and lets a tool take **extractors**, like an Axum handler: values pulled from the call before the tool runs. `Parameters<T>` is one. We write our own:

```rust
/// A tool can take `caller: Caller`, like an Axum handler takes an extractor. `require_token` put it
/// in the HTTP request's extensions; rmcp hands tools that request's `Parts`.
impl<C: AsRequestContext> FromContextPart<C> for Caller {
    fn from_context_part(context: &mut C) -> Result<Self, ErrorData> {
        let parts = context.as_request_context().extensions.get::<Parts>();
        parts
            .and_then(|parts| parts.extensions.get::<Caller>())
            .cloned()
            .ok_or_else(|| ErrorData::internal_error("no caller: require_token must run before the MCP server", None))
    }
}
```

`FromContextPart` is rmcp's version of Axum's `FromRequestParts`. If it's missing, something is wired wrong (the door isn't in front), so it's an internal error, not something the model can fix.

## Step 4: scopes and the same permissions
<!-- bite: f8d96277-8dec-4d75-b1d3-be11b0d11b5b -->

Bayo approved some scopes. The assistant's tools must respect them, **and** Bayo's own permissions from lesson 13 still apply. Both must say yes. In `oauth.rs`:

```rust
/// What the person let an assistant do. Named permissions they approved at the authorization server.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Scope {
    OrdersRead,
    OrdersWrite,
}

impl Scope {
    pub const ALL: [Scope; 2] = [Scope::OrdersRead, Scope::OrdersWrite];

    pub fn as_str(self) -> &'static str {
        match self {
            Scope::OrdersRead => "orders:read",
            Scope::OrdersWrite => "orders:write",
        }
    }
}

/// Who an assistant is acting for, which assistant it is, and what the person let it do.
#[derive(Clone, Debug)]
pub struct Caller {
    pub who: Identity,
    /// The assistant's client id at the authorization server.
    pub client: String,
    scopes: Vec<String>,
}

impl Caller {
    /// The person to act for, if they gave this assistant `scope`. The error is for the model to read.
    pub fn may(&self, scope: Scope) -> Result<Identity, String> {
        if self.scopes.iter().any(|s| s == scope.as_str()) {
            return Ok(self.who);
        }
        Err(format!(
            "This assistant wasn't given the \"{}\" permission on Mama Put. Ask the person to connect it again with that permission.",
            scope.as_str()
        ))
    }
}
```

`may` returns the `Identity` only if the scope is there. Its error is a whole sentence for the model, which can tell Bayo what to do: reconnect the assistant with that permission.

Each tool starts with its scope, then calls the service exactly as REST does. `src/mcp/orders.rs` has three tools; the first:

```rust
    /// Shows one of the person's own Mama Put orders: what's in it, whether it's paid, and whether it's ready.
    #[tool(annotations(title = "Check an order", read_only_hint = true, idempotent_hint = true, open_world_hint = false))]
    async fn check_order(&self, caller: Caller, Parameters(input): Parameters<CheckOrder>) -> Result<Json<OrderSummary>, String> {
        let who = caller.may(Scope::OrdersRead)?;
        // The same call as GET /v2/orders/{id}: someone else's order is "not found".
        let order = self.orders.get(input.order_id, who).await.map_err(|e| tool_error(e, ""))?;
        Ok(Json(self.summary(order).await))
    }
```

`self.orders.get(input.order_id, who)` is the same call as `GET /v2/orders/{id}`. Lesson 13 put the rule inside the service: you see an order if you're staff or it's yours, and someone else's order is "not found". Since `who` is always a customer, an assistant can only ever see its own person's orders, whatever id the model sends. The tool doesn't enforce that; it *can't* get it wrong.

Live, with Bayo's assistant asking about order 13, which is Ada's:

```json
{"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"There's no order 13."}],"isError":true}}
```

Why scopes on top of roles? Because Bayo might connect two assistants: one he trusts to place orders, and one that should only read. Same Bayo, same role, different scopes. **The role says what Bayo can do. The scope says what Bayo let this assistant do.** And a scope can only narrow: no scope gives the assistant more than Bayo has. A token with only `orders:read`, asking to prepare an order:

```json
{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"This assistant wasn't given the \"orders:write\" permission on Mama Put. Ask the person to connect it again with that permission."}],"isError":true}}
```

## The Rust in this part
<!-- bite: e471a0ca-a849-43bb-95f5-d81ab7947b27 -->

1. **Implementing another crate's trait for your type**, `impl<C: AsRequestContext> FromContextPart<C> for Caller`: our own extractor, usable in rmcp's tools like its built-in ones.
2. **Extractors in a tool's parameters**: `caller: Caller, Parameters(input): Parameters<CheckOrder>`. rmcp fills each one from the call before the tool runs, like Axum does for handlers.
3. **`.then_some(value)` on a `bool`**: `Some(value)` if true, `None` if false; `bearer` uses it to return the token only when the scheme is right.
4. **`str::split_once(' ')`**: splits at the first space into two parts, or gives `None` if there's no space.
5. **A route with its own state**, `get(handler).with_state(value)`: the route has what it needs, so the router can merge into an app with any state.
6. **`#[tool_router(router = order_tools)]` and `+` on routers**: two `impl` blocks each make a router, and `Self::menu_tools() + Self::order_tools()` joins them.
7. **`impl Into<ApiError>` as a parameter type**: `tool_error` now takes any error that can become an `ApiError`: menu, order or payment errors alike.

## Your project so far
<!-- bite: d1c7e99e-cc90-4639-ac5e-96f8e39bba85 -->

```text
mama-put/
└── src/
    ├── lib.rs                    ← merges mcp::router where nest_service("/mcp") was; AppState.mcp is an `Mcp`
    └── mcp/
        ├── mod.rs                ← MamaPut gains orders and payments; Services; Mcp; router()
        ├── oauth.rs              ← Scope, Caller, and Caller's rmcp extractor
        ├── gate.rs               ← NEW: Gate, require_token, the 401 challenge, ResourceMetadata
        ├── orders.rs             ← NEW: check_order (prepare_order and place_order come in part 3)
        └── tools.rs              ← tool_error takes any API error; the menu router is `menu_tools`
```

## Common mistakes
<!-- bite: b5d962e3-7cda-4fed-9793-bf36315d87ee -->

1. **Saying why a token failed.** One 401, `invalid_token`, nothing more. And a 503, not a 401, when it's your side that failed.
2. **Putting the metadata route behind the token check.** A client with no token can't find out where to get one.
3. **Scopes instead of permissions.** Both must say yes: the scope for the app, lesson 13's policy for the person.
4. **Checking ownership in the tool.** Call the same service as REST, with the `Identity`, and let it decide. A tool can't forget a rule it never had.
5. **Passing the person's token on to other services.** Use your own service credentials (lesson 33).

## Check your understanding
<!-- bite: 80d00837-b1f9-4ee5-96f4-2589169b3c5b -->

1. Why is every token problem the same 401, while a failed database lookup is a 503?
2. Why did `/mcp` have to move off the main router in Go, but only gain two layers in Axum?
3. In what order do `require_token` and `per_person` run, and how does the code say so?
4. How does a tool get the `Caller` that `require_token` made?
5. Bayo connects two assistants. One should only read his orders. What stops it placing one, and what stops either of them seeing Ada's orders?

<details>
<summary>Answers, after your attempt</summary>

1. The 401 tells an attacker nothing about which check to work on. A failed lookup isn't the token's fault, so it gets a 503 (try again), and the real error goes in our logs. A 401 would make the client think the token was bad, and maybe send Bayo to log in again for nothing.
2. Go's login was a middleware that read every Bearer token as one of the app's own, so an MCP token failed it before reaching the MCP server. Axum's login is an extractor, run only by routes that ask for `AuthUser`, so `/mcp` was never checked by it; it only needed its own token check and limit.
3. `require_token` first, then `per_person`. `.layer(a).layer(b)` puts `b` outside `a`, and `require_token` is added last, so it's outermost.
4. The middleware puts it in the HTTP request's extensions. rmcp hands every tool the request's `Parts`, and our `FromContextPart` impl takes the `Caller` out of them, so a tool just asks for `caller: Caller`.
5. The scope: its token only has `orders:read`, so `caller.may(Scope::OrdersWrite)` refuses. And lesson 13's policy inside `OrderService::get`: Bayo, as a customer, only sees his own orders, whichever assistant asks.

</details>

## Practice
<!-- bite: cccec5cc-659b-4e8a-86c1-651abb2233d7 -->

1. Write a test that the metadata route answers with no token at all, with `Access-Control-Allow-Origin: *`.
2. Add a `my_orders` tool with the `orders:read` scope that lists the person's recent orders. Which service call should it make, so it can't show anyone else's?
3. What would happen if `per_person` were added after `require_token` in the code? Work it out, then try it.

**Done when** you can follow a request from the `Authorization` header to `caller.may(...)` in a tool, and say what answers each kind of bad token gets. The code runs and is tested in part 5.

## Before moving on
<!-- bite: 70511808-38dc-4c0a-a11d-df67c2d3f633 -->

The assistant now arrives as Bayo, a customer, with only the scopes he gave it, and every tool asks the services the same questions REST does. It can read his orders. Next it will want to *place* one, and that's where a misunderstanding costs money. Part 3 builds ordering in three layers, so that a model can never spend Bayo's money on a guess.

## Related
<!-- bite: 8d510e2c-25d2-404c-b1d2-a0d228d03623 -->

- [[backend/frameworks/axum/26-mcp-in-production-3|Next: MCP in Production 3: Quotes and Asking the Person]]
- [[backend/frameworks/axum/24-mcp-in-production-1|MCP in Production 1: Logging In]] — the token check this door runs
- [[backend/frameworks/axum/13-authorization|Authorization]] — the policy that still applies under every scope
- [[backend/frameworks/axum/03-middleware|Middleware]] — how `.layer` wraps routes

## About this lesson
<!-- bite: ac92041f-bd21-4d3f-8c70-03ad3abfca82 -->

**Level:** Advanced. Part 2 of 5 on MCP in production, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), rmcp 3.11 and jsonwebtoken 12. Covers a token-checking middleware in front of rmcp on a router of its own, the 401 challenge with `resource_metadata` and `invalid_token`, a 503 for our own failures, the public protected resource metadata route, why Axum's extractor-based login didn't need `/mcp` moved, never passing tokens on, a custom rmcp extractor that brings the person to the tools, and scopes checked in each tool on top of the services' own policy.
