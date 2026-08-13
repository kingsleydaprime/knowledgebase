# OAuth Provider Integrations — The Practical Cut

[[concepts/01-backend/05-authentication-flows|05-authentication-flows]] covers what OAuth 2.0
*is*. This file covers what actually happens when you integrate four or five real providers:
where each one deviates from the spec, which failures are configuration and which are
policy, and what to plan for beyond the code.

Written 2026-08-12 from integrating X/Twitter, LinkedIn, Reddit, Facebook, Instagram and
TikTok into one scheduling product. Examples are from that work; the patterns generalise.

---

## 1. The Part That's Actually the Same Everywhere

Authorization Code flow, and it barely varies:

```
GET  {authUrl}?response_type=code&client_id=…&redirect_uri=…&scope=…&state=…
     → user approves
     → provider redirects to redirect_uri?code=…&state=…
POST {tokenUrl}  { grant_type: 'authorization_code', code, redirect_uri, client_id, client_secret }
     → { access_token, refresh_token?, expires_in? }
```

You can drive every provider from one table of `{ authUrl, tokenUrl, clientId, clientSecret,
scopes }`. Build that abstraction first — adding a platform then becomes one config entry
plus a publish function.

**The `state` parameter is not optional.** It's CSRF protection for the callback. A neat
trick: make `state` a short-lived signed JWT carrying your own user ID. The callback is
necessarily unauthenticated — the provider redirects a raw browser to it, with no session —
so `state` is how you know *which of your users* this code belongs to:

```ts
const state = jwt.sign({ userId }, SECRET, { expiresIn: '10m' });
// …in the callback:
const { userId } = jwt.verify(state, SECRET);
```

Short expiry doubles as replay protection. For PKCE providers, stash the `code_verifier` in
the same JWT rather than in server-side session state.

---

## 2. Where Providers Deviate — The Actual Time Sinks

### Parameter names

TikTok uses **`client_key`**, not `client_id` — in both the authorize URL and the token
exchange. One provider, one word, and a generic implementation breaks. Worth designing for:

```ts
const clientIdKey = config.clientIdParam ?? 'client_id';
const params = new URLSearchParams({ [clientIdKey]: config.clientId, … });
```

### Errors returned as HTTP 200

TikTok returns failures as **200 OK with an `error` object in the body**. `axios` and `fetch`
both treat that as success. If you only check status codes, a failed token exchange reads as
a successful one and you store `undefined` as an access token.

```ts
if (data?.error?.code && data.error.code !== 'ok') throw new Error(data.error.message);
```

Always check the body shape for providers you haven't used before.

### Redirect URI rules are stricter than you expect

Matching is **exact string comparison**, not URL equivalence. A trailing slash, a query
string, a `#fragment`, or `http` vs `https` all fail. Most providers cap the number you can
register (TikTok: 10).

**TikTok's Login Kit for Web requires `https`** — there is no localhost exception, and it
applies in sandbox too. Meta, X and Reddit all accept `http://localhost`. So one provider
forces a tunnel on your whole local setup unless you make the redirect base per-provider:

```ts
const redirectUriFor = (platform: string) =>
  `${CONFIG[platform]?.redirectBase ?? APP_URL}/api/v1/accounts/callback/${platform}`;
```

Without that, pointing one provider at a tunnel silently invalidates every other provider's
registered URI. See [[devops/08-networking-and-web/03-local-https-tunnels|local https tunnels]].

### Scope lists vs. dashboard-defined permission sets

Meta apps created through a **use case** get *Facebook Login for Business*, where a
**`config_id`** replaces `scope` in the auth URL — the permission set lives in a dashboard
configuration instead of your code. Classic Facebook Login still takes `scope`.

Two different flows for the same provider depending on how the app was created. Support both
and switch on whether a config ID is present:

```ts
...(configId ? { config_id: configId } : { scope: config.scopes })
```

### Permissions can live behind several layers

With Meta, a permission must be added to the **use case**, then selected in the **login
configuration**, and only then is it requested at consent. Miss any layer and it is silently
absent from the token — no error anywhere, the scope simply isn't there.

And **grants are frozen at consent time**: changing dashboard configuration does nothing to
tokens already issued. Always disconnect and reconnect after touching permissions, or you
will conclude a correct fix didn't work.

The general lesson: when a provider has a dashboard, treat "what the dashboard says" and
"what the token carries" as separate facts, and verify the second directly:

```
GET /me/permissions   →  the list that actually matters
```

---

## 3. The Token You Store Is Often Not the Token You Get

This is the biggest conceptual jump from tutorial OAuth. The access token from the exchange
is frequently just an intermediate step.

**Facebook** is the clearest case. Publishing targets a *Page*, not a user, so:

```
authorization code
  → short-lived user token   (~1 hour)
    → long-lived user token  (~60 days)   via fb_exchange_token
      → Page access token    ← what you actually store and publish with
```

The dependency that bites: **a Page token inherits the lifetime of the user token it was
derived from.** Derive from the short-lived token and your Page token dies in an hour. The
long-lived exchange isn't an optimisation, it's load-bearing.

**Instagram** is the same chain, ending at a Page token scoped to a linked Instagram
professional account.

Design implication: your `accounts` table shouldn't assume `access_token` + `refresh_token`
means what OAuth says it means. Facebook has **no `refresh_token` grant at all** — the
sensible move is to store the long-lived *user* token in the `refresh_token` column, because
that's the thing that lets you re-derive a fresh Page token without another consent screen.
Comment that loudly; it will confuse the next reader otherwise.

### Refresh is per-provider, not generic

| Provider | Mechanism |
|---|---|
| X/Twitter, Reddit, TikTok | Standard `grant_type=refresh_token` |
| LinkedIn | Standard, but doesn't always return a new refresh token — keep the old one |
| Facebook / Instagram | No refresh grant. Re-exchange the still-valid long-lived token, then re-derive |

Facebook's matters operationally: `fb_exchange_token` **only works before expiry**. If you
wait until the token is dead you cannot refresh it, only send the user through consent again.
So refresh proactively — a week early, not a minute early:

```ts
const REFRESH_WINDOW_MS = { facebook: 7*24*60*60*1000, twitter: 60_000, … };
```

---

## 4. Publishing Deviations Worth Knowing Upfront

These aren't OAuth, but they determine architecture, so they belong in the same planning pass.

**Some platforms fetch media by URL rather than accepting bytes.** Instagram and TikTok both
do. That means a public HTTPS host is a *prerequisite* for the feature, not a deployment
detail — see
[[devops/03-cloud/03-object-storage-and-direct-uploads|object storage & direct uploads]].
TikTok goes further and requires the **domain to be verified** in its developer portal.

**Video publishing is asynchronous, and the initiating call returns success immediately.**
Instagram's container creation and TikTok's `video/init/` both return before the media is
processed. Publish an Instagram container too early and you get a misleading "media ID is not
available" that looks like a permissions error. You must poll:

```
Instagram: GET /{container-id}?fields=status_code   → FINISHED
TikTok:    POST /v2/post/publish/status/fetch/      → PUBLISH_COMPLETE | SEND_TO_USER_INBOX
```

Skip the poll and you report failures to users as successes.

**Capabilities get removed.** The Graph API cannot post to a personal Facebook profile
timeline — for any app, at any tier. Not a permission you can request. Check that the thing
you're building is still *possible* before designing around it.

---

## 5. Non-Code Realities to Plan Around

**App review is the critical path.** Meta App Review and TikTok's audit both run 2–4 weeks
with multiple feedback rounds. Until approved, only accounts explicitly listed as testers in
the developer portal can connect. The code is not the long pole — submit as soon as you have
a working dev-mode integration and let review run in parallel.

TikTok's has a genuine catch-22: the demo recording must be made with the API *while it's
still restricted*, so you record a private-visibility post to prove an integration you're not
yet allowed to use publicly.

**Sandbox/dev modes have their own credentials.** A TikTok sandbox issues a separate client
key and secret from production, and only listed *target users* can authenticate. Expect to
swap credentials at launch and to keep two sets straight meanwhile.

**Some scopes are two different products.** TikTok splits posting into `video.upload` (lands
in the user's drafts, no audit) and `video.publish` (posts live, audit required). The code
difference is one scope string and one endpoint. Build both behind a flag and ship the
unaudited one — waiting a month for approval before shipping anything is the wrong trade.

**API versions expire on a schedule.** Meta retires each Graph API version roughly two years
after release. Hard-coding `v20.0` across five call sites is a time bomb; put it in one
constant fed by an env var, and check the changelog before bumping.

---

## 6. A Checklist for Adding a Provider

1. Can it even do what you need? (personal-profile posting, text-only posts on a video
   platform — check before designing)
2. Does the redirect URI need https? Does it need a verified domain?
3. Parameter names — `client_id` or something else?
4. Are errors returned as non-2xx, or as 200 with a body field?
5. Is the token you receive the token you publish with, or an intermediate?
6. How does refresh work — and does it need to run *before* expiry?
7. Is publishing synchronous, or does it need polling?
8. What does review/audit require, and how long does it take?
9. Does a sandbox exist, and does it use separate credentials?

Answering these before writing code is roughly an hour and saves days.

---

## Related
- [[concepts/01-backend/05-authentication-flows|05-authentication-flows]] — the theory
- [[devops/08-networking-and-web/03-local-https-tunnels|Local HTTPS tunnels]] — for https-only callbacks
- [[devops/03-cloud/03-object-storage-and-direct-uploads|Object storage & direct uploads]] — for fetch-by-URL platforms
- [[devops/09-secret-management/README|Secret management]] — storing provider tokens at rest
