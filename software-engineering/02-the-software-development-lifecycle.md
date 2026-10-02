# The Software Development Lifecycle

> **[Beginner]** · Six phases, what each is for, and what breaks when you skip it.

## Before you start

You can already:

- Describe a feature you built from "someone asked for it" to "users had it."
- Explain the difference between programming and engineering → [[software-engineering/01-what-software-engineering-is|what software engineering is]].

After this lesson you will be able to:

1. Name the six phases in order and say what each one produces.
2. Read a description of a failure and say **which phase it belongs to** — the skill that stops a team fixing the wrong layer.
3. Explain waterfall and agile as the same phases at different batch sizes.

**Study route.** Read §1–4, then stop and attempt the worked example's classification yourself before reading the answers under it.

## The kid version

Making a birthday cake has steps. Find out what cake they want. Plan it — what goes in, what order. Bake it. Taste it. Bring it to the party. Then, if they want another next year, remember what went wrong. **Skip "find out what they want" and you bake a perfect chocolate cake for someone who's allergic to chocolate.** Every step you skip shows up later as a problem that *looks* like it belongs to a different step.

**Where the analogy stops working.** You bake a cake once. Software goes round these steps over and over for years, in small loops — and the last step, keeping it working, is where most of the effort goes, not a footnote.

## 1. Why this exists

A team ships a password-reset feature. It works in testing. In production, attackers use it to discover which email addresses have accounts, because the page says "no account with that email." The team spends a week adding rate limiting and CAPTCHAs — coding fixes — while the actual failure was that nobody wrote down *"must not reveal whether an email is registered"* before building. **Without names for the phases, people fix the phase they're standing in, not the one that failed.**

## Terms used in this lesson

1. **SDLC (software development lifecycle)**: The letters stand for those three words. It is the observation that building software always involves the same six activities, whatever process a team wraps around them.
2. **Functional requirement**: This is a statement of *what* the system does. "Users can reset a password."
3. **Non-functional requirement**: This is also known as a **quality attribute**. It is a statement of *how well* the system does it — speed, scale, security, cost. "In under 300 milliseconds, without revealing whether an email is registered."
4. **Batch size**: This is how much work goes through all six phases before anyone gets feedback. A whole product at once is a large batch; one small feature is a small batch.
5. **Waterfall**: This is a process that runs all six phases once, in order, in one large batch.
6. **Agile**: This is a family of processes that run the six phases repeatedly in small batches, usually one to two weeks each. Scrum and Kanban are specific agile processes.
7. **Post-mortem**: This is also known as an **incident review**. It is a written analysis after something went wrong, aimed at the cause rather than the person.

## 2. The six phases

**Requirements → Design → Implementation → Testing → Deployment → Maintenance**

The phases are real. What varies between "methodologies" is only **how big a batch you push through them at a time**, and how willing you are to go backwards.

**1. Requirements — what are we building, and for whom?**
Turning a vague request into something specific enough to build and check. The distinction that does the most work is **functional** versus **non-functional** requirements. Non-functional requirements are the ones that quietly determine your architecture.
*Produces:* a written description someone else could check the result against.
*Skip it and:* you build the wrong thing correctly. The most expensive failure mode there is, because everything downstream was competent.

**2. Design — how will it be structured?**
Components, responsibilities, data, interfaces, failure modes. See [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|how to approach system design]].
*Produces:* a structure — sometimes a diagram, sometimes a paragraph and a schema.
*Skip it and:* you get a structure by accident — whatever fell out of the order you happened to write things in. Usually discovered as "we can't change X without breaking Y."

**3. Implementation — write it.**
The part people think is the whole job. See [[concepts/04-best-practices/01-clean-code/index|clean code]].
*Produces:* code.
*Skip it and:* well, quite.

**4. Testing — how do we know it works?**
Not just tests — reviews, static analysis, manual checking. See [[concepts/04-best-practices/04-testing-fundamentals/index|testing fundamentals]].
*Produces:* evidence that the code meets the requirements.
*Skip it and:* your users do the testing, and they report results to your competitors.

**5. Deployment — get it in front of people.**
Build, release, configuration, rollback. See [[devops/06-ci-cd/09-cd-and-deployment|CD and deployment]].
*Produces:* a running version, and a record of which version that is.
*Skip it and:* it works on your machine, which helps nobody.

**6. Maintenance — keep it working.**
Bugs, dependency updates, changing requirements, scaling. **This is where most of a system's total lifetime cost lives** — typically the majority — which is the economic argument behind every "write it clearly" instruction in this vault.
*Produces:* a system that still works next year.
*Skip it and:* the system rots until a rewrite looks cheaper than a fix. It usually isn't.

## 3. Waterfall, agile, and what actually changed

**Waterfall** runs the six once, in order, in big batches: all requirements, then all design, then all implementation. Its fatal assumption is that requirements can be known up front and won't change. For most software they can't and do.

**Agile** runs the same six phases in small batches, repeatedly — a slice of requirements through to deployment in a week or two, then again. Nothing was removed. **The phases didn't change; the batch size did.** Feedback arrives while it's still cheap to act on.

```
Waterfall (one large batch):
  [ Req ][ Design ][   Implementation   ][ Test ][ Deploy ] ......... first feedback

Agile (many small batches):
  [R D I T D] feedback [R D I T D] feedback [R D I T D] feedback ...
```

Everything else — Scrum, Kanban, XP — is a specific set of rituals for organising those small batches. Worth knowing the vocabulary (sprint, standup, backlog, retro) because you'll be asked, but the ceremony matters far less than the batch size.

**Where waterfall is still right.** When requirements genuinely are fixed and mistakes are very expensive to correct after release — firmware in a pacemaker, a satellite, a regulated system — more of the work moves up front on purpose. That's a trade-off, not a mistake.

## 4. Classifying a failure by phase

The question to ask is not "where did we notice it?" but **"what is the earliest phase where this could have been prevented?"** The failure usually *shows up* in testing or production, but it usually *belongs* earlier.

## 5. Worked example — five incidents, one question each

Attempt each before reading the answer under it: *what's the earliest phase that would have prevented it?*

1. **The reset page reveals which emails are registered** (§1).
<details><summary>Answer</summary>

**Requirements.** "Must not reveal whether an email is registered" is a non-functional requirement nobody wrote down. Rate limiting treats the symptom.

</details>

2. **Adding a "gift message" to orders needs changes in eleven files across four folders.**
<details><summary>Answer</summary>

**Design.** The structure spreads one concept across the codebase — see [[backend/03-structuring-a-backend/02-organising-by-layer-vs-by-feature/index|organising by layer vs by feature]].

</details>

3. **A discount applies twice when the customer double-clicks "Pay".** The requirement said "apply once."
<details><summary>Answer</summary>

**Implementation**, with a missed catch in **testing**. The requirement was right; the code didn't make the operation idempotent, and no test clicked twice.

</details>

4. **The new release worked in staging but crashed in production because an environment variable was missing.**
<details><summary>Answer</summary>

**Deployment.** Configuration is part of the release. A deploy checklist or startup validation of required variables would have prevented it.

</details>

5. **Two years after launch, nobody dares upgrade the web framework because it's four major versions behind.**
<details><summary>Answer</summary>

**Maintenance.** Small, regular dependency updates are cheaper than one large one; skipping them turns a routine task into a project.

</details>

## Where this shows up for you

You have already done all six phases across twelve projects, unnamed. The value of the vocabulary is being able to say *which phase a problem belongs to* — "this is a requirements failure, not a coding failure" is often the single most useful sentence in a post-mortem, because it stops a team fixing the wrong layer.

## Common pitfalls

1. **Blaming the phase where the failure surfaced.** Bugs are found in testing and production; they are rarely *caused* there.
2. **Thinking agile means skipping requirements or design.** Agile does them in smaller pieces, not never.
3. **Writing only functional requirements.** "Users can upload a photo" says nothing about size limits, formats, or who can see it — and those decide the design.
4. **Treating maintenance as "after the real work".** It's most of the lifetime cost.

## Check your understanding

1. List the six phases in order, and what each produces.
2. Write one functional and one non-functional requirement for a URL shortener.
3. A team says "we're agile, so we don't do design." What's wrong with that?
4. Why is a requirements failure more expensive than a coding failure, even though both get fixed with code?

<details>
<summary>Answers — after your attempt</summary>

1. Requirements → a checkable description; design → a structure; implementation → code; testing → evidence it meets requirements; deployment → a running, recorded version; maintenance → a system that keeps working.
2. Functional: "given a long URL, return a short code that redirects to it." Non-functional: "redirects complete in under 50 ms for 99% of requests," or "codes are not guessable in sequence."
3. Agile changes batch size, not the phases. They still design — either deliberately in small slices, or accidentally, which is the "skip it and" outcome for design.
4. Everything after the requirement was built on it, so all of it may need redoing; a coding failure usually affects one piece.

</details>

## Practice — independent task

**Write a post-mortem for one of your own projects.** Pick a real thing that went wrong — a bug, a rewrite, a feature that wasn't used.

1. One paragraph: what happened, as observed.
2. The phase where it **surfaced**, and the earliest phase where it **could have been prevented**, with one sentence of justification for each.
3. One concrete change to that earlier phase that would prevent it next time — a question to ask, a check to add, a requirement to write.

**Done when:** the "prevented" phase is earlier than or the same as the "surfaced" phase, the change you propose is specific enough that someone else could do it, and you can explain the difference between "surfaced" and "belongs" without notes.

## Before moving on

You can name the six phases from memory and classify a failure you haven't seen before.

**Recap.** Six phases — requirements, design, implementation, testing, deployment, maintenance — happen in every project. Waterfall and agile differ in batch size, not in which phases exist. Classify failures by the earliest phase that could have prevented them.

**Next.** [[software-engineering/03-the-engineering-roles|The engineering roles]] — who does which part of this work, and what really distinguishes them.

## Related
- [[software-engineering/01-what-software-engineering-is|what software engineering is]]
- [[architecture/01-system-design-fundamentals/index|system design fundamentals]] — the design phase, in depth
- [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD concepts]] — how modern delivery compresses phases 4–6

*Source: [reference]*
