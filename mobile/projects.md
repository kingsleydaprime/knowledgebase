# Mobile — Projects

*The domain where **shipping one small app teaches more than reading the whole course** — because the constraints here (process death, offline, store review) are ones you only internalise by hitting them. And both stores let you publish for a one-off or small fee.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 ⭐ **Survive process death** — build any two-screen app with a form, then turn on "Don't keep activities" (Android) or kill the process from Xcode. **Done when:** you can background the app mid-form, kill the process, return, and lose nothing. **Do this first** — it's an afternoon, and it teaches the constraint that shapes everything else → [[mobile/03-the-app-lifecycle|the lifecycle]].

- 🟢 **A list-detail app over a public API** — the "hello world" of mobile, done properly: loading, error, **and empty** states as one sealed type, pull-to-refresh, and a lazy list with stable keys. **Done when:** all four states render correctly and the list scrolls 1,000 items smoothly.

- 🟢 **Break your own network** — take the app above and test it with Network Link Conditioner on 3G, with airplane mode toggled mid-request, and behind a captive portal. **Done when:** none of the three produces a crash, an infinite spinner, or a lie. **This is the most commonly untested path in mobile** and it's the daily experience of a large share of users → [[mobile/08-networking-on-mobile|networking]].

- 🟡 ⭐ **An offline-first app** — local database as the source of truth, UI observes it, sync layer updates it, mutations queued in an **outbox table**. **Done when:** you can create, edit and delete with airplane mode on, then watch it all sync when you reconnect — **and you've decided, deliberately, what happens when two devices conflict** → [[mobile/07-data-and-offline-first|offline-first]].

- 🟡 **Ship it to a store** — actually publish. Privacy declarations, screenshots, a demo account in review notes, staged rollout. **Done when:** it's live and a stranger can install it. **The review process teaches things no note can**, and rejections are the useful part.

- 🟡 **Add push, end to end** — server → FCM/APNs → device → deep link into the right screen **from a cold start**, with auth restored first. **Done when:** tapping a notification with the app fully closed lands the user on the correct screen, logged in → [[mobile/06-navigation|navigation]].

- 🟡 **Profile and fix a real regression** — deliberately slow your own app (eager SDK init, a blocking network call at launch, an oversized image), measure the cold start and jank, then fix them. **Done when:** you have before/after numbers from Macrobenchmark or Instruments, not impressions → [[mobile/11-performance-and-battery|performance]].

- 🟡 **Make it accessible** — full keyboard/switch navigation, labelled controls, and 200% text size without broken layouts. **Done when:** you complete the app's main task using VoiceOver or TalkBack with the screen off.

- 🔴 ⭐ **The same app, two ways** — build one small app natively **and** in Flutter or React Native. **Done when:** you can name three things each made easy and three each made painful. **This is the only way to have an informed opinion** on [[mobile/14-native-vs-cross-platform|the native-vs-cross-platform question]], and it's the answer interviewers actually respect.

- 🔴 **Something that uses the hardware** — camera with real-time processing, background location with a geofence, BLE to a device you built → [[hardware/README|hardware]]. **Done when:** it works on a real device, in real conditions, with permissions denied at least once.

## If you only do one

**Ship a small app to a store.** Not because the app matters, but because the pipeline does — signing, privacy declarations, review, rejection, staged rollout, and a crash report from a device you've never seen. **You cannot simulate that**, and it's the single clearest signal in mobile hiring.

## Related
- [[mobile/README|the mobile course]] · [[mobile/interview/README|interview bank]]
- [[mobile/frameworks/README|frameworks]] — pick your stack
- [[project-ideas|Project Ideas]] — the vault-wide index
