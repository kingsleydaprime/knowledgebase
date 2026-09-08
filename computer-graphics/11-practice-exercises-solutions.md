# Practice Exercises — Solutions

> **[Intermediate → Advanced]** · Worked answers to [[foundations/computer-graphics/10-practice-exercises|note 10]].

**These are explanations, not code dumps** — graphics is a domain where the code is short and the *reason* is the hard part.

---

## Part A — The pipeline

### 1. Colour by normal

`normal * 0.5 + 0.5` maps the range $[-1,1]$ to $[0,1]$, because a normal is a unit vector with negative components and a colour channel cannot be negative.

**Why it's the best first exercise:** a wrong normal is *immediately visible*. Un-normalised normals give blown-out colour; normals in the wrong space rotate with the camera when they shouldn't; flipped winding turns the sphere inside out. **Every one of those bugs is diagnosable at a glance**, which is not true of any other debugging surface in this vault.

**Keep it as a debug view.** Rendering normals, UVs, depth or world position as colour is the standard graphics debugging technique.

### 2. The transform chain

$$\mathbf{v}_{clip} = P \cdot V \cdot M \cdot \mathbf{v}_{model}$$

- **Model** — object space → world. Where the object is
- **View** — world → camera space. Equivalent to moving the *world* by the camera's inverse
- **Projection** — camera → clip space. Applies perspective; sets $w$
- **Perspective divide** — $\div w$ → NDC. **This is where perspective actually happens**
- **Viewport** — NDC → pixels

**Order matters because matrix multiplication doesn't commute.** Swapping model and view renders as if the camera were the object. Swapping projection and view produces geometry that warps as you rotate.

**The perspective divide is the step people forget is separate.** The projection matrix only *arranges* for the divide by putting $z$ into $w$; the divide is done by the hardware afterwards. That's also why $w$ must be carried through interpolation → exercise 4 → [[foundations/computer-graphics/02-the-transform-pipeline|note 02]].

### 3. Rasterise a triangle

The edge function $E(a,b,p) = (p_x-a_x)(b_y-a_y) - (p_y-a_y)(b_x-a_x)$ is positive on one side of the edge. A pixel is inside when all three edge functions share a sign, and **the normalised edge values are the barycentric coordinates** — so the inside test and the interpolation weights come from the same arithmetic. That's the elegance of the method.

**The fiddly part is the fill rule.** A pixel centre landing exactly on a shared edge belongs to *exactly one* triangle. Without a rule (the standard is top-left), you get either **gaps** (both reject) or **double-drawn pixels** (both accept) — visible with transparency, and a correctness problem for stencil work.

### 4. Perspective-correct interpolation

Screen-space linear interpolation of UVs is **wrong** under perspective, because the perspective divide is non-linear: equal steps in screen space are *unequal* steps in world space.

Correct: interpolate $u/w$, $v/w$ and $1/w$ linearly, then recover $u = (u/w)/(1/w)$ per pixel.

**The PS1 had no per-pixel divide**, so it interpolated UVs affinely — producing the characteristic **wobbling, warping textures** on large polygons that define its look. Developers worked around it by subdividing geometry, which is why PS1 models have more triangles than they seem to need.

---

## Part B — Shading

### 5. Build up a lighting model

- **Flat** — a silhouette; no form
- **+ Lambert diffuse** ($\max(0, \mathbf{n}\cdot\mathbf{l})$) — **form appears.** The single biggest visual jump
- **+ Blinn–Phong specular** ($(\mathbf{n}\cdot\mathbf{h})^s$ with $\mathbf{h}$ the half-vector) — the highlight; the surface reads as a *material*
- **+ Ambient** — shadowed regions lift out of pure black

**Ambient is a confession, not a model.** It's a constant standing in for light bounced from everything else in the scene — the term global illumination and path tracing actually compute → exercise 10.

### 6. Physically based rendering

Cook–Torrance: $f_r = \frac{D\,F\,G}{4(\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v})}$ — $D$ the microfacet distribution (GGX), $F$ Fresnel (Schlick), $G$ geometric shadowing.

The roughness/metalness grid should look like every PBR chart: metals coloured by their *specular*, dielectrics with white highlights over a coloured base; rough surfaces with broad dim highlights, smooth ones with tight bright ones.

**Energy conservation is what buys you consistency.** A material cannot reflect more light than it receives, so a rougher surface *must* have a dimmer highlight — the total is redistributed, not increased. Blinn–Phong has no such constraint, so artists tuned each material per-light and it broke under new lighting.

**That's why PBR won: assets look right under any lighting**, which matters enormously for a production pipeline → [[game-development/03-graphics-for-games|graphics for games]].

### 7. Alias, then fix it

The receding checkerboard shimmers because at distance **many texels fall inside one pixel**, and point sampling picks one arbitrarily. Sub-pixel camera motion changes which — hence crawling.

**It is exactly undersampling.** The texture's spatial frequency exceeds the pixel grid's Nyquist limit, so high frequencies alias down into low-frequency patterns (moiré) → [[foundations/information-theory/README|information theory]].

**Mipmaps** pre-filter the texture into a chain of half-size levels; the hardware picks the level whose texel density ≈ pixel density. **You cannot fix aliasing by sampling harder at render time — you must remove the frequencies first**, which is what pre-filtering does.

**Anisotropic filtering** handles the surface being at a grazing angle, where the pixel's footprint is a long thin ellipse: isotropic mipmapping must choose a level for the *longer* axis and over-blurs the other. Anisotropic takes several samples along the ellipse — which is why it's the setting that makes ground textures crisp.

### 8. Gamma

Displays are non-linear (≈ $2.2$ exponent), and sRGB images are stored **pre-compensated**. So an sRGB value of 0.5 is *not* half the light.

**Averaging two sRGB values gives a midpoint that is too dark** — the classic case is a red/green gradient going through muddy brown instead of bright yellow.

**Correct: decode sRGB → linear, do all lighting maths in linear space, encode back for display.** Lighting is a physical process about *light quantities*; performing it on display-encoded values is arithmetic on the wrong numbers.

**A great deal of published imagery is wrong because of this**, and once you can see it you cannot stop. Modern engines handle it automatically via sRGB texture formats and framebuffers — which is precisely why those formats exist.

---

## Part C — Ray tracing and geometry

### 9. Ray tracer in a weekend

Shirley's book is the best learning resource in graphics: ~200 lines gets spheres, Lambertian, metal, dielectric, defocus blur and the cover image.

**Why it beats everything else here:** the rendering equation stops being notation. You *implement* "integrate incoming radiance over the hemisphere" as "fire a random ray and average", and the connection is undeniable.

**The dielectric is the one that teaches most** — Snell's law, total internal reflection, and the Schlick approximation, all visible in the glass ball.

### 10. Bounces and samples

**Bounces control light transport.** At 1 bounce, surfaces are lit directly and shadows are black. At 2+, **colour bleeding** appears — a red wall tints the white floor beside it. That's indirect illumination, and it's what "ambient" in exercise 5 was faking.

**Samples control noise.** Path tracing is Monte Carlo integration, so error falls as $O(1/\sqrt{N})$ — **not $1/N$.**

**The consequence is brutal and worth internalising: halving the noise costs 4× the samples.** 100 → 400 spp for one halving. This is why offline renders take hours, and why real-time ray tracing is *entirely* a denoising problem — you render at 1–2 spp and reconstruct → [[foundations/computer-graphics/07-ray-tracing-and-path-tracing|note 07]].

### 11. BVH

Without acceleration, each ray tests **every** object: $O(n)$ per ray. A BVH gives $O(\log n)$ by rejecting whole subtrees with one bounding-box test.

On 500 spheres expect **roughly 20–50×**; the gap widens with scene size, which is the point — it's a complexity change, not a constant factor.

**The same spatial-partitioning idea as [[game-development/03-graphics-for-games|game culling]] and collision broad-phase** — and the same trees as [[foundations/dsa/README|DSA]]. Build quality matters: the surface-area heuristic is the standard, and a naive median split is noticeably worse.

### 12. Mesh normals

**Face normals** → visible faceting; each triangle is uniformly lit.
**Smoothed vertex normals** (area- or angle-weighted average of adjacent faces) → smooth shading across the surface.

**A cube must not have smoothed normals.** Averaging across a 90° edge gives corner normals pointing diagonally, so the flat faces are shaded as if curved and the cube looks like a rounded blob.

**This is what "smoothing groups" / "hard edges" exist for**: an edge that should stay sharp needs *duplicated vertices* with different normals, because a vertex can carry only one normal. **That's why exported meshes often have more vertices than the model appears to have** — a cube needs 24, not 8 → [[foundations/computer-graphics/08-geometry-and-meshes|note 08]].

## Related
- [[foundations/computer-graphics/10-practice-exercises|the exercises]]
- [[foundations/computer-graphics/README|the course]]

*Source: [reference] — explanations from the course's primary sources; Shirley's *Ray Tracing in One Weekend* is the recommended companion.*
