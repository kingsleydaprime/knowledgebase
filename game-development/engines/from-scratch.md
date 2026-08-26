# From Scratch

> **[Advanced]** · Writing your own engine — what you actually learn, what it costs, and the honest framing.

## Say which project you're doing

**[[game-development/01-what-game-development-actually-is|Note 01]] names this as the commonest way an ambitious first project dies:** building an engine while believing you're building a game. They are different projects with different outcomes.

- **"I want to understand how engines work"** → excellent project. Do it deliberately, and don't expect a game
- **"I want to ship a game"** → use an engine. The one you'd write is thousands of person-years behind

**Both are legitimate. Conflating them is not.**

## The layers, in the order you'll build them

1. **A window and an input event loop** — SDL3, GLFW, or raw platform APIs
2. **A render backend** — OpenGL or WebGPU to start; Vulkan/DX12 if you want the pain → [[foundations/computer-graphics/06-the-gpu-graphics-pipeline|the GPU pipeline]]
3. **The game loop with a fixed timestep** → [[game-development/02-engines-and-the-game-loop|note 02]]. **Get this right first; everything else depends on it**
4. **Maths** — vectors, matrices, quaternions → [[robotics/04-rigid-body-transforms|transforms]]
5. **A scene representation** — a hierarchy, or an ECS
6. **Asset loading** — images, meshes (glTF), audio
7. **Collision and physics** → [[game-development/04-game-physics|note 04]]
8. **Audio mixing**
9. **A text renderer.** *(Everyone underestimates this. Font atlases, kerning, Unicode, and it's needed by every debug overlay)*
10. **Tooling** — a level editor, hot reload. **This is where the person-years actually go** → [[game-development/07-tools-and-production|tools and production]]

**Steps 1–5 are a satisfying month. Steps 6–10 are where engine projects quietly stop.**

## What you genuinely learn

**Things no engine user finds out:**

- **Where the frame budget actually goes**, because you wrote every part of it
- **Why engines make the API choices they do** — most "weird" engine decisions turn out to be forced
- **Data-oriented design as a felt constraint**, not a slogan → [[foundations/computer-architecture/09-caches-in-depth|caches]]
- **The whole [[foundations/computer-graphics/README|graphics course]] becomes concrete**
- **Memory management under a hard deadline** — why per-frame allocation is a bug → [[languages/04-c/README|C]] · [[languages/03-rust/README|Rust]]

**It is one of the best learning projects in software**, and this vault's [[build-your-own-shit/README|build-your-own-shit]] folder exists on the same premise.

## The languages

| | Why | Against |
|---|---|---|
| **C** | Simple, total control, tiny toolchain | You build everything, including safety |
| **C++** | The industry default; STL and RAII | Complexity, build times |
| **Rust** | Memory safety without GC; excellent tooling | Borrow checker vs graph-shaped scene data is genuinely awkward |
| **Zig** | C's simplicity, better ergonomics, great C interop | Young; smaller ecosystem |
| **Odin / Jai** | Designed with games in mind | Very small ecosystems |

**Rust deserves a specific caution:** scene graphs and entity references are exactly the aliasing-heavy, mutually-referential structures the borrow checker is strictest about. The idiomatic answer is arena/index-based storage — which is **also what ECS does anyway**, so it converges → [[game-development/02-engines-and-the-game-loop|ECS]] · [[foundations/programming-language-theory/07-effects-and-substructural-types|linearity]].

## Don't write these

Even in a from-scratch engine, use libraries for the solved problems:

- **Windowing/input** — SDL3, GLFW
- **Maths** — glm, cglm, nalgebra
- **Image loading** — stb_image
- **Font rendering** — stb_truetype, FreeType
- **glTF parsing** — cgltf, tinygltf
- **Debug UI** — **Dear ImGui.** Non-negotiable; you need a debug overlay from week one
- **Audio** — miniaudio
- **Physics** — Jolt, Box2D. *(Unless physics is the thing you're learning)*

**Writing your own PNG decoder teaches you about PNG, not about engines.**

## The honest scope

**A month** — window, loop, a rotating textured cube, basic input. Genuinely satisfying.
**Three months** — a small 2D game with collision, audio and a level format.
**A year+** — something you'd call an engine, with tooling, and it will do less than Godot does on day one.

**The strongest version of this project:** build the engine *and* one small finished game with it. The game forces you to build the parts that engine projects skip, and it produces something you can show → [[game-development/08-getting-started|getting started]].

## Related
- [[build-your-own-shit/README|build your own shit]] — the same premise, other systems
- [[game-development/02-engines-and-the-game-loop|the game loop]] — build this first
- [[foundations/computer-graphics/README|computer graphics]] · [[foundations/computer-architecture/README|architecture]]

*Source: [reference] — written Aug 2026.*
