# OAuth Provider Integrations — The Practical Cut

[[backend/05-auth/01-authentication-flows|05-authentication-flows]] covers what OAuth 2.0
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
- [[backend/05-auth/01-authentication-flows|05-authentication-flows]] — the theory
- [[devops/08-networking-and-web/03-local-https-tunnels|Local HTTPS tunnels]] — for https-only callbacks
- [[devops/03-cloud/03-object-storage-and-direct-uploads|Object storage & direct uploads]] — for fetch-by-URL platforms
- [[devops/09-secret-management/index|Secret management]] — storing provider tokens at rest

## 7. Account Linking — One Human, Several Ways to Prove It

Every provider integration eventually meets the same question: a user signs in
with Google today and with email+password tomorrow. **One account, or two?**

Almost always one. The work is in getting there without opening a takeover.

### 7.1 Linking by email is a takeover primitive without one check

The natural implementation — "look for an existing user with this email, and
attach the provider identity to it" — hands an attacker any account whose email
address they can *claim* at a provider, unless the provider actually
**verified** the address.

```ts
// Google, in the ID token
if (payload.email_verified !== true) throw new UnauthorizedException();
```

Write it as `!== true`, never `=== false`. The claim is attacker-adjacent
input, and a missing claim must fail closed — `=== false` lets `undefined`
through, which is precisely the case a future API version or an unusual
provider will hand you.

Providers differ in how much they promise here. Some never verify. Some (Apple)
support private relay addresses that are verified but not the user's real
mailbox. **If a provider does not assert verification, you cannot link by email
at all** — link only on an explicit, authenticated "connect this account"
action taken from inside an existing session.

### 7.2 Lookup precedence: subject id first, email second

Two identifiers can find the user, and they are not equally trustworthy:

| identifier | stability | trust |
|---|---|---|
| provider subject id (`sub`) | permanent per account | the identity itself |
| email | **changes**, and can move between accounts | a hint, verified at best |

So the order is fixed:

```
1. look up (provider, providerAccountId) → if found, done
2. else look up email                    → if found, link the identity onto it
3. else create a new account
```

**Do not fold these into one `OR` query.** An `OR` has no precedence: when a
user changes their provider-side email to one that already exists locally, two
rows match and the database returns whichever it likes — signing the visitor in
as either user, non-deterministically.

### 7.3 Make the database enforce uniqueness

```sql
CREATE UNIQUE INDEX ON accounts (provider, provider_account_id);
```

"Only one row can match" is an invariant; an invariant that lives only in
application code is one the database will eventually let you break. NULLs are
distinct in a unique index, so password-only accounts (no provider columns) are
unaffected and coexist freely.

### 7.4 One column pair per user does not survive a second provider

Storing `oauth_provider` / `oauth_id` directly on `users` works for exactly one
provider. Add a second and there is nowhere to put it: the user signs in fine
(the email is verified) but the new identity goes unrecorded, so they are only
ever found by email on that provider — and a provider-side email change orphans
them.

The standard shape, and what NextAuth/Auth.js models:

```
users     (id, email, ...)
accounts  (id, user_id, provider, provider_account_id, ...)
            UNIQUE (provider, provider_account_id)
```

One row per linked identity, many per user. **Adding this before launch is a
schema change; adding it afterwards is a data migration over live accounts.**
Decide early even if you ship with one provider.

### 7.5 The reverse direction is the one that gets forgotten

Teams test "password user adds Google" and ship. The other direction —
**provider user wants a password** — is usually broken, and broken *silently*:

- login returns "invalid credentials" for a correct address, because there is
  no hash to compare against;
- forgot-password skips provider-only accounts and still returns the generic
  "if that address exists, a link has been sent";
- no set-password endpoint exists at all.

Result: losing the provider account means permanent lockout, with every
response saying things are fine. Fixes:

1. **Let forgot-password work for provider-only accounts.** It does not weaken
   anything — the provider proved ownership of that mailbox, and the link goes
   to that same mailbox. Change the wording from "reset" to "set".
2. **Add an authenticated set/change-password endpoint.** Require the current
   password only when one exists; there is nothing to prove when there isn't.
3. **Tell the user at the login form** which provider the account uses, instead
   of a generic failure.

Step 3 admits the address is registered. That is a real enumeration leak and
should be a recorded decision — but check your registration endpoint first:
if it already answers "email already in use", the leak exists regardless, and
hardening only the login form buys nothing. **The two endpoints have to agree.**

### 7.6 Changing a password must end existing sessions

Adding a second sign-in method adds a second thing to revoke. If a password
reset does not invalidate tokens issued before it, an attacker holding a stolen
refresh token keeps the session for its full lifetime — and the victim's reset
did nothing.

The cheap, storage-free mechanism is a timestamp on the user row compared
against the token's `iat`:

```ts
if (user.passwordChangedAt) {
  const changedAt = Math.floor(user.passwordChangedAt.getTime() / 1000);
  if ((payload.iat ?? 0) < changedAt) throw new UnauthorizedException();
}
```

Two details that decide whether this works:

- **`iat` is in whole seconds; JS timestamps are milliseconds.** Floor the
  stored value, or a token minted in the same second as the change is rejected
  — the exact token you hand back after a self-service password change.
- **The change endpoint must return fresh tokens**, since it just invalidated
  the caller's own. Otherwise changing your password logs you out.

Put the check where a user row is already being loaded (session validation
usually loads one anyway) and it costs an extra column, not an extra query.

### 7.7 Checklist

1. Does each linking direction work, or only the one you tested?
2. What proves the provider verified the email — and does it fail closed?
3. Can the lookup match two rows? Does a unique index prevent it?
4. What happens when two sign-ins for a new user arrive at once?
5. When a credential changes, what still holds a live session?
6. If a user loses one method, is there a route back, and does the UI say so?
7. Does the enumeration posture match across login, register and reset?

→ applied: [[projects/nextvibe/learning/backend/02-auth|nextvibe auth notes]]
