# Networking on Mobile

**[Intermediate]** — designing for a network that is slow, expensive, metered and frequently absent.

## The kid version first

Server-to-server, the network is fast and reliable. **On a phone it's none of those things.**

Latency is hundreds of milliseconds. The connection dies in lifts and tunnels. The user may be paying per megabyte. And the radio itself **costs battery every time you wake it up** — which is why *when* you make requests matters as much as *what* you send.

## The constraints

**Latency dominates.** A cellular round trip is typically 50–300ms; on a poor connection, seconds. **Chattiness is the enemy** — five sequential requests is five round trips, and the user feels every one. One request returning what the screen needs beats five tidy ones.

**The radio has a tail.** Waking the cellular radio keeps it in a high-power state for **seconds after** your transfer finishes. **Ten small requests spread over a minute cost far more battery than one batch** — this is the single most counterintuitive fact about mobile networking, and it's why batching matters more here than anywhere else.

**Bandwidth may be metered.** Both platforms expose whether the connection is metered. **Respect it** — defer large downloads to Wi-Fi.

**Connectivity is not binary.** "Connected to Wi-Fi" doesn't mean "has internet" — captive portals in hotels and airports return login pages for every request. **Check for actual reachability**, not just an interface being up.

## Practical rules

**1. Batch and coalesce.** Combine requests. Debounce user-triggered ones (search-as-you-type is the classic offender). Let the background scheduler batch your syncs → [[mobile/10-background-work-and-push|background work]].

**2. Compress everything.** Gzip/Brotli on responses. **Prefer efficient formats for large payloads** — Protobuf or MessagePack over JSON when size matters.

**3. Paginate, always.** Cursor-based, not offset — data shifts between requests and offset pagination duplicates or skips rows.

**4. Right-size images. This is usually the biggest win available.** Serve device-appropriate resolutions; use modern formats (WebP, AVIF); never download a 4000px image for a 200px thumbnail. **Images are typically the majority of an app's bytes**, and fixing them is often a one-day change with a large measured effect.

**5. Timeouts, retries, backoff.** Short connect timeouts, longer read timeouts. **Retry only idempotent requests**, with exponential backoff and **jitter** — without jitter, every device retries simultaneously when your server recovers and knocks it over again → [[backend/06-cross-cutting/README|retries]].

**6. Cancel work the user walked away from.** Both platforms tie request scopes to lifecycle. Use them.

## The libraries

| Platform | Standard |
|---|---|
| **Android** | **Retrofit + OkHttp** (+ kotlinx.serialization), or Ktor Client |
| **iOS** | **URLSession** (`async/await`), or Alamofire |
| **Flutter** | Dio, or `http` |
| **React Native** | `fetch` + TanStack Query |
| **Images** | **Coil** (Android), **Kingfisher**/AsyncImage (iOS) — use one; they handle caching, downsampling and cancellation |

## API design for mobile clients

**Old app versions live for years**, so:

- **Version your API and never break old clients.** Add fields, don't remove or repurpose them
- **Clients must ignore unknown fields.** Both major serialisation libraries can be configured to do this; **make sure yours is**, or adding a field crashes every existing install
- **Give the client one call per screen where you can.** BFF (backend-for-frontend) or GraphQL exist largely for this — **round trips are the cost, not bytes**
- **Ship a "minimum supported version" endpoint** so you can force an upgrade when you must → [[mobile/13-release-and-distribution|release]]
- **Return structured, actionable errors** — a code the app can branch on, plus a message it can show

## Security on the wire

- **HTTPS only.** Both platforms block cleartext by default now — **do not add an exception to "make it work in dev"**, because that exception ships
- **Certificate pinning** is defence against a compromised CA or a user-installed root cert. **It's a real trade** — a pin that outlives its certificate **bricks your app** for everyone until they update. Pin the intermediate, ship backup pins, and have a kill switch. **Many teams shouldn't do this**
- **No secrets in the app.** An API key in your binary is public — anyone can extract it → [[mobile/12-security-on-device|security]]
- **Don't log request bodies** in release builds. Tokens end up in logs

## Testing for bad networks

**Your office Wi-Fi is lying to you.** Deliberately test on:

- **Network Link Conditioner** (iOS/macOS) — simulate 3G, high latency, packet loss
- **Android emulator network profiles**, or `adb shell svc data disable`
- **Airplane mode mid-request** — the case that finds the most bugs
- **Captive portal** — connect to a hotel-style network

**Test these on every screen that loads data.** "What happens on a bad connection" is the most common untested path in mobile, and it's the everyday experience for a large share of users → [[mobile/07-data-and-offline-first|offline-first]].

## Key insight

**On mobile the expensive thing is the round trip and the radio wake-up, not the bytes** — so batching, caching and fewer-but-larger requests beat the tidy, chatty API design that works fine server-to-server. Design the API for the screen, not for the resource model.

## Related
- [[mobile/07-data-and-offline-first|offline-first]] — where responses go
- [[mobile/11-performance-and-battery|performance and battery]] — the radio tail
- [[foundations/networking/README|networking]] — TCP, TLS and HTTP properly
- [[backend/02-api-design/README|API design]] — the other side of this contract

*Source: [reference] — Aug 2026.*
