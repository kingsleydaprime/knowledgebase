# The Data Centre Network

> **[Intermediate]** · Leaf-spine, east–west traffic, oversubscription, and why the network inside a data centre is built on the opposite assumptions to the internet.

[[foundations/networking/README|The networking course]] teaches the internet: a wide-area network of untrusted, unequal, variable-latency links where you must assume loss and congestion. **A data centre network inverts nearly every one of those assumptions**, and the result is a genuinely different design.

| | **The internet** | **Inside a data centre** |
|---|---|---|
| Ownership | Many parties | One |
| Latency | 10–200 ms | **0.05–0.5 ms** |
| Loss | Expected | Anomalous — usually means a real fault |
| Bandwidth | Scarce, paid for | Abundant, already bought |
| Topology | Unknown, changing | **Known and regular, by design** |
| Dominant traffic | Client → server | **Server → server** |

That last row is the one that reshaped the hardware.

## North–south and east–west

**North–south** traffic enters or leaves the data centre — a user's request arriving, a response going back.

**East–west** traffic moves *between* machines inside it — a web tier calling a service, a service querying a database, a replica syncing, a MapReduce shuffling, a distributed training job exchanging gradients.

**A single user request generates a burst of east–west traffic.** One page load might fan out to a dozen internal services, each hitting a cache and a database. [[architecture/03-architectural-patterns/README|Microservices]], replication and distributed storage all multiply it further.

The historical numbers are stark: east–west is commonly **70–80%+** of all data centre traffic. **And the classic three-tier network was built for the opposite case.**

## Why the old design broke

Traditional enterprise networks were a three-tier tree: access switches → aggregation → core. Traffic went *up* the tree to leave the building, and back down.

Two things go wrong when the traffic is mostly lateral:

**Path length is wildly unequal.** Two servers on the same access switch are one hop apart. Two servers in different pods must go up to aggregation, possibly up to the core, and back down — **five or more hops**. So identical code has different performance depending on which rack it landed in, which is exactly the kind of invisible variable that makes capacity planning miserable.

**Spanning Tree Protocol wastes the hardware you bought.** Ethernet cannot tolerate loops — a broadcast frame would circulate forever. STP prevents them by *disabling* redundant links until a failure. So you buy redundant capacity and are allowed to use half of it, and reconvergence after a failure takes seconds during which things simply stop.

## Leaf-spine

The modern answer, and it's a two-layer **Clos** topology:

```
        ┌────────┐  ┌────────┐  ┌────────┐   SPINE
        │ spine1 │  │ spine2 │  │ spine3 │
        └───┬────┘  └───┬────┘  └───┬────┘
       ╱────┼────╲ ╱────┼────╲ ╱────┼────╲
   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐  LEAF (top-of-rack)
   │ leaf1│   │ leaf2│   │ leaf3│   │ leaf4│
   └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘
   [servers]  [servers]  [servers]  [servers]
```

The rules are simple, and the simplicity is the point:

- **Every leaf connects to every spine.** No leaf connects to another leaf; no spine to another spine
- Each leaf is the **top-of-rack (ToR) switch** for its rack
- Any server-to-server path outside a rack is **exactly two hops**: leaf → spine → leaf

What that buys:

**Predictable latency.** Two hops, always. Rack placement stops being a performance variable — which is what makes a scheduler like [[devops/05-orchestration/README|Kubernetes]] free to put a pod anywhere.

**All links active.** Instead of STP, leaf-spine networks are routed at layer 3 with **ECMP** (equal-cost multi-path) — traffic is hashed across every available spine path. Add a spine and every leaf gets more bandwidth immediately.

**Horizontal scaling.** More racks → more leaves. More bandwidth between racks → more spines. Both are additive, and neither requires redesigning the network.

**Small failure domains.** A spine failure removes 1/N of the cross-rack capacity. Nothing goes down; things get proportionally slower. **Degradation instead of outage** is the same instinct that runs through [[architecture/04-distributed-systems/README|distributed systems]].

## Oversubscription

You will not have full bandwidth from every server to every other server simultaneously — that would be ruinously expensive and permanently idle. So the network is deliberately **oversubscribed**.

A rack with 48 servers at 25 Gbps each has 1,200 Gbps of possible server-side traffic. If its leaf has 4 × 100 Gbps uplinks to the spines, that's 400 Gbps out. **3:1 oversubscription.**

Typical ratios run 3:1 to 10:1 at the leaf, and modern spine layers are often 1:1. The tighter the ratio the more expensive, so the number is a budget decision — and it's the reason **network-heavy workloads are placed with intent**: distributed training and large shuffles want to be inside one rack, or on a fabric built with a tighter ratio.

**This is the thing to remember when a distributed job is mysteriously slow.** The compute is fine. You're at the top of an oversubscribed uplink.

## Overlays: why the network you configure isn't the network that exists

The physical fabric is a stable layer-3 routed network. But tenants want their own IP ranges, their own subnets, and the ability to move a workload without renumbering it.

So the tenant network is an **overlay** — virtual networks encapsulated inside the physical one, usually with **VXLAN** (an Ethernet frame wrapped in UDP), with the physical fabric acting as the **underlay** that carries the tunnels.

**This is what a VPC actually is.** When you define `10.0.0.0/16` in a [[devops/03-cloud/aws-cloud-reference|VPC]], no physical wire changed. You described an overlay; the provider's control plane programmed encapsulation rules; the packets still cross the same leaf-spine fabric alongside every other tenant's. It's the same move as [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|virtualisation]], applied to the network: **decouple the addressing from the wiring, and the wiring stops constraining you.**

It also explains two things that otherwise look arbitrary:

- **MTU quirks.** Encapsulation adds ~50 bytes of headers. If the underlay doesn't carry jumbo frames, the usable payload shrinks, and the symptom is the classic "small requests fine, large ones hang" — see [[foundations/networking/14-nat-firewalls-and-middleboxes|middleboxes]] and path MTU discovery
- **Security groups are not switches.** They're rules enforced at the virtual interface. Nothing is being physically segregated

## Storage on the network

Three ways servers reach storage, and the distinction is *what abstraction crosses the wire*:

| | Presents | Protocol | Feels like |
|---|---|---|---|
| **DAS** | Disks in the server | — | Local disk |
| **NAS** | A **filesystem** | NFS, SMB | A network share |
| **SAN** | **Raw blocks** | iSCSI, Fibre Channel | An unformatted local disk |

**SAN gives you blocks; the server formats them.** That's why a block device can be attached to exactly one machine at a time, and why it's what databases want.

**NAS gives you files, with the file server arbitrating access.** Which is why many machines can mount it at once, and why it's slower for random I/O.

The cloud mapping is direct: **EBS is a SAN** (block, one attachment, format it yourself), **EFS/Azure Files is a NAS** (POSIX filesystem, many mounts), and **S3 is neither** — object storage, HTTP API, no filesystem semantics at all. Choosing wrongly here is one of the most common and most expensive early architecture mistakes; see [[devops/03-cloud/03-object-storage-and-direct-uploads|object storage]].

## Incast — the DC-specific failure mode

Worth knowing because it's the one pathology that is *specific to this environment* and confuses people who learned TCP on the internet.

Many servers respond to one requester simultaneously — a fan-out query returning from 40 shards at once. All responses converge on one ToR port in the same instant, the switch's small buffer overflows, and packets are dropped. TCP interprets loss as congestion, backs off, and waits on a retransmission timer that may be orders of magnitude longer than the network's actual latency.

**The result: a request that should take 500 microseconds takes 200 milliseconds.** Not because anything is broken — because a congestion-control algorithm tuned for wide-area links is making wide-area assumptions on a network where they're wrong.

This is why data centres run **DCTCP** and ECN-based schemes that mark packets rather than dropping them, and why RDMA fabrics need lossless Ethernet. See [[foundations/networking/08-congestion-control|congestion control]] — the DC case is the clearest illustration that congestion control is a set of assumptions, not a law.

## Related
- [[devops/00-the-physical-layer/03-data-centres|data centres]] — the building these racks sit in
- [[foundations/networking/README|networking]] — the protocols, in depth
- [[foundations/networking/15-network-performance|network performance]] — latency budgets
- [[devops/08-networking-and-web/README|networking and web]] — the operator's view
- [[architecture/04-distributed-systems/README|distributed systems]] — what all this east–west traffic is doing

*Source: [reference] — from the freeCodeCamp IT Fundamentals course (data centre networking section), extended with Clos/ECMP, VXLAN overlay and incast detail from primary sources.*
