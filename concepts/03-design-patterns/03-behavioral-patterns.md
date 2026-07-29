# Behavioral Patterns

Where [[01-creational-patterns|creational-patterns]] and [[02-structural-patterns|structural-patterns]] are about creation and composition, behavioral patterns are about how objects **communicate and assign responsibility** to each other — how one object reacts to another's changes, how an algorithm's steps can vary, how a request gets handled without the sender needing to know by whom.

## Observer — reacting to another object's changes

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

## Strategy — swapping an algorithm's implementation at runtime

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

This directly relates back to [[01-creational-patterns|Factory]] — a Factory is often exactly what decides *which* Strategy to instantiate based on runtime input, the two patterns frequently showing up together in the same piece of code.

## Command — turning a request into an object

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

## Iterator — traversing a collection without exposing its internals

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

JavaScript's `for...of` loop and the iterator protocol above are a language-level implementation of exactly this pattern — see [[02-traversal|traversal]] in the DSA notes for the underlying structures (trees, graphs) this same idea generalizes to beyond simple linear collections.

## Gotchas

- Observer's decoupling is also a debugging cost — with many listeners subscribed to the same event across a large codebase, tracing "what actually happens when this event fires" can require hunting across many files, unlike a direct function call you can just follow.
- Strategy and simple conditional logic (`if/else` picking behavior directly) solve the same problem at small scale — Strategy earns its complexity when there are genuinely many interchangeable algorithms, or when new ones need to be added without modifying existing code; for two or three cases that rarely change, a plain conditional can be perfectly reasonable and more direct.
- Command's overhead (wrapping every action in an object) is only worth it when you actually need the deferred-execution, queuing, or undo capability it provides — using it for a simple, immediate, one-off action adds ceremony with no payoff.

## Related
- [[01-creational-patterns|creational-patterns]]
- [[02-structural-patterns|structural-patterns]]
- [[foundations/dsa/04-data-structures/05-trees/02-traversal|traversal]] — the same iteration idea generalized to trees and graphs
