# Servers, and What Actually Makes Them Servers

> **[Beginner]** · The machine under the abstraction. Same five components as your laptop — different economics, and that difference explains everything above it.

Every layer in this vault eventually runs on a physical box in a building. [[devops/03-cloud/01-cloud-fundamentals|Cloud fundamentals]] opens with "the cloud is someone else's computers" and then, reasonably, never mentions the computers again. This note is the computers.

## A server is not a different kind of machine

The honest answer to "what's a server?" is disappointing: **it's a computer with the same five components as the laptop you're reading this on.**

| Component | What it does | Measured in |
|---|---|---|
| **CPU** | Executes instructions | Clock speed (GHz) × cores × sockets |
| **RAM** | Holds what's currently running | GB / TB |
| **Storage** | Keeps data when the power goes | GB / TB, and **IOPS** |
| **NIC** | Talks to everything else | Gbps |
| **GPU** | Parallel maths, if present | VRAM + FLOPS |

What makes it a *server* is not the parts list. It's four things about how it's used:

**1. It serves other machines, not a person sitting at it.** No monitor, no keyboard. You reach it over the network — which is why [[devops/01-linux/14-basic-ssh-config|SSH]] is the single most important tool in the folder next door, and why a headless [[devops/01-linux/README|Linux]] install is the norm.

**2. It's specified for concurrency, not for one user's peak.** Your laptop is tuned to make *one* person's foreground task feel fast. A server is tuned to keep *thousands* of requests moving at once. That's why servers have many slower cores rather than few fast ones, and why RAM capacity matters more than RAM latency.

**3. It's expected to stay up.** Redundant power supplies, ECC memory that corrects single-bit errors instead of silently corrupting your data, hot-swappable drives, RAID. A consumer machine that crashes monthly is annoying; a server that crashes monthly is an outage budget.

**4. It's shaped to live in a rack.** Which is the constraint that drives the physical design — see [[devops/00-the-physical-layer/03-data-centres|data centres]].

## The form factors

**Rack-mount** — the flat pizza-box shape, sized in **U** (rack units, 1U = 1.75 inches / 44.45 mm of vertical space). A standard rack is 42U. A 1U server is the density workhorse; 2U and 4U buy room for more drives and full-height GPUs. Density is why they're loud: less vertical space means smaller fans spinning much faster.

**Blade** — a chassis holds many thin server "blades" sharing power, cooling and networking. Higher density, more vendor lock-in.

**Tower** — looks like a desktop. Small offices, labs, under-a-desk sins.

## ECC, and why it's the detail that gives it away

If you want a single technical marker separating "server" from "expensive desktop", it's **ECC RAM** (Error-Correcting Code). Cosmic rays and electrical noise genuinely flip bits in memory — rarely per machine, constantly across a fleet. ECC detects two-bit errors and silently corrects single-bit ones.

Without it, a flipped bit is a corrupted value with no error, no log line, and no way to reason about it afterwards. **This is the reliability story in miniature: not "prevent all failures" but "convert silent failures into loud ones."** The same instinct shows up as checksums in [[foundations/networking/02-the-link-layer|the link layer]], WAL in [[databases/10-durability-and-recovery|databases]], and health checks in [[devops/05-orchestration/README|orchestration]].

## Storage: the number that isn't capacity

Terabytes are the easy number and rarely the interesting one. The interesting one is **IOPS** — I/O operations per second — and its companion, latency.

| | Random-read latency | Rough IOPS |
|---|---|---|
| **HDD** (spinning disk) | ~5–10 ms | 100–200 |
| **SATA SSD** | ~0.1 ms | ~50,000–100,000 |
| **NVMe SSD** | ~0.02 ms | 500,000+ |

That's a **five-orders-of-magnitude** spread on random access from the same shelf of hardware. A spinning disk has to physically move a head; an SSD does not. This is the entire reason [[databases/04-b-trees-and-indexes|B-trees]] are shaped the way they are — they were designed to minimise seeks on a device where a seek cost 10ms — and why [[databases/05-lsm-trees|LSM trees]] became attractive once sequential writes stopped being the only fast thing.

**When someone says a database is "slow", ask what the storage is before you look at the query.** See [[foundations/computer-architecture/09-caches-in-depth|the memory hierarchy]] for the layers above this.

## Why one application per server was the norm — and the bill it created

Traditionally you bought a server, installed [[devops/01-linux/README|an OS]], and ran one application on it. Not from ignorance — from three real needs:

- **Isolation** — application A's runaway process shouldn't take down B
- **Security** — a compromise of one shouldn't be a compromise of all
- **Blast radius** — a bad config change should break one thing

And it produced four problems that shaped the next twenty years of infrastructure:

**Underutilisation.** A machine sized for peak load sits at 10–20% average utilisation. You bought all the muscle and use one arm. Across a fleet this is enormous waste — and it's the single fact that made virtualisation inevitable.

**Slow scaling.** Needing more capacity meant procurement, delivery, racking, cabling, installation. **Weeks to months.** Meanwhile the traffic spike you were responding to ended on Tuesday.

**Environment duplication.** Dev, staging and production each need their own hardware. Three times the cost, and they still drift apart.

**Hardware-shaped backups.** A restore assumed similar hardware. Recovery was a project, not a command.

Every one of these is a *utilisation* or *lead-time* problem — not a compute problem. **You can't fix them with faster machines, only by changing the unit you allocate.** Which is exactly what [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|virtualisation]] did.

## What this means when you rent instead of buy

Pick any cloud instance type and you're choosing these same five numbers, plus a sixth the marketing hides:

- `m5.large` → 2 vCPU, 8 GB RAM, "up to 10 Gbps" network
- A **vCPU is normally one hyperthread**, not one physical core. Two vCPUs ≈ one core's worth of real execution resources
- **"Up to"** means burst. Sustained throughput is often a fraction, governed by a credit balance
- Instance families encode the ratio — `c` compute-heavy, `r` memory-heavy, `i` storage-heavy, `t` burstable

**Reading an instance type is reading a spec sheet for a machine you'll never see.** That's the whole skill: the abstraction is thin, and it leaks exactly where the physics is.

## Related
- [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|virtualisation]] — how one of these became many
- [[devops/00-the-physical-layer/03-data-centres|data centres]] — the building it lives in
- [[foundations/computer-architecture/README|computer architecture]] — what's happening inside the CPU
- [[foundations/os/01-what-an-os-is|what an OS is]] — the software that makes the hardware usable
- [[devops/03-cloud/01-cloud-fundamentals|cloud fundamentals]] — renting all of the above

*Source: [reference] — distilled from the freeCodeCamp IT Fundamentals course (modules 1–2), cross-checked against vendor documentation.*
