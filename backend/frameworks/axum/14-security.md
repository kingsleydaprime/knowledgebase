---
id: 2db551d6-4ef3-4579-927b-3495d56456b9
---

# Security

**Web security, for an API, means assuming every request might come from someone trying to cause harm, and making each kind of harm either impossible or expensive.** Lessons 6, 8, 12 and 13 already closed the big ones: bad input, SQL injection, stolen passwords and reading other people's data. This lesson closes the rest of the common list: the headers browsers use to protect people, CORS, password guessing, trusting the wrong IP address, and files uploaded by strangers. In Axum, most of these are Tower layers from `tower-http`, plus two small pieces of our own.

## Before you start
<!-- bite: bf2427bb-655e-47f6-ae53-52b213f0bd7a -->

You should have:

1. Finished [[backend/frameworks/axum/13-authorization|lesson 13]], so roles and ownership are enforced and `cargo test` passes.
2. Read [[backend/06-cross-cutting/06-security-headers-and-cors|Security Headers and CORS]] and [[backend/06-cross-cutting/04-rate-limiting|Rate Limiting]] if you want the ideas first. Not required.

After this lesson you will be able to:

1. Send the security headers every API response should carry, and a looser set for the one page that needs it.
2. Configure CORS, and say what it does and doesn't protect.
3. Rate-limit the routes that check passwords, with a token bucket per client.
4. Find a client's real address, without trusting what the client says.
5. Accept file uploads safely: size, real type, name and folder.

## What to install
<!-- bite: a8cca210-da4d-47d7-a501-be5ff83f3980 -->

```bash
cargo add tower-http --features timeout,catch-panic,trace,request-id,set-header,cors,fs
cargo add axum --features macros,multipart
```

Three new tower-http features: `set-header` (add headers to every response), `cors`, and `fs` (serve files from a folder). Axum's `multipart` reads the form format browsers and phones use to send files.

## Where we stopped
<!-- bite: 2ac7bcaf-5aae-4eca-b03e-684ef934565b -->

Four holes, each one used on real APIs every day:

1. **Nothing stops someone trying a million passwords.** Lesson 12 made each guess slow, but slow times a million is still doable, and every guess costs us 19 MiB of memory.
2. **Responses don't carry the headers** that tell a browser not to guess file types, not to show our pages inside someone else's, and to use HTTPS.
3. **Any website can try to call us** from a visitor's browser. Today the browser blocks it, by accident, because we never said who's allowed. When the phone team builds a web app, we'll need to say.
4. **The kitchen wants photos of each dish.** That means accepting files from people, and files are where attacks like to hide.

## The kid version
<!-- bite: 19024816-8b44-4972-bd1c-e44d72e8817f -->

Mama's stall now has a few rules that have nothing to do with food.

A sign on the counter says "no photos of the kitchen, no reselling our food under another name" (security headers: what browsers may do with our answers). A list at the gate says which delivery companies may collect on customers' behalf (CORS). Anyone who asks for the till's combination more than ten times in a minute is told to come back later (rate limiting). And when someone hands Mama a "photo of their dish", she looks at what it actually is before pinning it on the wall (upload checks).

**Where the picture stops working.** Mama's list at the gate protects *her*. CORS doesn't protect us at all: it protects visitors, from other websites using their browsers. Someone with `curl` ignores CORS completely, so it's never a replacement for logging in.

## Terms used in this lesson
<!-- bite: e306d650-30af-4f29-bf2b-34b07b9ed6d7 -->

1. **Security headers**: These are response headers that tell the browser how to treat what we send: what it may run, whether it may be framed, whether to guess types.
2. **Origin**: This is the scheme, host and port of a web page: `https://app.mamaput.example`. Browsers keep pages from different origins apart.
3. **CORS**: This stands for **Cross-Origin Resource Sharing**. It's how a server tells browsers which other origins' pages may read its responses.
4. **Preflight**: This is the `OPTIONS` request a browser sends first, asking "may I?", before a cross-origin request that isn't a simple `GET`.
5. **Rate limiting**: This is capping how many requests one client may make in a period.
6. **Token bucket**: This is a rate-limiting method: each client has a bucket of tokens that refills at a steady rate; each request takes one; an empty bucket means wait.
7. **Reverse proxy**: This is a server in front of ours (nginx, Caddy, a cloud load balancer) that receives requests and passes them on. To us, every request then seems to come from the proxy.
8. **Magic bytes**: These are the first few bytes of a file, which say what kind of file it really is, whatever its name says.

## Step 1: security headers
<!-- bite: c3baf3e3-cf4c-4204-a21b-455fe5f1ccf8 -->

An API sends JSON, never web pages. That makes the strictest browser settings free: we lose nothing by forbidding everything. `src/http/security.rs`:

```rust
type SetHeader = SetResponseHeaderLayer<HeaderValue>;

fn set(name: HeaderName, value: &'static str) -> SetHeader {
    SetResponseHeaderLayer::if_not_present(name, HeaderValue::from_static(value))
}

/// For every response. An API sends JSON, never pages, so the strictest settings cost nothing.
pub fn security_headers(router: Router) -> Router {
    router
        // Don't guess a file's type from its contents: a "photo" that's really HTML stays a photo.
        .layer(set(header::X_CONTENT_TYPE_OPTIONS, "nosniff"))
        // Never show our responses inside someone else's page.
        .layer(set(header::X_FRAME_OPTIONS, "DENY"))
        // Load nothing, run nothing, and don't be framed. Pages that need more set their own first.
        .layer(set(header::CONTENT_SECURITY_POLICY, "default-src 'none'; frame-ancestors 'none'"))
        // Don't tell other sites which of our URLs a visitor came from.
        .layer(set(header::REFERRER_POLICY, "no-referrer"))
        // Only ever talk to us over HTTPS, for a year. Browsers ignore it on plain HTTP.
        .layer(set(header::STRICT_TRANSPORT_SECURITY, "max-age=31536000; includeSubDomains"))
}
```

1. **`X-Content-Type-Options: nosniff`** stops the browser "helpfully" deciding that a file we called `image/png` is really HTML and running it. That matters most for uploads (step 5).
2. **`X-Frame-Options: DENY`**, and **`frame-ancestors 'none'`** in the CSP, stop another site showing our pages in an invisible frame and tricking people into clicking (**clickjacking**).
3. **`Content-Security-Policy: default-src 'none'`** says "this response may load and run nothing". If a bug ever let someone's text into a response as HTML, there's nothing it could do.
4. **`Strict-Transport-Security`** (HSTS) tells the browser: for a year, never use plain HTTP to reach this site, even if a link says `http://`. It closes the gap where an attacker on café Wi-Fi intercepts the first, unencrypted request.
5. **`if_not_present`**: a response that already set its own header keeps it. That's how the docs page gets a looser policy.

`app` ends with `http::security_headers(app)`, so they wrap everything, errors included.

### The docs page

`/v2/docs` is the one real web page we serve, and it runs Scalar's script from a CDN. `default-src 'none'` would break it. So that route sets its own policy first:

```rust
/// The docs page is the one real web page we serve. It runs Scalar's script from a CDN.
pub fn docs_headers() -> SetHeader {
    SetResponseHeaderLayer::overriding(
        header::CONTENT_SECURITY_POLICY,
        HeaderValue::from_static(
            "default-src 'none'; script-src https://cdn.jsdelivr.net; style-src 'unsafe-inline' https://cdn.jsdelivr.net \
             https://fonts.scalar.com; font-src https://fonts.scalar.com https://cdn.jsdelivr.net data:; \
             img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none'",
        ),
    )
}
```

applied to that router alone:

```rust
        .merge(Router::from(Scalar::with_url("/v2/docs", docs::ApiDoc::openapi())).layer(http::docs_headers()))
```

Scripts only from `cdn.jsdelivr.net`, requests only back to us. If the page looks broken in a browser, open its console: a CSP refusal says exactly which source it blocked, and you add that one.

One honest worry about this page: the HTML utoipa-scalar writes loads `https://cdn.jsdelivr.net/npm/@scalar/api-reference`, with **no version** in the URL. Whatever that package publishes next runs on our docs page. That's a **supply-chain** risk: our safety depends on someone else's account staying secure. For an internal docs page it's a fair trade; for anything handling secrets, pin the version and add a hash (`integrity="sha384-..."`, called Subresource Integrity), or serve the script yourself (practice 5).

## Step 2: CORS, and what it isn't
<!-- bite: b5be1a43-1728-4727-9028-642053b42b51 -->

A browser keeps pages from different origins apart. A page on `https://evil.example` can *send* a request to our API, but by default the browser won't let it *read* the answer. **CORS** is how we tell the browser which origins may read.

That's all it is. It protects *visitors*: it stops a page they're visiting from using their browser, and whatever it's logged into, against us. It doesn't protect *us*: `curl`, a Python script, or any server ignores CORS completely. Our protection is the login and the policy, not this.

```rust
/// Which websites' pages may call us from a browser, and with what.
pub fn cors(config: &HttpConfig) -> CorsLayer {
    CorsLayer::new()
        .allow_origin(AllowOrigin::list(config.allowed_origins.clone()))
        .allow_methods([Method::GET, Method::POST, Method::PATCH, Method::DELETE])
        .allow_headers([header::AUTHORIZATION, header::CONTENT_TYPE, HeaderName::from_static("idempotency-key")])
        .expose_headers([header::LOCATION, HeaderName::from_static("x-request-id"), header::RETRY_AFTER])
        .max_age(std::time::Duration::from_secs(3600))
}
```

1. **`allow_origin(AllowOrigin::list(...))`**: exactly the web apps we run, from `ALLOWED_ORIGINS`. Never `*` together with credentials, and never "echo back whatever origin asked", which is `*` with extra steps.
2. **`allow_headers`**: the request headers a page may send, including `Authorization` for the token and lesson 15's `Idempotency-Key`.
3. **`expose_headers`**: response headers a page may *read*. By default a page can only see a few, so `Location`, our request id and `Retry-After` must be listed.
4. **`max_age(1 hour)`**: the browser may remember a preflight's answer, instead of asking before every request.

The settings come from the environment, in a small config struct carried in `AppState` as `http`:

```rust
/// Settings for the HTTP edge, read once in `main`.
#[derive(Clone, Debug, Default)]
pub struct HttpConfig {
    /// Websites whose pages may call the API from a browser: `https://app.mamaput.example`.
    pub allowed_origins: Vec<HeaderValue>,
    /// True when a proxy we run sits in front, so X-Forwarded-For can be trusted.
    pub behind_proxy: bool,
}
```

`HttpConfig::from_env` reads `ALLOWED_ORIGINS` (comma-separated) and `BEHIND_PROXY`. For the phone team's web app on their laptops, `.env` gets `ALLOWED_ORIGINS=http://localhost:5173`.

The CORS layer goes early in `app`'s `ServiceBuilder`, right after the request id:

```rust
        .layer(PropagateRequestIdLayer::x_request_id())
        // Before anything can refuse: a browser's preflight `OPTIONS` must get its answer.
        .layer(http::cors(&state.http))
```

A preflight carries no token. If CORS sat inside the login check, the preflight would get a 401, and the browser would never send the real request.

From a run:

```text
$ preflight from the app (origin: http://localhost:5173)
HTTP/1.1 200 OK
access-control-allow-methods: GET,POST,PATCH,DELETE
access-control-allow-headers: authorization,content-type,idempotency-key
access-control-max-age: 3600
access-control-allow-origin: http://localhost:5173

$ preflight from evil.example
HTTP/1.1 200 OK
access-control-allow-methods: GET,POST,PATCH,DELETE
access-control-allow-headers: authorization,content-type,idempotency-key
access-control-max-age: 3600
```

The second is the "no": there's no `access-control-allow-origin`, so the browser refuses to let evil.example's page send the request or read the answer.

## Step 3: rate limiting the password routes
<!-- bite: 943d6117-1545-41ad-a522-ac5370c68130 -->

Each password guess costs an attacker one request, and costs us 19 MiB and tens of milliseconds. So the routes that check a password or a token get a limit: per address, ten at once, then one every six seconds. Plenty for a person who mistyped; useless for a program trying a list of a million passwords.

A **token bucket** in `src/http/rate_limit.rs`:

```rust
#[derive(Clone)]
pub struct RateLimiter {
    behind_proxy: bool,
    burst: f64,
    per: Duration,
    buckets: Arc<Mutex<HashMap<IpAddr, Bucket>>>,
}

struct Bucket {
    tokens: f64,
    updated: Instant,
}
```

```rust
    /// Takes a token for `ip`. `Err` says how long until the next one.
    pub fn check(&self, ip: IpAddr, now: Instant) -> Result<(), Duration> {
        let mut buckets = self.buckets.lock().unwrap();
        if buckets.len() > 10_000 {
            // Forget addresses whose buckets have refilled, so the map can't grow without end.
            let (burst, per) = (self.burst, self.per);
            buckets.retain(|_, b| b.tokens + now.duration_since(b.updated).as_secs_f64() / per.as_secs_f64() < burst);
        }
        let bucket = buckets.entry(ip).or_insert(Bucket { tokens: self.burst, updated: now });
        let refilled = now.duration_since(bucket.updated).as_secs_f64() / self.per.as_secs_f64();
        bucket.tokens = (bucket.tokens + refilled).min(self.burst);
        bucket.updated = now;
        if bucket.tokens >= 1.0 {
            bucket.tokens -= 1.0;
            Ok(())
        } else {
            Err(self.per.mul_f64(1.0 - bucket.tokens))
        }
    }
```

1. **Each address starts with a full bucket** of `burst` tokens. Each request takes one.
2. **Refilling is worked out, not timed.** There's no background task adding tokens. Each time an address is seen, the bucket is topped up by "time since last seen ÷ `per`", up to `burst`. One subtraction per request.
3. **`buckets.entry(ip).or_insert(...)`**: the bucket for this address, made full if it's new.
4. **The map can't grow forever.** Every new address adds an entry; an attacker with many addresses could fill memory. Past 10,000 entries, buckets that have refilled are dropped: a full bucket and no bucket mean the same thing.
5. **It takes `now` as an argument**, the clock idea from lesson 5 again, so the test can step time forward without waiting.
6. **`std::sync::Mutex` is right**: the lock is held for a few arithmetic steps and never across an `.await` (lesson 2).

The middleware:

```rust
/// Middleware: 429 Too Many Requests, with `Retry-After`, once an address runs out.
pub async fn rate_limit(State(limiter): State<RateLimiter>, req: Request, next: Next) -> Response {
    let ClientIp(ip) = ClientIp::of(req.headers(), req.extensions(), limiter.behind_proxy);
    match limiter.check(ip, Instant::now()) {
        Ok(()) => next.run(req).await,
        Err(wait) => {
            let seconds = wait.as_secs() + 1;
            tracing::warn!(%ip, path = req.uri().path(), "rate limited");
            let mut response = ApiError::new(
                StatusCode::TOO_MANY_REQUESTS,
                "rate-limited",
                "Too many requests",
                format!("Slow down. Try again in {seconds} seconds."),
            )
            .into_response();
            response.headers_mut().insert(header::RETRY_AFTER, HeaderValue::from(seconds));
            response
        }
    }
}
```

`Retry-After` tells a well-behaved client exactly when to try again. lesson 7's `write_problems` keeps headers set further in, so it survives the problem being written.

The auth router puts it on the three routes that check something guessable:

```rust
/// `limiter` guards the routes that check a password or a token, so nobody can try millions.
pub fn router<S>(limiter: RateLimiter) -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    AuthService: FromRef<S>,
    Keys: FromRef<S>,
{
    let guessable = Router::new()
        .route("/auth/signup", post(sign_up))
        .route("/auth/login", post(log_in))
        .route("/auth/refresh", post(refresh))
        .route_layer(middleware::from_fn_with_state(limiter, rate_limit));
    guessable
        .route("/auth/logout", post(log_out))
```

and in `main`:

```rust
    // Ten tries at once, then one every six seconds: plenty for a person, useless for a guessing program.
    let login_limiter = RateLimiter::new(10, Duration::from_secs(6), http.behind_proxy);
```

**This limit is per copy of the app**, because the buckets are in memory. Three copies behind a load balancer give an attacker three buckets. That's still a good first defence. A shared limit across copies needs a shared store, like Redis (lesson 19).

## Step 4: who is the client, really?
<!-- bite: d003426c-9ef3-48f0-9b00-938cc5e1c287 -->

The limit is per address. Which address?

Running on its own, the address that connected is the client's. `main` keeps it, by serving with connection info:

```rust
    // `with_connect_info` keeps each connection's address, for `ClientIp`.
    let app = mama_put::app(state).into_make_service_with_connect_info::<SocketAddr>();
    axum::serve(listener, app).with_graceful_shutdown(shutdown_signal()).await?;
```

But in production, Mama Put will sit behind a **reverse proxy** (lesson 36). Then every request "comes from" the proxy, every customer shares one bucket, and the first attacker locks everyone out. Proxies solve this by adding a header, `X-Forwarded-For`, listing the address they saw.

The trap: **anyone can send `X-Forwarded-For`**. A client can write `X-Forwarded-For: 1.2.3.4` itself, and if we believed it, every guess could claim a new address and get a fresh bucket. `src/http/client_ip.rs`:

```rust
impl ClientIp {
    pub fn of(headers: &HeaderMap, extensions: &Extensions, behind_proxy: bool) -> ClientIp {
        // Tests built with `oneshot` have no connection at all.
        let peer = extensions.get::<ConnectInfo<SocketAddr>>().map_or(IpAddr::V4(Ipv4Addr::UNSPECIFIED), |c| c.0.ip());
        if !behind_proxy {
            return ClientIp(peer);
        }
        // Our proxy appends the address it saw to X-Forwarded-For. Anything before that was sent by the
        // client and can be made up, so only the last entry counts.
        let forwarded = headers
            .get_all("x-forwarded-for")
            .iter()
            .filter_map(|v| v.to_str().ok())
            .flat_map(|v| v.split(','))
            .last()
            .and_then(|ip| ip.trim().parse().ok());
        ClientIp(forwarded.unwrap_or(peer))
    }
}
```

1. **Not behind a proxy (the default): the header is ignored completely.** Only the real connection counts.
2. **Behind *our* proxy: only the last entry counts.** A proxy *appends* the address it saw. Whatever the client wrote comes before it, and can be made up; the last entry was written by our proxy.
3. **`BEHIND_PROXY=true` is a promise** that the app can only be reached through that proxy. If the app's port is also open to the internet, anyone can connect directly and send a fake header, and the promise is broken.

`ClientIp` is also an extractor, for handlers that want the address (reading `HttpConfig` from state). The rate limiter has its own state, so it calls `ClientIp::of` directly; both share the same rule.

From a run, twelve wrong logins in a row, each claiming a different `X-Forwarded-For`:

```text
401 401 401 401 401 401 401 401 401 401 429 429
retry-after: 2
{"type":".../problems/rate-limited","title":"Too many requests","status":429,"detail":"Slow down. Try again in 2 seconds.",...}
```

Ten tries, then refused. The made-up addresses bought nothing.

### Size limits and timeouts, once more

Lesson 1's ten-second timeout and lesson 6's 16 KB body limit are security too: they cap what one slow or greedy client can hold. One gap remains from lesson 1: `axum::serve` has no timeout for a client that sends its headers *very* slowly (a **slowloris** attack, holding thousands of connections open for almost nothing). In production, the reverse proxy closes that gap, which is one more reason to have one.

## Step 5: dish photos, uploaded safely
<!-- bite: 14754b3c-f9af-4796-8a6c-3c75d96fadca -->

Accepting files means accepting the most dangerous input there is. Five rules, each closing a known attack:

1. **A size limit for this route alone.** Photos are big; everything else keeps 16 KB.
2. **Check what the file is, from its bytes.** The name (`photo.jpg`) and the type the client claimed (`image/jpeg`) are just text the client chose.
3. **Choose our own name.** A client's file name could be `../../etc/passwd` or `index.html`.
4. **One folder, ours, outside the code.**
5. **Serve it so a browser can't run it**: the right `Content-Type`, `nosniff`, and our strict CSP.

A migration, `0006_dish_photos.sql`:

```sql
-- The file name of each dish's photo, in the uploads folder. Never a path the client chose.
ALTER TABLE dishes ADD COLUMN photo text;
```

`Dish` gains `photo: Option<String>`, every dish query returns it, `MenuStore` gets a `set_photo`, and v2's `DishV2` gains a `photoUrl` (a new optional field: a safe change, lesson 10). `src/menu/photos.rs` does the rest. What a file really is:

```rust
/// The only kinds of file we accept, told apart by their first bytes.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum ImageKind {
    Jpeg,
    Png,
    Webp,
}

impl ImageKind {
    /// What the bytes really are. The file's name and the type the client claimed are never trusted.
    pub fn sniff(bytes: &[u8]) -> Option<ImageKind> {
        match bytes {
            [0xFF, 0xD8, 0xFF, ..] => Some(ImageKind::Jpeg),
            [0x89, b'P', b'N', b'G', 0x0D, 0x0A, 0x1A, 0x0A, ..] => Some(ImageKind::Png),
            [b'R', b'I', b'F', b'F', _, _, _, _, b'W', b'E', b'B', b'P', ..] => Some(ImageKind::Webp),
            _ => None,
        }
    }
```

**Slice patterns** make this readable: `[0xFF, 0xD8, 0xFF, ..]` matches a slice that *starts* with those three bytes (`..` is "anything after"), `b'P'` is the byte for the letter P, and `_` is any one byte. Every JPEG starts `FF D8 FF`; every PNG starts with the same eight bytes; a WebP is `RIFF`, four bytes of length, then `WEBP`. Anything else is refused.

Saving, under a name we choose:

```rust
    /// Saves under a new random name, and returns it. Our name, our extension, our folder.
    pub async fn save(&self, bytes: &[u8], kind: ImageKind) -> std::io::Result<String> {
        let mut random = [0u8; 16];
        getrandom::fill(&mut random).map_err(std::io::Error::other)?;
        let name = format!("{}.{}", hex::encode(random), kind.extension());
        tokio::fs::write(self.dir.join(&name), bytes).await?;
        Ok(name)
    }
```

32 random hex characters and *our* extension, from what the bytes really are. A file called `../../../etc/passwd` becomes `eafaff0845b479a1f33e8d18742a3090.png`. **`tokio::fs::write`** writes without blocking a Tokio worker (it uses the blocking pool underneath, as lesson 12's hashing did).

The route, v2 only, because v1's dishes have no photo field:

```rust
/// `POST /menu/{id}/photo`, for v2 only: v1's dishes have no photo field.
pub fn router<S>() -> Router<S>
where
    S: Clone + Send + Sync + 'static,
    MenuService: FromRef<S>,
    Photos: FromRef<S>,
    Keys: FromRef<S>,
{
    Router::new()
        .route("/menu/{id}/photo", post(upload))
        // This one route may take a big body. Every other route keeps the 16 KB limit.
        .layer(DefaultBodyLimit::max(MAX_PHOTO_BYTES + 64 * 1024))
}

async fn upload(
    _kitchen: Can<MenuWrite>,
    State(menu): State<MenuService>,
    State(photos): State<Photos>,
    Path(id): Path<i64>,
    mut form: Multipart,
) -> Result<Data<DishV2>, ApiError> {
    let field = form.next_field().await.map_err(bad_form)?.ok_or_else(|| no_photo("The form is empty."))?;
    if field.name() != Some("photo") {
        return Err(no_photo("Send the photo in a form field called `photo`."));
    }
    let bytes = field.bytes().await.map_err(bad_form)?;
    if bytes.len() > MAX_PHOTO_BYTES {
        return Err(ApiError::new(StatusCode::PAYLOAD_TOO_LARGE, "photo-too-large", "Photo too large", "At most 2 MB."));
    }
    let kind = ImageKind::sniff(&bytes).ok_or_else(|| {
        ApiError::new(StatusCode::UNSUPPORTED_MEDIA_TYPE, "not-an-image", "Not a photo we take", "Send a JPEG, PNG or WebP.")
    })?;

    menu.get(id).await?; // 404 before anything is written
    let name = photos.save(&bytes, kind).await.map_err(ApiError::internal)?;
    Ok(Data(menu.set_photo(id, &name).await?.into()))
}
```

1. **`DefaultBodyLimit::max(...)` on this router** raises the limit for this route only. The global 16 KB from lesson 6 still applies everywhere else: the inner layer is closer to the handler, so it wins. (The extra 64 KB is room for the form's own wrapping around the file.)
2. **`Multipart`** reads the form one field at a time. It's the last argument: like `Json`, it reads the body.
3. **`Can<MenuWrite>`**: only staff upload. Lesson 13's guard, unchanged.
4. **The dish is checked before the file is written**, so a request for a dish that doesn't exist leaves nothing on disk.

`Photos` is in `AppState`, made in `main` from `UPLOAD_DIR` (default `uploads`, created at start-up with `tokio::fs::create_dir_all`). Add `/uploads` to `.gitignore`. The files are served from that folder, in `app`:

```rust
        .nest_service("/uploads", ServeDir::new(state.photos.dir()))
```

**`ServeDir`** sends files from one folder and nowhere else: it refuses `..` in paths. It sets `Content-Type` from our extension, so a `.png` is always `image/png`, and the security headers from step 1 add `nosniff` and the strict CSP. (In production, photos usually go to object storage, like S3 or Cloudflare R2, served from a separate domain; then a mistake can't touch the API's origin at all. Practice 4.)

From a run:

```text
$ upload a real PNG
{"data":{"id":1,"name":"Jollof rice",...,"photoUrl":"/uploads/eafaff0845b479a1f33e8d18742a3090.png"}}

$ upload HTML named sneaky.jpg, claiming image/jpeg
{"type":".../problems/not-an-image","title":"Not a photo we take","status":415,...}

$ upload 3 MB
{"type":".../problems/bad-form","title":"Form can't be read","status":413,"detail":"Request payload is too large",...}

$ GET /uploads/eafaff0845b479a1f33e8d18742a3090.png
HTTP/1.1 200 OK
content-type: image/png
x-content-type-options: nosniff
content-security-policy: default-src 'none'; frame-ancestors 'none'
```

The sneaky file was HTML with a script in it. Had it been stored as it came, under its own name, a browser might have run it on our domain, with access to whatever our domain can reach. That's why every one of the five rules is there.

The upload route is described in the docs too (a `multipart/form-data` body with one `photo` field), so the docs test checks 16.

## Step 6: the boring things that matter
<!-- bite: 51e7054c-c893-4272-a2d6-ec08b685986c -->

The attacks that actually get most APIs aren't clever. A short list to keep:

1. **Keep dependencies up to date, and check them.** `cargo install cargo-audit`, then `cargo audit` checks every crate in `Cargo.lock` against the RustSec list of known holes. Lesson 37 runs it in CI.
2. **Secrets come from the environment** (`DATABASE_URL`, `JWT_SECRET`, `STAFF_KEY`), never from the code, never in git, and each one is different in each environment.
3. **Errors don't leak**: lesson 7's `ApiError::internal`.
4. **TLS at the edge.** The reverse proxy speaks HTTPS to the world (lesson 36); HSTS makes browsers insist on it.
5. **Log security events** (rate limits, reused refresh tokens, role changes) at `warn` or `info`, with the request id, and look at them.

## The Rust in this lesson
<!-- bite: 1c60a803-b728-4ee6-a887-1d7fc8744376 -->

1. **`SetResponseHeaderLayer::if_not_present` and `::overriding`**: add a header to every response, unless set already, or always.
2. **A function that takes a `Router` and returns it with layers on**, instead of naming a complicated layer type.
3. **`CorsLayer` and `AllowOrigin::list`**.
4. **`Arc<Mutex<HashMap<IpAddr, Bucket>>>`** and **`HashMap::entry(...).or_insert(...)`**: shared state, and "get, or put in and get".
5. **`HashMap::retain`**: drop entries that fail a test.
6. **`std::time::Instant` arithmetic**: `duration_since`, `as_secs_f64`, `Duration::mul_f64`.
7. **`into_make_service_with_connect_info::<SocketAddr>()`** and the **`ConnectInfo`** extension.
8. **`HeaderMap::get_all`**: every value of a header that can appear more than once.
9. **`Iterator::last`**: the final item.
10. **Slice patterns**, `[0xFF, 0xD8, 0xFF, ..]` and `[b'R', b'I', b'F', b'F', _, _, _, _, ...]`.
11. **Byte literals and byte strings**, `b'P'` and `b"RIFF"`.
12. **`Multipart`**, `next_field`, `name()` and `bytes()`.
13. **`tokio::fs::write` and `create_dir_all`**, and **`std::io::Error::other`**.
14. **`ServeDir`** and **`Router::nest_service`**: serve a folder under a path.

## Your project so far
<!-- bite: 59218ef8-3a69-4fe7-a4dd-cf01cb0b4d6f -->

```text
mama-put/
├── .env                   ← + ALLOWED_ORIGINS
├── .gitignore             ← + /uploads
├── Cargo.toml             ← tower-http + set-header, cors, fs; axum + multipart
├── migrations/
│   └── 0006_dish_photos.sql
└── src/
    ├── main.rs            ← HttpConfig, Photos, the login limiter; serve with connect info
    ├── lib.rs             ← AppState.http, .photos, .login_limiter; CORS early; docs CSP; /uploads; security_headers
    ├── docs.rs            ← + upload_photo, PhotoUpload; checks 16
    ├── http/
    │   ├── security.rs    ← HttpConfig, security_headers, docs_headers, cors
    │   ├── rate_limit.rs  ← RateLimiter (token bucket per address), rate_limit middleware; 1 test
    │   └── client_ip.rs   ← ClientIp: the connection, or our proxy's last X-Forwarded-For entry
    ├── auth/handlers.rs   ← signup, login, refresh behind the limiter
    └── menu/
        ├── photos.rs      ← Photos, ImageKind::sniff, the upload route with its own body limit; 1 test
        ├── store.rs       ← photo in every query; set_photo
        └── versions.rs    ← DishV2.photoUrl
```

## Common mistakes
<!-- bite: 33fed192-22f2-4c73-9c99-f18d1a101f5a -->

1. **Thinking CORS protects the API.** It protects visitors' browsers. `curl` doesn't care.
2. **`Access-Control-Allow-Origin: *`, or echoing back any origin.** Every website's pages can read your API with your visitors' browsers.
3. **CORS inside the auth layer.** Preflights carry no token, get a 401, and the browser never sends the real request.
4. **No limit on login.** Slow hashes, multiplied by a million guesses.
5. **Trusting `X-Forwarded-For` from anyone.** Every guess claims a new address.
6. **Trusting an upload's name or `Content-Type`.** Check the bytes; choose the name.
7. **Serving uploads from the API's own origin without `nosniff` and a strict CSP.** A disguised HTML file runs as your site.
8. **One body limit for every route.** Either uploads fail, or every route accepts megabytes.
9. **A rate limiter whose map grows forever.** It becomes the memory attack it was meant to stop.

## Check your understanding
<!-- bite: 1e7819bc-2407-4b42-a696-aab844d42d30 -->

1. Why can an API use `Content-Security-Policy: default-src 'none'` when most websites can't?
2. Who does CORS protect, and from what? Why doesn't it protect the API?
3. Why does the CORS layer sit before anything that can refuse a request?
4. In the token bucket, how are tokens added back, and why is there no background task?
5. Why does the rate limiter's map drop full buckets once it's large?
6. A client sends `X-Forwarded-For: 1.2.3.4`. What does Mama Put do with it, with and without `BEHIND_PROXY`?
7. Name the five upload rules, and an attack each one stops.
8. How does the photo route accept 2 MB when lesson 6 limited bodies to 16 KB?

<details>
<summary>Answers, after your attempt</summary>

1. Because an API only sends JSON, never pages that need scripts, styles or images. Forbidding everything costs nothing, and it means that if a bug ever put someone's text into a response as HTML, there'd be nothing it could load or run.
2. It protects people visiting other websites: it stops a page on another origin from using their browser, and whatever it's logged into, to read our responses. It doesn't protect the API, because CORS is enforced by browsers; `curl`, scripts and servers ignore it.
3. Because a browser's preflight `OPTIONS` request carries no token. If the login check ran first, the preflight would get a 401, and the browser would never send the real request.
4. Each time an address is seen, its bucket is topped up by the time since it was last seen, divided by the refill interval, up to the burst size. Working it out on demand means one sum per request and nothing running in between.
5. Because every new address adds an entry, so an attacker with many addresses could fill memory. A bucket that has refilled to full behaves exactly like no bucket at all, so it can be dropped safely.
6. Without `BEHIND_PROXY`, it's ignored; the connection's address is used. With it, only the last entry counts, the one our proxy added; anything the client wrote comes before it and is ignored.
7. A per-route size limit stops huge uploads filling memory or disk; checking the bytes stops an HTML or script file posing as a photo; our own name stops path tricks like `../../etc/passwd` and overwriting files; one folder of ours keeps uploads away from code and config; serving with the right `Content-Type`, `nosniff` and a strict CSP stops a browser running anything that slipped through.
8. The photo router has its own `DefaultBodyLimit::max(...)` layer. It's closer to the handler than the global 16 KB layer, so it sets the limit that the multipart extractor reads, for that route only.

</details>

## Practice
<!-- bite: c87123a5-4030-4e26-b7b6-a17589d4c46b -->

1. Add `Permissions-Policy: camera=(), microphone=(), geolocation=()` to the security headers. Why does an API bother?
2. Rate-limit `POST /v2/orders` per *user* instead of per address: ten orders a minute. Where does the key come from, and why is per-user better here?
3. When a dish gets a new photo, delete the old file. What happens if the delete fails, and should the request fail too?
4. Upload photos to object storage instead of a folder, with the `object_store` crate and a local MinIO, and send `photoUrl` as a link on another domain.
5. Serve Scalar's script yourself: download a pinned version, serve it from `/v2/docs/scalar.js`, and tighten the docs page's CSP to `script-src 'self'`.

**Done when** every response carries the security headers (the docs page with its own policy), CORS lets only `ALLOWED_ORIGINS` read responses and answers preflights before any auth, signup, login and refresh are rate-limited per real client address, `X-Forwarded-For` is only believed behind our proxy, photos are checked by their bytes, renamed, size-limited on their own route and served with the right type and `nosniff`, and `cargo test` passes.

## Before moving on
<!-- bite: 2e3deef0-aeff-4b16-b197-c23e0e494390 -->

Mama Put now defends itself against the everyday attacks: browsers are told how to protect visitors, only Mama's own web apps may call it from a browser, password guessing is slowed to uselessness, a faked address buys nothing, and a "photo" is a photo or it's refused.

One problem left, and it isn't an attacker. A customer on a bus taps "order". The request reaches us, we take the plate and save the order, and the answer is lost when the bus goes into a tunnel. The app, hearing nothing, tries again, and Ada has two jollofs and one bill. Next lesson: idempotency, with an `Idempotency-Key`, so a retried request happens exactly once.

## Related
<!-- bite: e11e1315-a72c-45ae-a529-d4d4cbfd83a9 -->

- [[backend/frameworks/axum/15-idempotency|Next: Idempotency]]
- [[backend/frameworks/net-http/14-security|The same lesson in net/http]] — headers by hand, x/time/rate, and uploads
- [[backend/06-cross-cutting/06-security-headers-and-cors|Security Headers and CORS]] — the ideas, across languages
- [[backend/06-cross-cutting/04-rate-limiting|Rate Limiting]] — token buckets, windows, and shared limits
- [[backend/06-cross-cutting/07-file-uploads|File Uploads]] — the upload rules in depth

## About this lesson
<!-- bite: 343b5476-4d42-49d1-b9fa-a36e78a67377 -->

**Level:** Advanced. Lesson 14 of the [[backend/frameworks/axum/index|Axum]] subject. Written for Rust 1.85 or later (built and checked with 1.96), Axum 0.8 and tower-http 0.7. Covers `nosniff`, `X-Frame-Options`, a strict CSP, `Referrer-Policy` and HSTS with `SetResponseHeaderLayer`, a looser CSP for the docs page and the supply-chain risk of an unpinned CDN script, CORS with an origin list from the environment placed before any refusal and what CORS does and doesn't protect, a token-bucket rate limiter per address with on-demand refill and a bounded map, finding the client's address from `ConnectInfo` and trusting only our proxy's last `X-Forwarded-For` entry, slowloris and why a proxy helps, and safe uploads: a per-route `DefaultBodyLimit`, magic-byte checks with slice patterns, random names, one folder, `ServeDir`, and serving with the right type, `nosniff` and a strict CSP.
