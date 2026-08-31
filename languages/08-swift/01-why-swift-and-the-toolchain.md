# Why Swift, and the Toolchain

**[Beginner]** — what Swift is for, and the tooling reality.

## What Swift is

Apple's replacement for Objective-C, open-sourced in 2015. **A statically-typed, memory-safe, compiled language** with a modern type system — optionals, value types, generics, protocols, and structured concurrency.

**Why you'd learn it:** it's the only first-class way to build for iOS, macOS, watchOS, visionOS and tvOS. That's the honest answer — **Swift on the server exists and is niche**, and it doesn't meaningfully compete with Go or Rust outside Apple's ecosystem.

**The design goal, and it shows everywhere:** *safe by default, fast, and expressive.* Where C is unsafe by default and Java is safe by being simple, **Swift is safe by making unsafety explicit** — you cannot accidentally use nil, and you cannot accidentally overflow an integer.

## The toolchain

**Xcode, on macOS.** For iOS development there is no alternative — you need Xcode to build, sign and submit.

```bash
swift --version
swift build            # Swift Package Manager
swift test
swift run

xcodebuild -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15' test
```

**Swift Package Manager** is the dependency manager. `Package.swift` is itself Swift code:

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-argument-parser", from: "1.3.0")
]
```

CocoaPods and Carthage exist in older projects. **Use SPM for anything new.**

**Xcode, honestly:** it's the least-loved major IDE in software. Slow indexing, unhelpful errors (especially in SwiftUI, where a type error in one line can produce "the compiler is unable to type-check this expression in reasonable time"), and previews that break. **Everyone puts up with it.** Learning its shortcuts and the Reset-Package-Caches / Clean-Build-Folder ritual pays for itself.

**On Linux and Windows:** Swift genuinely runs there and is well-supported for server and CLI work. **It cannot build iOS apps** — those need Apple's SDKs and Xcode.

## Style, briefly

```swift
struct UserProfile { }          // UpperCamelCase for types
let maximumRetryCount = 3       // lowerCamelCase for everything else
func fetchUser(withID id: String) async throws -> User { }
```

**Swift's API design guidelines are unusually opinionated**, and the ecosystem follows them closely. Method names read as phrases at the call site — `list.remove(at: 3)`, not `list.removeAt(3)`. **Argument labels are part of the name**, which is the biggest surface difference from most languages.

`swift-format` and SwiftLint are the standard tools.

## Versions

Swift moves fast. **Swift 6 (2024) introduced strict concurrency checking** — data races become compile-time errors. That's the largest change since the language stabilised, and migrating an existing codebase is real work → [[languages/08-swift/10-concurrency-and-actors|concurrency]].

**Your deployment target is a product decision**, not just a technical one: `@Observable`, SwiftData and `NavigationStack` all require iOS 17, and adopting them drops users below that.

## Key insight

**Swift is a genuinely well-designed modern language locked to one vendor's platforms.** Learning it is learning Apple development — which is a large, well-paid, and durable niche, and not a general-purpose skill the way Go or Python is. **Learn it because you want to ship on Apple platforms**, and it'll be a pleasure. Learn it as a general language and you'll wonder where the ecosystem is.

## Related
- [[languages/08-swift/README|the Swift course]]
- [[mobile/frameworks/ios/README|iOS]] — the platform
- [[languages/README|languages]] — the rule about what lives here
