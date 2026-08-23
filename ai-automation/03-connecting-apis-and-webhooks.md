# Connecting APIs and Webhooks

> **[Intermediate]** · Auth, pagination, rate limits and idempotency — the four things that make an integration survive contact with production.

Most of a workflow's real complexity is here. The trigger and the happy path take ten minutes; **these four take the rest**, and skipping them is why automations that "worked yesterday" stop.

## Webhooks as triggers

A webhook node gives you a URL. The external service POSTs to it; your workflow runs.

**n8n gives you two URLs — test and production — and confusing them is the commonest beginner problem.** The test URL only listens while you're watching the editor. Register that one with the external service and everything works during development and silently stops when you close the tab.

**The four things a production webhook needs:**

**1. Verify it's genuinely from who you think.** A public URL accepts posts from anyone. Most providers sign the payload (Stripe, GitHub, Slack) — **verify the signature**, comparing with a constant-time check → [[cybersecurity/04-web-security/README|web security]].

**2. Respond fast.** Most providers time out in 3–30 seconds and will retry — or disable your endpoint after repeated failures. **Acknowledge immediately, then do the work asynchronously.** n8n's "respond immediately" mode exists for this.

**3. Expect duplicates.** Webhooks are **at-least-once**. Network hiccups, provider retries and your own timeouts all produce repeats → idempotency, below.

**4. Handle out-of-order delivery.** `updated` can arrive before `created`. If order matters, use the payload's own timestamp or version rather than arrival order → [[architecture/04-distributed-systems/README|distributed systems]].

## Authentication, in rough order of how often you meet it

| | How | Watch for |
|---|---|---|
| **API key** | Header or query param | Never in a query string — it lands in logs |
| **Bearer token** | `Authorization: Bearer …` | Expiry |
| **OAuth 2** | Redirect flow, refresh token | **n8n handles the dance** — the main reason to use an app node |
| **HMAC signature** | Sign the request body | Byte-exact canonicalisation; constant-time compare |
| **mTLS** | Client certificate | Rare, and awkward in hosted platforms |

**The rule everywhere: the credential lives in the credential store, never in the node's parameters and never in a Code node.** → [[devops/09-secret-management/README|secret management]]

## Pagination

**An API returning 100 results does not mean there are 100 results.** Three common shapes:

- **Offset/limit** — `?page=2&per_page=100`. Simple, and **drifts** if the underlying data changes between pages, so you can miss or duplicate rows
- **Cursor** — the response carries `next_cursor`. Stable under concurrent writes. **Prefer it when offered**
- **Link header** — `Link: <…>; rel="next"` (GitHub's style)

n8n's HTTP Request node has built-in pagination; the thing to get right is the **stop condition** — an empty page, a missing cursor, or a `has_more: false`. **A wrong stop condition either truncates silently or loops forever**, and the first is worse because nobody notices.

**And ask whether you should be paginating at all.** Pulling 40,000 records through a workflow every hour to find the three that changed is a design smell — use a webhook, or an incremental filter on `updated_since` → [[databases/README|databases]].

## Rate limits

Every API has them, and they're the most common cause of an automation that works at 10 items and fails at 1,000.

**The mechanisms:**
- **429 Too Many Requests**, usually with `Retry-After` — **honour it rather than guessing**
- **`X-RateLimit-Remaining` / `-Reset` headers** — throttle before you hit the wall
- **Token bucket**, allowing bursts up to a capacity

**In a workflow:** use **Split In Batches** to chunk, add a **Wait** node between batches, and configure retry-on-429 with **exponential backoff plus jitter**.

**Jitter matters and gets skipped.** Without it, everything that failed together retries together, and you rebuild the exact spike that caused the limit → [[architecture/04-distributed-systems/README|retry storms]].

## Idempotency — the one that prevents real damage

**Because retries and duplicate webhooks are guaranteed, every action with a side effect must be safe to perform twice.**

Three approaches, best first:

**1. Use the provider's idempotency key.** Stripe and others accept an `Idempotency-Key` header — the same key returns the original result rather than charging twice. **If the API offers this, use it.**

**2. Make the operation naturally idempotent.** "Set status to `paid`" is safe repeated; "add £10 to the balance" is not. **Prefer upserts and absolute values over increments** → [[backend/02-api-design/README|API design]].

**3. Deduplicate yourself.** Store the event id you've processed and skip repeats. n8n's "Remove Duplicates" node does this within a run; across runs you need a database or the static-data store.

**The failure this prevents is not theoretical: a webhook retried three times sending three invoices, or charging a card twice, is the standard automation incident.**

## Errors that aren't errors

**A 200 response does not mean it worked.** Plenty of APIs return `200 {"success": false, "error": "..."}`. If you only branch on the HTTP status, those pass straight through as successes and corrupt everything downstream.

**Check the body, not just the status** — and treat a schema you didn't expect as a failure rather than a shrug.

The classes worth handling separately:
- **4xx** — your fault. Retrying won't help (except **429**)
- **5xx** — their fault. Retry with backoff
- **Timeout** — **unknown.** The request may have succeeded. **This is exactly where idempotency saves you**

## Related
- [[ai-automation/05-error-handling-and-retries|error handling and retries]] — the workflow-level machinery
- [[ai-automation/02-n8n-core-concepts|n8n core concepts]]
- [[backend/02-api-design/README|API design]] — the other side of every integration
- [[foundations/networking/README|networking]] — what a timeout actually means

*Source: [reference] — written Aug 2026.*
