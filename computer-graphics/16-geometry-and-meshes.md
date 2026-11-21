---
id: 27db874b-8a0b-4d28-9b3f-7b2a6c162fb7
---

# Geometry and Meshes

A mesh is a 3D shape made of many small flat pieces, usually triangles, joined along their edges, like a football stitched from panels. Almost every 3D object in games and films is stored as a mesh, and this lesson also looks at other ways of describing shape.

## Meshes
<!-- bite: dc32b244-fe8b-4e64-bdc7-8f5edd452f3a -->

**The dominant representation: vertices, edges, faces.**

**Storage — indexed triangles, essentially always:**

```text
 vertices: [v0, v1, v2, v3, ...]           position, normal, UV, tangent
 indices:  [0,1,2,  0,2,3,  ...]           three per triangle
```

**Indexing avoids duplicating shared vertices** — a cube has 8 vertices, not 36. **And it lets the GPU cache transformed vertices**, so a vertex shared by six triangles is transformed once rather than six times.

**The subtlety: a vertex is a bundle of attributes, not just a position.** A cube corner has three different normals (one per face) and usually different UVs, **so it must be duplicated** — you can't share it. **This is why a "8-vertex cube" is actually 24 vertices in a renderer**, and it surprises people.

**Winding order** determines facing. Counter-clockwise is front-facing by convention in OpenGL. **A mirrored transform flips winding**, which is why negatively-scaled objects render inside-out. → [[computer-graphics/10-the-transform-pipeline|Coordinate systems]]

### Connectivity structures

**When you need to *query* topology — "which faces share this edge?" — the index buffer is inadequate.**

**Half-edge (doubly connected edge list)** — each edge stored as two directed halves, each knowing its face, its next half-edge, and its twin.

> **Gives you $O(1)$ adjacency queries**, which is what mesh *editing* needs — subdivision, simplification, smoothing, and anything walking the surface. **Blender, CGAL and OpenMesh all use a variant.**
>
> **The constraint: it requires a manifold mesh.** Non-manifold geometry — an edge shared by three faces, or a vertex joining two cones at a point — **breaks the invariants.** Real-world scanned and modelled meshes are frequently non-manifold, which is why repair tools exist.

**Winged-edge** is the older equivalent; **simplicial complexes** and sparse matrices for more general cases.

## Curves and surfaces
<!-- bite: 78482f24-8b65-4de2-9323-7452b5c3341e -->

**Smooth shapes, defined by control points.**

**Bézier curves:**

$$\mathbf{B}(t) = \sum_{i=0}^{n}\binom{n}{i}(1-t)^{n-i}t^i\,\mathbf{P}_i$$

**Cubic ($n=3$) is the workhorse.** Passes through the first and last control points, tangent to the control polygon at the ends.

**Every vector graphics tool and font format is cubic Béziers** — SVG, PostScript, TrueType (quadratic), OpenType.

**De Casteljau's algorithm** evaluates them by repeated linear interpolation. **Numerically stable, geometrically obvious, and it splits the curve for free** — which is how curves get subdivided for rendering.

**Worked by hand** — control points from velocities, de Casteljau tables, splitting, the derivative, flattening to a tolerance, and Chaikin corner cutting — in [[computer-graphics/07-curves-bezier-and-b-splines|note 07]].

**B-splines** — local control. **Moving one control point affects only a local region**, unlike a Bézier where every point influences the whole curve. Essential for editing complex shapes.

**NURBS** — rational B-splines. **Can represent conic sections exactly** — a true circle, not an approximation. **The CAD standard**, because engineering needs exact circles and cylinders.

> **This is the CAD/graphics divide.** **CAD uses NURBS** because manufacturing needs exact analytic surfaces. **Real-time graphics tessellates everything to triangles** because that's what GPUs rasterise. **Importing CAD into a renderer means tessellating**, and the tessellation tolerance is a real quality/performance knob.

→ [[mathematics/07-applied-and-computational/01-numerical-methods/06-interpolation-and-approximation|Splines]]

**Subdivision surfaces** — start with a coarse control mesh, repeatedly refine.

**Catmull–Clark** is the standard (and Ed Catmull went on to found Pixar). **Converges to a smooth limit surface, handles arbitrary topology**, and gives artists a low-poly cage to manipulate. **The film industry's standard representation.**

## Implicit surfaces
<!-- bite: 4f671faa-49e1-452d-bc31-cc8a0830b9b1 -->

**Define the surface as a level set: $f(\mathbf{x}) = 0$.**

**Signed distance fields** are the useful case — $f$ returns the distance to the surface, negative inside.

```text
sphere(p, r)  = length(p) - r
box(p, b)     = length(max(abs(p) - b, 0))
union(a, b)   = min(a, b)
intersect(a,b)= max(a, b)
subtract(a,b) = max(a, -b)
```

> **Boolean operations are `min` and `max`.** Constructive solid geometry becomes trivial, where doing the same on meshes requires robust and notoriously fiddly boolean algorithms. **Smooth blending is a softened `min`**, which is why SDF shapes blob together so naturally.

**Rendered by sphere tracing** — step along the ray by the distance value, which is guaranteed safe:

```text
t = 0
repeat:
    d = sdf(origin + t*dir)
    if d < epsilon: hit
    t += d
```

**The distance property is what makes it efficient** — you take the largest safe step every time.

**Where SDFs are used:** demoscene and Shadertoy (an entire scene in one fragment shader), **font rendering** (Valve's 2007 paper — scale to any size with sharp edges from a low-resolution texture), soft shadows and ambient occlusion (cheap from the distance field), collision queries, and **3D printing / voxel modelling**.

**The costs:** hard to texture (no natural UV), hard to author by hand, and expensive for complex scenes.

**Marching cubes** converts an implicit surface to a mesh by classifying each grid cell against the isosurface. **The standard for medical imaging (CT/MRI to a surface), terrain from voxels, and metaballs.** Dual contouring handles sharp features better.

## Point clouds and volumes
<!-- bite: c31b0f83-9400-4ed8-ab8d-90203b5eaa4d -->

**Point clouds** — just positions, from lidar or photogrammetry. **No connectivity**, so rendering means splatting or surface reconstruction (Poisson, ball-pivoting).

**Directly relevant to [[robotics/12-localisation-and-slam|SLAM]]**, where the map often *is* a point cloud.

**Gaussian splatting** (2023) represents a scene as millions of anisotropic 3D Gaussians, rasterised with alpha blending. **Photorealistic novel views at real-time rates**, trained from photos. **A genuinely significant recent development** — it's faster than NeRF at both training and rendering, and it revived splatting as a technique.

**Voxels** — a 3D grid. **Simple, memory-hungry** ($O(n^3)$). Sparse voxel octrees and bricks make it viable; used for volumetric effects, destructible terrain, and medical data.

**NeRF** — a neural network mapping position and view direction to colour and density, rendered by volumetric ray marching. **Impressive quality, slow to train and render**, and largely superseded by Gaussian splatting for practical use.

## Level of detail and simplification
<!-- bite: fc4c0579-00d1-49c7-ac05-d85e8250c483 -->

**Fewer triangles when it doesn't matter.**

**Discrete LOD** — several pre-built versions, swapped by distance. **Simple, and "popping" is visible** at the switch.

**Continuous LOD / progressive meshes** — collapse edges incrementally.

**Quadric error metrics** (Garland–Heckbert) is the standard simplification algorithm: **for each vertex, accumulate a quadric measuring squared distance to its incident planes, and collapse the edge with the lowest error.** Fast, high quality, and what every mesh-decimation tool implements.

**Nanite** (Unreal 5) — cluster-based, GPU-driven, **effectively continuous LOD with software rasterisation for sub-pixel triangles.** Removes the LOD authoring problem, which was a large chunk of art-pipeline effort.

**Impostors and billboards** — replace distant geometry with a textured quad. **Still the right answer for forests and crowds.**

## Mesh processing
<!-- bite: f1c413e7-ce0d-44b0-9a56-3394e3ef5389 -->

**The operations you'll meet:**

**Normal computation** — average the face normals around each vertex, **weighted by face area or angle.** Unweighted averaging biases toward regions with many small triangles.

**Smoothing** — Laplacian smoothing moves each vertex toward its neighbours' centroid. **Simple, and it shrinks the mesh**; Taubin smoothing alternates positive and negative steps to preserve volume.

**Parameterisation (UV unwrapping)** — minimise distortion, cut into charts, pack. **Genuinely hard**, and Gauss's *Theorema Egregium* says perfect flattening is impossible for curved surfaces. → [[computer-graphics/13-textures-and-sampling|UV mapping]]

**Remeshing** — improve triangle quality. **Sliver triangles cause numerical problems** in both rendering and simulation. → [[continuum-mechanics/13-computational-methods-and-fem|FEM mesh quality]]

**Repair** — fill holes, fix non-manifold edges, correct inconsistent winding. **Necessary before almost any serious processing**, and before 3D printing.

**Boolean operations** — union, intersection, difference on meshes. **Notoriously fragile** because of floating-point issues at coincident faces. **Exact predicates or SDF conversion are the robust approaches.**

## Practical notes
<!-- bite: 294fe33f-a94c-4de5-82b7-acea99dd9806 -->

**Use indexed triangles**, and optimise the index order for the vertex cache (Forsyth's algorithm, or `meshoptimizer`). **A cache-optimised index buffer is a free 10–20%** on vertex-bound scenes.

**Choose the representation for the operation.** Meshes for rendering, half-edge for editing, SDFs for booleans and blending, NURBS for CAD, point clouds for capture.

**Check for degenerate triangles** — zero area, duplicate vertices. **They produce NaN normals** that propagate silently. → [[mathematics/07-applied-and-computational/01-numerical-methods/02-floating-point-and-error|NaN]]

**Validate manifoldness** before running anything topological.

**Use a library.** `meshoptimizer` (optimisation and simplification), CGAL (robust computational geometry), libigl (research-friendly), Open3D (point clouds), Assimp (loading).

**Watch triangle count *and* draw calls.** A million triangles in one draw is usually fine; a thousand draws of a thousand triangles usually isn't. → [[computer-graphics/14-the-gpu-graphics-pipeline|Batching]]

---

## Related
<!-- bite: 20a44886-99c2-463d-9ad5-48d011ed4eee -->
- [[computer-graphics/07-curves-bezier-and-b-splines|Curves: Bézier and B-splines]] — the hand calculations, and the Cox–de Boor recursion
- [[mathematics/07-applied-and-computational/01-numerical-methods/06-interpolation-and-approximation|Interpolation]] — the spline mathematics
- [[computer-graphics/17-animation-and-simulation|Animation and Simulation]] — deforming these
- [[continuum-mechanics/13-computational-methods-and-fem|FEM]] — meshes for simulation rather than rendering
- [[computer-graphics/index|Computer graphics map]]

## About this lesson
<!-- bite: d8255a5b-df8f-42cb-9649-99680d3376a2 -->

**Level:** Intermediate → Advanced. **Covers:** Representing shape. Meshes, curves, implicit surfaces, and the trade-offs between them.
