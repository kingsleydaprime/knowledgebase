# Rasterisation

**[Intermediate → Advanced]** — Turning triangles into pixels. Edge functions, the z-buffer, and why interpolation needs a perspective correction.

## Why triangles

**Everything is triangles**, and the reasons are all practical:

**Always planar.** Three points define a plane; four might not.

**Always convex.** No self-intersection, no ambiguous interior.

**Simple interpolation** — barycentric coordinates work directly.

**Any polygon decomposes into triangles**, and any surface approximates as a mesh.

**So hardware only has to do one thing well**, and it does.

## Finding covered pixels

**The naive approach — compute the triangle's bounding box, test every pixel inside it.**

**The test uses edge functions.** For an edge from $\mathbf{a}$ to $\mathbf{b}$ and a point $\mathbf{p}$:

$$E(\mathbf{p}) = (\mathbf{b}_x - \mathbf{a}_x)(\mathbf{p}_y - \mathbf{a}_y) - (\mathbf{b}_y - \mathbf{a}_y)(\mathbf{p}_x - \mathbf{a}_x)$$

**That's the 2D cross product — its sign tells you which side of the line $\mathbf{p}$ is on.**

> **A point is inside the triangle iff all three edge functions have the same sign.** Three cross products, three sign checks. **That's the entire coverage test.**
>
> **And it's incremental:** $E$ is linear, so stepping one pixel right adds a constant. **The inner loop is three additions and three sign tests** — which is why this maps so beautifully to hardware, and why Pineda's 1988 formulation replaced scanline algorithms.

**Real hardware refines this:** tile-based traversal (test 8×8 blocks before individual pixels), hierarchical rejection, and **fragments processed in 2×2 quads** — because screen-space derivatives for texture filtering need neighbouring pixels. **That quad requirement is why a thin triangle wastes up to 75% of the shading work**, and it's a real cost of highly tessellated geometry.

## Barycentric coordinates

**The edge functions give you interpolation for free.**

$$\mathbf{p} = \lambda_0\mathbf{v}_0 + \lambda_1\mathbf{v}_1 + \lambda_2\mathbf{v}_2, \qquad \lambda_0+\lambda_1+\lambda_2 = 1$$

**The $\lambda$ values are the normalised edge functions** — the areas of the sub-triangles.

**Interpolate any per-vertex attribute** — colour, normal, texture coordinates, anything:

$$\text{attr}(\mathbf{p}) = \lambda_0 a_0 + \lambda_1 a_1 + \lambda_2 a_2$$

## Perspective-correct interpolation

**The subtlety that produces a very recognisable bug if you miss it.**

**Linear interpolation in *screen* space is wrong**, because the perspective divide is nonlinear. A texture on a floor stretching to the horizon should compress with distance; naive interpolation spreads it evenly.

**The fix — interpolate attribute/$w$ and $1/w$ linearly, then divide:**

$$\text{attr} = \frac{\lambda_0 \frac{a_0}{w_0} + \lambda_1\frac{a_1}{w_1} + \lambda_2\frac{a_2}{w_2}}{\lambda_0\frac{1}{w_0} + \lambda_1\frac{1}{w_1} + \lambda_2\frac{1}{w_2}}$$

> **Why it works: $1/w$ *is* linear in screen space, even though $w$ isn't.** So you interpolate the things that are linear and divide at the end.
>
> **The classic symptom of getting this wrong is the original PlayStation's warping textures** — it had no perspective correction in hardware, and floor and wall textures visibly swim as the camera moves. **A very recognisable look, and now you know its cause.**

**Modern hardware does this automatically.** In GLSL, `noperspective` opts out; `flat` disables interpolation entirely (useful for integer IDs, which must not be interpolated).

## The z-buffer

**Solving visibility: which surface is nearest?**

```
for each fragment:
    if depth < zbuffer[x][y]:
        zbuffer[x][y] = depth
        colour[x][y] = shaded_colour
```

**Per-pixel, order-independent, trivially parallel.** Catmull, 1974.

> **The z-buffer won because it needs no sorting.** The alternative — the painter's algorithm, drawing back to front — **fails on mutually overlapping triangles**, where no valid order exists. And sorting is $O(n\log n)$ per frame with global knowledge, which is exactly what rasterisation is trying to avoid.
>
> **The cost is memory and bandwidth**, which was prohibitive in 1974 and is trivial now.

**Early-Z** is the important optimisation: **test depth *before* running the fragment shader.** Rejected fragments cost nothing.

**But it's disabled if the shader writes `gl_FragDepth` or uses `discard`**, because the hardware can no longer know the depth in advance. **A single `discard` for alpha testing can therefore cost you a large fraction of your fill rate** — a real and non-obvious performance trap.

**A depth pre-pass** renders geometry depth-only first, then the real pass gets perfect early-Z rejection. **Worth it when shading is expensive.**

## Transparency

**The z-buffer's weakness, and it's fundamental.**

**Transparent surfaces must be blended in order**, because blending isn't commutative:

$$C = \alpha_{\text{src}}C_{\text{src}} + (1-\alpha_{\text{src}})C_{\text{dst}}$$

**So you must sort back-to-front** — reintroducing exactly the problem the z-buffer solved, and it fails on intersecting transparent geometry for the same reason the painter's algorithm did.

**The practical approaches:**

**Sort per object**, accept errors within objects. **What most games do**, and why transparent objects sometimes render in the wrong order.

**Alpha testing** — binary cut-out, no blending, works with the z-buffer. **Foliage and fences.** Costs early-Z.

**Order-independent transparency** — depth peeling (multiple passes), or weighted-blended OIT (an approximation in one pass). **Correct-ish, more expensive.**

**Premultiplied alpha** is worth adopting: store $(\alpha R, \alpha G, \alpha B, \alpha)$. **Blending becomes associative**, filtering doesn't produce dark fringes at edges, and compositing composes correctly. **It's simply the better representation** and the fringing artefact from non-premultiplied alpha is extremely common.

## Antialiasing

**A pixel is an area, not a point** — so a hard in/out coverage test aliases. → [[foundations/computer-graphics/01-how-rendering-works|Rendering as sampling]]

| Technique | How | Cost |
|---|---|---|
| **SSAA** | render bigger, downsample | **brutal** — 4× everything |
| **MSAA** | multiple *coverage/depth* samples, **one shading sample** | moderate |
| **FXAA/SMAA** | post-process edge detection and blur | **cheap**, blurry |
| **TAA** | accumulate over frames with jitter and motion vectors | **cheap, excellent — and ghosts** |
| DLSS/FSR | learned upscaling from a lower-resolution jittered render | needs hardware/model |

> **MSAA is the elegant one:** it recognises that **edge aliasing is a geometry problem, not a shading problem.** Sample coverage at 4 or 8 points per pixel but shade once — most of the quality of SSAA for a fraction of the cost.
>
> **It fails on deferred rendering** (the G-buffer would need multisampling throughout, which is prohibitive), and **doesn't help shader aliasing** — specular highlights and alpha-tested foliage still shimmer. **That's why the industry moved to TAA** despite its ghosting artefacts, and why upscalers like DLSS are essentially TAA with a learned reconstruction.

## Deferred shading

**A structural alternative worth knowing.**

**Forward rendering:** rasterise and shade in one pass. **Cost is $O(\text{objects} \times \text{lights})$**, and it wastes shading on fragments later overdrawn.

**Deferred:** rasterise into a **G-buffer** (position/depth, normal, albedo, roughness), then a second full-screen pass shades using it.

> **Cost becomes $O(\text{objects}) + O(\text{pixels}\times\text{lights})$** — **and shading happens exactly once per visible pixel**, which decouples light count from geometry complexity. **Hundreds of lights become feasible.**

**The costs:** heavy bandwidth (the G-buffer is several full-screen textures), **MSAA is impractical**, transparency needs a separate forward pass, and material variety is limited by what fits in the G-buffer.

**Forward+ / clustered forward** is the modern compromise: a depth pre-pass, then bin lights into screen-space tiles or 3D clusters so each fragment only evaluates nearby lights. **Keeps MSAA and material flexibility, scales to many lights.** This is what most current engines use.

## Practical notes

**Cull before rasterising.** Frustum and backface culling are nearly free. → [[foundations/computer-graphics/02-the-transform-pipeline|Culling]]

**Minimise overdraw.** Draw roughly front-to-back for opaque geometry so early-Z rejects more; back-to-front for transparent.

**Avoid `discard` and depth writes in shaders** unless necessary — they disable early-Z.

**Watch for tiny triangles.** Quad-based shading means sub-pixel triangles waste up to 75% of their work. **This is why extreme tessellation has diminishing returns**, and what Nanite's software rasteriser for small triangles addresses.

**Batch draw calls.** Each has CPU overhead and a potential pipeline flush. Instancing, texture atlases, and indirect drawing.

**Use premultiplied alpha.**

**Profile with a graphics debugger** — RenderDoc is excellent and free. **It shows you every draw call, every bound resource, and the state of every buffer** — the equivalent of `perf` for rendering.

---

## Related
- [[foundations/computer-graphics/04-shading-and-lighting|Shading and Lighting]] — computing the colour
- [[foundations/computer-graphics/06-the-gpu-graphics-pipeline|The GPU Graphics Pipeline]] — how this runs in hardware
- [[foundations/computer-graphics/02-the-transform-pipeline|The Transform Pipeline]] — what feeds this
- [[foundations/computer-graphics/README|Computer graphics map]]
