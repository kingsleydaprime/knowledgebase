# React Three Fiber (R3F)

React Three Fiber is a React renderer for three.js — not a wrapper that calls three.js imperatively from `useEffect`, but a genuine **custom React reconciler** (the same mechanism react-dom uses to turn JSX into DOM nodes) that turns JSX into three.js scene graph objects directly. This is a meaningfully deeper integration than how [[../03-gsap/06-react-integration|GSAP integrates with React]], which stays fully imperative underneath a `useGSAP` convenience hook.

## Installing

```bash
npm install @react-three/fiber three
npm install @react-three/drei   # a companion library of ready-made helpers (see below)
```

## The Canvas component and JSX scene graph

```jsx
import { Canvas } from "@react-three/fiber";

function Scene() {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} castShadow />
      <mesh>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="green" />
      </mesh>
    </Canvas>
  );
}
```

**How the JSX maps to plain three.js**: lowercase tag names correspond directly to three.js class names (`mesh` → `THREE.Mesh`, `boxGeometry` → `THREE.BoxGeometry`) — R3F auto-detects any class exported from three.js and makes it available as a JSX element. `args` passes constructor arguments (`new THREE.BoxGeometry(1, 1, 1)`), while regular JSX props set properties directly (`intensity={0.5}` → `light.intensity = 0.5`). `<Canvas>` sets up the scene, default camera, renderer, and animation loop automatically — the manual boilerplate from [[01-intro|intro]] is gone entirely.

## The animation loop: `useFrame`

Instead of a manual `requestAnimationFrame` loop (see [[04-transformations-and-animation-loop|transformations and the animation loop]]), R3F provides a hook that runs a callback every rendered frame, already wired to the component lifecycle (starts/stops automatically with mount/unmount — no manual `cancelAnimationFrame` needed):

```jsx
import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

function SpinningCube() {
  const meshRef = useRef();

  useFrame((state, delta) => {
    meshRef.current.rotation.y += delta; // delta = seconds since last frame, same Clock concept as vanilla three.js
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="orange" />
    </mesh>
  );
}
```

`state` (the first arg) gives access to the scene, camera, mouse position, and clock — most of what you'd otherwise reach for module-level variables to get in vanilla three.js.

## drei: common helpers, pre-built

`@react-three/drei` wraps common three.js add-ons (like [[06-camera-controls-and-raycasting|OrbitControls]]) as ready-to-use components, removing the manual `controls.update()` wiring:

```jsx
import { OrbitControls, Environment, Text } from "@react-three/drei";

<Canvas>
  <OrbitControls enableDamping />
  <Environment preset="sunset" /> {/* realistic HDRI lighting/reflections in one line */}
  <Text position={[0, 2, 0]}>Hello, 3D</Text>
  {/* ...meshes */}
</Canvas>
```

## Why reach for R3F instead of vanilla three.js in a React app

Three real advantages, not just syntax preference:
1. **Declarative scene graph** — the scene is described as a function of props/state, same mental model as the rest of a React app, instead of a separate imperative script bolted on via refs
2. **Automatic cleanup** — geometries, materials, and event listeners created by JSX elements are disposed automatically on unmount, sidestepping the manual disposal discipline covered in [[08-performance-and-gotchas|performance and gotchas]]
3. **Composability** — a 3D object can be its own React component, reused and parameterized with props exactly like any other component, rather than a standalone function that builds and returns a `THREE.Group`

The tradeoff: an extra abstraction layer between you and three.js's actual API, which occasionally makes debugging or reaching for a very specific three.js feature slightly more indirect than calling it directly.

## Related
- [[01-intro|intro]] — the plain three.js concepts this wraps
- [[04-transformations-and-animation-loop|transformations and the animation loop]] — what `useFrame` replaces
- [[06-camera-controls-and-raycasting|camera controls and raycasting]] — what `<OrbitControls />` from drei replaces
