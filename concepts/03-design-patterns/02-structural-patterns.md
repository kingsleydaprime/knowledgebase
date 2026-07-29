# Structural Patterns

Where [[01-creational-patterns|creational-patterns]] is about how objects get created, structural patterns are about how objects and classes are **composed together** into larger structures — making incompatible interfaces work together, adding behavior without modifying existing code, controlling access to an object.

## Adapter — making an incompatible interface fit

Wraps an object with an interface your code doesn't expect, exposing the interface your code *does* expect, translating calls between the two underneath. The classic use case: integrating a third-party library or legacy code whose interface doesn't match what the rest of your codebase expects, without modifying that third-party code at all.

```typescript
// third-party library's interface — not something you control or want to change
class LegacyLogger {
  writeLog(msg: string, level: number) { /* ... */ }
}

// the interface your application actually expects
interface Logger { info(msg: string): void; error(msg: string): void; }

class LegacyLoggerAdapter implements Logger {
  constructor(private legacy: LegacyLogger) {}
  info(msg: string) { this.legacy.writeLog(msg, 1); }
  error(msg: string) { this.legacy.writeLog(msg, 3); }
}

const logger: Logger = new LegacyLoggerAdapter(new LegacyLogger());
logger.info("app started");   // rest of the app only ever sees the clean `Logger` interface
```

## Decorator — adding behavior without modifying the original class

Wraps an object to add new behavior, transparently, without changing the original class's code — and multiple decorators can be stacked, each adding its own layer.

```typescript
interface Coffee { cost(): number; description(): string; }
class SimpleCoffee implements Coffee {
  cost() { return 2; }
  description() { return "Coffee"; }
}
class MilkDecorator implements Coffee {
  constructor(private coffee: Coffee) {}
  cost() { return this.coffee.cost() + 0.5; }
  description() { return this.coffee.description() + " + Milk"; }
}

let order: Coffee = new SimpleCoffee();
order = new MilkDecorator(order);   // stack another decorator the same way for "+ Sugar", etc.
console.log(order.description(), order.cost());   // "Coffee + Milk" 2.5
```

This is the same underlying idea as Python's `@decorator` syntax or a middleware chain (see `concepts/backend/http-servers.md`) — wrapping a thing with additional behavior, transparently, without the wrapped thing needing to know it's been wrapped.

## Proxy — controlling access to an object

Provides a stand-in for another object, controlling access to it — adding lazy loading (don't create the expensive real object until it's actually needed), access control, caching, or logging, transparently, from the caller's perspective.

```typescript
interface Image { display(): void; }
class RealImage implements Image {
  constructor(private filename: string) { this.loadFromDisk(); }   // expensive
  private loadFromDisk() { console.log(`Loading ${this.filename}`); }
  display() { console.log(`Displaying ${this.filename}`); }
}
class LazyImageProxy implements Image {
  private realImage?: RealImage;
  constructor(private filename: string) {}
  display() {
    if (!this.realImage) this.realImage = new RealImage(this.filename);   // only loads on first actual use
    this.realImage.display();
  }
}
```

JavaScript's built-in `Proxy` object is a direct, language-level implementation of this exact pattern — intercepting property access/assignment on an object transparently.

## Facade — a simple interface over a complex subsystem

Provides one simple, unified interface hiding a more complex set of underlying classes/subsystems working together — the caller interacts with one simple method instead of coordinating several underlying components' interactions itself.

```typescript
class VideoConverterFacade {
  convert(filename: string, format: string) {
    const codec = new CodecFactory().extract(filename);      // several underlying subsystems
    const buffer = new BitrateReader().read(filename, codec);
    const result = new AudioMixer().fix(buffer);
    return new FileWriter().write(result, format);
  }
}

// caller's perspective: one simple call, complexity hidden underneath
new VideoConverterFacade().convert("video.mp4", "avi");
```

The distinction from Adapter: an Adapter makes an *existing* interface compatible with what you need; a Facade creates a *new*, simpler interface over a genuinely complex set of subsystems, purely for ease of use.

## Gotchas

- Adapter and Facade solve genuinely different problems despite feeling similar — Adapter is about compatibility with an interface you don't control; Facade is about simplifying a complex interface you do control (or that's simply made up of many pieces).
- Overusing Decorator by stacking many layers can make it hard to reason about the final combined behavior/cost at a glance — readable up to a point, then a source of confusion past it; worth naming/documenting common decorator combinations if a codebase leans on this pattern heavily.
- Proxy's transparency is the whole point — a proxy that doesn't genuinely implement the same interface as the real object it stands in for defeats the pattern's purpose, since callers should be able to use either interchangeably without caring which they have.

## Related
- [[01-creational-patterns|creational-patterns]]
- [[03-behavioral-patterns|behavioral-patterns]]
