# Go

A small language that made a deliberate trade: less expressiveness, in exchange for code a stranger can read at 3am during an incident. Whether that trade is worth it is the only interesting argument about Go, and you can't have it honestly until you've written some.

**~14,000 words across 13 notes.** Built August 2026, cross-referenced against [roadmap.sh Go](https://roadmap.sh/golang).

**Source: `[reference]`.** There is no Go project in this vault yet, and this domain is honest about that — nothing here has been argued with under real constraints. The first Go build belongs in [[project-ideas|Project Ideas]] before these notes claim to be knowledge. The vault's own rule: [[PRIMETECHIE|reading is not a rank]].

> **The one idea to take away:** Go's concurrency isn't just "goroutines are cheap." It's that **you write blocking code and it scales anyway** — no `async`/`await`, so no split between async and sync versions of every library. Java needed until version 21 to get here; Node never did. Almost everything else about Go is a cost paid for that, plus fast builds.

## Reading order

**The language**

1. [[languages/02-go/01-why-go-and-the-toolchain|Why Go, and the Toolchain]] — **[Beginner]** — the four design goals everything follows from, the deliberate omissions, and the single tool that replaces your whole build stack
2. [[languages/02-go/02-language-fundamentals|Language Fundamentals]] — **[Beginner]** — declarations, zero values, a stricter type system than you expect, multiple returns, `defer`, and the three control structures
3. [[languages/02-go/03-composite-types|Composite Types]] — **[Beginner → Intermediate]** — arrays, maps, structs, and **slices**, whose aliasing behaviour is the most common source of real Go bugs
4. [[languages/02-go/04-methods-and-interfaces|Methods and Interfaces]] — **[Intermediate]** — receivers, implicit satisfaction, why interfaces are declared by the *consumer*, and the nil-interface trap

**Getting things wrong safely**

5. [[languages/02-go/05-errors|Errors]] — **[Intermediate]** — errors as values, `%w` wrapping, `errors.Is`/`As`, sentinel vs typed, and the narrow legitimate use of `panic`

**Concurrency — the reason people choose Go**

6. [[languages/02-go/06-goroutines-and-channels|Goroutines and Channels]] — **[Intermediate]** — the primitives, closing rules, `select`, deadlocks, and when *not* to use a channel
7. [[languages/02-go/07-concurrency-patterns|Concurrency Patterns]] — **[Intermediate → Advanced]** — `sync`, worker pools, fan-in/out, pipelines, `errgroup`, and the race detector
8. [[languages/02-go/08-context|Context]] — **[Intermediate]** — cancellation and deadlines propagated across every API boundary, and the rules that stop it becoming a junk drawer

**The rest of the language**

9. [[languages/02-go/09-generics|Generics]] — **[Intermediate]** — type parameters, `~` and unions, and the honest answer to when you should use them (less often than you think)
10. [[languages/02-go/10-the-standard-library|The Standard Library]] — **[Intermediate]** — `io`, `net/http`, `encoding/json`, `time`, `slog`, and why the stdlib being sufficient is a cultural fact

**Working with it**

11. [[languages/02-go/11-testing-and-benchmarking|Testing and Benchmarking]] — **[Intermediate]** — table-driven tests, test doubles without a mocking framework, benchmarks that don't lie, and fuzzing
12. [[languages/02-go/12-modules-and-project-layout|Modules and Project Layout]] — **[Intermediate]** — `go.mod`, minimal version selection, and the layout argument (`pkg/` is not official)
13. [[languages/02-go/13-performance-and-runtime|Performance and the Runtime]] — **[Advanced]** — the G-M-P scheduler, escape analysis, the GC, and pprof

## Where the frameworks are

Following [[languages/README|the vault rule]] — `languages/` teaches the language, `backend/frameworks/` teaches the frameworks:

### → **[[backend/frameworks/go/README|backend/frameworks/go/]]** — `net/http`, Chi, Gin

The stdlib case is unusually strong in Go. `net/http` is a production HTTP server, not a toy you replace, and Go 1.22's method-aware routing removed most of the remaining reason to pull in a router at all. Note 10 covers enough `net/http` to build a real service; the frameworks section covers what a router adds and when it's worth it.

## Reading Go you didn't write

The vault's own infrastructure is largely Go — Docker, Kubernetes, Terraform, Prometheus, and the [[git/15-the-github-cli|`gh` CLI]] are all written in it. That makes it unusually easy to learn from real code:

```bash
go doc net/http.Server           # docs in the terminal
go doc -src net/http.ListenAndServe   # the actual source
```

The standard library source is famously readable and is the best available Go style guide.

## Known gaps

- **No project.** The largest gap, and the one that matters. Everything here is `[reference]`
- **CGo** is absent — the FFI boundary, and the reasons "cgo is not Go"
- **Reflection** (`reflect`) is only mentioned via struct tags, not explained
- **Assembly and `unsafe`** — deliberately out of scope
- **gRPC and protobuf**, which is where a lot of real Go service code lives

---

## Related
- [[backend/frameworks/go/README|Go Backends]] — the frameworks
- [[languages/README|Languages]] — the language/framework split rule
- [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — goroutines among the alternatives
- [[languages/01-java/README|Java]] — the other language course here, and a useful contrast on nearly every decision
- [[project-ideas|Project Ideas]] — where the first Go build should be logged
