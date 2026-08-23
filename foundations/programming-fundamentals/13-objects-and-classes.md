# Objects and Classes

> **[Beginner → Intermediate]** · Bundling data with the code that operates on it — the idea most languages are organised around, and the one this course deliberately left until last.

Everything so far has kept two things apart: **data** (variables, collections) and **behaviour** (functions). You pass data into functions and get data back.

That works, and it stops scaling at a specific point. Consider a bank account:

```python
balance = 0
account_number = "12345"
owner = "Ada"

def deposit(balance, amount):
    return balance + amount

def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
```

Three problems, and they get worse with every account you add:

1. **The data isn't held together.** Three loose variables that happen to relate. Two accounts means six variables, and nothing stops you passing one account's balance with another's number
2. **Nothing protects the invariant.** `balance = -500` is legal. The rule "balance may not go negative" lives in `withdraw`, and any other code can bypass it
3. **The connection is by convention only.** Nothing says `deposit` belongs to accounts

## The idea

**An object bundles data with the functions that operate on it.**

```python
class BankAccount:
    def __init__(self, owner, account_number):
        self.owner = owner
        self.account_number = account_number
        self.balance = 0

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
```

```python
ada = BankAccount("Ada", "12345")
ada.deposit(100)
ada.withdraw(30)
print(ada.balance)      # 70
```

The vocabulary, which is consistent across languages even when the syntax isn't:

- **Class** — the blueprint. `BankAccount` describes what every account has and can do
- **Object** / **instance** — an actual one, living in memory. `ada` is an object
- **Attribute** / **field** / **property** — the data an object holds (`balance`)
- **Method** — a function belonging to the object (`deposit`)
- **Constructor** — the method that sets up a new instance (`__init__`, `constructor`, `new`)
- **`self`** / **`this`** — inside a method, the object it was called on

**A class is a blueprint; an object is a building.** One class, many objects, each with its own data.

## Encapsulation

The first of the ideas that gives this its value: **hide the internals, expose a deliberate interface.**

`ada.balance` in Python is publicly reachable, and `ada.balance = 1_000_000` works. Most languages let you prevent that:

```java
public class BankAccount {
    private double balance;              // ← nothing outside can touch it

    public void deposit(double amount) { ... }
    public double getBalance() { return balance; }
}
```

Python signals it by convention (`_balance` means "internal, don't touch") rather than enforcing it — a real difference in philosophy, not a missing feature.

**Why it matters isn't secrecy — it's that you can change the inside without breaking the outside.** If `balance` becomes a computed sum of a transaction list, every caller of `deposit()` keeps working. Every caller of `account.balance` breaks.

**This is the same abstraction move as [[foundations/programming-fundamentals/08-functions|note 08]]**, applied to state as well as steps: a boundary, a promise about what's on the other side, and freedom to change what's behind it.

## Inheritance

A class can be defined as a **specialisation of another**:

```python
class SavingsAccount(BankAccount):
    def __init__(self, owner, account_number, rate):
        super().__init__(owner, account_number)     # run the parent's setup
        self.rate = rate

    def add_interest(self):
        self.balance += self.balance * self.rate
```

`SavingsAccount` gets `deposit` and `withdraw` for free, and adds its own. A subclass can also **override** a parent method to behave differently.

**Inheritance is the most over-used idea in this note**, and it's worth knowing that early. It looks like a code-reuse tool, and using it that way produces deep, brittle hierarchies where a change three levels up breaks something you've never read.

The test that matters is **"is-a", not "has-a"**. A savings account *is* a bank account — fine. A `Car` extending `Engine` because it needs the engine's methods is wrong: a car *has* an engine.

The mainstream advice, which is close to unanimous now: **prefer composition over inheritance.** Build objects out of other objects rather than inheriting from them.

```python
class Car:
    def __init__(self):
        self.engine = Engine()      # has-a: composition
```

Composition is more flexible, changeable at runtime, and doesn't couple you to someone else's hierarchy. → [[concepts/03-design-patterns/README|design patterns]] is largely a catalogue of composition techniques.

## Polymorphism

**Different objects responding to the same message in their own way.**

```python
for account in [current, savings, business]:
    account.apply_monthly_fee()      # each does its own thing
```

The calling code doesn't know or care which kind it has. Add a fourth account type and this loop is unchanged.

**This is the real payoff of the whole model**, and it's what people mean when they say OOP is about extensibility: behaviour is selected by the object rather than by a `switch` statement you have to find and edit every time a case is added.

Some languages get this from inheritance, some from **interfaces** (a contract of methods with no implementation), and dynamic languages from **duck typing** — if it has the method, it works, regardless of its class. *"If it walks like a duck…"*

## Where it stops being the answer

OOP is not the only way to organise code and is not always the best one. The honest criticisms:

**Not everything is an object.** Forcing procedural work into classes produces `DataManagerFactoryHelper` — classes that are just namespaces for functions, with the ceremony and none of the benefit.

**Mutable shared state is the hard part of software**, and objects are, by default, mutable shared state. An object passed to three places can be modified by all of them → [[foundations/programming-fundamentals/05-variables-and-types|note 05]]. This is precisely what makes concurrency difficult, and it's the core of the functional-programming argument.

**Deep hierarchies are genuinely bad.** Beyond two or three levels, working out what a method does means reading five files.

**The pendulum has swung.** Go has no inheritance. Rust has traits, not classes. Modern Java and C# lean hard on immutability and records. The useful position: **encapsulation and polymorphism have aged extremely well; deep inheritance has not.**

## What to actually take from this

- **Bundle data with the behaviour that maintains it.** Anything with invariants wants to be an object
- **Encapsulate** so the inside can change
- **Compose**, don't inherit, unless it's genuinely "is-a"
- **Use polymorphism** to avoid `switch` statements over types
- **Don't force it.** A function that transforms input to output should stay a function

## Related
- [[foundations/programming-fundamentals/14-programming-paradigms|programming paradigms]] — where OOP fits among the alternatives
- [[languages/01-java/01-language/02-oop|OOP in Java]] — the same ideas with enforcement and full syntax
- [[languages/05-cpp/03-classes-and-raii|classes and RAII in C++]] — objects tied to resource lifetime
- [[concepts/03-design-patterns/README|design patterns]] — the catalogue built on top of this
- [[concepts/04-best-practices/05-solid-principles|SOLID]] — five rules for not making the mess described above

*Source: [reference] — written Aug 2026 to close the gap this course's own README named as its biggest, prompted by a third source (`sources/100 CS concepts explained.md`) raising it independently.*
