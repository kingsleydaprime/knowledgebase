# Engines and the Game Loop

> **[Beginner → Intermediate]** · The loop at the centre of every game, the fixed-timestep problem, and how to choose an engine.

## The loop

Every game is this, forever:

```
while running:
    process_input()
    update(dt)        # advance the simulation
    render()
```

**That's the whole architecture.** Everything else is detail inside `update` and `render`.

It is a fundamentally different shape from most software in this vault. A [[backend/README|backend]] is **reactive** — it sleeps until a request arrives. A game is **proactive** — it runs continuously whether or not anything happened, because the world must be redrawn regardless.

## The timestep problem

Naively, `dt` is the time the last frame took. This breaks immediately.

**Variable timestep** — `update(actual_frame_time)`:
- ✓ Smooth, always in sync with real time
- ✗ **Physics becomes non-deterministic.** The same inputs on two machines produce different results
- ✗ Large `dt` after a hitch causes **tunnelling** — an object moves so far in one step it passes through a wall without ever intersecting it

**Fixed timestep** — always `update(1/60)`:
- ✓ Deterministic, stable, reproducible. Essential for replays, networking and debugging
- ✗ Drifts from real time if frames take longer than the step

**The standard solution — accumulate:**

```
accumulator += frame_time
while accumulator >= FIXED_DT:
    update(FIXED_DT)          # may run 0, 1, or several times
    accumulator -= FIXED_DT
render(accumulator / FIXED_DT)    # interpolate between the last two states
```

Physics runs at a fixed rate; rendering runs as fast as it can and **interpolates** between the two most recent simulation states so motion looks smooth at any refresh rate.

**Two things to know about this:**

**Cap the inner loop.** If a frame takes 2 seconds (a breakpoint, a stall), the accumulator demands 120 physics steps, which takes longer than a frame, which grows the accumulator further. That's the **spiral of death**. Clamp `frame_time` to something like 250 ms and accept a small drift.

**This is the canonical article every game programmer reads** — Glenn Fiedler's *Fix Your Timestep!* Genuinely worth reading in full.

**Determinism matters more than it looks.** It's what makes replays, lockstep multiplayer, and reproducible bug reports possible → [[game-development/06-multiplayer-and-networking|networking]]. Note the tension with floating point: the same code on different CPUs can differ in the last bit, which is why deterministic lockstep games sometimes use fixed-point arithmetic → [[foundations/numerical-methods/02-floating-point-and-error|floating point]].

## Entity Component System

The dominant architecture for games, and it exists because inheritance fails here in a specific, instructive way.

**The naive approach:** `Entity → Character → Player`. Then you need a door that takes damage, a crate that moves, a turret that's a character but doesn't walk. **You get either duplicated code or a base class with everything in it** — the deep-hierarchy failure from [[foundations/programming-fundamentals/13-objects-and-classes|objects and classes]], in its purest form.

**ECS instead:**

- **Entity** — just an ID. No data, no behaviour
- **Component** — plain data, no logic. `Position`, `Velocity`, `Health`, `Sprite`
- **System** — logic that runs over every entity having a given set of components

```
Player = Entity + Position + Velocity + Sprite + Health + PlayerInput
Rock   = Entity + Position + Sprite
Turret = Entity + Position + Sprite + Health + AI

MovementSystem: for all entities with (Position, Velocity) → position += velocity * dt
```

**Composition over inheritance, at architectural scale** — a rock that should now take damage gets a `Health` component. No hierarchy changes.

**And the performance argument is the real reason it won.** Components of one type are stored in contiguous arrays, so a system iterating `Position` walks memory linearly — every cache line fully used, hardware prefetching working. The object-oriented version chases pointers to scattered objects and stalls on cache misses.

**On modern hardware that difference is often 10× or more**, because a cache miss costs hundreds of cycles while the arithmetic costs one → [[foundations/computer-architecture/09-caches-in-depth|caches]] and [[foundations/computer-architecture/08-the-memory-hierarchy|the memory hierarchy]]. This is **data-oriented design**, and games hit it first because they were the software most limited by memory access patterns.

## Choosing an engine

| | **Unity** | **Unreal** | **Godot** |
|---|---|---|---|
| Language | **C#** | **C++** + Blueprints | **GDScript** (Python-ish), C# |
| Strength | Versatility, 2D, mobile, **huge asset store** | **AAA visuals**, out-of-the-box fidelity | **Lightweight, open source**, excellent 2D |
| Weakness | Fragmented (several render pipelines) | Heavy, steep C++ curve, large builds | Smaller ecosystem, 3D less mature |
| Licence | Per-seat / revenue tiers | 5% royalty above a threshold | **MIT — genuinely free** |
| Best for | Indie, mobile, prototyping, VR | Photorealistic 3D, large teams | 2D, small teams, learning |

**Recommendation, for someone curious rather than committed: Godot.** MIT-licensed with no revenue conditions, small enough to understand, GDScript is close enough to Python to be immediately productive → [[languages/06-python/README|Python]], and the editor is itself a Godot application, so the engine is legible in a way the others aren't. **The concepts transfer** — nodes, scenes, the loop, components — so nothing is wasted if you move to Unity later.

**Unity** if you want the largest job market and asset ecosystem. Note the 2023 runtime-fee episode: it was reversed after significant backlash, but it demonstrated that licence terms on a proprietary engine can change under you. That's a real trade-study input → [[foundations/systems-engineering/05-trade-studies|trade studies]].

**Unreal** if the goal is photorealism or AAA employment. Its C++ is a specific dialect with its own macros, reflection and memory conventions — closer to a framework than to the [[languages/05-cpp/README|C++]] in this vault.

**Don't agonise.** The transferable skills are the loop, vectors, state machines, and how to finish something. All three teach those.

## Related
- [[game-development/03-graphics-for-games|graphics for games]] — what `render()` does
- [[game-development/04-game-physics|game physics]] — what `update()` does
- [[foundations/computer-architecture/09-caches-in-depth|caches]] — why ECS is fast
- [[foundations/programming-fundamentals/13-objects-and-classes|objects and classes]] — the inheritance failure ECS answers

*Source: [reference] — cross-referenced against [roadmap.sh game-developer](https://roadmap.sh/game-developer); timestep material from Fiedler's *Fix Your Timestep!*.*
