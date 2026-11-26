# Computer Graphics

## What computer graphics is

Computer graphics is the field of making a computer create, store, change and display pictures on a screen, using programming.

Underneath, a screen is just a grid of tiny dots called pixels. Every picture you’ve ever seen on a computer, whether a photo, a game, an app button or a 3D model, is the computer deciding which pixels to light up and in what colour. Computer graphics is the set of methods for making that decision correctly and quickly.

## What you'll be able to do

By the end you will be able to:
- explain how a screen shows a picture, and how much memory one screen's worth takes;
- draw lines, circles and filled shapes by hand, pixel by pixel, the way a computer does;
- cut away the parts of a drawing that fall outside a window;
- move, turn and resize shapes using matrices (grids of numbers);
- draw smooth curves from a handful of points;
- work out which objects in a 3D scene are hidden behind others;
- explain how games draw 3D worlds in real time, and how films get their lighting realistic.

## Where to start

The course has two parts. **Start with Part 1** if this subject is new to you. It begins with the screen itself and builds up one small step at a time. Part 2 is about how modern 3D rendering works, and it assumes you have Part 1.

If you're revising for the SSG 511 exam, Part 1 plus the three exam notes at the end cover the whole exam.

### Part 1: Drawing on the screen (start here)

Read 01 to 09 in order: 03 to 08 are one topic, line drawing, in six parts. 10 (clipping) can come next or later. Then read 11 to 19 in order: vectors in three parts, transformations, and curves in five parts each build on the one before. 20 comes last.

1. [[computer-graphics/01-introduction-to-computer-graphics|01 — Introduction to Computer Graphics]]: what computer graphics is, why it is about interaction, and visual problem solving.
2. [[computer-graphics/02-graphics-systems-and-display-hardware|02 — Graphics Systems and Display Hardware]]: how a screen draws a picture line by line, and how much memory a picture needs.
3. [[computer-graphics/03-line-drawing-and-antialiasing-1|03 — Line Drawing and Antialiasing 1: Slopes and the DDA Algorithm]]: how a computer draws a straight line out of square pixels, the simplest way.
4. [[computer-graphics/04-line-drawing-and-antialiasing-2|04 — Line Drawing and Antialiasing 2: Where DDA Goes Wrong]]: why that simple way drifts off the line on big screens, and why it is slow.
5. [[computer-graphics/05-line-drawing-and-antialiasing-3|05 — Line Drawing and Antialiasing 3: Bresenham for Gentle Slopes]]: the same line drawn with whole numbers only, so nothing drifts.
6. [[computer-graphics/06-line-drawing-and-antialiasing-4|06 — Line Drawing and Antialiasing 4: Bresenham for Steep Slopes and Every Direction]]: the exam derivation, and one program for every line.
7. [[computer-graphics/07-line-drawing-and-antialiasing-5|07 — Line Drawing and Antialiasing 5: The Midpoint View and Drawing Shapes]]: the same algorithm seen another way, then polygons and dashed lines.
8. [[computer-graphics/08-line-drawing-and-antialiasing-6|08 — Line Drawing and Antialiasing 6: Antialiasing]]: making the staircase edges of lines look smooth.
9. [[computer-graphics/09-circles-and-polygon-filling|09 — Circles and Polygon Filling]]: drawing circles and ellipses, and colouring in the inside of a shape.
10. [[computer-graphics/10-clipping|10 — Clipping]]: cutting off the parts of a drawing that fall outside the window you're looking through.
11. [[computer-graphics/11-vectors-1|11 — Vectors 1: Points, Vectors and the Journey from A to B]]: what a vector is, and why the vector from A to B is B − A.
12. [[computer-graphics/12-vectors-2|12 — Vectors 2: The Line Between Two Points]]: one number, t, that reaches every point between A and B; used for lines, animation, colours and rays.
13. [[computer-graphics/13-vectors-3|13 — Vectors 3: The Dot and Cross Products]]: how much two vectors point the same way, why lighting needs it, and how to find which way a triangle faces.
14. [[computer-graphics/14-2d-and-3d-transformations|14 — 2D and 3D Transformations]]: moving, turning and resizing shapes with matrices.
15. [[computer-graphics/15-curves-1|15 — Curves 1: Bézier Curves from Straight Lines]]: how three points and the line formula, used three times, make a smooth curve.
16. [[computer-graphics/16-curves-2|16 — Curves 2: The Bézier Formula and Pascal's Triangle]]: turning those steps into one formula, and where its numbers come from.
17. [[computer-graphics/17-curves-3|17 — Curves 3: The Cubic Bézier: Velocity and End Conditions]]: the 4-point curve, how fast it moves, and control points from velocities.
18. [[computer-graphics/18-curves-4|18 — Curves 4: de Casteljau, Splitting and Drawing with Lines]]: how a computer actually draws a curve on the screen.
19. [[computer-graphics/19-curves-5|19 — Curves 5: B-splines and Other Curve Families]]: long curves with local control, and curves that pass through every point.
20. [[computer-graphics/20-visible-surface-detection|20 — Visible Surface Detection]]: working out which objects are in front, so hidden ones aren't drawn.

### Part 2: How modern 3D pictures are made

22 to 26 build on each other, so read them in order. 27 stands on its own. 28 and 29 are about shapes and movement.

21. [[computer-graphics/21-how-rendering-works|21 — How Rendering Works]]: the two ways to turn a 3D scene into a flat picture, and the one equation both are trying to solve.
22. [[computer-graphics/22-the-transform-pipeline|22 — The Transform Pipeline]]: the steps that carry a 3D object from where it sits in the world to a spot on your screen.
23. [[computer-graphics/23-rasterisation|23 — Rasterisation]]: how a graphics card fills in triangles pixel by pixel, and keeps track of what's in front.
24. [[computer-graphics/24-shading-and-lighting|24 — Shading and Lighting]]: how light and materials decide each pixel's colour, so metal looks like metal and wood like wood.
25. [[computer-graphics/25-textures-and-sampling|25 — Textures and Sampling]]: wrapping images around 3D shapes, and keeping them sharp but not shimmering.
26. [[computer-graphics/26-the-gpu-graphics-pipeline|26 — The GPU Graphics Pipeline]]: how a graphics card is programmed, and which tools to learn it with.
27. [[computer-graphics/27-ray-tracing-and-path-tracing|27 — Ray Tracing and Path Tracing]]: following rays of light around a scene, the way films get realistic lighting.
28. [[computer-graphics/28-geometry-and-meshes|28 — Geometry and Meshes]]: how 3D shapes are stored as many small triangles, and other ways to describe them.
29. [[computer-graphics/29-animation-and-simulation|29 — Animation and Simulation]]: making things move: turning smoothly, bending characters, and simple physics.

### Exam support (SSG 511)

25. [[computer-graphics/32-ssg-511-question-bank|32 — SSG 511 Question Bank]]: the exam paper and every assignment question, without answers, each pointing to the note that teaches it.
26. [[computer-graphics/33-comsol-ink-jet-breakup|33 — COMSOL: Modelling Ink Jet Breakup]]: the model answer to exam question 3. It's about fluids, not graphics, so skip it unless you need it.
27. [[computer-graphics/34-ssg-511-formula-sheet|34 — SSG 511 Formula Sheet]]: every Part 1 formula on one page.

## Practice

- [[computer-graphics/30-practice-exercises|30 — Practice Exercises]]: twelve exercises, from colouring a shape by hand to writing a small program that draws a picture.
- [[computer-graphics/31-practice-exercises-solutions|31 — Solutions]]: worked answers. Try first.
- [[computer-graphics/32-ssg-511-question-bank|32 — SSG 511 Question Bank]]: Part 1's practice. Notes 03, 06, 10 and 18 have small programs to check your answers.
- [[build-your-own-shit/22-your-own-ray-tracer|Build your own ray tracer]]: a step-by-step project. You write a program that draws a 3D scene with realistic light, from scratch.

## Key ideas to remember

Once you've read the notes, these are the points worth keeping. Each links to where it's explained.

1. **Drawing a line is a choice between two pixels at every step:** which one is closer to the true line? A computer answers that using only whole numbers, which is fast. → [[computer-graphics/05-line-drawing-and-antialiasing-3|05]]
2. **Always step along the longer direction of a line,** or it comes out with gaps. → [[computer-graphics/03-line-drawing-and-antialiasing-1|03]]
3. **A tiny error that is never corrected keeps growing.** DDA rounds its step to a few digits: on an 8-pixel line nobody can see it, but across a 4K screen the line ends 5 pixels off. → [[computer-graphics/04-line-drawing-and-antialiasing-2|04]]
4. **In clipping, a "maybe" isn't a "yes".** When a line's codes don't rule it out, you still have to cut it and check again. → [[computer-graphics/10-clipping|10]]
5. **Moving a shape can't be done by multiplying with a 2 × 2 grid.** That's why graphics adds an extra coordinate, so moving, turning and resizing all become one multiplication. → [[computer-graphics/14-2d-and-3d-transformations|11]]
6. **Subtract to find the journey, add to apply it.** B − A is how far and which way; A + t(B − A) is where you are after a fraction t of the trip. Lines, animation, colour blends and rays are all this one formula. → [[computer-graphics/12-vectors-2|12]]
7. **A Bézier curve is the line formula used on lines of lines.** Find a point on each control-polygon line, then a point between those, all at the same t. It bends because the helper points move in different directions. → [[computer-graphics/15-curves-1|15]]
8. **A smooth curve can be split in half at any point** using a simple averaging trick, which is how computers draw curves. → [[computer-graphics/18-curves-4|18]]
9. **There are two ways to draw a 3D scene.** Fill in triangles one at a time (fast; used by games), or follow rays of light (slow but realistic; used by films). → [[computer-graphics/21-how-rendering-works|14]]
10. **The depth buffer won because it needs no sorting.** Each pixel remembers how far away its colour came from, and a nearer object simply replaces it. → [[computer-graphics/23-rasterisation|16]]
11. **Do lighting maths before converting colours for the screen,** or the picture comes out too dark with washed-out highlights. → [[computer-graphics/24-shading-and-lighting|17]]
12. **To find out what's slowing a game down, lower the resolution.** If it doesn't get faster, the graphics card isn't the problem. → [[computer-graphics/26-the-gpu-graphics-pipeline|19]]
13. **Move physics forward in fixed steps,** not "however long the last frame took", or the simulation behaves differently on fast and slow machines. → [[computer-graphics/29-animation-and-simulation|22]]

## Where to go next

- **[*Ray Tracing in One Weekend*](https://raytracing.github.io)**: free, short, and you finish with a real picture made by your own program. The best first project in graphics.
- **[LearnOpenGL](https://learnopengl.com)**: free lessons on drawing 3D scenes with a graphics card.
- **[Shadertoy](https://shadertoy.com)**: write a small program in your browser and see the picture change instantly.
- **Books:** *Fundamentals of Computer Graphics* (Marschner and Shirley) for the basics. After that, *Physically Based Rendering* (Pharr, Jakob and Humphreys), which is free online.

## Related

- [[gpu-and-parallel-computing/index|GPU and Parallel Computing]]: graphics cards were invented for this work.
- [[mathematics/07-applied-and-computational/01-numerical-methods/index|Numerical Methods]]: the maths behind curves and light calculations.
- [[machine-learning/06-computer-vision/index|Computer Vision]]: the reverse problem, getting a scene back from a picture.

---

## About this course

- **Size:** 34 notes, about 53,000 words, including practice, solutions, a question bank and a formula sheet.
- **History:** Part 2 (modern 3D, notes 21–29, with practice notes 30–31) was written in August 2026. Part 1 (drawing on the screen, notes 01–20) and the exam notes (32–34) were added in November 2026 from the SSG 511 course notes, and the notes were renumbered so the beginner part comes first. Later in November 2026 the one line drawing note was split into six parts (03–08), with more pictures, and the notes after it moved up by five. Then, still in November 2026, vectors were added in three parts (11–13) from a study conversation on vectors and Bézier curves, and the one curves note was split into five parts (15–19), with the conversation's step-by-step Bézier explanation as Curves 1 and 2; the notes after it moved up by seven.
- **Not covered yet:** colour science in depth, smoke and fog, light passing through skin, generating content procedurally, VR and AR, video compression, and drawing text and fonts.
