# SocioBoom — Playbook: Adding a Social Platform

The ordered process, derived from actually shipping Facebook Pages, Instagram and TikTok in
August 2026. Sections 1–7 of
[[projects/socioboom/learning/backend/10-media-and-social-publishing|10-media-and-social-publishing]]
cover *what* each API does; this covers *what order to do things in and why*, which is where
the time actually went.

The headline finding: **roughly 80% of the elapsed time was vendor dashboard configuration,
not code.** Every integration was written in an afternoon and took days to make work. Plan
accordingly.

---

## Phase 0 — Research Before Writing Anything

An hour here saved days each time. Answer these before opening an editor:

1. **Can it do what you want at all?** Facebook removed personal-profile publishing
   entirely. That's not a permission, it's gone. Instagram requires a professional account.
   Check capability before designing around it.
2. **What does it require that you don't have yet?** Instagram and TikTok fetch media by
   URL, which meant public file storage had to exist first. That reordered the entire
   project.
3. **Does the redirect URI need https? A verified domain?** TikTok needs both. That means a
   tunnel and a real domain before a single line runs.
4. **Is there an approval process, and how long?** Meta and TikTok are both 2–4 weeks.
   Start them early; they run in parallel with everything else.
5. **Is there a sandbox, and does it have separate credentials?** TikTok's does.

**Verify against the vendor's own current docs, not blog posts or memory.** Meta's app
creation flow, Graph API versions, and TikTok's scope model had all changed relative to
what tutorials described.

---

## Phase 1 — Prerequisites You Cannot Automate

These are account-level facts about the *human*, and they block everything downstream:

| Platform | Prerequisite |
|---|---|
| Facebook | A **Page** you administer. Personal profiles cannot be published to. |
| Instagram | A **professional** account (Business or Creator), linked **to that Page** |
| TikTok | A verified domain for media; an account listed as a sandbox Target User |

The Instagram case is the subtle one: **linking Instagram to your personal Facebook profile
is a different relationship** from linking it to a Page. Meta calls both "linking". Only the
Page link is visible to the API.

Do these first. Every hour spent debugging OAuth before the prerequisites exist is wasted.

---

## Phase 2 — Dashboard Configuration

The step that consumed the most time, and the least interesting to debug.

**Permissions live in more than one place.** With Meta this bit hard: a permission must be
added to the **use case**, *then* selected in the **Facebook Login for Business
configuration**, *then* granted at consent. Miss any layer and it silently isn't requested —
no error, it just isn't in the token. `pages_manage_posts` was missing for three rounds of
debugging because it was absent from the use case, so it never appeared in the configuration
picker.

**Sandbox config is separate from production config.** A TikTok redirect URI registered on
the production app is invisible to a sandbox key — and the error says only `redirect_uri`,
on a URL that looks perfectly correct.

**Grants are frozen at consent time.** Changing dashboard permissions does nothing to tokens
you already hold. **Always disconnect and reconnect** after touching configuration. Not
doing this produced several false "the fix didn't work" conclusions.

---

## Phase 3 — Code, in Dependency Order

Only now. The shape is the same each time:

1. **`shared/services/<platform>.ts`** — publish, fetch metrics, refresh token. Pure
   functions, no Express, no Prisma.
2. **`OAUTH_CONFIG` entry** in `account.controller.ts` — auth URL, token URL, scopes, plus
   any deviation flags (`clientIdParam`, `redirectBase`, `pkce`).
3. **Callback branch** — capture `platformUserId` and `username`. Store the token you'll
   actually *publish* with, which is often not the one OAuth handed you.
4. **`switch` case in the worker** — the publish call.
5. **Refresh function** + entry in `REFRESH_WINDOW_MS`.
6. **Frontend** — `platformIcons`, `PLATFORM_META`, any media requirement.

Keep deviations at the config layer rather than branching everywhere. TikTok's `client_key`
and https-only redirect are both one optional field on the config object, not scattered
`if (platform === 'tiktok')` checks.

---

## Phase 4 — Build a Diagnostic Before You Need One

`pnpm diagnose:meta` was written after the third round of guessing, and immediately paid for
itself twice. It asks the platform directly, using the token already stored, and reports a
**verdict per feature**:

```
✗ Facebook Page publishing — missing: pages_manage_posts
✓ Instagram publishing
```

That turns "connection failed" into an exact permission name in one second.

**Write this on the first integration, not the third.** The cost is twenty minutes; the
alternative is repeatedly guessing which of four dashboard layers is wrong.

---

## Phase 5 — Test in Isolating Order

Each step proves one thing, so a failure has one cause:

1. **Connect** → check the DB stored the right IDs and handle
2. **Text-only post** → proves the token and the simplest endpoint
3. **Image post** → proves media, storage, public URLs
4. **Video post** → proves the async polling, the piece most likely to differ from the docs
5. **Metrics** → proves `externalId` capture

Use **Post Now**, not scheduling. Waiting on a scheduler while debugging wastes the loop.

---

## Phase 6 — Submit for Review Immediately

Once dev-mode works. Review is the critical path — 2–4 weeks — and everything else can
continue while it runs.

Note TikTok's catch-22: the demo recording must be made with the API *while still
restricted*, so record a private-visibility post. Do this while the flow is fresh; you have
just performed exactly the sequence they want to see.

Trim unused permissions before submitting. Ours accumulated `pages_messaging`,
`instagram_manage_messages`, `read_insights` and others that arrived with use cases and are
never called. Reviewers ask why each is requested, and unused ones invite rejection.

---

## The Failure Table

Every real failure in this project, and what it actually was:

| Symptom | Actual cause | Layer |
|---|---|---|
| Upload fails, API logs clean | Bucket CORS policy missing | Vendor config |
| `redirect_uri` invalid, URL looks right | Registered on prod, using sandbox key | Vendor config |
| `url_ownership_unverified` | Media on a domain you don't own | Vendor config |
| Consent succeeds, `/me/accounts` empty | `pages_show_list` not granted | Vendor config |
| Permission missing after reconnect | Not added to the **use case** | Vendor config |
| Permission missing after config change | Didn't reconnect — grants are frozen | Process |
| No display name stored | Requested a field outside granted scope | Code |
| "Where's my video?" | Mobile-only inbox notification | Understanding |
| Post saved, never published | Worker not running / `delay > 0` bug | Code |

**One of nine was a logic error.** The rest were configuration, process, or a wrong mental
model. That ratio is the single most useful thing to carry to the next integration.

---

## Habits That Paid Off

- **Read the error body, don't retry a variation.** TikTok returns errors as HTTP 200 with
  an `error` field; Meta buries the reason in `err.response.data.error.message`. The
  message almost always named the problem.
- **Verify the assumption the error implicates.** `grep R2_PUBLIC_URL .env` plus one `curl`
  settled the TikTok domain question in thirty seconds, after a round of theorising.
- **Check state directly rather than inferring.** Querying `accounts` proved the Facebook
  Page token was stored correctly; guessing from UI behaviour would not have.
- **Make errors actionable at the point of failure.** `no_pages` now links to Page creation.
  The user hitting it is the least equipped to translate a code into an action.

---

## Related
- [[projects/socioboom/learning/00-how-it-fits-together|00-how-it-fits-together]] — the system shape
- [[projects/socioboom/learning/backend/10-media-and-social-publishing|10-media-and-social-publishing]] — per-platform API detail
- [[backend/05-auth/03-oauth-provider-integrations|OAuth provider integrations]] — the transferable version
- `socioboom/setup/nextsteps.md` — the live checklist
