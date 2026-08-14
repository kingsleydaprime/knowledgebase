# C Backends — scaffold

No course written yet. The shape, for when there is one:

**Concurrency model: whatever you build.** C has no runtime, so the model is a design decision rather than a language feature — a thread per connection, a process per connection (the old CGI/Apache model), or a single-threaded event loop over `epoll`/`kqueue`. Nearly every modern C server is the third. → [[backend/01-foundations/04-runtime-and-concurrency-models|runtime models]]

That's the interesting thing about C here: it's the layer the *other* models are implemented in. Node's event loop, Go's scheduler and Tokio's reactor are all `epoll` loops written in C or Rust. → [[foundations/networking/09-sockets-and-the-network-api|sockets]]

| Option | Character |
|---|---|
| **libmicrohttpd** | GNU, small, embeddable; the usual choice for adding HTTP to an existing C program |
| **Kore** | a full framework — TLS, routing, WebSockets, privilege separation. Opinionated and security-focused |
| **Ulfius** | REST-oriented, with JSON and WebSocket support |
| **civetweb / mongoose** | tiny, embeddable, popular in firmware and desktop apps |
| **raw `socket()` + `epoll`** | writing one yourself — planned as a guide in [[BUILD-PLAN\|build-your-own-x/]] |

## The honest question: should you?

Usually no. For an ordinary web service, C gives you the same [[languages/04-c/07-memory-management|memory-safety exposure]] on the most attacker-facing surface you have, in exchange for performance you'd also get from [[languages/02-go/README|Go]] or [[languages/03-rust/README|Rust]]. Parsing untrusted input in C is precisely where the CVEs come from.

The cases where it's a real answer:
- **Embedding HTTP in an existing C codebase** — firmware, a device's config UI, a game engine's debug server
- **Extremely constrained targets** where no other toolchain exists
- **Learning** — writing an HTTP server from `socket()` up teaches you more about HTTP than any framework will

## The things to know
- **You are writing the accept loop.** `socket` → `bind` → `listen` → `accept`, then `epoll` (Linux) or `kqueue` (BSD) for readiness. → [[foundations/networking/09-sockets-and-the-network-api|Sockets]]
- **Parsing is where the bugs are.** Every request line, header and body length is attacker-controlled. Use a battle-tested parser (`llhttp`, `picohttpparser`) rather than writing one for production, and [[languages/04-c/13-debugging-and-tooling|fuzz it]] if you do.
- **No string type** means every buffer needs an explicit length and bound. → [[languages/04-c/06-arrays-strings-and-decay|Arrays, Strings and Decay]]
- **Lifetimes across an event loop are the hard part** — a connection's buffers must outlive the callback that queued them, and there's no ownership system to help.

## Related
- [[backend/frameworks/README|frameworks/]] · [[languages/04-c/README|the C course]]
- [[foundations/networking/09-sockets-and-the-network-api|Sockets and the Network API]]
