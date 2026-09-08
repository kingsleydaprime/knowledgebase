# Ray Tracing and Path Tracing

**[Advanced]** — Solving light transport properly. BVHs, Monte Carlo, and why the image is noisy.

## Casting a ray

$$\mathbf{p}(t) = \mathbf{o} + t\mathbf{d}, \qquad t > 0$$

**Ray–sphere** is a quadratic. **Ray–triangle** is Möller–Trumbore, which computes the barycentric coordinates and $t$ in one go without needing the plane equation — **the standard, and worth knowing by name.**

**Ray–AABB** is the slab method: intersect against three pairs of parallel planes, keep the overlap. **Branch-free and fast**, which matters because it's the inner loop of every BVH traversal.

## Acceleration structures

**The naive cost is $O(n)$ per ray against $n$ triangles. At 1080p with a few bounces that's astronomically slow.**

**A bounding volume hierarchy fixes it:** a tree of nested bounding boxes, so a ray missing a box skips everything inside.

$$O(n) \longrightarrow O(\log n)$$

> **The BVH is what makes ray tracing possible at all.** It's the difference between billions of intersection tests and thousands.

**Building a good one matters.** The **surface area heuristic** is the standard: choose the split minimising

$$\text{cost} = \frac{A_L}{A}n_L + \frac{A_R}{A}n_R$$

**Intuition: the probability a random ray hits a box is proportional to its surface area.** So minimise expected traversal cost. **SAH-built BVHs are typically 2× faster to traverse than median-split ones**, and it's worth the build time.

**Alternatives:** kd-trees (better for static scenes, harder to rebuild), grids and octrees (simple, poor with non-uniform density). **BVH won** because it handles dynamic scenes with refitting and maps well to hardware.

**Two-level structures** — a bottom-level BVH per mesh, a top-level BVH over instances. **Move an object and you only update the top level**, which is what makes animation affordable. **This is exactly what the hardware APIs expose** (BLAS/TLAS in DXR and Vulkan RT).

## Whitted ray tracing

**The 1980 original — recursive, and deterministic.**

```
trace(ray):
    hit = nearest_intersection(ray)
    colour  = direct_lighting(hit)              # shadow ray per light
    colour += reflectivity * trace(reflect_ray)  # recurse
    colour += transparency * trace(refract_ray)  # recurse
    return colour
```

**Gives you sharp reflections, sharp refractions and hard shadows** — the classic chrome-spheres-and-checkerboard look, and that aesthetic is a direct consequence of the algorithm's limitations.

**What it can't do:** soft shadows, glossy reflections, colour bleeding, caustics — **anything requiring an *integral* rather than a single ray.** It samples one direction where physics integrates over many.

## Path tracing

**The correct approach: Monte Carlo estimation of the rendering equation.**

```
trace(ray, depth):
    if depth > max: return 0
    hit = nearest_intersection(ray)
    if not hit: return environment(ray)

    new_dir = sample_BRDF(hit)              # random, weighted by the BRDF
    L_in    = trace(new_dir, depth + 1)     # ONE bounce, randomly chosen
    return emitted(hit) + BRDF * L_in * cos(θ) / pdf(new_dir)
```

**One randomly-chosen path per sample.** Average many samples per pixel.

> **This converges to the true solution of the rendering equation** — Kajiya, 1986. **Every global effect emerges automatically**: soft shadows from sampling area lights, colour bleeding from diffuse bounces, caustics from specular paths, depth of field from sampling the lens aperture.
>
> **You don't implement soft shadows. You implement sampling, and soft shadows happen.** That's the appeal.

**The cost is noise, and it converges slowly:**

$$\text{error} \propto \frac{1}{\sqrt{N}}$$

**4× the samples for 2× less noise.** → [[foundations/numerical-methods/07-numerical-integration|Monte Carlo]]

**Which is why film renders take hours per frame at thousands of samples**, and why the noise-reduction techniques below are not optional extras.

## Variance reduction

**Making path tracing converge faster** — this is where most of the engineering is.

**Importance sampling** — sample directions proportional to where the integrand is large. **Sampling the BRDF lobe rather than the hemisphere uniformly is the single biggest win.**

**Next event estimation (direct light sampling)** — at each bounce, *also* cast a ray directly at a light rather than hoping a random bounce finds one.

> **Without NEE, a small bright light is almost never hit by chance** — you get an extremely noisy image or a black one. **With it, direct lighting converges almost immediately** and only indirect light remains noisy. **Essentially mandatory.**

**Multiple importance sampling (MIS)** — combine BRDF sampling and light sampling with weights that favour whichever is better for the current configuration. **Veach's 1995 result**, and it's what makes both glossy surfaces and small lights work in the same renderer.

**Russian roulette** — terminate paths probabilistically instead of at a fixed depth, dividing by the survival probability. **Unbiased, and it stops you wasting samples on paths contributing almost nothing.**

**Low-discrepancy sequences** — Sobol or Halton instead of pure random. **Better-distributed samples converge faster**, approaching $O(1/N)$ for smooth integrands.

**Blue-noise sample distribution across pixels** — the error becomes high-frequency, which denoisers and the eye handle far better than clumped noise. → [[foundations/computer-graphics/05-textures-and-sampling|Sampling]]

**Bidirectional path tracing** traces from the camera *and* the light and connects them — **much better for caustics and light through small openings**, which forward paths find by chance almost never.

## Denoising

**The development that made real-time ray tracing viable.**

> **Instead of tracing until the noise goes away, trace 1–4 samples per pixel and *denoise* aggressively.**

**Modern denoisers use auxiliary buffers** — albedo, normals, depth, motion vectors — **which are cheap and noise-free** because they come from the rasterised G-buffer. **Knowing the surface normal and albedo lets a denoiser separate lighting noise from genuine texture detail.**

**Temporal accumulation** reuses previous frames via motion vectors, which is where most of the effective sample count comes from.

**NVIDIA OptiX Denoiser, Intel Open Image Denoise, ReSTIR** for real-time; **ReSTIR in particular** (spatiotemporal reservoir resampling, 2020) reuses light samples across neighbouring pixels and frames and was a genuine step change.

**The cost is artefacts:** ghosting on fast motion, blurred detail, and temporal lag. **Denoising is why real-time ray tracing works and why it sometimes looks smeary.**

## Hardware ray tracing

**2018 onwards: dedicated silicon.**

**RT cores accelerate two things:** BVH traversal and ray–triangle intersection. **The rest — shading, sampling — runs on the normal shader cores.**

**The API model** (DXR, Vulkan RT, Metal) introduces new shader stages:

| Stage | Runs when |
|---|---|
| **Ray generation** | once per pixel — you cast the primary ray |
| **Intersection** | custom primitives (spheres, SDFs) |
| **Any-hit** | every candidate hit — alpha testing |
| **Closest-hit** | the nearest hit — shading |
| **Miss** | nothing hit — environment |

**Plus the shader binding table**, mapping geometry to shaders.

> **The practical reality: games are hybrid, not path-traced.** Rasterise primary visibility (fast, and every pixel needs it), then ray-trace the specific effects where rasterisation's approximations show most — **shadows first, then reflections, then ambient occlusion, then full global illumination.**
>
> **Full path-traced modes exist** (Cyberpunk's Overdrive, Portal RTX) and need aggressive denoising plus upscaling to be playable. **The trend is clear and the transition is gradual.**

## Where ray tracing goes beyond rendering

**The same machinery, elsewhere:**

**Collision detection and physics** — ray casts and sweeps. → [[foundations/computer-graphics/09-animation-and-simulation|Simulation]]

**Robotics** — lidar simulation is literally ray casting, and visibility queries for planning. → [[robotics/12-localisation-and-slam|SLAM]]

**Acoustics** — sound propagation modelled with rays.

**Radio propagation** — coverage prediction for wireless planning.

**Radiation transport** — medical physics and nuclear engineering use the same Monte Carlo transport equations.

**Differentiable rendering and NeRFs** — volumetric ray marching, differentiated to fit a scene to photographs.

## Practical notes

**Build a good BVH.** SAH is worth the build cost.

**Implement next event estimation early.** Without it your renders are unusably noisy.

**Use MIS** once you have both BRDF and light sampling.

**Use Russian roulette** rather than a hard depth cap.

**Watch for self-intersection.** A ray starting exactly on a surface re-hits it due to floating-point error — **shadow acne, again.** Offset the ray origin along the normal, or use a minimum $t$. **This is the first bug every ray tracer hits.** → [[foundations/numerical-methods/02-floating-point-and-error|Floating point]]

**Trace in linear colour space** and tone map at the end. → [[foundations/computer-graphics/04-shading-and-lighting|Colour]]

**Validate with a furnace test:** a scene with a uniform environment light and a white diffuse object should render the object exactly the same brightness as the background. **Any deviation means your BRDF isn't energy-conserving or your sampling weights are wrong.** It's the manufactured-solution idea applied to rendering, and it catches a whole class of subtle bugs. → [[foundations/numerical-methods/09-partial-differential-equations|Verification]]

**Start with a CPU path tracer.** *Ray Tracing in One Weekend* is genuinely a weekend, produces a real image, and teaches the whole structure before any API complexity.

---

## Related
- [[foundations/computer-graphics/01-how-rendering-works|How Rendering Works]] — the rendering equation
- [[foundations/numerical-methods/07-numerical-integration|Numerical Integration]] — Monte Carlo and variance reduction
- [[foundations/computer-graphics/04-shading-and-lighting|Shading and Lighting]] — the BRDFs being sampled
- [[foundations/computer-graphics/README|Computer graphics map]]
