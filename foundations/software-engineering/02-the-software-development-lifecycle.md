# The Software Development Lifecycle

> **[Beginner]** · Six phases, what each is for, and what breaks when you skip it.

The SDLC is the observation that building software always involves the same six activities, whatever process you wrap around them:

**Requirements → Design → Implementation → Testing → Deployment → Maintenance**

The phases are real. What varies between "methodologies" is only **how big a batch you push through them at a time**, and how willing you are to go backwards.

## The six phases

**1. Requirements — what are we building, and for whom?**
Turning a vague request into something specific enough to build and check. The distinction that does the most work: **functional** requirements (what it does — "users can reset a password") versus **non-functional** ones (how well — "in under 300ms, for 10,000 concurrent users, without leaking whether an email is registered). Non-functional requirements are the ones that quietly determine your architecture.
*Skip it and:* you build the wrong thing correctly. The most expensive failure mode there is, because everything downstream was competent.

**2. Design — how will it be structured?**
Components, responsibilities, data, interfaces, failure modes. See [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design|how to approach system design]].
*Skip it and:* you get a structure by accident — whatever fell out of the order you happened to write things in. Usually discovered as "we can't change X without breaking Y."

**3. Implementation — write it.**
The part people think is the whole job. See [[concepts/04-best-practices/01-clean-code|clean code]].
*Skip it and:* well, quite.

**4. Testing — how do we know it works?**
Not just tests — reviews, static analysis, manual checking. See [[concepts/04-best-practices/04-testing-fundamentals|testing fundamentals]].
*Skip it and:* your users do the testing, and they report results to your competitors.

**5. Deployment — get it in front of people.**
Build, release, configuration, rollback. See [[devops/06-ci-cd/09-cd-and-deployment|CD and deployment]].
*Skip it and:* it works on your machine, which helps nobody.

**6. Maintenance — keep it working.**
Bugs, dependency updates, changing requirements, scaling. **This is where most of a system's total lifetime cost lives** — typically the majority — which is the economic argument behind every "write it clearly" instruction in this vault.
*Skip it and:* the system rots until a rewrite looks cheaper than a fix. It usually isn't.

## Waterfall, agile, and what actually changed

**Waterfall** runs the six once, in order, in big batches: all requirements, then all design, then all implementation. Its fatal assumption is that requirements can be known up front and won't change. For most software they can't and do.

**Agile** runs the same six phases in small batches, repeatedly — a slice of requirements through to deployment in a week or two, then again. Nothing was removed. **The phases didn't change; the batch size did.** Feedback arrives while it's still cheap to act on.

Everything else — Scrum, Kanban, XP — is a specific set of rituals for organising those small batches. Worth knowing the vocabulary (sprint, standup, backlog, retro) because you'll be asked, but the ceremony matters far less than the batch size.

## Where this shows up for you

You have already done all six phases across twelve projects, unnamed. The value of the vocabulary is being able to say *which phase a problem belongs to* — "this is a requirements failure, not a coding failure" is often the single most useful sentence in a post-mortem, because it stops a team fixing the wrong layer.

## Related
- [[foundations/software-engineering/01-what-software-engineering-is|what software engineering is]]
- [[architecture/01-system-design-fundamentals/README|system design fundamentals]] — the design phase, in depth
- [[devops/06-ci-cd/01-ci-cd-concepts|CI/CD concepts]] — how modern delivery compresses phases 4–6

*Source: [reference]*
