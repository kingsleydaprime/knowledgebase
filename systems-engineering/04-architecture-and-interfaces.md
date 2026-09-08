# Architecture and Interfaces

> **[Intermediate]** · Decomposition, coupling, and the ICD — because the failures live in the seams.

Once requirements exist, you decide **what parts there will be and how they connect.** Systems engineering's distinctive claim is that **the connections deserve more attention than the parts**, because that's where the failures actually happen.

## Functional versus physical

Two decompositions, deliberately kept separate:

**Functional architecture** — what the system *does*. "Store energy", "regulate temperature", "authenticate the user". Solution-neutral.

**Physical architecture** — what the system *is*. Battery pack, radiator, auth service.

**Doing the functional decomposition first is the single most useful habit in this note**, because jumping straight to components smuggles in a solution before you've considered alternatives. "We need a database" precludes asking whether you need durability, queryability, or just a file.

The mapping between them is rarely one-to-one:

- **One function, several components** — braking = pedal + hydraulics + ABS controller + pads
- **One component, several functions** — a phone's glass is display, input, and structural
- **Both** — which is where complexity comes from

**A component doing many unrelated functions is the physical form of low cohesion**, and it produces the same problem as in software: you can't change one thing without touching everything → [[concepts/04-best-practices/05-solid-principles|SOLID]].

## Coupling and cohesion, in physical systems

The same two ideas [[concepts/04-best-practices/README|software best practices]] are built on, and they predate software by decades.

**High cohesion** — a subsystem's parts belong together, serving one purpose.

**Low coupling** — subsystems depend on each other as little as possible, through interfaces as narrow as possible.

Physical systems have coupling types software doesn't, and these are the ones that catch software people moving into hardware:

| Coupling | Example |
|---|---|
| **Spatial** | It has to physically fit, and be reachable for maintenance |
| **Thermal** | This component heats that one |
| **Electrical** | Shared ground, EMI, current draw |
| **Mechanical** | Vibration, load paths, resonance |
| **Temporal** | This must happen before that |
| **Data** | The interface you were thinking of |

**A heat-generating component next to a temperature-sensitive one is coupled even if no wire connects them.** These are the couplings nobody wrote down, and they're where integration surprises come from.

The **Design Structure Matrix** is the standard tool: components on both axes, mark every dependency, then cluster. Dense clusters are genuine subsystems; marks far off the diagonal are the couplings you should design out or manage explicitly.

## The Interface Control Document

An **ICD** specifies precisely what crosses a boundary, and it is the field's most transferable artefact. For a physical interface:

- **Mechanical** — dimensions, tolerances, fastener pattern, mass, alignment
- **Electrical** — voltage, current, connector, pinout, grounding
- **Data** — protocol, format, rate, **units**, byte order, error handling
- **Thermal** — heat transferred, temperature limits
- **Timing** — latency, jitter, sequence
- **Environmental** — the conditions it must survive

**"Units" is on that list because of Mars Climate Orbiter** → [[foundations/systems-engineering/01-what-systems-engineering-is|note 01]]. Pound-seconds versus newton-seconds, in an interface that both teams believed they understood.

**Why an ICD is powerful:** once it's agreed, two teams can work independently for months and their outputs will fit. **The interface is the contract, and it is owned by neither side** — which is the point, because an interface owned by one side quietly changes to suit that side.

**The software equivalent is an API contract** — an OpenAPI spec, a protobuf definition, a published schema → [[backend/02-api-design/README|API design]]. Same purpose, same failure when it drifts, and the same rule: **the interface is harder to change than either implementation**, so spend more thought on it.

## N² diagrams

Put every subsystem on the diagonal of a square matrix; every off-diagonal cell is an interface between two of them.

The value is that it's **exhaustive** — it forces you to consider every possible pair, and a filled cell you didn't expect is an interface nobody owns. **Unowned interfaces are where integration fails**, and they're invisible in a block diagram, which only shows connections someone remembered to draw.

## Design for change

Two ideas worth naming because software has independently reinvented both.

**Modularity** — parts replaceable without redesigning neighbours. Requires stable interfaces, and it's what lets you upgrade one subsystem across a product generation.

**Margin** — deliberate headroom against the requirement. Structural safety factors, thermal margin, 30% spare power budget, spare pins on a connector.

**Margin is the physical form of "don't run at 100% utilisation".** Systems with no margin are brittle: every subsequent change is a redesign, and every uncertainty is a risk. Software's versions are spare capacity, connection-pool headroom, and an error budget → [[devops/12-sre-and-platform-engineering/02-site-reliability-engineering|SRE]].

**Both cost money upfront**, which is why both get cut under schedule pressure, and why both getting cut is a reliable early indicator of a project in trouble.

## Conway's Law cuts both ways

> *Organisations design systems that mirror their own communication structures.* — Melvin Conway, 1967

Six teams produce six subsystems. **The architecture will follow the org chart whether or not that's the right architecture.**

The systems-engineering read is more actionable than the usual software one: **an interface between two organisations is far more expensive than an interface within one** — different tools, contracts, incentives, review cycles. So put your boundaries where you *want* the coordination cost to fall.

The deliberate use — **the inverse Conway manoeuvre** — is to organise teams to match the architecture you want. It's the same reasoning behind [[devops/12-sre-and-platform-engineering/03-platform-engineering|platform engineering]]'s team-shape argument.

## Related
- [[foundations/systems-engineering/05-trade-studies|trade studies]] — choosing between architectures
- [[architecture/02-building-blocks/README|building blocks]] — the software vocabulary
- [[backend/02-api-design/README|API design]] — the ICD, for software
- [[concepts/04-best-practices/05-solid-principles|SOLID]] — coupling and cohesion at code scale

*Source: [reference] — from the INCOSE handbook, NASA SE Handbook, and Conway (1967).*
