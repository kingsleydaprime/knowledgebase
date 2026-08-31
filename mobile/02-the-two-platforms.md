# The Two Platforms

**[Beginner]** — iOS and Android compared on the things that actually affect your work.

## The kid version first

Two ecosystems, roughly the same capabilities, **completely different cultures.**

Apple controls the hardware, the OS and the store, so everything is consistent and everything is their rules. Google licenses Android to hundreds of manufacturers, so everything is flexible and nothing is consistent.

**Those two sentences predict most of the differences below.**

## Side by side

| | iOS | Android |
|---|---|---|
| **Language** | Swift (Objective-C legacy) | **Kotlin** (Java legacy) |
| **UI** | SwiftUI (UIKit legacy) | Jetpack Compose (Views legacy) |
| **IDE** | Xcode — **macOS only** | Android Studio — any OS |
| **Devices** | ~dozens | **Thousands** |
| **OS adoption** | Fast — most users on the latest 1–2 | **Slow and fragmented** |
| **Review** | Hours to days, **strict** | Hours, more permissive |
| **Store fee** | 15–30% | 15–30% |
| **Sideloading** | Restricted (EU: now permitted) | **Allowed** |
| **Users spend** | **More per user** | More users globally |

**Two practical consequences for you personally:** you need a Mac to ship iOS, full stop — and **Android's fragmentation is the bigger day-to-day tax**, not its API.

## iOS

**Swift** is a modern, strongly-typed, memory-safe language with optionals, value types and structured concurrency → [[languages/08-swift/README|the Swift course]]. Memory is managed by **ARC** — automatic reference counting, deterministic, no GC pauses, and **retain cycles are your problem** (hence `weak`).

**SwiftUI** is the declarative present; **UIKit** is the imperative past that still underpins a lot and is still needed for things SwiftUI can't do. **Real codebases mix them.**

**The culture:** Apple's Human Interface Guidelines are followed closely, users expect platform conventions, and the review process enforces a lot of it. **Deviating from the platform look is noticed and disliked.**

**The friction:** Xcode is the least-loved major IDE in software; provisioning profiles, certificates and code signing are a genuine, recurring source of lost days; and **the annual OS release cycle means an API you adopt may need the newest Xcode**.

## Android

**Kotlin** is Google's official language since 2019 — concise, null-safe, with **coroutines** as the concurrency model → [[languages/09-kotlin/README|the Kotlin course]]. It runs on a JVM-derived runtime (ART), so it's **garbage collected**, and much of [[languages/01-java/README|the Java course]] transfers.

**Jetpack Compose** is the declarative present; the **View system** is the XML-based past, still enormous in existing codebases.

**Jetpack** is the set of libraries that made Android sane — Room (database), Navigation, WorkManager (background), DataStore (preferences), Lifecycle, Hilt (DI). **Learning "Android" today largely means learning Jetpack.**

**The culture:** Material Design, more layout flexibility, more user tolerance for apps that look like themselves.

**The friction — and it's the real one:** **manufacturer skins break background execution.** Xiaomi, Huawei, OnePlus and Samsung have all shipped aggressive battery managers that kill background work in ways that violate the documented behaviour. [dontkillmyapp.com](https://dontkillmyapp.com) exists solely to catalogue this. **Budget for it.**

## What's genuinely the same

More than the tribalism suggests, and this is why cross-platform works at all:

- **Declarative UI.** SwiftUI and Compose are strikingly similar — describe the UI as a function of state, let the framework diff it. **Learn one and the other is mostly renaming** → [[mobile/04-declarative-ui|declarative UI]]
- **Structured concurrency.** Swift's async/await and Kotlin's coroutines solve the same problem with similar shapes
- **The architecture.** Unidirectional data flow, a view model holding state, a repository over the network and database. **Identical on both**
- **The lifecycle problem.** Different callbacks, same constraint
- **Permissions, push, background limits.** Different APIs, converging policy

## Choosing where to start

**Learn Android first if:** you don't own a Mac (decisive), you want the larger global market, or you're targeting regions where Android dominates — **which includes most of Africa, India and Latin America.**

**Learn iOS first if:** you have a Mac, you're targeting the US/Western Europe consumer market, or revenue per user matters more than reach.

**In practice, learn the concepts first.** Sections 03–13 here are platform-agnostic, and they're most of the job. **The platform-specific part is the smaller half.**

## Key insight

**The platforms have converged technically and stayed divergent culturally.** Their UI frameworks, concurrency models and architectures now look remarkably alike — so the transferable skill is the *shape*, and what actually differs is the tooling friction, the review culture, and Android's fragmentation. Learn the shape once; the second platform is mostly vocabulary.

## Related
- [[languages/08-swift/README|Swift]] · [[languages/09-kotlin/README|Kotlin]]
- [[mobile/frameworks/ios/README|iOS]] · [[mobile/frameworks/android/README|Android]]
- [[mobile/14-native-vs-cross-platform|native vs cross-platform]]
- [[mobile/04-declarative-ui|declarative UI]] — where they're nearly identical

*Source: [reference] — Aug 2026.*
