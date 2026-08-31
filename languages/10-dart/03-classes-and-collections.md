# Classes and Collections

**[Intermediate]** — the object model, and the collection idioms Flutter code is built from.

## Classes

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

**`const` constructors matter more than they look.** A `const` widget is canonicalised and **Flutter can skip rebuilding it entirely**. Turn on `prefer_const_constructors` — it's a free performance win → [[mobile/frameworks/flutter/README|Flutter]].

**`this.field` in the constructor parameter list** assigns directly — no body needed.

## Everything is an object

`int`, `bool`, functions and `null` are all objects. **There are no primitives** and no `static` classes — a top-level function is fine and idiomatic.

## Mixins

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

The standard library is thin. **Add `collection` immediately** — it provides `firstWhereOrNull`, `groupBy`, `sortedBy`, `equals` for deep comparison, and much of what Kotlin has built in.

```dart
final byCity = groupBy(users, (User u) => u.city);
```

## Equality

**Dart's `==` is identity by default** — two `User` objects with identical fields are not equal unless you override `==` and `hashCode`.

**Nobody writes those by hand.** Use **`freezed`** (code generation) or **`equatable`**. This is the most-felt consequence of Dart lacking `data class` → [[languages/10-dart/06-tooling-and-codegen|code generation]].

## Key insight

**Dart's object model is conventional; what's distinctive is the collection syntax** — lazy `Iterable`s that need `.toList()`, cascades, and control flow inside literals. That last one is why Flutter's declarative widget trees read cleanly, and it's the piece of Dart most worth internalising early.

## Related
- [[languages/10-dart/02-types-and-null-safety|types and null safety]]
- [[languages/10-dart/06-tooling-and-codegen|codegen]] — `freezed`, and why you need it
- [[mobile/frameworks/flutter/README|Flutter]] — where the collection syntax pays off
