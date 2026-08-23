# Three.js: Intro

Three.js is a JavaScript 3D graphics library that wraps **WebGL** — the browser's low-level, GPU-accelerated 3D rendering API — in a much friendlier object-oriented API. Raw WebGL requires writing shader programs (GLSL) and manually managing buffers just to draw a single triangle; three.js gives you `Mesh`, `Camera`, `Light` objects and handles the WebGL calls underneath.

This is a genuinely different domain from [[frontend/frameworks/gsap/README|GSAP]] and [[frontend/frameworks/framer-motion/README|Framer Motion]] — those animate 2D DOM/SVG properties; three.js renders an actual 3D scene onto a `<canvas>` element, with its own coordinate system, cameras, and lighting model borrowed from real-world graphics/physics concepts.

## Installing

```bash
npm install three
```

```js
import * as THREE from "three";
```

## The three required pieces

Every three.js app needs exactly these three things before anything appears on screen:

```js
// 1. Scene — the container that holds every object, light, and camera
const scene = new THREE.Scene();

// 2. Camera — the viewpoint the scene is rendered from
const camera = new THREE.PerspectiveCamera(
  75,                                    // field of view (degrees)
  window.innerWidth / window.innerHeight, // aspect ratio — must match canvas dimensions
  0.1,                                    // near clipping plane
  1000                                     // far clipping plane
);
camera.position.z = 5;

// 3. Renderer — draws the scene from the camera's viewpoint onto a canvas
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
```

**Why near/far clipping planes exist**: WebGL uses a depth buffer with finite precision to figure out what's in front of what — without bounds, that precision would have to cover from 0 to infinity, which isn't numerically practical. Anything closer than `near` or farther than `far` simply isn't rendered. Setting these too far apart (e.g. `0.0001` to `1000000`) causes **z-fighting** — flickering artifacts where the renderer can't reliably tell which of two close surfaces is in front, because the available depth precision is spread across too large a range.

## A minimal complete scene

```js
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 5, 5);
scene.add(light);

function animate() {
  requestAnimationFrame(animate);
  cube.rotation.x += 0.01;
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();
```

Note the `MeshStandardMaterial` here requires a light to be visible at all — most materials are lit (they simulate how light interacts with a surface), which is why [[03-lighting-and-shadows|lighting]] is not optional the way it effectively is in 2D animation. A scene with geometry and no light will render as solid black.

## The coordinate system

Three.js uses a **right-handed** coordinate system: +X right, +Y up, +Z *toward the camera* (out of the screen). This trips people coming from 2D web/CSS work, where +Y conventionally points *down*. "Moving something back" in a 3D scene means decreasing Z, not increasing it.

## Related
- [[02-geometries-materials-meshes|geometries, materials, and meshes]] — what a `Mesh` actually is
- [[04-transformations-and-animation-loop|transformations and the animation loop]] — `requestAnimationFrame` in depth
- [[07-react-three-fiber|React Three Fiber]] — the declarative React wrapper, if working inside this frontend/React track
