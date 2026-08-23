# AI Automation

Orchestrating APIs and models into runnable workflows, rather than a pile of cron scripts.

**~5,500 words across 6 notes.** Built August 2026 against the plan this folder had carried since July. `[reference]`.

> **The one idea:** this category is not about the ability to call an API — you can already do that. **It's about everything around the call**: credentials for twenty services, execution history, retries, alerting, and a representation someone else can change. **Fifty small scripts on a box nobody remembers is the problem it exists to prevent.**

## Why this exists

Until now this folder was a **219-word stub** with a planned reading order and nothing behind it — the only genuinely empty domain in the vault. The plan was good, so these six notes are that plan, written.

**Distinct from [[ai-ml/README|ai-ml/]]**, which is about how models work. This is about *orchestrating* them — and everything else — into workflows.

## Reading order

1. [[ai-automation/01-what-workflow-automation-is|What Workflow Automation Is]] — **[Beginner]** — triggers and actions, **the specific threshold where a platform beats scripts**, the landscape, and where LLMs changed the category
2. [[ai-automation/02-n8n-core-concepts|n8n Core Concepts]] — **[Beginner]** — nodes, executions, credentials, **the array-of-items data model that confuses everyone**, and where the visual model stops helping
3. [[ai-automation/03-connecting-apis-and-webhooks|Connecting APIs and Webhooks]] — **[Intermediate]** — auth, pagination, rate limits, and **idempotency, which is the one that prevents real damage**
4. [[ai-automation/04-ai-agent-workflows|AI and Agent Workflows]] — **[Intermediate → Advanced]** — the four uses ranked by safety, structured output, agent guardrails, **and prompt injection as the security model**
5. [[ai-automation/05-error-handling-and-retries|Error Handling and Retries]] — **[Intermediate]** — classifying failures, backoff with jitter, dead-lettering, **and alerting on absence**
6. [[ai-automation/06-self-hosting-n8n|Self-Hosting n8n]] — **[Intermediate]** — Docker and Postgres, the encryption key, queue mode, **and when self-hosting is the wrong call**

## The things worth carrying

1. **You're buying the machinery around the call, not the call** → [[ai-automation/01-what-workflow-automation-is|01]]
2. **n8n passes an *array of items*, and most nodes run once per item automatically.** Almost every beginner confusion resolves to this → [[ai-automation/02-n8n-core-concepts|02]]
3. **When a workflow needs more than a handful of Code nodes, it wanted to be a service.** The platform's advantage is integration and operations, not logic → [[ai-automation/02-n8n-core-concepts|02]]
4. **Webhooks are at-least-once. Assume duplicates** → [[ai-automation/03-connecting-apis-and-webhooks|03]]
5. **A timeout doesn't tell you whether it happened** — which is exactly why idempotency exists → [[ai-automation/03-connecting-apis-and-webhooks|03]]
6. **A 200 doesn't mean it worked.** Check the body → [[ai-automation/03-connecting-apis-and-webhooks|03]]
7. **Schema-constrained output is well-formed, not correct** → [[ai-automation/04-ai-agent-workflows|04]]
8. **If you can draw the flowchart, draw it.** An agent is for when you can't → [[ai-automation/04-ai-agent-workflows|04]]
9. **A workflow with an LLM and tools executes instructions from anyone who can get text in front of it.** Least privilege on tools is the strongest control → [[ai-automation/04-ai-agent-workflows|04]]
10. **Jitter, or a provider outage becomes a retry storm** → [[ai-automation/05-error-handling-and-retries|05]]
11. **The most valuable alert is for the workflow that *didn't* run.** A stopped trigger produces no errors at all → [[ai-automation/05-error-handling-and-retries|05]]
12. **Lose `N8N_ENCRYPTION_KEY` and every credential is unrecoverable** — back it up separately from the database → [[ai-automation/06-self-hosting-n8n|06]]
13. **Prune execution data, or the disk fills.** The commonest self-hosting incident → [[ai-automation/06-self-hosting-n8n|06]]

## Where this connects

| | |
|---|---|
| [[ai-ml/03-ai-engineer/README\|AI engineer]] | **The depth behind note 04** — agents, structured output, evals, prompt injection |
| [[backend/02-api-design/README\|API design]] | The other side of every integration |
| [[devops/02-docker/README\|Docker]] · [[devops/04-vps/vps-setup\|VPS]] | What self-hosting runs on |
| [[devops/09-secret-management/README\|secret management]] | The credential-store argument |
| [[architecture/04-distributed-systems/README\|distributed systems]] | Retries, ordering, at-least-once |
| [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering\|SRE]] | Alerting philosophy, applied small |

## The honest note

**`[reference]`, and this one has a sharp version of the problem** — I have not run an n8n instance, self-hosted or otherwise. **Every operational claim here is read, not earned**, which matters more in this domain than in a theoretical one, because the whole subject *is* operations.

**What would close the gap, cheaply:**

1. **`docker compose up` the file in note 06** and build one workflow that does something you actually want. **An afternoon**, and it makes notes 02 and 06 concrete
2. **Break it on purpose** — wrong credential, malformed webhook, revoked token. Note 05 is a list of claims until you've watched each one
3. **Send the same webhook twice** and see whether your workflow does the thing twice. **Most first workflows do**
4. **Put a classification node in front of something real** — your own email, say — and keep a golden set of 20 cases. That's note 04's argument, verified
5. **Then let it run for a month** and see what actually breaks. Nothing else surfaces the absence-alerting problem

**What's missing:** Zapier/Make/Temporal in any depth (mentioned, not covered), the n8n Code node and custom nodes properly, queue mode operationally, workflow testing strategy, cost modelling at volume, and anything on the compliance side of processing personal data through third-party models.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[ai-ml/README|AI & ML]] — the models this orchestrates
- [[README|Vault README]] · [[BUILD-PLAN|Build Plan]]
