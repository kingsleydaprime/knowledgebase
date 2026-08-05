# Object-Oriented Programming in Java

**Source:** **[reference]** — the projects used classes and interfaces heavily but never had the OOP model written up as its own topic. Examples below are drawn from the projects' actual types (`Store`/`InMemoryStore`, `SubscriptionRecord`) where genuine; the pillar-by-pillar framing follows [roadmap.sh Java](https://roadmap.sh/java).

## Classes and objects

A **class** is a blueprint; an **object** is a concrete instance of it. A class bundles **state** (fields/attributes) with **behavior** (methods) that operates on that state:

```java
public class Transaction {
    private String id;              // attribute (field)
    private BigDecimal amount;

    public Transaction(String id, BigDecimal amount) {   // constructor
        this.id = id;
        this.amount = amount;
    }

    public BigDecimal getAmount() { return amount; }     // method (behavior)
}

Transaction t = new Transaction("T1", new BigDecimal("34.02"));  // an object
```

`new` allocates the object on the heap and runs the constructor. `this` refers to the current object — needed here to disambiguate the field `id` from the parameter `id`. A class with no explicit constructor gets a no-arg default one; declare any constructor and the default disappears.

**Overloaded constructors** give a class several ways to be built — same name, different parameter lists (the general overloading rule below). One constructor can delegate to another with `this(...)` so the real initialization lives in a single place:

```java
public class Pizza {
    private String bread, sauce, cheese;

    public Pizza() {                                 // no-arg: sensible defaults
        this("Hand-tossed", "Marinara", "Mozzarella");
    }
    public Pizza(String bread, String sauce, String cheese) {   // full control
        this.bread = bread;
        this.sauce = sauce;
        this.cheese = cheese;
    }
}
new Pizza();                                    // uses the defaults
new Pizza("Thin", "Pesto", "Feta");             // fully specified
```

`this(...)` must be the first statement in the constructor, and is the beginner echo of `super(...)`, which calls the *parent's* constructor (see [Inheritance](#2-inheritance)).

## The four pillars

### 1. Encapsulation

Keep fields `private` and expose controlled access through methods. The point isn't ceremony — it's that the object controls its own invariants, and callers can't put it in an invalid state or depend on its internal representation:

```java
public class Account {
    private BigDecimal balance = BigDecimal.ZERO;
    public void deposit(BigDecimal amount) {
        if (amount.signum() <= 0) throw new IllegalArgumentException("must be positive");
        balance = balance.add(amount);   // the only way balance changes — the invariant is enforceable here
    }
    public BigDecimal getBalance() { return balance; }
}
```

If `balance` were public, every caller could set it to anything and the "never negative" rule would live nowhere.

### 2. Inheritance

A subclass `extends` a superclass, inheriting its fields and methods and optionally adding or overriding:

```java
public class Payment { protected BigDecimal amount; void process() { /* base logic */ } }
public class CardPayment extends Payment {
    private String cardNumber;
    @Override void process() { super.process(); /* card-specific */ }   // super calls the parent version
}
```

Java has **single inheritance** for classes (one `extends`) but a class can implement many interfaces. `super` reaches the parent: `super(...)` calls the parent constructor (must be the first line of the child constructor), and `super.method()` calls the parent's version of an overridden method.

Favor **composition over inheritance** — inheritance couples a subclass tightly to its parent's implementation, and a deep hierarchy is rigid; holding a collaborator as a field (composition) is usually more flexible. Reach for inheritance only for a genuine "is-a" relationship, not just to reuse code. The distinction is **is-a vs has-a**: a `Car` *is-a* Vehicle (inheritance), but a `Car` *has-a* Engine (composition) — the car is built *from* an engine object it holds as a field:

```java
class Engine { void start() { System.out.println("Vroom"); } }

class Car {
    private final Engine engine = new Engine();   // has-a: Car is composed of an Engine
    void drive() { engine.start(); }              // delegates to its part
}
```

### 3. Polymorphism

One reference type, many runtime behaviors. A variable typed as the supertype can hold any subtype, and a call dispatches to the actual object's version:

```java
Payment p = new CardPayment();
p.process();   // runs CardPayment.process() — decided at runtime by the object's real type
```

This is **dynamic (runtime) binding** — the JVM picks the method based on the object, not the reference type. It's what lets the payment sandbox's `Store store` field hold an `InMemoryStore` today and a `DatabaseStore` tomorrow with zero caller changes.

### 4. Abstraction

Expose *what* something does, hide *how*. Interfaces and abstract classes are the tools; the `Store` interface is pure abstraction — callers depend on the operations, never the map-vs-database implementation behind them.

## Interfaces vs abstract classes

An **interface** is a pure contract — historically no state and no implementation (Java 8+ allows `default` methods with bodies, but still no instance fields). A class `implements` it and must provide every abstract method or the build fails:

```java
public interface Store {
    void createSubscription(String id, SubscriptionRecord record);
    SubscriptionRecord getSubscription(String id);
    default boolean exists(String id) { return getSubscription(id) != null; }  // default method — optional to override
}

public class InMemoryStore implements Store {
    // must implement createSubscription and getSubscription, or won't compile
}
```

An **abstract class** sits in between: it *can* hold state and concrete methods, but can't be instantiated and may declare `abstract` methods subclasses must fill in.

| | Interface | Abstract class |
|---|---|---|
| Multiple inheritance | Yes — implement many | No — extend one |
| Instance fields / state | No | Yes |
| Constructor | No | Yes |
| Use when | Defining a capability/contract many unrelated types can offer | Sharing state + partial implementation among close relatives |

Default guidance: prefer interfaces (they keep types decoupled and composable); use an abstract class only when subclasses genuinely share state and near-identical code.

## Overloading vs overriding

- **Overloading** — same method name, different parameter lists, in the same class. Resolved at **compile time** by the argument types (*static binding*): `stmt.setString(1, x)` vs `stmt.setBigDecimal(2, y)`.
- **Overriding** — a subclass replaces an inherited method with the same signature. Resolved at **runtime** by the object's actual type (*dynamic binding*). Mark it `@Override` — not required, but the compiler then rejects a typo'd "override" that silently becomes a new method instead.

Static vs dynamic binding is exactly the overloading-vs-overriding distinction: overload resolution is fixed at compile time; override resolution is deferred to runtime.

## Nested classes

A class declared inside another. Four flavors, by use:

- **Static nested** — a helper that doesn't need the outer instance (`Map.Entry`).
- **Inner (non-static)** — holds an implicit reference to the enclosing object; can access its private fields.
- **Local** — declared inside a method.
- **Anonymous** — a one-shot implementation at the point of use, largely superseded by lambdas for single-method interfaces (see [[languages/01-java/01-language/05-functional-programming|Functional Programming]]).

## The equals / hashCode contract

`==` compares references; `.equals()` compares logical value. `Object`'s default `equals` *is* `==`, so value types must override it — and whenever you override `equals`, you **must** override `hashCode` to match, or hash-based collections break:

**The contract:** if `a.equals(b)` then `a.hashCode() == b.hashCode()`. (The reverse needn't hold — different objects may collide on the same hash.)

Break it and a `HashMap` can't find a key you definitely put in, because it looks in the bucket chosen by `hashCode()` and never gets to the `equals()` check:

```java
@Override public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Transaction t)) return false;   // pattern matching — see Modern Java
    return Objects.equals(id, t.id);
}
@Override public int hashCode() { return Objects.hash(id); }
```

This is exactly the boilerplate Lombok's `@Data` and Java `record`s generate for you ([[languages/01-java/03-tooling/03-lombok-and-builders|Lombok]], [[languages/01-java/01-language/07-modern-java|Modern Java]]) — but you have to understand the contract to know why a broken `equals` corrupts a map, and to spot it in code that hand-rolls one.

## toString — a readable object

`Object`'s default `toString()` returns something useless like `Transaction@1b6d3586` (class name + hex hash). Printing an object, or concatenating it into a string, calls `toString()` implicitly — so override it to return something readable:

```java
public class Car {
    private String make, model;
    private int year;
    // ... constructor ...
    @Override public String toString() {
        return year + " " + make + " " + model;   // 2024 Toyota Corolla
    }
}

Car car = new Car("Toyota", "Corolla", 2024);
System.out.println(car);   // System.out.println(car.toString()) — "2024 Toyota Corolla"
```

This is purely for a human-readable representation (logging, debugging) — distinct from `equals`/`hashCode`, which define *identity*. Records and Lombok's `@Data` generate `toString` for you ([[languages/01-java/01-language/07-modern-java|Modern Java]], [[languages/01-java/03-tooling/03-lombok-and-builders|Lombok]]).

## Arrays of objects

An array (or `ArrayList`) can hold object references just like it holds primitives — the natural way to manage a collection of the same type. Each slot is a reference, so a freshly-`new`ed object array starts full of `null` until you populate it:

```java
Car[] garage = new Car[3];                 // three nulls
garage[0] = new Car("Toyota", "Corolla", 2024);
garage[1] = new Car("Honda", "Civic", 2023);
garage[2] = new Car("Ford", "Focus", 2022);

for (Car c : garage) {
    System.out.println(c);                 // calls each car's toString()
}
```

This is the shape behind the beginner "quiz" and "library of books" projects — an array of custom objects walked with a for-each loop. For a resizable version, use `ArrayList<Car>` ([[languages/01-java/01-language/04-collections|Collections]]).

## Object lifecycle and initializer blocks

An object lives from `new` until it becomes unreachable, at which point it's eligible for garbage collection ([[languages/01-java/02-jvm-and-concurrency/01-jvm-internals|JVM Internals]]). Construction order: static initializers (once, at class load) → instance initializer blocks and field initializers (top to bottom) → constructor body. `finalize()` is deprecated and effectively dead — for cleanup, use try-with-resources / `AutoCloseable` ([[languages/01-java/01-language/06-exceptions|Exceptions]]), never a finalizer.

## enums

An enum is a class with a fixed set of instances, safer than string/int constants and free to validate against — Jackson maps a matching JSON string to the constant and rejects anything else:

```java
public enum FrequencyType { DAILY, WEEKLY, MONTHLY, YEARLY }
```

Because they're real classes, enums can carry fields and methods — useful as lookup tables:

```java
public enum Channel {
    MTN("233"), TELECEL("233"), CARD(null);
    private final String prefix;
    Channel(String prefix) { this.prefix = prefix; }
    public String prefix() { return prefix; }
}
```

## Related
- [[languages/01-java/01-language/01-fundamentals|Fundamentals]] — access modifiers, static vs instance
- [[languages/01-java/01-language/03-generics|Generics]] — parameterizing the types these classes hold
- [[languages/01-java/01-language/07-modern-java|Modern Java]] — records and sealed classes, the modern evolution of OOP modeling
- [[concepts/03-design-patterns/README|Design Patterns]] — OOP patterns applied
