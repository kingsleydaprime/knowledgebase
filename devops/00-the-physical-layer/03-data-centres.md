# Data Centres

> **[Beginner]** · The building. Power, heat, redundancy tiers, and why "availability zone" is a physical fact rather than a marketing word.

A server has to live somewhere. Under a desk works until it doesn't — until the cleaner unplugs it, the room hits 40°C in August, or the building loses power for six hours. **A data centre is a building whose entire purpose is to remove those failure modes**, and it is more interesting than it sounds, because its constraints leak upward into things you'll actually configure.

## What the building is actually for

Four things, in rough order of how much they cost:

1. **Power that doesn't stop** — mains, plus UPS batteries for the seconds-to-minutes gap, plus diesel generators for the hours-to-days gap
2. **Heat removal** — a fully loaded rack dissipates 5–20 kW as heat, and a hall has hundreds of racks
3. **Connectivity** — multiple physical fibre routes from multiple carriers, entering the building at different points
4. **Physical security** — mantraps, biometrics, cameras, and a real answer to "who touched that machine"

**Compute is the cheap part.** The building, the power contract and the cooling dominate the cost, which is exactly why the cloud's economics work: those costs amortise brutally well across scale.

## Racks and the unit that everything is measured in

The **19-inch rack** is the organising standard, and it is remarkably old — it descends from railway signalling equipment. Vertical space is measured in **U** (1U = 44.45 mm). A full rack is 42U.

A rack contains servers, a **top-of-rack switch** (see [[devops/00-the-physical-layer/04-the-data-centre-network|the DC network]]), power distribution units, and cable management. Racks stand in rows; rows form halls.

**Power density is the real limit, not space.** A rack might have room for 42 1U servers but only enough power and cooling budget for 20. Empty U in a modern hall usually means the power circuit is full, not that nobody wants the space.

## Hot aisle / cold aisle

The single most important physical arrangement, and once you see it you can't unsee it.

Every server pulls cool air in the **front** and exhausts hot air out the **back**. So racks are arranged so that fronts face fronts and backs face backs:

```
   COLD AISLE          HOT AISLE           COLD AISLE
      ↓ ↓ ↓                ↑ ↑ ↑              ↓ ↓ ↓
  ┌────────┐┌────────┐  ┌────────┐┌────────┐
  │ rack → ││ ← rack │  │ rack → ││ ← rack │
  └────────┘└────────┘  └────────┘└────────┘
   front  back  back     front   front  back
```

Cool air is delivered to the cold aisles (often through a raised floor with perforated tiles), and hot exhaust is collected from the hot aisles and returned to the cooling plant. Modern halls **contain** one aisle or the other with physical barriers so the two air masses never mix.

**The failure this prevents:** if hot exhaust recirculates into an intake, that server runs hot, throttles, and eventually shuts down — while the room's average temperature reads fine. Mixing air is the enemy; the entire discipline is about keeping two air masses apart.

The efficiency metric is **PUE** (Power Usage Effectiveness) — total facility power ÷ IT equipment power. PUE 2.0 means you burn a watt on cooling and overhead for every watt of compute. A good modern facility is 1.1–1.2. Hyperscalers report figures near 1.1, which is a large part of why renting is cheaper than a server room in your office, where a PUE of 2 would be optimistic.

## Redundancy, and the N+1 notation

Redundancy is described by how many spare units you have relative to what you need:

- **N** — exactly enough capacity. No spare. One failure is an outage
- **N+1** — one spare component. Any single unit can fail or be serviced
- **2N** — a complete duplicate of everything. Two independent power paths
- **2N+1** — duplicate, plus a spare in each

The **Uptime Institute tier ratings** package this into four levels:

| Tier | Shape | Concurrently maintainable? | Rough availability |
|---|---|---|---|
| **I** | Single path, no redundancy | No | ~99.67% (~29 h/yr) |
| **II** | Single path, redundant components | No | ~99.75% (~22 h/yr) |
| **III** | Multiple paths, one active | **Yes** — service anything without downtime | ~99.98% (~1.6 h/yr) |
| **IV** | Multiple active paths, fault tolerant | Yes, and survives a failure during maintenance | ~99.995% (~26 min/yr) |

**Tier III is the commercially interesting line**, and the reason is maintenance rather than failure. Below it, routine work on the power path requires taking the load down. Most colocation you'd actually buy is Tier III.

**Read those availability figures carefully.** Tier IV's 99.995% is the *facility*. Your application's availability is that number multiplied by everything else in the chain — your code, your database, your deploy process. **The building is rarely your weakest link, which is the useful thing to know.** See [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability and reliability]] for how these numbers compose.

## Where your servers actually sit

Four models, and the difference is who owns which layer:

| Model | You own | They own |
|---|---|---|
| **On-premises** | Everything, including the building | — |
| **Colocation** | The servers | Space, power, cooling, connectivity |
| **Managed hosting** | The application | The hardware too |
| **Cloud** | A workload | All of it |

**Colocation is the one people forget exists**, and it's still the right answer for predictable, steady, high-volume workloads where cloud pricing stops being a bargain. The cloud's advantage is elasticity and speed, not unit cost — several well-known companies have repatriated steady workloads and saved substantially. The trade is that you get your lead times and your capacity planning back.

## Regions, availability zones, and what the words mean physically

This is the payoff, and it's why the building is worth a note.

**A cloud region is a geographic area** — `eu-west-1` (Ireland), `us-east-1` (Northern Virginia). Regions are genuinely separate: separate power grids, separate staff, and services are usually region-scoped. Data doesn't move between them unless you move it, which is what makes regions the unit of data residency and compliance.

**An availability zone is one or more physically distinct data centres within a region**, with independent power, cooling and networking — but connected to the other AZs in the region by dedicated low-latency fibre, typically **single-digit milliseconds** round trip.

That number is the whole design:

- **Far enough apart** that one flood, fire, or substation failure cannot take out two
- **Close enough** that synchronous replication between them is practical

So the standard advice — *spread across at least two AZs* — is not a cloud-vendor ritual. It's the statement that **an AZ is the blast radius of a physical event**, and one AZ is a single building's worth of risk no matter how many virtual machines you run inside it.

The corollary is worth stating plainly: **three instances in one AZ are not a redundant system.** They share a roof, a power feed, and a cooling plant. Multi-AZ protects against the building. Multi-region protects against the region — at the cost of latency and, usually, of strong consistency. See [[architecture/04-distributed-systems/README|distributed systems]] for what that trade costs.

## Related
- [[devops/00-the-physical-layer/04-the-data-centre-network|the data centre network]] — how the racks are wired together
- [[devops/00-the-physical-layer/01-servers-and-what-makes-them-servers|servers]] — what fills the racks
- [[devops/03-cloud/01-cloud-fundamentals|cloud fundamentals]] — regions and AZs as an API
- [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability and reliability]] — turning these numbers into design
- [[foundations/networking/08-congestion-control|congestion control]] — why DC networks behave unlike the internet

*Source: [reference] — from the freeCodeCamp IT Fundamentals course (module 3), extended with Uptime Institute tier definitions and cloud-provider AZ documentation.*
