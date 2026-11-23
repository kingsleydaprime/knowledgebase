---
id: c9123392-80b3-435c-a0ec-6911aa5b8651
---

# Calling Services Safely 2: Who's Calling?

**Service-to-service authentication means every call between our services carries proof of which service sent it, and the receiving service checks that proof, and what that service may ask for, before anything else runs.**

## Before you start
<!-- bite: 07256339-cba3-4be0-a318-e8b405bcc51a -->

You should have finished [[backend/frameworks/axum/33-calling-services-safely-1|part 1]]: notifications calls the API with deadlines, retries and a breaker. This part leans on lesson 12 (JWTs with the algorithm pinned), lesson 13 (a policy with default deny, and a test that every action has a rule) and lesson 24 (checking tokens from someone else's keys).

After this part you will be able to:

1. Explain why "it's on the internal network" isn't enough.
2. Sign short-lived service tokens with a service's own private key, on every call, without any call able to forget.
3. Check them on the API's gRPC server, per method, before tonic runs anything, with default deny.
4. Prove with a test that every gRPC method has a rule.
5. Say what TLS adds, and apply the same habits to plain HTTP calls.

## Where we stopped
<!-- bite: 150d7cad-e573-40eb-9dd1-c89a8e9af0e0 -->

`GetContact` returns personal data, and right now it trusts anyone who can reach port 50051. On `127.0.0.1` that's only programs on the same machine. But lesson 38 puts each service in its own container on a shared network, and then "the internal network" is anything that gets into any container. One compromised container, one misconfigured firewall, one curious engineer, and every customer's contact details walk out.

The API needs to know **which service** is calling and **what it's allowed to do**. The same idea as users (lessons 12 and 13), for programs.

## Terms used in this part
<!-- bite: 75b5103e-066f-49fd-8903-57fcd5b563a6 -->

1. **Service token**: This is a short-lived JWT a service signs with its own private key and sends with each call, saying who it is and what it may do.
2. **Mutual TLS (mTLS)**: This is TLS where both sides show a certificate, so the connection itself proves which service is on each end.
3. **Default deny**: This means anything without a rule is refused. A new method is closed until someone decides who may call it.

## Step 1: tokens or certificates?
<!-- bite: 878ecb6c-6598-407b-a55d-8eb55f94e89c -->

There are two common approaches, and production systems often use both:

1. **Mutual TLS.** Each service has its own certificate. Both sides check the other's when connecting, so the connection is encrypted *and* each side knows who the other is. Strong, but managing certificates is real work; service meshes like Istio and Linkerd exist largely to do it for you.
2. **Signed service tokens.** Each service has its own private key. With each call, it sends a short-lived JWT, signed with that key, saying who it is and what it may do. The receiver checks the signature with that service's **public** key.

We'll do tokens, because they need nothing new to run and they carry *permissions*, not just identity. The token's shape is shared, so it lives in `contracts/src/service_token.rs`:

```rust
/// Who the tokens are for: the API. A token for the API can't be used anywhere else.
pub const AUDIENCE: &str = "mama-put-api";

/// What a service may ask the API for.
pub const READ_CONTACT: &str = "customers:read-contact";
pub const READ_MENU: &str = "menu:read";

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    /// The calling service's name: `notifications`. It picks which public key checks the signature.
    pub iss: String,
    pub aud: String,
    pub iat: i64,
    pub exp: i64,
    /// Space-separated: `customers:read-contact menu:read`.
    pub scope: String,
}
```

## Step 2: notifications signs
<!-- bite: 1b751034-5bc0-427e-b19e-c26f5ba19253 -->

First, a key pair for notifications, made once:

```bash
mkdir -p keys
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out keys/notifications-private.pem
openssl pkey -in keys/notifications-private.pem -pubout -out keys/notifications-public.pem
```

The private key goes to notifications alone (`NOTIFICATIONS_KEY_FILE` in its `.env`); the public one to the API. **Neither goes in git**: `/keys` is in `.gitignore`. Both crates turn on jsonwebtoken's `use_pem` feature to read them.

`notifications/src/signer.rs`:

```rust
/// How long a token works. A stolen one is useless in minutes.
const LIFETIME: i64 = 120;

#[derive(Clone)]
pub struct Signer {
    service: String,
    scopes: String,
    key: Arc<EncodingKey>,
    /// The token in use, and when it expires: reused until 30 seconds before then.
    current: Arc<Mutex<Option<(String, i64)>>>,
}

impl Signer {
    /// `private_key_pem`: this service's key, which never leaves it. The API holds only the public half.
    pub fn new(service: &str, private_key_pem: &[u8], scopes: &[&str]) -> Result<Self, jsonwebtoken::errors::Error> {
        Ok(Signer {
            service: service.into(),
            scopes: scopes.join(" "),
            key: Arc::new(EncodingKey::from_ec_pem(private_key_pem)?),
            current: Arc::default(),
        })
    }

    pub fn token(&self) -> String {
        let now = SystemTime::now().duration_since(UNIX_EPOCH).expect("after 1970").as_secs() as i64;
        let mut current = self.current.lock().unwrap();
        if let Some((token, expires)) = &*current
            && now < expires - 30
        {
            return token.clone();
        }
        let claims = Claims { iss: self.service.clone(), aud: AUDIENCE.into(), iat: now, exp: now + LIFETIME, scope: self.scopes.clone() };
        // The key id is the service's name: it tells the API which public key to check with.
        let header = Header { kid: Some(self.service.clone()), ..Header::new(Algorithm::ES256) };
        let token = jsonwebtoken::encode(&header, &claims, &self.key).expect("signing with our own key works");
        *current = Some((token.clone(), now + LIFETIME));
        token
    }
}

/// tonic calls this for every request on a client made `with_interceptor(channel, signer)`: no call
/// can forget its token.
impl Interceptor for Signer {
    fn call(&mut self, mut request: Request<()>) -> Result<Request<()>, Status> {
        let value = MetadataValue::try_from(format!("Bearer {}", self.token())).map_err(|_| Status::internal("bad token text"))?;
        request.metadata_mut().insert("authorization", value);
        Ok(request)
    }
}
```

1. **`Interceptor`** is tonic's hook for every request a client sends. `CustomersServiceClient::with_interceptor(channel, signer)` (in `GrpcApi::new`) puts the signer on the client, so **every** call carries a token. No call can forget it.
2. **Tokens last 2 minutes**, and `token()` reuses one until 30 seconds before it expires: signing is cheap, but not free, and nobody needs a fresh token per call. The `Mutex` makes that safe from many tasks; `Arc` shares it between the two clients.
3. **The key id is the service's name**, and so is the issuer. The API uses the key id to pick which public key to check with.
4. **The scopes are what notifications needs**: `customers:read-contact` and `menu:read`, from `main`.

## Step 3: the API checks
<!-- bite: c9bb9e91-3344-4e49-8c76-ede0c237b957 -->

Where should the check go? tonic has server interceptors too, but an interceptor only sees the request's metadata, not **which method** is being called, and our rules are per method. One layer lower, a gRPC call is just an HTTP/2 request whose path *is* the method: `/mamaput.customers.v1.CustomersService/GetContact`. So the check is a Tower layer, tower-http's **`ValidateRequestHeaderLayer::custom`**, which gets the whole HTTP request before tonic does. `src/grpc/service_auth.rs`:

```rust
/// Every gRPC method, and the scope a caller needs for it. `""`: no token needed. A method that
/// isn't here is refused: lesson 13's default deny, for programs.
pub const RULES: &[(&str, &str)] = &[
    ("/mamaput.customers.v1.CustomersService/GetContact", READ_CONTACT),
    ("/mamaput.menu.v1.MenuService/GetDish", READ_MENU),
    ("/mamaput.menu.v1.MenuService/BatchGetDishes", READ_MENU),
    ("/mamaput.menu.v1.MenuService/WatchPortions", READ_MENU),
    ("/grpc.health.v1.Health/Check", ""),
    ("/grpc.health.v1.Health/Watch", ""),
    // Only served while developing (lesson 22), for grpcurl.
    ("/grpc.reflection.v1.ServerReflection/ServerReflectionInfo", ""),
];

/// The service making this call, as proved by its token. Handlers find it in the request's extensions.
#[derive(Clone, Debug, PartialEq)]
pub struct ServiceCaller {
    pub service: String,
}

/// Each calling service's PUBLIC key, by name. They can check signatures, never make them.
#[derive(Clone)]
pub struct ServiceCheck {
    keys: Arc<HashMap<String, DecodingKey>>,
}

impl ServiceCheck {
    pub fn new(public_keys_pem: &[(&str, &[u8])]) -> Result<Self, jsonwebtoken::errors::Error> {
        let mut keys = HashMap::new();
        for (service, pem) in public_keys_pem {
            keys.insert(service.to_string(), DecodingKey::from_ec_pem(pem)?);
        }
        Ok(ServiceCheck { keys: Arc::new(keys) })
    }

    /// The caller, if `authorization` holds a good token with `scope`.
    fn caller(&self, authorization: Option<&str>, scope: &str) -> Result<ServiceCaller, Status> {
        let no_token = || Status::unauthenticated("a service token is required");
        let bad = || Status::unauthenticated("the service token is not valid");
        let token = authorization.and_then(|v| v.strip_prefix("Bearer ")).ok_or_else(no_token)?;
        // The key id names the service. It's only a hint about which key to check with: a token that
        // says "notifications" but wasn't signed with notifications' key fails the signature check.
        let kid = decode_header(token).map_err(|_| bad())?.kid.ok_or_else(bad)?;
        let key = self.keys.get(&kid).ok_or_else(bad)?;
        let mut validation = Validation::new(Algorithm::ES256);
        validation.set_audience(&[AUDIENCE]);
        validation.set_required_spec_claims(&["exp", "iat", "aud", "iss"]);
        validation.leeway = 10;
        let claims = decode::<Claims>(token, key, &validation).map_err(|_| bad())?.claims;
        if claims.iss != kid {
            return Err(bad());
        }
        if !claims.scope.split_whitespace().any(|s| s == scope) {
            return Err(Status::permission_denied("this service may not call this method"));
        }
        Ok(ServiceCaller { service: claims.iss })
    }
}

/// tower-http runs this on every request before tonic sees it. It's the HTTP request, so the method's
/// path is there, which tonic's own interceptors can't see.
impl<B> ValidateRequest<B> for ServiceCheck {
    type ResponseBody = tonic::body::Body;

    fn validate(&mut self, request: &mut Request<B>) -> Result<(), Response<Self::ResponseBody>> {
        let path = request.uri().path();
        let Some((_, scope)) = RULES.iter().find(|(method, _)| *method == path) else {
            return Err(Status::permission_denied("this service may not call this method").into_http());
        };
        if scope.is_empty() {
            return Ok(());
        }
        let authorization = request.headers().get(header::AUTHORIZATION).and_then(|v| v.to_str().ok());
        match self.caller(authorization, scope) {
            Ok(caller) => {
                request.extensions_mut().insert(caller);
                Ok(())
            }
            Err(status) => {
                tracing::warn!(method = path, code = ?status.code(), "service call refused");
                Err(status.into_http())
            }
        }
    }
}
```

And in `grpc::serve`, right after the request log, so a refused call is still logged:

```rust
        // No call runs longer than 10 seconds, whatever deadline the caller sent; a shorter one wins.
        .timeout(Duration::from_secs(10))
        // The same Tower layers as the HTTP side: one log line per call.
        .layer(TraceLayer::new_for_grpc().on_response(DefaultOnResponse::new().level(Level::INFO)))
        // Then, before anything else runs: which service is calling, and may it call this method?
        .layer(ValidateRequestHeaderLayer::custom(check))
```

What this gives us:

1. **Only services we know** (whose public key is in the API's settings) can call at all.
2. **Each service only does what it's allowed.** Notifications has `customers:read-contact` and `menu:read`. A future reporting service might get `menu:read` only, and asking for a contact gives `PERMISSION_DENIED`.
3. **A method with no rule is refused.** Lesson 13's default deny, again. Add an RPC to a `.proto` and forget its rule, and it's closed, not open.
4. **Tokens are short-lived**, so a stolen token is useless in minutes.
5. **The private key never leaves its service.** The API holds only public keys, which can't sign anything. If the API were broken into, the attacker still couldn't pretend to be notifications.
6. **Audience again** (lessons 12 and 24): a token for `mama-put-api` can't be replayed at some other service.
7. **The caller reaches the handler.** `ServiceCaller` goes into the request's extensions, and tonic hands those to the handler. `CustomersApi` logs it:

```rust
        // Who's asking, from their token: the record you want when someone asks who has seen their data.
        let caller = request.extensions().get::<ServiceCaller>().map(|c| c.service.clone()).unwrap_or_default();
        let id = request.into_inner().customer_id;
        tracing::info!(service = %caller, customer_id = id, "contact details read");
```

"notifications read customer 7's contact" is exactly the record you want when someone asks who has seen their data.

Two details:

1. **The key id is read before the token is checked.** That's safe because it only *chooses* a key. If someone writes `"kid": "notifications"` on a token they signed themselves, the signature check against notifications' real public key fails. And `claims.iss != kid` refuses a token signed by one service claiming to be another.
2. **`Status::into_http()`** turns a gRPC error into the HTTP response tonic would have sent, with the code in the `grpc-status` header, so the client sees a normal `UNAUTHENTICATED` or `PERMISSION_DENIED`.

The API reads its known services from one setting, in `main.rs`:

```rust
/// The services allowed to call us over gRPC, and their public keys:
/// SERVICE_KEYS=notifications=keys/notifications-public.pem (more, separated by commas).
fn service_check() -> Result<grpc::ServiceCheck, Box<dyn std::error::Error>> {
    let mut keys = Vec::new();
    for entry in env("SERVICE_KEYS")?.split(',') {
        let (service, path) = entry.split_once('=').ok_or("SERVICE_KEYS entries look like name=path")?;
        keys.push((service.trim().to_owned(), std::fs::read(path.trim())?));
    }
    let keys: Vec<(&str, &[u8])> = keys.iter().map(|(s, k)| (s.as_str(), k.as_slice())).collect();
    Ok(grpc::ServiceCheck::new(&keys)?)
}
```

```bash
SERVICE_KEYS=notifications=keys/notifications-public.pem
```

To change a key: add the new public key to the API under a second name (`notifications-2`), move notifications to the new private key and that name, then remove the old public key.

## Step 4: every method has a rule
<!-- bite: e1ee5669-614a-46cb-a328-0bf011f73da3 -->

Default deny keeps a forgotten method closed. A test makes the gap *visible*, before someone wonders why their new call is refused. Every gRPC service compiles to a descriptor set (lesson 22 kept ours for reflection), which lists every service and method. In `tests/grpc.rs`:

```rust
/// Every method the server offers has a rule, and every rule is for a real method. A method added
/// without a rule is refused (default deny); this test makes the gap visible instead.
#[test]
fn every_grpc_method_has_a_rule() {
    let sets = [grpc::pb::FILE_DESCRIPTOR_SET, tonic_health::pb::FILE_DESCRIPTOR_SET, tonic_reflection::pb::v1::FILE_DESCRIPTOR_SET];
    let mut methods = Vec::new();
    for set in sets {
        for file in prost_types::FileDescriptorSet::decode(set).unwrap().file {
            for service in &file.service {
                for method in &service.method {
                    methods.push(format!("/{}.{}/{}", file.package(), service.name(), method.name()));
                }
            }
        }
    }
    for method in &methods {
        assert!(RULES.iter().any(|(m, _)| m == method), "no rule for {method}");
    }
    for (rule, _) in RULES {
        assert!(methods.iter().any(|m| m == rule), "a rule for a method that doesn't exist: {rule}");
    }
}
```

It checks both ways: every method has a rule, and every rule is for a real method (a rule left behind after a method is renamed is a sign something's wrong). I removed the `WatchPortions` rule to see it work:

```text
thread 'every_grpc_method_has_a_rule' panicked at tests/grpc.rs:206:9:
no rule for /mamaput.menu.v1.MenuService/WatchPortions
```

It's lesson 13's "every action has a rule" test, for programs.

And the refusals, through a real connection:

```rust
#[sqlx::test]
async fn only_our_services_with_the_right_scope_get_in(pool: PgPool) {
    let app = TestApp::new(pool).await;
    let (_, address) = client(&app).await;
    let both = format!("{READ_CONTACT} {READ_MENU}");
    let refused = [
        ("no token", None, Code::Unauthenticated),
        ("someone else's key", Some(token(STRANGER_KEY, "notifications", &both, 120)), Code::Unauthenticated),
        ("a service we don't know", Some(token(SERVICE_KEY, "reports", &both, 120)), Code::Unauthenticated),
        ("expired", Some(token(SERVICE_KEY, "notifications", &both, -60)), Code::Unauthenticated),
        ("allowed the menu, not contacts", Some(token(SERVICE_KEY, "notifications", READ_MENU, 120)), Code::PermissionDenied),
    ];
    for (why, token, code) in refused {
        let mut customers = customers_client(&address, Bearer(token)).await;
        let answer = customers.get_contact(GetContactRequest { customer_id: 1 }).await.unwrap_err();
        assert_eq!(answer.code(), code, "{why}: {}", answer.message());
    }
}
```

No token, someone else's key, a service we don't know, and an expired token are all `UNAUTHENTICATED` with the same plain message; a good token without the scope is `PERMISSION_DENIED`. The health check still needs no token (its test connects without one). The other gRPC tests now sign as notifications, with a key made for the tests in `tests/keys/`.

## Step 5: trying it
<!-- bite: 7a32542c-edf3-4e47-80c1-94e5790a0a98 -->

Lesson 22's example client is a service too now, so it signs with notifications' development key (`examples/menu_client.rs`):

```bash
cargo run --example menu_client -- 4
```

```text
Some(
    Dish {
        id: 4,
        name: "Moi moi",
```

And when notifications asks for contact details during part 1's live run, the API's log says who:

```text
INFO mama_put::grpc::customers: contact details read service=notifications customer_id=6
```

## Step 6: encrypting the traffic
<!-- bite: 8c05a33f-7f9c-40ee-b991-2b64bfcb0d93 -->

Tokens prove who's calling, but over a plain connection anyone who can watch the network can read the token and the contact details as they pass. In production, turn on TLS for gRPC (tonic's `tls-ring` feature):

```rust
// the API's gRPC server
let identity = Identity::from_pem(std::fs::read("api-grpc.crt")?, std::fs::read("api-grpc.key")?);
Server::builder().tls_config(ServerTlsConfig::new().identity(identity))?

// notifications' client
let ca = Certificate::from_pem(std::fs::read("internal-ca.crt")?);
Endpoint::from_shared("https://api:50051")?.tls_config(ClientTlsConfig::new().ca_certificate(ca).domain_name("api"))?
```

For **mutual TLS**, the server's config also gets `.client_ca_root(...)` and the client presents a certificate of its own; then the connection itself proves which service is on the other end, and the token adds the permissions. Where certificates come from (an internal certificate authority, or a service mesh that hands them out) is an operations choice. In lesson 38's Docker Compose, the services share a private network nothing outside can reach, and that's a reasonable place to stop for Mama Put.

## Step 7: the same habits for HTTP calls
<!-- bite: 2f584896-b4f3-4012-b49a-79d78d87ff39 -->

Everything in both parts applies to plain HTTP calls too, like lesson 17's calls to Paystack:

1. **Deadline**: lesson 17's client already had an 8-second timeout, under the app's own 10.
2. **Retries**: only for safe calls. Paystack's `verify` is a read, so a retry is fine; `initialize` creates a transaction, so a blind retry could create two. Lesson 17 gave each checkout attempt its own reference, so a retried `initialize` is a new attempt, not a double charge, but there's still no reason to make two.
3. **Circuit breaker**: part 1's `Breaker` would fit, counting 5xx answers and timeouts, not 4xx (part 1's practice). When Paystack is down, `start_checkout` answers 502 at once instead of making every customer wait 8 seconds for the same failure.
4. **Fallback**: there's no fallback for taking money. Fail fast and say so clearly.
5. **Lesson 17's outgoing webhooks** already had backoff with jitter, and a queue in Postgres, so a slow Okada Riders never holds anything up. That was this topic, early.

## The Rust in this part
<!-- bite: 0a064b21-b6dc-43f7-8964-9061a6e4b908 -->

1. **`tonic::service::Interceptor`**, and `Client::with_interceptor(channel, signer)`: a hook run for every request a client sends. The client's type becomes `CustomersServiceClient<InterceptedService<Channel, Signer>>`.
2. **`MetadataValue::try_from(String)`**: gRPC metadata must be valid header text, so making a value can fail.
3. **Implementing a trait from another crate generically**, `impl<B> ValidateRequest<B> for ServiceCheck`: our check works for any request body type tonic uses.
4. **`request.extensions_mut().insert(caller)`**: data travels with the request from the layer to the handler, by its type.
5. **A `const` slice of tuples**, `RULES: &[(&str, &str)]`: a table built into the program, searched with `.iter().find(...)`.
6. **`prost_types::FileDescriptorSet::decode(bytes)`**: reads a compiled descriptor set, to list every service and method.
7. **`Header { kid: Some(...), ..Header::new(Algorithm::ES256) }`**: struct update syntax, again, for a header with a key id.
8. **`EncodingKey::from_ec_pem` / `DecodingKey::from_ec_pem`**: keys read from the PEM files `openssl` writes (jsonwebtoken's `use_pem` feature).

## Your project so far
<!-- bite: f8edc033-19d8-4f83-a756-fd1949f9ee28 -->

The whole topic, both parts:

```text
mama-put/
├── .gitignore                    ← /keys
├── .env                          ← SERVICE_KEYS
├── keys/                         ← NEW, not in git: notifications-private.pem, notifications-public.pem
├── Cargo.toml                    ← jsonwebtoken use_pem; tower-http validate-request; prost-types (tests)
├── contracts/src/service_token.rs   ← NEW: Claims, AUDIENCE, the scopes
├── examples/menu_client.rs       ← signs as notifications
├── src/
│   ├── main.rs                   ← service_check() from SERVICE_KEYS
│   └── grpc/
│       ├── service_auth.rs       ← NEW: RULES, ServiceCheck (a ValidateRequest), ServiceCaller
│       ├── mod.rs                ← the check, right after the request log
│       └── customers.rs          ← logs which service read whose contact
├── tests/
│   ├── keys/                     ← service.pem, service-public.pem, stranger-service.pem: for tests only
│   └── grpc.rs                   ← signed clients; refusals; every method has a rule
└── notifications/
    ├── .env                      ← NOTIFICATIONS_KEY_FILE
    └── src/
        ├── signer.rs             ← NEW: Signer, an Interceptor
        ├── resilience.rs         ← part 1
        └── api.rs                ← clients with the signer; part 1's deadline, retries, breakers and fallback
```

## Common mistakes
<!-- bite: 595c803b-4945-4f57-b7f7-a16348ad0f8c -->

1. **Trusting the internal network.** One compromised container reaches everything on it. Make every call prove who it's from.
2. **Checking in a tonic interceptor and wanting per-method rules.** It can't see the method. Check in a Tower layer, where the path is the method.
3. **One shared secret for every service.** Any of them could pretend to be any other. A key pair per service, and the receiver holds only public keys.
4. **Long-lived service tokens.** A stolen one works for as long as it lives. Minutes.
5. **A rule list with no completeness test.** Default deny keeps gaps closed; the test makes them visible.
6. **Keys in git.** Make them, keep them in `keys/` (ignored), and give each service only its own.
7. **Tokens over a plain connection on a shared network.** Turn on TLS before the network isn't yours alone.

## Check your understanding
<!-- bite: 50e9338e-075f-4c6b-8068-f7afc55c91ce -->

1. Why isn't "it's only reachable on the internal network" enough for `GetContact`?
2. Why is the check a Tower layer and not a tonic interceptor?
3. Someone signs a token with their own key and writes `"kid": "notifications"`. What happens?
4. A new method, `DeleteCustomer`, is added to `customers.proto`, and nobody adds a rule. What happens to calls, and to the tests?
5. If the API were broken into, could the attacker call other services as notifications? Why?

<details>
<summary>Answers, after your attempt</summary>

1. Anything that gets onto that network (a compromised container, a misconfigured firewall, a curious engineer) could ask for every customer's contact details. Each call should prove which service sent it, and that service should be allowed to ask.
2. A tonic interceptor sees the request's metadata but not which method is being called, and our rules are per method. A Tower layer sees the whole HTTP request, whose path is the method.
3. The key id only chooses which public key to check with: notifications'. Their signature doesn't match it, so the token is refused, `UNAUTHENTICATED`.
4. Every call to it is refused, `PERMISSION_DENIED`, because a method with no rule is denied. And `every_grpc_method_has_a_rule` fails, naming `DeleteCustomer`, so nobody ships it without deciding who may call it.
5. No. The API holds only notifications' public key, which can check signatures but not make them. Notifications' private key never leaves notifications.

</details>

## Practice
<!-- bite: 84df0bd6-10b8-48b8-8650-0478c38858d8 -->

1. Add a "reports" service with `menu:read` only, with its own key pair, and test that it can read the menu but gets `PERMISSION_DENIED` for contacts.
2. Change keys the safe way, step by step: add `notifications-2`'s public key, move notifications to it, remove the old one. Check nothing is refused along the way.
3. Turn on TLS for the gRPC port with a certificate you make with `openssl`, and connect notifications over `https://`.

**Done when** every gRPC call carries a token, the refusal test and the rule-completeness test pass, the example client gets its dish, and the API's log names the service that read each contact; and `cargo test --workspace` runs 111 tests and passes, with NATS running.

## Before moving on
<!-- bite: 62f0afd2-9136-4bbe-9544-439c8e5969e9 -->

Two services now call each other the way strangers who trust each other should: with proof of who they are, only for what they're allowed, never waiting long, and backing off when the other side struggles. But look at how part 1's live run was understood: by reading two services' logs side by side and matching times by eye. With five services, or fifty requests a second, that stops working. Following one request through every program it touches, and knowing something's wrong before a customer tells you, is observability. That's the next lesson.

## Related
<!-- bite: e0052e10-a4e2-4e2a-9a09-59ceab72b764 -->

- [[backend/frameworks/axum/35-observability-1|Next: Observability 1: Logs]]
- [[backend/frameworks/net-http/26-calling-services-safely|The same topic in net/http]] — `PerRPCCredentials` and interceptors that can see the method
- [[backend/frameworks/axum/13-authorization|Authorization]] — default deny, and a test that every action has a rule
- [[backend/frameworks/axum/24-mcp-in-production-1|MCP in Production 1]] — checking tokens from someone else's keys

## About this lesson
<!-- bite: 0922c7e0-792d-488c-82e9-b1958029e2e1 -->

**Level:** Advanced. Part 2 of 2 on calling services safely, in the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.88 or later (built and checked with 1.96), tonic 0.14, tower-http 0.7 and jsonwebtoken 12. Covers why the internal network isn't a boundary, mutual TLS versus signed service tokens, a key pair per service with only public keys on the receiver, a tonic `Interceptor` that signs every call with short-lived cached tokens, a per-method check as a tower-http `ValidateRequest` layer because interceptors can't see the method, default deny with a completeness test built from descriptor sets, the caller passed to handlers through extensions, key rotation, TLS and mutual TLS, and the same habits for plain HTTP calls.
