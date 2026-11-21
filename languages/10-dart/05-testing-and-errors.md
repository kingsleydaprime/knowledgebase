---
id: dab803b2-ccf1-4d49-bd5d-fa4f328bec60
---

# Testing and Error Handling

## Exceptions — the loose part
<!-- bite: 1828d67f-b5a4-444c-acba-19942c7e2b7f -->

**Dart has no checked exceptions and no `throws` in the signature.** Any function may throw anything, and nothing tells you.

```dart
throw ArgumentError('id must not be empty');
throw StateError('not initialised');
throw FormatException('bad JSON');
throw MyCustomException('domain-specific');    // any object can be thrown
```

**`Error` vs `Exception` is a convention, not enforcement:**

- **`Error`** — a programming mistake. **Should not be caught.** `StateError`, `ArgumentError`, `RangeError`
- **`Exception`** — a recoverable condition. `FormatException`, `IOException`

**In practice the distinction is weakly observed**, including within the SDK. Treat it as documentation.

```dart
try {
  await risky();
} on FormatException catch (e) {
  handleBadData(e);
} on HttpException catch (e, stack) {
  log(e, stack);
} catch (e) {
  rethrow;                 // rethrow PRESERVES the original stack trace
} finally {
  cleanup();
}
```

**`rethrow`, not `throw e`.** The latter resets the stack trace and destroys your ability to debug it — this is a real and common mistake.

**Because nothing declares what throws, the discipline has to come from you:** document it in doc comments, and prefer returning a sealed result type for expected failures rather than throwing.

```dart
sealed class Result<T> {}
class Ok<T> extends Result<T> { final T value; Ok(this.value); }
class Err<T> extends Result<T> { final String message; Err(this.message); }
```

**`switch` over that is exhaustive**, which gives you something closer to Rust's or Swift's guarantees → [[languages/10-dart/02-types-and-null-safety|sealed classes]].

## Testing
<!-- bite: 04c19c98-4e93-45b5-a336-77cb2274d523 -->

```dart
import 'package:test/test.dart';

void main() {
  group('UserRepository', () {
    late FakeApi api;
    late UserRepository repo;

    setUp(() {
      api = FakeApi();
      repo = UserRepository(api);
    });

    test('caches the second call', () async {
      await repo.get('1');
      await repo.get('1');
      expect(api.callCount, 1);
    });

    test('throws on missing user', () {
      expect(() => repo.get('nope'), throwsA(isA<NotFoundException>()));
    });
  });
}
```

**Matchers** are expressive and worth knowing: `equals`, `isA<T>()`, `contains`, `throwsA`, `completion`, `isNull`, `predicate`, `orderedEquals`.

**Async testing:**

```dart
test('completes with a user', () {
  expect(repo.get('1'), completion(isA<User>()));
});

test('emits loading then success', () {
  expect(viewModel.stream, emitsInOrder([Loading(), isA<Success>()]));
});
```

**`fakeAsync`** (from `package:fake_async`) gives you a virtual clock so timers and delays complete instantly — the equivalent of Kotlin's `runTest`.

## Flutter testing
<!-- bite: b70ee4ac-3574-43ba-b538-b1a9c3748682 -->

Three tiers, and the cost curve matters:

```dart
// 1. Unit — pure logic. Fast. WHERE THE VALUE IS
test('discount is applied', () { ... });

// 2. Widget — a single widget, headless. Fast enough to run often
testWidgets('shows the count', (tester) async {
  await tester.pumpWidget(const MyApp());
  await tester.tap(find.byIcon(Icons.add));
  await tester.pump();
  expect(find.text('1'), findsOneWidget);
});

// 3. Integration — the real app on a device. Slow, flaky
```

**`pump()` advances one frame; `pumpAndSettle()` runs until no animation is pending** — and hangs forever on an infinite animation, which is a classic test timeout.

**Weight heavily toward unit and widget tests.** Integration tests are slow and brittle; keep them for critical flows only.

## Mocks and fakes
<!-- bite: 0187d6db-4197-40cb-86c3-8f7db9ba819e -->

**`mockito` needs code generation** in null-safe Dart (`@GenerateMocks` plus `build_runner`), which is friction. **`mocktail` needs none** and is the better default now.

**And prefer fakes to mocks** where you own the interface — a `FakeApi` backed by a map is more readable and doesn't break on refactor.

## Coverage and CI
<!-- bite: 4d620ed9-81b4-411b-b1d3-b2c0ac137976 -->

```bash
flutter test --coverage
dart analyze --fatal-infos
dart format --set-exit-if-changed .
```

**Run all three in CI.** `--fatal-infos` makes lint violations fail the build, which is the only way lints get fixed.

## Key insight
<!-- bite: ec2569b4-cfc1-493f-a051-1fdcfff147fc -->

**Dart's exception model gives you no compiler help at all** — nothing declares what throws, and `Error` vs `Exception` is convention. So for anything where failure is expected rather than exceptional, **a sealed result type gives you back the exhaustiveness the exception system doesn't provide** — and it's the single biggest reliability improvement available in Dart code.

## Related
<!-- bite: 9985ddee-b9b0-48b1-b03c-b6184975d63f -->
- [[languages/10-dart/02-types-and-null-safety|sealed classes]] — the Result pattern
- [[languages/10-dart/06-tooling-and-codegen|tooling]] — lints and build_runner
- [[mobile/frameworks/flutter/index|Flutter]] — widget testing

## About this lesson
<!-- bite: bdbfa31a-3221-492c-a065-5231795b9d2e -->

**Level:** Intermediate. **Covers:** the test framework, and Dart's unusually loose exception model.
