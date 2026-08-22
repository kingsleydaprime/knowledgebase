# The Physical Layer

The machine, the building, and the wiring — the four notes this folder's neighbours all assumed.

**~5,100 words across 4 notes.** Built August 2026. `[reference]`.

> **The one idea:** every abstraction above this — a container, an instance type, an availability zone, a VPC — is a *rental agreement over a physical constraint*. Knowing the constraint tells you where the abstraction leaks.

## Why this exists

[[devops/03-cloud/01-cloud-fundamentals|Cloud fundamentals]] opens with "the cloud is someone else's computers" and then never mentions the computers. [[devops/01-linux/README|01-linux]] starts with an OS already running on a machine that already exists. [[hardware/README|hardware/]] covers the layer below software but means microcontrollers and PCBs, not server rooms.

**So the vault had a gap exactly one layer wide:** between a soldered circuit board and a rented `t3.medium`, nothing explained the actual machine, the building it lives in, or why an availability zone is a physical fact rather than a marketing word.

This is numbered `00` because it sits *under* Linux, not after it. It is also the shortest section in `devops/`, deliberately — it exists to make four ideas concrete, not to turn anyone into a facilities engineer.

## Reading order

1. [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|Servers]] — **[Beginner]** — the same five components as your laptop, different economics; ECC, IOPS, and **the four problems with one-app-per-server that produced everything else**
2. [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|Virtualisation and Hypervisors]] — **[Beginner → Intermediate]** — Type 1 vs Type 2, oversubscription and steal time, and **why containers are not smaller VMs**
3. [[devops/00-the-physical-layer/03-data-centres|Data Centres]] — **[Beginner]** — power, hot aisle/cold aisle, PUE, the Uptime tiers, and **what an availability zone physically is**
4. [[devops/00-the-physical-layer/04-the-data-centre-network|The Data Centre Network]] — **[Intermediate]** — east–west traffic, leaf-spine, oversubscription ratios, VXLAN overlays, and **incast**

## The things worth carrying

1. **A server isn't a different kind of machine — it's the same parts, specified for concurrency and uptime.** ECC is the giveaway → [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|01]]
2. **IOPS, not capacity, is the storage number that decides performance.** Five orders of magnitude between an HDD and an NVMe on random reads → [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|01]]
3. **Underutilisation, not compute scarcity, is what made virtualisation inevitable.** You can't fix a 15%-utilised fleet with faster machines → [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|01]]
4. **CPU and memory virtualisation are nearly free; I/O is where the overhead lives.** So look at disk and network first → [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|02]]
5. **Steal time is your bill for someone else's busy hour.** The visible face of oversubscription → [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|02]]
6. **A VM virtualises hardware; a container virtualises an OS.** Which is why Docker on macOS is running a Linux VM → [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|02]]
7. **Once a running machine is a file, live migration exists** — and hardware maintenance stops being an outage → [[devops/00-the-physical-layer/02-virtualisation-and-hypervisors|02]]
8. **Power density, not floor space, is what fills a data centre** → [[devops/00-the-physical-layer/03-data-centres|03]]
9. **An AZ is the blast radius of a physical event.** Three instances in one AZ share a roof → [[devops/00-the-physical-layer/03-data-centres|03]]
10. **The facility is almost never your weakest link.** Tier IV is 26 minutes a year; your deploy process is worse → [[devops/00-the-physical-layer/03-data-centres|03]]
11. **70–80% of data centre traffic is east–west**, which is why the three-tier tree gave way to leaf-spine → [[devops/00-the-physical-layer/04-the-data-centre-network|04]]
12. **A VPC is an overlay, not a wire.** Nothing physical changed when you chose `10.0.0.0/16` → [[devops/00-the-physical-layer/04-the-data-centre-network|04]]
13. **SAN gives blocks, NAS gives files, S3 gives neither.** EBS/EFS/S3 in one line → [[devops/00-the-physical-layer/04-the-data-centre-network|04]]

## Where this connects

| | |
|---|---|
| [[devops/03-cloud/README\|03-cloud/]] | **The direct consumer.** Instance types, regions, AZs — this is what they're renting |
| [[devops/02-docker/README\|02-docker/]] | Note 02's other half, in depth |
| [[foundations/networking/README\|networking]] | Note 04 is the DC-shaped inversion of that course's assumptions |
| [[foundations/os/11-isolation-and-containers\|OS: isolation]] | The kernel primitives under containers |
| [[architecture/01-system-design-fundamentals/03-availability-and-reliability\|availability]] | Where the tier numbers turn into design |
| [[hardware/README\|hardware/]] | The layer below this one — boards, not buildings |

## The honest note

**`[reference]`, and the most reference-y section in `devops/`** — I have not racked a server or walked a data centre hall. Everything here is read, cross-checked, and arranged.

**What would close the gap:**

1. **Run a Type 2 hypervisor properly.** Build a three-VM lab, deliberately oversubscribe it, and watch `%st` appear in `top` under load. **Note 02 becomes an observation instead of a claim**
2. **Measure the thing you rent.** `fio` against an EBS volume vs an instance-store NVMe vs a local disk. The IOPS table in note 01 is only real once you've reproduced it
3. **Take one workload and place it badly on purpose** — same-AZ vs cross-AZ vs cross-region — and record the latency difference. That's note 03's single-digit-millisecond claim, verified
4. **Trace a packet out of a container** and count the encapsulation. `tcpdump` on the underlay while pinging across a VPC makes note 04's overlay point undeniable
5. **Ask for a tour.** Most colocation providers will show a prospective customer a hall. Twenty minutes in a cold aisle beats any amount of reading here

**What's missing:** liquid and immersion cooling in any depth, power distribution below the rack PDU, Fibre Channel specifics, RDMA/RoCE beyond a mention, GPU-cluster fabrics (NVLink, InfiniBand) — a real gap given [[foundations/gpu-and-parallel-computing/README|the GPU course]] — and anything about the economics of actually buying capacity.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[devops/README|DevOps]] — the folder this sits under
- [[devops/03-cloud/README|03-cloud/]] — where all of this gets rented instead
- [[BUILD-PLAN|Build Plan]]
