# Mobile

A map of this folder. **A 14-note numbered course, `frameworks/` for four stacks, and an `interview/` bank** — built Aug 2026 to close what was the vault's biggest structural gap: `frontend/`, `backend/`, `desktop/` and `game-development/` all existed, and there was nothing for the platform most people actually use.

**Sections 01–14 are platform-agnostic** and hold whether you write Swift, Kotlin, Dart or TypeScript. That's deliberate, and it's most of the job — the platform-specific part is the smaller half.

> **The one idea:** mobile is programming for an environment that **can pause you, kill you, deny you resources, and refuse to ship your code.** Every practice here follows from not being in control of your own process.

## The course

**Start with 01–03.** They're the constraints; everything after is a response to them.

1. [[mobile/01-what-makes-mobile-different|what-makes-mobile-different]] — **[Beginner]** — the six constraints, what changes versus web, and what's genuinely nicer
2. [[mobile/02-the-two-platforms|the-two-platforms]] — **[Beginner]** — iOS and Android compared on what affects your work; **what's actually the same** (more than the tribalism suggests); and where to start
3. [[mobile/03-the-app-lifecycle|the-app-lifecycle]] — **[Intermediate]** — **the note that shapes the most code.** The OS owns your process; the three durations of state; and **simulating process death, which most developers never do**
4. [[mobile/04-declarative-ui|declarative-ui]] — **[Intermediate]** — SwiftUI and Compose are the same idea, and it's React's. State hoisting, stable keys, and accessibility
5. [[mobile/05-state-and-architecture|state-and-architecture]] — **[Intermediate]** — the layered shape both platforms converged on; **modelling UI state as one sealed type**; and events that should happen once
6. [[mobile/06-navigation|navigation]] — **[Intermediate]** — the back stack, type-safe routes, **and deep links from a cold start**, which is where it gets hard
7. [[mobile/07-data-and-offline-first|data-and-offline-first]] — **[Advanced]** — **the single most important architectural decision**: the local database is the source of truth. Outbox, optimistic updates, and conflict resolution honestly
8. [[mobile/08-networking-on-mobile|networking-on-mobile]] — **[Intermediate]** — the radio tail, batching, API design for clients that live for years, and testing on bad networks
9. [[mobile/09-permissions-and-privacy|permissions-and-privacy]] — **[Intermediate]** — how to ask (and why priming doubles acceptance), the granular tiers people miss, store declarations, and the legal layer
10. [[mobile/10-background-work-and-push|background-work-and-push]] — **[Advanced]** — what you can do when you're not on screen, which is much less than you think. Plus **the Android manufacturer tax**
11. [[mobile/11-performance-and-battery|performance-and-battery]] — **[Intermediate]** — cold start, jank, memory, and **where battery actually goes** (the order is not what you'd guess)
12. [[mobile/12-security-on-device|security-on-device]] — **[Advanced]** — the app runs on the attacker's hardware. **There are no secrets in your binary**; the server enforces everything
13. [[mobile/13-release-and-distribution|release-and-distribution]] — **[Intermediate]** — review, staged rollout, and **the two switches you must add before you need them**
14. [[mobile/14-native-vs-cross-platform|native-vs-cross-platform]] — **[Intermediate]** — the first real decision, made on team and app rather than tribally

## Frameworks

[[mobile/frameworks/README|frameworks/]] — the per-stack implementation layer, copying the [[backend/frameworks/README|backend/frameworks]] convention:

- **[[mobile/frameworks/ios/README|ios/]]** — Swift + SwiftUI. Property wrappers, `@MainActor`, and why UIKit isn't optional knowledge
- **[[mobile/frameworks/android/README|android/]]** — Kotlin + Compose + Jetpack. `collectAsStateWithLifecycle`, and the Android-specific taxes
- **[[mobile/frameworks/flutter/README|flutter/]]** — Dart, and its own rendering engine. What that one decision buys and costs
- **[[mobile/frameworks/react-native/README|react-native/]]** — TypeScript and real native components. **Use Expo**, and why pre-2024 performance criticism is stale

## The languages

Three new language courses were written alongside this track:

- **[[languages/08-swift/README|Swift]]** — value types, optionals, ARC, protocols, structured concurrency
- **[[languages/09-kotlin/README|Kotlin]]** — null safety, coroutines and Flow, and the JVM underneath
- **[[languages/10-dart/README|Dart]]** — sound null safety, async, and the Flutter-shaped ecosystem

TypeScript for React Native is already covered → [[frontend/frameworks/react/README|React]].

## Build it

[[mobile/projects|projects/]] — graded reps with a *done when* for each. **Start with "survive process death"** (an afternoon, and it teaches the core constraint), and **the one that matters most is shipping a small app to a store** — the pipeline is what you can't simulate.

## Interview

[[mobile/interview/README|interview/]] — the mobile round. **The lifecycle questions are the filter**; they separate people who've shipped from people who've followed tutorials.

## Related
- [[frontend/README|frontend]] — the sibling discipline, and [[mobile/04-declarative-ui|note 04]] is largely shared with it
- [[backend/README|backend]] — the other side of the API contract
- [[desktop/README|desktop]] — the same cross-platform argument, one layer over
- [[cybersecurity/README|cybersecurity]] — [[mobile/12-security-on-device|note 12]] is applied version of it
- [[foundations/os/README|operating systems]] — what "the OS kills your process" means underneath

*Source: [reference] — Aug 2026. Nothing here has been shipped to a store by its author; [[mobile/projects|projects]] exists to change that.*
