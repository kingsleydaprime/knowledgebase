# Behavioural Patterns in Other Languages

> **[Intermediate]** · A companion to [[concepts/03-design-patterns/03-behavioral-patterns|behavioural patterns]], which teaches them in TypeScript. Several of these "patterns" are **built into some languages** — C#'s `event` is Observer, a generator is Iterator, a closure is Command — and Rust can turn State into **typestate**, where an illegal transition doesn't compile.

## Before you start

You can already:

- Explain observer, strategy, command, state and iterator, and model the order lifecycle as a transition table → [[concepts/03-design-patterns/03-behavioral-patterns|the main lesson]].
- Read code in at least one language below. Read §1 and your languages.

After this lesson you will be able to:

1. Recognise which behavioural patterns your language provides directly, so you don't hand-build them.
2. Write the order lifecycle with observers idiomatically in your language.
3. Explain typestate, and when it beats a runtime transition table.

## The kid version

Some board games come with a spinner, a timer and a scorepad in the box; with others you bring your own. The rules of play are the same either way. Languages are like that: in C#, the "tell everyone when something happens" pattern comes in the box as `event`; in C you build it from function pointers.

**Where the analogy stops working.** A spinner in the box is just convenient. A pattern built into a language often comes with checks the hand-built version can't have — like Rust making an illegal move impossible to write down at all.

## 1. Which patterns your language already has

| Pattern | Built in, or the idiom |
|---|---|
| **Observer** | C#: `event`. Go: channels, or a slice of funcs. Java: listener interfaces, `Flow`. Python, TypeScript: lists of callables, `EventEmitter`. Rust: closures in a `Vec`, or channels. C: function pointers. C++: `std::function`, Boost.Signals2 |
| **Strategy** | First-class functions everywhere — pass a function instead of a class. C: a function pointer |
| **Command** | A closure that captures its arguments; `Box<dyn FnOnce>` in Rust; a `Runnable` or lambda in Java |
| **State** | A transition table everywhere; an exhaustive `match` on an enum where the compiler checks it; **typestate** in Rust |
| **Iterator** | Python and C#: generators (`yield`). Go 1.23+: `iter.Seq` with range-over-func. Java: `Iterable`, streams. Rust: the `Iterator` trait. C++: `begin()`/`end()`, ranges. C: by hand |

**The practical rule:** in a language with first-class functions, Strategy and Command are rarely classes — a function *is* a one-method strategy. Reach for the class-based version only when the strategy needs several methods or its own state.

## Terms used in this lesson

1. **Generator**: This is a function that produces a sequence one item at a time with `yield`, pausing between items. It is Iterator written as a function.
2. **Typestate**: This is a design where each state of an object is a separate type, and each type only has the methods that are legal in that state.
3. **Event**: In C#, this is a language feature for Observer: a list of handlers that outside code can add to (`+=`) and only the owning class can invoke.
4. **Range-over-func**: In Go 1.23 and later, this lets `for x := range f` loop over a function that yields values — Go's iterator protocol.

## 2. Python

Listeners are plain callables in a list; a lambda is a full observer. The history is a **generator** — `yield` makes it an iterator with no class. A `match` statement over the `Status` enum is the closed alternative to the table.

```python
"""orders.py — State as a transition table, Observer as a list of callables,
Iterator as a generator."""
from enum import Enum
from typing import Callable, Iterator


class Status(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


TRANSITIONS: dict[Status, dict[str, Status]] = {
    Status.PENDING: {"pay": Status.PAID, "cancel": Status.CANCELLED},
    Status.PAID: {"ship": Status.SHIPPED, "cancel": Status.CANCELLED},
    Status.SHIPPED: {"deliver": Status.DELIVERED},
    Status.DELIVERED: {},
    Status.CANCELLED: {},
}


class IllegalTransition(Exception):
    pass


class Order:
    def __init__(self, order_id: str):
        self.id = order_id
        self.status = Status.PENDING
        self._listeners: list[Callable[[str, Status, Status], None]] = []
        self._history: list[Status] = [Status.PENDING]

    def on_change(self, listener: Callable[[str, Status, Status], None]) -> None:
        self._listeners.append(listener)

    def apply(self, action: str) -> None:
        nxt = TRANSITIONS[self.status].get(action)
        if nxt is None:
            raise IllegalTransition(f"cannot {action} an order that is {self.status.value}")
        before, self.status = self.status, nxt
        self._history.append(nxt)
        for listener in self._listeners:
            listener(self.id, before, nxt)

    def history(self) -> Iterator[str]:
        """Iterator: a generator yields one item at a time, without building a list."""
        for status in self._history:
            yield status.value
```

**Lab:** `labs/behavioral-patterns-python/` — checked with Python 3.14.

## 3. Go

Listeners are a slice of `func` values. Go 1.23's **range-over-func** gives Go a real iterator protocol: `History()` returns an `iter.Seq[Status]`, and callers write `for s := range order.History()`. For observers in *other goroutines*, the idiom is a **channel**: the order sends each change, and each subscriber receives from its own channel — at the cost of deciding what happens when a subscriber is slow.

```go
// Package orders: State as a transition table, Observer as a slice of funcs,
// Iterator as a range-over-func sequence (Go 1.23+).
package orders

import (
	"fmt"
	"iter"
)

type Status string

const (
	Pending   Status = "pending"
	Paid      Status = "paid"
	Shipped   Status = "shipped"
	Delivered Status = "delivered"
	Cancelled Status = "cancelled"
)

var transitions = map[Status]map[string]Status{
	Pending: {"pay": Paid, "cancel": Cancelled},
	Paid:    {"ship": Shipped, "cancel": Cancelled},
	Shipped: {"deliver": Delivered},
}

type Listener func(orderID string, from, to Status)

type Order struct {
	ID        string
	Status    Status
	listeners []Listener
	history   []Status
}

func New(id string) *Order { return &Order{ID: id, Status: Pending, history: []Status{Pending}} }

func (o *Order) OnChange(l Listener) { o.listeners = append(o.listeners, l) }

func (o *Order) Apply(action string) error {
	next, ok := transitions[o.Status][action]
	if !ok {
		return fmt.Errorf("cannot %s an order that is %s", action, o.Status)
	}
	from := o.Status
	o.Status = next
	o.history = append(o.history, next)
	for _, l := range o.listeners {
		l(o.ID, from, next)
	}
	return nil
}

// History is an iterator: callers write `for s := range order.History()`.
func (o *Order) History() iter.Seq[Status] {
	return func(yield func(Status) bool) {
		for _, s := range o.history {
			if !yield(s) {
				return
			}
		}
	}
}
```

**Lab:** `labs/behavioral-patterns-go/` — checked with Go 1.26.

## 4. Java

An `enum` and an **`EnumMap`** make a fast, readable transition table; `Consumer<Change>` listeners are lambdas. Implementing `Iterable` makes the order work in a for-each loop. For the closed version, a sealed interface of state records with an exhaustive `switch` (see [[concepts/04-best-practices/05b-solid-in-other-languages|SOLID in other languages]]).

```java
package orders;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

// State: an enum and an EnumMap transition table. Observer: Consumer listeners.
public final class Order implements Iterable<Order.Status> {
    public enum Status { PENDING, PAID, SHIPPED, DELIVERED, CANCELLED }
    public record Change(String orderId, Status from, Status to) {}

    private static final Map<Status, Map<String, Status>> TRANSITIONS = new EnumMap<>(Map.of(
        Status.PENDING, Map.of("pay", Status.PAID, "cancel", Status.CANCELLED),
        Status.PAID, Map.of("ship", Status.SHIPPED, "cancel", Status.CANCELLED),
        Status.SHIPPED, Map.of("deliver", Status.DELIVERED),
        Status.DELIVERED, Map.of(),
        Status.CANCELLED, Map.of()));

    public final String id;
    private Status status = Status.PENDING;
    private final List<Consumer<Change>> listeners = new ArrayList<>();
    private final List<Status> history = new ArrayList<>(List.of(Status.PENDING));

    public Order(String id) { this.id = id; }
    public Status status() { return status; }
    public void onChange(Consumer<Change> listener) { listeners.add(listener); }

    public void apply(String action) {
        Status next = TRANSITIONS.get(status).get(action);
        if (next == null) throw new IllegalStateException("cannot " + action + " an order that is " + status);
        Change change = new Change(id, status, next);
        status = next;
        history.add(next);
        listeners.forEach(l -> l.accept(change));
    }

    // Iterator: implementing Iterable lets callers use for-each.
    @Override public java.util.Iterator<Status> iterator() { return List.copyOf(history).iterator(); }
}
```

**Lab:** `labs/behavioral-patterns-java/` — checked with Java 21.

## 5. Rust — typestate

Rust can do the table version, but its distinctive answer is **typestate**. `Order<Pending>`, `Order<Paid>` and `Order<Shipped>` are different types, and only `Order<Pending>` and `Order<Paid>` have a `cancel` method. Each transition **consumes** the old value (`self`, not `&self`), so a stale `Order<Paid>` can't be used after it has shipped.

```rust
//! Typestate: each state is its own type, and each type only has the methods that state allows.
//! An illegal transition isn't rejected at runtime — it doesn't compile.
use std::marker::PhantomData;

pub struct Pending;
pub struct Paid;
pub struct Shipped;
pub struct Delivered;
pub struct Cancelled;

/// Observer: listeners registered by the composition root, called after each transition.
pub type Listener = Box<dyn Fn(&str, &str, &str)>;

pub struct Order<S> {
    pub id: String,
    listeners: Vec<Listener>,
    state: PhantomData<S>,
}

impl<S> Order<S> {
    // Moves the order into its next state, telling every listener. `self` is consumed,
    // so the old-state value can't be used again.
    fn to<T>(self, from: &str, to: &str) -> Order<T> {
        for listener in &self.listeners {
            listener(&self.id, from, to);
        }
        Order {
            id: self.id,
            listeners: self.listeners,
            state: PhantomData,
        }
    }
}

impl Order<Pending> {
    pub fn new(id: &str, listeners: Vec<Listener>) -> Self {
        Order {
            id: id.into(),
            listeners,
            state: PhantomData,
        }
    }
    pub fn pay(self) -> Order<Paid> {
        self.to("pending", "paid")
    }
    pub fn cancel(self) -> Order<Cancelled> {
        self.to("pending", "cancelled")
    }
}

impl Order<Paid> {
    pub fn ship(self) -> Order<Shipped> {
        self.to("paid", "shipped")
    }
    pub fn cancel(self) -> Order<Cancelled> {
        self.to("paid", "cancelled")
    }
}

impl Order<Shipped> {
    pub fn deliver(self) -> Order<Delivered> {
        self.to("shipped", "delivered")
    }
    // No `cancel` here: a shipped order has no way to be cancelled.
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;
    use std::rc::Rc;

    #[test]
    fn happy_path_with_an_observer() {
        let audit = Rc::new(RefCell::new(Vec::new()));
        let log = Rc::clone(&audit);
        let listener: Listener =
            Box::new(move |_, from, to| log.borrow_mut().push(format!("{from}->{to}")));

        let _delivered = Order::new("o1", vec![listener]).pay().ship().deliver();
        assert_eq!(
            *audit.borrow(),
            ["pending->paid", "paid->shipped", "shipped->delivered"]
        );
    }
}
```

```sh
#!/bin/sh
# Try to cancel a shipped order. With typestate, the method doesn't exist: E0599.
set -eu
export LC_ALL=C
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp -r Cargo.toml src "$work/"
cat >> "$work/src/lib.rs" <<'RS'

pub fn cancel_after_shipping() {
    let _ = Order::new("o2", vec![]).pay().ship().cancel();
}
RS
if (cd "$work" && cargo build --quiet 2>"$work/err.txt"); then echo "FAIL: cancelled a shipped order"; exit 1; fi
grep -q "error\[E0599\]: no method named \`cancel\` found for struct \`Order<Shipped>\`" "$work/err.txt" || { cat "$work/err.txt"; exit 1; }
echo "ok: rustc refused to cancel a shipped order (E0599)"
```

**Lab:** `labs/behavioral-patterns-rust/` — cancelling a shipped order fails with ``error[E0599]: no method named `cancel` found for struct `Order<Shipped>` ``. Checked with Rust 1.96.

**When typestate fits:** the state is known while the code is written — a builder that must be configured before `build()`, a connection that must be opened before use. **When it doesn't:** orders loaded from a database, whose state is only known at runtime. For those, an enum with an exhaustive `match`, or the table, is the right tool.

## 6. C

The transition table is a **2D array** indexed by state and action, with designated initialisers making it readable. Observers are function pointers with a context pointer — the same shape as the dependency-injection companion's interfaces.

```c
/* orders.c — State as a 2D transition table; Observer as an array of function pointers. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef enum { PENDING, PAID, SHIPPED, DELIVERED, CANCELLED, STATUS_COUNT } status;
typedef enum { PAY, SHIP, DELIVER, CANCEL, ACTION_COUNT } action;
#define NONE (-1)

/* transitions[from][action] = to, or NONE if not allowed */
static const int transitions[STATUS_COUNT][ACTION_COUNT] = {
    [PENDING] = {[PAY] = PAID, [SHIP] = NONE, [DELIVER] = NONE, [CANCEL] = CANCELLED},
    [PAID] = {[PAY] = NONE, [SHIP] = SHIPPED, [DELIVER] = NONE, [CANCEL] = CANCELLED},
    [SHIPPED] = {[PAY] = NONE, [SHIP] = NONE, [DELIVER] = DELIVERED, [CANCEL] = NONE},
    [DELIVERED] = {NONE, NONE, NONE, NONE},
    [CANCELLED] = {NONE, NONE, NONE, NONE},
};

typedef void (*listener)(void *ctx, status from, status to);

typedef struct {
    status current;
    struct { listener fn; void *ctx; } listeners[4];
    int listener_count;
} order;

static void on_change(order *o, listener fn, void *ctx) {
    o->listeners[o->listener_count].fn = fn;
    o->listeners[o->listener_count++].ctx = ctx;
}

/* Returns 0 on success, -1 for an illegal transition (and tells no one). */
static int apply(order *o, action a) {
    int next = transitions[o->current][a];
    if (next == NONE) return -1;
    status from = o->current;
    o->current = (status)next;
    for (int i = 0; i < o->listener_count; i++) o->listeners[i].fn(o->listeners[i].ctx, from, o->current);
    return 0;
}

static void count_changes(void *ctx, status from, status to) { (void)from; (void)to; ++*(int *)ctx; }

int main(void) {
    int changes = 0;
    order o = {.current = PENDING};
    on_change(&o, count_changes, &changes);
    assert(apply(&o, PAY) == 0 && apply(&o, SHIP) == 0);
    assert(apply(&o, CANCEL) == -1 && o.current == SHIPPED && changes == 2);
    assert(apply(&o, DELIVER) == 0 && o.current == DELIVERED && changes == 3);
    puts("ok: transition table and function-pointer listeners");
    return 0;
}
```

**Lab:** `labs/behavioral-patterns-c/` — checked with GCC 16.

## 7. C++

An `enum class`, a `std::map` table, `std::function` listeners, and `begin()`/`end()` so range-for walks the history. For the closed version, `std::variant` states with `std::visit`. Libraries such as Boost.Signals2 provide observers with automatic disconnection when a listener is destroyed — the part hand-rolled observer lists usually get wrong.

```cpp
// orders.cpp — State as a std::map table; Observer as std::function listeners;
// Iterator via begin()/end(), so range-for works.
#include <cassert>
#include <functional>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

enum class Status { Pending, Paid, Shipped, Delivered, Cancelled };

class Order {
public:
    using Listener = std::function<void(Status from, Status to)>;

    void on_change(Listener l) { listeners_.push_back(std::move(l)); }

    void apply(const std::string& action) {
        static const std::map<Status, std::map<std::string, Status>> transitions{
            {Status::Pending, {{"pay", Status::Paid}, {"cancel", Status::Cancelled}}},
            {Status::Paid, {{"ship", Status::Shipped}, {"cancel", Status::Cancelled}}},
            {Status::Shipped, {{"deliver", Status::Delivered}}},
        };
        auto state = transitions.find(status_);
        if (state == transitions.end() || !state->second.contains(action))
            throw std::logic_error("cannot " + action + " from this state");
        const Status from = status_;
        status_ = state->second.at(action);
        history_.push_back(status_);
        for (const auto& l : listeners_) l(from, status_);
    }

    Status status() const { return status_; }
    auto begin() const { return history_.begin(); }
    auto end() const { return history_.end(); }

private:
    Status status_ = Status::Pending;
    std::vector<Listener> listeners_;
    std::vector<Status> history_{Status::Pending};
};

int main() {
    int changes = 0;
    Order order;
    order.on_change([&](Status, Status) { ++changes; });
    for (const char* a : {"pay", "ship"}) order.apply(a);

    bool rejected = false;
    try { order.apply("cancel"); } catch (const std::logic_error&) { rejected = true; }
    assert(rejected && order.status() == Status::Shipped && changes == 2);

    int steps = 0;
    for (Status s : order) { (void)s; ++steps; }
    assert(steps == 3);
    std::cout << "ok: table, std::function listeners and range-for history\n";
}
```

**Lab:** `labs/behavioral-patterns-cpp/` — checked with GCC 16.

## 8. C#

Two patterns are language features. **`event EventHandler<Change>`** is Observer: outside code can only subscribe (`+=`) and unsubscribe (`-=`), and only `Order` can raise it. **`yield return`** is Iterator: `History()` is lazy and needs no iterator class.

```csharp
// C# has Observer in the language (`event`) and Iterator in the language (`yield return`).
var audit = new List<string>();
var order = new Order("o1");
order.Changed += (_, change) => audit.Add($"{change.From}->{change.To}");   // subscribe
foreach (var action in new[] { "pay", "ship", "deliver" }) order.Apply(action);

Check(audit.SequenceEqual(["Pending->Paid", "Paid->Shipped", "Shipped->Delivered"]), "listeners heard every change");
Check(order.History().Count() == 4, "history iterates lazily");

var shipped = new Order("o2");
shipped.Apply("pay"); shipped.Apply("ship");
try { shipped.Apply("cancel"); Check(false, "cancelled a shipped order"); }
catch (InvalidOperationException) { Check(shipped.Status == Status.Shipped, "status unchanged"); }
Console.WriteLine("ok: event, transition table and yield return");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }

enum Status { Pending, Paid, Shipped, Delivered, Cancelled }
record Change(string OrderId, Status From, Status To);

sealed class Order(string id)
{
    private static readonly Dictionary<Status, Dictionary<string, Status>> Transitions = new()
    {
        [Status.Pending] = new() { ["pay"] = Status.Paid, ["cancel"] = Status.Cancelled },
        [Status.Paid] = new() { ["ship"] = Status.Shipped, ["cancel"] = Status.Cancelled },
        [Status.Shipped] = new() { ["deliver"] = Status.Delivered },
    };

    private readonly List<Status> _history = [Status.Pending];
    public Status Status { get; private set; } = Status.Pending;

    public event EventHandler<Change>? Changed;   // Observer, built into the language

    public void Apply(string action)
    {
        if (!Transitions.TryGetValue(Status, out var allowed) || !allowed.TryGetValue(action, out var next))
            throw new InvalidOperationException($"cannot {action} an order that is {Status}");
        var change = new Change(id, Status, next);
        Status = next;
        _history.Add(next);
        Changed?.Invoke(this, change);
    }

    public IEnumerable<Status> History()           // Iterator, built into the language
    {
        foreach (var s in _history) yield return s;
    }
}
```

**Lab:** `labs/behavioral-patterns-csharp/` — runs in the .NET 10 SDK container. One `event` caveat: a subscriber that's never unsubscribed is kept alive by the publisher — a common source of memory leaks in long-running apps.

## Check your understanding

1. In which two languages is Observer a language or library feature you'd use directly, rather than a list you build?
2. Why is Strategy rarely a class in languages with first-class functions?
3. What does Rust's typestate turn from a runtime error into a compile error, and why can't it work for orders loaded from a database?
4. What's Go's iterator protocol since 1.23?
5. What memory problem do C# events cause if subscribers forget to unsubscribe?

<details>
<summary>Answers — after your attempt</summary>

1. C# (`event`) and Go (channels) are the clearest; Java's `Flow` and C++'s Boost.Signals2 are library versions.
2. A strategy with one method is just a function. Passing the function says the same thing with no class, no interface and no instantiation.
3. An illegal transition — the method doesn't exist on that state's type. A database order's state is only known at runtime, so the compiler can't know its type.
4. Range-over-func: a function of type `iter.Seq[T]` that calls `yield` per item, looped over with `for x := range seq`.
5. The publisher holds a reference to each handler, so subscribers stay reachable and are never garbage-collected — a leak in long-running applications.

</details>

## Practice — independent task

**In your second language:** add a `refund` action and a `refunded` state to the lab's order, plus a listener that records how long the order spent in each state, using an injected clock.

**Done when:** the new transition is tested, the illegal ones still are, and the timing listener's test doesn't read the real clock. In Rust, do it with typestate, so `refund` exists only on `Order<Delivered>`.

## Before moving on

You know which behavioural patterns your language provides, and you can write the order lifecycle idiomatically in it.

**Recap.** C# has `event` and `yield`; Python has generators; Go has channels and range-over-func; Rust has typestate, which makes illegal transitions uncompilable when states are known at compile time. Strategy and Command are usually just functions. The transition table works everywhere.

**Next.** Back to the course: [[concepts/03-design-patterns/02-structural-patterns|structural patterns]].

## Related
- [[concepts/03-design-patterns/03-behavioral-patterns|Behavioural patterns]] — the main lesson
- [[concepts/04-best-practices/05b-solid-in-other-languages|SOLID in other languages]] — open vs closed, and exhaustive matching
