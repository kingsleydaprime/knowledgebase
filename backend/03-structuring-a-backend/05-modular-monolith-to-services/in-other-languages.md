# The Modular Monolith in Other Languages

> **[Intermediate→Advanced]** · A companion to [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|modular monolith to services]], whose lab shows a broker's at-least-once delivery crediting a customer twice. The lesson is the same in every language: **modules talk through events, and every consumer is idempotent.** What differs is the event plumbing each ecosystem reaches for, and how modules are kept apart.

## Before you start

You can already:

- Explain the modular-monolith rules — published APIs, no shared tables, events between modules — and why a broker forces idempotent consumers → [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Name your ecosystem's in-process event mechanism and its usual broker client.
2. Write an idempotent consumer idiomatically, using your language's "add to a set and tell me if it was new" operation.
3. Say which tool keeps modules apart in your language.

## The kid version

A school with houses — red, blue, green — runs as one school but each house keeps its own register. When the office announces "sports day moved to Friday", every house hears it and updates its own plans; nobody walks into another house's room to change their register. Some schools announce over a speaker (**an in-process bus**), some by letters that might arrive twice (**a broker**). Either way, a house that's already moved sports day doesn't move it again.

**Where the analogy stops working.** A person notices a repeated announcement. Code doesn't, unless it keeps a list of announcements it has already handled — that list is the idempotent consumer.

## 1. The plumbing, by ecosystem

| Language | In-process events | Usual broker client | Keeping modules apart |
|---|---|---|---|
| TypeScript | `EventEmitter`, NestJS `EventEmitter2` | BullMQ, `amqplib`, KafkaJS | ESLint `no-restricted-paths` |
| Python | a list of callables, `blinker` | Celery, `aio-pika`, `confluent-kafka` | import-linter |
| Go | a slice of funcs; **channels** | `amqp091-go`, `franz-go` | `internal/` packages |
| Java | Spring `ApplicationEventPublisher` + `@EventListener` | Spring AMQP, Spring Kafka | Spring Modulith, ArchUnit |
| Rust | `std::sync::mpsc`, `tokio::sync::broadcast` | `lapin`, `rdkafka` | crates in a workspace |
| C | arrays of callbacks | `librabbitmq`, `librdkafka` | headers and build targets |
| C++ | `std::function` lists, Boost.Signals2 | `librdkafka` C++ API | CMake targets |
| C# | MediatR notifications, `event` | MassTransit, `Confluent.Kafka` | one project per module |

**Spring Modulith goes furthest:** its event publication registry stores each published event in the database in the same transaction as the business change, and re-sends any whose listener didn't complete. That's the [[architecture/03-architectural-patterns/05-transactional-outbox/index|transactional outbox]], built in.

## 2. The idempotent consumer, idiomatically

Every language has a set operation that **adds an item and reports whether it was new** — the whole idempotency check in one call:

| Language | "Add, and was it new?" |
|---|---|
| Python | `if id in seen: return` then `seen.add(id)` — `add` returns nothing |
| Go | `if seen[id] { return }; seen[id] = true` |
| Java | `if (!seen.add(id)) return;` |
| Rust | `if !seen.insert(id) { continue; }` |
| C++ | `if (!seen.insert(id).second) return;` |
| C# | `if (!seen.Add(id)) return;` |
| C | search the array, then append |

In production the set is a database table with a **unique constraint on the event ID**, written in the same transaction as the effect — so a crash can't record one without the other.

## Terms used in this lesson

1. **At-least-once delivery**: This is a broker's guarantee that every event arrives, possibly more than once.
2. **Idempotent consumer**: This is a handler that has the same effect whether an event arrives once or many times, usually by remembering event IDs.
3. **Event publication registry**: In Spring Modulith, this is a table of published events and whether each listener has completed — an outbox built into the framework.
4. **Channel**: In Go and Rust, this is a typed queue between parts of a program: one side sends values, the other receives them.

## 3. Python

```python
"""shop.py — two modules talking through events; a bus that delivers at least once."""
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class PaymentSucceeded:
    event_id: str
    order_id: str
    amount_kobo: int


Handler = Callable[[PaymentSucceeded], None]


class InProcessBus:
    def __init__(self):
        self.handlers: list[Handler] = []

    def subscribe(self, handler: Handler) -> None:
        self.handlers.append(handler)

    def publish(self, event: PaymentSucceeded) -> None:
        for handler in self.handlers:
            handler(event)


class AtLeastOnceBus(InProcessBus):
    """What a real broker promises. This one delivers every event twice."""

    def publish(self, event: PaymentSucceeded) -> None:
        super().publish(event)
        super().publish(event)


class Payments:
    def __init__(self, bus: InProcessBus):
        self.bus, self.n = bus, 0

    def record_success(self, order_id: str, amount_kobo: int) -> None:
        self.n += 1
        self.bus.publish(PaymentSucceeded(f"evt_{self.n}", order_id, amount_kobo))


class Orders:
    """Never imports Payments — it only knows the event's shape."""

    def __init__(self, bus: InProcessBus, idempotent: bool):
        self.paid: dict[str, int] = {}
        self.seen: set[str] = set()
        self.idempotent = idempotent
        bus.subscribe(self.on_payment)

    def on_payment(self, event: PaymentSucceeded) -> None:
        if self.idempotent:
            if event.event_id in self.seen:
                return
            self.seen.add(event.event_id)
        self.paid[event.order_id] = self.paid.get(event.order_id, 0) + event.amount_kobo
```

**Lab:** [`backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/python/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/python) — checked with Python 3.14.

## 4. Go

The bus here is a slice of functions; for modules in different goroutines, a **channel** per subscriber is the Go idiom — and forces you to decide what happens when a subscriber falls behind.

```go
// Package shop: modules exchange events over a bus. Orders never imports payments.
package shop

import "fmt"

type PaymentSucceeded struct {
	EventID    string
	OrderID    string
	AmountKobo int64
}

type Bus interface {
	Publish(PaymentSucceeded)
	Subscribe(func(PaymentSucceeded))
}

type InProcessBus struct{ handlers []func(PaymentSucceeded) }

func (b *InProcessBus) Subscribe(h func(PaymentSucceeded)) { b.handlers = append(b.handlers, h) }
func (b *InProcessBus) Publish(e PaymentSucceeded) {
	for _, h := range b.handlers {
		h(e)
	}
}

// AtLeastOnceBus delivers every event twice — what a broker is allowed to do.
type AtLeastOnceBus struct{ InProcessBus }

func (b *AtLeastOnceBus) Publish(e PaymentSucceeded) {
	b.InProcessBus.Publish(e)
	b.InProcessBus.Publish(e)
}

type Payments struct {
	Bus Bus
	n   int
}

func (p *Payments) RecordSuccess(orderID string, kobo int64) {
	p.n++
	p.Bus.Publish(PaymentSucceeded{EventID: fmt.Sprintf("evt_%d", p.n), OrderID: orderID, AmountKobo: kobo})
}

type Orders struct {
	Paid map[string]int64
	seen map[string]bool
}

func NewOrders(bus Bus, idempotent bool) *Orders {
	o := &Orders{Paid: map[string]int64{}, seen: map[string]bool{}}
	bus.Subscribe(func(e PaymentSucceeded) {
		if idempotent {
			if o.seen[e.EventID] {
				return
			}
			o.seen[e.EventID] = true
		}
		o.Paid[e.OrderID] += e.AmountKobo
	})
	return o
}
```

**Lab:** [`backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/go/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/go) — checked with Go 1.26.

## 5. Java

Plain Java below; in **Spring**, `payments` calls `ApplicationEventPublisher.publishEvent(...)` and `orders` has an `@EventListener` method — or, with Spring Modulith, `@ApplicationModuleListener`, which runs after the transaction commits and is retried from the registry if it fails.

```java
package shop;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;

// In Spring: payments calls ApplicationEventPublisher.publishEvent(...), orders has an
// @EventListener (or @ApplicationModuleListener with Spring Modulith). Same shape, plain Java here.
public final class Shop {
    public record PaymentSucceeded(String eventId, String orderId, long amountKobo) {}

    public static class InProcessBus {
        private final List<Consumer<PaymentSucceeded>> handlers = new ArrayList<>();
        public void subscribe(Consumer<PaymentSucceeded> h) { handlers.add(h); }
        public void publish(PaymentSucceeded e) { handlers.forEach(h -> h.accept(e)); }
    }

    // What a broker may do: deliver every event twice.
    public static final class AtLeastOnceBus extends InProcessBus {
        @Override public void publish(PaymentSucceeded e) { super.publish(e); super.publish(e); }
    }

    public static final class Payments {
        private final InProcessBus bus;
        private int n;
        public Payments(InProcessBus bus) { this.bus = bus; }
        public void recordSuccess(String orderId, long kobo) { bus.publish(new PaymentSucceeded("evt_" + ++n, orderId, kobo)); }
    }

    public static final class Orders {
        public final Map<String, Long> paid = new HashMap<>();
        private final Set<String> seen = new HashSet<>();
        public Orders(InProcessBus bus, boolean idempotent) {
            bus.subscribe(e -> {
                if (idempotent && !seen.add(e.eventId())) return;   // add() is false if already seen
                paid.merge(e.orderId(), e.amountKobo(), Long::sum);
            });
        }
    }

    public static void main(String[] args) {
        var naiveBus = new AtLeastOnceBus();
        var naive = new Orders(naiveBus, false);
        new Payments(naiveBus).recordSuccess("o1", 500_000);
        assert naive.paid.get("o1") == 1_000_000 : naive.paid;

        var bus = new AtLeastOnceBus();
        var orders = new Orders(bus, true);
        var payments = new Payments(bus);
        payments.recordSuccess("o1", 500_000);
        payments.recordSuccess("o1", 250_000);
        assert orders.paid.get("o1") == 750_000 : orders.paid;
        System.out.println("ok: naive consumer double-counts; idempotent one doesn't");
    }
}
```

**Lab:** [`backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/java/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/java) — checked with Java 21. `Set.add` returning `false` for a repeat makes the check one line.

## 6. Rust

The standard library's **`mpsc` channel** connects the modules: `payments` holds the sender, `orders` the receiver, and neither imports the other. `HashSet::insert` returns `false` for a repeat.

```rust
//! Modules talk through a channel: payments sends events, orders receives them.
//! std::sync::mpsc is the standard library's multi-producer, single-consumer channel.
use std::collections::{HashMap, HashSet};
use std::sync::mpsc::{Receiver, Sender, channel};

#[derive(Clone, Debug)]
pub struct PaymentSucceeded {
    pub event_id: String,
    pub order_id: String,
    pub amount_kobo: u64,
}

pub struct Payments {
    tx: Sender<PaymentSucceeded>,
    n: u32,
    pub deliver_twice: bool, // simulates a broker's at-least-once delivery
}

impl Payments {
    pub fn record_success(&mut self, order_id: &str, amount_kobo: u64) {
        self.n += 1;
        let event = PaymentSucceeded {
            event_id: format!("evt_{}", self.n),
            order_id: order_id.into(),
            amount_kobo,
        };
        if self.deliver_twice {
            self.tx.send(event.clone()).unwrap();
        }
        self.tx.send(event).unwrap();
    }
}

#[derive(Default)]
pub struct Orders {
    pub paid: HashMap<String, u64>,
    seen: HashSet<String>,
}

impl Orders {
    /// Handles every event waiting on the channel. `insert` returns false for a repeat.
    pub fn drain(&mut self, rx: &Receiver<PaymentSucceeded>, idempotent: bool) {
        for event in rx.try_iter() {
            if idempotent && !self.seen.insert(event.event_id.clone()) {
                continue;
            }
            *self.paid.entry(event.order_id).or_default() += event.amount_kobo;
        }
    }
}

pub fn wire(deliver_twice: bool) -> (Payments, Receiver<PaymentSucceeded>) {
    let (tx, rx) = channel();
    (
        Payments {
            tx,
            n: 0,
            deliver_twice,
        },
        rx,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn naive_consumer_double_counts() {
        let (mut payments, rx) = wire(true);
        let mut orders = Orders::default();
        payments.record_success("o1", 500_000);
        orders.drain(&rx, false);
        assert_eq!(orders.paid["o1"], 1_000_000);
    }

    #[test]
    fn idempotent_consumer_counts_each_event_once() {
        let (mut payments, rx) = wire(true);
        let mut orders = Orders::default();
        payments.record_success("o1", 500_000);
        payments.record_success("o1", 250_000);
        orders.drain(&rx, true);
        assert_eq!(orders.paid["o1"], 750_000);
    }
}
```

**Lab:** [`backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/rust/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/rust) — checked with Rust 1.96. In async services, `tokio::sync::broadcast` gives every subscriber its own copy of each event.

## 7. C

```c
/* shop.c — a bus as an array of callbacks; orders deduplicates on event id. */
#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct { char event_id[16]; char order_id[8]; long amount_kobo; } payment_succeeded;
typedef void (*handler)(void *ctx, const payment_succeeded *e);

typedef struct {
    struct { handler fn; void *ctx; } handlers[4];
    int count;
    int deliver_twice;   /* simulates a broker's at-least-once delivery */
} bus;

static void subscribe(bus *b, handler fn, void *ctx) { b->handlers[b->count].fn = fn; b->handlers[b->count++].ctx = ctx; }
static void publish(bus *b, const payment_succeeded *e) {
    for (int round = 0; round < (b->deliver_twice ? 2 : 1); round++)
        for (int i = 0; i < b->count; i++) b->handlers[i].fn(b->handlers[i].ctx, e);
}

typedef struct { long paid_o1; char seen[8][16]; int seen_count; int idempotent; } orders;

static void orders_on_payment(void *ctx, const payment_succeeded *e) {
    orders *o = ctx;
    if (o->idempotent) {
        for (int i = 0; i < o->seen_count; i++)
            if (strcmp(o->seen[i], e->event_id) == 0) return;   /* already handled */
        snprintf(o->seen[o->seen_count++], sizeof o->seen[0], "%s", e->event_id);
    }
    if (strcmp(e->order_id, "o1") == 0) o->paid_o1 += e->amount_kobo;
}

static long run(int idempotent) {
    bus b = {.deliver_twice = 1};
    orders o = {.idempotent = idempotent};
    subscribe(&b, orders_on_payment, &o);
    payment_succeeded first = {"evt_1", "o1", 500000}, second = {"evt_2", "o1", 250000};
    publish(&b, &first);
    publish(&b, &second);
    return o.paid_o1;
}

int main(void) {
    assert(run(0) == 1500000);   /* naive: both payments counted twice */
    assert(run(1) == 750000);    /* idempotent: each event once */
    puts("ok: naive consumer double-counts; idempotent one doesn't");
    return 0;
}
```

**Lab:** [`backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/c/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/c) — checked with GCC 16.

## 8. C++

```cpp
// shop.cpp — a bus of std::function handlers; orders deduplicates with an unordered_set.
#include <cassert>
#include <functional>
#include <iostream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

struct PaymentSucceeded { std::string event_id, order_id; long amount_kobo; };

class Bus {
public:
    explicit Bus(bool deliver_twice) : deliver_twice_(deliver_twice) {}
    void subscribe(std::function<void(const PaymentSucceeded&)> h) { handlers_.push_back(std::move(h)); }
    void publish(const PaymentSucceeded& e) {
        for (int round = 0; round < (deliver_twice_ ? 2 : 1); ++round)
            for (const auto& h : handlers_) h(e);
    }
private:
    bool deliver_twice_;
    std::vector<std::function<void(const PaymentSucceeded&)>> handlers_;
};

struct Orders {
    std::unordered_map<std::string, long> paid;
    std::unordered_set<std::string> seen;
    Orders(Bus& bus, bool idempotent) {
        bus.subscribe([this, idempotent](const PaymentSucceeded& e) {
            if (idempotent && !seen.insert(e.event_id).second) return;   // .second is false for a repeat
            paid[e.order_id] += e.amount_kobo;
        });
    }
};

int main() {
    Bus naive_bus(true);
    Orders naive(naive_bus, false);
    naive_bus.publish({"evt_1", "o1", 500'000});
    assert(naive.paid["o1"] == 1'000'000);

    Bus bus(true);
    Orders orders(bus, true);
    bus.publish({"evt_1", "o1", 500'000});
    bus.publish({"evt_2", "o1", 250'000});
    assert(orders.paid["o1"] == 750'000);
    std::cout << "ok: naive consumer double-counts; idempotent one doesn't\n";
}
```

**Lab:** [`backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/cpp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/cpp) — checked with GCC 16. `unordered_set::insert` returns a pair; `.second` says whether the item was new.

## 9. C#

In ASP.NET Core applications, the in-process bus is usually **MediatR** notifications, and the broker client **MassTransit**, which supports idempotent consumers through an inbox.

```csharp
// In ASP.NET Core apps this bus is usually MediatR notifications in-process, or MassTransit
// over a broker — whose consumers must be idempotent for the reason shown here.
var naiveBus = new Bus(deliverTwice: true);
var naive = new Orders(naiveBus, idempotent: false);
new Payments(naiveBus).RecordSuccess("o1", 500_000);
Check(naive.Paid["o1"] == 1_000_000, "naive consumer double-counts");

var bus = new Bus(deliverTwice: true);
var orders = new Orders(bus, idempotent: true);
var payments = new Payments(bus);
payments.RecordSuccess("o1", 500_000);
payments.RecordSuccess("o1", 250_000);
Check(orders.Paid["o1"] == 750_000, "idempotent consumer counts each event once");
Console.WriteLine("ok: naive consumer double-counts; idempotent one doesn't");

static void Check(bool ok, string what) { if (!ok) throw new Exception($"FAIL: {what}"); }

record PaymentSucceeded(string EventId, string OrderId, long AmountKobo);

sealed class Bus(bool deliverTwice)
{
    private readonly List<Action<PaymentSucceeded>> _handlers = [];
    public void Subscribe(Action<PaymentSucceeded> handler) => _handlers.Add(handler);
    public void Publish(PaymentSucceeded e)
    {
        for (var round = 0; round < (deliverTwice ? 2 : 1); round++)
            foreach (var h in _handlers) h(e);
    }
}

sealed class Payments(Bus bus)
{
    private int _n;
    public void RecordSuccess(string orderId, long kobo) => bus.Publish(new($"evt_{++_n}", orderId, kobo));
}

sealed class Orders
{
    public Dictionary<string, long> Paid { get; } = [];
    private readonly HashSet<string> _seen = [];
    public Orders(Bus bus, bool idempotent) => bus.Subscribe(e =>
    {
        if (idempotent && !_seen.Add(e.EventId)) return;   // Add is false for a repeat
        Paid[e.OrderId] = Paid.GetValueOrDefault(e.OrderId) + e.AmountKobo;
    });
}
```

**Lab:** [`backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/csharp/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/backend/03-structuring-a-backend/05-modular-monolith-to-services/labs/csharp) — runs in the .NET 10 SDK container.

## Check your understanding

1. Why does every language's consumer need the same fix, regardless of how its bus works?
2. What does Spring Modulith's event publication registry add, and what pattern is it?
3. In Java, C#, Rust and C++, what single call checks for a repeat and records the event?
4. Why must the processed-events record be written in the same transaction as the effect?

<details>
<summary>Answers — after your attempt</summary>

1. The duplicate comes from the delivery guarantee — at least once — not from the language. Any consumer that adds rather than sets will double-count.
2. It stores published events in the database with the business change and re-sends any whose listener didn't finish. It's the transactional outbox.
3. Java `seen.add(id)`, C# `seen.Add(id)` (both return `false` for a repeat), Rust `seen.insert(id)` (false for a repeat), C++ `seen.insert(id).second`.
4. Otherwise a crash between them could record the event without the effect (the effect is lost) or the effect without the event (it's applied again on redelivery).

</details>

## Practice — independent task

**In your second language:** extend the lab with an `inventory` module that reserves stock on `PaymentSucceeded` and publishes `StockReserved` or `StockUnavailable`, with orders reacting to both. Run it on the at-least-once bus.

**Done when:** every consumer is idempotent, an out-of-stock order ends with exactly one refund request, and no module imports another.

## Before moving on

You know your ecosystem's event plumbing and can write an idempotent consumer in it.

**Recap.** The event bus and broker client change by ecosystem; the rule doesn't: at-least-once delivery means idempotent consumers, keyed on event ID, recorded in the same transaction as the effect. Spring Modulith builds the outbox in; elsewhere you write it.

**Next.** Back to the course: [[backend/07-practices/01-backend-best-practices/index|backend best practices]] (week 6).

## Related
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|Modular monolith to services]] — the main lesson
- [[architecture/03-architectural-patterns/05-transactional-outbox/index|Transactional outbox]]
- [[concepts/03-design-patterns/03-behavioral-patterns/in-other-languages|Behavioural patterns in other languages]] — observers and channels
