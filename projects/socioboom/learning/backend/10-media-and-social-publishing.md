# SocioBoom Backend — Media Storage & Social Publishing APIs

Written 2026-08-11 alongside the R2 media pipeline, the Facebook Pages fix, and the
Instagram/TikTok publishers. See also `learning/backend/04-auth-and-security.md` (the OAuth
token lifecycles this builds on), `learning/backend/05-queues-and-jobs.md` (the worker that
runs these publishers), and `learning/frontend/09-media-uploads.md` (the browser side).

This file covers: why presigned uploads exist, the R2 setup, why Instagram and TikTok force
a media pipeline before anything else can work, the Facebook Pages token chain, Instagram's
container/publish two-step, TikTok's two-scope audit model, and the traps in each.

---

## 1. The Dependency Nobody Sees Coming

The task was "add TikTok posting." The actual blocker was that the app had no media
pipeline at all — the uploader called `URL.createObjectURL(file)` and sent the resulting
`blob:` URL to the backend, which ignored it.

That was invisible for as long as every supported platform accepted text-only posts.
Twitter, LinkedIn, Reddit, and Facebook all do. Instagram and TikTok do not. So adding
either one turned a cosmetic gap into a hard blocker.

**The lesson worth keeping:** when a feature "just" adds a new provider, check what that
provider *requires* rather than what it *does*. The new requirement is where the real work
hides. Here the ordering was forced:

```
file storage → media column on Post → Instagram/TikTok publishers
```

Building the TikTok publisher first would have produced code with nothing to publish.

---

## 2. Presigned Uploads — Why the File Must Not Touch Your API

The naive design is: browser POSTs the file to your server, your server forwards it to
storage. Three things break.

**Body size limits.** `main.ts` sets `express.json({ limit: "10kb" })`. A 200MB video is
20,000× that. You could raise the limit, but that just moves the problem.

**Process occupancy.** Node is single-threaded for your code. Streaming a 500MB upload
through an Express handler ties that request up for the entire duration. Ten concurrent
video uploads and your API stops answering anything else.

**Double bandwidth.** The bytes travel client → your server → storage. You pay for the
inbound and the outbound.

The fix is a **presigned URL**: your server signs a short-lived permission slip that says
"whoever holds this may PUT one object with this exact key, content-type, and length,
within the next 5 minutes." The browser then uploads *directly* to storage.

```
1. POST /media/presign   → server returns { uploadUrl, key, publicUrl }
2. PUT  <uploadUrl>      → browser → R2 directly.  Server not involved.
3. POST /media/confirm   → server HEADs the object to verify it landed
```

Step 3 is not ceremony. Without it, a client could skip step 2 entirely and POST any URL
it liked into `Post.media`. You'd discover the lie hours later when a publish failed.

### Pinning the signature

```ts
const command = new PutObjectCommand({
  Bucket: R2_BUCKET,
  Key: key,
  ContentType: mimeType,
  ContentLength: req.sizeBytes,
});
```

Both `ContentType` and `ContentLength` go *into the signature*. If the browser then tries
to upload a 2GB file after declaring 5MB, or sends `video/mp4` after declaring
`image/jpeg`, the signature doesn't validate and R2 rejects it. Declared limits enforced
by the server are real; declared limits checked only in JavaScript are decoration.

### Key naming

```ts
const key = `uploads/u${userId}/${randomUUID()}.${ext}`;
```

Namespaced by user, and a UUID instead of the original filename. User-supplied filenames
bring path traversal (`../../etc/passwd`), unicode normalization surprises, and collisions,
in exchange for nothing — nobody sees the key. The `uploads/u{id}/` prefix is also what
makes the ownership check a cheap string comparison:

```ts
if (!key.startsWith(`uploads/u${userId}/`)) throw new Error('That media does not belong to you');
```

### Why R2 over S3

Instagram and TikTok fetch media **by URL** — every publish is an outbound download of the
whole file from your bucket. On S3 you pay egress on each one. R2 has zero egress fees and
is S3-API-compatible, so the AWS SDK works unchanged and only the endpoint differs:

```ts
new S3Client({ region: 'auto', endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`, ... })
```

`region: 'auto'` because R2 has no regions in the AWS sense.

---

## 3. Facebook — The Bug That Was Always There

The original publisher did this:

```ts
await axios.post(`https://graph.facebook.com/v20.0/${platformUserId}/feed`, { message, access_token });
```

where `platformUserId` came from `GET /me` — i.e. the *user's own* Facebook ID.

**The Graph API cannot publish to a personal profile timeline.** Meta removed that
capability. Every post must target a **Page**. So this code could never have worked
against a real account; it just hadn't been tested with one.

### The token chain

This is the part worth internalizing, because it's four different kinds of token:

```
authorization code           (seconds,  single use)
  → short-lived user token   (~1 hour)
    → long-lived user token  (~60 days)   ← fb_exchange_token
      → Page access token    (inherits the user token's lifetime)
```

The critical dependency: **a Page token inherits the lifetime of the user token it was
derived from.** Derive a Page token from a *short-lived* user token and you get a Page
token that dies in an hour. So the exchange step is mandatory, not an optimization.

```ts
const longLived = await exchangeForLongLivedUserToken(accessToken);
const pages = await listPages(longLived.accessToken);
accessToken   = pages[0].accessToken;     // what we publish with
platformUserId = pages[0].id;             // the Page ID
refreshToken  = longLived.accessToken;    // how we re-derive later
```

Note what goes in `refreshToken`: not a refresh token — Facebook has no `refresh_token`
grant. We store the long-lived *user* token there because it's the thing that lets us
re-list Pages and get a fresh Page token without sending the user back through consent.
The schema field is reused for a different concept, which is worth a comment in the code
(and it has one).

### Scopes

```
pages_show_list         ← without this /me/accounts returns nothing
pages_manage_posts      ← publish
pages_read_engagement   ← read metrics back
```

`pages_show_list` is the easy one to miss: you can authenticate a user perfectly, get a
valid token, and still have nowhere to publish, because the Pages list comes back empty.

### Version pinning

Meta expires each Graph API version roughly two years after release. The codebase had
`v20.0` hard-coded in five places; v20.0 goes dark **2026-09-24**. Now it's one constant:

```ts
export const GRAPH_VERSION = process.env.FACEBOOK_GRAPH_VERSION || 'v25.0';
```

Check <https://developers.facebook.com/docs/graph-api/changelog/> before bumping. This is
exactly the class of fact you cannot answer from memory — it changes on a schedule.

---

## 4. Instagram — Containers, and Why Video Needs Polling

Instagram rides on the same Meta app. Publishing is two calls:

```
POST /{ig-user-id}/media          → { image_url | video_url, caption, media_type } → container ID
POST /{ig-user-id}/media_publish  → { creation_id: <container ID> }                → live
```

Three hard requirements:

1. **Professional account only.** Business or Creator. A personal Instagram account cannot
   publish through the API at any tier.
2. **Public URL, not bytes.** Instagram fetches the file itself. This is the requirement
   that forces the whole storage pipeline.
3. **Linked to a Page**, in the Facebook Login route. You find the IG account by walking
   the user's Pages and asking each for `instagram_business_account`.

### The async trap

Image containers are ready immediately. **Video containers are not.** Instagram downloads
and transcodes in the background, and publishing before that finishes fails with a
misleading "media ID is not available" error that looks like a permissions problem.

```ts
while (Date.now() < deadline) {
  const { data } = await axios.get(`${GRAPH}/${containerId}`, { params: { fields: 'status_code' } });
  if (data?.status_code === 'FINISHED') return;
  if (data?.status_code === 'ERROR') throw new Error(...);
  await new Promise(r => setTimeout(r, 5000));
}
```

Also worth knowing: **all API-published Instagram video becomes a Reel.** There is no
separate feed-video type — `media_type: 'REELS'` is the only video option.

Rate limit is 100 published posts per rolling 24 hours, readable at
`GET /{ig-user-id}/content_publishing_limit`.

---

## 5. TikTok — Two Scopes, One Audit

TikTok splits posting across two scopes that look similar and behave completely
differently:

| Scope | Endpoint | Behavior | Audit? |
|---|---|---|---|
| `video.upload` | `/v2/post/publish/inbox/video/init/` | Lands in the creator's drafts; they tap publish | No |
| `video.publish` | `/v2/post/publish/video/init/` | Posts straight live | **Yes** |

Unaudited clients using `video.publish` get every post forced to `SELF_ONLY` visibility.
The audit takes 2–4 weeks with multiple feedback rounds.

There's a genuine catch-22 in the process: the screen recording you submit as evidence has
to be made using the API *while it's still restricted*. You record a private-visibility
post to prove the integration works.

Hence the env flag — the difference between the two modes is one scope string and one
endpoint, so both are built and `TIKTOK_DIRECT_POST=true` flips it the day approval lands:

```ts
export const TIKTOK_SCOPES = TIKTOK_DIRECT_POST
  ? 'user.info.basic,video.publish'
  : 'user.info.basic,video.upload';
```

### OAuth deviations

TikTok does not follow OAuth 2.0 faithfully. Two differences bit immediately:

- The parameter is **`client_key`**, not `client_id` — in both the authorize URL and the
  token exchange. The generic `OAUTH_CONFIG` needed a `clientIdParam` override for this.
- Errors come back **HTTP 200 with an `error` field in the body**. `axios` won't throw.
  You have to check `data.error` explicitly or a failure reads as success.

### PULL_FROM_URL needs domain verification

TikTok fetches the video from a URL like Instagram does, but adds a requirement: the
domain must be verified in the developer portal under *URL properties*. The `r2.dev`
development subdomain won't work — this forces a custom domain bound to the bucket.

### Polling again

`video/init` returns as soon as the job is *queued*. Without polling
`/v2/post/publish/status/fetch/`, a download or transcode failure is reported to the user
as a successful post. Terminal states: `PUBLISH_COMPLETE` (direct) and
`SEND_TO_USER_INBOX` (draft mode).

---

## 6. The Pattern Across All Three

Once you've written three of these, the shape is the same every time:

1. **OAuth is the easy part** and is nearly identical everywhere. Adding a platform is one
   entry in `OAUTH_CONFIG`.
2. **The credential you store is rarely the one OAuth hands you.** Facebook: a Page token
   derived from an exchanged user token. Instagram: the same Page token, keyed to an IG
   user ID. Only Twitter and TikTok store what they return.
3. **Publishing is asynchronous** on every platform that takes video, and every one of them
   returns success from the *initiating* call. Poll, or you'll report failures as successes.
4. **Read the error body, not the status code.** TikTok returns 200 on failure; Meta buries
   the real reason in `err.response.data.error.message`.
5. **App Review gates everything.** Dev-mode testing with your own accounts works
   immediately; real users don't work until approval. Build and submit in parallel.

---

## 7. Prisma's Three-Valued JSON

A small trap hit while adding `Post.media`:

```ts
media: null            // ❌ type error on a nullable Json column
media: undefined       // "don't touch this column"
media: Prisma.DbNull   // "write SQL NULL"
```

The existing code used `contentByPlatform ?? undefined`, which quietly means *you can never
clear that field* — passing null just leaves the old value. Fine for its use, wrong for
media, where removing every attachment has to actually persist:

```ts
const jsonOrNull = (v: unknown) =>
  v === null || v === undefined ? Prisma.DbNull : (v as Prisma.InputJsonValue);
```

There is also `Prisma.JsonNull`, which writes the JSON value `null` *inside* the column
rather than SQL `NULL`. For a nullable column you almost always want `DbNull`.

---

## 8. Field Notes — What Actually Broke (2026-08-12)

Sections 1–7 were written from documentation, before any of it had touched a live API.
This section is what happened on first contact. Every item below cost real time, and none
of them were code bugs.

### R2: presign succeeds, upload fails, server logs look clean

**Buckets ship with no CORS policy.** The browser PUTs directly to R2, which is
cross-origin, so it's blocked before it's sent. `POST /media/presign` returns 200 in your
log and the failure never reaches your server at all — which is exactly what makes it
confusing.

```json
{ "AllowedOrigins": ["http://localhost:3000"], "AllowedMethods": ["PUT","GET","HEAD"],
  "AllowedHeaders": ["content-type"], "ExposeHeaders": ["ETag"], "MaxAgeSeconds": 3600 }
```

The diagnostic that identifies it instantly: **a cancelled PUT with no status code** in the
Network tab. Status 0 in `xhr.onerror` means "never completed at the HTTP level", and for a
cross-origin request that's almost always CORS.

Second-order lesson: `axios`'s `.message` for a failed request is only *"Request failed with
status code 400"*. The server's real message is in `error.response.data`. Unwrap it, or every
backend error reaches the user as a status code.

### Meta: the app creation flow changed under us

Meta replaced "app type: Business" with a **use-case picker**. Tick *Manage everything on
your Page* and *Manage messaging & content on Instagram*; avoid *Create an app without a use
case*, which yields an app with no permissions at all.

The consequence that matters: use-case apps get **Facebook Login for Business**, where a
`config_id` replaces `scope` in the auth URL — the permission set lives in a dashboard
configuration rather than your code. Classic Facebook Login still takes `scope`. Two
different flows for the same provider, decided by how the app was created. We support both:

```ts
...(configId ? { config_id: configId } : { scope: config.scopes })
```

### TikTok: four separate walls, in order

1. **Sandbox has its own client key and secret.** Keys prefixed `sbaw…` are sandbox;
   production starts `aw…`. Only accounts listed under *Target Users* can connect.

2. **Redirect URIs must be `https`.** No localhost exception for web apps — it's the only
   provider of the six with this rule. Fix is a tunnel
   ([[devops/08-networking-and-web/03-local-https-tunnels|cloudflared]]), and crucially the
   redirect base had to become **per-platform**, because pointing `APP_URL` at a tunnel would
   silently invalidate every Meta redirect URI at once.

3. **Sandbox config is separate from production config.** The redirect URI has to be
   registered *inside the sandbox*. Registering it on the production app while using a
   sandbox key produces `error_type=redirect_uri` with a URL that looks completely correct —
   the most misleading error of the whole session.

4. **`PULL_FROM_URL` requires a verified domain, in sandbox too.** `url_ownership_unverified`.
   `r2.dev` can't be verified because you don't own it, which forces a custom domain onto the
   bucket. Verify the **root** domain by DNS TXT — that covers all subdomains and paths.

### The scope/field trap

`user.info.basic` grants `open_id`, `avatar_url` and `display_name` — but **not** `username`,
which needs `user.info.profile`. Requesting a field outside your granted scope fails the
*entire* call, so asking for `display_name,username` returned nothing rather than partial
data. Request only what your scopes cover.

### Where the video actually lands

`SEND_TO_USER_INBOX` means a **notification in the TikTok mobile app's Inbox tab**, reading
*"Your video from <app> is ready."* Tapping it opens TikTok's editor with the video loaded.

It is **not** in the Drafts folder and **not** visible in TikTok Studio or anywhere on web.
Worth stating plainly in your own UI — the natural assumption is "drafts", and users will
hunt in the wrong place. Our platform page now says so explicitly.

### The pattern across all of it

Not one of these was a logic error. They were **configuration surfaces that only exist in a
vendor dashboard**, each invisible from the code, each producing an error that pointed
somewhere other than the cause:

| Symptom | Actual cause |
|---|---|
| Upload fails, API logs healthy | Bucket CORS |
| `redirect_uri` invalid on a correct-looking URL | Registered on prod, using sandbox key |
| `url_ownership_unverified` | Public URL on a domain you don't own |
| No display name stored | Requested a field outside granted scope |
| "Where's my video?" | Looking on web for a mobile-only notification |

The habit that shortened each one: **read the error body, then verify the assumption it
implicates — don't retry with a variation.** Checking `R2_PUBLIC_URL` in `.env` and `curl`-ing
the media URL took thirty seconds and settled the TikTok question outright.
