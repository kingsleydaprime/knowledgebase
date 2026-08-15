# Processes and Threads

**[Beginner → Intermediate]** — What a process actually consists of, why `fork()` is a strange and brilliant API, and what a thread shares that a process doesn't.

## A process is four things

```
┌──────────────────────────────────────┐
│ PROCESS                              │
│                                      │
│  1. ADDRESS SPACE   virtual memory   │
│     text / data / heap / stack       │
│                                      │
│  2. THREADS         ≥1 execution     │
│     each: registers, stack, PC       │
│                                      │
│  3. OPEN FILES      the fd table     │
│                                      │
│  4. KERNEL STATE    pid, uid, cwd,   │
│     signal handlers, limits, cgroup  │
└──────────────────────────────────────┘
```

The kernel tracks all of this in a **process control block** — on Linux, `struct task_struct`. It's large (a few kilobytes) and it's what a context switch has to swap around.

The address space layout:

```
high  ┌─────────────────┐
      │ kernel (mapped, │  ← present in every address space, inaccessible from ring 3
      │  not accessible)│
      ├─────────────────┤
      │ stack           │  ← grows DOWN; one per thread
      │       ↓         │
      │                 │
      │       ↑         │
      │ mmap region     │  ← shared libraries, large mallocs, mapped files
      ├─────────────────┤
      │ heap            │  ← grows UP via brk/mmap
      ├─────────────────┤
      │ BSS             │  ← uninitialised globals, zero-filled
      ├─────────────────┤
      │ data            │  ← initialised globals
      ├─────────────────┤
      │ text            │  ← the machine code; read-only, shared between instances
low   └─────────────────┘
```

Same picture as [[languages/04-c/07-memory-management|C's memory model]], seen from the kernel's side. `cat /proc/<pid>/maps` shows the real thing for any running process.

## `fork()`

The Unix process-creation API, and it's genuinely odd:

```c
pid_t pid = fork();

if (pid == 0) {
    // CHILD — a near-exact copy of the parent
} else if (pid > 0) {
    // PARENT — pid is the child's process ID
} else {
    // failed
}
```

**One call, two returns.** `fork` duplicates the calling process: same code, same memory contents, same open file descriptors, same instruction pointer. Both processes continue from the same line, distinguished only by the return value.

The child gets: a copy of the address space, copies of the file descriptors (pointing at the *same* open file descriptions — so the file offset is shared), and a new PID.

The child does **not** get: the parent's threads (only the calling thread survives), pending signals, or memory locks. That last point is why `fork` in a multithreaded program is dangerous — see below.

### Copy-on-write

Copying an entire address space would make `fork` unusably slow. It doesn't:

**Both processes' page tables point at the same physical pages, marked read-only. On the first write, the CPU faults, and the kernel copies just that page.**

So `fork` costs a page-table copy, not a memory copy. A process using 1GB forks in microseconds, and pages are only duplicated as they're actually modified. → [[foundations/os/04-virtual-memory|Virtual Memory]]

This is why `fork()` + immediately `exec()` is cheap — almost nothing gets copied before the address space is replaced entirely.

### `exec()`

```c
execl("/bin/ls", "ls", "-l", NULL);
// nothing after this runs — unless exec FAILED
```

`exec` **replaces** the current process image: new text, data, heap, and stack, same PID and same file descriptors (unless marked close-on-exec).

`fork` + `exec` together are how every process on a Unix system starts. It's how your shell runs a command:

```c
pid_t pid = fork();
if (pid == 0) {
    execvp(argv[0], argv);      // become the new program
    perror("exec");             // only reached on failure
    _exit(127);
}
waitpid(pid, &status, 0);       // parent waits
```

**That's the core of a shell**, and it's the first milestone in the [[BUILD-PLAN|build-your-own-shell]] guide.

### Why split them at all?

Windows uses `CreateProcess`, one call taking every parameter. Unix's split looks redundant until you see what happens *between* the two calls:

```c
if (fork() == 0) {
    close(STDOUT_FILENO);
    open("out.txt", O_WRONLY | O_CREAT, 0644);   // becomes fd 1
    execvp(argv[0], argv);                        // the new program writes to the file
}
```

**The child adjusts its own environment before becoming the new program.** Redirection, pipes, setting the user, changing directory, closing descriptors — all of it is ordinary code in the window between `fork` and `exec`, requiring no cooperation from the program being run and no special API.

That's how shell redirection and pipes are implemented, and it's a genuinely elegant design.

The cost: `fork` in a multithreaded process is treacherous. Only the calling thread exists in the child, so a mutex held by another thread stays locked forever — and `malloc` uses a mutex. The child may deadlock in `printf`. **After `fork` in a threaded program, call only async-signal-safe functions until `exec`.** `posix_spawn` exists to do the whole thing safely.

## Process lifecycle and zombies

```
        fork()
          ↓
      ┌────────┐  scheduled   ┌─────────┐
      │ READY  │─────────────→│ RUNNING │
      └────────┘←─────────────└────┬────┘
          ↑      preempted          │ blocks on I/O
          │                         ↓
          │                   ┌──────────┐
          └───────────────────│ BLOCKED  │
             I/O completes    └──────────┘
                                   │ exit()
                                   ↓
                              ┌──────────┐
                              │ ZOMBIE   │ ← waiting for the parent to reap it
                              └──────────┘
```

**A zombie is a process that has exited but whose exit status nobody has collected.** It holds no memory and no file descriptors — just a PID and an exit code, kept so the parent can ask how it died.

```c
waitpid(pid, &status, 0);        // reaps it
signal(SIGCHLD, SIG_IGN);        // or: tell the kernel you don't care
```

Zombies accumulate if a parent spawns children and never waits. They're harmless individually and eventually exhaust the PID table.

**An orphan is the opposite** — the parent died first. Orphans are re-parented to PID 1, which reaps them automatically. That's why `init`/`systemd` matters, and why **PID 1 in a container must reap children** — a container whose PID 1 is your application, and which spawns subprocesses, accumulates zombies unless you handle `SIGCHLD` or use `--init`. → [[foundations/os/11-isolation-and-containers|Isolation and Containers]]

```bash
ps aux | awk '$8 ~ /^Z/'     # find zombies (state Z, "defunct")
```

## Threads

A thread is a schedulable execution context. Threads in one process share almost everything:

| Shared | Per-thread |
|---|---|
| address space (heap, globals, text) | **stack** |
| file descriptors | registers, program counter |
| current directory, uid | thread ID |
| signal *handlers* | signal *mask*, pending signals |

**Sharing the address space is the whole point and the whole problem.** Communication is free — just write to a global. Correctness requires synchronisation, because two threads writing one variable is a data race. → [[foundations/os/06-concurrency-primitives|Concurrency Primitives]]

On Linux, the distinction is thinner than it appears:

```c
clone(CLONE_VM | CLONE_FS | CLONE_FILES | CLONE_SIGHAND | CLONE_THREAD, ...)  // a thread
clone(SIGCHLD, ...)                                                            // a process
fork()                                                                          // = the above
```

**Linux has one primitive: `clone`, with flags choosing what to share.** A "thread" is a task sharing the address space; a "process" is a task that doesn't. The kernel schedules both identically — they're all `task_struct`s. Threads in a process are a *thread group* sharing a `tgid`, which is what `getpid()` returns.

That's why Linux threads are relatively cheap compared to systems where processes and threads are fundamentally different objects.

### Costs

| | Cost |
|---|---|
| Thread stack | 8MB **virtual** by default; physical only as touched |
| `task_struct` + kernel stack | ~10KB |
| Creation | ~10–20µs |
| Context switch, same process | ~1–2µs |
| Context switch, different process | more — the TLB and cache suffer |

The 8MB is virtual reservation, not RAM — a thousand threads reserve 8GB of address space and use far less physically. But **thousands of threads is still the wrong design**: the scheduler overhead and cache pressure dominate. That's the C10K problem, and the reason for [[foundations/os/08-io-models|event loops]], goroutines, and virtual threads.

```c
pthread_attr_setstacksize(&attr, 512 * 1024);    // if you really need many threads
```

## Green threads

Runtimes that multiplex many logical threads onto few OS threads:

| Runtime | Model |
|---|---|
| **Go goroutines** | M:N, ~2KB initial stack, grows dynamically → [[languages/02-go/06-goroutines-and-channels\|goroutines]] |
| **Java virtual threads** | M:N since 21 → [[languages/01-java/02-jvm-and-concurrency/03-virtual-threads\|virtual threads]] |
| **Rust async tasks** | M:N, a state machine per task → [[languages/03-rust/14-async-and-tokio\|async]] |
| **Node** | one thread + an event loop, no green threads |

They're cheap because the kernel isn't involved — a "context switch" is a function call swapping registers in user space, ~100ns rather than ~1µs.

The catch is the same in all of them: **a green thread that blocks in a syscall blocks the OS thread underneath it.** Go's runtime detects this and hands the processor to another OS thread; Rust's tokio cannot, which is why `spawn_blocking` exists. → [[backend/frameworks/rust/04-async-pitfalls|Async Pitfalls]]

---

## Related
- [[foundations/os/03-scheduling|Scheduling]] — how the kernel picks what runs
- [[foundations/os/04-virtual-memory|Virtual Memory]] — copy-on-write, in full
- [[foundations/os/10-signals-and-ipc|Signals and IPC]] — how processes talk
- [[devops/01-linux/06-process-management|Linux: Process Management]] — the same thing from the shell
- [[foundations/os/README|OS course map]]
