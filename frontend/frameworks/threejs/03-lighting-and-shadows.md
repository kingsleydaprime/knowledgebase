---
id: 82433f1f-7503-4706-b382-60ab4e8d4404
---

# Lighting and Shadows

Most materials (anything except `MeshBasicMaterial`, see [[02-geometries-materials-meshes|geometries, materials, and meshes]]) are dark or invisible without a light source in the scene — lighting isn't decoration in three.js, it's required for the standard rendering path to produce anything visible at all.

## Light types
<!-- bite: 47572a01-0242-4cde-a33a-0e8e344706ef -->

```js
// AmbientLight — uniform light from all directions, no shadows, no directionality
const ambient = new THREE.AmbientLight(0xffffff, 0.5); // color, intensity
scene.add(ambient);

// DirectionalLight — parallel rays, like the sun; has a position AND a target
const directional = new THREE.DirectionalLight(0xffffff, 1);
directional.position.set(5, 10, 5);
scene.add(directional);

// PointLight — radiates in all directions from a single point, like a bare bulb
const point = new THREE.PointLight(0xffaa00, 1, 100); // color, intensity, distance (falloff range)
point.position.set(0, 5, 0);
scene.add(point);

// SpotLight — cone-shaped, like a flashlight/stage light
const spot = new THREE.SpotLight(0xffffff, 1);
spot.position.set(0, 10, 0);
spot.angle = Math.PI / 6; // cone width
scene.add(spot);
```

## Why `AmbientLight` alone looks flat
<!-- bite: bcfa9ca1-5972-4025-a65e-f1a0d0d7abee -->

`AmbientLight` illuminates every surface equally regardless of its orientation to the light — there's no directionality to create shading, so objects look flat and shapeless, like a photo with no shadows at all. Real-looking scenes almost always combine `AmbientLight` (so shadow areas aren't pitch black — approximating the effect of light bouncing around a real environment) with at least one directional/point light to create actual shading and form.

## Shadows: three separate switches, all required
<!-- bite: e5c950b4-28f2-4487-92d6-f4db6b4aac42 -->

Shadows are disabled by default (real cost — the renderer does an extra render pass per shadow-casting light) and need three things enabled together, or nothing appears:

```js
// 1. Enable shadow maps on the renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // softer shadow edges

// 2. Tell the light to cast shadows
directional.castShadow = true;

// 3. Tell each object whether it casts and/or receives shadows
cube.castShadow = true;
floor.receiveShadow = true;
```

**Why this is three separate flags instead of one**: each is a real performance cost, so three.js requires you to opt in individually. Every object has `castShadow`/`receiveShadow` both `false` by default — the most common "why aren't my shadows showing up" bug is forgetting one of the three, most often `receiveShadow` on the floor/ground plane.

## Shadow map resolution and quality
<!-- bite: f5c896b7-f0f3-40c3-b76b-b1c011683e80 -->

```js
directional.shadow.mapSize.width = 2048;
directional.shadow.mapSize.height = 2048;
directional.shadow.camera.near = 0.5;
directional.shadow.camera.far = 50;
```

A shadow map is essentially a depth-image rendered from the light's point of view, at a fixed resolution — low resolution produces blocky/jagged shadow edges ("shadow acne" or aliasing), especially over large scenes. `shadow.camera.near/far` bound the same way the main camera's clipping planes do (see [[01-intro|intro]]) — too wide a range wastes shadow-map precision on distances nothing actually occupies.

## Which lights cast shadows
<!-- bite: 48163a8f-d61e-4040-bf99-dfb5f8afb021 -->

Not all light types support `castShadow` equally cheaply — `PointLight` shadows are the most expensive (the engine effectively renders the depth map in six directions, like a cube, since a point light radiates every direction), while `DirectionalLight`/`SpotLight` shadow from a single direction. For scenes with many lights, it's common to enable shadows on only the one or two lights that actually need to cast a visible shadow, and leave the rest shadow-less.

## Related
<!-- bite: a53b6ae5-5334-41a7-a712-7b771f77b28d -->
- [[02-geometries-materials-meshes|geometries, materials, and meshes]] — why lit materials need this at all
- [[08-performance-and-gotchas|performance and gotchas]] — shadow map cost, light count budgets
