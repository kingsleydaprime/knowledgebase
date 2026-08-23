# Thinking Patterns
> Started 2026-07-27 · living profile, updated as patterns are actually observed

Not a technical concept note — this tracks *how* I reason and make decisions, across whatever project I'm working in at the time. Requested this deliberately as a self-improvement tool: I want direct, specific feedback on my thinking, not just on my code. See a project's own `thinking-patterns.md` (e.g. `projects/gees-arise/thinking-patterns.md`) for the specific instances behind entries here — this file is the cross-project pattern, not the story each time.

---

## Recurring strengths

**Catching real problems in my own proposals, unprompted, before anyone else flags them.**
First clear instance (gees-arise, 2026-07-27): proposed defaulting every circle's reset time to 23:59 "to match when the cron runs," then in the same message caught that this breaks across timezones — 23:59 UTC isn't midnight for a user in a different timezone, so a "universal" default doesn't actually deliver the "resets at your midnight" experience it sounds like it does. Explicitly chose to defer rather than force a shaky fix through. This is a strong instinct — most people ship the naive default and only discover the timezone problem when a real user in another timezone complains.

## Recurring blind spots / things to watch

**Proposing a new default without fully tracing through an architectural decision made moments earlier in the same conversation.**
Same instance as above: the reset-time proposal (coupling every circle's reset to the cron's schedule) ran against something we'd *just* built — the whole reason the scheduled-jobs migration used a 15-minute `pg_cron` sweep instead of once-daily Vercel Cron was specifically so each circle's reset time (and audit deadline) could be independent of the sweep's own schedule. The sweep catches each circle's deadline within ~15 minutes of whenever *that circle's* deadline actually is — there was never a need to couple the two. Worth watching for: after a design decision lands, check a next proposal against it before floating the idea, not just against the original requirement.

## Notes on communication pattern (not reasoning quality, but adjacent)

Messages sometimes bundle several independent, high-effort asks together (UI gaps + a new default + "continue the build plan" + a large new meta-request, all in one message, 2026-07-27). Not wrong, but worth naming: it risks any single one getting shallower treatment, or the most time-sensitive one getting lost among the others. Not a "bad thinking" pattern on its own — a pacing thing to be aware of.

**Recurred, larger, 2026-08-23.** One message contained nine asks: is the Python course complete · cross-reference everything against roadmap.sh · finance/tax/entrepreneurship · the systems-engineering gap · other kinds of software engineering · game development · desktop apps · data centres and infra careers · manufacturing as a business. Closing line: *"I'm thinking of so many things I can do to make a future-proof career man."*

Two things worth separating, because they're different and only one is a problem.

**The bundling was partly rational this time.** The stated reason — a subscription ending — is a genuine, time-bounded constraint, and "extract durable reference material while I can" is a correct response to it. Six domains were mapped in one session precisely *because* they were batched. That's the pattern working for him.

**The scatter underneath is the thing to watch.** Every item was framed as a possible *career direction*, and they arrived **forty-eight hours after** deliberately parking Java, mobile, embedded and robotics on the reasoning that *"a CV aimed at four roles reads as aimed at none"*. The parking decision was sound, was his own, and was re-opened almost immediately — not by revisiting the reasoning, but by curiosity arriving from a different angle.

**The same shape as the 2026-07-27 entry above:** a decision lands, and a later proposal isn't checked against it. There it was one architectural decision within a conversation; here it's a strategic decision across two days.

**What worked:** the interests became *notes*, not *courses*, and went into [[learning/catalogue|the parking lot]] — which is the mechanism his own system already contains for exactly this. The distinction he was already making implicitly, and worth making explicitly: **writing a map is cheap and reversible; starting a course is neither.**

**Worth watching:** whether "future-proof career" is doing the work of anxiety rather than planning. Six directions is not a hedge against an uncertain future — it's the thing that makes the current one take longer.
