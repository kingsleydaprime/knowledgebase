# Thinking Patterns
> Started 2026-07-27 · living profile, updated as patterns are actually observed

Not a technical concept note — this tracks *how* I reason and make decisions, across whatever project I'm working in at the time. Requested this deliberately as a self-improvement tool: I want direct, specific feedback on my thinking, not just on my code. See a project's own `thinking-patterns.md` (e.g. `projects/gees-arise/thinking-patterns.md`) for the specific instances behind entries here — this file is the cross-project pattern, not the story each time.

---

## Recurring strengths

**Catching real problems in my own proposals, unprompted, before anyone else flags them.**
First clear instance (gees-arise, 2026-07-27): proposed defaulting every circle's reset time to 23:59 "to match when the cron runs," then in the same message caught that this breaks across timezones — 23:59 UTC isn't midnight for a user in a different timezone, so a "universal" default doesn't actually deliver the "resets at your midnight" experience it sounds like it does. Explicitly chose to defer rather than force a shaky fix through. This is a strong instinct — most people ship the naive default and only discover the timezone problem when a real user in another timezone complains.

**Recurred 2026-10-01 (SWE 101).** After a review showed the course was overloaded, said unprompted: *"20 something weeks is a lot"* and proposed splitting it into 6–12-week courses (101, 102, 103). A real structural catch — shorter courses give a nearer finish line, which is the condition his own JAMB result came from.

**Recurred 2026-10-01 (vault work), process this time.** Mid-way through a long batch of generated lessons — seven companions, about 50 labs, nothing committed — asked unprompted: *"don't you think this should be done in batches… let's commit before going on."* The risk was real (one bad step could have tangled a large uncommitted change) and the AI doing the work hadn't raised it. Same instinct as the timezone catch, applied to a workflow rather than a design.

## Recurring blind spots / things to watch

**Proposing a new default without fully tracing through an architectural decision made moments earlier in the same conversation.**
Same instance as above: the reset-time proposal (coupling every circle's reset to the cron's schedule) ran against something we'd *just* built — the whole reason the scheduled-jobs migration used a 15-minute `pg_cron` sweep instead of once-daily Vercel Cron was specifically so each circle's reset time (and audit deadline) could be independent of the sweep's own schedule. The sweep catches each circle's deadline within ~15 minutes of whenever *that circle's* deadline actually is — there was never a need to couple the two. Worth watching for: after a design decision lands, check a next proposal against it before floating the idea, not just against the original requirement.

**Third instance, 2026-10-01 — a strategic decision re-opened by a feeling, not by its reasoning.** In the same message as the good catch above: *"I also think I need the fundamentals to apply for jobs. I don't know where I was rushing."* That reverses the central decision of SWE 101 — apply from week 7, in parallel — which his own plan had argued for in writing: *"Start before it feels ready. This is the instruction most likely to be ignored"*, and *"treating [fundamentals] as a prerequisite for applying is what pushed the original plan to 52 weeks before a single CV went out."* It arrived around week 6, the week before applications were due to start — exactly where the plan predicted the urge to wait would appear. And it merged two separate findings: the review said the *study load* was rushed, not that *applying* was premature. **What better looks like:** before reversing a decision, restate the reason it was made, and say what new evidence defeats that reason. "I feel unready" is not new evidence; the plan expected that feeling. **Correction, same day:** there *was* evidence I didn't know about. He had already been applying, got interviews, and failed the graph questions in the DSA rounds. So the reversal was driven by a real result, not only a feeling, and that part of the critique was wrong. What still stands: the evidence was "graphs are a gap", and the conclusion jumped to "fundamentals before applying". The narrower conclusion — "fix graphs while still applying" — is what the evidence supports. **The lesson for both of us:** state the evidence behind a reversal, not only the conclusion. "I failed graph questions in two interviews" would have made the case on its own.

## Notes on communication pattern (not reasoning quality, but adjacent)

Messages sometimes bundle several independent, high-effort asks together (UI gaps + a new default + "continue the build plan" + a large new meta-request, all in one message, 2026-07-27). Not wrong, but worth naming: it risks any single one getting shallower treatment, or the most time-sensitive one getting lost among the others. Not a "bad thinking" pattern on its own — a pacing thing to be aware of.

**Recurred, larger, 2026-08-23.** One message contained nine asks: is the Python course complete · cross-reference everything against roadmap.sh · finance/tax/entrepreneurship · the systems-engineering gap · other kinds of software engineering · game development · desktop apps · data centres and infra careers · manufacturing as a business. Closing line: *"I'm thinking of so many things I can do to make a future-proof career man."*

Two things worth separating, because they're different and only one is a problem.

**The bundling was partly rational this time.** The stated reason — a subscription ending — is a genuine, time-bounded constraint, and "extract durable reference material while I can" is a correct response to it. Six domains were mapped in one session precisely *because* they were batched. That's the pattern working for him.

**The scatter underneath is the thing to watch.** Every item was framed as a possible *career direction*, and they arrived **forty-eight hours after** deliberately parking Java, mobile, embedded and robotics on the reasoning that *"a CV aimed at four roles reads as aimed at none"*. The parking decision was sound, was his own, and was re-opened almost immediately — not by revisiting the reasoning, but by curiosity arriving from a different angle.

**The same shape as the 2026-07-27 entry above:** a decision lands, and a later proposal isn't checked against it. There it was one architectural decision within a conversation; here it's a strategic decision across two days.

**What worked:** the interests became *notes*, not *courses*, and went into [[learning/catalogue|the parking lot]] — which is the mechanism his own system already contains for exactly this. The distinction he was already making implicitly, and worth making explicitly: **writing a map is cheap and reversible; starting a course is neither.**

**Worth watching:** whether "future-proof career" is doing the work of anxiety rather than planning. Six directions is not a hedge against an uncertain future — it's the thing that makes the current one take longer.
