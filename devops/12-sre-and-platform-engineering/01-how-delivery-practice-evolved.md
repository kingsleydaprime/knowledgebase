# How Delivery Practice Evolved

> **[Beginner]** · Waterfall → Agile → DevOps → SRE → Platform Engineering → DevSecOps. Five transitions, each one solving the bottleneck the previous one created.

Job ads treat these as a pile of interchangeable buzzwords. They aren't. **Each is a response to a specific bottleneck that the previous approach produced by succeeding** — which means the sequence is causal, and knowing the causes tells you which one a given organisation actually needs.

The whole thing is one pattern repeated: *speed up one stage, and the bottleneck moves to the next stage.*

## Waterfall — batch the whole thing

Requirements → design → code → test → deploy → maintain, each phase completing before the next begins. A release every six to twelve months.

It is not stupid. It's the right shape when requirements genuinely are fixed, change is expensive, and you can't ship a patch — building a bridge, certifying avionics, pressing a CD-ROM.

**Where it fails is when requirements change during the six months**, which for most software is always. And because integration and testing happen only at the end, every mistake made in month one is discovered in month five, when it is at its most expensive to fix.

**The bottleneck:** the batch size. Feedback arrives once, far too late.

## Agile — shrink the batch

Ship in two-to-four-week increments. Gather requirements continuously. Test as you go.

The insight is smaller than the industry that grew around it: **most of Agile's benefit comes from reducing batch size**, which shortens the feedback loop, which means errors are found while they're cheap and while you still remember the code. See [[foundations/software-engineering/02-the-software-development-lifecycle|the SDLC]] — the phases didn't disappear, they got smaller and started repeating.

It worked. Development got dramatically faster. And that created the next problem.

**The bottleneck:** Agile transformed *development* and stopped at the handoff to operations. Dev now produced a release every two weeks; Ops still deployed monthly or quarterly, by hand, on a change-approval calendar. **Fast dev, slow ops.** Two teams with directly opposing incentives — development is measured on shipping change, operations on preventing change — separated by a wall and a ticket queue.

## DevOps — extend the loop past the handoff

DevOps deletes the wall. Same team, shared responsibility for the software from commit to production and beyond. Automate the handoff so it stops being a negotiation: [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD]], [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|infrastructure as code]], configuration management, automated testing, monitoring.

**DevOps didn't replace Agile — it extended Agile's loop across the phases Agile left alone.** Same idea, more of the pipeline.

The cultural claim underneath the tooling: *you build it, you run it.* Being on the hook for your own code in production changes the code you write, in a way no amount of review does.

**The bottleneck:** DevOps optimises for **delivery speed**, and quietly assumes that a deployed system will behave. Nobody in the model owns what happens after deploy — uptime, latency under real load, capacity planning, the 3 a.m. page, why it broke and what stops it recurring. "Ship faster" is a goal that, pursued alone, trades away reliability with no mechanism for noticing.

## SRE — make reliability an engineered quantity

Google's answer, and the reframe is sharp: **treat operations as a software problem, and treat reliability as something you can measure, budget and spend** rather than something you promise and hope for.

The mechanism is the [[devops/10-observability/01-observability-fundamentals|SLO and error budget]]: pick an availability target, and the shortfall becomes a budget. Budget remaining → ship aggressively. Budget exhausted → stop shipping features and stabilise.

**This is the important structural move, and it's easy to miss.** It converts the dev-vs-ops argument from a values dispute into arithmetic. Nobody has to argue about whether to prioritise reliability; the number decides, and both sides agreed to the number in advance.

SRE and DevOps are **not alternatives and not competitors.** DevOps says *what* should be true (shared ownership, automation, fast feedback). SRE is *one prescriptive implementation* with specific practices and specific numbers. Most organisations that have both run them as complementary: DevOps owns the path to production, SRE owns behaviour in production. → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|note 02]]

**The bottleneck:** none of this scales the *DevOps team itself.*

## Platform Engineering — stop the enabler becoming the queue

Two failure modes appear once DevOps succeeds and the organisation grows.

**One: the central DevOps team becomes the new wall.** They now own Kubernetes, pipelines, Terraform, secrets, observability, cloud accounts and security posture, across every team's differing stack. They are overwhelmed, so they become a ticket queue — and a queue in front of the team whose entire purpose was removing queues. **DevOps has recreated the bottleneck it was invented to delete.**

**Two: the obvious fix makes it worse.** Embed a DevOps engineer in each product team instead. Now every team has its own tools, its own pipeline conventions, its own security posture. No standardisation, no reuse, no portability of people, and no way to enforce a policy anywhere.

Platform engineering resolves the dilemma by **changing the unit of work from tickets to a product**: build an [[devops/12-sre-and-platform-engineering/03-platform-engineering|Internal Developer Platform]] that lets product teams self-serve a repo, a pipeline, an environment, monitoring and a deploy — no human in the path. Centralised standards, decentralised execution.

It does not replace DevOps. **It's DevOps expertise, delivered as a product instead of as a service.** → [[devops/12-sre-and-platform-engineering/03-platform-engineering|note 03]]

**The bottleneck:** everything above optimises for speed, reliability and scale. None of it mentions security — and a pipeline that deploys forty times a day is a pipeline that can ship a vulnerability forty times a day.

## DevSecOps — put the security back in the loop

Security's traditional shape was a gate at the end: build for months, hand to security for a review, wait. Under weekly releases, that gate is either bypassed or it becomes the bottleneck.

DevSecOps distributes it instead: threat modelling in planning, static analysis on commit, dependency scanning on build, secret scanning and policy checks in CI, image scanning before deploy, runtime detection in production. **Automated, in the pipeline, owned by everyone.** → [[devops/12-sre-and-platform-engineering/04-devsecops|note 04]]

## The whole sequence

| Era | Fixed | Created |
|---|---|---|
| **Waterfall** | Predictability for fixed requirements | Feedback arrives once, far too late |
| **Agile** | Batch size, so feedback is continuous | Ops still slow — the handoff is the wall |
| **DevOps** | The handoff — automate it, share ownership | Nobody owns behaviour after deploy |
| **SRE** | Reliability, as a measurable budget | Doesn't scale the DevOps team itself |
| **Platform Eng** | The DevOps team as a bottleneck | — |
| **DevSecOps** | Security as an end-stage gate | — |

**Three things worth taking from this.**

**They coexist; they're not a ladder.** A mature organisation runs all of them at once. "We've moved past DevOps to platform engineering" is nearly always a misunderstanding — the platform is built *by* people doing DevOps work.

**Each transition moved the bottleneck rather than removing it.** That's the [[architecture/01-system-design-fundamentals/README|theory of constraints]] applied to a delivery pipeline, and it predicts what breaks next: optimise anything, and the constraint relocates. Knowing where yours currently is matters more than knowing the vocabulary.

**Titles lag reality badly.** A "DevOps Engineer" role may be any of these depending on the company — at a fifty-person startup it's usually all five at once. Read the responsibilities, not the title. See [[foundations/software-engineering/03-the-engineering-roles|the engineering roles]].

## Related
- [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]] — the reliability discipline in depth
- [[devops/12-sre-and-platform-engineering/03-platform-engineering|platform engineering]] — the scaling answer
- [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]] — security in the pipeline
- [[foundations/software-engineering/02-the-software-development-lifecycle|the SDLC]] — the phases all of this is rearranging
- [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD concepts]] — the automation DevOps rests on

*Source: [reference] — from the freeCodeCamp IT Fundamentals course (final module), cross-checked against the Google SRE book and the DORA/Accelerate research.*
