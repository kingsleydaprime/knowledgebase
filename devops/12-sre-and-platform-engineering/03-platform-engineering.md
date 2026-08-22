# Platform Engineering

> **[Intermediate]** · The Internal Developer Platform, golden paths, and treating your own infrastructure team's output as a product with users.

The discipline exists because of a specific, well-documented failure: **DevOps succeeded, and then stopped scaling.**

## The two ways a successful DevOps team breaks

**Centralised: the team becomes a ticket queue.**

A central platform/DevOps team ends up owning Kubernetes, CI/CD, Terraform, secrets, observability, cloud accounts, networking and security posture — across every product team, each with a different stack. The surface area grows with the number of teams; the team does not. Work arrives as tickets, tickets queue, and product teams wait days for a database or a pipeline.

**The team invented to remove the wall between dev and ops has become a new wall.**

**Decentralised: everyone reinvents everything.**

The obvious fix is to embed a DevOps engineer in each product team. Now each team has its own Terraform conventions, its own pipeline, its own base images, its own idea of what "secure" means. Consequences:

- **No standardisation** — twelve ways to deploy a service
- **No reuse** — the same problem solved twelve times
- **No governance** — you cannot enforce a policy across twelve bespoke setups
- **No portability** — engineers can't move between teams, and neither can knowledge
- **Uneven security** — some teams get it right; you find out which ones during an incident

**Neither is a staffing problem, so neither is fixed by hiring.** They're structural.

## The reframe

Platform engineering's answer is to change the unit of delivery: **stop delivering infrastructure as a service humans perform, and start delivering it as a product teams consume.**

Concretely: the platform team builds an **Internal Developer Platform (IDP)** — a self-service layer where a product engineer can get a repository, a pipeline, an environment, a database, monitoring and a deploy **without a human in the path**.

Centralised standards. Decentralised execution. The expertise is encoded in the platform instead of being dispensed through a queue.

## What an IDP actually contains

Not a single product — an integration layer over tools you already run:

| Capability | What the developer gets | Typically built on |
|---|---|---|
| **Service scaffolding** | A new service, correct from minute one | Templates, Backstage, Cookiecutter |
| **Environments** | Dev/staging/preview on demand | Terraform/Crossplane, namespaces |
| **CI/CD** | A working pipeline, already wired | GitHub Actions, GitLab CI, Argo |
| **Deployment** | Ship without knowing Kubernetes | Argo CD, Flux, Helm |
| **Observability** | Dashboards and alerts pre-attached | Prometheus, Grafana, OTel |
| **Secrets** | Injected, never in a repo | Vault, External Secrets |
| **Data** | A database with backups configured | Operators, cloud APIs |
| **Catalogue** | Who owns what, and how to reach them | Backstage |

The interface can be a portal, a CLI, a set of pull-request templates, or a Kubernetes CRD. **The interface matters far less than whether the developer waits for a person.**

## Golden paths, not golden cages

**A golden path is the supported, paved, opinionated way to do a common thing.** Use it and you get scaffolding, pipeline, monitoring, security review and on-call integration for free.

The critical design property is that it is **paved, not mandatory.**

- **Cage:** "you must deploy this way." Teams with a genuinely different need are blocked, resent the platform, and route around it — usually badly, and usually invisibly
- **Path:** "this way is so much easier that you'll want it." Teams with unusual needs step off, accept that they now own the operational burden themselves, and everyone understands the trade

**Roughly 80% of services should be on the path.** If it's much lower, the platform doesn't fit the work. If it's 100%, you've almost certainly blocked something legitimate, or nobody is trying anything new.

## Platform as a product — the part that's actually hard

The technical work is the easy half. **The discipline that distinguishes platform engineering from "we built some Terraform modules" is treating internal developers as users.**

That means, unglamorously:

- **The platform has users, and adoption is voluntary in spirit even when it isn't in policy.** If teams avoid it, that's product feedback, not disobedience
- **A roadmap, and a way to request things**
- **Documentation that a new hire can follow alone.** The measure is whether they can ship on day one without asking anyone
- **Versioning and deprecation policies** — you cannot break your users on a Tuesday
- **Support**, and a real one
- **Measured outcomes**, not measured output

**The metrics that matter are about the users, not the platform:**

- **Time to first deploy for a new service** — the headline number. Days → minutes is the whole value proposition
- **Time for a new engineer to ship to production**
- **Adoption rate** — what fraction is on the golden path
- **Cognitive load** — how many tools must a product engineer understand? (Ask them. The answer is usually worse than the platform team believes)
- **DORA's four**, since the platform's purpose is to improve them → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|note 02]]

Note what's absent: number of modules shipped, tickets closed, services onboarded. **Those measure the platform team's activity, not its users' outcomes** — and optimising them produces a busy team and unhappy developers.

## Cognitive load is the actual thesis

The clearest statement of why any of this exists comes from *Team Topologies*: **a product team can only hold so much in its head.** Every tool it must understand — Kubernetes, Terraform, Helm, Prometheus, the cloud IAM model, the CI DSL — takes space that could have been the business domain.

A platform's job is to **reduce the intrinsic and extraneous load** so the team's capacity goes to the problem it was hired to solve. That is why "make developers learn Kubernetes properly" is not an alternative solution: it's a proposal to spend every product team's scarcest resource on undifferentiated work.

It also gives the honest failure test. **If your platform adds a layer developers must understand *in addition to* the underlying tools, it has increased cognitive load and made things worse.** Plenty of real internal platforms fail exactly here — a leaky abstraction that requires knowing both it and Kubernetes, which is strictly worse than knowing only Kubernetes.

## Does it kill DevOps?

No — and the confusion is worth clearing up because it's common in job ads.

**The platform team is doing DevOps work.** Building an IDP requires deep CI/CD, IaC, Kubernetes, cloud and security skill. What changed is the *delivery model*: that expertise is encoded into a product rather than dispensed as a service.

**In practice:**
- **Large organisations** — a distinct platform team, product teams consuming it, SREs on critical services
- **Small ones** — the same three or four people wear all the hats, and "platform engineer" in the job ad means *all of the above*

**Two honest cautions:**

**Don't build a platform for four teams.** Below a certain size the cost exceeds the benefit and you should just have good defaults and shared modules. The problem being solved here is a *scaling* problem — applying the solution before you have the problem produces an expensive internal product with three users.

**Buying doesn't skip the work.** Backstage, Humanitec, Port and friends are frameworks, not platforms. The integration, the opinions and the golden paths are yours to define, and they're where the actual value is.

## Related
- [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|how delivery practice evolved]] — the bottleneck this answers
- [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]] — the discipline it sits beside
- [[devops/11-delivery-and-advanced/01-gitops|GitOps]] — the deploy mechanism most IDPs are built on
- [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|infrastructure as code]] — what gets encoded into the platform
- [[foundations/software-engineering/01-what-software-engineering-is|what software engineering is]] — abstraction, and how a bad one costs you twice

*Source: [reference] — from the freeCodeCamp IT Fundamentals course (final module), extended with Team Topologies, the CNCF platforms white paper, and Backstage/Humanitec documentation.*
