---
id: 943d3d83-71b6-4b44-a3fe-71c44ebc2e01
---

# Testing and Tooling

Testing is writing small pieces of code that check your real code works, and tooling is the set of programs that help you find bugs and slow spots. Before an app goes to the App Store, these are how you know it behaves. This lesson covers Swift Testing, debugging, sanitizers and Instruments.

## Swift Testing — the new framework
<!-- bite: 5971d44e-3a91-4150-a94a-ae6e3c65c75f -->

Introduced 2024, and it's a genuine improvement:

```swift
import Testing

@Test func userParsesCorrectly() throws {
    let user = try JSONDecoder().decode(User.self, from: sampleJSON)
    #expect(user.name == "Ada")
    #expect(user.tags.count == 3)
}

@Test(arguments: [1, 2, 3, 100])
func doublingIsPositive(_ n: Int) {
    #expect(double(n) > 0)                    // runs once per argument
}

@Test func fetchThrowsOnMissing() async {
    await #expect(throws: NetworkError.notFound) {
        try await repo.fetch(id: "nope")
    }
}
```

**What's better than XCTest:** `#expect` shows the actual values on failure (no more `XCTAssertEqual` guessing), parameterised tests are one line, `async` works naturally, tests run in parallel by default, and no `XCTestCase` subclassing.

**XCTest is still required** for UI tests and performance tests, and it's what existing codebases use. **Both work in the same target.**

## What to actually test
<!-- bite: 7c90f05f-7b65-419b-819d-cb6ca11a501b -->

Mobile testing has an awkward cost curve, so aim deliberately:

- **View models — heavily.** Pure logic with a fake repository, milliseconds to run, and where your actual business rules live. **This is where the value is** → [[mobile/05-state-and-architecture|architecture]]
- **Repositories** — caching, merging, conflict handling
- **Parsing** — feed it real API responses, including malformed ones
- **A few UI tests** for critical flows only. They're slow and flaky; comprehensive UI testing is a trap
- **Snapshot tests** catch visual regressions cheaply (swift-snapshot-testing)

**Make dependencies injectable** — a protocol for the repository, a fake in tests. That's the whole reason for the protocol.

## Debugging
<!-- bite: 9ad4ea6c-d2d7-43cb-ba10-1c1febeb7dce -->

```text
po expression          # print object
p expression           # print value
bt                     # backtrace
v                      # variables (faster than po in recent LLDB)
```

**Breakpoint tricks worth knowing:**
- **Symbolic breakpoints** on `UIViewAlertForUnsatisfiableConstraints` catch Auto Layout problems at the moment they occur
- **An exception breakpoint** stops at the throw rather than in a useless stack frame. **Add this to every project** — it's the single most useful debugger setting
- **Conditional breakpoints** with a condition beat stepping through 500 iterations

## The sanitizers — turn these on
<!-- bite: 0c570cbc-709f-4ed9-888b-f8374314c34b -->

In the scheme's diagnostics settings:

- **Address Sanitizer** — memory errors
- **Thread Sanitizer** — **data races.** Genuinely finds bugs you'd never reproduce otherwise
- **Main Thread Checker** — on by default, catches UI updates off the main thread
- **Malloc Scribble / Zombie Objects** — use-after-free

**Run your test suite under Thread Sanitizer occasionally.** It's slow, and it finds real things.

## Instruments
<!-- bite: 0b3ffc4c-aa93-45b2-a114-cf667e5e4c72 -->

The profiler, and the templates that matter → [[mobile/11-performance-and-battery|performance]]:

- **Time Profiler** — where CPU goes
- **Allocations** / **Leaks** — memory growth
- **App Launch** — cold start breakdown
- **Energy Log** — battery impact

**And the Memory Graph Debugger** (the icon in the debug bar) for retain cycles → [[languages/08-swift/03-memory-and-arc|ARC]].

## The rest of the toolchain
<!-- bite: 353bc970-86e3-4c18-9441-130bb9f79ad5 -->

```bash
swift-format --in-place --recursive Sources/
swiftlint
```

- **SwiftLint** — the de facto linter. Configure it once, run it in CI
- **swift-format** — Apple's formatter
- **fastlane** — build, sign, screenshot, upload → [[mobile/13-release-and-distribution|release]]
- **Periphery** — finds unused code, which is surprisingly effective on an older project

## The Xcode problems everyone hits
<!-- bite: 8ffbcf31-5034-492f-9180-af4143b7d110 -->

Worth knowing the rituals, because you'll need them:

- **"Unable to type-check this expression in reasonable time"** — a SwiftUI view or a long expression chain. **Break it into smaller subexpressions with explicit types.** The error never points at the real problem
- **Previews crash or won't build** — Clean Build Folder (⇧⌘K), restart Xcode. Genuinely the fix, frustratingly
- **Package resolution stuck** — File → Packages → Reset Package Caches
- **Signing errors** — usually a mismatch between bundle ID, capabilities and profile → [[mobile/frameworks/ios/index|iOS]]
- **Derived data corruption** — delete `~/Library/Developer/Xcode/DerivedData`

**These aren't your fault**, and knowing the rituals saves hours of assuming they are.

## Key insight
<!-- bite: 78dbd455-34a8-4f12-b452-84abf37bec31 -->

**Swift Testing plus injectable dependencies makes the valuable tests cheap** — view-model logic runs in milliseconds and covers your actual rules. The trap is investing in UI tests, which are slow, flaky, and test the layer least likely to contain a real bug.

## Related
<!-- bite: e49311c1-fa83-4c83-b3af-5dc9a5d12441 -->
- [[mobile/05-state-and-architecture|architecture]] — what makes code testable
- [[languages/08-swift/10-concurrency-and-actors|concurrency]] — Thread Sanitizer's target
- [[mobile/13-release-and-distribution|release]] — CI and fastlane

## About this lesson
<!-- bite: 60e5d3f0-5a93-4a78-8322-8056f8ad5d50 -->

**Level:** Intermediate. **Covers:** Swift Testing, XCTest, and the tools worth configuring once.
