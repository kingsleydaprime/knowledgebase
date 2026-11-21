---
id: dd501ffe-7a35-4083-9457-7e4124a7579f
---

# Why Dart, and the Toolchain

**[Beginner]** — an honest account of a language that exists to serve one framework.

## What Dart is
<!-- bite: e3129d7d-c4e4-4b22-ab89-d534445118a6 -->

**A statically-typed, garbage-collected, object-oriented language** that Google built for client applications. Familiar if you know Java, C# or TypeScript — the syntax holds no surprises.

**Why you'd learn it: Flutter.** That's the honest answer. Dart on the server exists (`shelf`, `dart_frog`) and is niche; Dart for the web is legacy. **Learning Dart means committing to Flutter**, and that's a reasonable commitment — just make it knowingly.

## The two compilation modes — the thing that makes Flutter work
<!-- bite: 72111d71-e36a-4b9c-b715-c5728bb6bcf4 -->

This is Dart's genuinely interesting property:

| | Development | Release |
|---|---|---|
| Mode | **JIT** | **AOT** |
| Gives you | **Stateful hot reload in under a second** | Native machine code, fast startup |

**Hot reload is the reason Flutter's iteration loop feels good**, and it's a direct consequence of JIT in development. Change a widget, save, and the UI updates **while keeping its state** — you don't lose your place in a form or a navigation stack.

**AOT in release** means no interpreter warm-up and no JIT pauses, which matters for animation smoothness.

**Most languages pick one.** Dart shipping both, with the same source, is the design decision that justifies its existence.

## The toolchain
<!-- bite: 30023624-78ef-4756-80ec-252b072ff646 -->

```bash
dart --version
dart create my_app
dart run
dart test
dart format .            # not configurable — that's the point
dart analyze
dart fix --apply         # auto-applies many lint fixes

flutter create my_app
flutter run              # press r for hot reload, R for hot restart
flutter test
flutter build appbundle --release
```

**`pub`** is the package manager; `pub.dev` is the registry. Dependencies go in `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.2.0
dev_dependencies:
  test: ^1.25.0
```

**Check package health on pub.dev before depending on it** — the scores and maintenance status are shown, and **an abandoned package is a real risk in an ecosystem this size.**

**`dart format` has no options.** Deliberately — the ecosystem doesn't argue about formatting.

## The syntax, briefly
<!-- bite: 96b3f149-5230-4a65-85db-86cbbfbee190 -->

```dart
void main() {
  final name = 'Ada';               // final = single assignment
  const pi = 3.14159;               // const = compile-time constant
  var count = 0;                    // inferred, mutable

  print('Hello, $name');            // interpolation
  print('Sum: ${1 + 2}');
}

String greet(String name, {String greeting = 'Hello', int? times}) =>
    '$greeting, $name';

greet('Ada', greeting: 'Hi');       // named arguments
```

**`final` vs `const`:** `final` is set once at runtime; `const` is known at compile time and canonicalised. **In Flutter, `const` constructors let the framework skip rebuilding a widget** — which is why `prefer_const_constructors` is a lint worth enabling → [[mobile/frameworks/flutter/index|Flutter]].

**Named parameters with `required`** are the Flutter idiom, and they're why widget constructors read the way they do.

## Where Dart is weaker
<!-- bite: 965cd98f-ee2f-49b1-ab68-3251375b20d3 -->

Being straight about it:

- **The ecosystem is small outside Flutter.** For anything non-UI you'll find fewer, less mature libraries than in Python, JS or the JVM world
- **No macros.** Code generation via `build_runner` fills the gap — `json_serializable`, `freezed` — and it's a build step that's slow and clunky compared to Kotlin's or Swift's compile-time generation. **This is Dart's most-felt weakness day to day.** Macros were long promised and the effort was shelved
- **Single-threaded per isolate.** No shared-memory threading → [[languages/10-dart/04-async-and-isolates|isolates]]
- **It's Google's**, and Google's track record with projects is a real consideration people weigh

## Key insight
<!-- bite: 9f7eb275-6090-4904-b5e2-2ff84fddc1e4 -->

**Dart is a deliberately unsurprising language whose one clever idea is shipping both a JIT and an AOT compiler** — which is what buys Flutter sub-second stateful hot reload in development and native performance in release. **Learn it for Flutter**; as a general-purpose language it has no argument against Kotlin, TypeScript or Go.

## Related
<!-- bite: c72893f8-6e95-4240-be1e-af62f5ca0323 -->
- [[languages/10-dart/index|the Dart course]]
- [[mobile/frameworks/flutter/index|Flutter]] — the reason this exists
- [[languages/index|languages]]
