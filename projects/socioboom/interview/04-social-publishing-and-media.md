# SocioBoom — Social Publishing, OAuth & Media

From [`../learning/backend/10-media-and-social-publishing.md`](../learning/backend/10-media-and-social-publishing.md),
[`04-auth-and-security.md`](../learning/backend/04-auth-and-security.md) §16/§27,
[`07-feature-case-studies.md`](../learning/backend/07-feature-case-studies.md).

Six platform integrations is a genuinely unusual thing to have done. These questions are where it
pays off.

---

### Q1. [Intermediate] 🔥 Walk me through OAuth for a platform connection.

**Strong answer covers:** redirect the user to the platform's authorise URL with your client id, the
requested **scopes**, a redirect URI and a `state` parameter → the user consents → the platform
redirects back with a short-lived **authorization code** → your server exchanges that code (plus the
client secret, server-side) for an **access token** and usually a **refresh token** → you store them
against the user's connection record.

**Two details that separate a real answer from a recited one:** `state` is CSRF protection — you
generate it, store it, and verify it on the callback, or an attacker can trick a user into
connecting *their* account to the attacker's session. And the code exchange must happen server-side,
because it uses the client secret.

---

### Q2. [Advanced] 🔥 How do you handle tokens at rest and refresh across six platforms?

**Strong answer covers:** every platform expires differently, so the connection record stores the
access token, refresh token where one exists, and an expiry — and publishing refreshes **proactively**
when the token is near expiry, rather than reacting to a 401 in the middle of a publish. Refresh
logic lives in one place per platform behind a common interface, so the worker never has
platform-specific token code.

**The things to name unprompted:**
- Tokens are **credentials at rest** — they belong encrypted, not in plaintext columns, and they must
  never appear in logs or error payloads.
- **Refresh can race** — two concurrent jobs for the same account both refreshing means one of the
  new tokens is immediately invalidated on platforms that rotate. That needs a lock.
- A refresh that **fails permanently** (revoked access) is a different outcome from a transient
  failure: the user must be told to reconnect, because no amount of retrying fixes it.

---

### Q3. [Intermediate] Reddit uses an app-only token flow. What's different about it?

**Strong answer covers:** app-only (client-credentials) authentication proves *your application's*
identity, not a user's — you exchange client id and secret for a token that can read public data. So
it's right for research/read operations and cannot post on a user's behalf; that requires the
user-authorised flow. Reddit also requires a descriptive `User-Agent` and enforces per-app rate
limits, so the app-only token is effectively a shared budget across all your users — which matters
for a research feature that runs per user.

---

### Q4. [Advanced] 🔥🔥 Your Facebook publishing code could never have worked. Explain.

**Strong answer covers:** the original code posted to `/{platformUserId}/feed`, where
`platformUserId` came from `GET /me` — the *user's own* Facebook id. **The Graph API cannot publish
to a personal profile timeline.** Meta removed that capability. Every post must target a **Page**. So
the code wasn't broken by a change; it had simply never been tested against a real account.

**The token chain — this is the part to internalise, and it's four different kinds of token:**
```
authorization code          (seconds, single use)
  → short-lived user token  (~1 hour)
    → long-lived user token (~60 days)     ← fb_exchange_token
      → Page access token   (inherits the user token's lifetime)
```

**The critical dependency:** a **Page token inherits the lifetime of the user token it was derived
from.** Derive a Page token from a *short-lived* user token and you get a Page token that dies in an
hour — and the failure appears days later as "publishing randomly stopped working." So the exchange
step is **mandatory, not an optimisation**.

**The lesson to state:** an integration that has never run against a real account is not implemented,
it's drafted. The API accepted the shape of the call; that's not the same as the operation being
possible.

---

### Q5. [Advanced] 🔥🔥 Explain Instagram's container model and the async trap.

**Strong answer covers the two-call flow:**
```
POST /{ig-user-id}/media          → { image_url | video_url, caption, media_type } → container id
POST /{ig-user-id}/media_publish  → { creation_id: <container id> }                → live
```

**Three hard requirements:**
1. **Professional account only** (Business or Creator). A personal Instagram account cannot publish
   through the API at any tier.
2. **A public URL, not bytes** — Instagram fetches the file itself. *This is the requirement that
   forces the whole storage pipeline to exist*, which is the connection worth drawing.
3. **Linked to a Page** in the Facebook Login route; you find the IG account by walking the user's
   Pages and asking each for `instagram_business_account`.

**The async trap:** image containers are ready immediately; **video containers are not**. Instagram
downloads and transcodes in the background, and publishing early fails with a misleading "media ID is
not available" that looks like a permissions error. So video requires **polling `status_code` until
`FINISHED`** (with an `ERROR` branch and a deadline) before publishing.

**Two more facts worth knowing:** all API-published Instagram video becomes a **Reel** —
`media_type: 'REELS'` is the only video option, there's no feed-video type. And the rate limit is 100
published posts per rolling 24 hours, readable at `GET /{ig-user-id}/content_publishing_limit`.

---

### Q6. [Advanced] 🔥 TikTok has "two scopes, one audit." What does that mean?

**Strong answer covers:** posting capability is split across separate scopes with different review
requirements — one tier lets you publish to a private/self-only destination for testing, and actually
publishing publicly requires passing an app **audit**. So the integration can be fully correct in
code and still not able to post publicly, because approval is a *process* gate rather than a
technical one.

**The generalisable point, and it's a good one:** on social platforms, "can this API do X?" has three
different answers — can the endpoint do it, does your app have the scope, and has your app been
approved for that scope in production. Planning an integration means budgeting for the review, not
just the code.

---

### Q7. [Intermediate] 🔥 What's the common pattern across all three Meta/TikTok integrations?

**Strong answer covers:** the shape repeats —
1. **You can't post as a person.** Every platform routes publishing through a business/professional
   entity (a Page, a professional IG account, an audited app).
2. **The platform fetches your media by URL** rather than accepting bytes — which is why object
   storage with public (or signed) URLs is a hard requirement, not a convenience.
3. **Publishing is asynchronous** — containers, transcoding, review — so "the API returned 200" is
   not "the post is live", and the integration needs a polling/confirmation step.
4. **Tokens are chained and expiring**, so refresh is part of the publish path.

Being able to state the *pattern* rather than three anecdotes is what shows you'd onboard a seventh
platform quickly.

---

### Q8. [Intermediate] 🔥 Explain the presigned upload flow to R2, and why the file must not touch your API.

**Strong answer covers:** the client asks the API for an upload URL; the API (holding the
credentials) returns a **time-limited, key-scoped, method-scoped** signed URL; the browser uploads
**directly to R2**; the client then tells the API the resulting key so it can record metadata.

**Why the file must not pass through the API:** you'd pay double bandwidth, buffer the file in memory
(a real constraint on a small instance), hit platform body-size limits, and tie up a request for the
duration of the upload. R2 specifically also has no egress fees, which matters because the *platforms
themselves* fetch these files (Q5) — so every published post is an outbound transfer.

---

### Q9. [Advanced] 🔥🔥 Explain Prisma's three-valued JSON and the bug it caused.

**Strong answer covers the three values as three distinct instructions:**
```ts
media: null            // ❌ type error on a nullable Json column
media: undefined       // "don't touch this column"
media: Prisma.DbNull   // "write SQL NULL"
```

**The bug:** existing code used `contentByPlatform ?? undefined`, which quietly means **you can never
clear that field** — passing `null` just leaves the old value in place. Harmless for its original
use; wrong for media, where removing every attachment has to actually persist.

**The fix:**
```ts
const jsonOrNull = (v: unknown) =>
  v === null || v === undefined ? Prisma.DbNull : (v as Prisma.InputJsonValue);
```

**The fourth value to mention:** `Prisma.JsonNull` writes the JSON value `null` *inside* the column,
rather than SQL `NULL` on the column. For a nullable column you almost always want `DbNull`.

**Why it belongs in an interview:** it's the same family as NextVibe's `undefined`-in-a-`where` bug —
**`undefined` means "ignore this" to Prisma**, in both filters and writes, and that meaning is a
silent no-op rather than an error.

---

### Q10. [Intermediate] What patterns do you use for the external HTTP calls themselves?

**Strong answer covers:** one axios instance per platform with the base URL and default headers, so
auth and versioning live in one place; explicit timeouts on every call, because a hung request to a
third party will otherwise hold a worker slot indefinitely; error normalisation, since each platform
reports failure in its own envelope and the worker needs one shape to decide retry-vs-fail; and
**never logging the request headers**, which contain the tokens.

**The classification that matters:** distinguish **retryable** (429, 5xx, timeout) from **permanent**
(revoked token, missing scope, rejected content). Retrying a permanent failure three times with
backoff just delays telling the user something they need to act on.

---

### Q11. [Advanced] A user says "my post didn't go out." How do you investigate?

**Strong answer covers a route through the actual architecture:** was the job **enqueued** (does it
exist in Redis with the right delay)? Is the **worker running** — the failure that once silently
disabled all publishing (Q3 in [02-queues-and-deployment.md](02-queues-and-deployment.md))? Did the
job run and fail — what's in `publishedPlatforms`, which tells you whether it partly succeeded? Was
it a token problem (expired, revoked, missing scope) or a content rejection? For Instagram video,
did the container ever reach `FINISHED`?

**The structural point:** each of those is a different *stage*, and the whole reason the job records
per-platform progress is so this question has an answer better than "it failed."
