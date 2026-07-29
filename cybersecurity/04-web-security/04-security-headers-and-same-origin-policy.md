# Security Headers & the Same-Origin Policy

Browsers enforce a set of security rules and honor specific HTTP response headers that let a site opt into stronger protections than the web's default, historically quite permissive, behavior. Understanding these is what turns "the browser handles security" from a vague assumption into a set of specific, checkable controls.

## The Same-Origin Policy (SOP) — the web's foundational isolation rule

By default, a script running on one **origin** (scheme + domain + port, e.g. `https://example.com:443`) cannot read data from a different origin — a page from `evil.com` can't directly read cookies, local storage, or API responses belonging to `bank.com` in the same browser. This one rule is what makes it safe to have many different websites open in the same browser simultaneously without them interfering with each other by default.

## CORS — deliberately, safely relaxing SOP

Sometimes a site legitimately needs to let another origin access its data (a public API meant to be called from other websites' frontend code). **CORS (Cross-Origin Resource Sharing)** is the controlled mechanism for this — the server explicitly states which origins are allowed:

```
Access-Control-Allow-Origin: https://trusted-partner.com
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Credentials: true
```

A common, serious misconfiguration: `Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true` — the wildcard was meant for fully public, non-authenticated APIs, and pairing it with credentialed access effectively lets *any* website read authenticated responses on a logged-in user's behalf. Most browsers and spec-compliant servers now reject this exact combination for that reason, but hand-rolled or misconfigured CORS setups still produce equivalent, narrower mistakes.

## Content Security Policy (CSP) — restricting what a page is allowed to load and run

CSP is a header that tells the browser which sources of scripts, styles, images, and other content are legitimate for a given page — anything not matching the policy is blocked by the browser itself, regardless of how it got onto the page.

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.com; object-src 'none'
```

This directly backstops [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]]'s XSS defenses: even if a malicious `<script>` tag somehow got injected into a page despite proper output encoding, a strict CSP that doesn't allow inline scripts or untrusted script sources means the browser simply won't execute it. Defense in depth — CSP is a mitigation layered on top of fixing the underlying injection, not a substitute for it.

## Other common security headers

- **`X-Frame-Options: DENY`** (or the more flexible `frame-ancestors` CSP directive) — prevents a page from being embedded in an `<iframe>` on another site, which is what stops **clickjacking**: an attacker overlaying an invisible iframe of a legitimate site (e.g. a "confirm transfer" button) under attacker-controlled content, tricking a user into clicking something they didn't intend to on the real site underneath.
- **`X-Content-Type-Options: nosniff`** — stops the browser from guessing ("sniffing") a resource's content type, which can otherwise be tricked into treating an uploaded file as executable script when it was meant to be treated as plain data.
- **`Referrer-Policy`** — controls how much of the current page's URL gets leaked to other sites via the `Referer` header when a user clicks a link — relevant when URLs themselves might contain sensitive information (a session token in a query parameter, for instance, which is itself a design smell to avoid separately).

## Cookies and the same-origin model

`SameSite` is a cookie attribute directly related to this same isolation concern, restricting whether a cookie is sent along with cross-site requests:

```
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict
```

`SameSite=Strict` or `Lax` is what mitigates **CSRF (Cross-Site Request Forgery)** — an attack where a malicious site tricks a logged-in user's browser into submitting a request to a legitimate site the user is authenticated on, riding along on the user's existing session cookie. Combined with `HttpOnly` and `Secure` (covered in [[02-secure-authentication|secure-authentication]]), these three cookie flags address three genuinely distinct risks (script access, cross-site sending, and transmission over plain HTTP) that are easy to conflate into "just set it to be safe" without understanding which flag stops which specific attack.

## Gotchas

- Security headers are a real, meaningful layer, but they're mitigations that assume the underlying application logic (authentication, input handling) is otherwise sound — they reduce the blast radius of certain mistakes, they don't fix broken application logic.
- Overly permissive CSP (`script-src *` or wide use of `'unsafe-inline'`) provides a false sense of security while defeating much of CSP's actual protective value — a CSP has to be genuinely restrictive to be worth having.
- Testing whether these headers are actually present and correctly configured is a routine, easy check in a web security assessment (see [[06-scanning-and-enumeration|scanning-and-enumeration]]) — their absence is a common, low-effort finding.

## Related
- [[01-input-validation-and-output-encoding|input-validation-and-output-encoding]]
- [[02-secure-authentication|secure-authentication]]
- [[03-https-and-tls|https-and-tls]]
