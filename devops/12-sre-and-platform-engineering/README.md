# SRE and Platform Engineering

The disciplines that come *after* DevOps — and why each of them exists because the previous one succeeded.

**~5,400 words across 4 notes.** Built August 2026. `[reference]`.

> **The one idea:** Waterfall, Agile, DevOps, SRE, platform engineering and DevSecOps are not competing philosophies or a seniority ladder. **Each solved the bottleneck the previous one created by working.** Optimise any stage of a pipeline and the constraint relocates — that's the whole sequence.

## Why this exists

`devops/` had eleven sections covering the **tools** — pipelines, Terraform, Kubernetes, Prometheus — and [[devops/devops-reference|devops-reference]] had two paragraphs on the **disciplines** that decide how those tools get used. The vault knew what an error budget was ([[devops/10-observability/01-observability-fundamentals|observability 01]] covers SLI/SLO/SLA properly) but had **zero occurrences of "toil"**, nothing on on-call design, incident command or blameless postmortems, one passing mention of Internal Developer Platforms, and no note on DevSecOps at all.

**So: the vocabulary of the roles the vault is preparing you to hold, which existed everywhere in job ads and nowhere in these notes.**

## Reading order

**Read 01 first — the other three are its branches.**

1. [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|How Delivery Practice Evolved]] — **[Beginner]** — five transitions, each fixing the last one's bottleneck. **The spine of the folder**
2. [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|Site Reliability Engineering]] — **[Intermediate]** — toil and the 50% cap, on-call design, incident command, blameless postmortems, capacity planning, DORA's four
3. [[devops/12-sre-and-platform-engineering/03-platform-engineering|Platform Engineering]] — **[Intermediate]** — the two ways a DevOps team breaks, the IDP, golden paths not golden cages, and **cognitive load as the actual thesis**
4. [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]] — **[Intermediate]** — what runs at which pipeline stage, SAST vs SCA vs DAST, SBOMs, policy as code, and **the alert fatigue that kills most rollouts**

## The things worth carrying

1. **Each era created the next era's problem by succeeding.** Agile made dev fast → ops became the wall. DevOps fixed the wall → nobody owned production. SRE fixed that → the DevOps team didn't scale → [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|01]]
2. **They coexist. "We've moved past DevOps" is nearly always a misreading** — the platform is built by people doing DevOps work → [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|01]]
3. **The error budget turns a values argument into arithmetic.** Nobody debates reliability vs features; the number decides → [[devops/12-sre-and-platform-engineering/01-how-delivery-practice-evolved|01]]
4. **Toil is automatable manual work that scales with the service** — distinct from overhead, and capped at 50% *with enforcement*. Drop the enforcement and SRE becomes a renamed sysadmin role → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|02]]
5. **Every noisy alert makes the system less reliable.** Deleting alerts is real reliability work → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|02]]
6. **Mitigate first, diagnose second.** The rollback is reversible; live debugging on a burning system isn't → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|02]]
7. **Blameless isn't kindness, it's evidence collection.** Punish the name and you lose the detail you needed → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|02]]
8. **A central DevOps team becomes the wall it was created to remove** — and embedding engineers instead just trades the queue for twelve incompatible setups → [[devops/12-sre-and-platform-engineering/03-platform-engineering|03]]
9. **Golden paths, not golden cages.** Mandatory means teams route around it invisibly → [[devops/12-sre-and-platform-engineering/03-platform-engineering|03]]
10. **Measure users' outcomes, not the platform's output.** Time-to-first-deploy, not modules shipped → [[devops/12-sre-and-platform-engineering/03-platform-engineering|03]]
11. **If your platform must be understood *in addition to* the tools underneath, it made things worse** → [[devops/12-sre-and-platform-engineering/03-platform-engineering|03]]
12. **SCA is the highest-value scanner for most teams** — most of your code is code you didn't write → [[devops/12-sre-and-platform-engineering/04-devsecops|04]]
13. **A scanner nobody acts on is worse than none** — it converts a known gap into false confidence → [[devops/12-sre-and-platform-engineering/04-devsecops|04]]
14. **A leaked secret isn't fixed by deleting the commit.** Rotate first, clean history second → [[devops/12-sre-and-platform-engineering/04-devsecops|04]]

## Where this connects

| | |
|---|---|
| [[devops/10-observability/README\|10-observability/]] | **The prerequisite.** SLI/SLO/SLA and error budgets live there; note 02 deliberately doesn't repeat them |
| [[devops/06-ci-cd/README\|06-ci-cd/]] | The pipeline all four notes assume |
| [[devops/11-delivery-and-advanced/01-gitops\|GitOps]] | The deploy mechanism most IDPs sit on |
| [[cybersecurity/README\|cybersecurity]] | Note 04's other half, at depth |
| [[foundations/software-engineering/03-the-engineering-roles\|the engineering roles]] | What each of these is like to *hold* as a job |
| [[architecture/01-system-design-fundamentals/03-availability-and-reliability\|availability]] | Where the nines come from |

## The honest note

**`[reference]`, and unusually so — three of these four are organisational disciplines, and you cannot validate an organisational discipline by reading about it or by building a toy.** A one-person project has no dev/ops wall, no ticket queue, no on-call rotation and no cognitive-load problem. The conditions that make these ideas necessary are conditions of scale.

**What would close the gap, honestly ranked:**

1. **Define one real SLO on something you actually run** — including the bit everyone skips: decide in advance what you'll *stop doing* when the budget is gone. **Note 02 is theatre until that decision is real**
2. **Write a postmortem for a failure you caused.** Blameless is easy when it's someone else. It's a genuinely different exercise on your own mistake, and it's the one worth doing
3. **Track a week of your own work as toil / engineering / overhead.** Cheap, and usually uncomfortable
4. **Add SCA to one repo** — Dependabot or Trivy, ten minutes. Then actually resolve what it finds, which is the part that teaches you why baselining exists
5. **Add secret scanning with a pre-commit hook**, then deliberately try to commit a fake AWS key and watch it fail
6. **Build the smallest possible golden path** — one `create-service` script producing a repo with CI, a Dockerfile and a dashboard already wired. Note 03 at a scale of one, and it still teaches the trade
7. **The reading:** the Google [*SRE Book* and *SRE Workbook*](https://sre.google/books/) (free); *Accelerate* (Forsgren, Humble, Kim) for the DORA evidence; *Team Topologies* (Skelton & Pais) for the cognitive-load argument note 03 rests on

**What's missing:** chaos engineering in any depth (it's in [[devops/devops-reference|devops-reference]] and [[architecture/04-distributed-systems/15-testing-distributed-systems|distributed systems testing]]), FinOps and cost as a reliability constraint, progressive delivery specifics, compliance frameworks (SOC 2, ISO 27001 — see [[cybersecurity/08-governance-risk-and-compliance/README|GRC]]), and anything about the politics of actually introducing these to an organisation that hasn't asked for them, which is the hardest part in practice.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[devops/README|DevOps]] — the folder this closes
- [[devops/00-the-physical-layer/README|00-the-physical-layer/]] — the other end of the same course
- [[INTERVIEW|Interview Prep Index]]
- [[BUILD-PLAN|Build Plan]]
