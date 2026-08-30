# 03 — Backend / API (Route Handlers, validation, transactional email)

Part of the [[projects/kingsley-iheme/learning/README|kingsley-iheme learning log]]. Siblings: [[projects/kingsley-iheme/learning/01-frontend|01-frontend]] · [[projects/kingsley-iheme/learning/02-sanity|02-sanity]] · [[projects/kingsley-iheme/learning/04-devops|04-devops]].

General reference: [[backend/02-api-design/README|backend/api-design]] · [[backend/README|backend]].

---

## 0. The whole backend is one file

`src/app/api/contact/route.ts` — 70 lines. No database, no ORM, no auth, no session store.

That's worth stating plainly rather than apologising for. This is a **JAMstack-ish** shape: content lives in a hosted CMS, scheduling in a hosted booking tool, email in a hosted mail API, and the "backend" is one function that validates a form and calls someone else's API.

**The judgement being exercised is what you *didn't* build.** A contact form is the canonical excuse to add Postgres, a `submissions` table, an admin dashboard to read them, and auth to protect the dashboard. All of that would be real work, real running cost, real maintenance, and real GDPR exposure — to reimplement, badly, a thing called "an inbox" that the client already owns and checks daily.

Knowing when the answer is *no persistent store* is a senior instinct. The relevant question is never "could I build this?" but **"what does this project actually need to keep, and who reads it?"** Here the answer is: nothing, and Kingsley, in Gmail.

The corollary is honest too: the moment he wants to search past enquiries, track response times, or attach files, this decision flips and you add the store. A right-sized decision has a stated expiry condition.

---

## 1. Route Handlers

In the App Router, an API endpoint is a `route.ts` file exporting functions named after HTTP methods:

```ts
// src/app/api/contact/route.ts  →  POST /api/contact
export async function POST(request: Request) { ... }
```

Two things worth noticing:

**It's the Web Fetch API, not a framework abstraction.** `request` is a standard `Request`; you return a standard `Response`. Not Express's `(req, res)`, not `res.status(200).json(...)`. The same handler code is conceptually portable to Cloudflare Workers, Deno, Bun's server — the platform-specific part is the file location, not the function body.

**Only `POST` is exported, and that's the security posture.** Any other verb — `GET`, `PUT`, `DELETE` — automatically gets a **405 Method Not Allowed** with no code from you. A `GET` handler here would be actively wrong: a form submission mutates state (sends mail), and a GET endpoint that sends email can be triggered by an `<img src>` tag on any page on the internet. Exporting only what you implement is a free, correct default.

`NextResponse.json()` is a thin Next helper over `Response.json()` — sets `Content-Type` and serialises. `NextResponse` is used here purely for convenience; plain `Response.json()` would work identically.

---

## 2. Validation, hand-rolled — and where it's right and wrong

There's no Zod, no Yup, no validation library. Read the sequence, because the *order* is the design:

### Step 1 — configuration check, before anything else

```ts
if (!RESEND_API_KEY) {
  return NextResponse.json({ error: "not_configured" }, { status: 503 });
}
```

**First line of the handler.** Fail before parsing a body you have no ability to act on. This is the same graceful-degradation stance as [[projects/kingsley-iheme/learning/02-sanity|`sanityFetch`]] — but done *better*, because it's explicit rather than silent (see §4).

### Step 2 — parse defensively

```ts
let body: unknown;
try { body = await request.json(); }
catch { return NextResponse.json({ error: "invalid_body" }, { status: 400 }); }
```

`request.json()` **throws** on malformed JSON. Unwrapped, that throw becomes an unhandled rejection and a 500 — telling the caller "server error" when the truth is "your request was malformed." A 500 says *my fault*; a 400 says *your fault*. Getting that boundary right is the difference between an alert that wakes you and one that shouldn't.

Note the type: **`unknown`, not `any`.** `any` would let every subsequent property access compile unchecked. `unknown` forces the narrowing that follows. This is the single highest-value TypeScript habit for anything crossing a trust boundary — `any` disables the type system exactly where you need it most.

### Step 3 — narrow and check

```ts
const { name, email, interest, message } = (body ?? {}) as Record<string, unknown>;

if (typeof name !== "string" || !name.trim() ||
    typeof email !== "string" || !email.trim() ||
    typeof message !== "string" || !message.trim()) {
  return NextResponse.json({ error: "missing_fields" }, { status: 400 });
}
```

`typeof x !== "string"` handles a client sending a number, an array, `null`, or an object. `!x.trim()` handles the whitespace-only string that passes a `required` HTML attribute and means nothing. Both checks are needed and neither implies the other.

**Why `(body ?? {})` matters:** `JSON.parse("null")` succeeds and yields `null`. Destructuring `null` throws a TypeError → unhandled → 500. One `??` converts a crash into a clean 400. It's the kind of edge that only shows up under a fuzzer or a bad client, which is precisely why it's worth writing on purpose.

### Step 4 — allowlist the enum

```ts
const INTERESTS = new Set(["ghostwriting","editing","tutoring","translation",
                           "transcription","counseling","other"]);
const safeInterest =
  typeof interest === "string" && INTERESTS.has(interest) ? interest : "other";
```

**This is the most instructive line in the file.** Two decisions in it:

**Allowlist, not blocklist.** The set of valid values is enumerated; anything else is rejected. Blocklists fail because you must anticipate every bad input. Allowlists fail closed. This is the general rule for *all* untrusted enum-ish input — [[cybersecurity/04-web-security/README|web security]] is largely applications of it.

**And it coerces rather than rejects.** Unlike the fields above, an invalid `interest` doesn't 400 — it silently becomes `"other"`. That's the right call *here* and it's worth being able to say why: `interest` is a routing hint for a human reading an email, not data anything depends on. Rejecting the whole message because a dropdown value was odd would lose a real enquiry from a real potential client to protect a field that only affects a subject line. **Match validation strictness to what the field actually does.** Reject what you can't proceed without; coerce what's merely advisory.

Also note: **the `INTERESTS` list is duplicated** between the server (`route.ts`, a `Set` of values) and the client (`contact-form.tsx`, an array of `{value, label}`). They can drift — adding an option to the form dropdown without adding it to the server Set means that choice silently becomes "other". Not a security hole (the server is the one that decides, which is the correct direction), but a real maintenance trap. The fix is to derive both from one exported constant in `src/lib/`, the way `sessionTypes` and `navLinks` already are.

### Step 5 — format check

```ts
if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
  return NextResponse.json({ error: "invalid_email" }, { status: 400 });
}
```

Read it: one-or-more non-space-non-`@`, an `@`, same again, a `.`, same again. Deliberately loose.

**Loose is correct, and this is a hill worth understanding.** The RFC 5322 grammar for a valid address is notoriously baroque (quoted strings, comments, IP literals). The "perfect" email regex is a famous 6,000-character monster, and it *still* can't tell you whether the mailbox exists. Meanwhile every over-strict regex on the internet has rejected somebody's legitimate address — `+` tags, new TLDs, apostrophes.

So the real job splits in two: this regex catches *typos and obvious junk* cheaply; **only sending mail proves an address works.** Validate loosely at the edge, verify by delivery. (Related habit — [[cybersecurity/04-web-security/README|ReDoS]]: this pattern is safe because the character classes exclude the delimiters, so there's no ambiguity for the engine to backtrack through. Nested quantifiers over overlapping classes are where email regexes become a denial-of-service vector.)

### Should this use Zod?

For four fields, no — the hand-rolled version is explicit, dependency-free, and completely readable. At ten fields with nested objects it becomes error-prone and the answer flips. The genuine advantage of a schema library isn't fewer lines; it's that **`z.infer` gives you a TypeScript type derived from the validator**, so the type and the runtime check can't disagree. That's the same argument as TypeGen in [[projects/kingsley-iheme/learning/02-sanity|02 §8]]: one source of truth beats two that agree today.

---

## 3. Sending: Resend, and the `replyTo` trick

```ts
const resend = new Resend(RESEND_API_KEY);

const { error } = await resend.emails.send({
  from: FROM_EMAIL,
  to: CONTACT_EMAIL,
  replyTo: email.trim().slice(0, 320),
  subject: `New message from ${name.trim().slice(0, 200)} (${safeInterest})`,
  text: `From: ${name.trim().slice(0, 200)} <${email.trim().slice(0, 320)}>\nInterest: ${safeInterest}\n\n${message.trim().slice(0, 5000)}`,
});
```

### Why `from` is you and `replyTo` is them

The naive version sets `from: <the visitor's address>` so the email "comes from" them. **That fails**, and understanding why is core email knowledge:

**SPF** (Sender Policy Framework) is a DNS record listing which servers may send mail for a domain. **DKIM** cryptographically signs outgoing mail with a key published in the sender's DNS. **DMARC** tells receivers what to do when those checks fail. If Resend sends mail claiming to be `from: someone@gmail.com`, Gmail's SPF record does not list Resend — the message fails authentication and goes to spam or is rejected outright. That's not a bug; it's the entire anti-spoofing system doing its job.

So: **send as yourself, set `replyTo` to them.** The mail authenticates cleanly under *your* domain, and hitting Reply in the inbox addresses the visitor. Same ergonomics, no forgery.

`RESEND_FROM_EMAIL` defaults to `onboarding@resend.dev` — Resend's shared sandbox sender, which works immediately without DNS setup and is rate-limited and deliverable only to your own verified address. Fine for development; **a real domain with SPF/DKIM records is required before launch**, or the forwarded enquiries land in spam. That's a launch-checklist item, not a code change.

### Length caps at the boundary

`.slice(200)` on name, `.slice(320)` on email, `.slice(5000)` on the message. Nothing upstream enforces these — the HTML form has no `maxlength` and, more to the point, **anyone can POST directly to `/api/contact` with curl**, bypassing the form entirely. The client is not a validation layer; it's a convenience layer.

320 isn't arbitrary: it's the practical maximum length of an email address (64-char local part + `@` + 255-char domain). The caps bound the payload sent to a third-party API and prevent a 10MB message body from becoming your problem.

Two honest gaps in the same area:

**No rate limiting.** A script can POST this endpoint in a loop and flood the inbox — and burn the Resend quota. Genuinely the biggest missing piece. The cheap fixes, in ascending order: a honeypot field (a hidden input that only bots fill in, ~5 lines, catches most naive spam), an IP-keyed limiter in Upstash/Vercel KV, or Cloudflare Turnstile. Worth doing before the site gets any traffic, since spam bots find contact forms fast.

**No `Content-Type` check.** The handler doesn't verify the request declares JSON. Low impact — `request.json()` fails on non-JSON anyway and returns the clean 400 from Step 2 — but checking the header is one line and makes the contract explicit.

---

## 4. Status codes as a client contract

This is the part most worth internalising, and it's genuinely well done.

| Condition | Status | `error` code | Meaning |
|---|---|---|---|
| No API key configured | **503** | `not_configured` | *Service unavailable — nobody's fault, not set up* |
| Malformed JSON | 400 | `invalid_body` | Caller's fault |
| Missing/blank fields | 400 | `missing_fields` | Caller's fault |
| Bad email format | 400 | `invalid_email` | Caller's fault |
| Resend rejected it | **502** | `send_failed` | *Upstream dependency failed* |
| Sent | 200 | — | ✅ |

**503 vs 502 vs 400 is a real distinction, not decoration.**

- **400** — you sent me something I can't use. Fixable by the caller. Don't retry unchanged.
- **502 Bad Gateway** — I understood you, I tried, *my upstream* (Resend) failed. Not your fault. **Retrying may well work.**
- **503 Service Unavailable** — I'm not in a position to do this at all right now. Retrying is pointless until a human changes something.

Because the codes are honest, the client can react correctly without parsing prose:

```tsx
// src/components/contact-form.tsx
if (res.status === 503) { setStatus("not_configured"); return; }
if (!res.ok)            { setStatus("error"); return; }
setStatus("success");
```

Two different messages result:

```tsx
{status === "not_configured" && <p>The contact form isn't connected yet — email me directly using the button above.</p>}
{status === "error"          && <p>Something went wrong sending that. Try again, or email me directly using the button above.</p>}
```

The first says *don't bother retrying, use this other route*. The second says *try again*. A single generic "something went wrong" would send visitors into a retry loop against an endpoint that structurally cannot succeed — and lose the enquiry.

**And both paths point at the direct mailto link.** That's the whole graceful-degradation philosophy in one detail: *there is always a way to reach Kingsley*, and the form failing degrades to a slightly less convenient path rather than a dead end. Every failure mode has an exit.

### The contrast worth carrying forward

Compare this to `sanityFetch`'s bare `catch {}` ([[projects/kingsley-iheme/learning/02-sanity|02 §4]]). Same codebase, same author, opposite outcomes:

| | Contact API | `sanityFetch` |
|---|---|---|
| "Not configured" | explicit 503 | indistinguishable from empty |
| "Broken" | explicit 502 | indistinguishable from empty |
| Client can tell them apart | ✅ | ❌ |

The API models *not-configured*, *caller-error* and *upstream-broken* as three different things. The CMS fetcher collapses all three into "no content." **The API is the pattern to copy; the fetcher is the one to fix.** Having both in one small project is a useful side-by-side.

### One gap: nothing is logged on the 502

```ts
if (error) {
  return NextResponse.json({ error: "send_failed" }, { status: 502 });
}
```

Resend's SDK returns `{ data, error }` rather than throwing — a deliberate design that forces you to check rather than letting a rejection escape. Good. But `error` holds the actual reason — invalid API key, domain not verified, rate limit exceeded, recipient suppressed — **and it's discarded**. When a client reports "your contact form doesn't work," there is nothing in the Vercel function logs to read.

```ts
if (error) {
  console.error("[contact] resend send failed:", error);
  return NextResponse.json({ error: "send_failed" }, { status: 502 });
}
```

Note what is deliberately *not* done: the detail is logged server-side and **not** returned in the response body. Internal error detail in an HTTP response is an information-disclosure issue — it can leak infrastructure details, key states, and third-party account structure to anyone probing the endpoint. **Log verbosely inward; respond tersely outward.**

---

## 5. The client half

```tsx
// src/components/contact-form.tsx
type Status = "idle" | "submitting" | "success" | "not_configured" | "error";
const [status, setStatus] = useState<Status>("idle");
```

**A single status union rather than several booleans.** Compare the alternative: `isSubmitting`, `isSuccess`, `isError`, `isNotConfigured` — four booleans, sixteen representable combinations, of which twelve are nonsense (`isSuccess && isError`?). One union has exactly five states, all valid, and TypeScript will flag an unhandled one.

**Make illegal states unrepresentable.** It's a small instance of a large idea, and it's why the same pattern appears in [[projects/kingsley-iheme/learning/02-sanity|the `postType` discriminator]].

```tsx
const form = event.currentTarget;   // ← captured BEFORE the await
const data = new FormData(form);
...
form.reset();                       // ← used AFTER
```

Subtle and worth knowing: React reuses synthetic events, and `event.currentTarget` is **null after an `await`** in an async handler. Capturing `form` into a local before the network call is what makes `form.reset()` work afterwards. The bug this avoids ("cannot read properties of null") is confusing precisely because the code *looks* sequential.

**Uncontrolled inputs.** No `useState` per field — `FormData` reads the DOM at submit time. Less code, fewer re-renders, and `form.reset()` clears everything in one call. Controlled inputs earn their cost when you need live validation, cross-field logic, or formatting as you type; a contact form needs none of that. Note also `required` on the inputs and `type="email"` — browser-native validation is free, accessible, and localised, and it means most bad submissions never reach the network. It's a UX layer on top of the server checks, never a replacement.

The `<label htmlFor>` / `id` pairing on every field is the accessibility basics done right: screen readers announce the label, and clicking the label focuses the input.

---

## 6. Cal.com: the integration with no backend at all

Booking has **zero** server code. `@calcom/embed-react` mounts an iframe; availability, timezone maths, confirmation emails, calendar sync and rescheduling all happen in Cal.com.

The only "backend" is a typed config array:

```ts
// src/lib/cal-sessions.ts
export const CAL_USERNAME = process.env.NEXT_PUBLIC_CAL_USERNAME || "";
export const sessionTypes: CalSessionType[] = [
  { slug: "counseling-intro-call", label: "Intro call", duration: "15 min", description: "..." },
  ...
];
```

**Estimate what building this properly would cost:** availability windows, timezone conversion (with DST), double-booking prevention under concurrency, confirmation and reminder emails, cancellation and reschedule flows, calendar sync. That's weeks, and it's a category of problem — calendars and timezones — that is famously, disproportionately hard to get right.

The whole thing is an iframe and a config array. **Recognising which problems to hand to someone who has already solved them is a skill, not a shortcut** — and the tell is when a feature sounds simple ("let people book a call") but decomposes into a known-hard domain.

The same array feeds three things — the picker buttons, the Cal link (`${username}/${selected.slug}`), and the JSON-LD `OfferCatalog` on `/counseling`. One source of truth for UI, integration, and SEO. See [[projects/kingsley-iheme/learning/01-frontend|01 §8]] for the `key`-remount detail that makes switching sessions actually work, and for the copy bugs sitting in this array.

---

## Takeaways

1. **The best backend decision here was not building one.** Ask what the project needs to *keep*, and who reads it — then state the condition that would flip the decision.
2. **Export only the HTTP methods you implement.** Everything else 405s for free, and a `GET` that sends email is triggerable by an `<img>` tag.
3. **Parse untrusted input as `unknown`, never `any`**, and wrap `request.json()` — it throws, and an unwrapped throw turns the caller's mistake into your 500.
4. **`(body ?? {})`** — `JSON.parse("null")` is valid JSON and destructuring it crashes.
5. **Allowlist enums; match strictness to consequence.** Reject what you can't proceed without, coerce what's merely advisory.
6. **Validate email loosely; delivery is the real test.** Over-strict regexes reject real people and can be a ReDoS vector.
7. **`from` = you, `replyTo` = them.** SPF/DKIM/DMARC will spam-bin mail that claims to come from a domain you can't sign for.
8. **Cap lengths server-side.** The client isn't a validation layer — anyone can curl the endpoint.
9. **Status codes are a contract.** 400 = your fault, 502 = upstream broke (retry), 503 = not set up (don't). Honest codes let the client give honest advice.
10. **Log inward, respond outward.** Discarding the upstream error object leaves you blind; returning it leaks internals.
11. **One status union beats four booleans.** Make illegal states unrepresentable.
12. **Capture `event.currentTarget` before the `await`.**
13. **Rate limiting is the real gap here** — a honeypot field is ~5 lines and catches most of it.
