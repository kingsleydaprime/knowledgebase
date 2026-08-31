# Async and Isolates

**[Intermediate → Advanced]** — a single-threaded event loop, and the escape hatch when that isn't enough.

## The model

**Dart is single-threaded per isolate.** One thread, one event loop, no shared-memory concurrency, and therefore **no locks, no data races, no `synchronized`.**

```
    ┌──────────────────────────┐
    │      microtask queue     │  ← Futures. Drained FIRST, completely
    ├──────────────────────────┤
    │        event queue       │  ← I/O, timers, taps
    └──────────────────────────┘
              ↑ event loop
```

**Consequence:** async code is concurrent but not parallel. `await` yields to the loop; it never runs two Dart functions at the same instant.

**And the important consequence for Flutter: a long synchronous computation blocks the UI**, because rendering happens on the same loop. Dropped frames come from exactly this → [[languages/10-dart/README|isolates, below]].

## Futures and async/await

```dart
Future<User> fetchUser(String id) async {
  final response = await http.get(Uri.parse('$base/users/$id'));
  if (response.statusCode != 200) throw HttpException('${response.statusCode}');
  return User.fromJson(jsonDecode(response.body));
}

try {
  final user = await fetchUser('1');
} on HttpException catch (e) {
  handle(e);
} finally {
  cleanup();
}
```

**`on` catches a specific type; `catch` catches everything.** `catch (e, stackTrace)` gives you both.

## Parallel awaits

```dart
// Sequential — 2 round trips in series
final user = await fetchUser(id);
final posts = await fetchPosts(id);

// Concurrent
final results = await Future.wait([fetchUser(id), fetchPosts(id)]);
```

**`Future.wait` fails fast** — if one throws, it throws, and the others keep running unobserved. Pass `eagerError: false` or handle each individually if that matters.

## Streams

```dart
Stream<int> countTo(int n) async* {       // async* = a generator
  for (var i = 1; i <= n; i++) {
    await Future.delayed(const Duration(seconds: 1));
    yield i;
  }
}

await for (final n in countTo(3)) print(n);
```

**Two kinds, and the distinction causes real bugs:**

- **Single-subscription** (the default) — **can be listened to once.** Listening twice throws
- **Broadcast** (`.asBroadcastStream()`, `StreamController.broadcast()`) — many listeners

**Always cancel subscriptions.** In Flutter, cancel in `dispose()` — an uncancelled stream subscription is the most common Flutter memory leak.

```dart
StreamSubscription? _sub;
@override void dispose() { _sub?.cancel(); super.dispose(); }
```

**`StreamController`** when you need to push events manually. `rxdart` adds operators (`debounce`, `combineLatest`) if you want them.

## Isolates — the real parallelism

**An isolate has its own memory and its own event loop.** Nothing is shared; they communicate by **passing messages**, which are copied.

```dart
final result = await Isolate.run(() => expensiveComputation(data));   // Dart 2.19+
```

**`Isolate.run` is the modern, simple form** — it spawns, runs, returns and cleans up. The older `Isolate.spawn` with `SendPort`/`ReceivePort` is still there for long-lived workers.

**In Flutter, `compute()` is the same idea** with a friendlier name.

**When you need one:**
- Parsing a large JSON payload
- Image processing
- Cryptography
- Anything CPU-bound taking more than a frame's budget (~16ms)

**The cost:** messages are **copied**, so passing a large object has real overhead. For a big list, the copy can outweigh the computation. **Measure** — sometimes the answer is to send the raw bytes and parse in the isolate rather than sending the parsed result back.

**And note there's no shared mutable state at all**, which eliminates data races by construction — the same choice Erlang made, and it's why Dart has no concurrency primitives to learn.

## Common mistakes

```dart
// ❌ Not awaited — errors vanish, ordering is undefined
saveToDatabase(user);

// ✅
await saveToDatabase(user);
// or, deliberately fire-and-forget:
unawaited(saveToDatabase(user).catchError(log));
```

**An unawaited Future silently swallows its error.** The `unawaited_futures` lint catches this — **enable it.**

```dart
// ❌ Blocks the UI for a second
for (var i = 0; i < 1e9; i++) { }

// ✅ Isolate
await Isolate.run(() => heavyLoop());
```

**And `await` inside a loop is sequential** — use `Future.wait` over a mapped list when the iterations are independent.

## Key insight

**Dart chose message passing over shared memory, so concurrency bugs mostly don't exist** — no locks, no races, nothing to synchronise. The price is that parallelism requires copying data between isolates, and **anything CPU-bound on the main isolate freezes your UI.** Knowing which of your work is I/O-bound (use `async`) and which is CPU-bound (use an isolate) is the whole skill.

## Related
- [[languages/10-dart/03-classes-and-collections|collections]] — `Iterable` laziness is a related idea
- [[mobile/frameworks/flutter/README|Flutter]] — where blocking the loop is visible
- [[languages/09-kotlin/05-coroutines-and-flow|Kotlin coroutines]] — the comparison
- [[foundations/os/08-io-models|I/O models]] — event loops generally
