# Game Development

Software engineering under a hard real-time constraint, in service of a subjective goal.

**~12,550 words: 8 course notes + 4 engine pages + an interview bank + 2 index pages.** Built August 2026. `[reference]`. Cross-referenced against the [roadmap.sh game-developer roadmap](https://roadmap.sh/game-developer).

> **The one idea:** you have **16 milliseconds**, every frame, forever. Every technical decision in this folder — data-oriented design, fixed timesteps, culling, approximate physics, prediction, baked lighting — is that constraint showing through. Games are not "software with graphics"; they are software where **the worst case is the experience**.

## Why this exists, and why it's thin

Games were one of the three reasons you came into tech. That's reason enough to have the map.

**But the folder is deliberately small, because most of the game-developer roadmap is already in this vault** — written for graphics, robotics, DSA, numerical methods and ML. Restating it here would be duplication, and the far more useful thing is to *point at it*:

| Roadmap area | Already written, elsewhere |
|---|---|
| Vectors, matrices, transforms, **quaternions** | [[foundations/computer-graphics/02-the-transform-pipeline\|transforms]] · [[robotics/04-rigid-body-transforms\|rigid body transforms]] |
| Rendering, rasterisation, PBR, shading, ray tracing | [[foundations/computer-graphics/README\|computer graphics]] — 9 notes |
| Shaders, GPU parallelism | [[foundations/gpu-and-parallel-computing/README\|GPU & parallel computing]] |
| Integration, stability, ODEs | [[foundations/numerical-methods/README\|numerical methods]] |
| BVH, trees, A\*, graphs | [[foundations/dsa/README\|DSA]] · [[foundations/discrete-math/07-graph-theory\|graph theory]] |
| Neural nets, decision trees, RL | [[ai-ml/README\|AI & ML]] |
| Caches, data-oriented design | [[foundations/computer-architecture/README\|computer architecture]] |
| UDP, latency, distributed state | [[foundations/networking/README\|networking]] |

**Game development is largely an integration discipline** — which is also why the skills transfer outward into simulation, visualisation, robotics and film.

## Reading order

**01–02 first. 03–06 are the technical pillars and can be read in any order. 07–08 are how it actually gets done.**

1. [[game-development/01-what-game-development-actually-is|What Game Development Actually Is]] — **[Beginner]** — the 16 ms budget, the disciplines, the maths you actually need, **and the industry honestly**
2. [[game-development/02-engines-and-the-game-loop|Engines and the Game Loop]] — **[Beginner → Intermediate]** — the loop, **the fixed-timestep problem**, ECS and data-oriented design, choosing between Unity/Unreal/Godot
3. [[game-development/03-graphics-for-games|Graphics for Games]] — **[Intermediate]** — the frame budget, CPU vs GPU bound, culling and LOD, **and the catalogue of lies**
4. [[game-development/04-game-physics|Game Physics]] — **[Intermediate]** — broad/narrow phase, GJK and SAT, **why semi-implicit Euler and not Euler**, tunnelling, and when not to use a physics engine
5. [[game-development/05-game-ai|Game AI]] — **[Intermediate]** — state machines, behaviour trees, utility AI, A\* and navmeshes, **and why a perfect opponent isn't fun**
6. [[game-development/06-multiplayer-and-networking|Multiplayer and Networking]] — **[Advanced]** — prediction, reconciliation, interpolation, lag compensation, lockstep, **and why UDP**
7. [[game-development/07-tools-and-production|Tools and Production]] — **[Intermediate]** — the content pipeline, **iteration time as the metric**, why games broke git, scope
8. [[game-development/08-getting-started|Getting Started]] — **[Beginner]** — **the ladder from Pong upward**, game jams, and what to skip

## The things worth carrying

1. **The worst case is the experience.** A 99th-percentile frame is one visible stutter every 1.6 seconds → [[game-development/01-what-game-development-actually-is|01]]
2. **Plausible at speed beats correct.** Game physics isn't simulating Newton → [[game-development/01-what-game-development-actually-is|01]] · [[game-development/04-game-physics|04]]
3. **Building an engine while believing you're building a game** is the commonest way an ambitious first project dies → [[game-development/01-what-game-development-actually-is|01]]
4. **Fixed timestep for simulation, interpolate for rendering** — and cap the inner loop or you get the spiral of death → [[game-development/02-engines-and-the-game-loop|02]]
5. **ECS won on cache locality, not elegance.** Contiguous arrays beat pointer-chasing by ~10× → [[game-development/02-engines-and-the-game-loop|02]]
6. **First establish whether you're CPU- or GPU-bound.** Guessing wrong wastes days → [[game-development/03-graphics-for-games|03]]
7. **The cheapest work is work not done** — cull, LOD, batch → [[game-development/03-graphics-for-games|03]]
8. **Semi-implicit Euler: update velocity first.** One line's difference between stable and exploding → [[game-development/04-game-physics|04]]
9. **Solvers are allowed not to converge** — which is exactly why stacks jitter and joints go rubbery → [[game-development/04-game-physics|04]]
10. **Don't use physics for the player character.** Feel beats realism, and feel is authored → [[game-development/04-game-physics|04]]
11. **AI that isn't legible reads as broken.** Perceived intelligence is the product → [[game-development/05-game-ai|05]]
12. **A\*'s optimal path looks robotic.** Smooth it → [[game-development/05-game-ai|05]]
13. **Never trust the client.** The server simulates; the client predicts → [[game-development/06-multiplayer-and-networking|06]]
14. **You are in the present, everyone else is in the past** — and that's why you die behind cover → [[game-development/06-multiplayer-and-networking|06]]
15. **Iteration time is the most important number on the project** → [[game-development/07-tools-and-production|07]]
16. **Estimate, then cut to a third.** Scope kills more projects than skill → [[game-development/07-tools-and-production|07]] · [[game-development/08-getting-started|08]]
17. **A finished Pong on the internet beats an unfinished RPG on your disk** → [[game-development/08-getting-started|08]]

## Engines

**Same convention as [[backend/frameworks/README|backend/frameworks/]]** — the course teaches the concepts; these are how each engine names and does them.

[[game-development/engines/README|engines/]] — the map and the concept-translation table

- [[game-development/engines/godot|Godot]] — **[Beginner → Intermediate]** — MIT, small enough to read, GDScript. **The recommendation for learning**
- [[game-development/engines/unity|Unity]] — **[Intermediate]** — C#, the deepest job market, and **the fragmentation you should know about before committing**
- [[game-development/engines/unreal|Unreal]] — **[Advanced]** — C++ and Blueprints, AAA rendering free, strong opinions
- [[game-development/engines/from-scratch|From scratch]] — **[Advanced]** — the layers in build order, and **an honest account of which project you're doing**

## Practice and interviews

- [[project-ideas|project ideas → Game Development]] — tiered reps. **If you do one: a game jam**
- [[game-development/interview/README|interview/]] — the round: vectors, fixed timestep, diagnosing 30 fps, pooling, collision phases, lag compensation, ECS, and the portfolio conversation

## The honest note

**`[reference]`, and more so than most of this vault** — I have not shipped a game, not used Unity, Unreal or Godot in anger, and never had a frame budget. **Everything here is assembled from primary sources and from the parts of this vault that genuinely do apply.** Take the industry section in note 01 as reported rather than lived.

**What would close the gap:**

1. **Do a game jam.** 48 hours, one finished thing. **Nothing else in this list is close** — it tests scope discipline, finishing, and whether you actually enjoy it, all at once, for the price of a weekend
2. **Ship Pong.** Then Breakout. On itch.io, publicly. Two weekends
3. **Write a shader that colours a surface by its normal**, then by a light direction. Ten lines, and the graphics course stops being abstract
4. **Deliberately implement Euler integration and watch a pendulum gain energy**, then change two lines to semi-implicit and watch it stop. Note 04's central claim, verified in ten minutes
5. **Profile a frame with RenderDoc.** Seeing where 16 ms goes is worth more than this whole folder

**What's missing:** audio programming and middleware (FMOD/Wwise) entirely, animation systems at depth (blend trees, IK, motion matching), procedural generation, VR/AR, shader authoring in practice, console development, monetisation and live ops, and the entire design discipline — level design, systems design, narrative — which is a different field that happens to share a building.

→ [[PRIMETECHIE|Reading is not a rank.]]

## A note on priority

**This is now a full track** — course, engines, projects and an interview bank — rather than the map it started as. That doesn't change [[learning/04-one-active-course|the one-active-course rule]]: your own [[learning/catalogue|catalogue]] runs SWE 101 for a job search, and this is parked in the parking lot with a date on it.

**A track being complete is not a reason to start it.** It's here so that when games come round — and they will — nothing is missing.

## Related
- [[foundations/computer-graphics/README|computer graphics]] — the rendering half
- [[robotics/README|robotics]] — the other reason you came into tech, same maths
- [[foundations/gpu-and-parallel-computing/README|GPU & parallel computing]]
- [[project-ideas|project ideas]] · [[BUILD-PLAN|Build Plan]]
