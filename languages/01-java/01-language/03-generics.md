# Generics

**Source:** **[reference — barely exercised]** — the projects used generic *collections* (`List<Transaction>`, `Map<String, SubscriptionRecord>`, `ConcurrentHashMap.newKeySet()`) constantly but never *authored* a generic type or method. This file covers the topic properly because it's fundamental and interview-critical; the collection usages are real, the authored-generics examples are illustrative.

## The problem generics solve

Before generics (Java 5), collections held `Object`, so everything came out untyped and needed casting — and a wrong cast blew up at runtime, not compile time:

```java
List list = new ArrayList();
list.add("hello");
String s = (String) list.get(0);   // manual cast, and nothing stops list.add(42)
```

Generics move that type check to **compile time**. `List<String>` means "a list of Strings," enforced by the compiler, with no casts and no runtime surprise:

```java
List<String> list = new ArrayList<>();   // <> = the diamond operator, type inferred from the left
list.add("hello");
String s = list.get(0);                   // no cast; list.add(42) won't compile
```

## Generic classes and methods

A **type parameter** (`<T>`) lets a class or method work over any type while staying type-safe. This is the whole reason one `ArrayList` implementation serves every element type:

```java
public class Box<T> {
    private T value;
    public void set(T value) { this.value = value; }
    public T get() { return value; }
}
Box<Transaction> box = new Box<>();   // T is Transaction here
```

A **generic method** declares its own type parameter before the return type — the compiler infers it from the arguments:

```java
public static <T> T firstOrNull(List<T> items) {
    return items.isEmpty() ? null : items.get(0);
}
String s = firstOrNull(List.of("a", "b"));   // T inferred as String
```

Convention: `T` (type), `E` (element), `K`/`V` (key/value), `R` (result).

## Bounded type parameters

`<T extends SomeType>` constrains `T` to a subtype, which unlocks that type's methods inside the generic code. `extends` here means "is a subtype of," and works for both classes and interfaces:

```java
public static <T extends Comparable<T>> T max(List<T> items) {
    T best = items.get(0);
    for (T item : items) if (item.compareTo(best) > 0) best = item;  // compareTo available because of the bound
    return best;
}
```

Without the bound, `T` is effectively `Object` and you couldn't call `compareTo`.

## Wildcards — `? extends` vs `? super`

Wildcards appear in method *parameters* to accept a family of parameterizations. The guiding rule is **PECS — Producer `extends`, Consumer `super`**:

```java
// Producer: you READ T out of it → use ? extends T
double sum(List<? extends Number> nums) {          // accepts List<Integer>, List<Double>, ...
    double total = 0;
    for (Number n : nums) total += n.doubleValue();  // reading is safe
    // nums.add(...) is NOT allowed — the compiler can't know the exact element type
    return total;
}

// Consumer: you WRITE T into it → use ? super T
void addInts(List<? super Integer> sink) {          // accepts List<Integer>, List<Number>, List<Object>
    sink.add(1);                                     // writing an Integer is safe
    // reading gives back Object — the exact type is unknown
}
```

Why the asymmetry: with `? extends Number` you know every element *is at least* a `Number` (safe to read as `Number`) but not the exact subtype (unsafe to add). With `? super Integer` you know the list *accepts at least* `Integer` (safe to add) but reading yields only `Object`. An **unbounded** `<?>` means "some unknown type" — read-only as `Object`, useful when the type genuinely doesn't matter (`List<?> anything`).

## Type erasure — what generics are *not*

Generics are a **compile-time** feature. The compiler checks types, then **erases** them — at runtime `List<String>` and `List<Integer>` are both just `List`. This has hard consequences worth knowing:

```java
List<String> a = new ArrayList<>();
List<Integer> b = new ArrayList<>();
a.getClass() == b.getClass();     // true — both are just ArrayList at runtime

// You cannot do any of these, because the type isn't there at runtime:
if (obj instanceof List<String>) { }   // compile error
T value = new T();                       // can't instantiate a type parameter
T[] array = new T[10];                   // can't create a generic array
```

Erasure is why generics add zero runtime cost (no specialized classes per type, unlike C++ templates) — but also why reflection can't recover the element type of a `List`, and why you occasionally pass a `Class<T>` token when a method genuinely needs the runtime type. It's the single most common "gotcha" source in Java generics, and a frequent interview question.

## Where this shows up in real code

Every collection is generic (`Map<String, SubscriptionRecord>`), every stream carries a type (`Stream<Transaction>`), and `Optional<T>`, `CompletableFuture<T>`, and `Comparable<T>` are all generic. You'll *read* generic signatures far more than you write them — the payoff of this file is being able to read `Map<String, ? extends List<Transaction>>` without flinching, and knowing why `list.add(x)` sometimes won't compile against a wildcard.

## Related
- [[languages/01-java/01-language/04-collections|Collections]] — the generics you use constantly
- [[languages/01-java/01-language/05-functional-programming|Functional Programming]] — `Function<T,R>`, `Predicate<T>`, and other generic functional interfaces
- [[languages/01-java/01-language/02-oop|OOP]] — `Comparable<T>` and the type bounds it enables
