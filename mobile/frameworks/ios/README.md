# iOS

**Swift + SwiftUI.** The language is [[languages/08-swift/README|its own course]]; this is the platform.

## The toolchain

**Xcode, on a Mac. There is no alternative** — this is the hard requirement of iOS development.

```bash
xcodebuild -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15' test
xcrun simctl list                 # simulators
```

**Swift Package Manager** is the dependency manager now. CocoaPods still appears in older projects; **use SPM for anything new**.

**Signing** is where newcomers lose days — certificates, provisioning profiles, capabilities and bundle identifiers must all agree. **Use automatic signing**, and **fastlane match** for teams → [[mobile/13-release-and-distribution|release]].

## SwiftUI

```swift
struct ContentView: View {
    @StateObject private var vm = FeedViewModel()

    var body: some View {
        NavigationStack {
            List(vm.items) { item in
                NavigationLink(value: item) { ItemRow(item: item) }
            }
            .navigationDestination(for: Item.self) { ItemDetail(id: $0.id) }
            .task { await vm.load() }          // cancelled automatically on disappear
            .refreshable { await vm.refresh() }
        }
    }
}
```

**The property wrappers, which is what trips people up:**

| | Use |
|---|---|
| `@State` | Simple value owned by this view |
| `@Binding` | A two-way reference to state owned above |
| `@StateObject` | **The view creates and owns** a reference-type model. Created once |
| `@ObservedObject` | A model **passed in** from elsewhere. **Recreated on every redraw** |
| `@Environment` | Injected dependencies and system values |
| `@Observable` (iOS 17+) | **The modern replacement** for ObservableObject — less boilerplate, finer-grained updates |

**The classic bug:** using `@ObservedObject` where you meant `@StateObject`. The object is recreated on every view update, so state resets and network calls repeat. **If this view creates it, use `@StateObject`.**

**Use `@Observable` for new code** — it supersedes most of the above.

## Concurrency

Swift's structured concurrency is the model now:

```swift
@MainActor
final class FeedViewModel: ObservableObject {
    @Published private(set) var items: [Item] = []

    func load() async {
        do { items = try await repository.fetch() }
        catch { /* surface it */ }
    }
}
```

- **`@MainActor`** guarantees main-thread execution — put it on view models
- **`.task { }`** ties an async task to the view's lifetime and **cancels it on disappear**. Prefer it to `.onAppear`
- **Actors** protect mutable state from data races
- **Swift 6's strict concurrency checking** turns data races into compile errors. Genuinely valuable, and migrating an existing codebase is real work

## The platform pieces

- **SwiftData** (iOS 17+) for persistence; **Core Data** underneath it and still everywhere; **GRDB** if you want SQLite directly → [[mobile/07-data-and-offline-first|offline-first]]
- **URLSession** with async/await — you rarely need a networking library
- **Keychain** for tokens; **Secure Enclave** for hardware-backed keys → [[mobile/12-security-on-device|security]]
- **BackgroundTasks** for deferred work; **APNs** for push → [[mobile/10-background-work-and-push|background work]]
- **WidgetKit, Live Activities, App Intents** — the platform integrations that are a real reason to go native
- **Instruments** for profiling; **MetricKit** for field data → [[mobile/11-performance-and-battery|performance]]

## UIKit is not optional knowledge

**SwiftUI still can't do everything**, and most real codebases mix. `UIViewRepresentable` and `UIHostingController` bridge the two. **Expect to read UIKit**, especially for complex collection views, precise text input, and camera work.

## The iOS-specific gotchas

- **`@ObservedObject` vs `@StateObject`** — the recreation bug above
- **SwiftUI previews break constantly.** Frustrating, not your fault
- **`onAppear` fires more than you expect** — on navigation returns, on tab switches. Use `.task(id:)` when you need it once
- **Retain cycles** in closures capturing `self`. `[weak self]`, and Instruments' Memory Graph finds them
- **Minimum deployment target is a real product decision** — newer APIs (`@Observable`, SwiftData, NavigationStack) each cost you the users below that version
- **App Store review is strict** → [[mobile/13-release-and-distribution|release]]

## Related
- [[languages/08-swift/README|Swift]] — the language
- [[mobile/README|the mobile course]] · [[mobile/frameworks/README|frameworks]]
- [[mobile/04-declarative-ui|declarative UI]] — the model SwiftUI implements
