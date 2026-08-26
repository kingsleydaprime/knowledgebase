# When Not to Use C

**[Intermediate]** — The decision framework, argued properly, and the migration paths when the answer is "not this".

## The honest default

**For a new network service, C is the wrong choice.** Not because it's old or unfashionable, but for a specific and measurable reason:

> An HTTP server's parser is the most attacker-exposed code you will ever write, and C provides no mechanism to make it safe — only discipline, which does not survive deadlines or headcount.

The data: Microsoft reported that **~70% of the CVEs it assigns are memory-safety issues**. Google reported the same for Chrome, and later that Android's memory-safety vulnerabilities fell from 76% to 24% of the total as new code shifted to memory-safe languages. These aren't hypotheticals about careless programmers — they're the measured output of large teams of excellent C and C++ programmers over decades.

Every buffer overflow, use-after-free, and integer-overflow-into-heap-overflow in that dataset is a class of bug that **cannot occur** in [[languages/02-go/README|Go]], [[backend/frameworks/rust/README|Rust]], Java, or Python.

## What you actually gain

Being fair to the other side. C's genuine advantages for a server:

**No runtime, no GC, no VM.** Predictable latency with no pauses, minimal memory footprint, and instant startup.

**Total control over memory layout.** Matters for cache behaviour in genuinely hot paths.

**It runs anywhere.** Every platform has a C compiler.

**It embeds.** You can drop an HTTP server into an existing C program without a second process, a second runtime, or IPC.

Now compare against the alternatives:

| | C | Go | Rust |
|---|---|---|---|
| GC pauses | none | **small, tuneable** | none |
| Memory safety | **none** | guaranteed | guaranteed |
| Startup | instant | instant | instant |
| Binary | static | static | static |
| Memory footprint | smallest | small | small |
| Development speed | **slowest** | fastest | slow |
| Ecosystem for web | **minimal** | large | growing |

**Go's GC is the only real gap**, and modern Go's sub-millisecond pauses are irrelevant for the overwhelming majority of services. Rust closes even that.

So the honest summary: **you give up memory safety, development speed, and the entire web ecosystem, in exchange for a performance edge you probably can't measure and a memory footprint that rarely matters.**

## The cases where C is genuinely right

**1. Embedding in an existing C program.**

A device's configuration UI, a game engine's debug server, an instrument's control API, a database's admin endpoint. The process is already C for good reasons; adding libmicrohttpd beats adding a second process, an IPC layer, and a deployment unit.

> **This is the strongest case, and it's about the *process*, not about HTTP.** The question isn't "should I write a web server in C" — it's "should I add a second runtime to this program", and often the answer is no.

**2. Targets with no other toolchain.**

Small embedded systems, unusual architectures, or environments where only a C compiler is available. Shrinking every year as Rust's embedded support matures, and still real. → [[hardware/03-embedded-systems|Embedded Systems]]

**3. Learning.**

Writing an HTTP server from `socket()` up teaches you more about HTTP, TCP, and every runtime you'll ever use than any framework will. That's a genuinely good reason — for a project you don't deploy. → [[BUILD-PLAN|build-your-own-shit]]

**4. Extreme constraints, honestly assessed.**

Sub-millisecond p99 with a memory budget in single-digit megabytes. This is rarer than people claim, and it's usually a hardware or architecture problem rather than a language one.

## The cases where it isn't

**A new web service.** Use Go, Rust, or whatever your team knows.

**"It'll be faster."** Your bottleneck is the database, the network, or your algorithm. A Go service and a C service both spend 95% of a request waiting on I/O. Measure before believing this.

**"Fewer dependencies."** True, and you'll write those dependencies yourself — badly, in the most security-sensitive code in the system.

**"The team knows C."** Knowing C is not the same as knowing how to write a secure HTTP parser in C. Those are different skills, and the second is rare.

## If it's an existing native codebase

The most common real scenario, and there are three good options before "write it in C":

**1. Use [[backend/frameworks/cpp/README|C++]] instead.** If the codebase compiles as C++ or can link against it, Drogon or Crow give you RAII, `std::string`, real containers, a JSON layer, and coroutines. Most of [[backend/frameworks/c/02-parsing-http-safely|the parsing dangers]] become non-issues because `std::string` carries its length and destructors run on every path. **This is usually the right answer.**

**2. Put the network layer in another language and call C via FFI.** Rust or Go handles HTTP; your C library does the domain work behind a narrow, audited interface:

```rust
extern "C" { fn process_frame(data: *const u8, len: usize) -> i32; }

async fn handler(body: Bytes) -> Result<StatusCode, AppError> {
    let rc = unsafe { process_frame(body.as_ptr(), body.len()) };   // audited boundary
    ...
}
```

The attacker-facing parsing is memory-safe; the C is reached only through one function with validated inputs. → [[languages/03-rust/15-unsafe-and-ffi|Rust: FFI]]

**3. A reverse proxy in front.** nginx terminates TLS, enforces limits, and rejects malformed requests, so your C service sees a much narrower input range. **This is the highest-value single mitigation available** and you should do it regardless of what else you choose.

## The Rust argument specifically

For the case where C looked right — no GC, minimal footprint, systems-level — [[backend/frameworks/rust/README|Rust]] is the direct replacement:

- Same performance class, no runtime, static binary
- Memory safety **enforced at compile time**
- A real ecosystem for web work — Axum, sqlx, serde
- `serde` alone removes the by-hand JSON marshalling that dominates C web code

The costs are real: a steep learning curve, slow compiles, and immature libraries in some domains. But the specific trade C offers — manual memory management on an attacker-facing surface — is one Rust simply doesn't ask you to make.

This is why the industry is moving: the Linux kernel, Android, Windows components, and most new infrastructure. Not fashion — the CVE numbers.

## Migration, if you have C already

You rarely rewrite. The incremental path:

1. **Reverse proxy in front.** Immediate, no code change
2. **Replace the parser with llhttp.** One well-audited component instead of yours
3. **New endpoints in a new language**, routed by the proxy. The strangler-fig pattern → [[architecture/03-architectural-patterns/03-data-and-integration-patterns|integration patterns]]
4. **Keep the C as a library**, called via FFI from the new service
5. **Harden what remains**: sanitizers in CI, fuzzing, `-D_FORTIFY_SOURCE=2`, privilege separation

Steps 1 and 2 are cheap and remove most of the exposure. Do those first regardless of any longer-term plan.

## The summary

> **Write an HTTP server in C to understand how they work. Ship one when the process is already C and adding a runtime is worse than adding a parser. Choose anything else for anything new.**
>
> And whichever you choose, put a reverse proxy in front of it.

---

## Related
- [[backend/frameworks/c/03-the-c-frameworks|The C Frameworks]] — the options, if the answer is yes
- [[backend/frameworks/c/02-parsing-http-safely|Parsing HTTP Safely]] — the risk, concretely
- [[backend/frameworks/rust/README|Rust backends]] — the direct replacement
- [[backend/frameworks/cpp/README|C++ backends]] — the answer for an existing native codebase
- [[cybersecurity/06-attacks-and-threats/04-password-malware-and-exploits|Exploits]] — where the CVE numbers come from
- [[backend/frameworks/c/README|C backends]]
