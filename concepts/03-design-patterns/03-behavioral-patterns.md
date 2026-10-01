# Behavioral Patterns

> **[Intermediate]** · How objects **communicate and share responsibility** — reacting to changes, swapping algorithms, turning actions into objects, and changing behaviour as something moves through stages.

## Before you start

You can already:

- Write TypeScript classes and pass functions as arguments.
- Explain open/closed — adding a case without editing existing ones → [[concepts/04-best-practices/05-solid-principles|SOLID]].

After this lesson you will be able to:

1. Recognise observer, strategy, command, state and iterator in real code, and name the problem each solves.
2. Model an object's lifecycle as a state machine, so illegal moves are impossible rather than unchecked.
3. Add a reaction to an event without editing the code that raises it.

**Study route.** §1–6 are the patterns; §5 (State) and the worked example are the heaviest. Make the prediction before running the example.

## The kid version

At a football match, the referee blows the whistle, and everyone who cares reacts — players stop, the crowd cheers, the scoreboard updates. The referee doesn't tell each person what to do; **they just blow the whistle, and whoever is listening responds.** That's the observer pattern. And the game itself has stages — before kick-off, playing, half-time, finished — and what's allowed depends on the stage: you can't score at half-time. That's the state pattern.

**Where the analogy stops working.** At a match you can see who's listening. In code, the listeners are registered in other files, so "what happens when this event fires?" can mean searching the whole codebase — the cost listed in the pitfalls below.

## 1. Why this exists

When an order ships, the business wants a customer email, an inventory update, an analytics event — and next month, a WhatsApp message. If `ship()` calls each of those directly, every new reaction is an edit to the shipping code. Meanwhile, `cancel()`, `refund()` and `ship()` each start with their own slightly different `if (status === ...)` checks, and support finds a shipped order that got cancelled. **One is a communication problem, the other a responsibility problem** — the two kinds this lesson's patterns solve.

## Terms used in this lesson

1. **Subject**: This is also known as the **publisher** or **emitter**. It is the object that announces something happened.
2. **Observer**: This is also known as a **listener**, **subscriber** or **handler**. It is a function or object that registered to be told when the subject announces something.
3. **Strategy**: This is one of several interchangeable algorithms behind the same interface, chosen at runtime.
4. **Command**: This is an action, together with its inputs, stored as an object so it can be queued, logged, retried or undone.
5. **State machine**: This is a model of something that is always in exactly one of a fixed set of states, and moves between them only through allowed transitions.
6. **Transition**: This is a move from one state to another, triggered by an action, such as `pending` → `paid` on `pay`.
7. **Iterator**: This is an object that hands out a collection's items one at a time without revealing how the collection is stored.

## 2. Observer — reacting to another object's changes

One object (the **subject**) maintains a list of dependents (**observers**) and notifies all of them automatically whenever its state changes, without needing to know anything specific about what each observer actually does in response.

```typescript
class EventEmitter {
  private listeners: Record<string, Function[]> = {};
  on(event: string, callback: Function) {
    (this.listeners[event] ??= []).push(callback);
  }
  emit(event: string, data: unknown) {
    this.listeners[event]?.forEach((cb) => cb(data));
  }
}

const emitter = new EventEmitter();
emitter.on("order.placed", (order) => sendConfirmationEmail(order));
emitter.on("order.placed", (order) => updateInventory(order));
emitter.emit("order.placed", { id: 42 });   // both listeners run, emitter doesn't know or care what they do
```

This is the exact mechanism underneath DOM event listeners, Node's `EventEmitter`, and pub/sub messaging systems generally — the subject is fully decoupled from its observers, which is the whole point: new behavior can be added (a new listener) without ever touching the code that emits the event.

## 3. Strategy — swapping an algorithm's implementation at runtime

Defines a family of interchangeable algorithms behind a common interface, letting the specific one used be selected at runtime rather than hardcoded — the calling code depends only on the shared interface, not on any specific algorithm's implementation.

```typescript
interface ShippingStrategy { calculate(weight: number): number; }
class StandardShipping implements ShippingStrategy { calculate(weight: number) { return weight * 2; } }
class ExpressShipping implements ShippingStrategy { calculate(weight: number) { return weight * 5 + 10; } }

class Order {
  constructor(private shippingStrategy: ShippingStrategy) {}
  getShippingCost(weight: number) { return this.shippingStrategy.calculate(weight); }
}

const order = new Order(new ExpressShipping());   // swap this for StandardShipping — Order itself never changes
```

This directly relates back to [[concepts/03-design-patterns/01-creational-patterns|Factory]] — a Factory is often exactly what decides *which* Strategy to instantiate based on runtime input, the two patterns frequently showing up together in the same piece of code.

## 4. Command — turning a request into an object

Encapsulates a request (an action plus its parameters) as an object, so it can be passed around, queued, logged, or undone, rather than being just a direct function call that happens and is immediately forgotten.

```typescript
interface Command { execute(): void; undo(): void; }
class AddTextCommand implements Command {
  constructor(private document: Document, private text: string) {}
  execute() { this.document.content += this.text; }
  undo() { this.document.content = this.document.content.slice(0, -this.text.length); }
}

const history: Command[] = [];
function runCommand(cmd: Command) { cmd.execute(); history.push(cmd); }
function undoLast() { history.pop()?.undo(); }
```

This is exactly the pattern underneath undo/redo functionality, task queues, and any "record what happened so it can be replayed or reversed later" requirement — turning an action into a first-class object is what makes storing, queuing, and reversing it possible at all.

## 5. State — behaviour that depends on what stage something is in

An object whose allowed actions depend on its current stage — an order that can be cancelled while pending or paid but not once shipped — is a **state machine**. Without the pattern, every method starts with a growing `if (status === ...)` chain, and the rules for one stage are scattered across every method.

The State pattern puts the rules **per state**: each state says which actions it allows and which state each leads to. The classic object-oriented form gives each state its own class (`PendingState`, `PaidState`) with the same methods. In TypeScript, a **transition table** — a plain object mapping state → action → next state — usually says the same thing more clearly, and it's what the worked example uses.

```ts
// classic form — fragment
interface OrderState { pay(order: Order): void; ship(order: Order): void; cancel(order: Order): void }
class Pending implements OrderState {
  pay(order: Order) { order.state = new Paid(); }
  ship() { throw new Error("pay first"); }
  cancel(order: Order) { order.state = new Cancelled(); }
}
```

The payoff either way: **every legal move is written in one place**, so "can a shipped order be cancelled?" is answered by reading one line, and an illegal move is impossible rather than merely unhandled.

## 6. Iterator — traversing a collection without exposing its internals

Provides a standard way to step through a collection's elements sequentially, without the calling code needing to know whether the underlying collection is an array, a linked list, or a tree.

```typescript
class Range {
  constructor(private start: number, private end: number) {}
  [Symbol.iterator]() {
    let current = this.start;
    const end = this.end;
    return {
      next: () => current < end ? { value: current++, done: false } : { value: undefined, done: true },
    };
  }
}

for (const n of new Range(1, 5)) { console.log(n); }   // 1 2 3 4
```

JavaScript's `for...of` loop and the iterator protocol above are a language-level implementation of exactly this pattern — see [[dsa/02-data-structures/05-trees/04-traversal/index|traversal]] in the DSA notes for the underlying structures (trees, graphs) this same idea generalizes to beyond simple linear collections.

## 7. Worked example — an order lifecycle with State and Observer

**Predict before running.** A shipped order receives `cancel`. With the code below, what happens to its status, and do the listeners hear anything?

```ts
// order-state.ts — State (which actions are legal now) + Observer (who hears about changes)
export type Status = "pending" | "paid" | "shipped" | "delivered" | "cancelled";
export type Action = "pay" | "ship" | "deliver" | "cancel";

// The State pattern, table form: each state lists the actions it allows and where they lead.
// A state missing from an action's row means "not allowed here".
const transitions: Record<Status, Partial<Record<Action, Status>>> = {
  pending: { pay: "paid", cancel: "cancelled" },
  paid: { ship: "shipped", cancel: "cancelled" },
  shipped: { deliver: "delivered" },
  delivered: {},
  cancelled: {},
};

export class IllegalTransitionError extends Error {}

type Listener = (event: { orderId: string; from: Status; to: Status }) => void;

export class Order {
  id: string;
  status: Status = "pending";
  #listeners: Listener[] = [];

  constructor(id: string) {
    this.id = id;
  }

  // Observer: subscribers register; the order never knows what they do.
  onChange(listener: Listener) {
    this.#listeners.push(listener);
  }

  apply(action: Action) {
    const next = transitions[this.status][action];
    if (!next) throw new IllegalTransitionError(`cannot ${action} an order that is ${this.status}`);
    const from = this.status;
    this.status = next;
    for (const listener of this.#listeners) listener({ orderId: this.id, from, to: next });
  }

  allowedActions(): Action[] {
    return Object.keys(transitions[this.status]) as Action[];
  }
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { IllegalTransitionError, Order } from "./order-state.ts";

test("happy path, with two observers that don't know about each other", () => {
  const emails: string[] = [];
  const audit: string[] = [];
  const order = new Order("o1");
  order.onChange((e) => { if (e.to === "shipped") emails.push(`${e.orderId} is on its way`); });
  order.onChange((e) => audit.push(`${e.from}->${e.to}`));

  order.apply("pay");
  order.apply("ship");
  order.apply("deliver");

  assert.equal(order.status, "delivered");
  assert.deepEqual(emails, ["o1 is on its way"]);
  assert.deepEqual(audit, ["pending->paid", "paid->shipped", "shipped->delivered"]);
});

test("a shipped order cannot be cancelled, and nothing is announced", () => {
  const audit: string[] = [];
  const order = new Order("o2");
  order.onChange((e) => audit.push(`${e.from}->${e.to}`));
  order.apply("pay");
  order.apply("ship");
  assert.throws(() => order.apply("cancel"), IllegalTransitionError);
  assert.equal(order.status, "shipped");
  assert.deepEqual(audit, ["pending->paid", "paid->shipped"]);
});

test("the UI can ask which buttons to show", () => {
  const order = new Order("o3");
  assert.deepEqual(order.allowedActions(), ["pay", "cancel"]);
  order.apply("pay");
  assert.deepEqual(order.allowedActions(), ["ship", "cancel"]);
});
```

**Lab:** these files are in `labs/behavioral-patterns/`. From the vault root, `python3 labs/run.py behavioral-patterns` runs them and checks this page still shows the same code.

**Run it.** Both files in one folder; `node --test` from it (Node 23.6 or later; checked with Node 26). Expected:

```
ℹ tests 3
ℹ pass 3
ℹ fail 0
```

**The answer.** The `cancel` throws `IllegalTransitionError`, the status stays `shipped`, and **no listener runs**, because the order announces only after a successful transition. That ordering is deliberate — notify before changing state and an email would go out for a cancellation that never happened.

**Two things to notice.**
- The email listener and the audit listener don't know about each other, and `Order` doesn't know about either. Adding a WhatsApp notification is one `onChange` call in the composition root.
- `allowedActions()` comes free from the table. The UI can render exactly the buttons the current state allows, so the backend and frontend share one source of truth.

**The limits.** Listeners here run synchronously, in the same process, inside `apply`. If the email listener throws, `apply` throws *after* the status already changed. Production systems usually save the state change and an event record together, then deliver the event separately — the [[architecture/03-architectural-patterns/05-transactional-outbox|transactional outbox]] pattern.

## Common pitfalls

- Observer's decoupling is also a debugging cost — with many listeners subscribed to the same event across a large codebase, tracing "what actually happens when this event fires" can require hunting across many files, unlike a direct function call you can just follow.
- Strategy and simple conditional logic (`if/else` picking behavior directly) solve the same problem at small scale — Strategy earns its complexity when there are genuinely many interchangeable algorithms, or when new ones need to be added without modifying existing code; for two or three cases that rarely change, a plain conditional can be perfectly reasonable and more direct.
- Command's overhead (wrapping every action in an object) is only worth it when you actually need the deferred-execution, queuing, or undo capability it provides — using it for a simple, immediate, one-off action adds ceremony with no payoff.

## Check your understanding

1. What does the observer pattern decouple, and what does that decoupling cost you?
2. Strategy versus a plain `if/else` — when does strategy earn its extra structure?
3. Give two things you can do with a command object that you can't do with a direct function call.
4. In the worked example, why does `apply` notify listeners only *after* changing the status?
5. A payment can be `authorised`, `captured`, `refunded`, or `voided`, and you can't refund a voided payment. Which pattern, and what's the first thing you'd write down?

<details>
<summary>Answers — after your attempt</summary>

1. It decouples the code raising an event from the code reacting to it, so new reactions don't edit the emitter. The cost is traceability — finding everything that happens on an event means searching for every listener.
2. When there are many interchangeable algorithms, or new ones arrive regularly and you want to add them without editing existing code. For two stable cases, `if/else` is clearer.
3. Any two of: queue it for later, log or persist it, retry it, undo it, send it to another process.
4. So listeners only hear about changes that actually happened. Notifying first could send an email for a transition that then fails.
5. State. Write the transition table first — every state, every action, and which are allowed — before any code. Missing entries are exactly the bugs.

</details>

## Practice — independent task

**Extend the order state machine.**

1. Add a `refund` action allowed only from `delivered`, leading to a new `refunded` state.
2. Add `return_requested` between `delivered` and `refunded`, so a refund needs a return first. Update the table, and nothing else in `Order`.
3. Add a listener that records how long each order spent in each state, using timestamps passed in from the test so the test is deterministic.

**Done when:** `Order`'s methods are unchanged by steps 1–2, a test proves `cancelled → refund` throws, and the timing listener is tested without `Date.now()` or real waiting.

For interview-style questions, see [[concepts/interview/02-patterns-code-quality-and-review|patterns, code quality and review]].

## Before moving on

You can name the behavioural patterns in real code, model a lifecycle as a transition table, and add reactions without editing the emitter.

**Recap.** **Observer**: announce; whoever's listening reacts. **Strategy**: swap algorithms behind one interface. **Command**: an action as an object — queue, log, undo. **State**: what's allowed depends on the current stage; write the transitions in one place. **Iterator**: walk a collection without seeing inside it.

**Next.** [[backend/03-structuring-a-backend/03-dependency-injection-and-wiring|Dependency injection and wiring]] — where all these objects get created and connected.

## Related
- [[concepts/03-design-patterns/01-creational-patterns|creational patterns]]
- [[concepts/03-design-patterns/02-structural-patterns|structural patterns]]
- [[dsa/02-data-structures/05-trees/04-traversal/index|traversal]] — the same iteration idea generalized to trees and graphs
