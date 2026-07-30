# Transformations and the Animation Loop

## The three transform properties

Every `Object3D` (meshes, lights, cameras, groups — everything placed in a scene) has the same three transform properties, each a `Vector3`:

```js
cube.position.set(x, y, z);   // where it is
cube.rotation.set(x, y, z);    // orientation, in radians (NOT degrees)
cube.scale.set(x, y, z);        // size multiplier per axis, default (1, 1, 1)

cube.position.x += 1;   // properties are settable individually too
cube.rotation.y = Math.PI / 2; // 90 degrees, expressed in radians
```

**Why radians, not degrees**: this matches the underlying math (WebGL/trigonometric functions all operate in radians) and avoids a conversion step on every rotation calculation. `THREE.MathUtils.degToRad(90)` exists as a helper when it's more natural to think in degrees during development.

## Groups: transforming multiple objects together

`THREE.Group` has the same position/rotation/scale properties, and applies its transform to everything nested inside it — the standard way to move/rotate a compound object (e.g. a car body + four wheels) as one unit while still being able to animate the wheels independently within that group:

```js
const car = new THREE.Group();
car.add(body, wheelFL, wheelFR, wheelBL, wheelBR);
scene.add(car);

car.position.x += 1; // moves the whole car
wheelFL.rotation.x += 0.1; // spins just this wheel, relative to the group's transform
```

## The animation loop: `requestAnimationFrame`

Unlike [[../03-gsap/README|GSAP]] or [[../04-framer-motion/README|Framer Motion]], three.js has no built-in tweening — you drive change yourself, every frame, inside a render loop:

```js
function animate() {
  requestAnimationFrame(animate); // schedule the next frame before doing anything else
  cube.rotation.y += 0.01;
  renderer.render(scene, camera);
}
animate();
```

`requestAnimationFrame` asks the browser to call the given function right before the next repaint — typically 60 times per second, matching the display's refresh rate, and importantly it **pauses automatically when the tab isn't visible**, unlike `setInterval`, which keeps firing (and wasting battery/CPU) in a background tab.

## Frame-rate independence with `Clock`

`cube.rotation.y += 0.01` ties the animation's speed to the frame rate — on a 30fps device it'll rotate at half the speed of a 60fps device. `THREE.Clock` gives you the actual elapsed time between frames (`delta`), so motion can be expressed as "units per second" instead of "units per frame":

```js
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta(); // seconds since the last call
  cube.rotation.y += 1.0 * delta; // 1 radian per second, regardless of frame rate
  renderer.render(scene, camera);
}
animate();
```

This is the same underlying reason [[../03-gsap/02-tweens-and-easing|GSAP]] and [[../04-framer-motion/02-animate-props|Framer Motion]] both express animation in terms of `duration` (seconds) rather than per-frame increments — three.js just doesn't hide this from you the way those higher-level libraries do, since it's a lower-level rendering library, not an animation library.

## Cleanup on unmount (React/SPA context)

`requestAnimationFrame` keeps calling itself forever unless explicitly stopped — in a component-based app, failing to cancel the loop on unmount leaves it running against a canvas/scene that no longer exists:

```js
let frameId;
function animate() {
  frameId = requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();

// on cleanup:
cancelAnimationFrame(frameId);
```

[[07-react-three-fiber|React Three Fiber]] handles this automatically, which is one of its main practical advantages over wiring vanilla three.js into a React component by hand.

## Related
- [[01-intro|intro]] — the scene/camera/renderer setup this loop renders every frame
- [[06-camera-controls-and-raycasting|camera controls and raycasting]] — user-driven changes to the scene each frame
- [[07-react-three-fiber|React Three Fiber]] — where this loop is abstracted away
