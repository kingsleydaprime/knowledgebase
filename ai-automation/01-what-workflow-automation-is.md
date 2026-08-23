# What Workflow Automation Is

> **[Beginner]** · Triggers and actions — and the specific point at which a platform beats a pile of cron scripts.

Workflow automation is **connecting systems that weren't designed to talk to each other**, so that something happening in one causes something to happen in another, without a person in the middle.

A form submission creates a CRM record, posts to Slack, and sends a templated email. An invoice PDF lands in a mailbox, gets its fields extracted, and appears in the accounting system. A support ticket is classified and routed. **None of these are hard problems. All of them are tedious, and all of them break in the same handful of ways.**

## Triggers and actions

Every platform in this category has the same two primitives:

**Trigger** — what starts a run. A webhook, a schedule, a new row, a new email, a file appearing, a manual click.

**Action** — what happens next. Call an API, transform data, branch on a condition, write to a database, send a message.

A **workflow** is a graph of these. An **execution** is one run of it, with its own data and its own log.

**That's the whole model**, and its simplicity is the point — it's the same shape as an event-driven system → [[architecture/02-building-blocks/README|building blocks]], with the wiring done in a UI rather than in code.

## The honest question: why not just write a script?

**For one task, write the script.** A cron job calling two APIs is 30 lines and needs no platform.

The case for a platform appears at a specific threshold, and it's worth naming precisely — because adopting one too early is real overhead:

| You have | A script is fine | A platform starts winning |
|---|---|---|
| 1–3 automations | ✓ | |
| **Dozens, owned by several people** | | ✓ |
| One integration | ✓ | |
| **Many, each with its own auth** | | ✓ |
| You are the only maintainer | ✓ | |
| **Non-engineers need to change it** | | ✓ |
| Failures are rare and you notice | ✓ | |
| **You need retries, alerts, and an audit trail** | | ✓ |

**What you're actually buying** is not the ability to call an API — it's the surrounding machinery you'd otherwise build repeatedly:

- **Credential management** for 200 services, with OAuth flows handled
- **Execution history** — what ran, with what data, and what it returned
- **Retries, error branches and alerting** → [[ai-automation/05-error-handling-and-retries|note 05]]
- **A visual representation** a non-engineer can read and change
- **Scheduling and queueing** without you running a worker

**Fifty small scripts on a box nobody remembers is a genuine operational problem.** That's the failure mode this category exists to prevent, and it's why the argument is about *maintenance*, not capability.

## Where it sits against its neighbours

**Not the same as a CI/CD pipeline** → [[devops/06-ci-cd/README|CI/CD]]. Those are triggered by code changes and produce artefacts. Overlapping tooling, different job.

**Not the same as a durable workflow engine** — Temporal, AWS Step Functions, Airflow. Those are code-first, built for long-running, strongly-guaranteed, high-volume orchestration, and they're what you graduate to when the automation *is* the product → [[architecture/04-distributed-systems/README|distributed systems]].

**Not an ESB or an ETL tool**, though the boundaries blur. ETL moves bulk data on a schedule; this moves individual events reactively.

**The rough positioning:**

```
   script  →  automation platform  →  durable workflow engine
   (n8n, Zapier, Make)                (Temporal, Step Functions)

   one task            tens–hundreds        thousands/sec,
   one owner           several owners       exactly-once,
   fails silently      retries + history    survives anything
```

**Most teams need the middle column and reach for either end.**

## The landscape

| | Model | Self-host | Best at |
|---|---|---|---|
| **n8n** | Node graph, code when needed | **Yes** (fair-code) | Technical users; the default here |
| **Zapier** | Linear, huge app catalogue | No | Non-technical, breadth of integrations |
| **Make** | Visual, more branching power | No | Complex visual flows |
| **Temporal** | **Code-first** | Yes | Durable, high-scale, engineering-owned |
| **Airflow / Dagster** | Code-first DAGs | Yes | Scheduled data pipelines |

**This folder uses n8n** because it's self-hostable (so the data stays yours), node-based but with real code escape hatches, and its concepts transfer to the others → [[ai-automation/02-n8n-core-concepts|note 02]].

## Where the AI part comes in

The recent shift: an LLM is now just **another node** in the graph. That makes a category of previously-impossible automation trivial —

- **Classification** — is this email a bug, a billing query, or spam?
- **Extraction** — pull the total, date and supplier from this invoice
- **Generation** — draft a reply for a human to approve
- **Routing** — decide which branch this should take

**What it changes structurally:** automation used to require every input to be structured. **An LLM node lets a workflow accept messy human input** — free text, a PDF, an email — and produce something the rest of the graph can branch on.

**What it doesn't change:** the model can be wrong, so anything consequential needs a human in the loop or a validation step → [[ai-automation/04-ai-agent-workflows|note 04]] · [[using-ai/06-verifying-what-it-tells-you|verifying what it tells you]].

## Related
- [[ai-automation/02-n8n-core-concepts|n8n core concepts]] — the tool
- [[ai-automation/README|the domain index]]
- [[ai-ml/03-ai-engineer/README|AI engineer]] — building the models this orchestrates
- [[devops/06-ci-cd/README|CI/CD]] — the neighbour it's confused with

*Source: [reference] — written Aug 2026 against the plan this folder's README had carried since July.*
