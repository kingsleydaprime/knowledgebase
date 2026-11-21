---
id: 5d8c4a5f-e008-45c4-9c54-909c0c9a6169
---

# Classes and Collections

## Classes
<!-- bite: ea24dd8e-1162-46e8-8b4f-c07dfc09a11e -->

```dart
class User {
  final String id;
  final String name;
  int age;

  User({required this.id, required this.name, this.age = 0});   // the Flutter idiom

  User.anonymous() : id = '0', name = 'Anonymous';              // named constructor

  const User.empty() : id = '', name = '', age = 0;             // CONST constructor

  String get display => name.isEmpty ? 'Anonymous' : name;      // getter

  @override
  String toString() => 'User($id, $name)';
}
```

**Named parameters with `required` are the dominant style**, because it's what Flutter's widget constructors use — and with a dozen optional parameters, positional arguments would be unreadable.

**`const` constructors matter more than they look.** A `const` widget is canonicalised and **Flutter can skip rebuilding it entirely**. Turn on `prefer_const_constructors` — it's a free performance win → [[mobile/frameworks/flutter/index|Flutter]].

**`this.field` in the constructor parameter list** assigns directly — no body needed.

## Everything is an object
<!-- bite: 0cc892af-4985-4f96-9334-a20bd60bad71 -->

`int`, `bool`, functions and `null` are all objects. **There are no primitives** and no `static` classes — a top-level function is fine and idiomatic.

## Mixins
<!-- bite: 21ae1308-9ad2-46fd-a229-c8a992fece77 -->

Dart's answer to multiple inheritance:

```dart
mixin Loggable {
  void log(String m) => print('[$runtimeType] $m');
}

mixin Cacheable on Repository {       // only usable on Repository subclasses
  final _cache = <String, Object>{};
}

class UserRepo extends Repository with Loggable, Cacheable { }
```

**`with` composes behaviour without a hierarchy.** The `on` clause constrains where a mixin can be applied, so it can safely call the base type's members.

**Order matters** — later mixins override earlier ones.

## `abstract` and `implements`
<!-- bite: d18d0a4a-0296-4223-8859-cde41dd9a320 -->

```dart
abstract class Repository {
  Future<User?> get(String id);
  bool exists(String id) => true;      // may have implementations
}

class FakeRepo implements Repository {  // implements = interface only, no inheritance
  @override Future<User?> get(String id) async => null;
  @override bool exists(String id) => false;    // MUST implement everything
}
```

**Every class implicitly defines an interface**, so you can `implements` any class — which is genuinely handy for test fakes without declaring a separate interface.

**`extends` inherits implementation; `implements` requires you to provide all of it.**

**Dart 3 added `sealed`, `final`, `base` and `interface` modifiers** for controlling this precisely — `sealed` is the one you'll use → [[languages/10-dart/02-types-and-null-safety|sealed classes]].

## Collections
<!-- bite: e8c848dd-43d2-4412-b7b7-2e8939f13241 -->

```dart
final list = <String>['a', 'b'];
final set  = <int>{1, 2, 3};
final map  = <String, int>{'a': 1};

final names   = users.map((u) => u.name).toList();      // .toList() — map is LAZY
final adults  = users.where((u) => u.age >= 18).toList();
final total   = prices.fold<int>(0, (sum, p) => sum + p);
final first   = users.firstWhere((u) => u.isAdmin, orElse: () => User.anonymous());
final any     = users.any((u) => u.isAdmin);
final sorted  = [...users]..sort((a, b) => a.age.compareTo(b.age));
```

**`map` and `where` return a lazy `Iterable`, not a `List`.** Forgetting `.toList()` is the classic Dart mistake — the operation silently doesn't materialise, or re-evaluates every time you iterate.

**`firstWhere` throws if nothing matches** unless you pass `orElse`. Use `firstWhereOrNull` from `package:collection` instead — it returns null, which is almost always what you meant.

**The cascade `..`** returns the receiver, so you can chain mutations:

```dart
final list = [...users]..sort()..removeWhere((u) => !u.isActive);
```

## Collection literals with control flow
<!-- bite: d368db56-bdb4-445e-94cd-56c312db187a -->

Unusual and heavily used in Flutter:

```dart
final widgets = [
  const Header(),
  if (isLoggedIn) const ProfileTile(),          // conditional element
  for (final item in items) ItemTile(item),     // loop inside a literal
  ...extraWidgets,                              // spread
  ...?maybeNullList,                            // null-aware spread
];
```

**This is why Flutter widget trees don't need helper functions** for conditional children — it's the single most distinctive piece of Dart syntax, and it reads well once you've seen it.

## `package:collection`
<!-- bite: ab7a57dc-d775-4594-9c3f-273851537fc0 -->

The standard library is thin. **Add `collection` immediately** — it provides `firstWhereOrNull`, `groupBy`, `sortedBy`, `equals` for deep comparison, and much of what Kotlin has built in.

```dart
final byCity = groupBy(users, (User u) => u.city);
```

## Equality
<!-- bite: c515b53f-ae6d-4f21-a9be-0e30869db200 -->

**Dart's `==` is identity by default** — two `User` objects with identical fields are not equal unless you override `==` and `hashCode`.

**Nobody writes those by hand.** Use **`freezed`** (code generation) or **`equatable`**. This is the most-felt consequence of Dart lacking `data class` → [[languages/10-dart/06-tooling-and-codegen|code generation]].

## Key insight
<!-- bite: 46e2eb30-ad44-4a8c-ae57-878ee0408732 -->

**Dart's object model is conventional; what's distinctive is the collection syntax** — lazy `Iterable`s that need `.toList()`, cascades, and control flow inside literals. That last one is why Flutter's declarative widget trees read cleanly, and it's the piece of Dart most worth internalising early.

## Related
<!-- bite: 905df4d5-2206-4945-b121-6170ca2ee06e -->
- [[languages/10-dart/02-types-and-null-safety|types and null safety]]
- [[languages/10-dart/06-tooling-and-codegen|codegen]] — `freezed`, and why you need it
- [[mobile/frameworks/flutter/index|Flutter]] — where the collection syntax pays off

## About this lesson
<!-- bite: 79e63167-989b-481f-907d-22177ad9162c -->

**Level:** Intermediate. **Covers:** the object model, and the collection idioms Flutter code is built from.
