# Tooling and Code Generation

**[Intermediate]** — `build_runner`, the packages everyone uses, and Dart's most-felt weakness.

## Why code generation is unavoidable

**Dart has no macros and no compile-time metaprogramming.** So the things Kotlin and Swift generate for free — `==`, `hashCode`, `copyWith`, JSON serialisation — require **a separate build step.**

```bash
dart run build_runner build --delete-conflicting-outputs
dart run build_runner watch                          # regenerate on save
```

**This is Dart's most-felt weakness day to day:** it's slow on a large project, the generated `.g.dart` and `.freezed.dart` files clutter the tree, and forgetting to re-run it produces confusing errors. **Macros were long promised and the effort was shelved**, so this is the status quo.

## `freezed` — near-universal in real Flutter code

```dart
@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    @Default(0) int age,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

**Generates `copyWith`, `==`, `hashCode`, `toString` and JSON — everything Kotlin's `data class` gives you built in.**

And sealed unions, which is the other half of its value:

```dart
@freezed
sealed class UiState with _$UiState {
  const factory UiState.loading() = Loading;
  const factory UiState.success(List<Item> items) = Success;
  const factory UiState.error(String message) = Failure;
}

final text = switch (state) {
  Loading() => 'Loading…',
  Success(:final items) => '${items.length} items',
  Failure(:final message) => message,
};
```

**Exhaustive, with `copyWith`, in a few lines.** This is why nearly every serious Flutter codebase uses it.

## `json_serializable`

```dart
@JsonSerializable(fieldRename: FieldRename.snake)
class User {
  final String id;
  final String displayName;      // ← maps to display_name
  User({required this.id, required this.displayName});

  factory User.fromJson(Map<String, dynamic> j) => _$UserFromJson(j);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

**Unknown JSON keys are ignored by default**, which is the safe behaviour for a mobile app whose old versions live for years → [[mobile/08-networking-on-mobile|API compatibility]].

**For unknown enum values:**

```dart
enum Status {
  active, closed,
  @JsonValue('unknown') unknown,
}
// @JsonKey(unknownEnumValue: Status.unknown) on the field
```

**Do this for every server-controlled enum** — otherwise a new server value fails the whole parse.

## Lints

`analysis_options.yaml`:

```yaml
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    - prefer_const_constructors        # REAL performance win in Flutter
    - unawaited_futures                # catches silently swallowed errors
    - avoid_print
    - prefer_final_locals

analyzer:
  errors:
    invalid_annotation_target: ignore
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
```

**`prefer_const_constructors` and `unawaited_futures` are the two that catch real problems.** The first is free performance; the second catches errors vanishing into unobserved Futures → [[languages/10-dart/04-async-and-isolates|async]].

**`very_good_analysis`** is a stricter ruleset worth considering. **Excluding generated files is essential** or you'll drown in warnings you can't fix.

## The packages you'll actually use

| | |
|---|---|
| **freezed** | Data classes and unions. **Effectively mandatory** |
| **json_serializable** | JSON |
| **collection** | `firstWhereOrNull`, `groupBy` — **add it immediately** |
| **dio** or **http** | Networking |
| **riverpod** / **bloc** / **provider** | State management → [[mobile/frameworks/flutter/README\|Flutter]] |
| **get_it** / **injectable** | Dependency injection |
| **drift** / **isar** / **sqflite** | Local database → [[mobile/07-data-and-offline-first\|offline-first]] |
| **mocktail** | Mocking, **no codegen needed** |
| **intl** | Localisation and formatting |

**Check pub.dev scores and last-updated before depending on anything.** The ecosystem is smaller than JS or the JVM, and **abandoned packages are a genuine risk** — a dead plugin blocking a Flutter upgrade is a real situation teams end up in.

## Versioning and upgrades

```yaml
environment:
  sdk: ^3.5.0
dependencies:
  http: ^1.2.0        # ^ = compatible within the major version
```

```bash
dart pub outdated
dart pub upgrade --major-versions
```

**Commit `pubspec.lock` for applications; don't for libraries.** Same rule as most ecosystems.

## Key insight

**Code generation is the tax Dart pays for having no macros**, and it's the thing that most makes the language feel less polished than Kotlin or Swift. **The correct response is to accept it and set it up properly** — `freezed`, `json_serializable`, `build_runner watch`, and generated files excluded from analysis. Fighting it by hand-writing `==` and `copyWith` is worse.

## Related
- [[languages/10-dart/03-classes-and-collections|classes]] — what `freezed` generates
- [[languages/10-dart/05-testing-and-errors|testing]] — mocktail vs mockito
- [[mobile/frameworks/flutter/README|Flutter]] — where all of this is used
