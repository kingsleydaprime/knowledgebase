# Computer Graphics

Turning a 3D scene description into a 2D image. Rasterisation, shading, ray tracing, and the geometry and animation underneath.

**~14,100 words across 11 notes** (including practice + solutions). Built August 2026. `[reference]`.

> **The one idea:** every rendering algorithm is an approximation of the **rendering equation** — light leaving a point equals what it emits plus everything arriving, weighted by the material. **Rasterisation truncates it at one bounce; path tracing estimates it by Monte Carlo.** Knowing the equation tells you exactly what each technique is throwing away.

## An honest word on why this is here

**This was the weakest fit of the five domains in this batch, and it was chosen anyway.** Nothing else in the vault was waiting on it, unlike numerical methods (three domains asked) or GPU (98 ML notes needed it).

**What it does earn its place on:**

**It's where three other tracks meet concretely.** [[robotics/04-rigid-body-transforms|The transform maths]] is the same matrices as robotics. [[foundations/numerical-methods/07-numerical-integration|Monte Carlo integration]] is the same as numerical methods. [[foundations/gpu-and-parallel-computing/README|The GPU]] exists because of this workload. **Graphics is the application that makes all three tangible at once.**

**It's the most visual subject in computing.** A bug you can *see* is a bug you can debug, which makes it unusually good for building intuition — and unusually motivating.

**And it feeds robotics simulation** — MuJoCo, Isaac Sim and Gazebo are rendering plus physics.

## Reading order

**02–06 are the rasterisation pipeline** and build strictly in order. **07 is ray tracing**, independent. **08–09 are geometry and motion.**

1. [[foundations/computer-graphics/01-how-rendering-works|How Rendering Works]] — **[Intermediate]** — rasterisation vs ray tracing, **the rendering equation**, and rendering as a sampling problem
2. [[foundations/computer-graphics/02-the-transform-pipeline|The Transform Pipeline]] — **[Intermediate]** — model→world→view→clip→screen, projection matrices, **why depth precision is non-uniform**, and the normal matrix
3. [[foundations/computer-graphics/03-rasterisation|Rasterisation]] — **[Intermediate → Advanced]** — edge functions, the z-buffer, **perspective-correct interpolation**, antialiasing, deferred shading
4. [[foundations/computer-graphics/04-shading-and-lighting|Shading and Lighting]] — **[Intermediate → Advanced]** — BRDFs, **physically based rendering**, image-based lighting, shadow mapping, and the gamma bug everyone hits
5. [[foundations/computer-graphics/05-textures-and-sampling|Textures and Sampling]] — **[Intermediate]** — UV mapping, **mipmaps as pre-filtering**, anisotropic filtering, compression, SDFs
6. [[foundations/computer-graphics/06-the-gpu-graphics-pipeline|The GPU Graphics Pipeline]] — **[Intermediate → Advanced]** — shader stages, compute shaders, the modern APIs, and **why to learn on WebGPU rather than Vulkan**
7. [[foundations/computer-graphics/07-ray-tracing-and-path-tracing|Ray Tracing and Path Tracing]] — **[Advanced]** — BVHs, Monte Carlo light transport, **next event estimation**, denoising, hardware RT
8. [[foundations/computer-graphics/08-geometry-and-meshes|Geometry and Meshes]] — **[Intermediate → Advanced]** — indexed meshes, half-edge, Béziers and NURBS, **SDFs where booleans are trivial**, LOD
9. [[foundations/computer-graphics/09-animation-and-simulation|Animation and Simulation]] — **[Intermediate → Advanced]** — SLERP, skinning, rigid body physics, collision detection, and **the sim-to-real gap**

## The things worth carrying

1. **Rasterisation is fast and local; ray tracing is slow and global.** Every real-time global effect is an approximation working around that → [[foundations/computer-graphics/01-how-rendering-works|01]]
2. **The perspective divide is why homogeneous coordinates exist** — a matrix can't divide, but it can set up a division → [[foundations/computer-graphics/02-the-transform-pipeline|02]]
3. **Z-fighting is fixed by pushing the *near* plane out**, not the far plane. Precision goes as $n/z^2$ → [[foundations/computer-graphics/02-the-transform-pipeline|02]]
4. **Interpolate attribute/$w$ and $1/w$, then divide.** Skipping it gives you PlayStation-1 texture warping → [[foundations/computer-graphics/03-rasterisation|03]]
5. **The z-buffer won because it needs no sorting** — and transparency, which does, has been awkward ever since → [[foundations/computer-graphics/03-rasterisation|03]]
6. **Do all lighting maths in linear space.** The gamma bug is extremely common and looks like "too dark, blown highlights" → [[foundations/computer-graphics/04-shading-and-lighting|04]]
7. **PBR's real win is decoupling material from lighting** — author once, correct everywhere → [[foundations/computer-graphics/04-shading-and-lighting|04]]
8. **Mipmapping usually makes rendering *faster* as well as better** — better cache behaviour on distant surfaces → [[foundations/computer-graphics/05-textures-and-sampling|05]]
9. **Reduce the resolution: if the frame rate doesn't change, you're CPU-bound.** A ten-second test that saves days → [[foundations/computer-graphics/06-the-gpu-graphics-pipeline|06]]
10. **Next event estimation is not optional in a path tracer.** Without it, small lights are never found → [[foundations/computer-graphics/07-ray-tracing-and-path-tracing|07]]
11. **Never interpolate Euler angles or rotation matrices. SLERP, and check the sign first** → [[foundations/computer-graphics/09-animation-and-simulation|09]]
12. **Fix your timestep**, and use semi-implicit Euler or Verlet — never explicit Euler → [[foundations/computer-graphics/09-animation-and-simulation|09]]

## Where this connects

| | |
|---|---|
| [[foundations/gpu-and-parallel-computing/README\|GPU and parallel]] | **This workload is why GPUs exist** |
| [[robotics/04-rigid-body-transforms\|robotics]] | Identical transform maths; and robot simulators are rendering + physics |
| [[foundations/numerical-methods/07-numerical-integration\|numerical methods]] | Monte Carlo, splines, ODE integrators |
| [[foundations/information-theory/01-what-information-is\|information theory]] | Sampling, aliasing, band-limiting |
| [[engineering/01-continuum-mechanics/README\|continuum mechanics]] | Cloth, soft bodies and fluids are the same equations |
| [[ai-ml/02-ml-engineer/06-computer-vision/README\|computer vision]] | The inverse problem — image to scene |

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

**What's missing:** ~~exercises~~ — **closed by notes 10–11 (Aug 2026)**; colour science in depth, volumetric rendering and participating media, subsurface scattering, procedural generation beyond noise, VR/AR specifics, video codecs, and the whole 2D/vector graphics and typography side.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Practice

- [[foundations/computer-graphics/10-practice-exercises|Practice Exercises]] — twelve exercises — colour-by-normal, the transform chain by hand, gamma, and a ray tracer in a weekend
- [[foundations/computer-graphics/11-practice-exercises-solutions|Solutions]] — worked answers, **after you've tried**

## Related
- [[foundations/gpu-and-parallel-computing/README|GPU and Parallel Computing]] — the hardware this drove
- [[foundations/numerical-methods/README|Numerical Methods]] — the maths underneath
- [[robotics/README|Robotics]] — shared transforms, and simulation
- [[BUILD-PLAN|Build Plan]]
