# Native vs Cross-Platform

**[Intermediate]** — the first real decision, made honestly rather than tribally.

## The kid version first

Two codebases (Swift + Kotlin) means twice the work and the best possible result.

One codebase (Flutter, React Native, KMP) means roughly half the work and some compromises — occasionally none, occasionally serious.

**Neither is correct in general.** The right question isn't "which is better" but **"what is my team, and what does my app do?"**

## The options

| | What it is | Language |
|---|---|---|
| **Native** | Separate iOS and Android codebases | Swift + Kotlin |
| **Flutter** | Its own rendering engine — draws every pixel | **Dart** |
| **React Native** | JS driving **real native components** | TS/JS |
| **KMP** | Shared *logic*, **native UI on each platform** | Kotlin |
| **.NET MAUI** | Native components from C# | C# |
| **PWA / web wrapper** | A website in a shell | TS/JS |

## Flutter

**Draws everything itself with its own engine** — so a widget looks identical on both platforms because it isn't a platform widget at all.

**Good:** genuinely consistent UI, excellent hot reload, strong performance (compiles to native code), one codebase covering mobile plus desktop and web, and a mature widget set.

**The costs:**
- **Dart.** A pleasant language with a small ecosystem outside Flutter → [[languages/10-dart/README|the Dart course]]
- **You don't get platform widgets**, so you don't get platform behaviour free — including some accessibility and text-input subtleties. Material widgets on iOS look subtly foreign to iOS users
- **New OS features need a plugin**, so you wait
- **Larger binaries** — the engine ships with your app

**Best for:** design-led apps with a custom visual identity, small teams shipping both platforms, and anything where consistency matters more than platform idiom.

## React Native

**JavaScript drives real native components** — a `<Button>` is a genuine `UIButton`/Material button.

**Good:** enormous ecosystem, web developers are productive immediately, **real platform components** (so platform behaviour and accessibility come free), **CodePush-style over-the-air JS updates bypass store review for JS-only changes** — which is a significant practical advantage. **Expo** has made setup and builds dramatically easier and is the right default now.

**The costs:**
- **The bridge**, historically the performance ceiling. **The New Architecture (Fabric/TurboModules/JSI) substantially fixes this** and is now the default — much older criticism is out of date
- **Dependency fragility.** Native modules break across upgrades, and React Native upgrades have a reputation for being painful
- **You still need native knowledge** for anything unusual

**Best for:** teams with React experience, apps that are mostly views over an API, and startups needing speed → [[frontend/frameworks/react/README|React]].

## Kotlin Multiplatform

**The interesting middle.** Share business logic, networking, database and view models in Kotlin; **write the UI natively** in SwiftUI and Compose.

**Good:** the UI is fully native on both, you share the part that's actually duplicated (logic), and adoption is **incremental** — add it to an existing app one module at a time. Compose Multiplatform can now share UI too, if you want.

**Costs:** the Swift interop is workable but not seamless, tooling is younger, and you still write two UIs — so it's less of a saving than Flutter or RN.

**Best for:** teams that already have native apps, and anywhere the UI must feel genuinely platform-native.

## When native is right

Be clear-eyed: **native is still the right answer for a lot of apps.**

- **Heavy platform integration** — widgets, watch apps, Live Activities, CarPlay/Android Auto, deep camera or sensor work
- **Performance-critical** — games, real-time video, AR
- **Platform-idiomatic UX matters** — users notice, particularly on iOS
- **You want new OS features on day one**
- **You have the team.** Two specialists beat one generalist doing both
- **Long-lived apps.** No dependency on a third-party framework's roadmap

## How to actually decide

Four questions, in order:

1. **What can your team already write well?** A React team shipping React Native beats the same team learning two native stacks. **This dominates the technical arguments more often than people admit**
2. **How platform-specific is the app?** Mostly-screens-over-an-API → cross-platform. Deep hardware and OS integration → native
3. **How long will it live?** A 5-year product can afford native; a validation MVP shouldn't
4. **How much does platform idiom matter to your users?** Consumer iOS users notice. Internal tools' users don't

**And a caution about the "half the work" claim:** cross-platform saves less than expected. You still test on both, handle platform differences, write platform-specific code for anything unusual, and manage two store submissions. **Budget 60–70% of two native codebases, not 50%.**

## What isn't a good reason

- ❌ "Native is faster" — for a typical CRUD app, **the difference is imperceptible.** Your network and your images matter more
- ❌ "Cross-platform feels cheap" — not true for years. Plenty of apps you use are Flutter or RN and you haven't noticed
- ❌ "Everyone uses X" — irrelevant to your team and your app
- ❌ Choosing on benchmarks. **Nobody uninstalls over 4ms**; they uninstall over battery drain and crashes

## Key insight

**The decision is mostly about your team and your app's relationship to the platform, not about the frameworks' technical merits** — which are closer than the arguing suggests. A React team should probably ship React Native; a team building a camera-heavy app with widgets and a watch companion should probably go native; and a team that already has two native apps should look at KMP before rewriting anything.

## Related
- [[mobile/frameworks/README|the framework folders]] — each in more depth
- [[mobile/02-the-two-platforms|the two platforms]]
- [[languages/10-dart/README|Dart]] · [[languages/09-kotlin/README|Kotlin]] · [[languages/08-swift/README|Swift]]
- [[desktop/frameworks/README|desktop frameworks]] — the same argument, one layer over

*Source: [reference] — Aug 2026.*
