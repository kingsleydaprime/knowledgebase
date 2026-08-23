# Camera Controls and Raycasting

## OrbitControls

The camera created in [[01-intro|intro]] is completely static by default — moving it requires manually writing mouse/touch handlers, which is tedious to get right (inertia, zoom limits, avoiding the camera flipping upside down). `OrbitControls` is the standard solution: it lets the user rotate, pan, and zoom the camera around a target point using the mouse/touch, all built in.

```js
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; // smooth, inertia-like deceleration instead of stopping instantly
controls.dampingFactor = 0.05;
controls.target.set(0, 0, 0); // the point the camera orbits around

function animate() {
  requestAnimationFrame(animate);
  controls.update(); // REQUIRED every frame when enableDamping (or autoRotate) is on
  renderer.render(scene, camera);
}
```

**Why `controls.update()` has to be called every frame**: with damping enabled, the control's rotation/zoom doesn't jump to its final value instantly — it eases there over several frames, so `update()` needs to run each frame to advance that easing, exactly the same reason an animation loop calls `renderer.render()` every frame rather than once.

`OrbitControls` isn't part of the core `three` package import — it lives under `three/examples/jsm/`, a directory of officially-maintained but separately-imported add-ons (other camera controls like `FlyControls`/`FirstPersonControls`, loaders for formats like `.gltf`, post-processing effects, etc. all live there too).

## Raycasting: detecting what the mouse is pointing at

A 2D mouse click has no inherent meaning in 3D space — raycasting is the technique for converting "the mouse is at this 2D screen position" into "here's what 3D object is under it," by casting an imaginary ray from the camera through that screen point and checking what it intersects.

```js
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onClick(event) {
  // convert pixel coordinates to normalized device coordinates (-1 to +1)
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1; // Y is flipped: screen Y grows down, NDC Y grows up

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children);

  if (intersects.length > 0) {
    const clicked = intersects[0].object; // closest hit — intersects is sorted by distance
    clicked.material.color.set(0xff0000);
  }
}

window.addEventListener("click", onClick);
```

`intersectObjects` returns every object the ray passes through, sorted nearest-first — `intersects[0]` is what the user actually "sees" at that click point (whatever's in front); later entries are objects hidden behind it.

## Why mouse coordinates need normalizing

Raycasting works in **normalized device coordinates** (NDC) — a -1 to +1 range across both axes, independent of actual screen pixel dimensions — because that's the coordinate space the GPU/camera projection already operates in internally. The conversion in the snippet above (`(pixelX / width) * 2 - 1`) maps raw pixel coordinates into that space; skipping it (passing raw pixel values instead) produces wildly wrong or no intersections.

## Limiting raycasting to specific objects

`intersectObjects(scene.children)` checks the entire scene, including lights/helpers that don't need to be interactive — pass a specific array instead for both correctness and performance on scenes with many objects:

```js
const clickable = [cube, sphere, cone]; // only these are interactive
const intersects = raycaster.intersectObjects(clickable);
```

## Related
- [[04-transformations-and-animation-loop|transformations and the animation loop]] — where `controls.update()` and raycasting checks live inside the render loop
- [[07-react-three-fiber|React Three Fiber]] — `<OrbitControls />` and `onClick` become plain JSX props there
