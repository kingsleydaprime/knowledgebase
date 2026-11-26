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

Read 01 to 09 in order: 03 to 08 are one topic, line drawing, in six parts. After that, 10 to 13 can be read in any order.

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
11. [[computer-graphics/11-2d-and-3d-transformations|11 — 2D and 3D Transformations]]: moving, turning and resizing shapes with matrices.
12. [[computer-graphics/12-curves-bezier-and-b-splines|12 — Curves: Bézier and B-splines]]: drawing smooth curves, like the pen tool in a design app, from a few control points.
13. [[computer-graphics/13-visible-surface-detection|13 — Visible Surface Detection]]: working out which objects are in front, so hidden ones aren't drawn.

### Part 2: How modern 3D pictures are made

15 to 19 build on each other, so read them in order. 20 stands on its own. 21 and 22 are about shapes and movement.

14. [[computer-graphics/14-how-rendering-works|14 — How Rendering Works]]: the two ways to turn a 3D scene into a flat picture, and the one equation both are trying to solve.
15. [[computer-graphics/15-the-transform-pipeline|15 — The Transform Pipeline]]: the steps that carry a 3D object from where it sits in the world to a spot on your screen.
16. [[computer-graphics/16-rasterisation|16 — Rasterisation]]: how a graphics card fills in triangles pixel by pixel, and keeps track of what's in front.
17. [[computer-graphics/17-shading-and-lighting|17 — Shading and Lighting]]: how light and materials decide each pixel's colour, so metal looks like metal and wood like wood.
18. [[computer-graphics/18-textures-and-sampling|18 — Textures and Sampling]]: wrapping images around 3D shapes, and keeping them sharp but not shimmering.
19. [[computer-graphics/19-the-gpu-graphics-pipeline|19 — The GPU Graphics Pipeline]]: how a graphics card is programmed, and which tools to learn it with.
20. [[computer-graphics/20-ray-tracing-and-path-tracing|20 — Ray Tracing and Path Tracing]]: following rays of light around a scene, the way films get realistic lighting.
21. [[computer-graphics/21-geometry-and-meshes|21 — Geometry and Meshes]]: how 3D shapes are stored as many small triangles, and other ways to describe them.
22. [[computer-graphics/22-animation-and-simulation|22 — Animation and Simulation]]: making things move: turning smoothly, bending characters, and simple physics.

### Exam support (SSG 511)

25. [[computer-graphics/25-ssg-511-question-bank|25 — SSG 511 Question Bank]]: the exam paper and every assignment question, without answers, each pointing to the note that teaches it.
26. [[computer-graphics/26-comsol-ink-jet-breakup|26 — COMSOL: Modelling Ink Jet Breakup]]: the model answer to exam question 3. It's about fluids, not graphics, so skip it unless you need it.
27. [[computer-graphics/27-ssg-511-formula-sheet|27 — SSG 511 Formula Sheet]]: every Part 1 formula on one page.

## Practice

- [[computer-graphics/23-practice-exercises|23 — Practice Exercises]]: twelve exercises, from colouring a shape by hand to writing a small program that draws a picture.
- [[computer-graphics/24-practice-exercises-solutions|24 — Solutions]]: worked answers. Try first.
- [[computer-graphics/25-ssg-511-question-bank|25 — SSG 511 Question Bank]]: Part 1's practice. Notes 03, 06, 10 and 12 have small programs to check your answers.
- [[build-your-own-shit/22-your-own-ray-tracer|Build your own ray tracer]]: a step-by-step project. You write a program that draws a 3D scene with realistic light, from scratch.

## Key ideas to remember

Once you've read the notes, these are the points worth keeping. Each links to where it's explained.

1. **Drawing a line is a choice between two pixels at every step:** which one is closer to the true line? A computer answers that using only whole numbers, which is fast. → [[computer-graphics/05-line-drawing-and-antialiasing-3|05]]
2. **Always step along the longer direction of a line,** or it comes out with gaps. → [[computer-graphics/03-line-drawing-and-antialiasing-1|03]]
3. **A tiny error that is never corrected keeps growing.** DDA rounds its step to a few digits: on an 8-pixel line nobody can see it, but across a 4K screen the line ends 5 pixels off. → [[computer-graphics/04-line-drawing-and-antialiasing-2|04]]
4. **In clipping, a "maybe" isn't a "yes".** When a line's codes don't rule it out, you still have to cut it and check again. → [[computer-graphics/10-clipping|10]]
5. **Moving a shape can't be done by multiplying with a 2 × 2 grid.** That's why graphics adds an extra coordinate, so moving, turning and resizing all become one multiplication. → [[computer-graphics/11-2d-and-3d-transformations|11]]
6. **A smooth curve can be split in half at any point** using a simple averaging trick, which is how computers draw curves. → [[computer-graphics/12-curves-bezier-and-b-splines|12]]
7. **There are two ways to draw a 3D scene.** Fill in triangles one at a time (fast; used by games), or follow rays of light (slow but realistic; used by films). → [[computer-graphics/14-how-rendering-works|14]]
8. **The depth buffer won because it needs no sorting.** Each pixel remembers how far away its colour came from, and a nearer object simply replaces it. → [[computer-graphics/16-rasterisation|16]]
9. **Do lighting maths before converting colours for the screen,** or the picture comes out too dark with washed-out highlights. → [[computer-graphics/17-shading-and-lighting|17]]
10. **To find out what's slowing a game down, lower the resolution.** If it doesn't get faster, the graphics card isn't the problem. → [[computer-graphics/19-the-gpu-graphics-pipeline|19]]
11. **Move physics forward in fixed steps,** not "however long the last frame took", or the simulation behaves differently on fast and slow machines. → [[computer-graphics/22-animation-and-simulation|22]]

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

- **Size:** 26 notes, about 40,000 words, including practice, solutions, a question bank and a formula sheet.
- **History:** Part 2 (modern 3D, notes 14–24) was written in August 2026. Part 1 (drawing on the screen, notes 01–13) and the exam notes (25–27) were added in November 2026 from the SSG 511 course notes, and the notes were renumbered so the beginner part comes first. Later in November 2026 the one line drawing note was split into six parts (03–08), with more pictures, and the notes after it moved up by five.
- **Not covered yet:** colour science in depth, smoke and fog, light passing through skin, generating content procedurally, VR and AR, video compression, and drawing text and fonts.
