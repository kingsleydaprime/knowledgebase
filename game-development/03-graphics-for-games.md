# Graphics for Games

> **[Intermediate]** · What real-time rendering adds to the graphics you already have — the frame budget, culling, batching, and why games cheat everywhere.

**This vault already has [[foundations/computer-graphics/README|a nine-note graphics course]]** — the rendering equation, the transform pipeline, rasterisation, shading and PBR, textures, the GPU pipeline, ray tracing, meshes and animation. Read that for the theory.

**This note is only what changes when you have 16 milliseconds.**

## Offline versus real-time

| | Film rendering | Game rendering |
|---|---|---|
| Per frame | **Hours** | **16 ms** |
| Approach | Simulate light properly | **Approximate convincingly** |
| Method | Path tracing, many samples | Rasterisation, precomputation, tricks |
| Wrong answer | Unacceptable | **Fine if nobody notices** |

**Every technique below is a lie chosen because it's cheap and looks right.** That's the discipline: not accuracy, but *perceptual sufficiency per microsecond*.

## The frame budget

At 60 fps you have 16.67 ms for everything, and rendering gets maybe 10–12 of it:

```
  2 ms  game logic, AI, physics
  1 ms  animation, skinning
  1 ms  culling and scene traversal
  3 ms  shadow map rendering
  5 ms  main geometry pass
  2 ms  post-processing
  2 ms  UI, audio, slack
```

**And two processors must both finish in time.** The CPU builds the frame; the GPU draws it. Either can be the bottleneck, and **the first question in any performance investigation is which** — the answer changes what you should do, and guessing wrong wastes days.

- **CPU-bound** → too many draw calls, too much per-object work, bad cache behaviour → batch, instance, use ECS
- **GPU-bound** → too many pixels, overdraw, expensive shaders → reduce resolution, simplify shaders, cull harder

**Draw calls are the classic CPU cost.** Each one is driver and API overhead. A thousand objects submitted individually can cost more in overhead than in drawing. The answers: **batching** (merge into one call), **instancing** (one call, many transforms), and modern APIs (Vulkan, DX12, Metal) that reduce per-call cost by design.

## Culling — the cheapest work is work not done

Everything here is about **not drawing things**:

**Frustum culling** — skip anything outside the camera's view volume. Test bounding volumes, not geometry.

**Occlusion culling** — skip anything hidden behind something else. Harder, since you must know what's in front.

**Backface culling** — skip triangles facing away. Free, done by the GPU, roughly halves triangle load on closed meshes.

**Level of detail (LOD)** — swap in simpler meshes with distance. A character might have 50k triangles up close and 500 at range. **The pop when it switches is the artefact you're trading against**, which is why LOD transitions get blended.

**Spatial partitioning** makes culling fast: quadtrees (2D), octrees, BVH, spatial hashes. **These are the [[foundations/dsa/README|tree structures]] you already know**, applied to space — the question "what is near this point" is the same as "what is in this subtree".

## Shaders

Programs that run on the GPU, massively in parallel → [[foundations/gpu-and-parallel-computing/README|GPU and parallel computing]].

- **Vertex shader** — runs per vertex; transforms into clip space
- **Fragment/pixel shader** — runs per pixel; computes colour. **This is where the cost is**, because there are far more pixels than vertices
- **Compute shader** — general-purpose GPU work: particles, culling, post-processing

Languages: **HLSL** (DirectX), **GLSL** (OpenGL/Vulkan), **MSL** (Metal), and engine-level graph editors that generate them.

**The mental shift is the same one as NumPy vectorisation** → [[languages/06-python/14-performance-and-the-runtime|performance]]: you write the code for *one* element and it runs on millions, so branches are expensive (divergent threads in a warp serialise) and memory access patterns dominate.

## The lies, catalogued

The techniques that make real-time rendering possible, each an approximation:

**Shadow maps** — render depth from the light's view, compare when shading. Cheap, and gives you aliasing, peter-panning and acne, which is why cascaded shadow maps exist for large scenes.

**Baked lighting** — precompute static lighting into lightmaps. **Free at runtime, and completely static.** The reason so many games have beautiful lighting and no movable lights.

**Ambient occlusion (SSAO)** — approximate contact shadows from the depth buffer. Physically unjustifiable, perceptually convincing.

**Normal mapping** — fake surface detail with a texture instead of geometry. **The single highest-value trick in real-time graphics** — a flat wall looks like carved stone at no geometric cost.

**Billboards and impostors** — draw distant complex objects as flat textured quads facing the camera. Every distant forest.

**Screen-space reflections** — reflect using only what's on screen. Breaks visibly at screen edges, and shipped everywhere anyway.

**Deferred rendering** — render surface properties to a G-buffer, then light in screen space. Decouples lighting cost from geometry, so hundreds of lights become affordable. Costs you cheap transparency and MSAA.

**Ray tracing** is now viable for parts of a frame on recent hardware (RTX, DXR) — typically hybrid: rasterise, then ray-trace reflections or shadows, then heavily denoise → [[foundations/computer-graphics/07-ray-tracing-and-path-tracing|ray tracing]].

## What to actually learn

**In order, and the first three cover most games:**

1. **The transform pipeline** — model → world → view → clip → screen. Understand it once and the rest follows → [[foundations/computer-graphics/02-the-transform-pipeline|transforms]]
2. **Write a simple shader.** Colour a surface by its normal. Then by a light direction. **Ten lines, and it demystifies the whole subject**
3. **Textures and UVs** — how images map onto geometry
4. **Basic lighting** — diffuse, specular, then PBR → [[foundations/computer-graphics/04-shading-and-lighting|shading]]
5. **Profile a frame.** RenderDoc, or your engine's profiler. **Seeing where 16 ms actually goes is worth more than any amount of reading**

**For 2D games you need almost none of this.** Sprites, transforms and a camera. Don't let the 3D pipeline put you off starting.

## Related
- [[foundations/computer-graphics/README|computer graphics]] — **the theory, already written**
- [[foundations/gpu-and-parallel-computing/README|GPU and parallel computing]] — the hardware
- [[game-development/02-engines-and-the-game-loop|the game loop]] — where rendering sits
- [[foundations/dsa/README|data structures]] — the trees under spatial partitioning

*Source: [reference] — cross-referenced against [roadmap.sh game-developer](https://roadmap.sh/game-developer).*
