# Dart

**Google's client-application language, and in practice: the language you learn to use [[mobile/frameworks/flutter/README|Flutter]].**

**6 notes, built Aug 2026** alongside [[mobile/README|the mobile track]]. `[reference]`.

> **The one idea:** Dart is a deliberately unsurprising language whose one clever decision is **shipping both a JIT and an AOT compiler from the same source** — JIT in development buys Flutter sub-second *stateful* hot reload, AOT in release buys native performance. That single trick is what justifies the language's existence.

## Why this exists

Written for the [[mobile/README|mobile track]], because Flutter is one of the four stacks in [[mobile/frameworks/README|frameworks/]] and the vault had nothing on Dart.

**The honest scope note:** learning Dart means committing to Flutter. Dart on the server is niche and Dart for the web is legacy. **That's a reasonable commitment — just make it knowingly**, because as a general-purpose language Dart has no argument against Kotlin, TypeScript or Go.

## Reading order

**Shorter than the other language courses on purpose** — Dart holds few surprises for anyone who knows Java, C# or TypeScript, so this covers what's actually different.

1. [[languages/10-dart/01-why-dart-and-the-toolchain|why-dart-and-the-toolchain]] — **[Beginner]** — **the JIT/AOT trick that makes hot reload possible**, pub, and where Dart is weaker
2. [[languages/10-dart/02-types-and-null-safety|types-and-null-safety]] — **[Beginner → Intermediate]** — **sound** null safety (no platform-type hole, unlike Kotlin), flow promotion and where it fails, and Dart 3's records, patterns and sealed classes
3. [[languages/10-dart/03-classes-and-collections|classes-and-collections]] — **[Intermediate]** — mixins, `const` constructors (a real Flutter performance win), lazy `Iterable`s, and **control flow inside collection literals** — the syntax that makes widget trees read well
4. [[languages/10-dart/04-async-and-isolates|async-and-isolates]] — **[Intermediate → Advanced]** — a single-threaded event loop, so **no locks and no data races** — and isolates for when CPU work would freeze the UI
5. [[languages/10-dart/05-testing-and-errors|testing-and-errors]] — **[Intermediate]** — **Dart's exception model gives you no compiler help**, so sealed result types earn their place. Plus the three tiers of Flutter testing
6. [[languages/10-dart/06-tooling-and-codegen|tooling-and-codegen]] — **[Intermediate]** — `build_runner`, `freezed`, and **Dart's most-felt weakness: no macros, so everything needs a build step**

## If you only take three things

1. **`.toList()` after `map` and `where`** — they're lazy `Iterable`s, and forgetting is the classic Dart bug ([[languages/10-dart/03-classes-and-collections|03]]).
2. **CPU work goes in an isolate**, or it freezes the UI ([[languages/10-dart/04-async-and-isolates|04]]).
3. **Use `freezed`.** Hand-writing `==`, `hashCode` and `copyWith` is how Dart codebases rot ([[languages/10-dart/06-tooling-and-codegen|06]]).

## Related
- [[mobile/frameworks/flutter/README|Flutter]] — the reason this language exists for you
- [[mobile/README|mobile]] — the course this was written alongside
- [[languages/README|languages]] · [[languages/projects|projects]]
- [[languages/09-kotlin/README|Kotlin]] — the closest comparison, and the one Dart is usually weighed against
