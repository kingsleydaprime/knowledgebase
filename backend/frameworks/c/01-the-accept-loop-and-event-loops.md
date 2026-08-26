# The Accept Loop and Event Loops

**[Advanced]** — Building the thing every other framework in this vault is built on. This is where Node's event loop, Go's netpoller and tokio's reactor actually live.

**Source:** `[reference]`. Assumes [[languages/04-c/README|the C course]] and [[foundations/networking/09-sockets-and-the-network-api|sockets]].

## The blocking server

Every HTTP server starts here:

```c
int fd = socket(AF_INET, SOCK_STREAM, 0);

int opt = 1;
setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof opt);   // reuse a TIME_WAIT port

struct sockaddr_in addr = {
    .sin_family = AF_INET,
    .sin_addr.s_addr = INADDR_ANY,
    .sin_port = htons(8080),          // host to network byte order
};
bind(fd, (struct sockaddr *)&addr, sizeof addr);
listen(fd, SOMAXCONN);                 // SOMAXCONN, not 5 — the backlog matters under load

for (;;) {
    int client = accept(fd, NULL, NULL);
    if (client < 0) { if (errno == EINTR) continue; break; }
    handle_connection(client);         // BLOCKS here — one client at a time
    close(client);
}
```

That's a working HTTP server that serves exactly one client at a time. Everything past this point is a strategy for handling the second client.

**`SO_REUSEADDR`** is not optional: without it, restarting your server fails with "Address already in use" for up to two minutes while the previous socket sits in `TIME_WAIT`. It's the first thing that will annoy you.

## The four strategies

| Model | Concurrency unit | Cost each | Scales to |
|---|---|---|---|
| **Process per connection** | `fork()` | ~1MB + page tables | hundreds |
| **Thread per connection** | `pthread_create` | ~8MB virtual stack | thousands |
| **Thread pool** | pre-spawned workers | bounded | thousands |
| **Event loop** | one thread, `epoll` | ~few KB per fd | **hundreds of thousands** |

### Process per connection

```c
int client = accept(fd, NULL, NULL);
pid_t pid = fork();
if (pid == 0) { close(fd); handle_connection(client); _exit(0); }
close(client);
```

This is the original CGI and Apache prefork model. It's genuinely robust — a crash or leak in one connection can't touch another, since they're separate address spaces — and expensive enough that it's now rare outside of privilege-separation designs.

You must `waitpid` for children or accumulate zombies. `signal(SIGCHLD, SIG_IGN)` is the lazy fix.

### Thread per connection

```c
pthread_t t;
int *arg = malloc(sizeof *arg);        // heap — passing &client races with the next accept
*arg = client;
pthread_create(&t, NULL, worker, arg);
pthread_detach(t);                      // or you leak the thread struct
```

Simple to write, and it collapses at roughly 10k connections — the **C10K problem**. Each thread reserves stack, the scheduler thrashes, and most threads are idle waiting on I/O.

The `malloc` for the argument is not paranoia: passing `&client` hands every thread a pointer to the same stack variable, which the next `accept()` overwrites.

### The event loop

The answer, and the model everything modern uses:

```c
int ep = epoll_create1(0);

struct epoll_event ev = { .events = EPOLLIN, .data.fd = listen_fd };
epoll_ctl(ep, EPOLL_CTL_ADD, listen_fd, &ev);

struct epoll_event events[MAX_EVENTS];
for (;;) {
    int n = epoll_wait(ep, events, MAX_EVENTS, -1);      // BLOCKS until something is ready
    for (int i = 0; i < n; i++) {
        int fd = events[i].data.fd;
        if (fd == listen_fd) {
            int client = accept4(listen_fd, NULL, NULL, SOCK_NONBLOCK);
            struct epoll_event cev = { .events = EPOLLIN | EPOLLET, .data.ptr = conn_new(client) };
            epoll_ctl(ep, EPOLL_CTL_ADD, client, &cev);
        } else {
            handle_ready(events[i].data.ptr);            // never blocks
        }
    }
}
```

**One thread, tens of thousands of connections.** `epoll_wait` sleeps until at least one file descriptor is ready, then hands you only the ready ones — O(ready), not O(total), which is what `select()` and `poll()` got wrong.

> **This loop is what Node's event loop, Go's netpoller, tokio's reactor and nginx all are underneath.** Writing it once makes every one of those permanently unmysterious — and explains why blocking inside an async handler is catastrophic. You're blocking *this* loop.

The portability layer: `epoll` on Linux, `kqueue` on BSD/macOS, IOCP on Windows. `libuv` (which Node uses) and `libevent` paper over the difference.

`io_uring` is the newer Linux interface — genuinely asynchronous *operations* rather than readiness notification, so you submit a read and get the completed data rather than "you may now read". Meaningfully faster; much more complex. → [[foundations/networking/09-sockets-and-the-network-api|Sockets]]

## Non-blocking is mandatory

```c
int flags = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, flags | O_NONBLOCK);
```

Every socket in an event loop must be non-blocking, because **readiness is a promise about the past**. `epoll` says "readable"; by the time you call `read()` the data may be gone (another thread took it, or it was a spurious wakeup), and a blocking `read` would then hang the entire loop.

```c
ssize_t n = read(fd, buf, sizeof buf);
if (n < 0) {
    if (errno == EAGAIN || errno == EWOULDBLOCK) return;   // not an error — try later
    if (errno == EINTR) continue;                          // signal — retry
    close_connection(c);
    return;
}
if (n == 0) { close_connection(c); return; }               // peer closed cleanly
```

Handling `EAGAIN`, `EINTR` and `n == 0` correctly is most of what makes non-blocking I/O fiddly. Every one of them is a real case.

## Level-triggered vs edge-triggered

```c
ev.events = EPOLLIN;              // level-triggered: notifies while data REMAINS
ev.events = EPOLLIN | EPOLLET;    // edge-triggered: notifies once per ARRIVAL
```

**Level-triggered** is forgiving — read some data, and if any remains you'll be notified again.

**Edge-triggered** notifies only on a state *change*, so you must **drain the socket until `EAGAIN`** or you'll never hear about the remaining bytes:

```c
for (;;) {
    ssize_t n = read(fd, buf, sizeof buf);
    if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) break;   // NOW you're done
    if (n <= 0) { close_connection(c); return; }
    consume(c, buf, n);
}
```

Edge-triggered is faster (fewer syscalls) and the source of a classic hang: a connection that stops responding because 200 bytes are sitting in a buffer nobody will be told about again. **Start level-triggered.**

## Connection state

The consequence of never blocking: a request may arrive across several `read()` calls, so you cannot keep parser state on the stack. Each connection needs an explicit state machine:

```c
typedef enum { ST_REQUEST_LINE, ST_HEADERS, ST_BODY, ST_RESPONDING, ST_CLOSING } state_t;

typedef struct {
    int      fd;
    state_t  state;
    char     in[8192];
    size_t   in_len;              // how much is buffered
    char    *out;
    size_t   out_len, out_sent;   // partial writes are NORMAL
    time_t   last_active;         // for idle timeouts
} conn_t;
```

**Partial writes are normal.** `write()` returning less than you asked is not an error — the kernel buffer was full. You must track `out_sent`, register for `EPOLLOUT`, and finish later:

```c
ssize_t n = write(c->fd, c->out + c->out_sent, c->out_len - c->out_sent);
if (n > 0) c->out_sent += (size_t)n;
if (c->out_sent < c->out_len) {
    ev.events = EPOLLIN | EPOLLOUT;      // tell me when it's writable again
    epoll_ctl(ep, EPOLL_CTL_MOD, c->fd, &ev);
}
```

Forgetting this truncates large responses under load and works perfectly in testing.

This hand-written state machine is exactly what `async`/`await` generates for you — [[languages/03-rust/14-async-and-tokio|a Rust `async fn`]] compiles into a state machine with the same shape. Writing one by hand is the clearest possible explanation of what the keyword does.

## Scaling across cores

One event loop uses one core. Two options:

**`SO_REUSEPORT`** — several processes each with their own listening socket on the same port; the kernel load-balances new connections:

```c
setsockopt(fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof opt);
```

This is nginx's model, and it's the cleanest — no shared state, no lock, no thundering herd.

**One acceptor, many worker loops** — accept centrally, distribute descriptors to per-core event loops.

Both give you **thread-per-core**, which is also what Actix Web does and what makes it fast: no cross-thread synchronisation on the hot path.

## The other things production needs

```c
signal(SIGPIPE, SIG_IGN);         // MANDATORY — writing to a closed socket kills you otherwise
```

Without ignoring `SIGPIPE`, a client that disconnects mid-response terminates your process. `write` then returns `EPIPE`, which you handle normally.

Also: idle timeouts (walk connections by `last_active`, or use a `timerfd`), file-descriptor limits (`ulimit -n` and `setrlimit`), backpressure when the output buffer grows unboundedly, and a graceful shutdown that stops accepting and drains.

## What this is worth

**Do write one** to understand the layer. The [[BUILD-PLAN|build-your-own-shit]] HTTP server guide starts exactly here, and the payoff is understanding every runtime you'll use afterwards.

**Don't ship one** without a strong reason. The list above is the *easy* half — parsing untrusted input in C is where the CVEs are, and every framework in [[backend/frameworks/c/README|the C options]] has already solved this correctly.

---

## Related
- [[backend/frameworks/c/02-parsing-http-safely|Parsing HTTP Safely]] — the dangerous half
- [[foundations/networking/09-sockets-and-the-network-api|Sockets and the Network API]] — the syscalls
- [[backend/01-foundations/04-runtime-and-concurrency-models|Runtime & Concurrency Models]] — where this sits
- [[languages/03-rust/14-async-and-tokio|Rust: Async]] — the state machine, generated
- [[backend/frameworks/c/README|C backends]]
