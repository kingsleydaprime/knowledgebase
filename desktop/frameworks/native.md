# Native per Platform — scaffold

**[Intermediate → Advanced]** · Write it once per OS, using that OS's own SDK. Best result, most work.

## The stacks

| Platform | UI | Language |
|---|---|---|
| **macOS** | SwiftUI (modern) / AppKit (mature) | **Swift** |
| **Windows** | WinUI 3 / WPF | **C#** |
| **Linux** | GTK4 / libadwaita, or Qt | C, Rust, Python, C++ |

## When this is right

**When the app *is* the platform experience.** Professional creative tools, system utilities, anything where users are expert and notice everything. Apple's own apps, Windows system tools.

**When you need APIs nobody wraps** — deep OS integration, a specific hardware framework, kernel-adjacent behaviour, a new platform feature on day one.

**When performance or size is genuinely critical.** A native app can be a few MB with near-zero idle memory.

**When you only ship to one platform.** If your users are all on macOS, "cross-platform" is a cost with no benefit — and SwiftUI is a genuinely pleasant way to build.

## The things to know

**The cost is linear in platforms and it is not amortised.** Three platforms is three UIs, three build pipelines, three sets of bugs, three areas of expertise. **The usual compromise is a shared core** — business logic in Rust, C++ or Kotlin Multiplatform — **with a native UI per platform.** That's the architecture behind several well-regarded cross-platform apps, and it's a straightforward application of [[foundations/systems-engineering/04-architecture-and-interfaces|interface design]]: put the boundary where the platforms genuinely differ, which is the UI, and share everything below it.

**SwiftUI and WinUI have converged on the same model** — declarative UI as a function of state, with the framework diffing. The same idea as React → [[frontend/frameworks/react/README|React]]. **Learning one makes the others much faster.**

**Accessibility, localisation and platform conventions come free**, which is the quiet argument for native and the thing cross-platform toolkits spend the most effort approximating.

## Related
- [[desktop/frameworks/README|frameworks/]] · [[desktop/01-what-desktop-development-is|what desktop development is]]

*Source: [reference] — scaffold, from Apple, Microsoft and GNOME documentation.*
