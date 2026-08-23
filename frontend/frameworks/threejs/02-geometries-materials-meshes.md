# Geometries, Materials, and Meshes

A **`Mesh`** — the thing you actually see rendered — is always the combination of two separate objects: a **`Geometry`** (the shape — vertex positions) and a **`Material`** (how the surface responds to light/color). This separation is deliberate: the same geometry can be reused with different materials, and vice versa, without duplicating data.

```js
const geometry = new THREE.SphereGeometry(1, 32, 16); // radius, widthSegments, heightSegments
const material = new THREE.MeshStandardMaterial({ color: 0x4488ff });
const sphere = new THREE.Mesh(geometry, material);
scene.add(sphere);
```

## Common built-in geometries

```js
new THREE.BoxGeometry(width, height, depth);
new THREE.SphereGeometry(radius, widthSegments, heightSegments);
new THREE.PlaneGeometry(width, height);
new THREE.CylinderGeometry(radiusTop, radiusBottom, height, radialSegments);
new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments); // donut shape
```

`SphereGeometry`'s `widthSegments`/`heightSegments` (and similar `*Segments` params on other geometries) control how many flat polygons approximate the curved surface — more segments look smoother but cost more to render. This is a real performance/quality tradeoff, not just a visual nicety: a sphere with `128, 64` segments has roughly 16x the vertices of `32, 16`, all of which the GPU has to process every frame.

## Materials — the response to light is what differs

The material class determines whether/how the object is affected by scene lighting:

| Material | Lit? | Use for |
|---|---|---|
| `MeshBasicMaterial` | No — flat, unlit color regardless of light | UI elements, wireframes, things that should always look the same brightness |
| `MeshStandardMaterial` | Yes — physically-based rendering (PBR) | The general-purpose default for realistic-looking objects |
| `MeshPhysicalMaterial` | Yes — PBR + extras (clearcoat, transmission/glass) | High-fidelity materials needing glass, car paint, etc. |
| `MeshLambertMaterial` | Yes — simpler, cheaper diffuse-only lighting | Performance-sensitive scenes with many lit objects |
| `MeshPhongMaterial` | Yes — adds specular highlights, cheaper than Standard | Shiny plastic-like look without full PBR cost |

**Why `MeshBasicMaterial` renders in a scene with no lights and `MeshStandardMaterial` doesn't**: Basic ignores lighting math entirely and just paints the flat `color` — it's the material to reach for when debugging "why is my object invisible," since it rules out lighting as the cause.

## Key material properties

```js
const material = new THREE.MeshStandardMaterial({
  color: 0xff0000,
  roughness: 0.5,   // 0 = mirror-smooth, 1 = fully matte
  metalness: 0.8,    // 0 = non-metal (dielectric), 1 = metal — affects how it reflects
  wireframe: false,   // render as a wireframe mesh instead of solid — useful for debugging geometry
  transparent: true,   // must be true for `opacity` below 1 to have any effect
  opacity: 0.5,
});
```

`roughness`/`metalness` are the two core PBR (physically-based rendering) parameters — instead of hand-tuning ad-hoc "shininess" values like older material models, PBR parameterizes surfaces the way real-world material science does, so combinations tend to look physically plausible by default rather than needing extensive manual tuning.

## Reusing geometry/material across many meshes

Because geometry and material are separate objects, the same instances can back many meshes — cheaper on memory than creating a new geometry/material per object:

```js
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });

for (let i = 0; i < 100; i++) {
  const cube = new THREE.Mesh(geometry, material); // shared geometry & material
  cube.position.set(Math.random() * 10, Math.random() * 10, Math.random() * 10);
  scene.add(cube);
}
```

For genuinely large counts (thousands+) of identical objects, `InstancedMesh` goes further and renders them all in a single draw call — covered in [[08-performance-and-gotchas|performance and gotchas]].

## Related
- [[01-intro|intro]] — the minimal scene this builds on
- [[03-lighting-and-shadows|lighting and shadows]] — why lit materials need light sources to be visible at all
- [[05-textures|textures]] — applying images to a material instead of a flat color
