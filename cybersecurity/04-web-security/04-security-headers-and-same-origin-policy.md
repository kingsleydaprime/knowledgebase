# Security Headers & the Same-Origin Policy

> **[Beginner→Intermediate]** · Browsers enforce rules that keep websites from reading each other's data, and they'll enforce more if you ask with the right response headers. This lesson covers the same-origin policy, CORS and its most common misconfiguration, CSP, the cookie flags, and CSRF — and turns "the browser handles security" into a list of things you can check.

## Before you start

You can already:

- Set response headers on an HTTP server, and explain what a cookie is.
- Explain XSS and why output is encoded → [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation and output encoding]], this week's other core lesson.

After this lesson you will be able to:

1. Say what an origin is, and what the same-origin policy does and doesn't stop.
2. Configure CORS with an allowlist, and recognise the reflected-origin misconfiguration.
3. Explain why CORS is not access control.
4. Set CSP, the other security headers, and the three cookie flags, and say which attack each one stops.

**Study route.** The kid version and §1–6, then the worked example. The practice task completes SWE 101's week 7 milestone, the threat model.

## The kid version

In a block of flats, every flat has its own lock. Your neighbour can't walk in and read your letters, even though you share a building — that's the **same-origin policy**: each website is a flat, and the browser is the building that keeps them apart.

Sometimes you *want* a neighbour to collect your parcels, so you leave a note at the front desk: "Flat 4B may collect mine." That note is **CORS**. The danger is a careless note — "anyone who asks may collect my parcels" — which is the misconfiguration this lesson's lab demonstrates.

**Where the analogy stops working.** The building's rules only apply to people *inside the building*. Someone standing in the street with a crowbar — a script, `curl`, an attacker's server — ignores the front desk completely. The browser's rules protect **users from other websites**; they don't protect **your server** from anyone. Your server still has to check who's asking.

## 1. Why this exists

A user is logged into their bank in one tab and visits a malicious site in another. Without browser rules, that site's JavaScript could call the bank's API — the browser would send the bank's cookie along — and read the account details. The same-origin policy is why it can't. But then a developer, fixing a CORS error in development, configures the API to allow *whatever origin asks*, with credentials. The protection is gone, and nothing visibly broke. **These headers are the difference, and they're invisible unless you check for them.**

## Terms used in this lesson

1. **Origin**: This is the combination of scheme, host and port — `https://app.example.com:443`. Two URLs have the same origin only if all three match.
2. **SOP (same-origin policy)**: The letters stand for those three words. It is the browser rule that a page's scripts can't read responses from a different origin.
3. **CORS (cross-origin resource sharing)**: The letters stand for those three words. It is a set of response headers a server sends to tell the browser which other origins may read its responses.
4. **Preflight**: This is an `OPTIONS` request the browser sends before certain cross-origin requests, asking the server whether the real request is allowed.
5. **CSP (content security policy)**: The letters stand for those three words. It is a response header telling the browser which sources of scripts, styles and other content the page may use; anything else is blocked.
6. **Clickjacking**: This is an attack where your page is loaded invisibly inside a frame on another site, so the user clicks your buttons without knowing.
7. **CSRF (cross-site request forgery)**: The letters stand for those three words. It is an attack where another site makes the user's browser send a request to your site, carrying the user's cookie, so it acts as them.
8. **HSTS (HTTP strict transport security)**: The letters stand for those four words. It is a header telling the browser to use only HTTPS for your site for a set time, even if someone types `http://`.

## 2. The same-origin policy

By default, a script on one origin can't read data from another: a page on `evil.com` can't read the cookies, storage or API responses of `bank.com`, even in the same browser. That one rule is what makes it safe to have many sites open at once.

Two things it does **not** do, and both matter:

- **It doesn't stop requests being *sent*.** A page can still submit a form or load an image from another origin — and the browser attaches that origin's cookies. The policy stops the page from *reading* the response, not from *causing* the request. That gap is CSRF (§6).
- **It doesn't apply outside browsers.** `curl`, scripts and servers don't enforce it at all.

## 3. CORS — relaxing the policy, carefully

When your frontend on `https://app.example.com` calls your API on `https://api.example.com`, those are different origins, so the browser blocks reading the response unless the API says otherwise:

```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Vary: Origin
```

**Use an allowlist.** Compare the request's `Origin` with a fixed list and echo it back only if it's on the list. Send `Vary: Origin`, so a cache doesn't serve one origin's answer to another.

**The common misconfiguration** is echoing back *any* `Origin` with `Allow-Credentials: true`. It usually starts as a quick fix for a CORS error in development. It lets every website read your API as the logged-in user. (Browsers refuse the literal `*` with credentials, which is exactly why people reach for reflection instead — it gets around the refusal and the protection along with it.)

**CORS is not access control.** It only tells *browsers* whether *a page* may read the response. It does nothing to stop a request from `curl` or a script, which never asks. Every endpoint still has to authenticate and authorise the request itself.

## 4. Content Security Policy

CSP tells the browser which sources of content are legitimate; anything else is blocked, however it got onto the page.

```
Content-Security-Policy: default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'
```

This is the **backstop for XSS**: if a malicious `<script>` slips past output encoding, a strict policy that disallows inline scripts and unknown sources means the browser won't run it. It's defence in depth, not a replacement for encoding. A policy full of `'unsafe-inline'` or `*` looks like protection and provides little. If your app needs some inline scripts, use a **nonce** — a random value per response that marks the scripts you wrote — rather than allowing all inline code.

## 5. The other headers, and what each stops

- **`Strict-Transport-Security`** — HTTPS only, for the stated time. Stops an attacker on the network from downgrading a user to plain HTTP.
- **`X-Content-Type-Options: nosniff`** — the browser trusts your `Content-Type` instead of guessing, so an uploaded "image" can't be run as a script.
- **`frame-ancestors 'none'`** in CSP (and the older **`X-Frame-Options: DENY`**) — nobody may frame your pages, which stops clickjacking.
- **`Referrer-Policy: strict-origin-when-cross-origin`** — other sites learn only your origin, not full URLs that might contain IDs or tokens.

In Express, the `helmet` package sets sensible versions of these in one line: `app.use(helmet())`. Read what it sets rather than trusting it blindly — the CSP in particular usually needs adjusting for your app.

## 6. Cookies, and CSRF

```
Set-Cookie: session=abc123; Path=/; HttpOnly; Secure; SameSite=Lax
```

Three flags, three different attacks — easy to confuse, so worth getting exact:

- **`HttpOnly`** — scripts can't read the cookie. Limits what an XSS can steal (it can still act as the user while the page is open).
- **`Secure`** — sent only over HTTPS. Stops it leaking over plain HTTP.
- **`SameSite`** — controls whether it's sent on requests started by *other* sites. **`Lax`**, the browser default today, sends it only on top-level navigations using safe methods like `GET`. **`Strict`** never sends it cross-site. This is the main defence against CSRF.

`SameSite=Lax` still sends the cookie when another site *links* to you, so **a `GET` must never change anything** — no "delete" or "transfer" links. For extra protection on sensitive actions, also use a CSRF token, or check the `Origin` header on state-changing requests. And a JSON API that only accepts `Content-Type: application/json` gets some protection for free: a plain HTML form can't send that, so a cross-site attempt would need a preflight, which your CORS allowlist refuses.

## Worked example — headers you can test

A small API on Node's built-in server that sets every header above, with its CORS function swappable so the test can compare the right version with the common mistake.

```javascript
// headers.mjs — the response headers that switch on the browser's protections.

export const SECURITY_HEADERS = {
  // Only load scripts, styles and images from our own origin; no plugins; nobody may frame us.
  "content-security-policy": "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
  "x-content-type-options": "nosniff",                 // don't guess file types; trust content-type
  "referrer-policy": "strict-origin-when-cross-origin", // other sites see our origin, never full URLs
  "strict-transport-security": "max-age=31536000; includeSubDomains", // HTTPS only, for a year
  "x-frame-options": "DENY",                           // older browsers' version of frame-ancestors
};

// MISCONFIGURED, and common: echo back whatever Origin asked, with credentials allowed.
// Every website on the internet can now read logged-in users' responses.
export function corsReflectAnything(origin) {
  return origin ? { "access-control-allow-origin": origin, "access-control-allow-credentials": "true" } : {};
}

// CORRECT: only origins on the list, and say the answer depends on Origin so caches don't mix them up.
export function corsAllowlist(origin, allowed) {
  const headers = { vary: "Origin" };
  if (origin && allowed.includes(origin)) {
    headers["access-control-allow-origin"] = origin;
    headers["access-control-allow-credentials"] = "true";
  }
  return headers;
}

// The session cookie: not readable by scripts, HTTPS only, not sent on cross-site requests.
export const sessionCookie = (id) => `session=${id}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=86400`;
```

```javascript
// app.mjs — an API that sets every header above. `cors` is swappable so the test can compare.
import { createServer } from "node:http";
import { SECURITY_HEADERS, corsAllowlist, sessionCookie } from "./headers.mjs";

export function createApp({ cors = (origin) => corsAllowlist(origin, ["https://app.example.com"]) } = {}) {
  return createServer((req, res) => {
    const base = { ...SECURITY_HEADERS, ...cors(req.headers.origin) };

    if (req.method === "OPTIONS") {
      // The browser's preflight: "may this origin send this kind of request?"
      res.writeHead(204, { ...base, "access-control-allow-methods": "GET, POST", "access-control-allow-headers": "content-type" });
      return res.end();
    }
    if (req.url === "/login" && req.method === "POST") {
      res.writeHead(204, { ...base, "set-cookie": sessionCookie("s3cr3t") });
      return res.end();
    }
    if (req.url === "/me") {
      // Real code checks the session cookie here. CORS does not do this for you.
      res.writeHead(200, { ...base, "content-type": "application/json" });
      return res.end(JSON.stringify({ email: "ada@x.com" }));
    }
    res.writeHead(404, base);
    res.end();
  });
}
```

**Predict before running.**

1. A request to `/me` with `Origin: https://evil.example`. With the allowlist, does the response say evil.example may read it?
2. The same request against the reflect-anything version?
3. With the allowlist in place, does the evil-origin request still get the user's email in the response body?

```javascript
import { test } from "node:test";
import assert from "node:assert/strict";
import { createApp } from "./app.mjs";
import { corsReflectAnything } from "./headers.mjs";

async function start(options) {
  const server = createApp(options).listen(0);
  await new Promise((r) => server.once("listening", r));
  return { base: `http://127.0.0.1:${server.address().port}`, close: () => server.close() };
}

test("every response carries the security headers", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await fetch(`${app.base}/me`);
  assert.equal(res.headers.get("x-content-type-options"), "nosniff");
  assert.match(res.headers.get("content-security-policy"), /frame-ancestors 'none'/);
  assert.match(res.headers.get("strict-transport-security"), /max-age=31536000/);
});

test("CORS allowlist: our app's origin is allowed, anyone else's isn't", async (t) => {
  const app = await start(); t.after(app.close);
  const ours = await fetch(`${app.base}/me`, { headers: { origin: "https://app.example.com" } });
  assert.equal(ours.headers.get("access-control-allow-origin"), "https://app.example.com");
  const evil = await fetch(`${app.base}/me`, { headers: { origin: "https://evil.example" } });
  assert.equal(evil.headers.get("access-control-allow-origin"), null); // a browser would hide the response
  assert.equal(evil.headers.get("vary"), "Origin");
});

test("the common misconfiguration: reflecting any origin, with credentials", async (t) => {
  const app = await start({ cors: corsReflectAnything }); t.after(app.close);
  const evil = await fetch(`${app.base}/me`, { headers: { origin: "https://evil.example" } });
  assert.equal(evil.headers.get("access-control-allow-origin"), "https://evil.example");
  assert.equal(evil.headers.get("access-control-allow-credentials"), "true"); // evil.example can read /me as the user
});

test("CORS is not access control: a non-browser client gets the data regardless", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await fetch(`${app.base}/me`, { headers: { origin: "https://evil.example" } });
  assert.deepEqual(await res.json(), { email: "ada@x.com" }); // Node, curl and scripts ignore CORS entirely
});

test("preflight for an allowed origin lists what's permitted", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await fetch(`${app.base}/me`, { method: "OPTIONS", headers: { origin: "https://app.example.com" } });
  assert.equal(res.status, 204);
  assert.equal(res.headers.get("access-control-allow-methods"), "GET, POST");
});

test("the session cookie: HttpOnly, Secure, SameSite", async (t) => {
  const app = await start(); t.after(app.close);
  const res = await fetch(`${app.base}/login`, { method: "POST" });
  const cookie = res.headers.get("set-cookie");
  for (const flag of ["HttpOnly", "Secure", "SameSite=Lax", "Path=/"]) assert.ok(cookie.includes(flag), flag);
});
```

**Lab:** these files are in `labs/security-headers/`. From the vault root, `python3 labs/run.py security-headers` runs them and checks this page still shows the same code.

**Run it.** From `labs/security-headers/`, `node --test` (checked with Node 26). Expected:

```
ℹ tests 6
ℹ pass 6
ℹ fail 0
```

**The answers.**

1. **No** — there's no `Access-Control-Allow-Origin`, so a browser would hide the response from evil.example's page.
2. **Yes**, with credentials allowed: any website can read `/me` as the logged-in user.
3. **Yes.** Node's `fetch`, like `curl` or any script, ignores CORS completely and gets the data. CORS protects users' browsers from other sites; it never protected the endpoint. In real code, `/me` checks the session — that's the access control.

## Common pitfalls

1. **Reflecting any origin with credentials** to make a CORS error go away.
2. **Treating CORS as access control** — leaving an endpoint unauthenticated because "CORS only allows our frontend".
3. **A CSP so loose it does nothing** — `'unsafe-inline'`, `*`, or `unsafe-eval` everywhere.
4. **State-changing `GET` requests** — `SameSite=Lax` still sends cookies on cross-site links.
5. **Mixing up the cookie flags** — `HttpOnly` doesn't stop CSRF; `SameSite` doesn't stop XSS.
6. **Assuming the headers are there.** Check the live site — browser dev tools, `curl -I`, or a scanner. Missing headers are among the commonest findings in a security review → [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|scanning and enumeration]].

## Check your understanding

1. Are `https://example.com` and `https://api.example.com` the same origin? What about `http://example.com`?
2. What does the same-origin policy stop, and what doesn't it stop?
3. Why is reflecting the `Origin` header with credentials so dangerous?
4. Your API is "protected by CORS". A teammate says that's enough for an admin endpoint. What do you tell them?
5. Which cookie flag addresses each of these: a script stealing the cookie; another site making the user's browser submit a transfer; the cookie travelling over plain HTTP?

<details>
<summary>Answers — after your attempt</summary>

1. No — the hosts differ. `http://example.com` is also different, because the scheme differs (and so does the default port).
2. It stops a page *reading* responses from other origins. It doesn't stop requests being *sent* — with cookies — and it doesn't apply to non-browser clients.
3. Every website can then read your API's responses as whichever user is logged in, which defeats the same-origin policy entirely for your API.
4. CORS only governs what browsers let *pages* read. Anyone can call the endpoint directly with `curl`. The endpoint must authenticate the caller and check they're an admin.
5. `HttpOnly` — script theft. `SameSite` — the cross-site transfer (CSRF). `Secure` — plain HTTP.

</details>

## Practice — independent task

**Finish SWE 101's week 7 milestone: the flagship's threat model.**

1. Run `curl -sI https://<your-flagship>` and list which headers from §5 are missing. Add them (with `helmet` or your framework's equivalent), and a test that checks they're present, like the lab's first test.
2. Find the flagship's CORS configuration. Write a test that an origin not on your list gets no `Access-Control-Allow-Origin`.
3. Check the session cookie's flags in the browser's dev tools. Fix any missing one.
4. Search for any `GET` route that changes data, and change it to `POST`, `PUT` or `DELETE`.
5. Write the threat model: the flagship's **top five risks** — including what you found last lesson and this one — each with what you did about it, or why you accepted it.

**Done when:** the header and CORS tests pass, the cookie has all three flags, no `GET` changes state, and the threat model is in the repository.

## Before moving on

You can explain what the browser enforces and what it doesn't, configure CORS safely, and set and test the headers and cookie flags that matter.

**Recap.** An origin is scheme, host and port. The same-origin policy stops pages reading other origins' responses, not sending requests to them. CORS relaxes it for listed origins — never reflect any origin with credentials — and it is not access control. CSP is the XSS backstop. HSTS, `nosniff`, `frame-ancestors` and `Referrer-Policy` each close one door. Cookies need `HttpOnly`, `Secure` and `SameSite`, and `GET` must never change state.

**Next.** Week 8: ship the flagship, and a timed DSA mock — the end of [[learning/swe-101/index|SWE 101]].

## Related
- [[cybersecurity/04-web-security/04b-security-headers-in-other-languages|Security Headers in Other Languages]] — where each framework sets headers and CORS, and what it sets by default
- [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|Input validation and output encoding]]
- [[cybersecurity/04-web-security/02-secure-authentication|Secure authentication]] — sessions, and the cookie in context
- [[cybersecurity/04-web-security/03-https-and-tls|HTTPS and TLS]] — what HSTS enforces
- [[cybersecurity/02-ethical-hacking/06-scanning-and-enumeration|Scanning and enumeration]] — how missing headers get found
