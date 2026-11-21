---
id: 224f84b2-2843-4abb-82d9-f1aaee54ec96
---

# Types and Null Safety

**[Beginner → Intermediate]** — sound null safety, and what "sound" actually buys you.

## Null safety
<!-- bite: 9fa3dff9-a9c3-4897-9bc9-f4673b7182b1 -->

```dart
String name = 'Ada';        // can never be null
String? maybe;              // may be null
int? age;

maybe.length;               // ❌ compile error
maybe?.length;              // ✅ null-aware — returns int?
maybe ?? 'default';         // ✅ default value
maybe!.length;              // ⚠️ assertion — THROWS if null
```

Same shape as [[languages/09-kotlin/02-null-safety|Kotlin]] and [[languages/08-swift/02-values-references-and-optionals|Swift]]. The distinguishing word is **sound**.

**Sound means the compiler's guarantee is total:** if a variable is typed `String`, it **cannot** be null at runtime — the compiler proves it, and can therefore optimise away null checks entirely.

**Contrast with Kotlin**, where platform types from Java can still be null despite the declared type. **Dart has no such hole** — because there's no Java to interoperate with. That's a real advantage of a smaller ecosystem.

## Flow analysis
<!-- bite: b8f75d2a-27e7-4ee6-9f7f-2a0c34b4ee15 -->

```dart
void greet(String? name) {
  if (name == null) return;
  print(name.length);        // no ! needed — the compiler PROMOTED it to String
}
```

**Promotion is automatic** after a null check, a `return`, a `throw`, or an assertion.

**Where promotion fails, and it's the common frustration:**

```dart
class User { String? name; }

void show(User u) {
  if (u.name != null) {
    print(u.name.length);    // ❌ won't promote — it's a FIELD, could change
  }
}

void show(User u) {
  final name = u.name;       // ✅ copy to a local
  if (name != null) print(name.length);
}
```

**Fields aren't promoted because another reference could mutate them between the check and the use.** Copy to a local `final` — the same workaround as Kotlin, for the same reason.

## `late`
<!-- bite: 7770afb4-8d7b-49a6-a3f1-7e5188343f01 -->

```dart
late final Database db;      // initialised later, but definitely before use

class Widget {
  late final controller = TextEditingController();   // lazily initialised
}
```

**`late` defers the null check to runtime** — reading before assignment throws `LateInitializationError`, which is at least a clearer message than a null dereference.

**`late final` with an initialiser is lazy** — computed on first access, once. Genuinely useful for expensive setup.

**Don't reach for `late` to silence the compiler.** It's for genuine "definitely assigned before use" cases (dependency injection, `initState`), not for avoiding a nullable type.

## The type system
<!-- bite: 009fe2cf-26db-4a97-acbb-166a356128c9 -->

```dart
dynamic x = 'anything';      // ALL type checking disabled. Avoid
Object? y = 'anything';      // any value, but you must check before using
var z = 'inferred';          // String, inferred
```

**`dynamic` turns off the type system** — errors move to runtime. **`Object?` is almost always what you actually want**: it accepts anything and still forces you to narrow before use.

**Common Dart types:** `int`, `double`, `num`, `String`, `bool`, `List<T>`, `Set<T>`, `Map<K,V>`, `Iterable<T>`, `Record`.

**Note `int` and `double` are distinct** and `num` is their supertype — unlike JavaScript, division always produces a `double`, and `~/` is integer division.

## Records and patterns (Dart 3)
<!-- bite: 4387de5b-3dbd-44dd-aa47-85c098f06f01 -->

```dart
(String, int) pair = ('Ada', 36);
({String name, int age}) named = (name: 'Ada', age: 36);

final (name, age) = pair;              // destructuring
print(named.name);
```

**Records give you multiple return values without declaring a class:**

```dart
(int sum, int count) analyse(List<int> xs) => (xs.reduce((a,b) => a+b), xs.length);
```

**Pattern matching:**

```dart
final result = switch (response) {
  Success(:final data) => 'Got ${data.length}',
  Failure(:final message) => 'Error: $message',
};
```

**`switch` as an expression, with destructuring** — and with sealed classes, it's exhaustive.

## Sealed classes
<!-- bite: b99948b0-30b4-475a-b24d-32b6631c4057 -->

```dart
sealed class UiState {}
class Loading extends UiState {}
class Success extends UiState { final List<Item> items; Success(this.items); }
class Failure extends UiState { final String message; Failure(this.message); }

final text = switch (state) {           // EXHAUSTIVE — no default needed
  Loading()          => 'Loading…',
  Success(:final items) => '${items.length} items',
  Failure(:final message) => message,
};
```

**Add a subclass and every non-exhaustive `switch` fails to compile.** Same payoff as Kotlin's sealed and Swift's enums → [[mobile/05-state-and-architecture|state modelling]].

**`freezed`** is the package that generates this plus `copyWith`, `==` and `hashCode` — **near-universal in real Flutter codebases**, because writing it by hand is tedious.

## Key insight
<!-- bite: 4e03d816-b4f2-4a2c-9b66-8a7b0a5bdc10 -->

**Dart's null safety is sound, with no escape hatch equivalent to Kotlin's platform types** — so the guarantee actually holds end to end, and the compiler can optimise on it. **Dart 3's records, patterns and sealed classes closed the gap** with Kotlin and Swift on data modelling; the remaining weakness is that you need `freezed` and a build step to get what those languages generate at compile time.

## Related
<!-- bite: 2d162995-0fbf-4f07-82aa-08f70df9e053 -->
- [[languages/10-dart/03-classes-and-collections|classes and collections]]
- [[languages/09-kotlin/02-null-safety|Kotlin's null safety]] — the comparison, including the hole Dart doesn't have
- [[mobile/frameworks/flutter/index|Flutter]]
