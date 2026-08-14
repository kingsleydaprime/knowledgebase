# Performance and the Runtime

**[Advanced]** — The scheduler, escape analysis, the garbage collector, and pprof — the tool that turns performance work from guessing into reading.

## The scheduler (G-M-P)

Go's runtime multiplexes goroutines onto OS threads with three entities:

- **G** — a goroutine
- **M** — an OS thread (machine)
- **P** — a processor: a scheduling context holding a run queue. `GOMAXPROCS` sets how many exist, defaulting to `NumCPU()`

An M must hold a P to run Gs. Each P has a local run queue, with a global queue as overflow, and an idle P **steals work** from a busy one — which is what keeps cores fed without central coordination.

Two behaviours worth knowing:

**Blocking syscalls detach the M.** When a goroutine makes a blocking syscall, the M blocks with it, but the P is handed to another M so the other goroutines on that P keep running. This is why blocking file I/O doesn't stall your server the way it would in Node.

**The scheduler is preemptive since 1.14.** Before that a tight loop with no function calls could hog a P forever; now the runtime can interrupt via signals. You'll still see this described as cooperative in older material.

`GOMAXPROCS` in a container is the trap: the runtime reads the **host's** CPU count, not the cgroup limit. A 2-CPU container on a 64-core host gets 64 Ps, which causes heavy context switching and throttling. Use `automaxprocs`, or set it explicitly:

```go
import _ "go.uber.org/automaxprocs"    // reads the cgroup quota
```

This is one of the most common Go-in-Kubernetes performance bugs. → [[devops/05-orchestration/README|Orchestration]]

## Escape analysis

The compiler decides at build time whether a value lives on the stack or the heap. Stack allocation is nearly free and needs no GC; heap allocation costs both.

```bash
go build -gcflags="-m" ./...       # what escapes, and why
go build -gcflags="-m -m" ./...    # more detail
```

```
./main.go:12:6: can inline process
./main.go:15:2: moved to heap: buf
./main.go:20:9: &User{...} escapes to heap
```

The common causes of escape:

- **Returning a pointer to a local** — it must outlive the frame
- **Storing a pointer in an interface** — `fmt.Println(x)` boxes `x`, which is why logging in a hot loop allocates
- **Sending a pointer on a channel**
- **Closures capturing by reference**
- **A slice whose size isn't known at compile time**

Note `&User{}` does *not* automatically mean heap — if it doesn't escape the function, it's a stack allocation. Go's `new` vs `&` distinction is cosmetic; escape analysis decides.

## The garbage collector

A **concurrent, tri-colour mark-and-sweep** collector, tuned hard for low latency over throughput. Sub-millisecond pauses are typical, because marking runs concurrently with your program and only two brief stop-the-world phases remain.

There is **no generational collection** and no compaction — unusual, and a deliberate trade. It means no object relocation, so pointers stay stable, but also that fragmentation is possible and allocation-heavy code pays more than it would on the JVM.

```bash
GOGC=100      # default: collect when the heap doubles since the last GC
GOGC=400      # collect less often; more memory, less CPU
GOGC=off      # with GOMEMLIMIT set, for latency-critical services
GOMEMLIMIT=4GiB   # soft memory ceiling (1.19+)
```

`GOMEMLIMIT` is the important modern knob. Before it, a container with a hard memory limit could be OOM-killed because the GC hadn't decided to run yet. Setting a soft limit slightly below the container limit makes the GC work harder as you approach it, instead of dying.

**The way to make GC cheaper is to allocate less**, not to tune the GC. In order of impact:

```go
out := make([]T, 0, len(in))     // 1. preallocate — biggest easy win
var sb strings.Builder           // 2. don't build strings with +=
buf := pool.Get().(*bytes.Buffer)  // 3. sync.Pool, for genuinely hot paths
```

`sync.Pool` is a free-list for temporary objects, cleared on every GC cycle. It helps in hot paths and adds complexity everywhere else — measure before reaching for it.

## pprof

The reason performance work in Go is pleasant. Import the handler:

```go
import _ "net/http/pprof"          // registers on http.DefaultServeMux

go func() { log.Println(http.ListenAndServe("localhost:6060", nil)) }()
```

> Bind to **localhost** or a separate admin port. `/debug/pprof` on a public interface is a real information leak.

```bash
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30   # CPU
go tool pprof http://localhost:6060/debug/pprof/heap                 # memory
go tool pprof http://localhost:6060/debug/pprof/goroutine            # goroutine count
go tool pprof http://localhost:6060/debug/pprof/mutex                # lock contention
go tool pprof http://localhost:6060/debug/pprof/block                # blocking ops
```

Inside the tool:

```
(pprof) top10          # hottest functions by self time
(pprof) top -cum       # by cumulative time — usually more useful
(pprof) list funcName  # line-by-line cost within a function
(pprof) web            # SVG call graph (needs graphviz)
```

Or straight to a browser flame graph:

```bash
go tool pprof -http=:8081 http://localhost:6060/debug/pprof/profile?seconds=30
```

From benchmarks instead of a live server:

```bash
go test -bench=. -cpuprofile=cpu.out -memprofile=mem.out
go tool pprof -http=:8081 cpu.out
```

**`goroutine` is the profile to check first for a mysterious problem.** A count that only climbs is a goroutine leak, and `?debug=2` prints every stack so you can see exactly where they're stuck. That single endpoint diagnoses most Go production incidents.

For memory, `-alloc_space` shows total allocated (what pressures the GC) while `-inuse_space` shows what's currently live (what leaks). They answer different questions and people conflate them constantly.

## The execution tracer

When pprof says the CPU is idle but throughput is bad:

```bash
go test -trace=trace.out
go tool trace trace.out
```

This shows per-goroutine timelines, scheduler latency, GC events, and syscall blocking. It's the tool for "why is this waiting" rather than "what is this burning" — contention, starvation, and serialisation through a mutex all show up here and nowhere else.

## Rules of thumb

1. **Measure first.** Go's compiler and GC are good; intuition about hot spots is usually wrong.
2. **Allocations are the usual answer.** `-benchmem` and the `allocs/op` column point at it more often than CPU profiles do.
3. **Preallocate slices and maps** when you know the size.
4. **Don't use `sync.Pool` speculatively.**
5. **Prefer `[]byte` over `string`** in hot paths to avoid conversions.
6. **Set `GOMEMLIMIT` and fix `GOMAXPROCS` in containers.** These two config lines beat most code optimisation.
7. **A goroutine leak looks like a memory leak.** Check the goroutine profile before the heap profile.

---

## Related
- [[languages/02-go/11-testing-and-benchmarking|Testing and Benchmarking]] — where the numbers come from
- [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]] — the leaks pprof finds
- [[languages/01-java/02-jvm-and-concurrency/README|Java: JVM & Concurrency]] — generational GC, the road Go didn't take
- [[devops/10-observability/README|Observability]] — profiling as a production practice
- [[languages/02-go/README|Go course map]]
