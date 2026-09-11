# Build Your Own Ray Tracer

> **[Intermediate]** · Spheres → materials → a camera → meshes → a BVH. **A weekend for the first image, and global illumination shows up without you writing it.**

## What you're building

**A path tracer** — a program that produces a photorealistic image by simulating light itself: firing rays through pixels into a scene, bouncing them off surfaces, and averaging what comes back. Soft shadows, reflections, refraction through glass and colour bleeding between surfaces all emerge from one recursive function.

**And what you're deliberately not:** real-time, GPU-accelerated, spectrally correct, or denoised. **Your renderer will take minutes per frame and that is fine** — it is how film rendering worked for two decades.

**This is the guide with the shortest distance to a result you want to look at.** `computer-graphics/` has eleven written notes and, until now, nothing to build.

## What you need first

- **What rendering is, and the two families of approach** → [[computer-graphics/01-how-rendering-works|how rendering works]]
- **Ray tracing and path tracing specifically** → [[computer-graphics/07-ray-tracing-and-path-tracing|ray tracing and path tracing]]
- **Vectors, dot and cross products** — the dot product is in almost every line of this project → [[mathematics/04-linear-algebra/02-vectors/01-vectors|vectors]]
- **Lines in 3D, and solving a quadratic** → [[mathematics/03-geometry-trigonometry/07-analytic-geometry-3d/01-lines-and-planes|lines and planes]]
- **Expectation and sampling**, because a path tracer is a Monte Carlo integrator → [[mathematics/05-probability-statistics/03-probability/01-probability|probability]]
- Helpful: [[computer-graphics/04-shading-and-lighting|shading and lighting]] for the physical model

**C++ and Rust are the usual choices** and the speed matters more here than in most guides — a scene is millions of rays. **Go is comfortable.** **Python is educational but painfully slow** unless you vectorise with NumPy, which changes the shape of the code considerably.

**Peter Shirley's *Ray Tracing in One Weekend* is the reference** — free online, and the title is honest.

## The build order

**1. Write an image file.**
PPM is a three-line ASCII header followed by RGB triples, so you need no library at all:
```
P3
400 225
255
255 0 0   ...
```
Output a gradient.
*Works when:* an image viewer opens it and the colours go the way you expect. **Set up a one-key rebuild-and-view loop now** — you will run it several hundred times.

**2. A vector type, and a ray.**
Three floats with the usual operators, doubling as points, directions and colours. A ray is $P(t) = A + tB$: an origin, a direction, and a parameter.
*Works when:* your camera fires one ray per pixel and colouring by ray direction reproduces the gradient.

**3. Ray–sphere intersection.**
Substitute the ray into the sphere equation and you get a quadratic in $t$. The discriminant tells you whether it hits; the smaller positive root is the near hit.
*Works when:* shading each hit by its surface normal gives you **the classic red-green-blue sphere**. It is the first image that looks like computer graphics, and it arrives about ninety minutes in.

**4. Antialiasing.**
Fire many rays per pixel with jittered offsets and average. Edges go from jagged to smooth for about five lines of code.
*Works when:* 100 samples per pixel produces clean edges and about a 100× slowdown. **That trade is the whole economics of this field.**

**5. Diffuse materials — and the moment the project justifies itself.**
When a ray hits a diffuse surface, bounce it in a random direction in the hemisphere and recurse, multiplying by the surface colour. Cap the recursion depth.

**Soft shadows, ambient occlusion and colour bleeding all appear immediately, and you did not implement any of them.** They were never features — they are what light does, and you are now simulating light.

Apply gamma correction, roughly a square root on the final colour, or everything looks far too dark.
*Works when:* a sphere on a plane casts a soft-edged shadow and picks up a tint from the surface beneath it.

**6. Metal and glass.**
Metal reflects: $\vec{r} = \vec{v} - 2(\vec{v} \cdot \vec{n})\vec{n}$, with a fuzz parameter that perturbs the reflected ray. Glass refracts by Snell's law, falls back to reflection under **total internal reflection**, and mixes the two by the **Schlick approximation** — which is why glass looks mirrored at a glancing angle and transparent head-on.
*Works when:* a glass sphere shows an inverted image through it, and a hollow one — a sphere with a smaller sphere of negative radius inside — looks like a soap bubble.

**7. A camera you can move.**
Position, look-at point, up vector, vertical field of view. Then defocus blur via a thin-lens model: originate rays from a disc rather than a point.
*Works when:* you can frame a shot, and a wide aperture puts the background out of focus.

**8. Light sources.**
Add an emissive material that returns colour without bouncing, and a lamp is simply a bright object. **A path tracer needs no special case for lights**, which is why the architecture is worth the noise.
*Works when:* a dark scene lit only by a glowing rectangle renders, grainily.

**9. Triangles and meshes.**
Möller–Trumbore intersection, then an OBJ loader. Now you can render models rather than spheres.
*Works when:* the Stanford bunny renders. **It will be unbearably slow**, which motivates the next step exactly as it should.

**10. A bounding volume hierarchy.**
Without acceleration, every ray tests every triangle — and a 100,000-triangle mesh at 1 million rays is 10¹¹ tests. Put objects in a tree of nested boxes and a ray discards half the scene per level, taking it from linear to logarithmic.
*Works when:* the bunny renders **a hundred times faster** and the image is pixel-identical to the slow version. That second condition is the test — a BVH bug looks like missing geometry, not like an error.

**11. Optional: threads, textures, noise.**
Rendering is embarrassingly parallel — one thread per row of pixels, with **its own random number generator**. Then image textures, Perlin noise, and motion blur, which is just randomising the ray's time.

## The parts that will bite you

**Shadow acne.** Rays bounce off a surface and immediately re-hit the same surface at $t = 10^{-9}$, producing black speckles everywhere. Ignore hits below `t_min = 0.001`. **Every renderer has this constant** and now you know why.

**Gamma.** Monitors are non-linear. Do all your arithmetic in linear space and convert only when writing the file. Skipping it makes images muddy in a way that is hard to name and impossible to unsee.

**Unnormalised normals.** Reflection and the dot product both assume unit length. A normal scaled by 1.7 gives a subtly wrong image — not obviously broken, just off — which is the worst kind of bug to hunt.

**Inside versus outside for dielectrics.** When a ray is *inside* glass the normal must be flipped and the refractive index ratio inverted. Getting this wrong yields glass that looks almost right, which costs more time than glass that looks clearly wrong.

**NaNs propagate silently.** One square root of a negative number turns a pixel black, then averages into its neighbours. Assert that colour components are finite while developing.

**Noise is the price of the architecture.** Halving the noise takes **four times** the samples — it falls as $1/\sqrt{N}$. This is not a bug to fix; it is the Monte Carlo convergence rate, and every technique in production rendering is an attempt to cheat it.

## How to know it works

1. **The furnace test.** Put a purely white diffuse object inside a uniformly white emissive environment. **A correct renderer makes the object invisible** — it reflects exactly as much as it receives. If it appears darker, you are losing energy; brighter, you are creating it. This is the sharpest correctness test in rendering and it takes ten minutes to set up
2. **A Cornell box** — the standard scene, and reference images are everywhere. Colour bleeding onto the white walls from the red and green ones is the thing to look for
3. **The BVH image is pixel-identical** to the brute-force one
4. **Doubling the samples reduces noise by $\sqrt{2}$**, measured rather than eyeballed
5. **Compare against the reference book's images** at each chapter's end

## Where to stop

**Stop after the BVH and a scene you are happy to look at.**

**Not worth it here:** spectral rendering, subsurface scattering, bidirectional path tracing, Metropolis light transport, or a GPU port. Each is a real technique and each is a separate project — and the GPU port in particular teaches you about GPUs, not about light → [[gpu-and-parallel-computing/index|GPU and parallel computing]].

**You will have learned** why offline rendering and real-time rendering are different disciplines rather than different budgets, why noise is the fundamental currency, and what a rendering equation is an equation *about*. **The [[computer-graphics/03-rasterisation|rasterisation]] note will read completely differently afterwards** — as the other answer to the same question, arrived at from the opposite direction.

## Related

- [[computer-graphics/07-ray-tracing-and-path-tracing|Ray tracing and path tracing]] — the reference note for this guide
- [[computer-graphics/index|computer-graphics/]] — the full course
- [[build-your-own-shit/12-your-own-physics-engine|Your Own Physics Engine]] — the other half of a renderer's world, and the same vector maths
- [[game-development/03-graphics-for-games|Graphics for games]] — where the real-time constraint changes every answer
- [[build-your-own-shit/index|Build Your Own Shit index]]

*Source: [reference] — build guide, Sep 2026.*
