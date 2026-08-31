# The Mobile Round

**[Intermediate → Advanced]** — what gets asked, what a strong answer covers, and the detail that separates memorised from understood. 🔥 marks the ones asked constantly.

## Lifecycle and process

**🔥 Q: What happens when the user backgrounds your app and comes back an hour later?**

**A strong answer covers:** the OS may have killed the process entirely. On return it's a cold start, and the app must restore state to look as though nothing happened.

**The detail worth adding — this is the whole question:** the **three durations of state**. `remember`/`@State` survives a redraw; `ViewModel`/`@StateObject` survives a configuration change; **only persisted state survives process death.** Candidates who name all three separately are the ones who've shipped something → [[mobile/03-the-app-lifecycle|the lifecycle]].

**Q: How do you test that?**

**A strong answer covers:** "Don't keep activities" in developer options, or `adb shell am kill`. **Swiping the app away is not the same thing** — that's user-initiated and behaves differently.

**The detail worth adding:** it should be on during development, not a pre-release check. **This is the bug class that only appears in the wild**, and it's the most common untested path in mobile.

**Q: Why does Android have `ViewModel` *and* `SavedStateHandle`?**

**A strong answer covers:** they solve different problems. `ViewModel` survives configuration changes (rotation, dark mode, split-screen) but dies with the process. `SavedStateHandle` is persisted and survives process death, but is small — it's for IDs and scroll positions, not data.

## Architecture

**🔥 Q: Where does state live in your app?**

**A strong answer covers:** UI is stateless and renders what it's given; a ViewModel holds UI state and handles events; a repository is the source of truth for a kind of data. Data flows down, events flow up.

**The detail worth adding:** **the UI observes the local database, never the network.** The network's only job is to update the database. That single decision gives you offline support, instant launches, and a UI that can't spin forever → [[mobile/07-data-and-offline-first|offline-first]].

**Q: How do you model loading, error and empty states?**

**A strong answer covers:** one sealed type or enum, not four booleans. Four booleans is sixteen combinations, most of them nonsense, and you will eventually render a spinner over an error over stale data.

**The detail worth adding:** **`Success(emptyList())` is a distinct state needing its own UI.** "Loaded and there's nothing" is not "loading" — shipping a permanent spinner for empty results is the classic version of this bug.

**Q: Why does my snackbar appear twice after rotating?**

**A strong answer covers:** it's modelled as state rather than as a one-shot event, so re-collecting the state re-emits it. Fix with a `Channel`/`SharedFlow`, or state the UI explicitly consumes and clears.

## Offline and networking

**🔥 Q: Design an app that works offline.**

**A strong answer covers:** local database as source of truth; UI observes it; sync layer updates it. Optimistic writes go to the DB immediately and queue in an **outbox table** (not in memory — memory doesn't survive process death). Retry with backoff and a client-generated idempotency key.

**The detail worth adding:** **conflict resolution, honestly.** Last-write-wins is the default, is usually fine, and **silently destroys someone's work occasionally** — so it's a deliberate choice, not a default you fall into. Naming the alternatives (server-wins, field-level merge, CRDTs) and saying it depends on what the data means is the strong answer → [[mobile/07-data-and-offline-first|offline-first]].

**Q: Why batch network requests on mobile?**

**A strong answer covers:** latency and round trips dominate, so chattiness is expensive.

**The detail worth adding, and it's the one that impresses:** **the radio tail.** Waking the cellular radio keeps it in a high-power state for seconds *after* the transfer completes — so ten small requests spread over a minute cost far more battery than one batch. **The cost is the wake-up, not the bytes** → [[mobile/11-performance-and-battery|battery]].

**Q: Your API adds a field. What breaks?**

**A strong answer covers:** nothing, if clients ignore unknown fields — **and everything if they don't.** Old app versions live for years, so the API can add but never remove or repurpose.

## Performance

**🔥 Q: The app is janky when scrolling. How do you diagnose it?**

**A strong answer covers:** profile first, don't guess. Check for main-thread work (I/O, JSON parsing, image decoding), confirm the list is lazy with stable keys, and check image sizes.

**The detail worth adding:** **image decoding is usually it.** A 4000×3000 photo is ~48MB decoded, and a few of those is an OOM crash, not just jank. Downsample to display size before decoding.

**Q: Cold start is 4 seconds. Where do you look?**

**A strong answer covers:** work in app initialisation (every SDK initialised eagerly adds directly), a blocking network call before first render, and synchronous disk I/O on the main thread.

**The detail worth adding:** **render cached data immediately and refresh after** — never block first paint on the network. And on Android, **Baseline Profiles** give 20–30% for free with no code change.

**Q: How does declarative UI cause performance problems?**

**A strong answer covers:** the framework re-runs your UI function often, so state placed high in the tree re-renders everything beneath it. **One big state object at the root is the commonest bug.** Keep state narrow, lists lazy, keys stable, and never allocate in the render body.

## Platform

**Q: What can't you do in the background?**

**A strong answer covers:** run continuously, poll frequently, or guarantee execution at a time. You describe work; the OS schedules it, batched and delayed.

**The detail worth adding:** **manufacturer battery killers on Android** — Xiaomi, Huawei, OnePlus and others kill background work in ways that violate documented behaviour. **So never let correctness depend on background execution**; sync opportunistically and always on foreground → [[mobile/10-background-work-and-push|background work]].

**Q: How do you handle a permission denial?**

**A strong answer covers:** the feature degrades but works — manual entry instead of location. Prime with your own explanation *before* the system dialog.

**The detail worth adding:** **on iOS, denial is close to permanent** — you get one ask, and recovery means talking the user into Settings. That's why the priming screen is the highest-leverage UI in the flow. Plus the granular tiers: "only this once", approximate location, selected photos → [[mobile/09-permissions-and-privacy|permissions]].

**🔥 Q: Where do you store an auth token?**

**A strong answer covers:** Keychain (iOS) or Keystore (Android). Never `UserDefaults`/SharedPreferences — those are plain files.

**The detail worth adding:** **hardware-backed keys** (Secure Enclave, StrongBox) never exist in extractable form and can require biometrics to use. And **biometrics should unlock a stored key, not set a boolean the app checks** — a boolean is trivially patched → [[mobile/12-security-on-device|security]].

**Q: Can you put an API key in the app?**

**A strong answer covers:** it's public. Extractable in minutes, obfuscated or not. Proxy through your server, or restrict the key server-side and treat it as public.

**The detail worth adding:** the general rule — **the app is untrusted, the server enforces.** Client-side price calculation, permission checks and receipt validation are all bypassable. **Receipt validation must be server-to-server.**

## Release

**Q: You shipped a crash. What now?**

**A strong answer covers:** there's no rollback. Halt the staged rollout, disable the feature by **remote config**, and ship a fix through review.

**The detail worth adding:** **the two switches you need before you need them** — feature flags and a forced-update endpoint. **Retrofitting the forced-update mechanism is impossible**, because the users you need to reach are on the version that lacks it → [[mobile/13-release-and-distribution|release]].

## The judgement question

**🔥 Q: Native or cross-platform?**

**A strong answer covers:** it depends on the team and how platform-specific the app is. A React team ships React Native faster than they learn two native stacks. Deep OS integration — widgets, watch, CarPlay, heavy camera — argues for native.

**The detail worth adding, and this is what's being tested:** **calibration.** Naming a real cost of the option you prefer, noting that cross-platform saves ~60–70% rather than 50% (you still test both, handle platform differences, and manage two submissions), and knowing that **React Native's bridge criticism is out of date** since the New Architecture. Confident tribalism in either direction reads as not having thought about it.

## What this round tests

1. **Have you dealt with the lifecycle?** The process-death questions separate people who've shipped from people who've followed tutorials
2. **Do you think about the constrained environment** — battery, network, memory — by default?
3. **Do you know the client is untrusted?**
4. **Are you calibrated about frameworks** rather than tribal?

## Related
- [[mobile/README|the mobile course]] · [[mobile/projects|projects]]
- [[mobile/03-the-app-lifecycle|the lifecycle]] — the most-asked area
- [[INTERVIEW|Interview Prep Index]]
