# State and Architecture

**[Intermediate]** — the layered shape both platforms converged on, and the rule that makes it work.

## The kid version first

Three jobs, kept apart:

- **The screen** draws things and reports taps. It knows nothing else.
- **The view model** holds what the screen should show, and decides what happens on a tap.
- **The repository** gets data — from the network, from the database — and hides which.

**Keep those separate and the app is testable, survives being killed, and doesn't turn into one 3,000-line file.** Merge them and it does.

## The layers

```
   UI (SwiftUI / Compose)        ← stateless. Renders state, emits events
        │ state ↓      ↑ events
   ViewModel                     ← holds UI state, survives rotation
        │
   Repository                    ← the single source of truth for a kind of data
        │
   ┌────┴────┐
 Network   Database              ← Database is usually the REAL source of truth
```

**The rule that makes it work: data flows down, events flow up.** No layer reaches back up. The UI never calls the network; the repository never knows a screen exists.

## Unidirectional data flow

```
  ┌──────────────────────────────────────────┐
  │                                          │
State ──► UI renders ──► user acts ──► Event ┘
                                        │
                              ViewModel handles it,
                              produces NEW state
```

**One direction, one place where state changes.** When something is wrong on screen, there's exactly one place to look. This is the same idea as Redux, Elm and React's model → [[frontend/04-state-and-data/README|state and data]].

## Model UI state as one type

The highest-value habit here, and the one most codebases miss:

```kotlin
// BAD — four booleans = 16 combinations, most of them nonsense
var isLoading: Boolean
var error: String?
var data: List<Item>?
var isEmpty: Boolean
```

```kotlin
// GOOD — the impossible states can't be represented
sealed interface UiState {
    data object Loading : UiState
    data class Success(val items: List<Item>) : UiState
    data class Error(val message: String, val retryable: Boolean) : UiState
}
```

**With booleans you will eventually render a spinner over an error over stale data**, because nothing stopped you. With a sealed type — or a Swift `enum` with associated values — **the compiler makes that unrepresentable**, and `when`/`switch` forces you to handle every case.

**And note `Success(emptyList())` is a real state that needs its own UI.** "Loaded, and there's nothing" is not "loading", and shipping a spinner forever for empty results is a classic.

## Where state lives — the three durations

From [[mobile/03-the-app-lifecycle|the lifecycle note]], because it's the thing to get right:

| Survives | Mechanism |
|---|---|
| Redraw | `remember` / `@State` |
| **Rotation** | `ViewModel` / `@StateObject` |
| **Process death** | `SavedStateHandle`, DataStore, database |

**Test the third one deliberately** — background the app, kill the process, return.

## Events that should happen once

A subtle bug worth naming: **navigation, toasts and dialogs are events, not state.**

If "show error snackbar" is a boolean in your state, rotating the screen re-emits it and the snackbar shows again. And again.

**The fix:** a `Channel`/`SharedFlow` of one-shot events (Android), or state that the UI explicitly consumes and clears. **Any "why does this toast appear twice" bug is this.**

## The repository, and the source of truth

```kotlin
fun observeItems(): Flow<List<Item>> = database.observeItems()   // UI reads THIS

suspend fun refresh() {
    val fresh = api.getItems()
    database.upsert(fresh)                                       // UI updates automatically
}
```

**The UI observes the database, never the network.** The network's only job is to update the database. This gives you offline support, instant launches, and a UI that can't show a spinner forever because the data is already there → [[mobile/07-data-and-offline-first|offline-first]].

**This is the single most important architectural decision in a mobile app**, and it's cheap if you make it on day one and expensive later.

## Dependency injection

You need it to swap the network for a fake in tests. **Constructor injection is enough** — a framework is optional.

- **Android:** Hilt is the standard; Koin is lighter
- **iOS:** often manual, or a lightweight container. SwiftUI's `@Environment` covers a lot

**Whatever you choose, the point is that a ViewModel takes its repository as a parameter** rather than constructing one. That's what makes it testable.

## What to actually test

Mobile testing has an awkward cost curve — UI tests are slow and flaky. So:

- **Test ViewModels heavily.** They're pure logic with fake repositories, run in milliseconds, and hold your actual business rules. **This is where the value is**
- **Test repositories** — caching, merge, conflict logic
- **A few UI tests** for critical flows only (login, checkout). Not comprehensive coverage
- **Screenshot tests** catch visual regressions cheaply
- **Test process death.** Not automatable easily; do it by hand per screen

## Key insight

**Both platforms converged on the same architecture because the lifecycle forced them to** — when the OS can destroy your UI at any moment, state cannot live in the UI. Everything else (unidirectional flow, sealed state types, database-as-source-of-truth) follows from putting state somewhere that outlives the screen.

## Related
- [[mobile/03-the-app-lifecycle|the app lifecycle]] — the constraint this answers
- [[mobile/07-data-and-offline-first|offline-first]] — the repository pattern in full
- [[frontend/03-structuring-a-frontend/README|structuring a frontend]] — the same layering
- [[backend/03-structuring-a-backend/README|structuring a backend]] — and again

*Source: [reference] — Aug 2026.*
