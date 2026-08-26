# Game Dev Interview — The Round

**Game interviews are unusually technical and unusually concrete.** Expect maths on a whiteboard, performance reasoning, and a portfolio conversation that goes deeper than in most software roles — because in games, *"show me the thing you shipped"* is the primary signal.

From the [[game-development/README|game development course]].

---

### Q1. [Beginner→Intermediate] 🔥 What's the dot product, and what do you use it for?

**Strong answer covers:** $\mathbf{a}\cdot\mathbf{b} = |\mathbf{a}||\mathbf{b}|\cos\theta$. For **unit** vectors it's just $\cos\theta$ — so it's an angle test that costs three multiplies and two adds.

**The uses, which is what they're actually asking for:**
- **Is the enemy in front of me?** `dot(forward, toTarget) > 0`
- **Field-of-view check** — `dot(forward, normalize(toTarget)) > cos(fovRadians/2)`. **Cheaper and more robust than computing the angle**, because no `acos`
- **Backface culling** — `dot(normal, viewDir) < 0`
- **Diffuse lighting** — `max(0, dot(normal, lightDir))` → [[foundations/computer-graphics/04-shading-and-lighting|shading]]
- **Projection** of one vector onto another

**The cross product**, for contrast: gives a perpendicular; used for surface normals, "is the target to my left or right" (sign of the y component in 2D), and torque.

**The senior point:** *"compare against `cos(threshold)` rather than calling `acos`"* is the answer that shows you've written this rather than read it — the trig call is dramatically more expensive and you don't need it.

---

### Q2. [Intermediate] 🔥 Why do engines separate `Update` and `FixedUpdate`?

**Strong answer covers:** rendering runs as fast as it can; **physics must run at a fixed rate or it isn't deterministic.** With a variable timestep, the same inputs produce different results on different machines, and large frame gaps cause **tunnelling** — an object moves further in one step than the wall is thick, so no intersection is ever tested.

**The standard structure:**
```
accumulator += frameTime
while accumulator >= FIXED_DT:
    physicsStep(FIXED_DT)
    accumulator -= FIXED_DT
render(accumulator / FIXED_DT)      // interpolate between the last two states
```

**Details that matter:**
- **Cap the inner loop**, or a long frame demands more steps than fit in a frame, which demands more still — the **spiral of death**
- **Interpolate for rendering**, or motion looks juddery at refresh rates that don't divide the physics rate
- Determinism is what makes **replays and lockstep multiplayer** possible → [[game-development/06-multiplayer-and-networking|networking]]

**The senior point:** naming *"putting `Rigidbody` code in `Update`"* as the classic bug — and that it makes gameplay frame-rate dependent, so the game plays differently on a better machine → [[game-development/02-engines-and-the-game-loop|note 02]].

---

### Q3. [Intermediate] 🔥 The game runs at 30 fps. Walk me through diagnosing it.

**Strong answer covers a method, not a list of fixes:**

1. **CPU-bound or GPU-bound?** **Ask this first, because the answer changes everything.** The cheap test: drop the render resolution. Frame rate unchanged → **CPU-bound**. Frame rate improves → **GPU-bound**
2. **CPU-bound** → profile. Too many draw calls? Per-object `Update` on thousands of objects? GC spikes? Physics with too many active bodies?
3. **GPU-bound** → overdraw, expensive fragment shaders, too many pixels, shadow-map resolution, post-processing chain
4. **Fix one thing, measure again**

**The specific fixes worth naming:** batching and instancing for draw calls, object pooling to eliminate per-frame allocation, LOD and culling, reducing shadow cascade count, simplifying the most expensive shader.

**The senior point:** **"the worst frame is the experience, not the average"** → [[game-development/01-what-game-development-actually-is|note 01]]. A 60 fps average with a 200 ms hitch every two seconds is a broken game, and an average-only metric hides it. Look at the frame-time graph, not the fps counter.

---

### Q4. [Intermediate] Why is object pooling worth the complexity?

**Strong answer covers:** allocation in the game loop causes **garbage collection**, and a GC pause is a visible stutter within a 16 ms budget. Pooling pre-allocates, then deactivates and reuses rather than destroying and recreating.

**Where it matters:** bullets, particles, enemies, UI elements, audio sources — anything spawned frequently.

**Details that matter:**
- In C#/Unity the concern is the managed heap and GC spikes → [[languages/07-csharp/README|C#]]
- In C++ it's fragmentation and allocator cost, and the answer is usually an **arena or pool allocator** → [[foundations/os/05-memory-allocation|memory allocation]]
- **Pooling has a cost:** objects must be reset properly on reuse, and stale state is a classic bug — a pooled enemy that remembers its old health

**The senior point:** this is the same instinct as data-oriented design — **contiguous, reused memory beats scattered allocation**, and the reason is cache locality as much as GC → [[foundations/computer-architecture/09-caches-in-depth|caches]].

---

### Q5. [Intermediate] 🔥 How do you detect collisions efficiently?

**Strong answer covers the two-phase split**, which is the whole answer:

**Broad phase** — cheaply eliminate pairs that can't possibly touch. Test AABBs using a spatial structure: a uniform grid, a BVH/dynamic AABB tree, or sweep-and-prune. **Turns O(n²) into roughly O(n log n)**.

**Narrow phase** — exact tests on survivors. Sphere-sphere is trivial; convex shapes use **SAT** (simpler, boxes and simple polyhedra) or **GJK** for intersection plus **EPA** for penetration depth.

**Details that matter:**
- **Concave shapes are decomposed into convex pieces** — every efficient algorithm assumes convexity, which is why engines ask for convex hulls
- **Fast objects need continuous collision detection or a raycast along the path**, or they tunnel → Q2
- Collision *detection* and collision *response* are separate problems

**The senior point:** naming the O(n²) problem unprompted. *"1,000 objects is half a million pair tests per frame"* is the sentence that shows you understand why broad phase exists → [[game-development/04-game-physics|note 04]].

---

### Q6. [Advanced] 🔥 Why do I sometimes die behind cover in an online shooter?

**Strong answer covers:** **lag compensation**, and it's a deliberate choice rather than a bug.

You are always seeing other players **in the past** — client-side interpolation renders them ~100 ms behind, using snapshots. When the shooter fires, the server **rewinds** every other player to where the *shooter's client* showed them at that moment, and tests the hit there.

So on the shooter's screen you were exposed; on yours you'd already reached cover. **The server sided with the shooter.**

**Details that matter:**
- **Client prediction** makes your own movement feel instant; **server reconciliation** corrects it, and a mismatch is the "rubber-banding" you feel
- **Never trust the client** — a client reporting its own hits is an aimbot waiting to happen
- The alternative (favouring the victim) makes shooting feel unresponsive, which players report as a worse experience

**The senior point:** the trade is explicit — **someone must experience the inconsistency**, and the design decision is who. Being able to state that as a *choice* rather than a defect is the answer → [[game-development/06-multiplayer-and-networking|note 06]].

---

### Q7. [Intermediate] Why is ECS faster than an object hierarchy?

**Strong answer covers:** **cache locality**, not algorithmic complexity.

In an OO hierarchy, objects are scattered on the heap; iterating them chases pointers and stalls on cache misses. In ECS, components of one type live in **contiguous arrays**, so a system iterating `Position` walks memory linearly — every cache line fully used, hardware prefetching working.

**A cache miss costs hundreds of cycles; the arithmetic costs one.** That ratio is the whole argument, and it's often 10× or more.

**The secondary benefit — and the reason it was adopted before performance mattered:** composition over inheritance. A rock that should now take damage gets a `Health` component; no hierarchy changes → [[foundations/programming-fundamentals/13-objects-and-classes|note 13]].

**The senior point:** ECS is not free — it's harder to debug, harder to reason about one entity, and overkill for a small game. **"We used plain GameObjects because we had 200 entities, not 200,000"** is a strong answer → [[foundations/computer-architecture/08-the-memory-hierarchy|memory hierarchy]].

---

### Q8. [Intermediate] Talk me through something you shipped.

**Not a technical question, and often the most heavily weighted one.**

**What they're listening for:**
- **You finished it.** Scope discipline is the single most valued trait in this industry → [[game-development/07-tools-and-production|scope kills projects]]
- **A specific hard problem** and how you diagnosed it — not "I made a platformer" but "the jump felt wrong and I fixed it with coyote time and jump buffering"
- **What you'd do differently.** Uncritical enthusiasm about your own work reads as inexperience
- **Feel.** Games are judged subjectively, and being able to talk about *why* something feels good is a real skill
- **Evidence of players.** Even a game jam with twenty ratings beats a polished thing nobody played

**The strongest single preparation for this round is a finished game jam entry** → [[game-development/08-getting-started|getting started]]. A weekend produces a shippable artefact, public feedback, and a genuine scope story.

---

## Related
- [[game-development/README|the course]] · [[game-development/engines/README|engines]]
- [[foundations/computer-graphics/10-practice-exercises|graphics exercises]] — the reps behind Q1 and Q3
- [[project-ideas|project ideas]] — the game-development tier
- [[INTERVIEW|Interview Prep Index]]

*Source: [reference] — assembled Aug 2026 from the course. **See the scope note in the folder README.***
