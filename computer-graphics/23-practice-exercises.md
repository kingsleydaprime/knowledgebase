---
id: 2dd72d46-cd09-4aa3-8146-80bce93c1b50
---

# Practice Exercises

These exercises turn the graphics notes into pictures you make yourself.

## What these exercises are
<!-- bite: 5e0f88ff-30a6-44df-962a-529593636a1d -->

Graphics is the subject where you can see whether you are right. That's its advantage over every other course in this vault: a wrong matrix produces a visibly wrong picture, and a wrong shading model looks like plastic. **The feedback is immediate and unambiguous.**

**Two routes, and both are fine:**
- **[Shadertoy](https://www.shadertoy.com)** — a fragment shader in a browser, zero setup. Best for 1, 4–7
- **A CPU renderer in any language** writing a PPM/PNG file. Best for 2–3, 8–10. **No graphics API, no drivers, no build system** — just arithmetic and a file

Solutions in [[computer-graphics/24-practice-exercises-solutions|note 24]].

Next: Part A, the pipeline.

## Part A — The pipeline (notes 15–16)
<!-- bite: 27702db1-440b-4db4-9293-dd16b8897a87 -->

**1. Colour by normal.**
Render a sphere and set the pixel colour to `normal * 0.5 + 0.5`.
**Done when:** you get the classic pastel ball, and can say why the transform is needed — **and this is the single best first graphics exercise there is**, because a wrong normal is instantly visible → [[computer-graphics/17-shading-and-lighting|note 17]].

**2. Build the transform chain by hand.**
Implement model → world → view → projection → NDC → screen for a cube. No library.
**Done when:** the cube renders in perspective, and you can state what each matrix does **and what happens if you swap two of them** → [[computer-graphics/15-the-transform-pipeline|note 15]].

## Part A, continued: exercises 3–4
<!-- bite: 45788301-3140-431c-9bd9-92c8745093df -->

**3. Rasterise a triangle.**
Implement the edge-function test and barycentric interpolation. Fill a triangle with vertex colours interpolated across it.
**Done when:** the gradient is smooth, adjacent triangles share edges with **no gaps and no double-drawn pixels** — the fill rule is the fiddly bit → [[computer-graphics/16-rasterisation|note 16]].

**4. Break perspective-correct interpolation.**
Texture a large quad interpolating UVs *linearly in screen space*, then correctly (interpolate $u/w$, $v/w$, $1/w$).
**Done when:** the naive version shows the characteristic warped seam and the correct one doesn't. **This is why PS1 games look the way they do.**

---

## Part B — Shading (notes 17–18)
<!-- bite: f3a72cdc-0d3b-4256-aa76-ded86013578c -->

**5. Build up a lighting model.**
Start with flat colour, add Lambert diffuse, add Blinn–Phong specular, add ambient. Render each stage.
**Done when:** you have four images and can attribute each visual change to its term → [[computer-graphics/17-shading-and-lighting|note 17]].

**6. Make it physically based.**
Replace Blinn–Phong with a GGX/Cook–Torrance BRDF. Render a grid varying roughness and metalness.
**Done when:** the grid looks like the material charts in every PBR guide, and you can say what energy conservation buys you.

## Part B, continued: exercises 7–8
<!-- bite: be5b64b8-8997-452a-9fca-2f97089ac86c -->

**7. Alias, then fix it.**
Render a checkerboard receding to the horizon with point sampling. Then add mipmapping, then anisotropic filtering.
**Done when:** you've seen the shimmer, and can explain it as **undersampling a signal above the Nyquist limit** → [[computer-graphics/18-textures-and-sampling|note 18]] · [[information-theory/index|information theory]].

**8. Gamma.**
Render a gradient and a lighting calculation without gamma correction, then with. Average two colours in sRGB space, then in linear space.
**Done when:** you can show that averaging in the wrong space gives a visibly wrong midpoint — **and you know which of your favourite images are wrong because of this.**

---

## Part C — Ray tracing and geometry (notes 20–21)
<!-- bite: 4c42406a-f9fd-4f7c-b298-3260b10172a0 -->

**9. Write a ray tracer in a weekend.**
Follow Shirley's *Ray Tracing in One Weekend*: spheres, diffuse, metal, dielectric, defocus blur.
**Done when:** you have the cover image. **This is the highest-value single exercise in the course** — the rendering equation stops being notation.

**10. Add one bounce, then many.**
Render your scene at 1, 2, 4, 16 bounces, and at 1, 10, 100, 1000 samples per pixel.
**Done when:** you can point at **colour bleeding** that appears only with multiple bounces, and explain why noise falls as $1/\sqrt{N}$ rather than $1/N$ → [[computer-graphics/20-ray-tracing-and-path-tracing|note 20]].

## Part C, continued: exercises 11–12
<!-- bite: 3baf2e2e-8d6e-49d2-9a3f-a17fd6808681 -->

**11. Make it fast with a BVH.**
Add a bounding volume hierarchy. Time before and after on a scene of 500+ spheres.
**Done when:** you have the ratio and can state the complexity change from $O(n)$ per ray → [[dsa/index|DSA]].

**12. Mesh normals.**
Load an OBJ, compute face normals, then smooth vertex normals by averaging. Render both.
**Done when:** you can see faceting versus smooth shading, and can explain why a cube should **not** have smoothed normals → [[computer-graphics/21-geometry-and-meshes|note 21]].

## Part D — Classical raster graphics (notes 01–13)
<!-- bite: 07f9400c-e2d0-49e2-8eab-b06342df503e -->

**The SSG 511 exam and assignment questions are the practice set for Part 1** — Bresenham tables, Cohen–Sutherland clipping, transforming shapes, Bézier control points and de Casteljau splits. They are in the [[computer-graphics/25-ssg-511-question-bank|question bank]], deliberately unsolved; each teaching note ends with its own independent task, and the runnable scripts in notes 03, 06, 10 and 12 check your hand work.

## Related
<!-- bite: 3b4fc421-c9ab-4375-8ba3-8eb10ec5d19c -->
- [[computer-graphics/24-practice-exercises-solutions|Solutions]]
- [[computer-graphics/25-ssg-511-question-bank|SSG 511 question bank]]
- [[computer-graphics/index|the course]]
- [[game-development/03-graphics-for-games|graphics for games]] — the same material under a frame budget

## About this lesson
<!-- bite: f2754ed1-1b95-4f67-829e-cbeeac027c07 -->

**Level:** Intermediate → Advanced. **Covers:** Twelve exercises. **Graphics is the domain where you can see whether you understood it.**

*Source: [reference] — built from this course's own gap-closing list.*
