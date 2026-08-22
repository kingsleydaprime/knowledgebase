# Site Reliability Engineering

> **[Intermediate]** · What the discipline owns that DevOps doesn't: toil, on-call, incident command, blameless postmortems, and capacity planning.

[[devops/10-observability/01-observability-fundamentals|Observability fundamentals]] already covers the vocabulary — SLI, SLO, SLA, error budgets — and [[devops/devops-reference|the devops reference]] has the maths. **This note is deliberately about the other half: the operational practices that are what SRE actually looks like day to day**, and which the numbers exist to serve.

## The founding claim

*"SRE is what happens when you ask a software engineer to design an operations team."* — Ben Treynor, who started it at Google.

Two consequences follow, and both are more radical than they sound.

**Operational load is a bug, not a job description.** If a system needs constant human attention, that's a defect in the system. The engineer's response is to write software that removes the need, not to get better at the manual work.

**Reliability is a feature with a cost curve.** Each additional nine costs roughly an order of magnitude more than the last, and past some point the user cannot tell — their mobile network is less reliable than your 99.99% service. **So 100% is the wrong target for every system**, and the right question is "how unreliable are we allowed to be?"

## Toil — the concept the vault was missing

**Toil** is operational work that is:

- **Manual** — a human does it
- **Repetitive** — done the same way each time
- **Automatable** — a machine could do it
- **Tactical** — reactive, interrupt-driven
- **Devoid of enduring value** — the service is no better afterwards than before
- **Scaling linearly with the service** — twice the traffic, twice the work

Restarting a stuck service. Manually failing over a database. Copying a config to twelve servers. Approving a routine access request.

**Toil is not the same as overhead.** Meetings, planning, HR, email are overhead — necessary, non-engineering, unavoidable. Toil is specifically *engineering work a machine should be doing*.

The canonical practice is a cap: **SREs spend at most 50% of their time on operations, and at least 50% on engineering that reduces future operations.** The cap is enforced — if a team exceeds it, work is pushed back to the development team until the system improves.

**That enforcement is the entire mechanism, and it's the part usually dropped.** Without it, toil expands to fill available time, the team never gets to the automation, and "SRE" becomes a renamed sysadmin function. Which is what has happened in a large fraction of companies that adopted the title.

The measurement is simple and worth actually doing: categorise a week of your work into toil / engineering / overhead. Most people are surprised.

## On-call, done seriously

Being paged is the visible part of SRE and the part most easily done badly.

**What good looks like:**

- **Enough people.** Roughly 8+ in a rotation, so a shift comes round infrequently enough to have a life
- **Every page is actionable.** If a human can't do anything useful, it shouldn't be a page — it's a dashboard entry or a ticket
- **Every alert has a runbook** — what this means, how to check, how to mitigate
- **A hard cap on pages per shift.** Google's rule of thumb is ~2 incidents per 12-hour shift; more than that and there's no time to do the follow-up properly
- **Compensation** — time off in lieu or pay. Unpaid on-call quietly means nobody escalates a problem with the on-call system
- **Symptom-based alerting.** Page on "checkout error rate is burning the budget", not "CPU is at 81%"

**The failure mode is alert fatigue**, and it's insidious because it looks like diligence. A rotation with fifty pages a night trains humans to acknowledge and dismiss without reading, and then the one real incident is dismissed too. **Every noisy alert is actively making the system less reliable**, so deleting alerts is real reliability work.

## Incident response

Under pressure, unstructured response produces five people debugging the same thing and nobody talking to customers. The standard structure (borrowed from emergency services, via Google's IMAG) separates roles:

| Role | Owns | Does not |
|---|---|---|
| **Incident Commander** | Coordination, decisions, who does what | Debug. **The IC's hands stay off the keyboard** |
| **Operations lead** | Actually changing the system | Field questions |
| **Communications lead** | Status page, stakeholders, customers | Debug |
| **Planning** | Notes, timeline, handovers | Debug |

In a small incident one person holds all four. The point of naming them is that when it grows, the roles are already known and can be handed off explicitly.

**The order of operations that people get wrong: mitigate first, diagnose second.** Roll back, fail over, shed load, flip the feature flag. Understanding *why* is a task for after the users are served. It feels unsatisfying, and it is correct — the rollback is reversible, a live debugging session on a burning system is not.

## Blameless postmortems

Every significant incident gets a written postmortem: timeline, impact, what happened, why, what we're changing, with owners and dates.

**Blameless** does not mean "no cause identified". It means the analysis targets *systems and conditions*, not people. The reasoning is practical rather than kind: if naming a person is punished, people conceal detail, and you lose the information you need to fix the system. **The engineer who ran the bad command is your best source of evidence, and only if it's safe to be.**

The reframe: not *"why did Sam delete the table?"* but *"why was it possible to delete a production table with no confirmation, no backup verification, and no permission boundary?"* Sam is a proximate cause. The absence of guardrails is the actual one, and it's the only one you can fix — because the next person will make the same mistake.

**Action items must have owners and dates or the postmortem is theatre.** The most common organisational failure here is producing excellent documents that change nothing.

## Capacity planning

Genuinely SRE-owned and largely absent from the DevOps picture:

- **Organic growth** — normal traffic increase over time
- **Inorganic growth** — launches, marketing, seasonal spikes
- **Forecasting** against real numbers, not intuition
- **Load testing** to find where the system actually breaks, rather than where you assume it does
- **Provisioning for the forecast plus a margin**, and checking the margin is real

Autoscaling is not a substitute. Autoscaling reacts within its configured limits, needs headroom to scale *into*, and doesn't help when the constraint is a database connection pool, a third-party rate limit, or a quota. **The failures that hurt are the ones that scale nothing.**

## SRE vs DevOps, stated cleanly

| | **DevOps** | **SRE** |
|---|---|---|
| Optimises for | Delivery speed | **Reliability** |
| Owns | The path to production | **Behaviour in production** |
| Core artefacts | Pipelines, IaC, config management | SLOs, error budgets, runbooks, postmortems |
| Measures | Deploy frequency, lead time | Availability, latency, error rate, toil % |
| Paged for | Usually not | **Yes** |

They overlap heavily in skills — both need Linux, cloud, Kubernetes, networking, scripting. **What differs is what you're accountable for.** As [[foundations/software-engineering/03-the-engineering-roles|the roles note]] puts it: the honest way to tell roles apart is what failure you fear. DevOps fears a broken pipeline. **SRE fears the pager.**

## The four numbers that tie it together

DORA's research (published in *Accelerate*) found that speed and stability are **not** a trade-off — the same practices improve both, which is the empirical backing for this whole discipline:

- **Deployment frequency** — how often you ship
- **Lead time for changes** — commit to production
- **Change failure rate** — % of deploys causing degradation
- **Time to restore service** — how fast you recover

The first two are DevOps-shaped, the last two SRE-shaped, and elite performers are strong on all four simultaneously. **Which is the point: the argument between shipping fast and staying up was empirically wrong.**

## Related
- [[devops/10-observability/01-observability-fundamentals|observability fundamentals]] — SLI/SLO/SLA and error budgets, in depth
- [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|how delivery practice evolved]] — why SRE appeared when it did
- [[devops/12-sre-and-platform-engineering/03-platform-engineering|platform engineering]] — the next constraint
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability and reliability]] — how the nines compose
- [[backend/interview/01-production-debugging|production debugging]] — the same work at interview scale

*Source: [reference] — from the freeCodeCamp IT Fundamentals course (final module), with practices from Google's SRE book and the DORA/Accelerate research.*
