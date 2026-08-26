# Security Headers and CORS

> **[Intermediate]** · The headers that are nearly free, and the one browser mechanism everybody misunderstands.

## The headers

**A handful of response headers remove entire vulnerability classes**, and most take one line of middleware.

| Header | Does |
|---|---|
| **`Strict-Transport-Security`** | Forces HTTPS for future visits. **Kills SSL-strip** |
| **`Content-Security-Policy`** | Restricts where scripts/styles/images may load from. **The strongest XSS defence** |
| **`X-Content-Type-Options: nosniff`** | Stops the browser guessing content types |
| **`X-Frame-Options` / `frame-ancestors`** | **Prevents clickjacking** |
| **`Referrer-Policy`** | Stops leaking URLs (and tokens in them) to third parties |
| **`Permissions-Policy`** | Disables camera, mic, geolocation by default |
| `Cache-Control: no-store` | On authenticated responses, so shared caches don't retain them |

**Set them centrally.** Helmet (Node), `SecurityHeaders` middleware (.NET), `secure` (Python), or at the reverse proxy → [[devops/08-networking-and-web/README|networking and web]].

## CSP is the one worth effort

**Content-Security-Policy is the difference between an XSS bug and an XSS incident.** Even with a bug, a strict CSP can prevent the injected script from executing.

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-{random}';
  object-src 'none';
  base-uri 'none';
  frame-ancestors 'none'
```

**The trap: `'unsafe-inline'` in `script-src` disables most of the protection.** It's also what nearly every "just make it work" CSP ends up containing, because inline scripts and inline event handlers break otherwise.

**The fix is a per-response nonce** or a hash allowlist. It requires moving inline scripts out — real work, and the reason CSP adoption is patchy.

**Roll it out with `Content-Security-Policy-Report-Only` first**, collect violation reports, then enforce. Enforcing a guessed policy breaks production → [[cybersecurity/04-web-security/04-security-headers-and-same-origin-policy|security headers]].

## CORS — what it is and isn't

**The most misunderstood mechanism in web development.**

**CORS does not protect your server. It protects your users' *other* tabs.**

The **same-origin policy** stops JavaScript on `evil.com` from reading responses from `yourbank.com` using the visitor's cookies. **CORS is how a server opts *out* of that restriction** for origins it trusts.

**Three consequences people get wrong:**

**A CORS error is a browser decision, not a server rejection.** The request often *reached* your server and executed. The browser refused to let the *page* read the response. **Non-browser clients — curl, Postman, another server — are unaffected entirely.**

**So CORS is not access control.** `Access-Control-Allow-Origin: *` on a public read-only API is fine. On an authenticated endpoint it is not — but the fix is authentication, not CORS.

**The preflight.** For anything beyond a simple request (custom headers, `PUT`/`DELETE`, JSON content-type), the browser sends an `OPTIONS` request first and only proceeds if the response permits it. **This is why "it works in Postman but not the browser"** — Postman doesn't preflight.

```
Access-Control-Allow-Origin: https://app.example.com     ← echo a specific origin
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400                             ← cache the preflight
```

**`Allow-Origin: *` and `Allow-Credentials: true` are mutually exclusive** — browsers reject the combination, deliberately. To support credentials you must **echo back a specific allowed origin**, which means validating against an allowlist. **Reflecting whatever `Origin` was sent is a vulnerability**, not a solution.

**Set `Access-Control-Max-Age`** or every request pays a preflight round trip.

## CSRF — a different problem

**Cookies are sent automatically on cross-site requests. That's the vulnerability.**

`evil.com` can submit a form to `yourbank.com/transfer`, and the browser attaches the session cookie. **The attacker can't read the response — and doesn't need to.**

**The defences, and you want more than one:**

**`SameSite` cookies** — `Lax` is the modern browser default and blocks the classic case. **`Strict` for sensitive actions.** This has substantially reduced CSRF, and is not a complete answer for older browsers or non-cookie flows.

**CSRF tokens** — a per-session token in a hidden field or header, verified server-side. Belt and braces with `SameSite`.

**Token in a header, not a cookie** — an `Authorization: Bearer` header is not sent automatically cross-site, so header-based auth is structurally immune to CSRF. **That's a genuine argument for it in SPAs** → [[backend/05-auth/README|auth]].

**Never make a state-changing operation a `GET`.** `GET /delete?id=5` is triggerable by an `<img>` tag on any page.

## Related
- [[backend/06-cross-cutting/03-error-handling|error handling]] — don't leak internals in errors either
- [[cybersecurity/04-web-security/README|web security]] — the depth behind all of this
- [[backend/05-auth/README|auth]] · [[backend/frameworks/cross-language-recipes|cross-language recipes]]

*Source: [reference] — written Aug 2026.*
