## Process Management

Every program running on your system is a **process**. Your browser, your terminal, your music player — all processes.

When you run a command, the shell creates a new process for it. When it finishes, the process dies.

---

### Key concepts first

**PID** — every process has a unique ID

**PPID** — Parent Process ID. Every process was spawned by another process. That's its parent.

**The process tree** — since every process has a parent, all processes form a tree rooted at PID 1 (systemd).

Visualize it:
```
systemd (PID 1)
├── sshd
├── nginx
├── postgres
└── bash (your terminal)
    └── ls (when you run ls)
```

When you close your terminal, bash dies — and anything it spawned dies with it.

---

### See the process tree live

```bash
pstree
```

Or with PIDs shown:
```bash
pstree -p
```

---

### See all running processes

```bash
ps aux
```

| Column | Meaning |
|---|---|
| `USER` | who owns the process |
| `PID` | process ID |
| `%CPU` | CPU usage |
| `%MEM` | memory usage |
| `STAT` | process state |
| `COMMAND` | what command is running |

---

```txt
You said every program running is a process. But in linux since everything is a file, every process is a file right?
```

Yes and no — and this is a great distinction to make.

Every process **has** a file representation — in `/proc`. Remember `/proc/1/` we mentioned earlier? That's PID 1 represented as a directory. Every running process gets a folder in `/proc` with its PID as the name.

```bash
ls /proc/$$    # $$ is your current shell's PID
```

You'll see files like:
- `cmdline` — the command that started it
- `status` — memory, state, PPID
- `fd/` — all file descriptors it has open
- `maps` — memory map

So the process itself isn't a file — it's a live thing running in memory, being scheduled by the kernel. But Linux exposes it **as if** it were files so you can inspect and interact with it through the filesystem.

That's the deeper meaning of "everything is a file" — it's not that everything literally is a file, it's that Linux uses the file interface as a **universal API**. Devices, processes, sockets, hardware info — all accessible through file paths.

Clean way to think about it:
- **Process** = live thing in memory
- **`/proc/PID/`** = the kernel's window into that process, exposed as files

Now run:
```bash
cat /proc/$$/status
```

Good output. Let's decode the `STAT` column since you saw various letters.

---

### Process States

| Code | State | Meaning |
|---|---|---|
| `S` | Sleeping | Waiting for something (most processes are here) |
| `R` | Running | Actually using CPU right now |
| `D` | Uninterruptible sleep | Waiting on I/O (disk/network) — can't be killed |
| `Z` | Zombie | Finished but parent hasn't acknowledged it yet |
| `I` | Idle | Kernel thread, doing nothing |
| `T` | Stopped | Paused (Ctrl+Z does this) |

### Modifier letters (appear after the main state)

| Code | Meaning |
|---|---|
| `s` | Session leader |
| `l` | Multi-threaded |
| `+` | Foreground process |
| `<` | High priority |
| `N` | Low priority |
| `L` | Pages locked in memory |

---

Three things worth pointing out from your specific output:

**1. You have a zombie:**
```
kijuchi+   26144  0.0  0.0      0     0 ?        Z    11:42   0:00 [sd_espeak-ng]
```
A dead process whose parent hasn't cleaned it up yet. Harmless unless there are thousands.

**2. Zen browser is eating your machine:**
```
kijuchi+    3523  7.5  4.5  ...  109:00 /opt/zen/zen
```
109 minutes of CPU time. Multiple processes. That's your browser.

**3. You caught yourself:**
```
kijuchi+   40074 50.0  0.0  13904  4892 pts/1    R+   15:48   0:00 ps aux
```
`ps aux` itself at 50% CPU — you caught it in the act of running.

---

Ready to learn how to control processes — killing, pausing, backgrounding them?


## Controlling Processes

### Killing a process

```bash
kill PID              # graceful — asks process to stop
kill -9 PID           # force kill — no questions asked
killall process_name  # kill by name
pkill process_name    # kill by name pattern
```

The difference between `kill` and `kill -9`:
- `kill` sends **SIGTERM** — "please stop" — process can clean up first
- `kill -9` sends **SIGKILL** — "die now" — kernel forces it, no cleanup

Always try `kill` first. Use `-9` only when it doesn't respond.

---

### Pausing & resuming

```bash
Ctrl+Z      # pause (suspend) a running process
fg          # bring it back to foreground
bg          # resume it in the background
jobs        # list all paused/background processes
```

---

### Running in the background

```bash
command &           # start directly in background
nohup command &     # run in background, survives terminal close
```

`nohup` is important for servers — without it, closing your terminal kills the process.

---

### Practical example

Try this:
```bash
sleep 100 &
jobs
ps aux | grep sleep
kill %1        # %1 refers to job number 1 from jobs list
jobs
```

Tell me what you see at each step.

```txt
So if I run a command and put & after it, It runs in the background but when I close the terminal it closes? Short answer please
```

Yes. Use `nohup command &` to survive terminal close.

Perfect tree. A few things worth pointing out from yours:

**You can see exactly where you are:**
```
x-terminal-emul─┬─zsh───pstree
```
Your terminal → zsh → pstree. You're looking at yourself running the command.

**Your editor spawned a shell:**
```
bash───zed-editor─┬─zed-editor
                  ├─zsh
```
Zed opened a bash session which spawned zsh inside it.

**Zen browser's full madness is visible:**
```
zen─┬─forkserver─┬─Isolated Web Co (×11)
                 ├─Privileged Cont
                 ├─RDD Process
                 ├─Socket Process
                 ├─Web Content (×4)
                 └─WebExtensions
```
Every tab is a separate process. That's why it's eating your RAM.

**The zombie from earlier:**
```
speech-dispatch─┬─sd_espeak-ng───{sd_espeak-ng}
```
That's the zombie's parent — speech-dispatcher. It spawned it and never cleaned it up.

---

Now the hands-on part. Run:

```bash
sleep 100 &
jobs
ps aux | grep sleep
kill %1
jobs
```

```bash
sleep 100 &
```
Starts a process that does nothing for 100 seconds. `&` runs it in the background.

```bash
jobs
```
Lists all background/paused processes in your current terminal session.

```bash
ps aux | grep sleep
```
Searches all running processes for anything with "sleep" in the name. The `|` pipes `ps aux` output into `grep` which filters it.

```bash
kill %1
```
Kills job number 1 from your `jobs` list. `%1` refers to job 1, not PID 1.

```bash
jobs
```
Run again to confirm it's gone.

Good eye on htop. We'll come back to it.

---

## Processes vs Threads vs Jobs vs Tasks

### Process
A running program. Has its own memory space, PID, resources. Completely isolated from other processes.

### Thread
A unit of execution **inside** a process. Multiple threads share the same memory space within one process.

Think of it like this:
```
Process = a factory
Thread  = a worker inside that factory
```

A process can have many threads all working simultaneously, sharing the same resources. That's why you saw `118*[{zen}]` in your pstree — zen browser is one process with 118 threads inside it.

### Job
A shell concept only. When you run a command in your terminal, the shell calls it a job. It's just the shell's way of tracking what it started. Has no meaning outside your terminal session.

### Task
Not a strict Linux term — it's loosely used to mean either a process or a thread depending on context. In the kernel's code, processes and threads are both called tasks internally. In htop you'll see "Tasks" meaning the total count of processes + threads.

---

Summary:
| Term | Scope | Has own memory? |
|---|---|---|
| Process | OS-wide | Yes |
| Thread | Inside a process | No — shares with process |
| Job | Terminal session only | — |
| Task | Kernel internal term | Depends |

---

Your machine has 16GB RAM and you're already at 7.7GB — half gone just from idle + Zen browser. That tracks with what we saw earlier.

---

## Reading htop

### Top section — System overview

**CPU bars (your 4 cores)**
Each bar shows how much of that core is being used right now. Different colors mean:
| Color | Meaning |
|---|---|
| Green | User processes (your apps) |
| Red | Kernel/system processes |
| Blue | Low priority processes |

**Memory bar**
```
7.7GB/15.5GB
```
| Color | Meaning |
|---|---|
| Green | Used by processes |
| Blue | Buffer/cache (kernel using it for speed, will release if needed) |

**Load Average** — three numbers like `1.20 0.85 0.90`
Represents system load over last 1min, 5min, 15min. On a 4-core machine, anything under 4.0 is fine. Above 4.0 means processes are queuing for CPU.

**Uptime** — how long since last boot.

---

### Bottom section — Process list

You already know most columns from `ps aux`. New ones in htop:

| Column | Meaning |
|---|---|
| `VIRT` | Total memory process *could* use |
| `RES` | Memory it's *actually* using right now |
| `SHR` | Shared memory with other processes |
| `NI` | Nice value — priority (-20 highest, 19 lowest) |

---

### Useful htop shortcuts
| Key | Action |
|---|---|
| `F6` | Sort by column |
| `F4` | Filter by name |
| `F9` | Kill selected process |
| `F5` | Tree view |
| `t` | Toggle tree view |
| `q` | Quit |

---

Press `F5` in htop — it'll show you the process tree we saw in `pstree` but with live resource usage alongside it. What do you see?

```txt
Quick one, can a process have an infinite number of threads (say maybe theoretically or something)
```

Theoretically yes. Practically no.

The kernel has a limit. Check yours:

```bash
cat /proc/sys/kernel/threads-max
```

Also per-process, each thread needs its own stack in memory — so RAM is the real ceiling. More threads = more memory consumed.

There's also a concept called **thread exhaustion** — spawn too many threads and the system slows to a crawl or crashes because the kernel spends more time switching between threads than actually doing work. It's called **context switching overhead**.

That's actually why modern high-performance systems moved toward **async/event-driven** models — instead of one thread per task, one thread handles thousands of tasks by not blocking. That's what Node.js, nginx, and Go's goroutines are built around.

Go takes it further — goroutines aren't even real OS threads. They're lightweight "green threads" the Go runtime manages itself, multiplexed onto a small number of real OS threads. That's how Go handles millions of concurrent tasks efficiently.

You'll feel this deeply when we get to backend and DevOps work.
