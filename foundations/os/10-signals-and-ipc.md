# Signals and IPC

**[Intermediate → Advanced]** — How processes are interrupted and how they talk. Signals are the oldest and most awkward part of Unix; the IPC mechanisms are where shell pipelines and containers get built.

## Signals

A signal is an **asynchronous notification** — the kernel interrupts your process, runs a handler, and resumes. It's the software analogue of a hardware interrupt.

```bash
kill -l                    # all of them
```

| Signal | Default | Notes |
|---|---|---|
| `SIGINT` (2) | terminate | Ctrl-C |
| `SIGQUIT` (3) | terminate + core | Ctrl-\ |
| `SIGKILL` (9) | **terminate** | **cannot be caught, blocked, or ignored** |
| `SIGSEGV` (11) | terminate + core | invalid memory access |
| `SIGPIPE` (13) | **terminate** | write to a closed pipe/socket |
| `SIGTERM` (15) | terminate | the polite "please exit" — **catch this** |
| `SIGCHLD` (17) | ignore | a child stopped or exited |
| `SIGSTOP` (19) | stop | **cannot be caught** |
| `SIGCONT` (18) | continue | |
| `SIGHUP` (1) | terminate | terminal closed; conventionally "reload config" |
| `SIGUSR1/2` | terminate | yours to define |

**`SIGKILL` and `SIGSTOP` cannot be handled** — that's deliberate, so a process can always be killed. Everything else you can catch.

```c
struct sigaction sa = { .sa_handler = handler, .sa_flags = SA_RESTART };
sigemptyset(&sa.sa_mask);
sigaction(SIGTERM, &sa, NULL);      // use sigaction, NOT signal()
```

**Use `sigaction`, not `signal`.** `signal()`'s semantics differ between platforms and historically reset the handler after firing, creating a race. `SA_RESTART` makes interrupted syscalls resume automatically rather than returning `EINTR`.

### Handlers are severely constrained

A handler can fire **between any two instructions**, including in the middle of `malloc`. So:

> **Only async-signal-safe functions may be called from a signal handler.** `printf`, `malloc`, and most of libc are **not** on that list.

Calling `printf` from a handler that fired inside `printf` corrupts its internal state. It works 999 times and deadlocks on the thousandth.

The safe list is short: `write`, `_exit`, `signal`, `kill`, `sigaction`, and a few dozen others (`man 7 signal-safety`).

**The standard pattern — set a flag, do nothing else:**

```c
volatile sig_atomic_t shutdown_requested = 0;

void handler(int sig) { shutdown_requested = 1; }     // that's ALL

// main loop
while (!shutdown_requested) { do_work(); }
cleanup();
```

`volatile sig_atomic_t` is the only type guaranteed safe to write from a handler and read from the main flow.

**The self-pipe trick** integrates signals with an event loop, which is otherwise awkward:

```c
void handler(int sig) { write(pipe_fd, "x", 1); }     // write IS async-signal-safe
// then epoll on pipe_fd like any other descriptor
```

Modern Linux has a cleaner answer:

```c
int sfd = signalfd(-1, &mask, 0);      // signals arrive as READABLE DATA on a fd
```

`signalfd` turns signals into ordinary file descriptors — no handler, no async-safety constraints, and it composes with [[foundations/os/08-io-models|epoll]]. Same idea as `timerfd` and `eventfd`. **Prefer this in any event-driven program.**

### The ones that bite

**`SIGPIPE` kills your process by default.** Writing to a socket the peer closed terminates you — which is catastrophic in a server:

```c
signal(SIGPIPE, SIG_IGN);                 // then write() returns EPIPE, which you handle
send(fd, buf, len, MSG_NOSIGNAL);          // or suppress per-call
```

Every network program must do one of these. Go and Rust handle it in their runtimes; C and C++ don't. → [[backend/frameworks/c/01-the-accept-loop-and-event-loops|The Accept Loop]]

**`SIGTERM` is the graceful-shutdown contract.** Kubernetes sends `SIGTERM`, waits `terminationGracePeriodSeconds` (default 30), then `SIGKILL`. A process that ignores `SIGTERM` gets killed mid-request every deploy. → [[devops/05-orchestration/README|Orchestration]]

**`SIGCHLD` and zombies.** Ignore it explicitly or reap with `waitpid`, or children accumulate. → [[foundations/os/02-processes-and-threads|Processes and Threads]]

**Signals and threads.** A signal is delivered to *one arbitrary thread* that hasn't blocked it. The usual discipline: block signals in all threads, then have one dedicated thread call `sigwait` — which is exactly what `signalfd` replaces more cleanly.

## Pipes

```c
int fd[2];
pipe(fd);                    // fd[0] = read end, fd[1] = write end
```

A unidirectional in-kernel byte buffer, 64KB by default. Writes block when full, reads block when empty — **backpressure for free**.

This is how shell pipelines work:

```c
// ls | wc -l
int fd[2];
pipe(fd);

if (fork() == 0) {                      // ls
    dup2(fd[1], STDOUT_FILENO);         // stdout becomes the pipe
    close(fd[0]); close(fd[1]);
    execlp("ls", "ls", NULL);
}
if (fork() == 0) {                      // wc
    dup2(fd[0], STDIN_FILENO);          // stdin becomes the pipe
    close(fd[0]); close(fd[1]);
    execlp("wc", "wc", "-l", NULL);
}
close(fd[0]); close(fd[1]);             // PARENT MUST CLOSE BOTH
```

**The parent closing both ends is essential.** `wc` sees EOF only when *every* write end is closed — including the parent's copy. Forgetting this is the classic "my pipeline hangs" bug, and it's the trickiest part of [[BUILD-PLAN|building a shell]].

`dup2` is the mechanism behind all shell redirection: it makes one descriptor number refer to another's open file.

**Named pipes** (FIFOs) are the same thing with a filesystem name, usable between unrelated processes:

```bash
mkfifo /tmp/mypipe
```

## Unix domain sockets

Sockets that never touch the network stack:

```c
int fd = socket(AF_UNIX, SOCK_STREAM, 0);
struct sockaddr_un addr = { .sun_family = AF_UNIX };
strcpy(addr.sun_path, "/tmp/my.sock");
```

**Faster than TCP over loopback** (no checksums, no protocol processing) and they add two things nothing else has:

**Credential passing** — `SO_PEERCRED` gives you the peer's authenticated uid/pid, verified by the kernel. That's how systemd, Docker and D-Bus authorise local clients without any credential exchange.

**File descriptor passing** — `SCM_RIGHTS` sends an open descriptor to another process. The receiver gets a working descriptor for a file or socket it never opened. This is how privilege-separated servers work (a root process opens port 80 and hands the socket to an unprivileged worker) and how systemd socket activation works.

Almost every local daemon uses these: `/var/run/docker.sock`, `/var/run/postgresql/.s.PGSQL.5432`, systemd's journal.

## Shared memory

The fastest IPC — no copying at all:

```c
int fd = shm_open("/myshm", O_CREAT | O_RDWR, 0666);
ftruncate(fd, size);
void *p = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
```

Both processes map the same physical pages. A write by one is instantly visible to the other — **there is no send or receive.**

Which is also the problem: **no synchronisation comes with it.** You need a mutex or semaphore in the shared region itself (`PTHREAD_PROCESS_SHARED`), and all the memory-ordering concerns from [[foundations/os/06-concurrency-primitives|Concurrency Primitives]] apply across processes.

Use it for large data at high frequency — databases (Postgres's shared buffers), video pipelines, `/dev/shm`. Avoid it when a socket is fast enough, because the correctness burden is real.

## The rest

**System V IPC** — `msgget`, `semget`, `shmget`. Older API, system-wide namespace, and objects **persist after the process dies** (`ipcs` / `ipcrm` to clean up). Avoid for new code; POSIX equivalents are better.

**POSIX message queues** — `mq_open`, prioritised messages, works with `epoll` on Linux.

**eventfd** — a counter as a file descriptor, for lightweight wakeups between threads/processes. What `epoll`-based code uses to interrupt its own loop.

**D-Bus** — high-level desktop/system message bus. Method calls and signals over Unix sockets.

## Choosing

| Need | Use |
|---|---|
| Parent → child stream | **pipe** |
| Unrelated local processes | **Unix domain socket** |
| Peer identity, or passing an fd | **Unix socket** (`SO_PEERCRED` / `SCM_RIGHTS`) |
| Large data, high frequency | **shared memory** + explicit synchronisation |
| Notification only | **eventfd** / **signalfd** |
| Across machines | **TCP** → [[foundations/networking/README\|networking]] |
| Interrupting a process | **signal** |

> **Default to Unix domain sockets.** They're fast, they're the same API as network sockets (so the code ports), they carry authenticated credentials, and they integrate with event loops. Reach for shared memory only when profiling shows the copy is the bottleneck.

---

## Related
- [[foundations/os/02-processes-and-threads|Processes and Threads]] — `fork`, and zombies
- [[foundations/os/08-io-models|I/O Models]] — `signalfd`/`eventfd` in an event loop
- [[foundations/os/06-concurrency-primitives|Concurrency Primitives]] — synchronising shared memory
- [[devops/01-linux/06-process-management|Linux: Process Management]] — signals from the shell
- [[foundations/os/README|OS course map]]
