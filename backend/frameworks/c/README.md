# C Backends

**Concurrency model: whatever you build.** C has no runtime, so the model is a design decision rather than a language feature — a process per connection (the old CGI/Apache model), a thread per connection, a thread pool, or a single-threaded event loop over `epoll`/`kqueue`. Nearly every modern C server is the last. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

**~8,000 words across 4 notes.** `[reference]`. Assumes [[languages/04-c/README|the C course]].

> **The interesting thing about C here: it's the layer the *other* models are implemented in.** Node's event loop, Go's netpoller and tokio's reactor are all `epoll` loops. Writing one makes every runtime you use afterwards unmysterious — and explains exactly why blocking inside an async handler is catastrophic.

## Reading order

1. [[backend/frameworks/c/01-the-accept-loop-and-event-loops|The Accept Loop and Event Loops]] — **[Advanced]** — `socket`/`bind`/`listen`/`accept`, the four concurrency strategies, `epoll`, edge vs level triggering, and why partial writes force a per-connection state machine
2. [[backend/frameworks/c/02-parsing-http-safely|Parsing HTTP Safely]] — **[Advanced]** — every byte is attacker-controlled and C has no bounds checking. **The note that matters most**
3. [[backend/frameworks/c/03-the-c-frameworks|The C Frameworks]] — **[Intermediate]** — libmicrohttpd, Kore, civetweb, Ulfius: what each is for
4. [[backend/frameworks/c/04-when-not-to-use-c|When Not to Use C]] — **[Intermediate]** — the decision framework, and the migration paths

## The honest question: should you?

**Usually no.** For a new network service C is the wrong choice, for a specific measurable reason: an HTTP parser is the most attacker-exposed code you will ever write, and C offers no mechanism to make it safe — only discipline, which doesn't survive deadlines.

Microsoft and Google both report **~70% of their CVEs are memory-safety bugs**, and Android's fell from 76% to 24% as new code moved to memory-safe languages. That's not careless programmers; it's the measured output of excellent ones over decades.

The cases where it's a real answer:
- **Embedding HTTP in an existing C codebase** — firmware, a device's config UI, a game engine's debug server. The strongest case, and it's about avoiding a second runtime rather than about HTTP
- **Extremely constrained targets** where no other toolchain exists
- **Learning** — writing one from `socket()` up teaches you more than any framework will → [[BUILD-PLAN|build-your-own-x]]

If the reason is an existing native codebase, look at [[backend/frameworks/cpp/README|C++]] first — RAII, `std::string` and a real JSON layer remove most of note 02's difficulty.

## The options

| Option | Character |
|---|---|
| **libmicrohttpd** | GNU, small, embeddable; the usual choice for adding HTTP to an existing C program |
| **Kore** | a full framework — TLS, routing, WebSockets, **privilege separation**. Opinionated and security-focused |
| **Ulfius** | REST-oriented, with JSON and WebSocket support |
| **civetweb / mongoose** | tiny, embeddable, popular in firmware and desktop apps |
| **raw `socket()` + `epoll`** | writing one yourself — note 01 |

## The things to know

- **You are writing the accept loop.** `socket` → `bind` → `listen` → `accept`, then `epoll` (Linux) or `kqueue` (BSD) for readiness → note 01
- **Parsing is where the bugs are.** Use `llhttp` or `picohttpparser` rather than writing one for production, and [[languages/04-c/13-debugging-and-tooling|fuzz it]] if you do → note 02
- **No string type** means every buffer needs an explicit length and bound → [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]]
- **Lifetimes across an event loop are the hard part** — a connection's buffers must outlive the callback that queued them, and there's no ownership system to help
- **`SIGPIPE` will kill your process** when a client disconnects mid-write, unless you ignore it

## If you ship it

1. **Use llhttp or picohttpparser** — don't ship your own parser
2. **Bound every buffer**, cap every limit
3. **Compile hardened**: `-D_FORTIFY_SOURCE=2 -fstack-protector-strong -fPIE -pie -Wl,-z,relro,-z,now`
4. **Fuzz the parser**; run tests under ASan and UBSan in CI
5. **Drop privileges after `bind()`**; `chroot` and `seccomp` if you can
6. **Put a reverse proxy in front** — the highest-value single mitigation available

## Related
- [[backend/frameworks/README|frameworks/]] · [[languages/04-c/README|the C course]]
- [[foundations/networking/09-sockets-and-the-network-api|Sockets and the Network API]]
- [[backend/frameworks/rust/README|Rust backends]] — the direct replacement
- [[cybersecurity/04-web-security/README|Web Security]]
