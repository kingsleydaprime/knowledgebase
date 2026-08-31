# Navigation

**[Intermediate]** — the back stack, deep links, and why navigation is harder on mobile than on the web.

## The kid version first

On the web, the URL *is* the state — paste it anywhere and you land on the same page.

On mobile there's no address bar, so the app keeps a **stack** of screens in memory: push to go deeper, pop to go back. Simple, until you remember [[mobile/03-the-app-lifecycle|the OS kills your process]] — **and then that stack has to be rebuilt from nothing.**

The modern answer is to make mobile navigation more like the web: **give every screen an address.**

## The back stack

```
push Home → push List → push Detail
   [Home, List, Detail]        ← back pops Detail
```

**Android has a hardware/gesture back button, and it is a system-wide contract.** Users expect it to work everywhere, and breaking it is one of the fastest ways to get bad reviews. **iOS has no back button** — it has a back *gesture* and a nav-bar button you provide.

**The practical consequence:** on Android, handle back explicitly for anything that isn't a simple pop — a bottom sheet, a multi-step form, unsaved changes. Ignoring back is a bug; hijacking it is worse.

## Type-safe routes

Both ecosystems have converged on describing destinations as data:

```kotlin
// Compose Navigation, type-safe (Navigation 2.8+)
@Serializable data class ProductDetail(val id: String)

navController.navigate(ProductDetail(id = "abc123"))
```

```swift
// SwiftUI NavigationStack
@State private var path = NavigationPath()
path.append(Product(id: "abc123"))
```

**SwiftUI's `NavigationStack` (iOS 16+) was the important fix** — the old `NavigationLink`-based system made programmatic navigation and deep linking genuinely painful. Anything you read from before that is describing a system you shouldn't copy.

**Why type-safe routes matter:** string routes (`"product/$id"`) are a runtime error waiting to happen — a typo compiles fine and crashes in production. **Make destinations a sealed type or an enum**, and the compiler checks them.

## Deep links — where it gets hard

A user taps a link in a message, an email, or a push notification. Your app may be **cold** — not running at all.

```
link tapped
   → app not running → cold start
       → restore auth session
           → resolve the link to a destination
               → build a sensible back stack
                   → render
```

**Three things people get wrong:**

**1. Navigating before auth is restored.** The user lands on login and the destination is lost. **Queue the destination, restore the session, then navigate.**

**2. An empty back stack.** The user deep-links into a product page, presses back, and the app closes. **Synthesise a back stack** — most users expect back to go to the list or home, not to exit.

**3. Not verifying the link.** Use **App Links** (Android) and **Universal Links** (iOS) — verified via a file hosted on your domain — rather than custom schemes (`myapp://`). **Custom schemes can be registered by any other app**, which is a genuine hijacking vector → [[mobile/12-security-on-device|security]].

## Modals, sheets and tabs

- **Tabs** each keep their **own** back stack. Switching tabs preserves where you were in each. Getting this wrong — resetting a tab's stack on switch — is immediately noticeable
- **Modals interrupt.** Use them for a self-contained task; the dismiss action must be obvious
- **Bottom sheets are Android-idiomatic** and increasingly used on iOS
- **Don't nest navigation deeply.** A modal containing a tab bar containing a stack is a maintenance problem and a confusing experience

## Passing data between screens

**Pass IDs, not objects.**

```kotlin
navigate(ProductDetail(id = product.id))     // ✅
navigate(ProductDetail(product = product))   // ❌
```

Two reasons: **the object may be stale** by the time the destination renders, and **it must survive process death** — which means serialising it into the saved state, which means it must be small. **An ID plus a repository lookup is correct, current, and survives everything.**

For results flowing *back* (a picker returning a selection), use the platform's result API or shared state — **not a callback captured in the previous screen**, which won't survive recreation.

## Key insight

**Mobile navigation is a stack in memory that must be reconstructible from nothing** — because a deep link, a notification tap or a process kill can drop the user anywhere with no history. Treating every destination as an addressable, serialisable value (an ID, not an object) is what makes that possible, and it's the web's URL model arriving on mobile late.

## Related
- [[mobile/03-the-app-lifecycle|the app lifecycle]] — why the stack must be rebuildable
- [[mobile/10-background-work-and-push|push notifications]] — the other cold-start entry point
- [[mobile/12-security-on-device|security]] — deep link hijacking
- [[frontend/03-structuring-a-frontend/README|frontend routing]] — the comparison

*Source: [reference] — Aug 2026.*
