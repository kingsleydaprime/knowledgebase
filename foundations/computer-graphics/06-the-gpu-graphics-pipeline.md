# The GPU Graphics Pipeline

**[Intermediate → Advanced]** — Shader stages, the modern APIs, and how the graphics pipeline relates to the compute model.

> **[[foundations/gpu-and-parallel-computing/02-gpu-architecture|GPU Architecture]] covers the hardware** — SMs, warps, memory. **This note is the graphics-specific programming model built on it.**

## The stages

```
 vertex buffer
      │
      ▼  VERTEX SHADER      ← programmable: transform each vertex
      ▼  tessellation       ← optional, programmable
      ▼  GEOMETRY SHADER    ← optional, and usually avoid it
      ▼  clip / cull / raster  ← FIXED FUNCTION
      ▼  FRAGMENT SHADER    ← programmable: colour each fragment
      ▼  depth / stencil / blend  ← fixed function (mostly)
 framebuffer
```

**Programmable stages you write; fixed-function stages you configure.**

**Vertex shader** — runs once per vertex. **Transform to clip space**, pass through attributes. → [[foundations/computer-graphics/02-the-transform-pipeline|Transforms]]

**Fragment (pixel) shader** — runs once per covered fragment. **Compute colour.** This is where shading and texturing happen, and **it's usually where the time goes.** → [[foundations/computer-graphics/04-shading-and-lighting|Shading]]

**Geometry shader** — can emit new primitives. **Flexible and slow on most hardware** — it serialises output ordering. **Compute shaders are almost always the better answer**, and GS is essentially deprecated in practice.

**Tessellation** — subdivide patches on-GPU. Useful for displacement and terrain; largely superseded by mesh shaders and by Nanite-style approaches.

## Compute shaders

**The stage that broke the pipeline open.**

**A compute shader is a general-purpose kernel with no fixed-function graphics around it** — the same model as [[foundations/gpu-and-parallel-computing/03-the-programming-model|CUDA]]: workgroups, shared memory, barriers.

**What it enabled:**

- **Post-processing** — bloom, tone mapping, blur, TAA resolve
- **Particle systems** entirely on-GPU
- **Culling and draw-call generation** on-GPU → GPU-driven rendering
- **Physics, cloth, fluids**
- **Light binning** for clustered forward shading
- **Building acceleration structures**

> **"GPU-driven rendering" is the current direction**: the GPU culls, decides what to draw, and generates its own draw calls via indirect dispatch — **with the CPU barely involved.** The CPU submitting draw calls was the bottleneck, and compute shaders removed it.

**Mesh shaders** (2018+) replace the vertex/geometry/tessellation front end with a compute-like model that emits small "meshlets" directly. **More flexible, better culling granularity**, and it's how Nanite works.

## The APIs

| API | Character |
|---|---|
| **OpenGL** | old, high-level, global state machine. **Easiest to learn**, effectively legacy |
| **Vulkan** | explicit, verbose, low overhead. **~1000 lines for a triangle** |
| **Direct3D 12** | Windows/Xbox equivalent of Vulkan |
| **Metal** | Apple. **Nicer ergonomics than Vulkan**, same explicitness |
| **WebGPU** | **the modern portable one.** Vulkan-like concepts, sane defaults |

> **The explicit APIs exist because the drivers were guessing.** OpenGL drivers did shader recompilation, state validation and memory management behind your back — **unpredictable hitches, and vendor-specific behaviour.** Vulkan and D3D12 move those decisions to you: explicit memory allocation, explicit synchronisation, pre-compiled pipeline state objects.
>
> **The cost is enormous verbosity.** The benefits are predictable performance and multi-threaded command recording — **which matter for a shipping engine and are pure overhead for learning.**

**The practical recommendation: learn on WebGPU or OpenGL, not Vulkan.** WebGPU has the modern concepts (explicit pipelines, bind groups, command buffers) without the 1000-line triangle, and it runs in a browser. **You'll learn the ideas faster and can move to Vulkan later if you need to.**

## Shading languages

**GLSL** (OpenGL/Vulkan), **HLSL** (D3D, and increasingly everywhere), **WGSL** (WebGPU), **MSL** (Metal). **All C-like, and mutually translatable** via SPIR-V and tools like SPIRV-Cross.

```glsl
// vertex
layout(location=0) in vec3 pos;
uniform mat4 mvp;
void main() { gl_Position = mvp * vec4(pos, 1.0); }

// fragment
layout(location=0) out vec4 colour;
void main() { colour = vec4(1.0, 0.5, 0.2, 1.0); }
```

**Shader performance rules, and they're the [[foundations/gpu-and-parallel-computing/02-gpu-architecture|warp]] rules restated:**

**Avoid divergent branches.** Threads in a warp execute both paths. **Uniform branches (same for the whole draw) are free.**

**Minimise texture fetches**, and keep them cache-coherent.

**Watch register pressure.** Complex shaders reduce occupancy.

**Avoid `discard`** — it disables early-Z. → [[foundations/computer-graphics/03-rasterisation|Early-Z]]

**Prefer built-ins** (`dot`, `mix`, `clamp`, `fma`) — they map to single instructions.

**Do work at the coarsest useful stage.** Per-object uniform > per-vertex > per-fragment. **Moving a calculation from the fragment shader to the vertex shader can be a 100× reduction in how often it runs.**

## Resource binding

**Getting data to shaders**, and it's where the APIs differ most.

**Uniform buffers (UBO/constant buffers)** — small, read-only, frequently updated. Matrices, material parameters.

**Storage buffers (SSBO)** — large, read-write. Particle data, instance data, compute output.

**Textures and samplers** — the sampler (filtering, wrap mode) is separate from the texture in modern APIs, so one texture can be sampled several ways.

**Push constants** — tiny, fast, no buffer needed. Per-draw indices.

**Descriptor sets / bind groups** — group resources by update frequency. **The standard organisation:**

```
 set 0:  per-frame     (camera, time, lights)
 set 1:  per-material  (textures, parameters)
 set 2:  per-object    (model matrix)
```

**Bind rarely-changing sets once and leave them.** This organisation directly minimises state changes, which is why the APIs expose it.

**Bindless** — put everything in one large array and index it. **Removes most binding overhead** and is required for GPU-driven rendering.

## Synchronisation

**The hardest part of the explicit APIs, and where the bugs are.**

**The CPU and GPU run asynchronously.** The GPU is typically 1–3 frames behind.

**What you must handle:**

**Don't write a buffer the GPU is reading.** Use **double or triple buffering** — $N$ copies of per-frame resources, cycled.

**Fences** — CPU waits for GPU completion. Use them to know when a frame's resources are reusable.

**Semaphores** — GPU-to-GPU ordering between queues.

**Barriers** — the subtle one. **Declare that a resource's *layout* and *access pattern* are changing** (e.g. render target → shader-readable). **The GPU needs this for cache flushes and layout transitions**, and a missing barrier gives you a race that works on one vendor and corrupts on another.

> **Vulkan's validation layers are essential, not optional.** They catch missing barriers, wrong layouts, incorrect usage flags and synchronisation hazards. **Develop with them on.** The equivalent in D3D12 is the debug layer.

## Debugging and profiling

**RenderDoc** — capture a frame, inspect **every draw call, every bound resource, every intermediate buffer, and step through shader execution.** Free, excellent, and the single most valuable graphics tool.

**Nsight Graphics / PIX / Xcode Frame Debugger** — vendor tools with hardware counters.

**What to look for:**

**Draw call count.** Thousands per frame means CPU-bound; batch and instance.

**Overdraw.** Visualise it — RenderDoc can. **Heavy overdraw means poor sorting or too much transparency.**

**Are you CPU- or GPU-bound?** Reduce resolution: **if the frame rate doesn't change, you're CPU-bound** and optimising shaders is wasted effort. **A ten-second test that saves days.**

**Shader complexity vs bandwidth.** Same roofline reasoning as compute. → [[foundations/gpu-and-parallel-computing/06-performance-and-the-roofline|Roofline]]

**Pipeline stalls** from synchronisation — visible on a timeline as GPU gaps.

## Practical notes

**Start with WebGPU or OpenGL.** Vulkan's explicitness is a distraction while learning the concepts.

**Batch and instance.** Draw call overhead is often the real limit. One instanced draw of 10,000 objects beats 10,000 draws.

**Sort draws by state** — pipeline, then material, then object. **State changes are expensive.**

**Compile pipelines at load time**, not during rendering. **Shader compilation hitches are the classic modern stutter**, and precompilation or a pipeline cache is the fix.

**Test the resolution trick** before optimising anything.

**Use compute shaders** for anything that isn't literally rasterising triangles.

**Read the validation layer output.** It is telling you about real bugs.

---

## Related
- [[foundations/gpu-and-parallel-computing/02-gpu-architecture|GPU Architecture]] — the hardware underneath
- [[foundations/computer-graphics/03-rasterisation|Rasterisation]] — the fixed-function stage
- [[foundations/gpu-and-parallel-computing/03-the-programming-model|The Compute Programming Model]] — the sibling model
- [[foundations/computer-graphics/README|Computer graphics map]]
