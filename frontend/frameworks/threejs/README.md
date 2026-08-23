# Three.js

**[Beginner → Advanced]** — a JavaScript 3D graphics library wrapping WebGL: scenes, cameras, lights, geometry, and materials rendered onto a canvas. A different domain from [[frontend/frameworks/gsap/README|GSAP]]/[[frontend/frameworks/framer-motion/README|Framer Motion]] (2D DOM/SVG animation) — this is real-time 3D rendering. Part of the [[frontend/README|frontend]] course.

## Structure

1. [[01-intro|01 — Intro]] — WebGL, the scene/camera/renderer trio, the right-handed coordinate system
2. [[02-geometries-materials-meshes|02 — Geometries, Materials, and Meshes]] — the Mesh = Geometry + Material split, PBR materials
3. [[03-lighting-and-shadows|03 — Lighting and Shadows]] — light types, why most materials need light, the three shadow flags
4. [[04-transformations-and-animation-loop|04 — Transformations and the Animation Loop]] — position/rotation/scale, `requestAnimationFrame`, `Clock`
5. [[05-textures|05 — Textures]] — TextureLoader, PBR texture maps, UV mapping, tiling
6. [[06-camera-controls-and-raycasting|06 — Camera Controls and Raycasting]] — OrbitControls, mouse-to-3D-object picking
7. [[07-react-three-fiber|07 — React Three Fiber]] — the declarative React renderer for three.js, `useFrame`, drei
8. [[08-performance-and-gotchas|08 — Performance and Gotchas]] — manual `dispose()`, draw calls, InstancedMesh, LOD

## Related
- [[frontend/README|frontend course map]]
- [[frontend/frameworks/gsap/README|GSAP]] / [[frontend/frameworks/framer-motion/README|Framer Motion]] — 2D animation libraries, different rendering model entirely
- [[frontend/README|frontend concepts]]
