# Codable and JSON

**[Intermediate]** — compiler-generated serialisation, and the customisations you'll actually need.

## The free case

```swift
struct User: Codable {
    let id: String
    let name: String
    let email: String
}

let user = try JSONDecoder().decode(User.self, from: data)
let data = try JSONEncoder().encode(user)
```

**The compiler synthesises the encoding and decoding** as long as every property is itself `Codable`. Nested structs, arrays, optionals and enums with raw values all work automatically.

**This is one of Swift's best features** — no annotations, no reflection, no third-party library, and it's type-checked.

## Key naming

```swift
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase    // user_name → userName
```

Or per-property:

```swift
struct User: Codable {
    let id: String
    let displayName: String

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
    }
}
```

**Defining `CodingKeys` means listing every key you want included** — omitting one excludes that property entirely, which is either the bug or the feature depending on intent.

## Dates, which is where it usually goes wrong

```swift
decoder.dateDecodingStrategy = .iso8601                     // the common case
decoder.dateDecodingStrategy = .secondsSince1970
decoder.dateDecodingStrategy = .custom { ... }
```

**The default is `.deferredToDate`, which is a Core Data timestamp format nobody's API uses.** Set the strategy explicitly, always — a mismatched date format is the most common Codable failure.

**And note `.iso8601` doesn't accept fractional seconds by default**, which many APIs send. If you're getting date failures from a well-formed ISO string, that's why — use a custom formatter.

## Custom decoding

When the synthesised version isn't enough:

```swift
struct Product: Decodable {
    let id: String
    let price: Decimal
    let tags: [String]

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(String.self, forKey: .id)

        // API sends price as a string
        let raw = try c.decode(String.self, forKey: .price)
        price = Decimal(string: raw) ?? 0

        // tags may be absent
        tags = try c.decodeIfPresent([String].self, forKey: .tags) ?? []
    }
}
```

**`decodeIfPresent` with a default is the workhorse** — it handles both "key missing" and "value is null".

## The mobile-specific trap: strict enums

```swift
enum Status: String, Codable { case active, suspended }
```

**If the server adds `"archived"`, decoding fails and the whole object is lost.** Old app versions live for years, so this breaks users who can't update → [[mobile/08-networking-on-mobile|API compatibility]].

**The fix:**

```swift
enum Status: String, Codable {
    case active, suspended, unknown

    init(from decoder: Decoder) throws {
        let raw = try decoder.singleValueContainer().decode(String.self)
        self = Status(rawValue: raw) ?? .unknown
    }
}
```

**Do this for every server-controlled enum.** It's a two-minute change that prevents a class of production breakage you cannot hotfix.

## Failing gracefully on lists

One bad element shouldn't lose the whole response:

```swift
struct Safe<T: Decodable>: Decodable {
    let value: T?
    init(from decoder: Decoder) throws {
        value = try? decoder.singleValueContainer().decode(T.self)
    }
}

let items = try decoder.decode([Safe<Item>].self, from: data).compactMap(\.value)
```

**Whether you want this is a judgement call** — silently dropping records hides server bugs. **Log what you dropped.**

## Debugging failures

`DecodingError` is genuinely informative if you read it:

```swift
catch let DecodingError.keyNotFound(key, context) {
    print("Missing '\(key.stringValue)' at \(context.codingPath)")
} catch let DecodingError.typeMismatch(type, context) {
    print("Expected \(type) at \(context.codingPath)")
}
```

**`context.codingPath` tells you exactly where in the JSON it failed** — print it rather than guessing. Most "Codable is confusing" experiences are from catching the error generically and losing this.

## Key insight

**Codable removes the boilerplate and the reflection cost, and leaves you exactly two decisions: dates and unknown values.** Both have a correct answer — set the date strategy explicitly, and give every server-controlled enum an `unknown` case — and both are cheap to get right up front and expensive to discover in production.

## Related
- [[languages/08-swift/05-enums-and-pattern-matching|enums]] — the unknown-case pattern
- [[mobile/08-networking-on-mobile|networking]] — why old clients matter
- [[languages/08-swift/06-error-handling|error handling]]
