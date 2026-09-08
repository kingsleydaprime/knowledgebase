# Geometry and Meshes

**[Intermediate → Advanced]** — Representing shape. Meshes, curves, implicit surfaces, and the trade-offs between them.

## Meshes

**The dominant representation: vertices, edges, faces.**

**Storage — indexed triangles, essentially always:**

```
 vertices: [v0, v1, v2, v3, ...]           position, normal, UV, tangent
 indices:  [0,1,2,  0,2,3,  ...]           three per triangle
```

**Indexing avoids duplicating shared vertices** — a cube has 8 vertices, not 36. **And it lets the GPU cache transformed vertices**, so a vertex shared by six triangles is transformed once rather than six times.

**The subtlety: a vertex is a bundle of attributes, not just a position.** A cube corner has three different normals (one per face) and usually different UVs, **so it must be duplicated** — you can't share it. **This is why a "8-vertex cube" is actually 24 vertices in a renderer**, and it surprises people.

**Winding order** determines facing. Counter-clockwise is front-facing by convention in OpenGL. **A mirrored transform flips winding**, which is why negatively-scaled objects render inside-out. → [[foundations/computer-graphics/02-the-transform-pipeline|Coordinate systems]]

### Connectivity structures

**When you need to *query* topology — "which faces share this edge?" — the index buffer is inadequate.**

**Half-edge (doubly connected edge list)** — each edge stored as two directed halves, each knowing its face, its next half-edge, and its twin.

> **Gives you $O(1)$ adjacency queries**, which is what mesh *editing* needs — subdivision, simplification, smoothing, and anything walking the surface. **Blender, CGAL and OpenMesh all use a variant.**
>
> **The constraint: it requires a manifold mesh.** Non-manifold geometry — an edge shared by three faces, or a vertex joining two cones at a point — **breaks the invariants.** Real-world scanned and modelled meshes are frequently non-manifold, which is why repair tools exist.

**Winged-edge** is the older equivalent; **simplicial complexes** and sparse matrices for more general cases.

## Curves and surfaces

**Smooth shapes, defined by control points.**

**Bézier curves:**

$$\mathbf{B}(t) = \sum_{i=0}^{n}\binom{n}{i}(1-t)^{n-i}t^i\,\mathbf{P}_i$$

**Cubic ($n=3$) is the workhorse.** Passes through the first and last control points, tangent to the control polygon at the ends.

**Every vector graphics tool and font format is cubic Béziers** — SVG, PostScript, TrueType (quadratic), OpenType.

**De Casteljau's algorithm** evaluates them by repeated linear interpolation. **Numerically stable, geometrically obvious, and it splits the curve for free** — which is how curves get subdivided for rendering.

**B-splines** — local control. **Moving one control point affects only a local region**, unlike a Bézier where every point influences the whole curve. Essential for editing complex shapes.

**NURBS** — rational B-splines. **Can represent conic sections exactly** — a true circle, not an approximation. **The CAD standard**, because engineering needs exact circles and cylinders.

> **This is the CAD/graphics divide.** **CAD uses NURBS** because manufacturing needs exact analytic surfaces. **Real-time graphics tessellates everything to triangles** because that's what GPUs rasterise. **Importing CAD into a renderer means tessellating**, and the tessellation tolerance is a real quality/performance knob.

→ [[foundations/numerical-methods/06-interpolation-and-approximation|Splines]]

**Subdivision surfaces** — start with a coarse control mesh, repeatedly refine.

**Catmull–Clark** is the standard (and Ed Catmull went on to found Pixar). **Converges to a smooth limit surface, handles arbitrary topology**, and gives artists a low-poly cage to manipulate. **The film industry's standard representation.**

## Implicit surfaces

**Define the surface as a level set: $f(\mathbf{x}) = 0$.**

**Signed distance fields** are the useful case — $f$ returns the distance to the surface, negative inside.

```
sphere(p, r)  = length(p) - r
box(p, b)     = length(max(abs(p) - b, 0))
union(a, b)   = min(a, b)
intersect(a,b)= max(a, b)
subtract(a,b) = max(a, -b)
```

> **Boolean operations are `min` and `max`.** Constructive solid geometry becomes trivial, where doing the same on meshes requires robust and notoriously fiddly boolean algorithms. **Smooth blending is a softened `min`**, which is why SDF shapes blob together so naturally.

**Rendered by sphere tracing** — step along the ray by the distance value, which is guaranteed safe:

```
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

**Point clouds** — just positions, from lidar or photogrammetry. **No connectivity**, so rendering means splatting or surface reconstruction (Poisson, ball-pivoting).

**Directly relevant to [[robotics/12-localisation-and-slam|SLAM]]**, where the map often *is* a point cloud.

**Gaussian splatting** (2023) represents a scene as millions of anisotropic 3D Gaussians, rasterised with alpha blending. **Photorealistic novel views at real-time rates**, trained from photos. **A genuinely significant recent development** — it's faster than NeRF at both training and rendering, and it revived splatting as a technique.

**Voxels** — a 3D grid. **Simple, memory-hungry** ($O(n^3)$). Sparse voxel octrees and bricks make it viable; used for volumetric effects, destructible terrain, and medical data.

**NeRF** — a neural network mapping position and view direction to colour and density, rendered by volumetric ray marching. **Impressive quality, slow to train and render**, and largely superseded by Gaussian splatting for practical use.

## Level of detail and simplification

**Fewer triangles when it doesn't matter.**

**Discrete LOD** — several pre-built versions, swapped by distance. **Simple, and "popping" is visible** at the switch.

**Continuous LOD / progressive meshes** — collapse edges incrementally.

**Quadric error metrics** (Garland–Heckbert) is the standard simplification algorithm: **for each vertex, accumulate a quadric measuring squared distance to its incident planes, and collapse the edge with the lowest error.** Fast, high quality, and what every mesh-decimation tool implements.

**Nanite** (Unreal 5) — cluster-based, GPU-driven, **effectively continuous LOD with software rasterisation for sub-pixel triangles.** Removes the LOD authoring problem, which was a large chunk of art-pipeline effort.

**Impostors and billboards** — replace distant geometry with a textured quad. **Still the right answer for forests and crowds.**

## Mesh processing

**The operations you'll meet:**

**Normal computation** — average the face normals around each vertex, **weighted by face area or angle.** Unweighted averaging biases toward regions with many small triangles.

**Smoothing** — Laplacian smoothing moves each vertex toward its neighbours' centroid. **Simple, and it shrinks the mesh**; Taubin smoothing alternates positive and negative steps to preserve volume.

**Parameterisation (UV unwrapping)** — minimise distortion, cut into charts, pack. **Genuinely hard**, and Gauss's *Theorema Egregium* says perfect flattening is impossible for curved surfaces. → [[foundations/computer-graphics/05-textures-and-sampling|UV mapping]]

**Remeshing** — improve triangle quality. **Sliver triangles cause numerical problems** in both rendering and simulation. → [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM mesh quality]]

**Repair** — fill holes, fix non-manifold edges, correct inconsistent winding. **Necessary before almost any serious processing**, and before 3D printing.

**Boolean operations** — union, intersection, difference on meshes. **Notoriously fragile** because of floating-point issues at coincident faces. **Exact predicates or SDF conversion are the robust approaches.**

## Practical notes

**Use indexed triangles**, and optimise the index order for the vertex cache (Forsyth's algorithm, or `meshoptimizer`). **A cache-optimised index buffer is a free 10–20%** on vertex-bound scenes.

**Choose the representation for the operation.** Meshes for rendering, half-edge for editing, SDFs for booleans and blending, NURBS for CAD, point clouds for capture.

**Check for degenerate triangles** — zero area, duplicate vertices. **They produce NaN normals** that propagate silently. → [[foundations/numerical-methods/02-floating-point-and-error|NaN]]

**Validate manifoldness** before running anything topological.

**Use a library.** `meshoptimizer` (optimisation and simplification), CGAL (robust computational geometry), libigl (research-friendly), Open3D (point clouds), Assimp (loading).

**Watch triangle count *and* draw calls.** A million triangles in one draw is usually fine; a thousand draws of a thousand triangles usually isn't. → [[foundations/computer-graphics/06-the-gpu-graphics-pipeline|Batching]]

---

## Related
- [[foundations/numerical-methods/06-interpolation-and-approximation|Interpolation]] — the spline mathematics
- [[foundations/computer-graphics/09-animation-and-simulation|Animation and Simulation]] — deforming these
- [[engineering/01-continuum-mechanics/13-computational-methods-and-fem|FEM]] — meshes for simulation rather than rendering
- [[foundations/computer-graphics/README|Computer graphics map]]
