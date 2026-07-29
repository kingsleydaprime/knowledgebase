# Tune System Performance

> RHCSA V10

Part of [[README|RHCSA V10]]. Builds on [[devops/01-linux/06-process-management|Process Management]], which already covers `top` and the `NI` (nice) column shown there.

---

## nice and renice — process priority

Every process has a **niceness** value from **-20 (highest priority, least "nice" to other processes) to 19 (lowest priority, most "nice")**. Default is 0. Lower niceness = more CPU time relative to other processes when the CPU is contended.

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

Common built-in profiles:

| Profile | Use case |
|---|---|
| `balanced` | Default — reasonable tradeoff of power saving and performance |
| `powersave` | Laptops, minimizing energy use over raw performance |
| `throughput-performance` | Servers doing sustained heavy I/O/CPU work — the classic "make this server fast" answer |
| `latency-performance` | Minimize response latency over throughput — real-time-ish workloads |
| `virtual-guest` | Tuned for running *inside* a VM |
| `virtual-host` | Tuned for a machine *hosting* VMs |

`tuned-adm profile <name>` is almost always the actual exam-correct answer to "tune this system for X workload" — knowing the right profile name matters more than knowing what's inside it.

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
