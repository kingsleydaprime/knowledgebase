# What Makes Mobile Different

**[Beginner]** — the six constraints that make mobile a distinct discipline rather than "web development on a small screen".

## The kid version first

A web page runs on a machine that's plugged in, has a keyboard, and is on a network. **A mobile app runs on a battery, in someone's hand, on a network that keeps vanishing, and can be killed mid-sentence by the operating system without asking.**

Every difference below comes from that.

## The six constraints

**1. The OS is in charge, not you.**

This is the big one. On a server, your process runs until it crashes or you stop it. On a phone, **the OS terminates your app whenever it wants** — to reclaim memory, to save battery, because the user switched away.

```
user opens your app → OS gives you memory
user switches to Instagram → you're backgrounded
OS needs memory → YOUR PROCESS IS KILLED. No warning, no callback guaranteed
user taps your icon → you must LOOK like you were never gone
```

**"Restore state as if nothing happened" is a core requirement, not a polish item** → [[mobile/03-the-app-lifecycle|the app lifecycle]].

**2. The network is unreliable, and that's the normal case.**

Not an edge case to handle at the end. Users go into lifts, tunnels, and buildings with thick walls; they switch from Wi-Fi to cellular mid-request; they have 2 bars and 400ms of latency.

**Designing offline-first from the start is far cheaper than retrofitting it** → [[mobile/07-data-and-offline-first|offline-first]].

**3. Battery is a budget you spend.**

Every wake-up, every GPS fix, every network request costs power. **The OS actively fights you** — it batches your background work, delays your alarms, and will restrict your app entirely if it drains too much. Users uninstall battery hogs, and both stores surface the data.

**4. You ship through a gatekeeper.**

You cannot deploy on Friday afternoon. **Apple and Google review your build**, which takes hours to days and can be rejected for reasons that aren't bugs. Then users must *choose* to update — **so old versions of your app live forever**, and your API must keep supporting them → [[mobile/13-release-and-distribution|release]].

**5. Fragmentation is real, especially on Android.**

Screen sizes, aspect ratios, notches, OS versions, manufacturer skins, and — on Android — vendors who alter background execution in undocumented ways. **"Works on my Pixel" means very little.**

**6. Permissions are asked, and refused.**

Location, camera, contacts, notifications: the user is prompted and **can say no, or grant "only this once"**. Your app must work — degraded but functional — without each one → [[mobile/09-permissions-and-privacy|permissions]].

## What this changes about how you build

| Web habit | Mobile reality |
|---|---|
| Deploy anytime | **Review queue**, and users choose when to update |
| Assume network | **Assume no network**, sync when it returns |
| Process runs until it doesn't | **Process is killed routinely.** Persist state |
| Fix forward | **Old versions persist for years.** Version your API |
| Fetch on render | **Cache first**, then refresh |
| Log to the server | User is offline. **Buffer, then send** |

## The thing that surprises web developers most

**There's no reload button.**

A bad web deploy is fixed in five minutes. A bad mobile release is in the store for days while review runs, and on users' phones for **months**. That single fact drives everything cautious about mobile engineering: staged rollouts, feature flags, remote config, and forced-update mechanisms.

**Feature flags aren't optional on mobile.** They're how you turn off a broken feature without shipping a build.

## What's genuinely nicer than web

Worth saying, because the list above is all constraints:

- **One platform, one renderer.** No browser matrix. What you test is what users get
- **Real APIs to real hardware** — camera, sensors, biometrics, NFC, background location — with none of the browser's sandboxing
- **A design system that's already there.** Both platforms ship comprehensive, accessible components. Accepting them gets you most of the way
- **Users pay for apps.** A payment relationship exists that the web spent thirty years failing to build
- **Performance is predictable.** You know the hardware range

## Key insight

**Mobile development is programming for an environment that can pause you, kill you, deny you resources, and refuse to ship your code** — none of which the web or the server does. Every practice in this folder is a response to not being in control of your own process.

## Related
- [[mobile/02-the-two-platforms|the two platforms]] — iOS and Android, compared honestly
- [[mobile/03-the-app-lifecycle|the app lifecycle]] — the constraint that shapes the most code
- [[mobile/14-native-vs-cross-platform|native vs cross-platform]] — the first real decision
- [[frontend/01-foundations/01-what-a-frontend-is|what a frontend is]] — the sibling discipline

*Source: [reference] — Aug 2026.*
