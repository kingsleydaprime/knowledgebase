# Performance and Battery

**[Intermediate]** — the metrics both stores measure, and the small number of things that actually move them.

## The kid version first

Users judge an app on three moments: **how fast it opens**, **whether scrolling is smooth**, and **whether their battery survives the day.**

The stores measure all three and show them to you. Get them wrong and you get uninstalled — usually without a review explaining why.

## Startup — the metric users judge first

```
COLD start    process doesn't exist       ← the one that matters. Target < 2s
WARM start    process alive, UI destroyed
HOT start     everything alive            ← near-instant
```

**Cold start is what you optimise.** The killers, in order:

1. **Doing work in app initialisation.** Every SDK initialised eagerly at launch adds directly to it. **Analytics, crash reporting, ad SDKs and A/B frameworks all want to init at startup** — defer everything that isn't needed for the first frame
2. **A blocking network call before first render.** Never. **Render cached data immediately**, refresh after → [[mobile/07-data-and-offline-first|offline-first]]
3. **Reading files or a database synchronously on the main thread**
4. **A heavy first screen.** Render something meaningful fast; fill in the rest

**Measure it properly:** Android Vitals and Macrobenchmark; Xcode Instruments' App Launch template and MetricKit. **Both stores penalise slow startup in ranking**, so this is commercial, not just aesthetic.

**Baseline Profiles (Android)** are close to free money — a precompiled profile that reduces cold start by 20–30% with no code changes. **Add one.**

## Rendering — smooth scrolling

**60fps means 16.6ms per frame; 120fps means 8.3ms.** Miss it and the user sees jank.

**The rules:**
- **Never block the main thread.** No I/O, no JSON parsing, no image decoding. This causes nearly all jank
- **Lazy lists always** — `LazyColumn`, `List`, `RecyclerView`. A non-lazy container with 2,000 items builds 2,000 views
- **Stable keys** on list items → [[mobile/04-declarative-ui|declarative UI]]
- **Downsample images to display size before decoding.** A 4000×3000 photo is ~48MB decoded — **a few of those is an out-of-memory crash.** Coil and Kingfisher handle this; hand-rolled image loading usually doesn't
- **Keep state narrow.** State at the root re-renders everything beneath it — **the most common declarative-UI performance bug**
- **Avoid nested scrolling** in the same direction

**Measure, don't guess:** Compose recomposition counts and compiler metrics; SwiftUI's `_printChanges()`; the platform profilers. **The bottleneck is routinely not where you'd assume.**

## Memory

- **Both platforms kill you when memory is tight**, and a background app with a large footprint is the first to go → [[mobile/03-the-app-lifecycle|the lifecycle]]. **Low memory usage is directly a "did our state survive" feature**
- **Images are almost always the largest consumer**
- **Leaks:** on Android, a `Context` or `View` held past its lifetime — **LeakCanary finds these automatically, add it in debug builds.** On iOS, **retain cycles** — closures capturing `self` strongly. `[weak self]` is the fix, and Instruments' Leaks/Memory Graph finds them

## Battery — where it actually goes

The intuition is wrong here, so it's worth stating the order:

```
1. The SCREEN            (mostly not yours — but dark mode on OLED helps)
2. The CELLULAR RADIO    ← the one you control most
3. GPS / high-accuracy location
4. Sustained CPU / GPU
```

**The radio tail is the key mechanism:** waking the cellular radio keeps it in a high-power state for **seconds after** your transfer ends. So **ten small requests spread across a minute cost far more than one batched request** — this is why batching matters more on mobile than anywhere else → [[mobile/08-networking-on-mobile|networking]].

**Location is the second offender.** Continuous high-accuracy GPS is brutal. Use the coarsest accuracy that works, use significant-change or geofence APIs instead of continuous updates, and **stop when you don't need it.** A forgotten location subscription is a classic battery bug.

**Wake locks** (Android) held too long, and unbounded background work, round out the list.

**Both platforms report your battery impact to users and to you** — Android Vitals flags excessive wake-ups and wake locks; iOS shows per-app battery usage. **Users check this and uninstall accordingly.**

## App size

- **Both stores impose cellular-download warnings** past a threshold, and **install conversion drops measurably with size** — especially in markets with expensive data, which is much of the world
- **Android App Bundles** ship only the code and resources each device needs. **Use them; it's the default now**
- **iOS App Thinning** does the equivalent
- **The usual bloat:** uncompressed images, unnecessary localisations, multiple analytics SDKs, and debug symbols in release builds
- **Audit your dependencies.** A convenience library pulling in 8MB is a real cost

## Measure before you optimise

Same discipline as everywhere → [[foundations/computer-architecture/12-performance|performance method]]:

| | Tool |
|---|---|
| **Android** | Android Studio Profiler, **Macrobenchmark**, **Android Vitals** (real users), Perfetto |
| **iOS** | **Instruments** (Time Profiler, Allocations, Energy Log), **MetricKit**, Xcode Organizer |
| **Both** | Firebase Performance Monitoring |

**Field data beats lab data.** Android Vitals and MetricKit report from real devices on real networks — **your flagship phone on office Wi-Fi is not your median user**, who is on a mid-range Android with 3 bars.

## Key insight

**The three things users judge — startup, jank, battery — each have one dominant cause: work at launch, work on the main thread, and waking the radio.** Almost all real mobile performance work is moving work off those three paths, and the profilers will tell you which one you're guilty of far faster than reasoning about it will.

## Related
- [[mobile/08-networking-on-mobile|networking]] — the radio tail
- [[mobile/04-declarative-ui|declarative UI]] — recomposition cost
- [[mobile/10-background-work-and-push|background work]] — why the OS restricts you
- [[foundations/computer-architecture/12-performance|performance method]] — measure first

*Source: [reference] — Aug 2026.*
