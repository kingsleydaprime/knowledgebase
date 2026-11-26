---
id: 929dc59e-6d1a-4159-b981-6db2231ac4e4
---

# Getting Started

Getting started in game development means picking a tiny first game, using an existing engine and actually finishing it. Most beginners fail by building their own engine or by planning a game that is far too big. This lesson gives you a ladder of small projects to climb, plus where to learn and practise next.

## The three failure modes
<!-- bite: 9ab59a11-9bb4-44ed-bbb8-4e41d3f6298a -->

**1. Building an engine instead of a game.** You will learn a lot and ship nothing. If the goal is understanding, that's fine — *say so*. If the goal is a game, use an engine → [[game-development/02-engines-and-the-game-loop|engines]].

**2. Scope.** The classic first project is an open-world multiplayer RPG. It will not be finished. **Every experienced developer's advice converges on the same instruction: make something absurdly small, and finish it.**

**3. Endless tutorials.** Following a tutorial teaches you to follow tutorials → [[programming-fundamentals/12-choosing-what-to-build-next|tutorial hell]]. Do one, then build something different without one.

## The ladder
<!-- bite: cf9efb75-045c-462a-a7d3-5345ec3caeb9 -->

Each step introduces exactly one new thing. **Finish each — including menus, sound, and a build someone else can run.** The last 20% is where the learning is.

**1. Pong.** Input, movement, collision, score, a win state. **A weekend, and you'll still learn something.**

**2. Breakout.** Many objects, level layouts, particles, juice — screen shake, hit pauses, sounds. *Juice* is the difference between a mechanically correct game and one that feels good, and it's a real skill.

**3. A platformer, one level.** Character controller feel — coyote time, jump buffering, variable jump height. **Hand-authored movement, not physics** → [[game-development/04-game-physics|physics]]. Tile maps, a camera that follows well, checkpoints.

**4. A top-down shooter or roguelike.** Enemy AI (state machines → [[game-development/05-game-ai|game AI]]), spawning, pathfinding, procedural levels, progression.

**5. Something 3D and small.** Transforms and cameras in 3D → [[computer-graphics/15-the-transform-pipeline|transforms]], lighting, models and animation.

**6. Then pick a direction** — graphics, gameplay systems, tools, engine, networking.

**Ship each one.** itch.io is free and takes ten minutes. **A finished Pong on the internet beats an unfinished RPG on your disk**, and the act of finishing is the skill you're actually training.

## Game jams
<!-- bite: 2e0a8dd3-b8b8-442a-900a-1cb74ef4f219 -->

**The single highest-value activity in this list.** Ludum Dare, GMTK Jam, or any of the hundreds on itch.io: a theme, 48 hours, ship something.

They work because they force the thing you'll otherwise avoid — **brutal scope discipline and an actual finish line.** You'll produce more learning in a weekend than in a month of tutorials, and you get a finished artefact and feedback from strangers.

**Do one before you decide whether you like game development.** It is the cheapest possible test of the real experience.

## What to learn, and when
<!-- bite: b220b9a6-50a3-4b01-bc78-3bcaf3fa146d -->

**Now:** vectors, the game loop, state machines, one engine.
**Soon:** transforms, basic shaders, spatial partitioning, profiling.
**When you need it:** advanced rendering, physics internals, networking.
**Probably never:** most of the graphics roadmap, unless you go into graphics specifically.

**The [roadmap.sh game-developer roadmap](https://roadmap.sh/game-developer) is enormous** — 150+ topics, heavily weighted toward graphics and physics research. **Read it as a map of the field, not a curriculum.** Working through it linearly before making a game is a way to spend two years and ship nothing.

## What this vault already gives you
<!-- bite: a4dbbb4d-1dce-4b91-be8a-ce0cbf9306a4 -->

**This is the useful part, and it's why game-development is a thin folder rather than a thick one.** A surprising amount of the roadmap is already written here for other reasons:

| Roadmap area | Already in this vault |
|---|---|
| Linear algebra, vectors, matrices, transforms | [[computer-graphics/15-the-transform-pipeline\|transforms]] · [[robotics/04-rigid-body-transforms\|rigid body transforms]] |
| **Quaternions** | [[robotics/04-rigid-body-transforms\|robotics 04]] |
| Rendering, rasterisation, PBR, shading, ray tracing | [[computer-graphics/index\|computer graphics]] — 9 notes |
| GPU pipeline, shaders, parallelism | [[gpu-and-parallel-computing/index\|GPU & parallel computing]] |
| Integration, ODEs, numerical stability | [[mathematics/07-applied-and-computational/01-numerical-methods/index\|numerical methods]] |
| Trees, BVH, spatial partitioning, A\*, graphs | [[dsa/index\|DSA]] · [[mathematics/02-discrete-math/07-graph-theory\|graph theory]] |
| Neural nets, decision trees, RL, naive Bayes | [[machine-learning/index\|AI & ML]] |
| Memory, caches, data-oriented design | [[computer-architecture/index\|computer architecture]] |
| C++, Rust, Python | [[languages/index\|languages]] |
| Networking, UDP, latency | [[networking/index\|networking]] |
| Rigid body dynamics, materials | [[continuum-mechanics/index\|continuum mechanics]] |

**Game development is largely an integration discipline.** The maths and systems are the same ones robotics, graphics and simulation need — which is exactly why the skills transfer outward, and why the time isn't wasted even if you never ship a commercial game.

## Resources
<!-- bite: dba7684f-1f01-4038-b522-7d70c2499352 -->

- **Godot docs** — genuinely excellent, and the best free way in
- **Fiedler, *Fix Your Timestep!*** — the loop, properly
- **Gambetta, *Fast-Paced Multiplayer*** — prediction and reconciliation
- ***Game Programming Patterns*** (Nystrom) — **free online, and the best book on the subject.** Read it after your second project
- ***Real-Time Rendering*** (Akenine-Möller et al.) — the graphics reference
- ***Game Engine Architecture*** (Gregory) — if you want to know how engines work

## Related
<!-- bite: c518e2c7-eebd-45f7-81b6-f5a6c5967f52 -->
- [[game-development/01-what-game-development-actually-is|what game development is]] — including the industry, honestly
- [[programming-fundamentals/12-choosing-what-to-build-next|what to build next]] — the same argument, generally
- [[learning/04-one-active-course|one active course]] — **read this before starting**
- [[project-ideas|project ideas]] — the vault's build list

## About this lesson
<!-- bite: d583c87e-d89b-4e44-82ce-4f6bbd2718a8 -->

**Level:** Beginner. **Covers:** What to build first, in what order, and the specific ways beginners lose two years.

*Source: [reference] — cross-referenced against [roadmap.sh game-developer](https://roadmap.sh/game-developer).*
