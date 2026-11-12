# Computer Graphics

Turning a 3D scene description into a 2D image. Rasterisation, shading, ray tracing, and the geometry and animation underneath — **plus, in Part 2, the classical raster algorithms a university course examines**: line and circle drawing, filling, clipping, transforms and curves by hand.

**~40,000 words across 21 notes** (including practice, solutions, a question bank and a formula sheet). Part 1 built August 2026; **Part 2 added November 2026 from the SSG 511 course notes**. `[reference]`.

> **The one idea:** every rendering algorithm is an approximation of the **rendering equation** — light leaving a point equals what it emits plus everything arriving, weighted by the material. **Rasterisation truncates it at one bounce; path tracing estimates it by Monte Carlo.** Knowing the equation tells you exactly what each technique is throwing away.

## An honest word on why this is here

**This was the weakest fit of the five domains in this batch, and it was chosen anyway.** Nothing else in the vault was waiting on it, unlike numerical methods (three domains asked) or GPU (98 ML notes needed it).

**What it does earn its place on:**

**It's where three other tracks meet concretely.** [[robotics/04-rigid-body-transforms|The transform maths]] is the same matrices as robotics. [[mathematics/07-applied-and-computational/01-numerical-methods/07-numerical-integration/index|Monte Carlo integration]] is the same as numerical methods. [[gpu-and-parallel-computing/index|The GPU]] exists because of this workload. **Graphics is the application that makes all three tangible at once.**

**It's the most visual subject in computing.** A bug you can *see* is a bug you can debug, which makes it unusually good for building intuition — and unusually motivating.

**And it feeds robotics simulation** — MuJoCo, Isaac Sim and Gazebo are rendering plus physics.

## Reading order

**Two parts.** **Part 1 (01–09) is the modern view** — the GPU pipeline, physically based shading, path tracing. **Part 2 (12–18) is classical raster graphics** — the by-hand algorithms underneath. **If pixels, Bresenham and homogeneous matrices are new, read Part 2 first (12 → 18), then Part 1.** If you are revising for SSG 511, Part 2 plus notes 19–21 is the whole exam.

### Part 1 — modern rendering

**02–06 are the rasterisation pipeline** and build strictly in order. **07 is ray tracing**, independent. **08–09 are geometry and motion.**

1. [[computer-graphics/01-how-rendering-works|How Rendering Works]] — **[Intermediate]** — rasterisation vs ray tracing, **the rendering equation**, and rendering as a sampling problem
2. [[computer-graphics/02-the-transform-pipeline|The Transform Pipeline]] — **[Intermediate]** — model→world→view→clip→screen, projection matrices, **why depth precision is non-uniform**, and the normal matrix
3. [[computer-graphics/03-rasterisation|Rasterisation]] — **[Intermediate → Advanced]** — edge functions, the z-buffer, **perspective-correct interpolation**, antialiasing, deferred shading
4. [[computer-graphics/04-shading-and-lighting|Shading and Lighting]] — **[Intermediate → Advanced]** — BRDFs, **physically based rendering**, image-based lighting, shadow mapping, and the gamma bug everyone hits
5. [[computer-graphics/05-textures-and-sampling|Textures and Sampling]] — **[Intermediate]** — UV mapping, **mipmaps as pre-filtering**, anisotropic filtering, compression, SDFs
6. [[computer-graphics/06-the-gpu-graphics-pipeline|The GPU Graphics Pipeline]] — **[Intermediate → Advanced]** — shader stages, compute shaders, the modern APIs, and **why to learn on WebGPU rather than Vulkan**
7. [[computer-graphics/07-ray-tracing-and-path-tracing|Ray Tracing and Path Tracing]] — **[Advanced]** — BVHs, Monte Carlo light transport, **next event estimation**, denoising, hardware RT
8. [[computer-graphics/08-geometry-and-meshes|Geometry and Meshes]] — **[Intermediate → Advanced]** — indexed meshes, half-edge, Béziers and NURBS, **SDFs where booleans are trivial**, LOD
9. [[computer-graphics/09-animation-and-simulation|Animation and Simulation]] — **[Intermediate → Advanced]** — SLERP, skinning, rigid body physics, collision detection, and **the sim-to-real gap**

### Part 2 — classical raster graphics (SSG 511)

**12–14 build in order** (hardware → lines → circles and fills). **15–18 can be read in any order after 13**, though 15's Bézier clipping uses 17.

12. [[computer-graphics/12-graphics-systems-and-display-hardware|Graphics Systems and Display Hardware]] — **[Beginner → Intermediate]** — visual problem solving, interactive computing, the GUI, **CRT, raster versus random scan**, frame-buffer sums, refresh rate, double buffering, bitmap versus vector
13. [[computer-graphics/13-line-drawing-and-antialiasing|Line Drawing and Antialiasing]] — **[Intermediate]** — DDA, **Bresenham derived for both slopes**, midpoint lines, worked tables, an integer-only program, shapes and dashed lines, four antialiasing methods
14. [[computer-graphics/14-circles-and-polygon-filling|Circles and Polygon Filling]] — **[Intermediate]** — eight-way symmetry, **midpoint and Bresenham circles**, ellipses, scan-line fill with edge tables, flood and boundary fill, **4- versus 8-connected leaking**
15. [[computer-graphics/15-clipping|Clipping]] — **[Intermediate]** — region codes, **Cohen–Sutherland**, midpoint subdivision, Cyrus–Beck, **Liang–Barsky as a check**, 3D frustum and Bézier clipping
16. [[computer-graphics/16-2d-and-3d-transformations|2D and 3D Transformations]] — **[Intermediate]** — homogeneous matrices, **reading a matrix by its pattern**, row versus column vectors, the pivot check, the four blocks of a 4 × 4, the cone method
17. [[computer-graphics/17-curves-bezier-and-b-splines|Curves: Bézier and B-splines]] — **[Intermediate → Advanced]** — where the Bernstein weights come from, **control points from velocities**, de Casteljau and splitting, Cox–de Boor, Chaikin, flattening to a tolerance
18. [[computer-graphics/18-visible-surface-detection|Visible Surface Detection]] — **[Intermediate]** — object versus image space, **the depth buffer by hand**, back-face detection, painter's, BSP trees, scan-line, Warnock, ray casting

**Exam support:**

19. [[computer-graphics/19-ssg-511-question-bank|SSG 511 Question Bank]] — the exam paper and every assignment question, **unsolved on purpose**, each pointing to its note, with an exam-coverage table and a study order
20. [[computer-graphics/20-comsol-ink-jet-breakup|COMSOL: Modelling Ink Jet Breakup]] — **[Advanced]** — the model answer to exam Q3 (fluid dynamics, not graphics — and skippable)
21. [[computer-graphics/21-ssg-511-formula-sheet|SSG 511 Formula Sheet]] — every Part 2 formula on one page

## The things worth carrying

1. **Rasterisation is fast and local; ray tracing is slow and global.** Every real-time global effect is an approximation working around that → [[computer-graphics/01-how-rendering-works|01]]
2. **The perspective divide is why homogeneous coordinates exist** — a matrix can't divide, but it can set up a division → [[computer-graphics/02-the-transform-pipeline|02]]
3. **Z-fighting is fixed by pushing the *near* plane out**, not the far plane. Precision goes as $n/z^2$ → [[computer-graphics/02-the-transform-pipeline|02]]
4. **Interpolate attribute/$w$ and $1/w$, then divide.** Skipping it gives you PlayStation-1 texture warping → [[computer-graphics/03-rasterisation|03]]
5. **The z-buffer won because it needs no sorting** — and transparency, which does, has been awkward ever since → [[computer-graphics/03-rasterisation|03]]
6. **Do all lighting maths in linear space.** The gamma bug is extremely common and looks like "too dark, blown highlights" → [[computer-graphics/04-shading-and-lighting|04]]
7. **PBR's real win is decoupling material from lighting** — author once, correct everywhere → [[computer-graphics/04-shading-and-lighting|04]]
8. **Mipmapping usually makes rendering *faster* as well as better** — better cache behaviour on distant surfaces → [[computer-graphics/05-textures-and-sampling|05]]
9. **Reduce the resolution: if the frame rate doesn't change, you're CPU-bound.** A ten-second test that saves days → [[computer-graphics/06-the-gpu-graphics-pipeline|06]]
10. **Next event estimation is not optional in a path tracer.** Without it, small lights are never found → [[computer-graphics/07-ray-tracing-and-path-tracing|07]]
11. **Never interpolate Euler angles or rotation matrices. SLERP, and check the sign first** → [[computer-graphics/09-animation-and-simulation|09]]
12. **Fix your timestep**, and use semi-implicit Euler or Verlet — never explicit Euler → [[computer-graphics/09-animation-and-simulation|09]]
13. **Bresenham is "which of two pixels is closer?", answered with integers.** Multiply the distance difference by $dx$ to clear the fraction, and the sign is all you need → [[computer-graphics/13-line-drawing-and-antialiasing|13]]
14. **Step the long axis.** For $|m| > 1$, step $y$ and swap every $x$ and $y$ in the derivation; $p_0 = 2dx - dy$ → [[computer-graphics/13-line-drawing-and-antialiasing|13]]
15. **AND = 0000 means *maybe* visible, not visible.** Clip and recompute the code until accept or reject → [[computer-graphics/15-clipping|15]]
16. **Homogeneous coordinates exist because translation isn't a 2 × 2 multiplication.** Then state your vector convention, and check the pivot lands where it should → [[computer-graphics/16-2d-and-3d-transformations|16]]
17. **$P_1 = P_0 + v_0/3$, $P_2 = P_3 - v_1/3$** — and the left edge of the de Casteljau triangle is the first half → [[computer-graphics/17-curves-bezier-and-b-splines|17]]

## Where this connects

| | |
|---|---|
| [[gpu-and-parallel-computing/index\|GPU and parallel]] | **This workload is why GPUs exist** |
| [[robotics/04-rigid-body-transforms\|robotics]] | Identical transform maths; and robot simulators are rendering + physics |
| [[mathematics/07-applied-and-computational/01-numerical-methods/07-numerical-integration/index\|numerical methods]] | Monte Carlo, splines, ODE integrators |
| [[information-theory/01-what-information-is\|information theory]] | Sampling, aliasing, band-limiting |
| [[continuum-mechanics/index\|continuum mechanics]] | Cloth, soft bodies and fluids are the same equations |
| [[ai-ml/02-ml-engineer/06-computer-vision/index\|computer vision]] | The inverse problem — image to scene |

## The honest note

**`[reference]`, and this domain has the best reps-to-effort ratio in the entire vault** — because **you can see whether it's working.**

Unlike a numerical method that returns a plausible wrong number, **a broken renderer looks broken.** That makes it unusually good for learning, and it means the gap here is genuinely cheap to close.

**What would close it, in order:**

1. **[*Ray Tracing in One Weekend*](https://raytracing.github.io).** Free, genuinely a weekend, and you finish with a real rendered image. **The single best entry point in graphics** — no API, no build system, just a program that writes a PPM file
2. **Then [*Ray Tracing: The Next Week*](https://raytracing.github.io)** for BVHs, textures and motion blur
3. **[LearnOpenGL](https://learnopengl.com)** for the rasterisation pipeline — transforms, shaders, lighting, shadow maps. **Excellent and free**
4. **Write a software rasteriser.** No GPU, no API — edge functions, a z-buffer, perspective-correct interpolation. **A few hundred lines, and note 03 becomes permanent**
5. **Deliberately reproduce the classic bugs:** skip perspective correction and watch textures warp; treat sRGB as linear and watch it go dark; set the near plane to 0.001 and watch z-fighting. **Seeing each failure is worth more than reading about it**
6. **[Shadertoy](https://shadertoy.com)** for SDFs and ray marching — a whole scene in one fragment shader, with instant feedback
7. **The books:** *Real-Time Rendering* (Akenine-Möller et al.) — the standard reference; ***Physically Based Rendering*** (Pharr, Jakob, Humphreys) — **free online, a literate program, and the best book in the field**; *Fundamentals of Computer Graphics* (Marschner & Shirley) for the basics

**What's missing:** ~~exercises~~ — **closed by notes 10–11 (Aug 2026)**; ~~the classical 2D raster algorithms~~ — **closed by Part 2, notes 12–21 (Nov 2026)**; colour science in depth, volumetric rendering and participating media, subsurface scattering, procedural generation beyond noise, VR/AR specifics, video codecs, and vector rendering of fonts and paths (typography, GPU path rendering).

→ [[PRIMETECHIE|Reading is not a rank.]]

## Practice

- [[computer-graphics/10-practice-exercises|Practice Exercises]] — twelve exercises — colour-by-normal, the transform chain by hand, gamma, and a ray tracer in a weekend
- [[computer-graphics/11-practice-exercises-solutions|Solutions]] — worked answers, **after you've tried**
- [[computer-graphics/19-ssg-511-question-bank|SSG 511 question bank]] — Part 2's practice: the exam paper and assignments, unsolved, with runnable checkers in notes 13, 15 and 17

## Build it

- [[build-your-own-shit/22-your-own-ray-tracer|Your Own Ray Tracer]] — **[Intermediate]** — note 07 as running code, and the long version of exercise 10's weekend ray tracer: spheres, antialiasing, diffuse bounces, metal and glass, a movable camera, meshes and a BVH. **Soft shadows and colour bleeding arrive without you implementing either**, and the furnace test tells you whether your renderer conserves energy

## Related
- [[gpu-and-parallel-computing/index|GPU and Parallel Computing]] — the hardware this drove
- [[mathematics/07-applied-and-computational/01-numerical-methods/index|Numerical Methods]] — the maths underneath
- [[robotics/index|Robotics]] — shared transforms, and simulation
- [[BUILD-PLAN|Build Plan]]
