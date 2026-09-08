# I/O Models

**[Intermediate → Advanced]** — Blocking, non-blocking, multiplexed, and truly asynchronous — the progression from one thread per connection to a million connections on one core.

## The five models

The classic taxonomy, and the thing to notice is what each does during the two phases of an I/O operation: **waiting for data** and **copying it**.

| Model | Waiting | Copying |
|---|---|---|
| **Blocking** | blocked | blocked |
| **Non-blocking (polling)** | returns `EAGAIN`, you retry | blocked |
| **I/O multiplexing** (`select`/`epoll`) | blocked in `epoll_wait` | blocked |
| **Signal-driven** | not blocked | blocked |
| **Asynchronous** (`io_uring`, AIO) | not blocked | **not blocked** |

Only the last is *truly* asynchronous by POSIX's definition: the kernel does the copy too and tells you when everything is finished. `epoll` is **readiness notification** — it tells you that a read *would* succeed, and you still perform it.

That distinction is why `io_uring` is genuinely different rather than a faster `epoll`.

## Blocking

```c
ssize_t n = read(fd, buf, size);      // returns when data is ready. Thread sleeps.
```

Simple, and correct. The thread is descheduled and costs nothing while waiting — the problem is that **you need a thread per concurrent operation.**

At 10,000 connections that's 10,000 threads: ~80GB of virtual stack, ~100MB of kernel structures, and a scheduler spending more time context-switching than working. That's **C10K**, and the reason everything below exists. → [[foundations/os/02-processes-and-threads|Processes and Threads]]

## Non-blocking

```c
fcntl(fd, F_SETFL, flags | O_NONBLOCK);

ssize_t n = read(fd, buf, size);
if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
    // no data right now — NOT an error
}
```

The call returns immediately either way. Polling every descriptor in a loop is **CPU-burning and pointless** — but non-blocking mode is a prerequisite for everything that follows, because readiness notification is a statement about the past and the data may be gone by the time you read.

## Multiplexing: `select` → `poll` → `epoll`

**`select`** — the original. Pass a bitmask of descriptors, block until one is ready.

```c
select(nfds, &readfds, &writefds, &exceptfds, &timeout);
```

Two fatal flaws: **`FD_SETSIZE` is 1024**, hard-coded, and it's **O(n)** — the kernel scans every descriptor on every call, and you rescan to find which fired. It also destroys the fd sets, so you rebuild them each iteration.

**`poll`** — removes the 1024 limit with an array instead of a bitmask. Still O(n): you pass the entire array every call, and the kernel walks all of it.

**`epoll`** — the fix, and the reason Linux servers scale:

```c
int ep = epoll_create1(0);

struct epoll_event ev = { .events = EPOLLIN, .data.ptr = conn };
epoll_ctl(ep, EPOLL_CTL_ADD, fd, &ev);            // register ONCE

struct epoll_event events[MAX];
int n = epoll_wait(ep, events, MAX, -1);           // returns ONLY ready fds
for (int i = 0; i < n; i++) handle(events[i].data.ptr);
```

**The interest set lives in the kernel.** You register a descriptor once; `epoll_wait` returns only what's ready. That's **O(ready)**, not O(total) — 100,000 idle connections cost nothing per call.

BSD's `kqueue` is the equivalent, and arguably a better design (it handles files, signals, timers and process events uniformly). Windows has IOCP, which is completion-based like `io_uring`.

### Level vs edge triggered

```c
ev.events = EPOLLIN;              // level: notified WHILE data remains
ev.events = EPOLLIN | EPOLLET;    // edge: notified once per ARRIVAL
```

**Edge-triggered requires draining to `EAGAIN`:**

```c
for (;;) {
    ssize_t n = read(fd, buf, sizeof buf);
    if (n < 0 && errno == EAGAIN) break;      // NOW you're done
    if (n <= 0) { close_conn(c); return; }
    consume(c, buf, n);
}
```

Miss that and the remaining bytes sit in the buffer forever with no further notification — a hung connection that looks like a bug in your protocol handling. Edge-triggered is fewer syscalls and less forgiving. **Start level-triggered.** → [[backend/frameworks/c/01-the-accept-loop-and-event-loops|The Accept Loop]]

### The thundering herd

Multiple threads in `epoll_wait` on the same listening socket all wake on one connection; one wins, the rest go back to sleep having done nothing.

Fixes: `EPOLLEXCLUSIVE` (wake only one), or `SO_REUSEPORT` — each thread gets its own listening socket and the kernel load-balances. `SO_REUSEPORT` is nginx's approach and the cleaner one.

## `io_uring`

The genuinely new thing (Linux 5.1, 2019), and the first Linux interface that's properly asynchronous.

**Two shared ring buffers, mapped between kernel and user space:**

```
SUBMISSION QUEUE   →  you write operation descriptions here
COMPLETION QUEUE   ←  the kernel writes results here
```

```c
struct io_uring ring;
io_uring_queue_init(256, &ring, 0);

struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read(sqe, fd, buf, len, offset);
io_uring_sqe_set_data(sqe, conn);
io_uring_submit(&ring);                        // ONE syscall — can submit MANY operations

struct io_uring_cqe *cqe;
io_uring_wait_cqe(&ring, &cqe);                // the read is ALREADY DONE
```

What's different:

**Batching.** Submit dozens of operations in one syscall. With `IORING_SETUP_SQPOLL`, a kernel thread polls the queue and you make **zero syscalls** in steady state.

**Real completion.** The data is in your buffer when you're notified. No second `read` call.

**It works on regular files.** `epoll` doesn't — a regular file is always "ready", so buffered file I/O had no async story at all before this. That's a large gap it closes.

**Everything, not just I/O.** `openat`, `accept`, `statx`, `send`, `recv`, `fsync`, timeouts, and chained operations (`IOSQE_IO_LINK`) where the next runs only if the previous succeeded.

The costs: **Linux 5.1+ only** (5.6+ realistically, 6.x for the good parts), the API is complex, and there have been enough security issues that **some environments disable it outright** — Google disabled it in ChromeOS and Android, and several container platforms restrict it via seccomp. Check before designing around it.

Use `liburing`, never the raw syscalls.

Adoption is real and growing: tokio has a backend, Netty supports it, and it's the basis of high-performance storage engines.

## Where each runtime sits

| Runtime | Underneath |
|---|---|
| **Node.js** | libuv → `epoll`/`kqueue`/IOCP, plus a thread pool for file I/O and DNS |
| **Go** | netpoller → `epoll`, integrated with the scheduler so a blocking read parks the *goroutine* |
| **Rust tokio** | mio → `epoll`; an `io_uring` backend exists |
| **Java NIO** | `epoll`; virtual threads park on it since 21 |
| **nginx** | `epoll` directly, `SO_REUSEPORT`, worker per core |

**Go's integration is the interesting one.** A goroutine calling `read` looks blocking, but the runtime converts it into a non-blocking read plus a netpoller registration and schedules another goroutine. You get blocking-style code with event-loop scaling and no function colouring — which is the concrete reason Go is pleasant for network services. → [[languages/02-go/06-goroutines-and-channels|Goroutines]]

## Choosing

| Situation | Use |
|---|---|
| A handful of connections | **blocking threads.** Simplest, and correct |
| Thousands of connections | **`epoll`** — or a runtime that wraps it |
| Maximum throughput, modern kernel | **`io_uring`** |
| Async file I/O | **`io_uring`** — it's the only real option |
| Cross-platform | a library: libuv, libevent, asio, tokio |

> **The framing worth keeping:** blocking I/O isn't obsolete, it's *thread-expensive*. If the concurrency is low, threads are simpler and faster to write. Everything above exists to break the one-thread-per-connection coupling — and every runtime you use is one of these models with a nicer surface.

## Measuring

```bash
strace -c -e trace=network,read,write ./prog       # syscall counts and time
perf stat -e syscalls:sys_enter_epoll_wait ./prog
ss -tn state established | wc -l                    # actual connection count
cat /proc/<pid>/fdinfo/<fd>                         # per-descriptor state
cat /proc/pressure/io                                # time lost waiting on I/O
```

A high syscall count per request is the signature of a poorly-batched I/O loop — the thing `io_uring` is designed to fix.

---

## Related
- [[foundations/os/07-filesystems-and-storage|Filesystems and Storage]] — the page cache and `fsync`
- [[foundations/networking/09-sockets-and-the-network-api|Sockets and the Network API]] — the same material, network-side
- [[backend/frameworks/c/01-the-accept-loop-and-event-loops|Building an Event Loop]] — writing one
- [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — how frameworks expose this
- [[foundations/os/README|OS course map]]
