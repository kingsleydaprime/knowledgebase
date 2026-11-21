---
id: beea9564-6f81-43a4-8c03-fbaa17d47668
---

# Structs, Classes and Initialisation

**[Intermediate]** — the initialiser rules, which are more intricate than they look, and the property features you'll use daily.

## Initialisers
<!-- bite: 3cbdbf2d-5f04-4704-8f8e-fff18b169cfc -->

```swift
struct Point {
    var x: Int
    var y: Int
}
let p = Point(x: 1, y: 2)          // memberwise init — FREE for structs
```

**Structs get a memberwise initialiser automatically. Classes do not** — you write every initialiser yourself.

**A caution:** the memberwise init is **`internal`**, so it isn't visible outside your module. **A struct in a package needs an explicit `public init`**, and forgetting that is the most common Swift package mistake.

**And defining any `init` in the struct's own declaration suppresses the memberwise one.** Put custom initialisers in an `extension` to keep both.

## The class initialisation rules
<!-- bite: ff46ef27-4f9a-4a34-8432-2160f4610bff -->

```swift
class Vehicle {
    var wheels: Int
    init(wheels: Int) { self.wheels = wheels }
}

class Car: Vehicle {
    var brand: String
    init(brand: String) {
        self.brand = brand          // 1. own properties FIRST
        super.init(wheels: 4)       // 2. then super
    }
}
```

**The order is enforced:** initialise your own stored properties, then call `super.init`, then you may use `self`. **The compiler will tell you**, but knowing why saves confusion — Swift guarantees no method sees a partially-initialised object, which is a real class of bug in C++ and Java.

**`required init`** must be implemented by subclasses. **`convenience init`** must delegate to a designated initialiser in the same class.

**Failable initialisers** return an optional:

```swift
init?(rawValue: String) { ... }        // nil if invalid
```

## Properties
<!-- bite: c91b5de7-4ab8-496e-a9d5-8aa91060501e -->

```swift
struct Circle {
    var radius: Double

    var area: Double { .pi * radius * radius }        // COMPUTED — no storage

    var diameter: Double {
        get { radius * 2 }
        set { radius = newValue / 2 }
    }

    lazy var expensive = computeOnce()                 // computed on first access only

    var name: String = "" {
        willSet { print("about to become \(newValue)") }
        didSet  { print("was \(oldValue)") }            // OBSERVERS
    }
}
```

**`lazy` is genuinely useful** for expensive setup you may not need — but it makes the struct mutating on first read, so a `lazy var` in a struct can't be read from a `let`.

**`didSet` doesn't fire during initialisation** — a real gotcha when you rely on it to keep something in sync.

## Property wrappers
<!-- bite: 66414609-f46e-4eee-87e9-82856ec42068 -->

The mechanism behind `@State`, `@Published` and friends:

```swift
@propertyWrapper
struct Clamped {
    private var value: Int
    private let range: ClosedRange<Int>

    var wrappedValue: Int {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }
    init(wrappedValue: Int, _ range: ClosedRange<Int>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

struct Settings {
    @Clamped(0...100) var volume = 50
    // volume = 150  →  stores 100
}
```

**Worth understanding rather than writing.** Knowing that `@State` is a struct with a `wrappedValue` demystifies why the SwiftUI wrappers behave as they do — including why `@ObservedObject` recreates its object and `@StateObject` doesn't → [[mobile/frameworks/ios/index|SwiftUI]].

## Extensions
<!-- bite: 149e5493-7863-40bc-90e8-720284ff1fc8 -->

```swift
extension String {
    var isValidEmail: Bool { contains("@") }
}

extension Array where Element: Numeric {
    var total: Element { reduce(0, +) }
}
```

**Add methods to any type, including the standard library's and Apple's.** No subclassing, no wrappers.

**You cannot add stored properties** — only computed ones — because that would change the type's memory layout.

**Extensions are also the idiomatic way to organise a file**: the type's stored properties in the main declaration, and each protocol conformance in its own extension. That's the convention across the ecosystem.

## `static` vs `class` members
<!-- bite: 320fb4bc-2a6c-4474-8bf7-73937202edd4 -->

```swift
struct Config { static let shared = Config() }
class Base { class func make() -> Self { ... } }   // `class` = overridable static
```

## Key insight
<!-- bite: 95b8158e-244c-43b0-9b28-47e1b70098e7 -->

**Swift's initialisation rules exist to guarantee that no code ever observes a partially-constructed object** — which is why the ordering is enforced and why classes don't get a free memberwise init. The rules feel fussy until you've debugged the equivalent bug in a language that doesn't have them.

## Related
<!-- bite: 9a328e1f-41f8-4db8-9e98-df620eda52bd -->
- [[languages/08-swift/02-values-references-and-optionals|value vs reference types]]
- [[languages/08-swift/04-protocols-and-generics|protocols and extensions]]
- [[mobile/frameworks/ios/index|SwiftUI]] — property wrappers in practice
