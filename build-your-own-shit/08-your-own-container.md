# Build Your Own Container

**[Intermediate]** — The best effort-to-insight ratio on this list. Roughly 200 lines, one evening, and Docker stops being magical permanently.

## What you're building

A program that runs a process in isolation: its own PID space, filesystem, network, and hostname, with CPU and memory limits. `./mycontainer run alpine /bin/sh` gives you a shell that believes it's alone on the machine.

By the end **you'll run a real Alpine root filesystem in it** — the same tarball Docker uses.

**What you're deliberately not building:** an image format and registry (pulling and layering OCI images is a separate project), a daemon, an orchestrator, or full network setup with veth pairs and NAT (we'll isolate the network, not connect it).

**Why this one:** it's the shortest path to deleting a piece of mystique. [[foundations/os/11-isolation-and-containers|There is no such thing as a container]] — there are namespaces, cgroups, and a pivot_root, and after this you'll have assembled them yourself.

## What you need first

| You should know | Where |
|---|---|
| **Namespaces and cgroups** | [[foundations/os/11-isolation-and-containers\|os/11]] — **read this first; it's the spec** |
| **`fork`/`exec`, and PID 1's duties** | [[foundations/os/02-processes-and-threads\|os/02]] |
| **Mounts and the filesystem tree** | [[foundations/os/07-filesystems-and-storage\|os/07]] |
| **What Docker does from above** | [[devops/02-docker/README\|Docker]] |

**Linux only.** Namespaces and cgroups are Linux kernel features — macOS and Windows run Docker in a Linux VM for exactly this reason.

**You'll need root** (or a user namespace, which is milestone 7).

## The build order

### 0. Prove it works before writing code

Before implementing anything, do it by hand:

```bash
sudo unshare --pid --fork --mount-proc --uts --ipc --net --mount /bin/bash
# now: hostname, ps aux, ip link
```

`ps aux` shows two processes. `hostname foo` doesn't affect the host. **You just made a container with one command** — everything below is doing this programmatically.

> Run this once before starting. It converts the whole project from "how do I build a container" into "how do I call these five syscalls".

### 1. Run a command

Plain `fork`/`exec`, no isolation yet — the skeleton.

```
./mycontainer run /bin/echo hello
```

**Test:** it runs the command and exits with the child's status.

**Watch for:** the same [[build-your-own-shit/07-your-own-shell|`fork`/`exec` mechanics]] as the shell guide. If you built that, this milestone is copy-paste.

### 2. UTS namespace — a hostname of its own

The gentlest namespace, and a good first success.

```c
clone(child_fn, stack_top, CLONE_NEWUTS | SIGCHLD, arg);
// in the child:
sethostname("container", 9);
```

**Test:** inside, `hostname` shows `container`. Outside, unchanged.

**Watch for:** `clone` is not `fork` — it takes a function pointer and a **stack you allocate yourself**, growing downward, so you pass the *top*. Getting this wrong is an immediate segfault.

### 3. PID namespace — being PID 1

```c
clone(child_fn, stack_top, CLONE_NEWPID | CLONE_NEWUTS | SIGCHLD, arg);
```

**Test:** inside, `echo $$` prints 1.

**Watch for:** `ps` still shows every host process until you fix `/proc` in the next milestone — the namespace is active, but `/proc` is still the host's.

**And you're now PID 1**, which has duties: reap orphaned children, and handle signals explicitly (the kernel applies no default handlers to PID 1). This is exactly the "container PID 1 problem" and why `docker run --init` exists. → [[foundations/os/02-processes-and-threads|Processes and Threads]]

### 4. Mount namespace and a root filesystem

Grab a real root filesystem:

```bash
mkdir -p rootfs && cd rootfs
curl -sL https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-minirootfs-3.20.0-x86_64.tar.gz | tar xz
```

Then, in the child with `CLONE_NEWNS`:

```c
mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL);   // don't leak mounts to the host
mount("rootfs", "rootfs", NULL, MS_BIND, NULL);      // bind-mount it onto itself
// pivot_root into it, then unmount the old root
mount("proc", "/proc", "proc", 0, NULL);             // now ps works correctly
```

**Test:** inside, `ls /` shows Alpine's filesystem. `ps aux` shows only your processes. `cat /etc/alpine-release` works.

**Watch for — the two that catch everyone:**

**`MS_REC | MS_PRIVATE` on `/` first.** Without it your mounts propagate to the host, and unmounting inside affects the parent. This is the most common bug in a hand-rolled container.

**`pivot_root`, not `chroot`.** `chroot` is escapable by a process with `CAP_SYS_CHROOT` — a few lines of C gets you out. `pivot_root` combined with unmounting the old root is the real boundary. → [[foundations/os/11-isolation-and-containers|Isolation]]

**Mount `/proc` after pivoting**, or `ps` reads the host's.

### 5. Network namespace

```c
clone(..., CLONE_NEWNET | ..., ...);
```

**Test:** inside, `ip link` shows only `lo`, and it's down. No network access at all.

**Watch for:** **complete isolation is the easy part; connectivity is the work.** Giving the container a network means creating a veth pair, moving one end into the namespace, assigning addresses, adding routes, and setting up NAT with iptables:

```bash
ip link add veth0 type veth peer name veth1
ip link set veth1 netns <pid>
ip addr add 172.18.0.1/24 dev veth0 && ip link set veth0 up
# then inside: configure veth1, add a default route
# then on the host: iptables -t nat -A POSTROUTING -s 172.18.0.0/24 -j MASQUERADE
```

**That's a legitimate place to stop.** Isolating the network demonstrates the namespace; wiring it up is networking work rather than container work. → [[foundations/networking/README|networking]]

### 6. cgroups — resource limits

Namespaces control what a process *sees*; cgroups control what it can *use*.

```c
mkdir("/sys/fs/cgroup/mycontainer", 0755);
write_file("/sys/fs/cgroup/mycontainer/memory.max", "100M");
write_file("/sys/fs/cgroup/mycontainer/cpu.max", "50000 100000");   // 0.5 CPU
write_file("/sys/fs/cgroup/mycontainer/pids.max", "100");
write_file("/sys/fs/cgroup/mycontainer/cgroup.procs", pid_string);
```

**Test:**

```bash
# inside, with memory.max=100M:
dd if=/dev/zero of=/dev/null bs=200M count=1     # gets OOM-killed
# with pids.max=100, a fork bomb hits the limit instead of taking down the host
:(){ :|:& };:
```

**Watch for:** writing the PID into `cgroup.procs` is what applies the limits. Order matters — do it before `exec` so the process is constrained from the start.

**CPU limits throttle, they don't slow.** Exhaust the quota early in a period and everything freezes until the next one. Check `cpu.stat`'s `nr_throttled`. → [[foundations/os/03-scheduling|Scheduling]]

Clean up the cgroup directory when the container exits, or you leak them.

### 7. User namespace — root without root

```c
clone(..., CLONE_NEWUSER | ..., ...);
// then write the uid/gid maps from the PARENT:
// /proc/<pid>/uid_map:  "0 1000 1"   → uid 0 inside == uid 1000 outside
```

**Test:** run the whole thing **as an unprivileged user**. Inside, `id` shows uid 0.

**Watch for:** the mapping must be written by the parent, and `/proc/<pid>/setgroups` must be set to `deny` before writing `gid_map` (a security requirement).

> **This is the milestone that makes it genuinely interesting.** Root inside maps to an unprivileged user outside, so an escape lands you as nobody rather than root. It's what makes rootless Podman possible — and Docker still doesn't enable it by default.

### 8. Layered filesystem with overlayfs

How images actually work:

```c
mount("overlay", "merged", "overlay", 0,
      "lowerdir=base:layer1,upperdir=diff,workdir=work");
```

Read-only lower layers plus one writable upper layer. Fifty containers from one image share the lower layers on disk *and* in the page cache.

**Test:** run two containers from the same `lowerdir`. Write a file in one; confirm it doesn't appear in the other, and that the base is unmodified.

**Watch for:** **copy-up** — modifying a file from a lower layer copies the *whole file* up first. Appending one line to a 2GB file copies 2GB. That's why write-heavy paths belong on a volume. → [[devops/02-docker/README|Docker]]

### 9. Capabilities and seccomp (optional)

```c
// drop everything except what's needed
cap_drop_all_except(CAP_NET_BIND_SERVICE);

prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0);      // required before seccomp
seccomp_load(ctx);                            // filter the syscall surface
```

**Test:** inside, `mount` fails with EPERM even as root.

**Watch for:** `PR_SET_NO_NEW_PRIVS` must be set first or seccomp refuses to load. Dropping `CAP_SYS_ADMIN` is the single highest-value capability restriction — it covers so much that having it is close to being root.

## Per-language toolkit

| Milestone | C | Rust | Go | Python |
|---|---|---|---|---|
| **clone/namespaces** | `clone()` directly | `nix::sched::clone` | `SysProcAttr.Cloneflags` | `ctypes` → libc |
| **mount/pivot_root** | `mount`, `pivot_root` | `nix::mount` | `syscall.Mount` | `ctypes` |
| **cgroups** | write files | write files | write files | write files |
| **Capabilities** | `libcap` | `caps` crate | `syscall` | `python-prctl` |
| **seccomp** | `libseccomp` | `seccompiler` | `libseccomp-golang` | `pyseccomp` |

**Language notes:**

**Go is unusually good here** — `syscall.SysProcAttr` exposes `Cloneflags`, `Unshareflags`, `UidMappings` and `GidMappings` declaratively, and it's what Docker and containerd are written in. The famous ["Containers From Scratch"](https://www.youtube.com/watch?v=8fi7uSYlOdc) talk does it in ~100 lines of Go.

The one catch: **Go's runtime is multithreaded, and namespace operations are per-thread**, so `CLONE_NEWUSER` and `unshare` from Go need care — the usual pattern is re-executing yourself (`/proc/self/exe`) with the flags set, which is exactly what Docker does.

**C** is the most direct — `clone`, `mount`, `pivot_root` are right there, and you see exactly which syscall does what.

**Rust** with `nix` gives you the raw calls with better types.

**Python** works via `ctypes` and is good for exploring, awkward for the `clone` stack handling.

**Recommendation: Go for the shortest path, C to see the syscalls plainly.**

## The parts that will bite you

**Forgetting `MS_REC | MS_PRIVATE` on `/`.** Your mounts leak to the host and you'll wonder why unmounting inside broke your desktop.

**Using `chroot` instead of `pivot_root`.** Escapable, and the whole point is a boundary.

**Mounting `/proc` before pivoting.** You get the host's process list.

**`clone`'s stack.** You allocate it and pass the *top*, not the bottom.

**PID 1 duties.** No default signal handlers, and orphans become your children to reap.

**cgroup v1 vs v2.** The layouts differ completely. Modern distributions are v2 (unified); check `stat -fc %T /sys/fs/cgroup` — `cgroup2fs` means v2. Most older tutorials are v1.

**Leaked cgroup directories** if you don't clean up on exit.

**`setgroups` before `gid_map`.** A required security step that fails confusingly.

## How to know it works

```bash
sudo ./mycontainer run ./rootfs /bin/sh

# inside:
hostname                  # your chosen name
echo $$                   # 1
ps aux                    # only your processes
ls /                      # Alpine's filesystem
ip link                   # only lo
cat /proc/self/cgroup     # your cgroup
id                        # uid 0 (and unprivileged outside, if milestone 7)
```

**Compare against the real thing** at each step:

```bash
docker run --rm -it alpine /bin/sh      # what does the real one show?
sudo lsns                                # every namespace, and which PIDs are in them
ls -l /proc/<pid>/ns/                    # your container's namespace IDs vs the host's
```

`lsns` and `/proc/<pid>/ns/` are how you *prove* isolation happened — the namespace inode numbers differ from the host's.

**Test the limits destructively:** a fork bomb should hit `pids.max` rather than taking down your machine; a memory hog should be OOM-killed inside the cgroup, not by the host's OOM killer.

**Escape testing** is the real security check. Try `mount`, try accessing a host path, try `nsenter`. If you skipped `pivot_root` for `chroot`, a known escape gets out.

## Where to stop

**Stop after cgroups (milestone 6), or after user namespaces (7) for the satisfying version.** You'll have learned:

- That a container is namespaces + cgroups + `pivot_root` — no more
- Why your app becomes PID 1 and what that costs you
- Why `--init` and `tini` exist
- Why CPU limits cause latency spikes rather than gradual slowdown
- Why containers share the kernel, and what that means for isolation
- How overlayfs makes fifty containers from one image nearly free

**Real runtimes additionally have:** the OCI image and runtime specs, registry pull with layer deduplication, full CNI networking, volume management, checkpoint/restore, rootless with subuid mapping, and integration with systemd, SELinux and AppArmor.

**And the boundary is real:** namespaces isolate *views*, not the kernel. A kernel vulnerability is a shared failure domain. For untrusted code you need gVisor or a microVM like Firecracker. → [[foundations/os/11-isolation-and-containers|Isolation and Containers]]

**If you want to go further:** implement **image pulling** — fetch an OCI image from a registry, unpack the layers, and assemble them with overlayfs. It's the other half of Docker, and it's mostly HTTP and tar rather than kernel work.

---

## Related
- [[foundations/os/11-isolation-and-containers|Isolation and Containers]] — the specification for this project
- [[devops/02-docker/README|Docker]] — the same thing from above
- [[build-your-own-shit/07-your-own-shell|Your Own Shell]] — the `fork`/`exec` skeleton
- [[cybersecurity/09-cloud-security/README|Cloud Security]] — container escape as a threat model
- [[build-your-own-shit/README|build-your-own-shit]]
