# Tune System Performance

> RHCSA V10

Part of [[README|RHCSA V10]]. Builds on [[devops/01-linux/06-process-management|Process Management]], which already covers `top` and the `NI` (nice) column shown there.

---

## nice and renice — process priority

**RHEL 10 changed the actual scheduler underneath this**, worth knowing since it's a real, current fact rather than trivia: the default scheduling policy for ordinary processes (**`SCHED_NORMAL`**, also called `SCHED_OTHER`) is now implemented by **EEVDF (Earliest Eligible Virtual Deadline First)**, replacing the older **CFS (Completely Fair Scheduler)** used in earlier RHEL versions. EEVDF assigns each task a "virtual deadline" based on how much CPU time it's owed and its priority, then always runs whichever runnable task's deadline is soonest — the practical result for you is the same idea as before (a fairness-based scheduler you influence via niceness), just a different algorithm underneath.

**Niceness only affects `SCHED_NORMAL` processes.** Real-time scheduling policies (`SCHED_FIFO`, `SCHED_RR` — first-in-first-out and round-robin, used for genuinely time-critical work) sit in a strictly higher-priority class that always preempts normal processes regardless of nice value; niceness has no way to let a normal process outrank a real-time one. Nearly everything you run day to day is `SCHED_NORMAL` — this distinction mostly matters so you don't expect `renice` to fix contention against something running real-time.

Every `SCHED_NORMAL` process has a **niceness** value from **-20 (highest priority, least "nice" to other processes) to 19 (lowest priority, most "nice")**. Default is 0. Lower niceness = more CPU time relative to other processes when the CPU is contended.

```bash
nice -n 10 some-command          # start a new process with LOWER priority (nicer, gives way to others)
nice -n -5 some-command          # start with HIGHER priority — requires root
renice -n 5 -p 1234              # change priority of an ALREADY-RUNNING process, by PID
renice -n -10 -u kingsley        # apply to all processes owned by a user
```

Only **root** can set a *negative* niceness (raise priority above default) or lower the niceness of a process that isn't yours. A regular user can only make their own processes *nicer* (raise the number), never more aggressive.

```bash
ps -eo pid,ni,comm --sort=-ni | head    # processes sorted by niceness, highest (nicest) first
top                                      # NI column, live — see devops/linux/process-management
```

`top` also shows a **`PR`** (priority) column alongside `NI` — don't confuse the two. `NI` is the value you set; `PR` is `top`'s own computed scheduling priority, on a single unified scale that also represents real-time processes (which is why you'll occasionally see a `PR` of `-` or a negative number far below what any `NI` value could produce — that's a real-time task, entirely outside the nice-value system above).

---

## tuned — profile-based system tuning

`tuned` is a daemon that applies a bundle of kernel and sysctl-level tuning parameters as a named **profile**, instead of hand-tuning dozens of individual sysctl values yourself. This is the RHEL-idiomatic way to tune a system — it's what's actually tested on the exam, not manual `sysctl` tweaking.

```bash
systemctl status tuned              # confirm the daemon is running (it is, by default, on RHEL)
tuned-adm list                      # every profile available on this system, active one marked
tuned-adm active                    # just the currently active profile
tuned-adm profile throughput-performance    # switch profiles — takes effect immediately
tuned-adm recommend                 # tuned's own suggestion based on detected hardware/role
```
```
$ tuned-adm list
Available profiles:
- balanced             - General non-specialized tuned profile
- throughput-performance - Broadly applicable tuning for high throughput workloads
- virtual-guest         - Optimize for running inside a virtual guest
...
Current active profile: balanced
```

Common built-in profiles:

| Profile | Use case |
|---|---|
| `balanced` | Default — reasonable tradeoff of power saving and performance |
| `balanced-battery` | Balanced, but tuned further toward power saving |
| `powersave` | Laptops, minimizing energy use over raw performance |
| `desktop` | Optimized for desktop interactive use |
| `throughput-performance` | Servers doing sustained heavy I/O/CPU work — the classic "make this server fast" answer |
| `latency-performance` | Deterministic low latency, at the cost of higher power draw |
| `network-throughput` | Streaming network throughput — mainly older CPUs or 40G+ networks |
| `network-latency` | Deterministic low latency specifically for network response time |
| `virtual-guest` | Tuned for running *inside* a VM |
| `virtual-host` | Tuned for a machine *hosting* KVM guests |
| `hpc-compute` | High-performance-computing compute workloads |
| `aws` | Optimized specifically for AWS EC2 instances |
| `accelerator-performance` | Increased performance for accelerator-driven workloads |
| `optimize-serial-console` | Tuned for serial-console-driven systems |

(`intel-sst` also exists, for Intel Speed Select frequency configuration on supported hardware — narrow enough it's not worth memorizing unless you're on that specific hardware.)

`tuned-adm profile <name>` is almost always the actual exam-correct answer to "tune this system for X workload" — knowing the right profile name matters more than knowing what's inside it.

### Static vs. dynamic tuning

`tuned` applies a profile in one of two modes:

- **Static** (the RHEL default) — settings from the profile are applied once, when `tuned` starts or you switch profiles, and stay fixed regardless of what the system does afterward. Predictable, and enough for almost every real use case.
- **Dynamic** — `tuned` keeps monitoring live system activity (via its *monitor plugins* — CPU load, disk I/O, network traffic) and continuously adjusts settings on top of the base profile via *tuning plugins* (e.g. the `net` plugin scaling interface speed with actual usage). Disabled by default specifically because static tuning is more predictable; enable it in `/etc/tuned/tuned-main.conf`:
  ```ini
  dynamic_tuning = 1
  update_interval = 10   # seconds between adjustment checks
  ```

### Profiles are just directories you can inherit from

Shipped profiles live in `/usr/lib/tuned/profiles/<name>/tuned.conf` — never edit these directly (a package update overwrites them). A profile can `include=` another profile to inherit its settings and only override what's different:
```ini
[main]
summary=Optimize for running inside a virtual guest
include=throughput-performance

[sysctl]
vm.swappiness = 30
```
To customize, copy the profile directory to `/etc/tuned/profiles/<name>/` (same override-precedence pattern as systemd units and `tmpfiles.d`) and edit the copy there instead.

RHEL 10 ships considerably more profiles than the obvious ones — worth knowing the full breadth exists rather than assuming it's just balanced/powersave/throughput/latency:

---

## Reading system load

```bash
uptime
# 14:32:01 up 3 days,  2:14,  2 users,  load average: 0.52, 0.78, 0.91
```

The three numbers are load average over the **last 1, 5, and 15 minutes**. Load isn't a percentage — it's roughly "how many processes were runnable (running or waiting for CPU) on average." Compare it against your CPU core count:

```bash
nproc            # number of CPU cores available
```

- Load consistently **below** `nproc` → CPU has headroom
- Load consistently **above** `nproc` → processes are queuing for CPU time — the system is CPU-bound
- Rising trend across the three windows (1min > 5min > 15min) → load is climbing right now, not settling

---

## Quick resource snapshots

```bash
free -h                  # memory: total/used/free/available, plus swap — see devops/linux/process-management for interpretation
vmstat 1                 # system-wide stats (procs, memory, swap, io, cpu), refreshing every 1s — good for "is it CPU, memory, or I/O bound"
iostat -x 1              # per-disk I/O stats, refreshing every 1s (needs the `sysstat` package: dnf install sysstat)
mpstat -P ALL 1          # per-core CPU breakdown (also from sysstat) — spot a single maxed-out core hiding behind an average that looks fine
```

`vmstat`'s `wa` column (I/O wait) is the tell for "this looks CPU-bound in `top` but it's actually waiting on disk" — high `wa` means CPUs are idle *because* they're stuck waiting on storage, not because there's no work.
