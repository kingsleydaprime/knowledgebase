# The App Lifecycle

**[Intermediate]** — the constraint that shapes more mobile code than anything else: **your process is not yours.**

## The kid version first

Your app has three states: **on screen**, **in the background**, and **dead.**

The OS moves you between them without asking. Backgrounded, you get almost no CPU. Then, at any moment and with **no guaranteed warning**, the OS kills you to reclaim memory.

When the user comes back, they tap your icon and expect to be **exactly where they left off** — same screen, same scroll position, same half-typed message. Your process died an hour ago. **Making that seamless is the job.**

## The states

```
   NOT RUNNING
        │ user taps icon
        ▼
   FOREGROUND (active)  ←──────┐
        │ user switches away   │ user returns
        ▼                      │
   BACKGROUND ──────────────────┘
        │ OS needs memory
        ▼
   TERMINATED  ← no reliable callback. You may simply cease.
```

**The transition that matters is the last one.** Both platforms *try* to tell you, and **neither guarantees it**. iOS may terminate a suspended app silently; Android may kill your process without calling anything.

> **Save state when you're backgrounded, not when you're dying.** By the time you're dying, you may not get to run.

## Platform specifics

**iOS** delivers scene-phase transitions (`active` → `inactive` → `background`), and you get roughly **30 seconds** of background time to finish work before suspension. `applicationWillTerminate` **is not called** for suspended apps that get killed — a classic wrong assumption.

**Android** is more complex because of `Activity`: `onCreate` → `onStart` → `onResume` → `onPause` → `onStop` → `onDestroy`. Two things to internalise:

- **`onPause`/`onStop` are your save points.** `onDestroy` is not guaranteed
- **Configuration changes destroy and recreate the Activity by default** — including rotating the screen, changing dark mode, resizing in split-screen, or changing the language. **Your Activity is recreated from scratch, several times a day**

That second point is why Android has `ViewModel`, which survives configuration changes, and `SavedStateHandle`, which survives process death. **They solve different problems and you need both.**

## The three durations of state

Getting this taxonomy right is most of the work:

| State survives | Use |
|---|---|
| **A recomposition/redraw** | Local UI state — `remember`, `@State` |
| **A configuration change** (rotation) | `ViewModel` (Android), `@StateObject` (iOS) |
| **Process death** | **Persisted** — `SavedStateHandle`, `NSUserDefaults`/`DataStore`, or a database |

**The bug this catalogue prevents:** everything works in testing, then a user rotates their phone and loses a form, or leaves the app for twenty minutes and comes back to a blank screen. **The second one is process death and only appears in the wild** — which is why you must simulate it.

## Simulate process death, or you will ship the bug

**This is the single most important testing habit in mobile**, and most developers never do it. Pressing "back" or swiping the app away is **not** the same as the OS killing you — those are user-initiated and behave differently.

**Android:**
```
Developer options → "Don't keep activities"   ← leave this ON during development
# or, with the app backgrounded:
adb shell am kill <package>
```

**iOS:** in Xcode, background the app, then use Debug → Simulate Background Fetch, or stop and relaunch from the home screen rather than from Xcode.

**Do it for every screen.** Background the app, kill the process, return. If anything is lost or crashes, that's a real bug your users will hit.

## Deep links and cold start

A user taps a link, a notification, or a widget. **Your app may not be running.** So every entry point must work from a cold start:

```
notification tap → app not running → launch → restore auth →
    resolve the deep link → navigate to the right screen → THEN render
```

**The common bug:** the deep link is handled before authentication is restored, so the user lands on a login screen having lost the destination. **Queue the destination, restore session, then navigate** → [[mobile/06-navigation|navigation]].

## What good looks like

- **Persist as you go.** Save the draft on every change (debounced), not on submit
- **Treat every screen as resumable.** Ask: "if the process dies here, what does the user lose?"
- **Never hold important state only in memory**
- **Don't do slow work in lifecycle callbacks** — they're on the main thread, and blocking `onResume` is a visible stutter
- **Cancel work when you're backgrounded.** Both platforms tie coroutine/task scopes to lifecycle for exactly this; use them or you leak
- **Cold-start fast.** Users judge an app by launch time, and both stores measure it

## Key insight

**You are a guest in a process the OS owns and can revoke.** Everything else in mobile architecture — view models, saved-state handles, offline-first databases, resumable navigation — exists to make an app that is *repeatedly destroyed and recreated* feel to the user like it never went away.

## Related
- [[mobile/05-state-and-architecture|state and architecture]] — the patterns that handle this
- [[mobile/07-data-and-offline-first|offline-first]] — where persisted state lives
- [[mobile/10-background-work-and-push|background work]] — what you can do while not on screen
- [[foundations/os/02-processes-and-threads|processes]] — what "the OS kills your process" means underneath

*Source: [reference] — Aug 2026.*
