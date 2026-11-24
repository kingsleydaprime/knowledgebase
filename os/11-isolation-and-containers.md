---
id: 264f60d8-12e1-4d80-b3a6-9d083fe0a942
---

# Isolation and Containers

A container is an ordinary program that the operating system has fenced off, so it sees only its own files, network and processes, and can use only a set share of the machine. Tools like Docker build containers out of these fences. This lesson shows what each fence does, which helps when a container won't start.

## The claim
<!-- bite: 1ffb3a02-93a3-496f-80e5-64419749acf2 -->

> **A container is not a kernel object.** There is no `container` struct, no `create_container()` syscall, and nothing in `/proc` called a container. It's an ordinary Linux process with several isolation features switched on at once.

Understanding the pieces makes container behaviour predictable instead of magical — and it's what lets you debug a container that won't start.

## Namespaces — what a process can *see*
<!-- bite: 5b1ee96d-176e-45c8-875c-b0a79b0c2517 -->

Each namespace virtualises one global resource, so processes inside see a different view.

| Namespace | Isolates | Flag |
|---|---|---|
| **PID** | process IDs — your PID 1 is the host's PID 4823 | `CLONE_NEWPID` |
| **Mount** | the filesystem tree | `CLONE_NEWNS` |
| **Network** | interfaces, routes, ports, iptables | `CLONE_NEWNET` |
| **UTS** | hostname, domain name | `CLONE_NEWUTS` |
| **IPC** | System V IPC, POSIX message queues | `CLONE_NEWIPC` |
| **User** | uid/gid mappings — **root inside, unprivileged outside** | `CLONE_NEWUSER` |
| **Cgroup** | the cgroup root as seen from inside | `CLONE_NEWCGROUP` |
| **Time** | boot and monotonic clock offsets | `CLONE_NEWTIME` |

```c
clone(child_fn, stack, CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET | SIGCHLD, NULL);
unshare(CLONE_NEWNS);                    // move the CURRENT process into a new namespace
setns(fd, CLONE_NEWNET);                 // JOIN an existing one — this is `docker exec`
```

```bash
lsns                                      # every namespace on the system
ls -l /proc/<pid>/ns/                     # which ones a process is in
nsenter -t <pid> -n ss -tlnp              # run a command in another process's netns
unshare --user --map-root-user --pid --fork --mount-proc bash    # a container, by hand
```

That last command gives you a shell that believes it's root with PID 1 — no Docker involved. **Running it once makes containers permanently unmysterious.**

Three consequences worth knowing:

**PID namespaces explain the PID 1 problem.** Your app becomes PID 1, which has special duties: it must reap orphaned children, and **the kernel doesn't apply default signal handlers to it**. A process with no explicit `SIGTERM` handler ignores it entirely as PID 1 — so `docker stop` waits 10 seconds and then `SIGKILL`s. That's why `--init` and `tini` exist. → [[os/10-signals-and-ipc|Signals]]

**Network namespaces are why containers need veth pairs and NAT.** A container's netns has no interfaces at all; the runtime creates a virtual ethernet pair, puts one end inside, and bridges the other.

**User namespaces are the security story.** Root inside maps to an unprivileged uid outside, so a container escape lands you as nobody rather than root. It's what makes rootless Podman possible, and Docker still doesn't enable it by default.

## cgroups — what a process can *use*
<!-- bite: f00169a9-9d6d-4593-9680-0ed7c5946b0a -->

Namespaces control visibility; cgroups control **resource consumption**.

cgroup v2 is a single unified hierarchy (v1 had a separate tree per controller, which was a mess):

```bash
/sys/fs/cgroup/
├── cpu.max              # "200000 100000" = 2 CPUs per 100ms period
├── cpu.weight           # relative share under contention (default 100)
├── cpu.stat             # nr_throttled, throttled_usec  ← CHECK THIS
├── memory.max           # hard limit — exceed it and you're OOM-killed
├── memory.high          # soft limit — throttle and reclaim instead
├── memory.current
├── memory.events        # oom_kill counter
├── io.max               # IOPS and bandwidth limits per device
├── pids.max             # fork-bomb protection
└── mygroup/             # nested — limits compose downward
```

```bash
mkdir /sys/fs/cgroup/mygroup
echo "200000 100000" > /sys/fs/cgroup/mygroup/cpu.max
echo $$ > /sys/fs/cgroup/mygroup/cgroup.procs      # move this shell into it
```

**The two operationally important behaviours**, both covered in more depth elsewhere but worth stating together:

**CPU throttling is a cliff, not a slope.** Exhaust your quota 40ms into a 100ms period and every thread freezes for 60ms. The symptom is p99 latency spikes at low average CPU. Check `nr_throttled`. → [[os/03-scheduling|Scheduling]]

**Memory limits kill; they don't slow.** Hitting `memory.max` triggers an OOM kill inside the cgroup — exit code 137, `OOMKilled` in Kubernetes. `memory.high` applies reclaim pressure instead, and is usually what you actually want. → [[os/04-virtual-memory|Virtual Memory]]

**And runtimes must be told the limits**, because they read the host's CPU count and RAM:

```bash
GOMEMLIMIT=450MiB                      # Go
-XX:MaxRAMPercentage=75                 # JVM
go.uber.org/automaxprocs                # Go GOMAXPROCS from the quota
```

This single misconfiguration — a runtime sizing itself from the host — explains a large share of "slow in Kubernetes, fine locally".

## The filesystem: chroot, pivot_root, overlayfs
<!-- bite: 177e64fb-a038-4a3b-90fe-2f94a00589f4 -->

```c
chroot("/new/root");     // change the apparent root — WEAK, escapable if you have privileges
pivot_root(new, old);    // properly swap the root mount — what runtimes actually use
```

`chroot` alone is not a security boundary: a process with `CAP_SYS_CHROOT` can escape it in a few lines. `pivot_root` combined with a mount namespace is the real mechanism.

**overlayfs** is what makes images work:

```text
        ┌──────────────────────────┐
merged  │  what the container sees │
        ├──────────────────────────┤
upper   │  writable layer          │  ← all writes land here
        ├──────────────────────────┤
lower   │  image layer 3 (RO)      │
        │  image layer 2 (RO)      │  ← shared between ALL containers of this image
        │  image layer 1 (RO)      │
        └──────────────────────────┘
```

Read-only image layers plus one writable layer. Fifty containers from one image share the lower layers on disk and in the page cache.

**Copy-up is the performance gotcha:** modifying a file that lives in a lower layer copies the **entire file** to the upper layer first. Appending one line to a 2GB file in an image copies 2GB. Write-heavy paths belong on a volume, not the container filesystem. → [[devops/03-docker/index|Docker]]

## Capabilities
<!-- bite: 61f6400c-66f2-49fb-a795-92e5bdc40d5b -->

Root's powers, split into ~40 separate privileges, so you don't need full root for one thing:

```bash
CAP_NET_BIND_SERVICE     # bind ports < 1024
CAP_NET_ADMIN            # configure interfaces, iptables
CAP_SYS_ADMIN            # a grab-bag; effectively root — avoid granting it
CAP_SYS_PTRACE           # attach a debugger to other processes
CAP_CHOWN, CAP_SETUID, CAP_DAC_OVERRIDE
```

```bash
capsh --print                                       # what do I have?
getcap /usr/bin/ping                                 # file capabilities
setcap cap_net_bind_service=+ep ./myserver           # bind :80 without being root
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE ...
```

**`--cap-drop=ALL` then add back what you need** is the correct posture. `CAP_SYS_ADMIN` is the one to be suspicious of — it covers so much that granting it is close to granting root.

## seccomp
<!-- bite: 041fa1ac-2bc6-4896-991c-e7b097c127da -->

Filter which **syscalls** a process may make, using a BPF program:

```c
prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);      // required first — no setuid escalation
seccomp_load(ctx);
```

Docker applies a default profile blocking ~44 syscalls (`kexec_load`, `mount`, `ptrace`, `bpf`…). It's a meaningful reduction in kernel attack surface — most container escapes have gone through a syscall a normal application never makes.

```bash
docker run --security-opt seccomp=profile.json ...
grep Seccomp /proc/<pid>/status              # 0=off 1=strict 2=filtered
```

This is also why **`io_uring` is disabled in some environments** — it's a large new syscall surface with a history of vulnerabilities. → [[os/08-io-models|I/O Models]]

## LSMs, and what containers don't isolate
<!-- bite: 6a915c6a-827a-4e20-80fa-8db1abda850d -->

**SELinux / AppArmor** add mandatory access control on top — labels and policies the process cannot override even as root.

But the fundamental limit:

> **Containers share one kernel.** A kernel vulnerability is a shared failure domain. Namespaces isolate *views*, not the kernel itself.

Not isolated by default: the kernel, `/proc/sys` (partly), the system clock (without a time namespace), and kernel modules. A container that can load a module owns the host.

When you need a real boundary — untrusted or multi-tenant code — you need a VM or a sandboxed runtime:

| | Isolation | Cost |
|---|---|---|
| **runc** (standard) | namespaces + cgroups | none |
| **gVisor** | a user-space kernel intercepting syscalls | ~10–30% overhead |
| **Kata / Firecracker** | a real VM per container | ~125ms boot, more memory |

Firecracker is what AWS Lambda uses — microVM boundaries with near-container startup.

## Assembling one
<!-- bite: 332c1204-9385-4a74-8489-1fa106173f6d -->

Everything a container runtime does, in order:

1. **`clone`** with the namespace flags
2. **`pivot_root`** into the overlayfs mount
3. **Mount** `/proc`, `/sys`, `/dev` inside the new mount namespace
4. **Write** the PID into a cgroup
5. **Set up** the veth pair and routes
6. **Drop** capabilities, apply seccomp, set the LSM label
7. **`setuid`** to a non-root user
8. **`execve`** the entrypoint

```bash
# steps 1-3, roughly, by hand:
unshare --user --map-root-user --pid --fork --mount --net --uts --ipc \
        --mount-proc chroot ./rootfs /bin/sh
```

That's the whole trick. **Docker is a convenient wrapper around eight kernel features.**

---

## Check your understanding
<!-- bite: a5967cef-2da7-4a9b-8ca1-e792b9c7678f -->

Try each one before you open the answer.

1. <!-- q: gap id="5bf89a9b" answers="namespaces|namespace;cgroups|cgroup|control groups" -->
   A container is an ordinary process. Linux ___ control what it can see (its own PIDs, mounts and network), and ___ control how much it can use (CPU, memory, I/O).

   <details><summary>Answer</summary>

   Namespaces, then cgroups. There is no "container" object in the kernel; the runtime combines these with a few other features.

   </details>

2. <!-- q: mcq id="2b1f2556" -->
   Which namespace makes "root" inside a container map to an unprivileged user on the host?

   - [ ] PID
   - [ ] Mount
   - [x] User
   - [ ] UTS

   <details><summary>Answer</summary>

   The user namespace. A process that escapes the container then lands as nobody rather than root. It's what makes rootless Podman possible.

   </details>

3. <!-- q: mcq id="4c7a59bc" -->
   What does `docker exec` use to run a command inside a running container?

   - [ ] `fork` from the container's PID 1
   - [x] `setns`, to join the container's existing namespaces
   - [ ] SSH into the container
   - [ ] `chroot` into the image

   <details><summary>Answer</summary>

   `setns`. A new process joins the namespaces the container already has. `nsenter` does the same from the command line.

   </details>

4. <!-- q: open id="f5d44781" -->
   A container image includes a 1.5 GB data file. The app appends one line to it at startup, and every new container uses 1.5 GB of extra disk. Why?

   <details><summary>Answer</summary>

   overlayfs copy-up. The image layers are read-only, so changing a file from a lower layer first copies the whole file into the container's writable upper layer. Keep files that change in a volume, not in the image.

   </details>

5. <!-- q: mcq id="07eb0dab" -->
   A web server in a container only needs to bind port 80. What is the right capability setup?

   - [ ] Run it as full root
   - [ ] Add `CAP_SYS_ADMIN`
   - [x] `--cap-drop=ALL --cap-add=NET_BIND_SERVICE`
   - [ ] No capabilities are needed for ports below 1024

   <details><summary>Answer</summary>

   Drop everything and add back the one it needs. `CAP_SYS_ADMIN` covers so much that granting it is close to granting root.

   </details>

6. <!-- q: open id="0bf04c58" -->
   You must run untrusted code from many customers on one host. Why isn't a standard container enough, and what would you use?

   <details><summary>Answer</summary>

   All containers share one kernel, so a kernel bug is a shared failure: namespaces isolate views, not the kernel itself. For untrusted multi-tenant code, use a stronger boundary: gVisor (a user-space kernel that intercepts syscalls) or a microVM per workload such as Firecracker or Kata, which is what AWS Lambda uses.

   </details>

## Related
<!-- bite: d4c511a6-2831-426b-8f57-ca87006ee90d -->
- [[os/03-scheduling|Scheduling]] — cgroup CPU throttling
- [[os/04-virtual-memory|Virtual Memory]] — cgroup memory limits and the OOM killer
- [[devops/03-docker/index|Docker]] — the same thing from above
- [[devops/10-orchestration/index|Orchestration]] — where the limits get set
- [[cybersecurity/09-cloud-security/index|Cloud Security]] — container escape as a threat model
- [[os/index|OS course map]]

## About this lesson
<!-- bite: 4900d1ea-02f0-4092-863c-0cba0d375cbe -->

**Level:** Intermediate → Advanced. **Covers:** Containers from below. There is no such thing as a container — there are namespaces, cgroups, and a chroot, assembled by a tool.
