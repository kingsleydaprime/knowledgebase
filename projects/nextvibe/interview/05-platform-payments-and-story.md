# NextVibe — Platform, Payments, AI & Project Story

From [`../learning/09-devops.md`](../learning/09-devops.md),
[`../learning/backend/03-modules.md`](../learning/backend/03-modules.md),
[`04-games-ai.md`](../learning/backend/04-games-ai.md),
[`../learning/00-sys-design.md`](../learning/00-sys-design.md).

---

### Q1. [Advanced] 🔥🔥 Your service kept getting OOM-killed on a 512MB instance. Diagnose it.

**Strong answer covers the arithmetic, which is the whole answer:** the AI generator called
OpenRouter with `max_tokens: 60000`. Holding a response of that size in Node — token buffers, JSON
parse buffers, intermediate strings — costs roughly **240 MB per request**. On a 512 MB Render
instance that leaves ~270 MB for Prisma connections, cached queries and active sessions. One AI
request plus normal traffic crossed the limit and the platform killed the process.

**The fix — per-game-type token caps, justified by the actual output shape:**
```ts
const maxTokens = dto.gameType === 'WORD_PUZZLE' ? 8000 : 4000;
```
`WORD_PUZZLE` returns a full 10×10 grid (100 cells) plus hidden-word metadata, so it genuinely needs
more; trivia and the true/false formats have compact question shapes where 4,000 covers ten
questions per round comfortably. Memory impact: ~16 MB per request at 4,000 tokens, ~32 MB at 8,000
— both fine on 512 MB.

**The extra step worth naming:** `node --max-old-space-size=400 dist/main.js`, so V8 garbage-collects
aggressively before the platform's hard limit rather than after it. Without it, Node happily grows
toward a limit it doesn't know exists.

**The lesson to state:** `max_tokens` is not just a cost parameter, it's a **memory allocation
decision** — and a generous default set for convenience became a production outage. On a constrained
instance, every buffer size is a capacity plan.

---

### Q2. [Advanced] 🔥🔥 MinIO has two URLs. Explain why, and the bug it caused.

**Strong answer covers the distinction:**

| Variable | What it is | Who uses it |
|---|---|---|
| `MINIO_ENDPOINT` | Where **NestJS** connects to MinIO | Server-to-server |
| `CDN_BASE_URL` / `MINIO_EXTERNAL_URL` | Where **clients** fetch files from | Browsers, mobile apps |

They can legitimately be different addresses for the *same* instance: inside a Docker network the
server reaches it at `minio:9000`, while a browser must use `https://files.yourdomain.com`.

**The bug:** MinIO moved to Railway and `MINIO_ENDPOINT` was updated, but `CDN_BASE_URL` was left at
the local dev value `http://localhost:9000/nextvibe`. So the server uploaded successfully and every
client got a URL pointing at **its own machine** — uploads "worked", images were broken, and nothing
errored server-side.

**The generalisable lesson:** whenever one resource has an internal and an external address, they're
**two separate configuration values with two separate failure modes**, and only one of them is
exercised by your server's own health checks. A localhost value surviving into production is the
signature symptom.

---

### Q3. [Advanced] 🔥 How does a presigned URL signature actually work?

**Strong answer covers:** the server, holding the secret key, computes an HMAC over a canonical
description of the request — bucket, object key, HTTP method, expiry timestamp, and headers — and
appends it to the URL as query parameters. Storage recomputes the same HMAC with its copy of the key
and compares. Because the signature covers all of those fields, **changing any of them invalidates
it**: you can't reuse a PUT signature for a different key, a different method, or after the expiry.

**Why that's the security model:** the client never sees a credential, only a narrowly-scoped
capability with a deadline. The client-side details that matter: the request must be made *exactly*
as signed (extra headers can break it), and the bucket's CORS policy must allow the browser's direct
request.

---

### Q4. [Intermediate] 🔥 Why is the payments module webhook-driven?

**Strong answer covers:** the browser redirect after payment is **not** proof of payment — the user
can close the tab, lose connectivity, or never return, and none of that changes whether money moved.
The authoritative signal is the provider's server-to-server **webhook**. So the redirect is UX and
the webhook is truth.

**What the webhook handler must do, and this is the checklist they're listening for:**
1. **Verify the signature** — the endpoint is unauthenticated by definition, so anything that can
   POST could otherwise grant itself a ticket.
2. **Be idempotent** — providers retry, and at-least-once delivery means the same event will arrive
   twice. Key on the provider's event/reference id so a replay is a no-op.
3. **Respond fast, then do the work** — acknowledge quickly and process asynchronously, or the
   provider times out and retries, multiplying the load.
4. **Branch on event type** rather than assuming success, and handle the failure/cancelled cases
   explicitly.
5. **Handle out-of-order delivery** — a `success` may arrive after a `pending`, or vice versa.

---

### Q5. [Intermediate] Anything specific about integrating a Nigerian payment provider?

**Strong answer covers:** amounts in **NGN and in minor units** — providers commonly expect kobo, so
a naira figure sent unconverted is off by 100×, in whichever direction ruins your day. Never
represent money as a float; keep it as an integer of minor units end to end and format only at
display. Then the usual: webhook branching by status, and enriching notifications with the order
context so the user's email says what they bought rather than "payment received."

---

### Q6. [Advanced] 🔥 Why OpenRouter instead of calling a model provider directly?

**Strong answer covers:** one API and one key across many models, so the model choice becomes a
configuration value rather than an integration. That matters when the workload is
cost/quality-sensitive and you want to move between models as prices and capabilities change, or
fall back when one provider is degraded.

**The honest counterweight:** you add a hop and a dependency, you're subject to their availability
and margin, and you lose provider-specific features (prompt caching, provider-native tool formats,
structured-output guarantees) that only exist on the direct API. The rule is the same one as
`my-applicant`'s: **abstract when varying the thing is a requirement**, not because varying it is
conceivable.

---

### Q7. [Advanced] 🔥 Explain the guest-to-user merge pattern for anonymous game play.

**Strong answer covers:** anonymous play removes the signup wall, so the game must run with no
account — which means a guest identity (a client-generated or server-issued token) owns the session
and its results. When that person later signs up or logs in, their guest records must be **merged**
into the real account.

**The hard parts to name:** the merge must be idempotent (it will be retried); it must handle a guest
who logs into an account that **already has** results, so it's a merge and not an overwrite; and
there's an abuse question — a guest session that can be claimed by any account is a way to transfer
scores, so the claim needs to be tied to the session's own secret. Plus the "already played" guard
has to work across both identities, or merging hands someone a second attempt.

---

### Q8. [Advanced] 🔥 Tell me about a bug where two parts of the system disagreed.

**Strong answer covers — pick one and be precise:**
- **The `paymentRequired` disagreement** — an `EventPlan` null guard meant one code path concluded
  payment was required and another didn't, from the same underlying data. Same class as the ranking
  disagreement in Arete: **one fact, two computations**. The fix is one function owning the answer.
- **`mapType` enum keys not matching the backend exactly** — the frontend's enum drifted from the
  backend's, so a value serialised fine and matched nothing. The structural fix is generating shared
  types from one source rather than maintaining two enums by hand.
- **`correctAnswerIndex` vs `correctAnswer`** — the game page compared the wrong field, so answers
  were scored against an index. Two representations of the same concept coexisting is the root
  cause, not the comparison.

**The pattern across all three:** duplicated definitions of one truth. Every fix is "make there be
one."

---

### Q9. [Intermediate] Your word puzzle had a serialisation bug. What happened, and what did the audit find?

**Strong answer covers:** the game's config had to survive a round trip — created in a wizard,
stored, then read back by the play page — and the shape written wasn't the shape expected, so the
grid didn't reconstruct. The broader activity worth describing is **auditing an implementation
against the design spec**: going feature by feature through the spec and checking what the code
actually does, which is how you find the gaps that no test covers because nobody wrote a test for
the requirement they forgot.

**The related cleanup:** identifying dead code — functions that had become unreachable — and removing
them, because unreachable code reads as intent and misleads the next person debugging.

---

### Q10. [Intermediate] 🔥 What breaks between dev and prod, in your experience?

**Strong answer covers, from the notes:** environment variables that were never updated for the new
environment (the `CDN_BASE_URL` localhost bug is the canonical one); CORS, which is permissive in dev
and exact in prod; cookie flags (`Secure` / `SameSite`) that behave differently over https; memory
limits that only exist on the deployed instance; and build-time versus run-time env vars — a value
inlined at build time can't be changed by editing the platform's settings afterwards, which produces
"I changed the variable and nothing happened."

**The habit:** read the **server startup logs** on first boot rather than assuming success. A process
that starts and then fails to reach a dependency looks identical from outside to a healthy one, and
the logs are where the difference is visible.

---

### Q11. [Intermediate] What is "robust process error handling" at the Node level?

**Strong answer covers:** `unhandledRejection` and `uncaughtException` handlers that **log and exit**
rather than log and continue — after an uncaught exception the process is in an unknown state, and
staying alive means serving requests from a corrupted runtime. Combined with a process manager or
platform that restarts on exit, the right behaviour is to fail fast and come back clean. Graceful
shutdown belongs alongside: close DB connections and sockets on `SIGTERM` so a deploy doesn't drop
in-flight work.

---

### Q12. [Advanced] 🔥 How would you improve this codebase, given a month?

**Strong answer covers a ranked list with reasons, not a wishlist:**
1. **Tests on the money and authorisation paths** — the bugs that cost the most (phantom followers,
   `paymentRequired` disagreement) were both silent and both in that category.
2. **One source of truth for shared types** — generate the frontend's types from the backend's
   schema, killing the enum-drift and field-name-mismatch class entirely.
3. **Structured logging with request correlation** — currently a single user action spanning webhook,
   service and socket produces three unlinked log streams.
4. **Rate limiting and webhook signature verification** as an explicit audit, not a per-endpoint
   memory.
5. **Consolidate duplicated flows** — the Google-vs-regular login cookie divergence is the template
   for that whole bug family.

---

### Q13. [Intermediate] 🔥 What's your mental model for being a good engineer, from this project?

**Strong answer covers — pick two and mean them:**
- **Find which end of the pipeline is broken before poking the middle.** One grep diagnosed the
  notification system.
- **Anything with a consequence is derived server-side.** Capacity from tier, identity from token,
  price from the catalogue — never from the client.
- **Duplicated definitions of one truth are the root cause of most cross-cutting bugs.** Two login
  paths, two enums, two rank formulas, two field names.
- **Silent failures deserve more design attention than loud ones.** Every serious bug in this project
  threw nothing at all.

---

### Q14. [Beginner] Explain NextVibe to a non-technical interviewer.

**Strong answer covers:** it's a platform for events — organisers set up an event and sell tickets,
attendees buy them, chat with each other in real time, and play AI-generated games during the event.
The technically interesting parts are keeping everyone's screens in sync live, and making sure money
and tickets are handled correctly even when someone closes their browser mid-payment.

That last clause is the hook: it names the hard problem in a sentence a non-engineer understands.
