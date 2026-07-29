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
