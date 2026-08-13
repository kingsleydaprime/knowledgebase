# SocioBoom — How It All Fits Together

The whole system in one place: what each piece is for, and a trace of a single post from
keystroke to Instagram. Read this before the domain files — they go deep on parts, this
gives you the shape.

Written 2026-08-12, after the media pipeline and the Instagram/TikTok integrations.

---

## 1. The Moving Parts

Five processes, three of which you run locally:

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Next.js    │────▶│  Express    │────▶│  PostgreSQL  │
│  :3000      │     │  API :5000  │     │  :5432       │
└──────┬──────┘     └──────┬──────┘     └──────────────┘
       │                   │
       │                   ▼
       │            ┌─────────────┐     ┌──────────────┐
       │            │   Redis     │◀────│   Worker     │
       │            │   :6379     │     │  (separate   │
       │            └─────────────┘     │   process)   │
       │                                └──────┬───────┘
       │                                       │
       ▼                                       ▼
┌─────────────┐                        ┌──────────────┐
│ Cloudflare  │◀───────fetches─────────│  Facebook /  │
│     R2      │                        │  Instagram / │
└─────────────┘                        │  TikTok / …  │
                                       └──────────────┘
```

| Piece | Job | Fails how |
|---|---|---|
| **Next.js** | UI, composer, previews. Talks only to the API. | Nothing publishes; API unaffected |
| **Express API** | Auth, CRUD, presigning uploads, queueing jobs. **Never publishes.** | UI dead, scheduled posts still publish |
| **PostgreSQL** | Users, posts, accounts, analytics | Everything stops |
| **Redis + BullMQ** | The job queue — delayed publishing, retries | Posts save but never publish |
| **Worker** | The only thing that talks to social platforms | **Posts save, nothing publishes, silently** |
| **Cloudflare R2** | Media. Public so platforms can fetch it. | Image/video posts fail, text fine |

**The most common local confusion:** forgetting `pnpm dev:worker`. The UI works, posts save,
success toasts appear, and nothing is ever published — because nothing is consuming the
queue.

---

## 2. Why the Worker Is a Separate Process

Publishing is slow and unreliable in ways HTTP requests shouldn't be:

- A post is scheduled for **next Tuesday**. No request can wait that long.
- Instagram video needs **polling for up to a minute** while it transcodes.
- Platforms fail transiently and need **retry with backoff**.
- One post may hit **five platforms**, some succeeding and some not.

So the API's only job at publish time is to put a row in Postgres and a job in Redis. The
worker does everything hard. This also means the API can restart mid-publish without losing
anything — the job is in Redis, not in memory.

---

## 3. Trace: One Instagram Post, End to End

**① Upload — the file never touches the API**

```
Browser                    API                    R2
  │─── POST /media/presign ─▶│
  │◀── { uploadUrl, key } ───│   (signed, 5 min, content-type + length pinned)
  │──────────── PUT bytes ──────────────────────────▶│
  │─── POST /media/confirm ─▶│─── HEAD object ──────▶│
  │◀── MediaItem ────────────│   (verify it exists)
```

The middle step bypasses the server entirely. `express.json` caps bodies at 10kb, and
streaming 500MB through Node would occupy the process for the whole upload.

**② Compose and submit**

The composer holds `MediaItem[]` in React state and POSTs everything at once:

```json
{ "content": "...", "platforms": ["instagram"], "media": [...], "scheduledAt": "..." }
```

**③ API validates and queues** — `post.service.ts`

- Ownership: every media key must start with `uploads/u{userId}/`
- Platform rules: Instagram requires media, TikTok requires video
- Writes the `Post` row, then `postQueue.add(..., { delay })`

`delay` is `max(0, scheduledAt - now)`, so "Post Now" is just a delay of zero — the same
path, not a special case.

**④ Worker publishes** — `worker.ts`

```
re-read post from DB          ← honours edits made after queueing
for each platform:
  load account → ensureFreshToken() → publish → store externalId
```

Two details that matter:

- **`publishedPlatforms` in job data.** If Instagram succeeds and TikTok fails, the retry
  skips Instagram. Without it, retries double-post.
- **The post is re-read from the DB**, not taken from the job payload, so editing a
  scheduled post actually changes what gets published.

**⑤ Instagram specifically** — `instagram.ts`

```
POST /{ig-user}/media          → container id     (video_url + caption)
GET  /{container}?status_code  → poll until FINISHED   ← video only
POST /{ig-user}/media_publish  → live
```

Instagram fetches the video **from R2**, which is why the bucket must be public.

**⑥ Status and metrics**

Worker sets `published` / `partial` / `failed`; failures also write a `Notification`. The
calendar polls while anything is mid-flight. Separately, an hourly job re-reads engagement
counts into `PostAnalytic`.

---

## 4. Where State Lives

| State | Home | Notes |
|---|---|---|
| Post content, schedule, status | `posts` | `media` is JSON, not a table |
| Platform post ID + metrics | `post_analytics` | `externalId` is how metrics are fetched later |
| OAuth tokens | `accounts` | **Encrypted at rest** |
| Pending publish jobs | Redis | Lost if Redis is wiped — posts stay `scheduled` forever |
| Uploaded files | R2 | Only the URL is in Postgres |

The `accounts` table has one non-obvious convention: **`accessToken` is not always a user
token.** For Facebook and Instagram it's a *Page* token, and `refreshToken` holds a
long-lived *user* token used to re-derive it. See
[[projects/socioboom/learning/backend/10-media-and-social-publishing|10-media-and-social-publishing]].

---

## 5. The Publish Path Per Platform

| Platform | Endpoint | Media | Async? |
|---|---|---|---|
| X/Twitter | `POST /2/tweets` | Not implemented | No |
| LinkedIn | `POST /v2/ugcPosts` | Not implemented | No |
| Reddit | `POST /api/submit` | Not implemented | No |
| Facebook | `/{page}/feed` · `/photos` · `/videos` | URL | No |
| Instagram | container → `media_publish` | URL | **Yes — poll** |
| TikTok | `inbox/video/init/` → `status/fetch/` | URL, **verified domain** | **Yes — poll** |

Text-only platforms silently ignore attached media; the composer warns about this at compose
time rather than dropping files at publish time.

---

## 6. Reading the System When Something Breaks

Work down the pipeline — each stage has a distinct signature:

1. **Browser console / Network** — upload failures (CORS shows as a cancelled PUT with no
   status code)
2. **API terminal** — validation, presigning, queueing. A 201 here means *saved*, not
   *published*
3. **Worker terminal** — the only place publish errors exist. Platform error bodies are
   logged verbatim
4. **`pnpm diagnose:meta`** — what Meta actually grants, versus what you think it does
5. **The database** — `SELECT status FROM posts` is the ground truth

The rule that saved the most time: **a success toast means queued, not published.** Any
question of the form "did it post?" is answered in the worker terminal or the `posts` table,
never in the browser.

---

## Related
- [[projects/socioboom/learning/backend/11-integration-playbook|11-integration-playbook]] — the process for adding a platform
- [[projects/socioboom/learning/backend/10-media-and-social-publishing|10-media-and-social-publishing]] — storage and platform APIs in depth
- [[projects/socioboom/learning/backend/05-queues-and-jobs|05-queues-and-jobs]] — BullMQ mechanics
- [[projects/socioboom/learning/frontend/09-media-uploads|frontend/09-media-uploads]] — the browser side
