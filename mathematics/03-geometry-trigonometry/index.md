# Geometry and Trigonometry

**Shape, measurement, and the arguments that make them certain.** Written to [[COURSE-STANDARD|the course standard]]: every lesson has prerequisites, observable outcomes, a worked derivation, a runnable lab whose output has been checked against an actual run, practice with hidden answers, and a demonstrable finish line.

This umbrella merges both curricula — the [[ss1-ss3-course-outline|SS1–SS3 NERDC outline]] and the [[uni-math-course-outline|university track]] — so each subject appears once, secondary treatment first and university treatment after. Trigonometry, for instance, runs from SS1 ratios through SS2 bearings to university hyperbolic functions in one sequence.

> **The one idea:** geometry replaced *measuring* with *proving*. A protractor gives you an angle to half a degree; a two-line argument gives you the same angle exactly, for every figure of that shape that will ever be drawn. Everything here is built on a small set of assumptions — and knowing **which** statements are assumed rather than proved is the difference between doing geometry and reciting it.

## Reading order

The dependencies are real. The angle-sum proof needs parallel lines; the circle theorems need the exterior angle theorem; the trigonometric ratios need similar triangles; the sine rule needs the ratios; latitude and longitude needs the sine and cosine rules.

### 01 — Deductive geometry *(SS1 Term 2)*

1. [[01-deductive-geometry/01-angles-and-parallel-lines|Angles and Parallel Lines]] — **[Beginner]** — how measuring one angle gives you seven, and which single fact about parallels is assumed rather than proved
2. [[01-deductive-geometry/02-triangles-and-polygons|Triangles and Polygons]] — **[Beginner]** — the angle sum proved, and why **SSA is not a congruence criterion**, with two triangles from identical data
3. [[01-deductive-geometry/03-constructions|Constructions]] — **[Beginner]** — exact figures from two tools that cannot measure, and why trisecting a general angle is *impossible* rather than merely hard

### 02 — Circle geometry *(SS2 Terms 2–3)*

4. [[02-circle-geometry/01-circle-theorems|Circle Theorems]] — **[Beginner]** — one theorem about the centre, and the four results that follow from it for free
5. [[02-circle-geometry/02-tangents|Tangents to a Circle]] — **[Intermediate]** — the alternate segment theorem, and **power of a point**: one formula covering chords, secants and tangents

### 03 — Coordinate geometry *(SS2 Term 3)*

6. [[03-coordinate-geometry/01-coordinate-geometry|Coordinate Geometry]] — **[Beginner]** — Descartes' bridge: geometry becomes algebra, and a theorem proved earlier by congruent triangles falls out of a gradient product

### 04 — Trigonometry *(SS1 T3 → SS2 T3 → university)*

7. [[04-trigonometry/01-ratios-and-right-triangles|Trigonometric Ratios]] — **[Beginner]** — why a ratio of sides depends only on an angle, and measuring a tree you cannot climb
8. [[04-trigonometry/02-graphs-and-identities|Graphs and Identities]] — **[Intermediate]** — the unit circle extends the ratios to every angle; the addition formula **derived**, not stated
9. [[04-trigonometry/03-sine-and-cosine-rules|Sine and Cosine Rules]] — **[Intermediate]** — triangles without a right angle, and the ambiguous case worked through in full
10. [[04-trigonometry/04-bearings|Bearings]] — **[Intermediate]** — navigation angles, and solving one journey two ways as a check
11. [[04-trigonometry/05-hyperbolic-functions|Hyperbolic Functions]] — **[Advanced]** — the hanging chain that Galileo got wrong, and the family that parametrises a hyperbola instead of a circle

### 05 — Mensuration *(SS1 Term 3)*

12. [[05-mensuration/01-plane-shapes|Plane Shapes]] — **[Beginner]** — areas by rearrangement, then $\pi r^2$ derived as a **limit of polygons**, reproducing Archimedes' bounds
13. [[05-mensuration/02-solids|Solids]] — **[Intermediate]** — Cavalieri's principle, and the sphere's volume from a cylinder minus a cone

### 06 — Latitude and longitude *(SS3 Term 1)*

14. [[06-latitude-and-longitude/01-latitude-and-longitude|Latitude and Longitude]] — **[Intermediate]** — measuring *on* a sphere, where two points at the same latitude are not most quickly reached by heading due east

### 07 — Analytic geometry in space *(university Year 1)*

15. [[07-analytic-geometry-3d/01-lines-and-planes|Lines and Planes in Space]] — **[Advanced]** — vectors replace gradient, and **skew** lines appear: neither parallel nor meeting
16. [[07-analytic-geometry-3d/02-quadric-surfaces|Quadric Surfaces]] — **[Advanced]** — classification by signs, the saddle, and a curved surface built entirely from straight lines

## Where the two curricula meet

| Lesson | Secondary source | University source |
| :--- | :--- | :--- |
| Angles, triangles, constructions | SS1 T2 deductive geometry | assumed |
| Circle theorems, tangents | SS2 T2–T3 | assumed |
| Coordinate geometry | SS2 T3 | extended in lesson 15 |
| Trigonometric ratios, graphs | SS1 T3 | Y1S1 algebra and trigonometry |
| Sine and cosine rules, bearings | SS2 T3 | applied throughout |
| Hyperbolic functions | — | Y1S1 |
| Mensuration | SS1 T3 | superseded by integration |
| Latitude and longitude | SS3 T1 | — |
| Lines, planes, quadrics | — | Y1S2 vectors and analytic geometry |

## What is verified

Every lesson's lab has been executed and its documented "Expected output" block generated from that run rather than written by hand. Several labs check a claim the prose makes rather than merely illustrating it:

- **SSA is ambiguous** — two distinct triangles from $A = 30°$, $a = 5$, $b = 8$.
- **Archimedes' bounds** — the $96$-gon semi-perimeters bracket $\pi$ between $3.141032$ and $3.142715$.
- **Cavalieri's principle** — a hemisphere and a cylinder-minus-cone match slice for slice.
- **The parallel route is longer** — $10{,}008$ km along $60°$N against $6{,}672$ km over the pole.
- **The hyperboloid is doubly ruled** — points along two families of straight lines satisfy $x^2+y^2-z^2=1$ to within $10^{-12}$.
- **Haversine versus the cosine rule** — at one metre's separation the cosine rule has lost most of its significant figures.

## How to study this

1. **Attempt the prediction before reading past it.** Most lessons stop and ask you to commit to an answer. The answers are at the end of *Check your understanding*, deliberately not next to the question.
2. **Do the constructions physically at least once.** Lesson 3 can be done entirely in code, and something is lost if it is.
3. **Run the labs and change them.** Each one is self-contained, standard library only, and writes no files.
4. **Track which statements are assumed.** The parallel postulate in lesson 1, Cavalieri in lesson 13, the sphere approximation in lesson 14. Each is flagged where it is used.

## Related

- [[mathematics/index|mathematics/]] — the parent course and the full topic map
- [[01-linear-equations|Linear Equations]] — the algebra every angle chase reduces to
- [[04-linear-algebra/02-vectors/01-vectors|Vectors]] — the same objects as lesson 15, developed as algebra
- [[06-calculus/03-calculus-2/03-applications|Applications of Integration]] — where the mensuration limits become integrals
- [[COURSE-STANDARD|Course standard]] — the teaching shape these lessons follow
