# Error Handling and Retries

> **[Intermediate]** · The difference between an automation and a production automation — and the failure mode that matters most is the silent one.

**A workflow that works is a demo. A workflow that fails correctly is a system.**

And the failure that costs most is not the loud one. It's the workflow that **stopped running three weeks ago** and nobody noticed, because nothing was expected to arrive.

## Classify the failure before you retry

Retrying the wrong class of error wastes quota and hides bugs:

| Class | Example | Response |
|---|---|---|
| **Transient** | 503, timeout, connection reset | **Retry with backoff** |
| **Rate limit** | 429 | Retry, **honouring `Retry-After`** |
| **Permanent — their fault** | 404, 410 | Don't retry. Route to an error branch |
| **Permanent — your fault** | 400, 401, 422 | Don't retry. **Alert a human** |
| **Ambiguous** | Timeout *after* the request landed | **Retry only if idempotent** |

**That last row is the dangerous one.** A timeout doesn't tell you whether the operation happened. Retrying a non-idempotent action after a timeout is how a customer gets charged twice → [[ai-automation/03-connecting-apis-and-webhooks|note 03]].

## Retries done properly

**Exponential backoff with jitter**, a maximum attempt count, and a cap:

```
attempt 1:  wait 1s  ± random
attempt 2:  wait 2s  ± random
attempt 3:  wait 4s  ± random
give up  →  error branch
```

**Jitter is the part that gets omitted and is the part that matters at scale.** Without it, every workflow that failed during a provider outage retries in lockstep the instant it recovers — and knocks it over again. That's a **retry storm**, and it's how a brief outage becomes a long one → [[architecture/04-distributed-systems/README|distributed systems]].

**Cap total attempts.** Infinite retries against a permanently broken endpoint is a slow-motion denial of service against yourself, with a bill attached.

## The error branch

n8n gives every node an **error output** and workflows an **error workflow** — a separate workflow that runs when this one fails.

**A useful error path does four things:**

1. **Capture context** — which workflow, which execution, which node, what input, what the error said
2. **Notify a human**, somewhere they'll see it
3. **Preserve the payload** so the work isn't lost — a database row, a queue, or a "failed" table
4. **Make replay possible** once the cause is fixed

**Point 3 is the one people skip**, and it's the difference between "we had an outage" and "we lost Tuesday's orders."

**A dead-letter table is the standard pattern** — the same idea as a message queue's DLQ, and worth having even at small scale.

## Alert on absence, not just presence

**The most valuable alert in this domain is the one for a workflow that didn't run.**

A failing workflow is loud. A workflow whose trigger quietly stopped — an expired OAuth token, a webhook the provider disabled after too many timeouts, a changed schedule — produces **no errors at all**. Everything looks green. The work simply stops.

**Two cheap defences:**

- **A heartbeat.** The workflow records a timestamp on each successful run, and a separate scheduled check alerts if it's stale
- **Volume alerting.** *"Fewer than 10 orders processed today"* catches what error alerting structurally cannot

**This is the same argument as symptom-based alerting in [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]]** — page on the user-visible outcome, not on internal causes. And it's the same instinct as **converting silent failure into loud failure** in [[foundations/systems-engineering/08-risk-and-failure-analysis|FMEA]]: the detection column, not the severity column, is usually what you can cheaply improve.

## Partial failure

**Item 47 of 100 fails. What should happen?**

There is no default answer — you must choose, and n8n makes you choose per node:

- **Stop the whole run** — right when items are related and a partial result is wrong
- **Continue, routing failures to the error output** — right for independent items. **Usually correct**, and it needs the failed items captured
- **Continue and ignore** — almost never right, and it's the setting that silently drops data

**The question that decides it: is this batch a transaction, or 100 independent jobs?** Sending 100 unrelated emails is the latter. Writing 100 rows that must be consistent is the former, and that probably wants a real database transaction rather than a workflow → [[databases/08-transactions-and-acid|transactions]].

## Timeouts

**Set one everywhere.** A node with no timeout can hang for the platform's maximum, holding a worker slot and blocking the queue.

Workflow-level timeouts matter too — a run that legitimately takes 10 minutes and one that's stuck look identical without one.

## Testing failure deliberately

**You cannot claim a workflow handles errors if you've never seen it fail.** Cheap ways to check:

- Point a node at a deliberately wrong URL, or a bad credential
- Feed a malformed payload through the webhook
- Revoke a token and confirm the alert fires
- Send a duplicate webhook and confirm the idempotency check holds
- Return a 429 (many APIs have a sandbox that will)

**This is chaos engineering at the smallest possible scale**, and it takes twenty minutes → [[architecture/04-distributed-systems/15-testing-distributed-systems|testing distributed systems]] · [[foundations/systems-engineering/06-verification-and-validation|V&V]].

## Related
- [[ai-automation/03-connecting-apis-and-webhooks|connecting APIs and webhooks]] — idempotency
- [[ai-automation/06-self-hosting-n8n|self-hosting]] — where the alerting runs
- [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]] — alerting philosophy
- [[devops/10-observability/README|observability]]

*Source: [reference] — written Aug 2026.*
