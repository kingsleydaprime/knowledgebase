# Practice Exercises

> **[Intermediate → Advanced]** · Twelve exercises. **Graphics is the domain where you can see whether you understood it.**

That's its advantage over every other course in this vault: a wrong matrix produces a visibly wrong picture, and a wrong shading model looks like plastic. **The feedback is immediate and unambiguous.**

**Two routes, and both are fine:**
- **[Shadertoy](https://www.shadertoy.com)** — a fragment shader in a browser, zero setup. Best for 1, 4–7
- **A CPU renderer in any language** writing a PPM/PNG file. Best for 2–3, 8–10. **No graphics API, no drivers, no build system** — just arithmetic and a file

Solutions in [[foundations/computer-graphics/11-practice-exercises-solutions|note 11]].

---

## Part A — The pipeline (notes 02–03)

**1. Colour by normal.**
Render a sphere and set the pixel colour to `normal * 0.5 + 0.5`.
**Done when:** you get the classic pastel ball, and can say why the transform is needed — **and this is the single best first graphics exercise there is**, because a wrong normal is instantly visible → [[foundations/computer-graphics/04-shading-and-lighting|note 04]].

**2. Build the transform chain by hand.**
Implement model → world → view → projection → NDC → screen for a cube. No library.
**Done when:** the cube renders in perspective, and you can state what each matrix does **and what happens if you swap two of them** → [[foundations/computer-graphics/02-the-transform-pipeline|note 02]].

**3. Rasterise a triangle.**
Implement the edge-function test and barycentric interpolation. Fill a triangle with vertex colours interpolated across it.
**Done when:** the gradient is smooth, adjacent triangles share edges with **no gaps and no double-drawn pixels** — the fill rule is the fiddly bit → [[foundations/computer-graphics/03-rasterisation|note 03]].

**4. Break perspective-correct interpolation.**
Texture a large quad interpolating UVs *linearly in screen space*, then correctly (interpolate $u/w$, $v/w$, $1/w$).
**Done when:** the naive version shows the characteristic warped seam and the correct one doesn't. **This is why PS1 games look the way they do.**

---

## Part B — Shading (notes 04–05)

**5. Build up a lighting model.**
Start with flat colour, add Lambert diffuse, add Blinn–Phong specular, add ambient. Render each stage.
**Done when:** you have four images and can attribute each visual change to its term → [[foundations/computer-graphics/04-shading-and-lighting|note 04]].

**6. Make it physically based.**
Replace Blinn–Phong with a GGX/Cook–Torrance BRDF. Render a grid varying roughness and metalness.
**Done when:** the grid looks like the material charts in every PBR guide, and you can say what energy conservation buys you.

**7. Alias, then fix it.**
Render a checkerboard receding to the horizon with point sampling. Then add mipmapping, then anisotropic filtering.
**Done when:** you've seen the shimmer, and can explain it as **undersampling a signal above the Nyquist limit** → [[foundations/computer-graphics/05-textures-and-sampling|note 05]] · [[foundations/information-theory/README|information theory]].

**8. Gamma.**
Render a gradient and a lighting calculation without gamma correction, then with. Average two colours in sRGB space, then in linear space.
**Done when:** you can show that averaging in the wrong space gives a visibly wrong midpoint — **and you know which of your favourite images are wrong because of this.**

---

## Part C — Ray tracing and geometry (notes 07–08)

**9. Write a ray tracer in a weekend.**
Follow Shirley's *Ray Tracing in One Weekend*: spheres, diffuse, metal, dielectric, defocus blur.
**Done when:** you have the cover image. **This is the highest-value single exercise in the course** — the rendering equation stops being notation.

**10. Add one bounce, then many.**
Render your scene at 1, 2, 4, 16 bounces, and at 1, 10, 100, 1000 samples per pixel.
**Done when:** you can point at **colour bleeding** that appears only with multiple bounces, and explain why noise falls as $1/\sqrt{N}$ rather than $1/N$ → [[foundations/computer-graphics/07-ray-tracing-and-path-tracing|note 07]].

**11. Make it fast with a BVH.**
Add a bounding volume hierarchy. Time before and after on a scene of 500+ spheres.
**Done when:** you have the ratio and can state the complexity change from $O(n)$ per ray → [[foundations/dsa/README|DSA]].

**12. Mesh normals.**
Load an OBJ, compute face normals, then smooth vertex normals by averaging. Render both.
**Done when:** you can see faceting versus smooth shading, and can explain why a cube should **not** have smoothed normals → [[foundations/computer-graphics/08-geometry-and-meshes|note 08]].

## Related
- [[foundations/computer-graphics/11-practice-exercises-solutions|Solutions]]
- [[foundations/computer-graphics/README|the course]]
- [[game-development/03-graphics-for-games|graphics for games]] — the same material under a frame budget

*Source: [reference] — built from this course's own gap-closing list.*
