# DevOps Interview — Linux, Containers & Operations

From [[devops/01-linux/README|01-linux]], [[devops/02-docker/README|02-docker]], [[devops/06-ci-cd/README|06-ci-cd]], [[devops/10-observability/README|10-observability]].

---

### Q1. [Intermediate] 🔥 A server is at 100% CPU. Walk me through it.

**Strong answer covers a method:**
1. **`top` / `htop`** — one process or many? And **check the load average against core count** — load 8 on 8 cores is saturated but healthy; load 80 is a queue.
2. **Distinguish `us` from `sy` from `wa`.** High **user** = application compute. High **system** = syscall churn (often excessive I/O or context switching). High **iowait** = it's *not* CPU-bound at all, it's blocked on disk — a completely different investigation.
3. **`pidstat -t` / `top -H`** — which *thread*? In a JVM, map the thread ID to a Java thread with a thread dump.
4. **Profile it** — `perf top`, or async-profiler for a JVM. Get a flame graph rather than guessing.
5. **Check whether it's a symptom.** A GC death spiral, a retry storm, or a lock convoy all present as 100% CPU while the root cause is elsewhere.

**What scores:** naming the `us`/`sy`/`wa` split. It's the fastest branch in the whole investigation and most people skip straight to "restart it."

---

### Q2. [Intermediate] 🔥 Disk is full. Find and fix it.

**Strong answer covers:**
```sh
df -h                                  # which filesystem
du -sh /* 2>/dev/null | sort -rh | head # walk down from the top
du -sh /var/log/* | sort -rh | head
```

**The trap that makes this question interesting:** `df` says full but `du` doesn't account for it. That means a **deleted file is still held open by a process** — the inode isn't freed until the last descriptor closes. Classic case: log rotation removed the file but the application still holds it and keeps writing to a file nobody can see.

```sh
lsof +L1        # files with zero links still open — the smoking gun
```
Fix by restarting the process or truncating via `/proc/<pid>/fd/<n>`.

**The other trap:** `df -i` — you can exhaust **inodes** while having free space, typically from millions of tiny files (a cache directory, or a mail queue). "No space left on device" with free space showing is this.

---

### Q3. [Intermediate] 🔥 What is a container, actually? How is it different from a VM?

**Strong answer covers:** a container is **a process on the host kernel with restricted visibility**. There is no container object in the kernel — it's a combination of:
- **Namespaces** — what the process can *see* (PID, network, mount, UTS, IPC, user, cgroup). This is the isolation.
- **Cgroups** — what the process can *use* (CPU, memory, I/O limits). This is the resource control.
- **Union filesystem** (overlayfs) — layered images with a thin writable layer on top. This is why images are cacheable and cheap to ship.

**Versus a VM:** a VM virtualises *hardware* and runs its own kernel, so isolation is much stronger but startup is seconds and overhead is gigabytes. A container shares the host kernel — milliseconds to start, megabytes of overhead, **weaker isolation**.

**The security consequence to state:** a kernel exploit escapes a container but not (usually) a VM. That's why multi-tenant platforms run untrusted workloads in lightweight VMs (Firecracker, gVisor) rather than plain containers. And it's why `--privileged` and mounting the Docker socket are effectively root on the host.

---

### Q4. [Intermediate] 🔥 How do you make a Docker image small and secure?

**Strong answer covers:**
- **Multi-stage build** — compile in a full image, copy only the artifact into a minimal runtime. Often 1 GB → 100 MB.
- **Order layers by change frequency** — dependency manifests and install *before* application source, so a code change doesn't invalidate the dependency layer. Massive CI speedup and the most common thing people get wrong.
- **`.dockerignore`** — keep `.git`, `node_modules`, and secrets out of the build context.
- **Run as non-root** with an explicit `USER`. Containers default to root, and that root is (namespaced but) host root in many escape scenarios.
- **Pin base image versions** — `:latest` makes builds non-reproducible.
- **Distroless or Alpine** for the runtime, with the caveat that Alpine uses musl, which has caused real DNS-resolution and glibc-compatibility surprises.
- **Scan images** (Trivy/Grype) in CI.

**The one to say last, because it's the most important:** **secrets never go in an image.** A layer is immutable — deleting a file in a later layer doesn't remove it from the earlier one; anyone can `docker history` it out. Use build secrets or runtime injection.

---

### Q5. [Intermediate] What actually happens when you run `kubectl apply`?

**Strong answer covers:** the manifest goes to the **API server** (authn → authz → admission controllers → validation) and is persisted to **etcd**. That's it — the request is done. Everything after is asynchronous reconciliation:

- The **deployment controller** notices a Deployment with no matching ReplicaSet and creates one.
- The **ReplicaSet controller** notices it has 0 of 3 pods and creates Pod objects.
- The **scheduler** notices unscheduled pods and binds each to a node (filter feasible nodes, then score).
- The **kubelet** on that node notices a pod bound to it, pulls images, and asks the container runtime to start it.

**The concept to name — this is the actual answer:** the **reconciliation loop**. Every controller watches for a difference between desired and actual state and takes one step to close it. It's declarative, level-triggered rather than edge-triggered, so a missed event doesn't break anything — the next loop sees the same difference. That's why Kubernetes is resilient to controller restarts, and it's the same control-plane/data-plane split as [[foundations/networking/04-routing|routing]].

---

### Q6. [Intermediate] 🔥 What makes a good CI/CD pipeline?

**Strong answer covers:**
- **Fast feedback.** Under 10 minutes for PR checks or people stop reading them. Cheap checks first (lint, typecheck), expensive ones later; parallelise.
- **Build once, promote the artifact.** The exact binary tested in staging is the one deployed to production. Rebuilding per environment means you deployed something you never tested.
- **Config from environment, secrets from a secret manager** — never baked into the image.
- **Reproducible** — pinned dependencies, pinned base images, a lockfile.
- **Rollback is a first-class path**, tested. "We'll roll forward" is a plan that fails at 3am.
- **The pipeline is the only way to production.** Manual deploys mean the pipeline's guarantees are optional.

**Deployment strategies:** rolling (default, gradual), blue-green (instant switch and instant rollback, double the resources), canary (small traffic slice first, needs good metrics to judge it). **Feature flags** decouple deploy from release entirely, which is the most useful idea here — you can ship code dark and turn it on separately.

---

### Q7. [Intermediate] 🔥 Logs, metrics, and traces — what is each for?

**Strong answer covers:**
- **Metrics** — aggregated numbers over time. Cheap, bounded cardinality, good for alerting and dashboards. Answers *"is something wrong?"*
- **Logs** — discrete events with detail. Expensive at volume, good for forensics. Answers *"what exactly happened to this request?"*
- **Traces** — one request's path across services with timing per hop. Answers *"where did the time go?"* — indispensable the moment you have more than a couple of services.

**The rule:** alert on metrics, debug with traces, confirm with logs.

**Details that show experience:** **high-cardinality labels destroy a metrics system** — putting a user ID or request ID in a Prometheus label creates a separate time series per value and will take down your Prometheus. That's what logs and traces are for. And **structured logging** (JSON with a correlation/trace ID) is what makes logs joinable to traces; without a correlation ID, logs across services are unusable.

**On alerting:** alert on **symptoms users feel** (error rate, latency SLO burn), not causes (CPU is high). Cause-based alerts page you for things that don't matter and miss things that do.

---

### Q8. [Intermediate] Explain Linux file permissions, and what `chmod 777` really does.

**Strong answer covers:** three triads — owner, group, other — each with read(4)/write(2)/execute(1). On a **directory**, the meanings shift and this is the part people get wrong: `r` = list contents, `w` = create/delete entries *within* it, `x` = traverse into it. You can have `x` without `r` (enter but not list) — which is how `/home/user` is often set up.

**`chmod 777`:** everyone can read, write, and execute. It's not a fix, it's giving up — and it's frequently the actual vulnerability. When someone reaches for it, the real problem is nearly always ownership or a missing `x` on a parent directory.

**Special bits worth knowing:** **setuid** (run as the file's owner — how `passwd` works, and a classic privilege-escalation target), **setgid**, and the **sticky bit** on `/tmp` (anyone can create, only the owner can delete — otherwise any user could delete anyone's temp files).

---

### Q9. [Intermediate] What's the difference between a process, a thread, and what does a zombie mean?

**Strong answer covers:** a **process** has its own address space; a **thread** shares it with its siblings. On Linux both are tasks to the scheduler — `clone()` with different flags decides what's shared.

**A zombie** is a process that has exited but whose parent hasn't `wait()`ed to collect its exit status. It holds no memory, just a PID table entry. **Many zombies = a bug in the parent**, not in the child.

**Where this bites in practice:** running an application as **PID 1 in a container**. PID 1 has special responsibilities — it must reap orphaned children and it doesn't get default signal handlers. An app that doesn't reap accumulates zombies; an app that ignores `SIGTERM` gets `SIGKILL`ed after the grace period and loses in-flight requests. That's what `--init` / `tini` exists for, and it's a great practical answer.

---

### Q10. [Intermediate] 🔥 Production is down. What do you do in the first five minutes?

**Strong answer covers, in this order:**
1. **Mitigate before diagnosing.** Roll back the last deploy, fail over, or shed load. Restoring service is the priority; understanding it is the follow-up. People invert this and spend 40 minutes on root cause while users are down.
2. **Communicate.** Post in the incident channel, say what you know and what you're doing. Silence during an incident is its own problem.
3. **Check what changed.** Deploys, config changes, feature flags, certificate expiry, a dependency's status page. **Most incidents are caused by a change**, so "what changed in the last hour" has the highest prior.
4. **Look at the golden signals** — latency, traffic, errors, saturation.
5. **Preserve evidence** before restarting — a thread dump, a heap dump, the logs. A restart fixes the symptom and destroys the diagnosis.

**Afterwards:** a **blameless postmortem** with a real root cause (ask why more than once), and action items with owners. The point that lands: *"the goal is finding the systemic gap that let a human error become an outage, not finding who typed it."* Blame-driven postmortems produce hidden incidents, which is strictly worse than the original problem.
