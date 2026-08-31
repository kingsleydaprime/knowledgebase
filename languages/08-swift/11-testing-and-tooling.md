# Testing and Tooling

**[Intermediate]** — Swift Testing, XCTest, and the tools worth configuring once.

## Swift Testing — the new framework

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

Mobile testing has an awkward cost curve, so aim deliberately:

- **View models — heavily.** Pure logic with a fake repository, milliseconds to run, and where your actual business rules live. **This is where the value is** → [[mobile/05-state-and-architecture|architecture]]
- **Repositories** — caching, merging, conflict handling
- **Parsing** — feed it real API responses, including malformed ones
- **A few UI tests** for critical flows only. They're slow and flaky; comprehensive UI testing is a trap
- **Snapshot tests** catch visual regressions cheaply (swift-snapshot-testing)

**Make dependencies injectable** — a protocol for the repository, a fake in tests. That's the whole reason for the protocol.

## Debugging

```
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

In the scheme's diagnostics settings:

- **Address Sanitizer** — memory errors
- **Thread Sanitizer** — **data races.** Genuinely finds bugs you'd never reproduce otherwise
- **Main Thread Checker** — on by default, catches UI updates off the main thread
- **Malloc Scribble / Zombie Objects** — use-after-free

**Run your test suite under Thread Sanitizer occasionally.** It's slow, and it finds real things.

## Instruments

The profiler, and the templates that matter → [[mobile/11-performance-and-battery|performance]]:

- **Time Profiler** — where CPU goes
- **Allocations** / **Leaks** — memory growth
- **App Launch** — cold start breakdown
- **Energy Log** — battery impact

**And the Memory Graph Debugger** (the icon in the debug bar) for retain cycles → [[languages/08-swift/03-memory-and-arc|ARC]].

## The rest of the toolchain

```bash
swift-format --in-place --recursive Sources/
swiftlint
```

- **SwiftLint** — the de facto linter. Configure it once, run it in CI
- **swift-format** — Apple's formatter
- **fastlane** — build, sign, screenshot, upload → [[mobile/13-release-and-distribution|release]]
- **Periphery** — finds unused code, which is surprisingly effective on an older project

## The Xcode problems everyone hits

Worth knowing the rituals, because you'll need them:

- **"Unable to type-check this expression in reasonable time"** — a SwiftUI view or a long expression chain. **Break it into smaller subexpressions with explicit types.** The error never points at the real problem
- **Previews crash or won't build** — Clean Build Folder (⇧⌘K), restart Xcode. Genuinely the fix, frustratingly
- **Package resolution stuck** — File → Packages → Reset Package Caches
- **Signing errors** — usually a mismatch between bundle ID, capabilities and profile → [[mobile/frameworks/ios/README|iOS]]
- **Derived data corruption** — delete `~/Library/Developer/Xcode/DerivedData`

**These aren't your fault**, and knowing the rituals saves hours of assuming they are.

## Key insight

**Swift Testing plus injectable dependencies makes the valuable tests cheap** — view-model logic runs in milliseconds and covers your actual rules. The trap is investing in UI tests, which are slow, flaky, and test the layer least likely to contain a real bug.

## Related
- [[mobile/05-state-and-architecture|architecture]] — what makes code testable
- [[languages/08-swift/10-concurrency-and-actors|concurrency]] — Thread Sanitizer's target
- [[mobile/13-release-and-distribution|release]] — CI and fastlane
