# Scheduling

**[Intermediate]** — How the kernel decides what runs next, what a context switch actually costs, and the cgroup throttling that makes containers mysteriously slow.

## The problem

More runnable threads than CPUs. The scheduler picks which runs, for how long, and on which core — aiming at several goals that conflict:

- **Fairness** — nobody starves
- **Throughput** — maximise useful work
- **Latency** — an interactive process should feel responsive
- **Efficiency** — the scheduler itself must be cheap; it runs constantly

You cannot maximise all of them. A scheduler tuned for throughput (long time slices, few switches) feels laggy; one tuned for latency (short slices) wastes time switching.

## Preemptive multitasking

A **timer interrupt** fires periodically (typically 250Hz or 1000Hz on Linux, configurable). The CPU jumps to the kernel, which may decide to run someone else. The running process gets no say — that's what "preemptive" means.

Cooperative multitasking (classic Mac OS, Windows 3.x) required processes to yield voluntarily. One buggy infinite loop froze the machine. Preemption removed that failure mode.

Modern Linux is also **tickless** (`NO_HZ`) — an idle CPU stops receiving timer interrupts entirely, which matters for laptop battery and for virtualisation density.

## Context switching

What actually happens:

1. Save the current thread's registers into its `task_struct`
2. Load the next thread's registers
3. **If it's a different process**, switch the page table base register (CR3 on x86)
4. Return to user space

Direct cost: **~1–3µs**. But that undersells it, because step 3 has consequences:

- **TLB flush.** Switching page tables invalidates cached virtual→physical translations, so subsequent memory accesses take a page-table walk until the TLB refills. (PCID/ASID tags mitigate this on modern CPUs.)
- **Cache pollution.** The new thread's working set displaces the old one's. The old thread resumes with a cold cache.

**The indirect cost often exceeds the direct cost several times over.** This is why thread-per-connection collapses at scale: at 10,000 threads you spend more time switching and refilling caches than working.

Same-process thread switches are cheaper — no page-table change, so the TLB survives.

```bash
vmstat 1                 # cs column = context switches/sec
pidstat -w -p <pid> 1    # voluntary vs involuntary switches for one process
perf stat -e context-switches,cpu-migrations ./prog
```

**Voluntary** switches mean the thread blocked (usually on I/O) — normal. **Involuntary** means it was preempted — high numbers mean CPU contention.

## CFS and EEVDF

Linux's scheduler for normal tasks was **CFS** (Completely Fair Scheduler) from 2007, replaced by **EEVDF** in kernel 6.6 (2023).

**CFS** tracked `vruntime` — virtual runtime, weighted by priority — and always ran the thread with the lowest one, kept in a red-black tree. "Fair" meant every thread converged on an equal share, with nice values weighting the accumulation rate.

**EEVDF** (Earliest Eligible Virtual Deadline First) adds a **latency** dimension. Each task gets a virtual deadline; among eligible tasks, the earliest deadline runs. This lets a task request low latency without also demanding more CPU — CFS could only express "more important" as "more CPU".

```bash
chrt -p $$                    # scheduling policy and priority
nice -n 10 ./batch_job        # lower priority (-20 highest, 19 lowest)
renice -n 5 -p 1234
```

Nice values are roughly a **10% CPU change per step**, not linear — nice 0 vs nice 5 is about a 3× weight difference.

### Real-time policies

```bash
chrt -f 50 ./realtime_task    # SCHED_FIFO — runs until it yields or is preempted by higher priority
chrt -r 50 ./task             # SCHED_RR — FIFO with time slices among equals
chrt -d ./task                # SCHED_DEADLINE — specify runtime/period/deadline
```

`SCHED_FIFO` and `SCHED_RR` **always** preempt normal tasks. A runaway FIFO task with no blocking can lock up a core — hence `sched_rt_runtime_us`, which reserves 5% of each period for normal tasks by default.

`SCHED_DEADLINE` is the most principled: you declare "I need 2ms of CPU every 10ms", and the kernel admission-controls it. That's the right tool for genuine real-time work — audio, motor control, robotics. → [[robotics/README|robotics]]

## Multicore: run queues, load balancing, affinity

Each CPU has **its own run queue**. A single global queue would need a lock on every scheduling decision, which doesn't scale.

**Load balancing** periodically migrates tasks between queues to even things out. It's deliberately reluctant, because migration is expensive:

**Cache affinity** — a thread that has been running on CPU 3 has its working set in CPU 3's L1/L2. Moving it to CPU 7 means starting cold. The scheduler weighs this and prefers to leave things where they are.

```bash
taskset -c 0,1 ./prog          # pin to CPUs 0 and 1
taskset -cp 2 1234             # pin a running process
```

Pinning helps latency-sensitive work by eliminating migration entirely. It also **removes the scheduler's ability to balance**, so it's a commitment, not a free optimisation.

### NUMA

On multi-socket machines, memory is attached to a specific socket. Accessing another socket's memory costs **1.5–2× the latency**.

```bash
numactl --hardware             # topology and inter-node distances
numactl --cpunodebind=0 --membind=0 ./prog
cat /proc/<pid>/numa_maps
```

Linux allocates memory on the node where the faulting thread runs (first-touch policy), and `numa_balancing` migrates pages toward the threads using them.

**The classic NUMA bug:** a startup thread allocates and initialises a large buffer, so every page lands on node 0. Worker threads on node 1 then pay remote latency for the program's lifetime. The fix is to have each worker touch its own region first.

## cgroup CPU limits — the container gotcha

The most operationally important part of this note.

```bash
# cgroup v2
/sys/fs/cgroup/mygroup/cpu.max     # "200000 100000" = 2 CPUs' worth per 100ms period
/sys/fs/cgroup/mygroup/cpu.weight  # relative share when contended
/sys/fs/cgroup/mygroup/cpu.stat    # nr_throttled, throttled_usec  ← CHECK THIS
```

**CPU quota is enforced by throttling, per period.** With `cpu.max = "200000 100000"`, your cgroup gets 200ms of CPU per 100ms wall-clock period (i.e. 2 cores). Use it up in 40ms and **every thread is frozen for the remaining 60ms.**

```
period:  |--------100ms--------|--------100ms--------|
quota used:  ████████ (40ms across 8 threads = 200ms CPU)
                    ^^^^^^^^^^^ THROTTLED — nothing runs
```

The symptom is p99 latency spikes with **average CPU utilisation well under the limit** — because you're not limited by average, you're stalled at the end of periods.

Why it bites hardest in containers: **a runtime that sizes its thread pool by `nproc` sees the host's core count, not the quota.** A 2-CPU container on a 64-core node creates 64 worker threads, all runnable, burning quota 32× faster than a period allows.

```bash
cat /sys/fs/cgroup/cpu.stat        # nr_throttled > 0 means you're being throttled
```

The fixes, per runtime:

```go
import _ "go.uber.org/automaxprocs"          // Go: read the cgroup quota
```
```
java -XX:ActiveProcessorCount=2               # JVM (usually detects it, verify)
```
```
UV_THREADPOOL_SIZE=4                          # Node's libuv pool
```

**And prefer CPU *requests* over hard *limits*** in Kubernetes for latency-sensitive services. Requests give you a guaranteed share via `cpu.weight` without the throttle cliff. → [[devops/05-orchestration/README|Orchestration]]

This single mechanism explains a large fraction of "our service is slow in Kubernetes but fine locally" reports.

## Priority inversion

A low-priority thread holds a lock. A high-priority thread needs it and blocks. A medium-priority thread preempts the low one, which now never runs to release the lock — so the high-priority thread waits on the medium one indefinitely.

This is not academic: it nearly ended the **Mars Pathfinder** mission in 1997.

The fix is **priority inheritance** — the lock holder temporarily inherits the priority of the highest waiter:

```c
pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
```

Linux futexes support this (`FUTEX_LOCK_PI`), and it's what `PTHREAD_PRIO_INHERIT` uses. → [[foundations/os/06-concurrency-primitives|Concurrency Primitives]]

## Diagnosing

```bash
top -H                              # per-thread
htop                                # F2 to show custom meters
pidstat -w -p <pid> 1               # context switches
perf sched record -- sleep 5 && perf sched latency    # scheduling delays per task
cat /proc/<pid>/sched                # per-task scheduler statistics
cat /proc/pressure/cpu               # PSI — how much time is LOST to CPU contention
```

**PSI (Pressure Stall Information)** is the modern answer to "is this machine overloaded". `some avg10=25.00` means tasks were stalled waiting for CPU 25% of the last 10 seconds — a far more actionable number than load average, which conflates CPU wait with uninterruptible I/O.

---

## Related
- [[foundations/os/02-processes-and-threads|Processes and Threads]] — what's being scheduled
- [[foundations/os/11-isolation-and-containers|Isolation and Containers]] — cgroups in full
- [[foundations/os/06-concurrency-primitives|Concurrency Primitives]] — blocking, and priority inheritance
- [[languages/02-go/13-performance-and-runtime|Go: the G-M-P scheduler]] — a user-space scheduler on top of this
- [[foundations/os/README|OS course map]]
