---
id: 920b8ab0-d6cb-49dd-b3cb-320f5f58c135
---

# Concurrency Patterns

**[Intermediate → Advanced]** — The `sync` package, the four patterns that cover most real concurrent code, and the race detector you should be running already.

## `sync`
<!-- bite: 9210296d-8f5f-49ef-8961-27e8f04d7451 -->

```go
var mu sync.Mutex
mu.Lock()
defer mu.Unlock()
// critical section
```

`sync.RWMutex` allows many concurrent readers or one writer — worth it only when reads genuinely dominate, since it's slower than a plain `Mutex` under contention.

**Never copy a struct containing a mutex.** Once a type has a mutex field, all its methods need pointer receivers. `go vet` catches this.

```go
var wg sync.WaitGroup
for _, url := range urls {
    wg.Add(1)                     // BEFORE the go statement, always
    go func() {
        defer wg.Done()           // defer, so a panic still decrements
        fetch(url)
    }()
}
wg.Wait()
```

`wg.Add` inside the goroutine is a race — `Wait` may return before the goroutine has started.

```go
var once sync.Once
once.Do(func() { conn = connect() })   // runs exactly once, even under concurrency
```

`sync.Once` is the correct lazy singleton. It's also the right answer to "how do I close this channel exactly once from several places".

`sync/atomic` for single values, cheaper than a mutex:

```go
var count atomic.Int64      // Go 1.19+ typed atomics
count.Add(1)
count.Load()
```

## Pattern 1 — worker pool
<!-- bite: 66a43798-4aa0-4c6e-a8a6-d502b519e428 -->

The most useful one, and the fix for unbounded goroutine spawning:

```go
func workerPool(jobs []Job, n int) []Result {
    jobCh := make(chan Job)
    resCh := make(chan Result, len(jobs))
    var wg sync.WaitGroup

    for range n {                    // Go 1.22+ range-over-int
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := range jobCh {   // exits when jobCh closes
                resCh <- process(j)
            }
        }()
    }

    for _, j := range jobs { jobCh <- j }
    close(jobCh)                     // tells workers to finish
    wg.Wait()
    close(resCh)

    var out []Result
    for r := range resCh { out = append(out, r) }
    return out
}
```

The shape to internalise: **N goroutines ranging over one shared channel**, closed by the producer. Work distributes itself — a worker that finishes early takes the next job — so no manual partitioning.

`n` is your concurrency limit. Picking it: CPU-bound work → `runtime.NumCPU()`; I/O-bound → higher, bounded by what the downstream can take. An unbounded pool is a denial-of-service attack on your own database.

## Pattern 2 — fan-out / fan-in
<!-- bite: 5f86d114-970c-40b1-99e1-7026c327d9fa -->

```go
func merge(chans ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    for _, c := range chans {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c { out <- v }
        }(c)
    }
    go func() { wg.Wait(); close(out) }()   // close after all senders finish
    return out
}
```

The `go func(){ wg.Wait(); close(out) }()` idiom is how you close a channel with multiple senders — no single sender knows when to close, so a coordinator does it.

## Pattern 3 — pipeline
<!-- bite: bf54aaa8-5d63-4a6b-82eb-bc68469d8719 -->

Stages connected by channels, each stage a goroutine:

```go
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() { defer close(out); for _, n := range nums { out <- n } }()
    return out
}

func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() { defer close(out); for n := range in { out <- n * n } }()
    return out
}

for v := range sq(sq(gen(1, 2, 3))) { fmt.Println(v) }
```

Each stage closes its own output when its input closes, so closure propagates down the pipeline naturally.

The catch: if a consumer stops early, upstream stages block forever on send and leak. Real pipelines take a `done` channel or a `context` in every stage. → [[languages/02-go/08-context|Context]]

## Pattern 4 — `errgroup`
<!-- bite: bf224951-06cf-4c56-8e30-d11644b3e39f -->

The one you'll actually reach for. From `golang.org/x/sync/errgroup`:

```go
g, ctx := errgroup.WithContext(ctx)
g.SetLimit(10)                       // bounded concurrency, built in

for _, url := range urls {
    g.Go(func() error {
        return fetch(ctx, url)       // first error cancels ctx for everyone
    })
}
if err := g.Wait(); err != nil {
    return fmt.Errorf("fetching: %w", err)
}
```

This is `WaitGroup` + error propagation + cancellation in one type. `WithContext` cancels the shared context on the first non-nil error, so siblings stop instead of finishing pointless work. `SetLimit` makes it a worker pool without writing one.

Not in the standard library, but effectively standard.

## The race detector
<!-- bite: 8214778b-8725-4840-8b65-124b6f62828d -->

```bash
go test -race ./...
go run -race .
go build -race
```

**Run this.** It instruments memory access and reports concurrent unsynchronised access with both stack traces:

```
WARNING: DATA RACE
Write at 0x00c000018098 by goroutine 7:
  main.main.func1()
Previous read at 0x00c000018098 by main goroutine:
  main.main()
```

It's a **dynamic** detector — it only finds races on code paths that actually execute, so it needs decent test coverage to be useful. It costs ~10x CPU and ~5x memory, so it's a CI and local-test tool, not a production one. Wire it into the test job in [[devops/05-ci-cd/08-ci-pipelines|your CI pipeline]].

Go's memory model is explicit that a data race is undefined behaviour, not merely "a stale read". Anything unsynchronised is a bug even if it appears to work.

## Choosing between them
<!-- bite: c488fb36-2d5a-40a4-95b1-46129673df35 -->

| Situation | Use |
|---|---|
| Protecting shared state | `sync.Mutex` |
| One-off lazy initialisation | `sync.Once` |
| A counter | `sync/atomic` |
| Wait for N things, collect errors | `errgroup` |
| Bounded parallel work over a list | worker pool, or `errgroup.SetLimit` |
| Passing ownership of data between stages | channels |
| Cancellation and deadlines | `context` |

The failure mode to avoid is reaching for channels because they're the interesting feature. Most concurrent Go is a mutex and an `errgroup`.

---

## Related
<!-- bite: 2caabf3a-47ea-4689-a77d-16cf88f24afb -->
- [[languages/02-go/06-goroutines-and-channels|Goroutines and Channels]] — the primitives underneath
- [[languages/02-go/08-context|Context]] — the cancellation these patterns thread through
- [[languages/02-go/11-testing-and-benchmarking|Testing]] — where `-race` lives
- [[languages/01-java/02-jvm-and-concurrency/02-concurrency|Java: Concurrency]] — executors and the same patterns with threads
- [[languages/02-go/index|Go course map]]
