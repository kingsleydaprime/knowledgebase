# Goroutines and Channels

**[Intermediate]** — The feature Go is actually famous for: concurrency as a language primitive rather than a library, and the ways it goes wrong.

## Goroutines

```go
go doWork()                          // that's it
go func() { fmt.Println("hi") }()    // anonymous
```

A goroutine is a function running concurrently, scheduled by the Go runtime onto OS threads. It starts at about **2KB of stack** which grows as needed — versus roughly 1MB for an OS thread. Hundreds of thousands of goroutines is normal; hundreds of thousands of threads is not.

This is the **green threads / M:N** model: many goroutines multiplexed onto few OS threads. → [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]]

The consequence for how you write code: **you write blocking code and it scales anyway.** There is no `async`/`await`, so there's no function colouring — no split between async and sync versions of every library. When a goroutine blocks on I/O, the scheduler parks it and runs another on that thread. Java only got here with virtual threads in 21; Node never did.

### Three things that bite immediately

**`main` returning kills everything.** Goroutines are not joined automatically:

```go
func main() {
    go fmt.Println("never printed")
    // main returns; process exits
}
```

**Goroutines leak, and nothing tells you.** A goroutine blocked forever on a channel is never collected. Unbounded spawning — one per request, per file, per loop iteration, with no bound and no exit path — is *the* characteristic Go bug.

> **Every goroutine you start needs a known way to stop.** If you can't say what makes it exit, you've written a leak.

**A panic in any goroutine kills the whole process.** `recover` in the parent does not help. Anything spawned needs its own recovery if a panic there shouldn't be fatal. → [[languages/02-go/05-errors|Errors]]

## Channels

> *"Don't communicate by sharing memory; share memory by communicating."*

```go
ch := make(chan int)        // unbuffered
ch := make(chan int, 10)    // buffered, capacity 10

ch <- 42        // send
v := <-ch       // receive
close(ch)
```

**Unbuffered channels are a rendezvous.** A send blocks until a receiver is ready, and vice versa. That's a synchronisation point, not just a queue — the two goroutines meet.

**Buffered channels** let the sender continue until the buffer fills. Use them when you deliberately want slack between producer and consumer; the capacity is a backpressure decision, not a performance tweak.

### Closing and ranging

```go
close(ch)               // sender closes; NEVER the receiver
v, ok := <-ch           // ok is false once drained and closed
for v := range ch { }   // loops until the channel is closed
```

Rules that matter:

- **Only the sender closes.** A receiver closing causes a send on a closed channel → panic.
- **Sending on a closed channel panics.** Receiving from one returns zero values forever.
- **Closing twice panics.**
- Closing is a *broadcast*: every receiver unblocks. That's why a `chan struct{}` closed as a signal is the idiomatic "stop everyone" primitive.

```go
done := make(chan struct{})
go worker(done)
close(done)   // every goroutine selecting on <-done wakes up
```

You don't have to close a channel that's simply garbage collected. Close to signal "no more values are coming", not for cleanup.

### Direction types

```go
func produce(out chan<- int)  // send-only
func consume(in <-chan int)   // receive-only
```

Restricting direction in a parameter is a compile-time guarantee about what a function can do, and it documents intent better than a comment. Use it.

## `select`

```go
select {
case v := <-ch1:
    fmt.Println("from ch1:", v)
case ch2 <- 42:
    fmt.Println("sent to ch2")
case <-time.After(time.Second):
    fmt.Println("timeout")
default:
    fmt.Println("nothing ready")   // makes the whole select non-blocking
}
```

`select` blocks until one case can proceed. If several are ready, it picks **randomly** — deliberately, to prevent starvation.

Two idioms carry most of the weight:

**Timeout:**
```go
select {
case res := <-resultCh:
    return res, nil
case <-time.After(2 * time.Second):
    return nil, errors.New("timed out")
}
```

**Cancellation** — the pattern that becomes `context`:
```go
for {
    select {
    case <-done:
        return
    case job := <-jobs:
        process(job)
    }
}
```

A `select` with only a `default` and nothing ready is a busy loop. If you find yourself spinning, you want a blocking receive.

## Deadlocks

```go
func main() {
    ch := make(chan int)
    ch <- 1     // fatal error: all goroutines are asleep - deadlock!
}
```

An unbuffered send with no receiver blocks forever. The runtime detects the case where *every* goroutine is blocked and panics with a useful message — but it cannot detect a partial deadlock where one goroutine hangs while others run. Those show up as a request that never returns.

```bash
kill -QUIT <pid>      # dump every goroutine's stack
```

`GOTRACEBACK=all` and the `/debug/pprof/goroutine?debug=2` endpoint do the same thing on a live server, and a goroutine count that only ever climbs is the signature of a leak. → [[languages/02-go/13-performance-and-runtime|Performance and the Runtime]]

## When *not* to use a channel

Channels are the famous feature, so they get over-applied. For plain shared state, a mutex is simpler, faster, and easier to read:

```go
type Counter struct {
    mu sync.Mutex
    n  int
}
func (c *Counter) Inc() { c.mu.Lock(); c.n++; c.mu.Unlock() }
```

The Go team's own guidance: **use channels for passing ownership of data and for coordination; use mutexes for protecting state.** A channel-based counter is a party trick. → [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]]

---

## Related
- [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]] — `sync`, worker pools, and the race detector
- [[languages/02-go/08-context|Context]] — cancellation done properly
- [[languages/01-java/02-jvm-and-concurrency/README|Java: JVM & Concurrency]] — threads, and virtual threads arriving at the same place
- [[foundations/os/README|Operating Systems]] — what the runtime is scheduling onto
- [[languages/02-go/README|Go course map]]
