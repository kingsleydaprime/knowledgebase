# What Game Development Actually Is

> **[Beginner]** · The shape of the field, the real-time constraint that drives every technical decision, and an honest account of the industry.

Game development is **software engineering under a hard real-time constraint, in service of a subjective goal.** Both halves are unusual, and between them they explain nearly every way game code differs from the rest of this vault.

## The 16-millisecond budget

At 60 frames per second, you have **16.67 ms** to do everything: read input, update the world, run physics, run AI, cull, submit draw calls, and present. At 144 Hz it's **6.9 ms**. In VR you must hold 90 Hz on two eyes or people feel ill.

**Miss the budget and the user sees it immediately.** A web request that takes 200 ms instead of 100 ms is invisible. A frame that takes 20 ms instead of 16 is a visible stutter, and a stutter every second is a broken game.

This single constraint drives the differences:

| | Most software in this vault | Games |
|---|---|---|
| Latency target | p99, in ms or s | **Every frame, in µs** |
| Worst case | Rare, tolerable | **Worst case IS the experience** |
| Memory | Allocate freely, GC handles it | **Allocation in the loop is a bug** |
| Correctness | Must be right | **Must be plausible, at speed** |
| Architecture driver | Maintainability | **Cache locality** |

**"Must be plausible rather than right" is the one that surprises people.** A physics engine is not solving Newtonian mechanics; it's producing something that looks convincing within the budget. Interpenetrating objects are pushed apart by an approximation nobody would defend as physics. Being visibly wrong is a bug; being *actually* wrong is normal → [[game-development/04-game-physics|game physics]].

**And "worst case is the experience" reframes optimisation.** In web work you optimise the average and watch the tail. In games the tail *is* the product — a 99th-percentile frame is one bad frame every 1.6 seconds at 60 Hz.

## What's actually in a game

The disciplines, and roughly how a team divides:

**Engineering** — gameplay, engine, graphics, physics, AI, networking, tools, audio programming. Tools programmers are the least visible and among the most valuable: everyone else's productivity runs through them.

**Art** — concept, 3D modelling, texturing, rigging, animation, VFX, technical art (the people who sit between art and engineering, and are perpetually scarce).

**Design** — systems design, level design, narrative, balancing, UX.

**Audio** — composition, sound design, implementation.

**Production** — scheduling, scope, shipping.

**Most of a game is not code.** On a large title, engineers are a minority, and much of their work is building the tools and systems that let designers and artists work without them. **That's the structural difference from most software teams, and it's why "content pipeline" is a first-class engineering concern** → [[game-development/07-tools-and-production|tools and production]].

## The two ways in

**Use an engine.** Unity, Unreal or Godot give you rendering, physics, audio, input, asset pipeline, editor and platform ports. You write gameplay. **This is the correct default**, and the reason is scope: the engine represents thousands of person-years you get for free → [[game-development/02-engines-and-the-game-loop|engines]].

**Write your own.** You learn enormously and ship far less. Legitimate as *education* — and it's the honest framing: a custom engine is a study project unless you have a specific technical need no engine meets.

**The failure mode to name early: building an engine while believing you're building a game.** They are different projects with different outcomes, and conflating them is the most common way an ambitious first game dies.

## The maths you actually need

**Less than people fear for gameplay, more than they hope for graphics and physics.**

**Essential, immediately** — vectors (add, dot, cross, normalise), and enough trigonometry to point things at other things. Dot product for angles and projection; cross product for perpendiculars and winding. **If you understand the dot product, you can write gameplay code.**

**Essential for 3D** — matrices and transforms, and quaternions for rotation. Not the theory; the operations and what they mean → [[foundations/computer-graphics/02-the-transform-pipeline|transforms]] and [[robotics/04-rigid-body-transforms|rigid body transforms]], which this vault already has because robotics needed exactly the same maths.

**For physics** — Newtonian mechanics, integration, and why Euler integration explodes → [[foundations/numerical-methods/08-ordinary-differential-equations|ODEs]].

**For graphics** — linear algebra properly, plus the rendering equation → [[foundations/computer-graphics/README|computer graphics]].

**You don't need most of it to start.** A 2D game needs vectors and nothing else.

## The industry, honestly

**Since you asked out of genuine interest, this is the part worth knowing before you invest years.**

**Pay is lower than equivalent software roles**, often substantially — because supply exceeds demand. Many people want to make games; comparatively few companies need them. The same skills in fintech or infrastructure pay more.

**"Crunch" is real**, though improving under unionisation pressure and public scrutiny. Studio culture varies enormously; it is worth researching a specific studio rather than the industry.

**Employment is volatile.** Layoffs follow project completion as a structural pattern, not an anomaly, and 2023–25 saw very large ones across the sector.

**Most games don't make money.** The distribution is brutally long-tailed — a small number of titles earn nearly everything.

**The counterweight, which is also real:** it is genuinely creatively satisfying in a way most software isn't, the technical work is among the hardest and most interesting in the industry, and the skills transfer *outward* well — real-time rendering, performance work and simulation are wanted in visualisation, simulation, film, defence, automotive HMI, medical imaging and increasingly robotics.

**The pragmatic route, and the one this vault would recommend given [[learning/04-one-active-course|the one-active-course rule]]:** keep game development as a *side* discipline while earning from general software. It's a legitimate hobby, an outstanding way to learn graphics and performance, and it does not require you to accept the industry's economics to benefit from its skills.

## Related
- [[game-development/02-engines-and-the-game-loop|engines and the game loop]] — the technical starting point
- [[game-development/08-getting-started|getting started]] — what to actually build first
- [[foundations/computer-graphics/README|computer graphics]] — the rendering half, already here
- [[foundations/programming-fundamentals/README|programming fundamentals]] — if this is where you're starting from

*Source: [reference] — cross-referenced against the [roadmap.sh game developer roadmap](https://roadmap.sh/game-developer).*
