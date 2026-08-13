# Sockets & the Network API

**[Intermediate]** — where all the theory becomes code you actually write. The socket API is from 1983 (BSD 4.2) and has barely changed, which means it's the single most portable interface in computing — and also that it carries forty years of assumptions that no longer hold.

## The kid version first

A socket is a **phone**. The API is the sequence of things you do with a phone:

- **Server:** get a phone (`socket`), get a number assigned (`bind`), turn the ringer on (`listen`), pick up when it rings (`accept`).
- **Client:** get a phone (`socket`), dial (`connect`).
- **Both:** talk (`write`), listen (`read`), hang up (`close`).

The one thing that surprises people: when the server picks up (`accept`), it gets a **new phone** for that conversation. The original phone keeps ringing for everyone else. That's why a server has one listening socket and thousands of connected ones.

## The two sequences

```
SERVER                          CLIENT
socket()                        socket()
bind(addr, port)                
listen(backlog)                 
accept()  ──── blocks ────►     connect(addr, port)   ← the 3-way handshake
   │ returns a NEW fd                │
read()/write()   ◄───────────►  write()/read()
close()                         close()
```

Two things worth pinning down, because they're the source of a lot of confusion:

- **`accept()` returns a different file descriptor.** The listening socket is identified by `(local IP, local port)`; each accepted socket by the full [[foundations/networking/05-udp-and-ports|4-tuple]]. That's how the kernel routes incoming packets to the right connection.
- **`connect()` blocks for a full round trip** — it's performing the [[foundations/networking/06-tcp-connection-lifecycle|handshake]]. In an async runtime, this is the call that must never happen on your event loop thread.

**"Everything is a file"** is doing real work here: a socket is a file descriptor, so `read`/`write`/`close`/`select` all work on it, and so do pipes and files. This is why Unix's I/O model composes so well, and it links directly to [[foundations/os/fundamentals|OS fundamentals]].

## The socket options you will actually need

Most socket options are trivia. These five are not:

- **`SO_REUSEADDR`** — allows binding to a port still in `TIME_WAIT` from a previous process. **This is why your server can't restart immediately** with "address already in use," and setting it is standard practice for any server you'll restart. It does *not* let two live processes share a port.
- **`SO_REUSEPORT`** (Linux 3.9+) — genuinely lets **multiple processes bind the same port**, with the kernel load-balancing incoming connections across them. This is how modern multi-process servers (nginx workers, Go/Rust servers, Node's `cluster`) scale across cores without a single accepting thread becoming the bottleneck. It also enables zero-downtime restarts: start the new process, let it bind alongside the old one, drain the old one.
- **`TCP_NODELAY`** — disables [[foundations/networking/07-tcp-reliability-and-flow-control|Nagle's algorithm]]. Set by virtually every RPC framework and database driver, for the 40ms-stall reason.
- **`SO_KEEPALIVE`** + `TCP_KEEPIDLE`/`KEEPINTVL`/`KEEPCNT` — detect dead peers. Defaults (2 hours) are useless; if you use it, tune it.
- **`SO_LINGER`** — controls what `close()` does with unsent data. Setting it to 0 makes close send a **RST** instead of a FIN, skipping `TIME_WAIT`. Occasionally the right call for a proxy under extreme connection churn; usually a footgun that discards data in flight.

## Blocking, non-blocking, and the C10K problem

This is the part that shapes every server architecture you'll ever work with.

**Blocking I/O:** `read()` sleeps until data arrives. Beautifully simple — the code reads top to bottom. But one thread can serve one connection, so 10,000 connections need 10,000 threads. Each thread costs ~1 MB of stack plus scheduler pressure and context-switch overhead. This is the **C10K problem**: the cost is per-*connection*, but most connections are idle most of the time, so you're paying for concurrency you aren't using.

**Non-blocking + readiness notification:** set sockets non-blocking, and ask the kernel *"which of these thousands of sockets have something to do right now?"* One thread then services only the ready ones.

The evolution of that "ask the kernel" call is worth knowing because the reason for each step is the same reason:

| API | How it asks | Cost |
|---|---|---|
| `select()` | pass a bitmap of all fds, kernel scans all of them | O(n) per call, capped at `FD_SETSIZE` (1024) |
| `poll()` | pass an array, no fixed cap | still O(n) per call |
| **`epoll`** (Linux) / `kqueue` (BSD/macOS) | register fds **once**, kernel keeps the set and hands back only ready ones | O(ready), scales to millions |
| **`io_uring`** (Linux 5.1+) | shared submission/completion ring buffers — submit *operations*, not just readiness | fewer syscalls still; true async, not just readiness |

The pattern is: **stop re-telling the kernel what you care about on every single call.** `epoll` is the foundation under nginx, Redis, Node's libuv, Netty, and Nginx-style event loops generally. `io_uring` goes further by making the I/O itself asynchronous rather than just the notification, which finally makes async *file* I/O work properly too.

**The event-loop trade:** one thread + `epoll` handles enormous connection counts cheaply, but **any blocking work on that thread stalls every connection**. That's the whole reason "don't block the event loop" is the first rule of [[backend/01-nodejs/README|Node]], why Redis (single-threaded) is astonishingly fast until you run one `KEYS *`, and why CPU-bound work needs a worker pool.

**Threads came back, though.** Green threads / virtual threads give you blocking-style code on an event-loop-style runtime — the runtime parks the lightweight thread and reuses the OS thread. Go's goroutines have always worked this way; [[languages/01-java/02-jvm-and-concurrency/README|Java's Project Loom]] brought it to the JVM. The lesson is that the *programming model* (blocking, sequential, readable) and the *execution model* (multiplexed onto few OS threads) were never actually required to match — we just lacked the runtime to separate them.

## Things the API lies to you about

The socket API's abstraction leaks in specific, predictable ways. These cause real bugs:

- **`write()` returning doesn't mean anything was delivered.** It means the bytes were copied into the kernel's send buffer. The peer may be dead. Only an application-level acknowledgement tells you the other side *processed* it. This is the networking version of the [[architecture/04-distributed-systems/01-what-makes-distributed-systems-hard|two generals problem]] and the reason "fire and forget plus assume success" is never safe.
- **TCP is a byte stream, not a message stream.** `write("HELLO")` then `write("WORLD")` may arrive as one `read()` of `"HELLOWORLD"`, or as `"HEL"` + `"LOWORLD"`. **You must frame your own messages** — length prefix, or a delimiter. Every "it works locally but corrupts data under load / over the internet" protocol bug is this. Local loopback rarely splits packets; a real network does.
- **A short `read()` is normal.** Asking for 4096 bytes and getting 100 is not an error. Loop until you have what you need.
- **A half-open connection is invisible until you write.** If the peer's machine loses power, no FIN or RST is sent. Your socket stays `ESTABLISHED` forever. You'll discover it on the next write, minutes later. Hence keepalives and application-level heartbeats.

## Key insight

The socket API models the network as **a file you can read and write**, and that abstraction is what made networking programmable by ordinary developers. But every hard networking bug you will ever hit is a place where the file metaphor breaks: files don't have message boundaries that vanish, files don't silently die between writes, files don't succeed on write and lose your data. **Learn where the metaphor stops being true, and you've learned most of practical network programming.**

## Related
- [[foundations/networking/06-tcp-connection-lifecycle|TCP Connection Lifecycle]] — the states behind these calls
- [[foundations/os/fundamentals|OS Fundamentals]] — file descriptors, threads, context switching
- [[languages/01-java/02-jvm-and-concurrency/README|JVM & Concurrency]] — NIO, Netty, and virtual threads
- [[foundations/networking/16-debugging-networks|Debugging Networks]] — `lsof`, `ss`, and finding fd leaks
