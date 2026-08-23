# Textures

A texture maps a 2D image onto a 3D surface, replacing (or modulating) the flat `color` a material would otherwise use. This is how three.js gets from "grey plastic sphere" to "photorealistic planet" or "wood-grain floor."

## Loading and applying a texture

```js
const loader = new THREE.TextureLoader();
const texture = loader.load("/textures/wood.jpg");

const material = new THREE.MeshStandardMaterial({ map: texture });
const cube = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), material);
```

`TextureLoader.load()` is **asynchronous** — it returns a `Texture` object immediately and fills in the image data once it finishes loading in the background, so the mesh can be created and added to the scene right away without waiting; the surface just appears untextured for the first frame or two. A callback/promise form exists for cases where you specifically need to know when loading completes:

```js
loader.load(
  "/textures/wood.jpg",
  (texture) => { /* onLoad */ },
  undefined,
  (error) => console.error("texture failed to load", error)
);
```

## Texture map types (beyond `map`)

A `MeshStandardMaterial` can combine several texture maps at once, each feeding a different part of the PBR lighting calculation (see [[02-geometries-materials-meshes|geometries, materials, and meshes]]):

```js
const material = new THREE.MeshStandardMaterial({
  map: colorTexture,            // base color/albedo
  normalMap: normalTexture,      // fake surface bumps/detail without adding geometry
  roughnessMap: roughnessTexture, // per-pixel roughness variation
  metalnessMap: metalnessTexture,  // per-pixel metalness variation
  aoMap: aoTexture,                 // ambient occlusion — pre-baked soft shadowing in crevices
});
```

**Why `normalMap` matters**: it's the difference between a flat-looking surface and one that reads as having real surface detail (brick mortar lines, fabric weave, dented metal) — without adding a single extra vertex to the geometry. The normal map encodes, per pixel, which direction the "fake" surface should be treated as facing for lighting purposes, so the lighting calculation produces highlights/shadows that look like real bumps.

## UV mapping

Textures are applied via **UV coordinates** — a 2D (u, v) coordinate per vertex describing where on the flat image that vertex should sample from. Built-in geometries (`BoxGeometry`, `SphereGeometry`, etc.) come with sensible default UVs already computed; custom/imported geometry sometimes needs UVs generated or fixed manually if a texture appears stretched or misaligned.

## Repeating and tiling

```js
texture.wrapS = THREE.RepeatWrapping; // horizontal wrap mode
texture.wrapT = THREE.RepeatWrapping; // vertical wrap mode
texture.repeat.set(4, 4); // tile the texture 4x in each direction instead of stretching once across the surface
```

Without `RepeatWrapping`, `texture.repeat` values above 1 sample past the image edge and produce a stretched/clamped result instead of tiling — the wrap mode has to be set explicitly.

## Related
- [[02-geometries-materials-meshes|geometries, materials, and meshes]] — the material properties textures plug into
- [[08-performance-and-gotchas|performance and gotchas]] — texture size/memory cost, disposing loaded textures
