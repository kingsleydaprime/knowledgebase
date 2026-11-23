---
id: 4a997da2-54e7-4640-bac4-e68b7fe66773
---

# How Rendering Works

Rendering is turning a description of a 3D scene into a 2D picture.

## What rendering is
<!-- bite: ea3023a6-63f4-4915-8bfa-aa978f8e81fd -->

**Given a description of a 3D scene, produce a 2D image.**

**The scene:** geometry (triangles, usually), materials, lights, and a camera.

**The image:** a grid of pixels, each with a colour.

**Two fundamentally different ways to bridge that gap**, and the difference is which direction you iterate.

## Rasterisation — loop over geometry
<!-- bite: 5dbac92a-a26c-4872-b73f-59bb623dd4d3 -->

```text
for each triangle:
    project to screen space
    for each pixel it covers:
        compute colour, keep if nearest
```

**Object-order.** You ask "where does this triangle land?"

**The killer property: it's embarrassingly parallel over triangles and pixels, and it never needs the whole scene at once** — stream triangles through, and each is independent.

**Which is why it's what GPUs were built for.** The entire fixed-function graphics pipeline is a rasteriser in silicon. → [[computer-graphics/11-rasterisation|Rasterisation]]

**What it's bad at:** anything requiring a triangle to know about *other* triangles. **Shadows, reflections, refraction and indirect light are all global effects, and rasterisation is fundamentally local.** Every real-time technique for those is an approximation bolted on — shadow maps, environment maps, screen-space reflections.

## Ray tracing — loop over pixels
<!-- bite: b34416e5-8364-406b-ab77-87a902a95fda -->

```text
for each pixel:
    cast a ray from the camera
    find the nearest intersection
    compute colour (possibly casting more rays)
```

**Image-order.** You ask "what does this pixel see?"

**The killer property: global effects are natural.** A reflection is just another ray. A shadow is a ray toward the light. Refraction, depth of field and motion blur all fall out of casting the right rays.

## What ray tracing is bad at
<!-- bite: a99b894e-52b5-4d83-bb81-93a689e9b17e -->

**What it's bad at:** you need the whole scene queryable at once, and naive intersection is $O(\text{triangles})$ per ray. **Acceleration structures (BVH) fix the complexity; the memory requirement is inherent.** → [[computer-graphics/15-ray-tracing-and-path-tracing|Ray Tracing]]

> **The honest summary:** rasterisation is fast and local; ray tracing is slow and global. **Real-time rendering spent thirty years finding clever approximations of global effects within a local framework** — and hardware ray tracing (2018 onwards) is the beginning of that pressure easing.
>
> **Modern engines are hybrid:** rasterise primary visibility (fast, and every pixel needs it), ray-trace the effects that need global information.

## The rendering equation
<!-- bite: 8c9bd3f2-fad0-425e-9ff7-e9b5580a4700 -->

**What both approaches are approximating.** Kajiya, 1986:

$$L_o(\mathbf{x}, \omega_o) = L_e(\mathbf{x},\omega_o) + \int_\Omega f_r(\mathbf{x}, \omega_i, \omega_o)\,L_i(\mathbf{x},\omega_i)\,(\omega_i\cdot\mathbf{n})\,d\omega_i$$

**In words: light leaving a point in a direction = light it emits + all incoming light, weighted by how the surface reflects it and by the angle.**

| Term | Meaning |
|---|---|
| $L_o$ | outgoing radiance — **what you want** |
| $L_e$ | emitted (only for light sources) |
| $f_r$ | **BRDF** — how the material reflects → [[computer-graphics/12-shading-and-lighting\|Shading]] |
| $L_i$ | incoming radiance **from everywhere** |
| $(\omega_i\cdot\mathbf{n})$ | Lambert's cosine — glancing light contributes less |

## Why the rendering equation is hard
<!-- bite: 2c4f82e3-d540-4686-b73c-fb1cf3a117bf -->

> **The difficulty is that $L_i$ depends on $L_o$ at every other surface.** It's a recursive integral equation over an infinite-dimensional space — **light bounces forever.**
>
> **Every rendering algorithm ever written is a way of approximating this integral.** Rasterised direct lighting truncates it at one bounce with no integral at all. Path tracing estimates it by Monte Carlo. **Knowing the equation tells you exactly what each technique is throwing away.**

**And note the integral is high-dimensional**, which is why Monte Carlo is the method of choice — quadrature dies above ~4 dimensions and Monte Carlo's error is dimension-independent. → [[mathematics/07-applied-and-computational/01-numerical-methods/07-numerical-integration/index|Monte Carlo]]

## The real-time pipeline
<!-- bite: 830ecbaa-9da9-4f32-a94e-7b16543b3a16 -->

**What happens for each frame at 60 Hz:**

```text
 scene data
     │
     ▼  VERTEX PROCESSING   transform to clip space
     ▼  CLIPPING & CULLING  discard what's invisible
     ▼  RASTERISATION       triangles → fragments
     ▼  FRAGMENT SHADING    compute colour per fragment
     ▼  OUTPUT MERGING      depth test, blending
  framebuffer
```

**Covered in detail across notes 10–14.** The structure to notice: **it's a stream, with each stage massively parallel and no stage needing global scene information.**

## Rendering as sampling
<!-- bite: a0ad3c98-8d95-4fb0-8c74-b76beadc7a14 -->

**A framing that unifies a surprising amount, and connects to [[information-theory/index|information theory]].**

**A pixel is not a point — it's an area.** Its correct colour is the *average* of the image over that area:

$$C_{\text{pixel}} = \int_{\text{pixel}} \text{image}(x,y)\,dx\,dy$$

**Rendering is estimating that integral by sampling.** And sampling theory then explains most visual artefacts:

**Aliasing** — sampling below the Nyquist rate. **Jagged edges, shimmering textures, moiré patterns.** Fixed by supersampling (more samples), mipmapping (pre-filtering), or reconstruction filters. → [[computer-graphics/13-textures-and-sampling|Textures and Sampling]]

## Rendering as sampling: noise and other artefacts
<!-- bite: d0b4372b-da2e-4089-a742-07772bc32847 -->

**Noise** — too few Monte Carlo samples. **Path tracing's grainy look**, and it decreases as $O(1/\sqrt{N})$, which is why film renders take hours.

**Banding** — quantisation error from too few bits per channel. Dithering trades it for noise, which the eye tolerates better.

> **Noise and aliasing are the same problem sampled differently.** Regular sampling produces structured error (aliasing — visually objectionable because the eye finds patterns). Random sampling produces unstructured error (noise — less objectionable). **Stratified and blue-noise sampling deliberately sit between them**, which is why blue-noise dithering looks so much better than white noise at the same error level.

## Where graphics connects
<!-- bite: 4d2d0f7c-1359-49b8-b730-ab9310d6f9cd -->

**The reason this domain earns its place here, given it's the furthest from what you build:**

**GPU programming.** Graphics *is* why GPUs exist, and the [[gpu-and-parallel-computing/index|compute model]] is the graphics model generalised. Understanding the pipeline explains why GPUs are shaped the way they are.

**Linear algebra and transforms.** The [[robotics/04-rigid-body-transforms|same homogeneous transforms]] as robotics — same matrices, different application. Learning one gives you the other.

**Numerical methods.** Monte Carlo integration, interpolation, splines and ODE integration for physics. → [[mathematics/07-applied-and-computational/01-numerical-methods/index|Numerical Methods]]

**Signal processing.** Sampling, filtering, aliasing, reconstruction.

**Simulation and robotics.** Physics engines, collision detection, and rendering for [[robotics/index|robot simulators]] — MuJoCo, Isaac Sim and Gazebo all need this.

**Machine learning.** Differentiable rendering, NeRFs and Gaussian splatting are graphics and ML fused, and the rendering equation is what they're learning to invert.

## Reading order
<!-- bite: 6b07eca1-e822-4753-b861-5007f7d1ce91 -->

This note opens Part 2. It assumes Part 1 (notes 01–08): how a screen shows pixels, drawing lines and shapes, and moving shapes with matrices. If those are new, start at [[computer-graphics/01-introduction-to-computer-graphics|note 01]].

**09–13 are the steps a graphics card goes through** and build in order: placing objects, filling in triangles, lighting, textures, then how the card is programmed.

**14 is ray tracing** and can be read on its own.

**15–16 are shapes and movement.**

**Prerequisites:** [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/index|linear algebra]] — vectors, matrices, dot and cross products — is essential. Trigonometry. **[[robotics/04-rigid-body-transforms|Rigid body transforms]] covers most of note 10 already** if you've read it.

## Check your understanding
<!-- bite: a83597b1-22fe-4fef-b2dc-becdde06d6c5 -->

Try each one before you open the answer.

1. <!-- q: mcq id="456c9582" -->
   Which approach asks "what does this pixel see?"

   - [ ] Rasterisation
   - [x] Ray tracing

   <details><summary>Answer</summary>

   Ray tracing, which is image-order. Rasterisation is object-order: it asks "where does this triangle land?"

   </details>

2. <!-- q: mcq id="83a2b44c" -->
   Which effects are hard for rasterisation because they are global? Choose all that apply.

   - [x] Shadows
   - [x] Reflections
   - [x] Indirect light
   - [ ] Filling a triangle's pixels

   <details><summary>Answer</summary>

   Shadows, reflections, refraction and indirect light need a triangle to know about other triangles. Rasterisation is local, so every real-time technique for them is an approximation.

   </details>

3. <!-- q: gap id="f93dba5a" answers="emits|emitted;reflects|reflected" -->
   Fill in the gaps. The rendering equation says: light leaving a point = light it ___ + all incoming light, weighted by how the surface ___ it and by the angle.

   <details><summary>Answer</summary>

   Emits, then reflects. It is hard because the incoming light depends on light leaving every other surface: light bounces forever.

   </details>

4. <!-- q: exact id="63bd397e" answer="4" accept="four|4x|4 times" -->
   Path tracing noise falls as 1/√N. How many times more samples do you need to halve the noise?

   <details><summary>Answer</summary>

   4 times. Halving 1/√N needs √N to double, so N must be 4 times bigger. That is why film renders take hours.

   </details>

5. <!-- q: mcq id="e218c29f" -->
   How do modern game engines combine the two approaches?

   - [x] Rasterise primary visibility, and ray-trace the effects that need global information
   - [ ] Ray-trace everything
   - [ ] Rasterise everything and never ray-trace

   <details><summary>Answer</summary>

   They are hybrid. Every pixel needs primary visibility, so rasterise that fast, then ray-trace reflections, shadows and similar effects.

   </details>

6. <!-- q: open id="12ec7035" -->
   "Noise and aliasing are the same problem sampled differently." What does that mean?

   <details><summary>Answer</summary>

   Both are errors from too few samples. Regular sampling gives structured error (aliasing), which the eye notices as patterns. Random sampling gives unstructured error (noise), which the eye tolerates better.

   </details>

---

## Related
<!-- bite: 78ae90c2-e9ab-4340-ae5d-793b53580272 -->
- [[computer-graphics/10-the-transform-pipeline|The Transform Pipeline]] — getting from 3D to 2D
- [[computer-graphics/15-ray-tracing-and-path-tracing|Ray Tracing and Path Tracing]] — the other paradigm
- [[gpu-and-parallel-computing/index|GPU and Parallel Computing]] — the hardware this drove
- [[computer-graphics/index|Computer graphics map]]

## About this lesson
<!-- bite: c1f619a4-8a5f-44ae-b4c3-d46c24e81bb8 -->

**Level:** Intermediate. **Covers:** The two paradigms, why one won for real-time and the other for film, and what they're both approximating.

**Source:** `[reference]` — see [[computer-graphics/index|the domain note]].
