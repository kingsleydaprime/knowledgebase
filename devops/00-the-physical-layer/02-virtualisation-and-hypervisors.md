# Virtualisation and Hypervisors

> **[Beginner → Intermediate]** · The layer that turned one machine into many, why containers are not a smaller version of it, and the trade you're making either way.

The previous note ended on four problems with one-app-per-server: underutilisation, slow scaling, duplicated environments, hardware-shaped backups. **All four are solved by changing what you hand out.** Stop allocating physical machines. Allocate slices of one.

## The idea

A **hypervisor** (also: virtual machine monitor) sits between the hardware and the operating systems, and presents each guest OS with what looks like its own complete machine — its own CPUs, memory, disks, network cards.

The guest OS is not modified and is not told. It boots, probes for hardware, finds a plausible machine, and installs itself. **The deception is the product.** That's why you can run Windows and three Linuxes on one box: each believes it has the whole thing.

```
┌─────────┬─────────┬─────────┐
│  VM 1   │  VM 2   │  VM 3   │  ← guest OS in each, complete and independent
│ Linux   │ Windows │ Linux   │
├─────────┴─────────┴─────────┤
│         Hypervisor          │  ← divides the real resources
├─────────────────────────────┤
│  Physical server: CPU/RAM/  │
│  disk/NIC                   │
└─────────────────────────────┘
```

Each VM gets **virtual** instances of the real components: vCPUs, virtual disks (a file on the host, usually), virtual NICs on a virtual switch.

## Type 1 and Type 2

The only structural distinction worth memorising, and it's simply *what's underneath the hypervisor*.

| | **Type 1 (bare metal)** | **Type 2 (hosted)** |
|---|---|---|
| Runs on | The hardware directly | On top of a normal OS |
| Carries | Its own minimal kernel | Nothing — borrows the host's |
| Overhead | Low | Higher (two schedulers, two memory managers) |
| Examples | VMware ESXi, Xen, Hyper-V, **KVM** | VirtualBox, VMware Workstation, UTM |
| Where | Data centres, **every cloud provider** | Your laptop |

**Everything you rent in a cloud is a guest on a Type 1 hypervisor.** AWS ran Xen for years and moved to a KVM-derived stack (Nitro) that pushes virtualisation work onto dedicated hardware cards, so the host CPU spends nearly all its cycles on your workload. That's the direction of travel across the industry: make the tax approach zero by moving it off the general-purpose CPU.

Type 2 is for a laptop lab — a Linux VM on a Windows machine, a [[cybersecurity/02-ethical-hacking/05-home-lab-setup|pentest lab]], testing an installer.

**KVM is the interesting edge case:** it's a Linux kernel module that turns the kernel itself into a Type 1 hypervisor. So it's genuinely bare metal, while looking like software you installed on an OS. Most of the world's cloud compute runs on it.

## What the hardware does for you

Early virtualisation was slow because privileged instructions had to be trapped and emulated in software. Then Intel (VT-x) and AMD (AMD-V) added a mode where guest code runs directly on the CPU at near-native speed, with the hypervisor invoked only on genuine transitions.

Two more that matter operationally:

- **EPT / NPT** (nested page tables) — the CPU translates guest-virtual → guest-physical → host-physical in hardware. Without it, the hypervisor maintains shadow page tables in software, which is as expensive as it sounds.
- **SR-IOV** — a physical NIC presents itself as several independent virtual NICs, and a VM talks to hardware directly. Removes the hypervisor from the data path.

**The practical consequence: CPU and memory virtualisation are close to free; I/O is where the overhead lives.** If a virtualised workload is slow, look at disk and network before you look at compute.

## Oversubscription — the economics, and the trap

You can allocate 128 vCPUs across VMs on a 64-core host, because most VMs are idle most of the time. The whole business model of cloud compute rests on this.

It works until it doesn't. When guests genuinely want their allocation simultaneously, they queue. The symptom is **CPU steal time** — visible in `top` as `st`, meaning "my vCPU was ready to run and the hypervisor gave the physical core to someone else."

```bash
top     # the %st column; anything sustained above ~5% means you're fighting neighbours
```

**Memory is oversubscribed far more cautiously than CPU**, because the failure mode is swapping rather than waiting, and swapping is catastrophic rather than merely slow.

This is the mechanism behind the **noisy neighbour** problem, and the reason dedicated/metal instance types exist and cost more. See [[foundations/os/03-scheduling|scheduling]] for why queuing behaves this way.

## VMs and containers are not the same tool

The most common confusion in this area, and worth being precise about.

**A VM virtualises the hardware.** Each guest runs a full kernel.
**A container virtualises the operating system.** All containers share the host kernel; they're isolated by [[foundations/os/11-isolation-and-containers|namespaces and cgroups]] — namespaces control what a process can *see*, cgroups control what it can *use*.

| | **VM** | **Container** |
|---|---|---|
| Kernel | Its own | **Shared with the host** |
| Boot | 30s–minutes | Milliseconds |
| Size | GBs (whole OS) | MBs (just your app + deps) |
| Isolation | Strong — hardware boundary | Weaker — a kernel bug crosses it |
| Runs a different OS? | Yes | **No** — Linux containers need a Linux kernel |

That last row is the one people trip on. Docker on macOS or Windows runs a **Linux VM** and puts your containers inside it. Containers didn't replace virtualisation there; they're sitting on top of it.

**Neither replaced the other, and production usually runs both:** Kubernetes nodes are almost always VMs. You get the hardware-strength boundary between tenants from virtualisation, and the packaging speed and density from containers, and you accept two layers of overhead because each is buying something different.

Where the boundary genuinely matters — running untrusted code — the industry built hybrids: **Firecracker** (behind AWS Lambda and Fargate) boots a stripped-down VM in ~125ms, buying hardware isolation at roughly container speed. **gVisor** takes the other route, intercepting syscalls in userspace.

## What virtualisation actually bought

Reading back against the four problems:

- **Underutilisation** → many workloads per host, utilisation up from ~15% to 60–80%
- **Slow scaling** → a new machine is an API call, not a purchase order
- **Duplicated environments** → staging is a clone, and clones are cheap
- **Hardware-shaped backups** → a VM is a **file**. Snapshot it, copy it, boot it elsewhere

**The last one is quietly the biggest.** Once a running machine is a file, live migration becomes possible: move a running VM between physical hosts with no downtime, so hardware maintenance stops being an outage. That capability is why the cloud can patch the machine your instance is on without telling you.

And the same insight — *make the unit of deployment a portable artefact* — is what [[devops/02-docker/README|container images]], [[devops/07-infrastructure-as-code/01-provisioning-and-terraform|Terraform state]] and [[devops/11-delivery-and-advanced/01-gitops|GitOps]] are all separately re-applying one layer up.

## The honest cost

Virtualisation is not free, and the bill has three lines:

1. **Performance** — a few percent on CPU, more on I/O-heavy workloads
2. **Resource duplication** — every VM runs a full kernel and full system services. Thirty VMs means thirty kernels' worth of RAM you're not using for work
3. **A new attack surface** — hypervisor escape is rare and devastating. Shared-hardware side channels (Spectre/Meltdown, see [[foundations/computer-architecture/07-branch-prediction-and-speculation|speculation]]) are cross-tenant risks that simply don't exist on a machine you own

## Related
- [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|servers]] — the problems this solved
- [[devops/02-docker/README|Docker]] — the container half, in depth
- [[foundations/os/11-isolation-and-containers|namespaces and cgroups]] — the kernel primitives containers are built from
- [[build-your-own-x/08-your-own-container|build your own container]] — where this stops being reading
- [[cybersecurity/09-cloud-security/01-cloud-and-infrastructure-security|cloud security]] — multi-tenancy as a threat model

*Source: [reference] — from the freeCodeCamp IT Fundamentals course (module 2), extended with hardware-assist and container-boundary detail from vendor documentation.*
