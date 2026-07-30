# Performance and Gotchas

## Manual memory management: `dispose()`

Unlike DOM elements, three.js objects (geometries, materials, textures) allocate GPU memory that JavaScript's garbage collector **cannot reclaim automatically** — removing a mesh from the scene doesn't free the GPU buffers it used. Each must be disposed explicitly:

```js
scene.remove(mesh);
mesh.geometry.dispose();
mesh.material.dispose();
if (mesh.material.map) mesh.material.map.dispose(); // textures too
```

**Why this is necessary at all**: geometries/materials/textures are uploaded to the GPU as buffers outside the reach of JS's garbage collector, which only tracks JS heap memory. Forgetting to dispose creates a real memory leak that accumulates every time objects are created and removed — a common cause of a three.js app that "gets slower the longer it runs" or eventually crashes the tab, especially in single-page apps where scenes are frequently rebuilt (e.g. navigating between routes). [[07-react-three-fiber|React Three Fiber]] mitigates this by disposing automatically on unmount for anything it created.

## Draw calls: batch, don't duplicate

Every distinct mesh with its own geometry/material combination is (roughly) a separate draw call — an instruction sent to the GPU. Many draw calls, even of simple geometry, cost more than fewer draw calls of more complex geometry, because of the CPU-side overhead of issuing each one.

```js
// Expensive: 1000 draw calls
for (let i = 0; i < 1000; i++) {
  scene.add(new THREE.Mesh(geometry, material));
}

// Cheap: 1 draw call for all 1000 instances
const instancedMesh = new THREE.InstancedMesh(geometry, material, 1000);
const matrix = new THREE.Matrix4();
for (let i = 0; i < 1000; i++) {
  matrix.setPosition(Math.random() * 10, Math.random() * 10, Math.random() * 10);
  instancedMesh.setMatrixAt(i, matrix);
}
scene.add(instancedMesh);
```

`InstancedMesh` renders many copies of the *same* geometry/material with per-instance transforms in a single draw call — the standard fix once a scene has hundreds/thousands of visually-identical objects (particle effects, foliage, crowds), covered briefly in [[02-geometries-materials-meshes|geometries, materials, and meshes]].

## Polygon count and LOD

High-`segments` geometry (see [[02-geometries-materials-meshes|geometries, materials, and meshes]]) looks better up close but costs more to render regardless of how close the camera actually is. **Level of Detail (LOD)** swaps between a high-detail and low-detail version of the same object based on camera distance:

```js
import { LOD } from "three";

const lod = new LOD();
lod.addLevel(highDetailMesh, 0);   // used when camera is within 0 units
lod.addLevel(medDetailMesh, 10);    // used from 10 units away
lod.addLevel(lowDetailMesh, 50);     // used from 50 units away
scene.add(lod);
```

## Texture size and memory

Large texture images (4K+) consume significant GPU memory and bandwidth, especially with multiple maps (`map`, `normalMap`, `roughnessMap`, etc. — see [[05-textures|textures]]) all loaded per material. Texture dimensions that are powers of two (512, 1024, 2048...) are historically the safest/most compatible choice, and resizing source images to only as large as they'll actually appear on screen is a straightforward, high-impact optimization most projects skip until it becomes a visible problem.

## Shadow cost (cross-reference)

Covered in [[03-lighting-and-shadows|lighting and shadows]], but worth repeating here as a performance line item: every shadow-casting light adds a full extra render pass, and `PointLight` shadows specifically render six times per frame (once per cube face) — budget shadow-casting lights carefully in performance-sensitive scenes rather than enabling `castShadow` by default on every light.

## Profiling: don't guess

Before optimizing, check what's actually slow — `renderer.info` exposes real counts (draw calls, triangles, geometries, textures currently in memory):

```js
console.log(renderer.info.render.calls);     // draw calls this frame
console.log(renderer.info.render.triangles); // triangles rendered this frame
console.log(renderer.info.memory.geometries); // geometries currently tracked
console.log(renderer.info.memory.textures);    // textures currently tracked
```

A steadily climbing `memory.geometries`/`memory.textures` count over time, with no corresponding growth in visible scene complexity, is the clearest sign of a disposal leak described above.

## Related
- [[02-geometries-materials-meshes|geometries, materials, and meshes]] — `InstancedMesh`, segment counts
- [[03-lighting-and-shadows|lighting and shadows]] — shadow map cost
- [[07-react-three-fiber|React Three Fiber]] — automatic disposal on unmount
