---
id: 6f0c73ac-5953-47fa-b9fd-61505153ddcd
---

# The Engineering Roles

The engineering roles are the different jobs on a software team, such as frontend, backend, security and the people who keep the servers running. Everyone works on the same product, but each role worries about a different thing going wrong, the same way a chef and a waiter in one restaurant do.

## Before you start
<!-- bite: ef5f51b4-4366-41f9-bf56-9a6cd28ba108 -->

You can already:

- Name the six phases of the [[software-engineering/02-the-software-development-lifecycle|SDLC]].
- Say what part of a product you yourself have built — screens, APIs, databases, devices.

After this lesson you will be able to:

1. Place a job ad or a piece of work on the map of roles, by what it owns rather than its title.
2. Tell two roles apart using **the failure each one fears** and **its feedback loop**.
3. Say what separates junior, mid, senior and staff, independent of specialism.

**Study route.** Read straight through. Stop at *Check your understanding*; the practice task uses real job ads, so have two or three open when you get there.

## The kid version
<!-- bite: 7ba3ed3c-f5d9-4ec4-8f42-093672accbf1 -->

A restaurant has a chef, a waiter, a dishwasher, a manager and someone who checks the fridges are cold enough. They all serve the same meal. What makes them different isn't the food — **it's what each one is scared of.** The waiter fears a customer waiting too long. The chef fears a dish coming out wrong. The fridge checker fears food poisoning that nobody notices until next week. Software teams are the same: everyone ships the same product, and you tell the jobs apart by what keeps each person up at night.

**Where the analogy stops working.** In a restaurant one person rarely does two jobs. In software, especially at startups, one person often owns several rows of the table below at once — that's what "full-stack" means.

## 1. Why this exists
<!-- bite: 48216fb1-6bc4-4ed5-99ee-ecca1ebb624b -->

Two job ads, both titled "Software Engineer." One wants you to build React screens and care about how fast a page loads on a cheap Android phone. The other wants you to run Kubernetes clusters and be on call at night. **Same title, almost nothing in common.** Titles are inconsistent across companies, so you need a better way to read what a role actually is — for job hunting, and for knowing who to ask when something breaks.

## Terms used in this lesson
<!-- bite: 1bf91e7e-4759-444c-85cf-4e3dab8b8206 -->

1. **Role**: This is the area of the system a person is responsible for, regardless of their job title.
2. **The stack**: This is the set of layers a product is built from, from the user's screen down through the API, the database, the operating system and the hardware.
3. **On call**: This is also known as **being paged**. It means being the person who is alerted, day or night, when production breaks.
4. **p99 latency**: This is the response time that 99% of requests are faster than. It describes the slow tail that a few unlucky users experience, which the average hides.
5. **Feedback loop**: This is the time between making a change and finding out whether it worked.
6. **Leaky abstraction**: This is an abstraction that stops hiding its details in some situation, forcing you to understand the layer underneath.

## 2. The roles
<!-- bite: d021152e-3d27-493d-927c-4b70e42ae198 -->

Titles are inconsistent across companies — the same work is "backend engineer" at one and "platform engineer" at another. What's stable is **the layer of the stack you're responsible for, and what you get paged about.**

| Role | Owns | The daily reality | In this vault |
|---|---|---|---|
| **Frontend** | What the user touches | Rendering, state, accessibility, bundle size, "why is it slow on a mid-range Android" | [[frontend/index\|frontend]] |
| **Backend** | Everything behind the API | Data modelling, APIs, auth, queues, "why is p99 latency 4 seconds" | [[backend/index\|backend]] |
| **Full-stack** | Both, end to end | Owning a feature from database to button. Common at startups | both |
| **Mobile** | iOS/Android apps | Platform APIs, offline state, app-store release cycles, device fragmentation | [[mobile/index\|mobile]] |
| **Embedded** | Software on hardware | C, constrained memory, interrupts, no OS or a small one, hardware that lies | [[hardware/index\|hardware]] |
| **Systems** | The layer everything runs on | OS internals, compilers, databases, performance measured in microseconds | [[os/index\|OS]] · [[compilers/index\|compilers]] |
| **DevOps / SRE** | Delivery and uptime | Pipelines, infrastructure, monitoring, incidents, being on call | [[devops/index\|devops]] |
| **Security** | Making attacks expensive | Threat modelling, reviews, testing, incident response | [[cybersecurity/index\|cybersecurity]] |
| **Data** | Data other people depend on | Pipelines, warehouses, the correctness of numbers people make decisions on | [[data-science/index\|data scientist]] |
| **ML** | Models in production | Training, evaluation, drift, serving | [[machine-learning/index\|ML engineer]] |
| **AI engineer** | Products built on models | RAG, agents, prompts, **evals**, cost and latency. Mostly application engineering | [[ai-engineering/index\|AI engineer]] |

## 3. What actually differs
<!-- bite: bc3b176b-33d2-463b-9080-7992a4ed1c80 -->

Less than the table suggests. Every role above runs the same six [[software-engineering/02-the-software-development-lifecycle|SDLC]] phases and uses the same three habits. What changes:

**The failure you fear.** Frontend fears a broken layout on a device you don't own. Backend fears data loss. SRE fears the pager. Security fears the breach nobody detects. Embedded fears the bug that needs a physical recall. **This is the most honest way to tell roles apart** — it shapes every trade-off the role makes.

**The feedback loop.** Frontend sees the result in a second. Backend in a test run. Embedded in a flash cycle. ML in a training run measured in hours. Slower loops force more care upfront, which is why embedded and ML cultures feel more conservative than web ones.

**How much of the stack you're allowed to ignore.** Nobody holds all of it. The difference is *which* abstractions you may treat as solid — and every role eventually meets the day theirs leaks, which is when the layer underneath stops being optional.

## 4. Seniority, which matters more than specialism
<!-- bite: 086846ff-baf4-4f15-963f-6251fd75b81e -->

Roughly, and independent of which row you're in:

- **Junior** — given a well-defined task, completes it, asks when stuck
- **Mid** — given a problem, decomposes and solves it, spots the edge cases
- **Senior** — given an ambiguous goal, works out what should be built, and is trusted on the trade-offs
- **Staff+** — works on which problems are worth solving at all

**The jump from junior to mid is mostly about tolerance for ambiguity, not volume of knowledge.** Worth knowing when reading job ads: "3 years experience" is usually a proxy for "has been on the hook for something in production."

## 5. Worked example — reading a job ad by what it owns
<!-- bite: 7733830c-c050-4835-9eff-4cc95dadc8da -->

> *"Software Engineer II. You'll own our checkout service end to end: the API, its Postgres schema, and the deploy pipeline. You'll join the on-call rotation. Experience with TypeScript and queues preferred. You'll work with product to scope new payment methods."*

Read it with the three questions from §3 rather than the title:

1. **What does it own?** An API, a schema, and its pipeline — everything behind the API. That's the **backend** row, with some **DevOps** (owning the pipeline).
2. **What failure does it fear?** Checkout and payments: **lost or doubled money**, and checkout being down. Being on call confirms it — this role gets paged.
3. **What's the feedback loop?** Test runs and deploys — minutes. Fast enough to iterate, slow enough that tests matter.

And the seniority signal: *"work with product to scope new payment methods"* means turning ambiguous goals into buildable work — the **mid-to-senior** line from §4, whatever "II" means at that company.

**Conclusion:** a backend role with operational ownership, at mid level. Your preparation is data modelling, idempotency, queues and incident handling — not React, despite "Software Engineer" in the title.

## Common pitfalls
<!-- bite: 659a832a-69da-4199-a054-5bc35c64de76 -->

1. **Reading the title instead of the responsibilities.** "Platform engineer", "backend engineer" and "SRE" can describe the same job at three companies.
2. **Treating seniority as years.** It's the size and ambiguity of the problem you can be trusted with.
3. **Assuming the layers below you are solid forever.** Every role eventually meets a leaky abstraction; the frontend engineer debugging a CORS error is doing a little networking.

## Check your understanding
<!-- bite: d5f42ec9-fd89-46dd-9426-387e2d470526 -->

1. What is the most honest way to tell two roles apart, and why does it work better than the title?
2. Why do embedded and ML cultures tend to be more careful up front than web cultures?
3. A junior and a senior are both given "users say the dashboard is slow." What does each typically do differently?
4. Name the failure a security engineer fears that most other roles don't think about.

<details>
<summary>Answers — after your attempt</summary>

1. The failure each one fears. It decides every trade-off the role makes — what it tests, what it monitors, what it won't risk — and it's stable across companies, unlike titles.
2. Their feedback loops are slow (a flash cycle, a training run), so mistakes cost more time to discover, which rewards thinking before running.
3. The junior usually needs it narrowed down ("make this query faster") before starting. The senior works out what "slow" means, measures where the time goes, decides whether it's worth fixing now, and picks among the fixes with reasons.
4. The breach nobody detects — an attacker who is quietly inside, where nothing visibly broke.

</details>

## Practice — independent task
<!-- bite: 5dd00209-6ad9-4fc2-a25e-9440cdd73b1d -->

**Read three real job ads by ownership.** Find three current ads you would plausibly apply to.

For each, write four lines:
1. What it owns (the row or rows of the table in §2).
2. The failure it fears, with the phrase from the ad that tells you.
3. Its feedback loop.
4. Its seniority signal, with the phrase that tells you.

**Done when:** each line cites words from the ad rather than the title, and you can say which of the three is the closest fit for what you've actually built — and which row you'd need to study to close the gap.

## Before moving on
<!-- bite: f83e4234-39cb-4928-be91-a6f96ba11d87 -->

You can look at any software job and say what it owns, what it fears, and what level it's pitched at.

**Recap.** Titles vary; ownership doesn't. Tell roles apart by the failure they fear and their feedback loop. Seniority is about how ambiguous a problem you can be trusted with, and it matters more than which row you're in.

**Next.** [[software-engineering/04-the-kinds-of-software-engineering|The kinds of software engineering]] cuts the same field by constraint rather than by product — optional for SWE 101, but useful if you're weighing embedded or systems work. Then week 2 starts design principles with [[concepts/01-best-practices/01-clean-code/index|clean code]].

## Related
<!-- bite: a2961b8c-4547-4c3c-bf08-148461f955f6 -->
- [[software-engineering/01-what-software-engineering-is|what software engineering is]]
- [[PRIMETECHIE|the Primetechie path]] — how these layers connect rather than sitting in silos
- [[INTERVIEW|the interview banks]] — organised by these same domains

## About this lesson
<!-- bite: 8c015f04-bb98-4c68-907b-528dd8b9eacd -->

**Level:** Beginner. **Covers:** What each role actually does day to day, and what genuinely differs between them.

*Source: [reference]*
