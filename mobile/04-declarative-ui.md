# Declarative UI

**[Intermediate]** — SwiftUI and Compose are the same idea, and it's the idea React had.

## The kid version first

**Old way (imperative):** you build the screen, keep a reference to every label and button, and when data changes you find each one and update it by hand. Miss one and the screen lies.

**New way (declarative):** you write a function that says *"given this data, the screen looks like this."* When the data changes, the framework re-runs your function and works out what to change on screen.

**You describe the destination; the framework finds the route.**

## The shape, on both platforms

```swift
// SwiftUI
struct CounterView: View {
    @State private var count = 0
    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("Increment") { count += 1 }
        }
    }
}
```

```kotlin
// Jetpack Compose
@Composable
fun CounterView() {
    var count by remember { mutableStateOf(0) }
    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) { Text("Increment") }
    }
}
```

**Those are the same program.** If you know [[frontend/frameworks/react/README|React]], you already know this model — `@State`/`remember` is `useState`, and `body`/`@Composable` is the render function.

**This convergence is the single most useful fact in mobile right now:** learn the model once and it transfers across SwiftUI, Compose, React Native and Flutter.

## The core rules

**1. UI is a function of state.** The same state always produces the same UI. **No hidden mutation** — if the screen shows something not derivable from your state, you have a bug waiting.

**2. Your UI function will run many times, unpredictably.** So it must be:
- **Fast** — no network calls, no database reads, no heavy computation
- **Side-effect free** — logging, analytics or navigation inside the body is a bug. Compose calls this "recomposition"; SwiftUI just re-evaluates. **Neither tells you how often**

**3. Side effects have their own escape hatches** — `LaunchedEffect`/`DisposableEffect` in Compose, `.task`/`.onAppear` in SwiftUI. They exist precisely because the body can't do this.

**4. Identity matters in lists.** Both frameworks need stable keys (`id:` in SwiftUI's `ForEach`, `key =` in Compose's `items`) to tell "this item moved" from "this item was replaced". **Without them, lists lose scroll position, animations jump, and state attaches to the wrong row** — the same bug as React's key warning.

## State hoisting — the pattern to learn

**Push state up; pass data down; pass events up.** A component that owns its own state can't be controlled, tested or reused.

```kotlin
// stateful — hard to test, can't be controlled from outside
@Composable fun Counter() { var n by remember { mutableStateOf(0) } ... }

// stateless — a pure function of its inputs. Testable, previewable, reusable
@Composable fun Counter(n: Int, onIncrement: () -> Unit) { ... }
```

**Make components stateless by default**, and let state live in a view model → [[mobile/05-state-and-architecture|state and architecture]]. This is the same "lifting state up" advice as React, and it's just as load-bearing.

## Performance

The framework re-runs your code a lot, so:

- **Keep state as narrow as possible.** State high in the tree re-renders everything under it. **The commonest mobile performance bug is one big state object at the root**
- **Use lazy containers for lists** — `LazyColumn`, `List`, `LazyVStack`. A non-lazy column builds every child, which is fine for 20 items and fatal for 2,000
- **Stable keys** on list items
- **Watch for unstable parameters.** Compose can skip re-running a composable only if it can prove its inputs are unchanged — **passing a lambda or an unstable class defeats this.** Compose's compiler metrics show you where
- **Never allocate in the body.** Creating a formatter or a list inside a composable creates it on every recomposition

## The legacy systems are not gone

**UIKit** (iOS) and **the View system** (Android) are imperative, mature, and still enormous in real codebases. Both platforms provide interop (`UIViewRepresentable`, `AndroidView`), and **most real apps are mixed**.

**Learn the declarative one first** — it's where new code goes — but expect to read the old one, and expect to drop into it for things the new frameworks still don't do well.

## Accessibility, which is not optional

Both platforms ship strong accessibility support and both stores care:

- **Label everything meaningful** — `contentDescription` (Compose), `.accessibilityLabel` (SwiftUI). An unlabelled icon button is a dead end for a screen-reader user
- **Respect the user's text size.** Dynamic Type and Android's font scale are widely used, especially by older users. **Test at 200%** — fixed-height containers break here
- **Hit targets ≥ 44pt (iOS) / 48dp (Android)**
- **Honour reduce-motion**
- **Test with VoiceOver and TalkBack.** Ten minutes, and it finds things nothing else does → [[frontend/06-cross-cutting/README|accessibility]]

## Key insight

**SwiftUI, Compose, React Native and Flutter have converged on one model — UI as a pure function of state, with the framework diffing the result.** So the transferable skill isn't a framework; it's the discipline the model demands: narrow state, stateless components, stable keys, and no side effects in the render path.

## Related
- [[mobile/05-state-and-architecture|state and architecture]] — where the state actually lives
- [[frontend/frameworks/react/README|React]] — the same model, and where it came from
- [[frontend/02-rendering/README|rendering]] — the general theory
- [[mobile/11-performance-and-battery|performance]]

*Source: [reference] — Aug 2026.*
