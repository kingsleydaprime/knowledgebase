# How Rendering Works

**[Intermediate]** — The two paradigms, why one won for real-time and the other for film, and what they're both approximating.

**Source:** `[reference]` — see [[foundations/computer-graphics/README|the domain note]].

## The problem

**Given a description of a 3D scene, produce a 2D image.**

**The scene:** geometry (triangles, usually), materials, lights, and a camera.

**The image:** a grid of pixels, each with a colour.

**Two fundamentally different ways to bridge that gap**, and the difference is which direction you iterate.

## Rasterisation — loop over geometry

```
for each triangle:
    project to screen space
    for each pixel it covers:
        compute colour, keep if nearest
```

**Object-order.** You ask "where does this triangle land?"

**The killer property: it's embarrassingly parallel over triangles and pixels, and it never needs the whole scene at once** — stream triangles through, and each is independent.

**Which is why it's what GPUs were built for.** The entire fixed-function graphics pipeline is a rasteriser in silicon. → [[foundations/computer-graphics/03-rasterisation|Rasterisation]]

**What it's bad at:** anything requiring a triangle to know about *other* triangles. **Shadows, reflections, refraction and indirect light are all global effects, and rasterisation is fundamentally local.** Every real-time technique for those is an approximation bolted on — shadow maps, environment maps, screen-space reflections.

## Ray tracing — loop over pixels

```
for each pixel:
    cast a ray from the camera
    find the nearest intersection
    compute colour (possibly casting more rays)
```

**Image-order.** You ask "what does this pixel see?"

**The killer property: global effects are natural.** A reflection is just another ray. A shadow is a ray toward the light. Refraction, depth of field and motion blur all fall out of casting the right rays.

**What it's bad at:** you need the whole scene queryable at once, and naive intersection is $O(\text{triangles})$ per ray. **Acceleration structures (BVH) fix the complexity; the memory requirement is inherent.** → [[foundations/computer-graphics/07-ray-tracing-and-path-tracing|Ray Tracing]]

> **The honest summary:** rasterisation is fast and local; ray tracing is slow and global. **Real-time rendering spent thirty years finding clever approximations of global effects within a local framework** — and hardware ray tracing (2018 onwards) is the beginning of that pressure easing.
>
> **Modern engines are hybrid:** rasterise primary visibility (fast, and every pixel needs it), ray-trace the effects that need global information.

## The rendering equation

**What both approaches are approximating.** Kajiya, 1986:

$$L_o(\mathbf{x}, \omega_o) = L_e(\mathbf{x},\omega_o) + \int_\Omega f_r(\mathbf{x}, \omega_i, \omega_o)\,L_i(\mathbf{x},\omega_i)\,(\omega_i\cdot\mathbf{n})\,d\omega_i$$

**In words: light leaving a point in a direction = light it emits + all incoming light, weighted by how the surface reflects it and by the angle.**

| Term | Meaning |
|---|---|
| $L_o$ | outgoing radiance — **what you want** |
| $L_e$ | emitted (only for light sources) |
| $f_r$ | **BRDF** — how the material reflects → [[foundations/computer-graphics/04-shading-and-lighting\|Shading]] |
| $L_i$ | incoming radiance **from everywhere** |
| $(\omega_i\cdot\mathbf{n})$ | Lambert's cosine — glancing light contributes less |

> **The difficulty is that $L_i$ depends on $L_o$ at every other surface.** It's a recursive integral equation over an infinite-dimensional space — **light bounces forever.**
>
> **Every rendering algorithm ever written is a way of approximating this integral.** Rasterised direct lighting truncates it at one bounce with no integral at all. Path tracing estimates it by Monte Carlo. **Knowing the equation tells you exactly what each technique is throwing away.**

**And note the integral is high-dimensional**, which is why Monte Carlo is the method of choice — quadrature dies above ~4 dimensions and Monte Carlo's error is dimension-independent. → [[foundations/numerical-methods/07-numerical-integration|Monte Carlo]]

## The real-time pipeline

**What happens for each frame at 60 Hz:**

```
 scene data
     │
     ▼  VERTEX PROCESSING   transform to clip space
     ▼  CLIPPING & CULLING  discard what's invisible
     ▼  RASTERISATION       triangles → fragments
     ▼  FRAGMENT SHADING    compute colour per fragment
     ▼  OUTPUT MERGING      depth test, blending
  framebuffer
```

**Covered in detail across notes 02–06.** The structure to notice: **it's a stream, with each stage massively parallel and no stage needing global scene information.**

## Rendering as sampling

**A framing that unifies a surprising amount, and connects to [[foundations/information-theory/README|information theory]].**

**A pixel is not a point — it's an area.** Its correct colour is the *average* of the image over that area:

$$C_{\text{pixel}} = \int_{\text{pixel}} \text{image}(x,y)\,dx\,dy$$

**Rendering is estimating that integral by sampling.** And sampling theory then explains most visual artefacts:

**Aliasing** — sampling below the Nyquist rate. **Jagged edges, shimmering textures, moiré patterns.** Fixed by supersampling (more samples), mipmapping (pre-filtering), or reconstruction filters. → [[foundations/computer-graphics/05-textures-and-sampling|Textures and Sampling]]

**Noise** — too few Monte Carlo samples. **Path tracing's grainy look**, and it decreases as $O(1/\sqrt{N})$, which is why film renders take hours.

**Banding** — quantisation error from too few bits per channel. Dithering trades it for noise, which the eye tolerates better.

> **Noise and aliasing are the same problem sampled differently.** Regular sampling produces structured error (aliasing — visually objectionable because the eye finds patterns). Random sampling produces unstructured error (noise — less objectionable). **Stratified and blue-noise sampling deliberately sit between them**, which is why blue-noise dithering looks so much better than white noise at the same error level.

## Where graphics connects

**The reason this domain earns its place here, given it's the furthest from what you build:**

**GPU programming.** Graphics *is* why GPUs exist, and the [[foundations/gpu-and-parallel-computing/README|compute model]] is the graphics model generalised. Understanding the pipeline explains why GPUs are shaped the way they are.

**Linear algebra and transforms.** The [[robotics/04-rigid-body-transforms|same homogeneous transforms]] as robotics — same matrices, different application. Learning one gives you the other.

**Numerical methods.** Monte Carlo integration, interpolation, splines and ODE integration for physics. → [[foundations/numerical-methods/README|Numerical Methods]]

**Signal processing.** Sampling, filtering, aliasing, reconstruction.

**Simulation and robotics.** Physics engines, collision detection, and rendering for [[robotics/README|robot simulators]] — MuJoCo, Isaac Sim and Gazebo all need this.

**Machine learning.** Differentiable rendering, NeRFs and Gaussian splatting are graphics and ML fused, and the rendering equation is what they're learning to invert.

## Reading order

**02–06 are the rasterisation pipeline** and build in order — transforms, rasterising, shading, texturing, then how the GPU runs it.

**07 is ray tracing** and can be read independently.

**08–09 are geometry and animation.**

**Prerequisites:** [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|linear algebra]] — vectors, matrices, dot and cross products — is essential. Trigonometry. **[[robotics/04-rigid-body-transforms|Rigid body transforms]] covers most of note 02 already** if you've read it.

---

## Related
- [[foundations/computer-graphics/02-the-transform-pipeline|The Transform Pipeline]] — getting from 3D to 2D
- [[foundations/computer-graphics/07-ray-tracing-and-path-tracing|Ray Tracing and Path Tracing]] — the other paradigm
- [[foundations/gpu-and-parallel-computing/README|GPU and Parallel Computing]] — the hardware this drove
- [[foundations/computer-graphics/README|Computer graphics map]]
