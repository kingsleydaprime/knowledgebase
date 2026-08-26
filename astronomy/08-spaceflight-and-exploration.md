# Spaceflight and Exploration

> **[Intermediate]** · Orbits, why getting to space is mostly about sideways speed, and what's actually flying.

## Orbit is not altitude

**The most common misconception in the subject: space is not far, it's fast.**

The Kármán line is 100 km up — a drive you'd make without thinking. **Getting to that altitude is comparatively easy. Staying there is the hard part.**

**An orbit is a trajectory where you fall toward Earth and keep missing**, because your sideways velocity carries you past the horizon as fast as you drop. Newton's cannonball: fire hard enough and the ground curves away as fast as the ball falls.

**The numbers make the point:**
- Reaching 100 km vertically: **~1.4 km/s**
- Staying in low Earth orbit: **~7.8 km/s**

**Roughly 90% of the energy goes into horizontal speed, not height.** This is why rockets pitch over almost immediately after launch, and why suborbital flights (Blue Origin's New Shepard) are a fundamentally easier problem than orbital ones.

## Delta-v is the currency

**Δv — the total velocity change a mission needs — is the budget everything is planned against.** Rocket equation:

$$\Delta v = v_e \ln\frac{m_0}{m_f}$$

**The logarithm is brutal.** Doubling your Δv doesn't double the fuel — it squares the mass ratio. **This is why rockets are almost entirely propellant**, why staging exists (drop the empty tanks so you stop accelerating them), and why every kilogram of payload is fought over.

**Rough Δv from Earth's surface:**

| Destination | Δv |
|---|---|
| Low Earth orbit | ~9.4 km/s (incl. losses) |
| Geostationary transfer | +2.4 |
| The Moon (surface) | +~5.9 |
| Mars (surface) | ~+4.5 with aerobraking |

**Once you're in LEO you are, energetically, halfway to anywhere.**

## Orbital mechanics that feel wrong

**To speed up, you slow down.** Firing your engine *forward* (retrograde) drops you to a lower orbit, where orbital velocity is *higher*. To catch something ahead of you, you go *lower* and overtake, then raise back up. **Intuition from driving is actively misleading here.**

**Hohmann transfer** — the fuel-efficient way between two circular orbits: one burn to enter an elliptical path, one at the far end to circularise. Slow but cheap.

**Launch windows** exist because the geometry has to line up. **Mars windows come every ~26 months**, which is why missions cluster and why a slip costs two years.

**Gravity assists** — steal a little orbital energy from a planet by flying past it. Voyager, Cassini and New Horizons all depended on them. **The planet loses an utterly negligible amount of its orbital energy; the spacecraft gains a great deal.**

**Lagrange points** — five positions where the gravity of two bodies and the orbital motion balance. **JWST sits at Earth–Sun L2**, 1.5 million km out, so Earth and Sun stay in the same direction and one sunshield blocks both.

## What's actually flying

**Crewed:** the **ISS** (continuously occupied since 2000, retirement planned ~2030), China's **Tiangong**, and commercial vehicles — SpaceX **Crew Dragon** carries astronauts routinely.

**Launch:** the dominant change of the last decade is **reusability**. Falcon 9 boosters land and refly, which cut cost per kilogram substantially and changed what missions are affordable. **Starship** aims at full reuse at much larger scale.

**Robotic exploration** is where most science happens: **Perseverance** and **Curiosity** on Mars; **JWST** and **Hubble**; **Parker Solar Probe** flying through the Sun's corona; **Europa Clipper** en route to Jupiter's ocean moon; **Voyager 1 and 2** in interstellar space after 47+ years.

**The honest framing: robots do the science, humans do the difficult, expensive, inspiring part.** A rover costs a fraction of a crewed mission and needs no return trip. The case for humans is partly scientific (a geologist on Mars would outpace a rover enormously) and substantially political and cultural — and that's worth saying plainly rather than pretending otherwise.

## Why it's hard

**Vacuum** — no convection, so thermal management is entirely radiative. Spacecraft overheat as readily as they freeze.

**Radiation** — no atmosphere or magnetosphere beyond LEO. Damages electronics (hence radiation-hardened, deliberately old, slow chips) and is a major unsolved obstacle for long crewed missions.

**Debris** — tens of thousands of tracked objects, millions untracked, at orbital speeds where a paint fleck is dangerous. **Kessler syndrome** — a cascade of collisions making some orbits unusable — is a genuine concern, not a hypothetical.

**Microgravity on humans** — bone density loss, muscle atrophy, fluid shifts, vision changes, immune effects.

**Distance and latency** — Mars is 4–24 light-minutes away. **No real-time control**, so spacecraft must be substantially autonomous.

## The engineering discipline

**Spaceflight is where [[foundations/systems-engineering/README|systems engineering]] was invented**, and the reasons are structural: you cannot iterate, you cannot repair, and the cost of failure is total.

**Everything in that folder shows up here:** requirements traceability, interface control documents (**Mars Climate Orbiter is the canonical failure** → [[foundations/systems-engineering/01-what-systems-engineering-is|note 01]]), FMEA, redundancy and margin, technology readiness levels, and V&V against an environment you cannot fully reproduce.

**It's also where real-time and safety-critical software lives** → [[foundations/software-engineering/04-the-kinds-of-software-engineering|kinds of software engineering]] — flight software is written in restricted language subsets with formal review, and the Apollo Guidance Computer's software is still studied.

## Related
- [[foundations/systems-engineering/README|systems engineering]] — the discipline this field created
- [[astronomy/05-planets-and-solar-systems|planets]] — the destinations
- [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]] — how trajectories are computed
- [[engineering/02-control-theory/README|control theory]] — guidance and attitude control

*Source: [reference] — written Aug 2026.*
