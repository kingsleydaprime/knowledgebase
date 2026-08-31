# Mobile — Interview Prep

From the [[mobile/README|mobile course]].

## Files
1. [[mobile/interview/01-the-mobile-round|The Mobile Round]] — lifecycle and process death, architecture, offline, performance, platform, release, and the native-vs-cross-platform judgement question. 🔥 marks what comes up constantly

## The scope note — read this first

**[[INTERVIEW|INTERVIEW.md]] states a principle this bank sits against:** *"an interview bank for a subject you haven't practised would be memorisation, not preparation."*

That holds, and this bank exists anyway — **written from the course, not from having sat these interviews, and honestly labelled.** A map of what the round asks, not a substitute for reps.

**What actually prepares you is a shipped app.** Mobile hiring weights a published app heavily, because the constraints in this domain — process death, offline, store review — are ones you only genuinely internalise by hitting them. **A single small app on a store outperforms every answer here** → [[mobile/projects|mobile projects]].

## What this round tests differently

**The lifecycle questions are the filter.** Almost anyone can describe MVVM; the people who've shipped are the ones who immediately distinguish *rotation* from *process death*, and who know that swiping an app away isn't the same as the OS killing it.

Two failure modes this bank is written against:

1. **Describing architecture generically.** "I use MVVM with a repository" is table stakes. *Why* the UI observes the database rather than the network is the answer that shows understanding
2. **Framework tribalism.** "Native is faster" and "cross-platform is always enough" both read as untested opinion. **The strong answer names a real cost of the option it prefers**

## Related
- [[mobile/README|the course]] · [[mobile/14-native-vs-cross-platform|native vs cross-platform]]
- [[frontend/interview/README|frontend bank]] — the adjacent round, and it shares the declarative-UI material
- [[INTERVIEW|Interview Prep Index]]
