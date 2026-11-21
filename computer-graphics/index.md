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

Read 01 → 02 → 03 → 04 in order. After that, 05 to 08 can be read in any order.

1. [[computer-graphics/01-introduction-to-computer-graphics|Introduction to Computer Graphics]]: what computer graphics is, why it is about interaction, and visual problem solving.
2. [[computer-graphics/02-graphics-systems-and-display-hardware|Graphics Systems and Display Hardware]]: how a screen draws a picture line by line, and how much memory a picture needs.
3. [[computer-graphics/03-line-drawing-and-antialiasing|Line Drawing and Antialiasing]]: how a computer draws a straight line out of square pixels, and how to make it look less jagged.
4. [[computer-graphics/04-circles-and-polygon-filling|Circles and Polygon Filling]]: drawing circles and ellipses, and colouring in the inside of a shape.
5. [[computer-graphics/05-clipping|Clipping]]: cutting off the parts of a drawing that fall outside the window you're looking through.
6. [[computer-graphics/06-2d-and-3d-transformations|2D and 3D Transformations]]: moving, turning and resizing shapes with matrices.
7. [[computer-graphics/07-curves-bezier-and-b-splines|Curves: Bézier and B-splines]]: drawing smooth curves, like the pen tool in a design app, from a few control points.
8. [[computer-graphics/08-visible-surface-detection|Visible Surface Detection]]: working out which objects are in front, so hidden ones aren't drawn.

### Part 2: How modern 3D pictures are made

10 to 14 build on each other, so read them in order. 15 stands on its own. 16 and 17 are about shapes and movement.

9. [[computer-graphics/09-how-rendering-works|How Rendering Works]]: the two ways to turn a 3D scene into a flat picture, and the one equation both are trying to solve.
10. [[computer-graphics/10-the-transform-pipeline|The Transform Pipeline]]: the steps that carry a 3D object from where it sits in the world to a spot on your screen.
11. [[computer-graphics/11-rasterisation|Rasterisation]]: how a graphics card fills in triangles pixel by pixel, and keeps track of what's in front.
12. [[computer-graphics/12-shading-and-lighting|Shading and Lighting]]: how light and materials decide each pixel's colour, so metal looks like metal and wood like wood.
13. [[computer-graphics/13-textures-and-sampling|Textures and Sampling]]: wrapping images around 3D shapes, and keeping them sharp but not shimmering.
14. [[computer-graphics/14-the-gpu-graphics-pipeline|The GPU Graphics Pipeline]]: how a graphics card is programmed, and which tools to learn it with.
15. [[computer-graphics/15-ray-tracing-and-path-tracing|Ray Tracing and Path Tracing]]: following rays of light around a scene, the way films get realistic lighting.
16. [[computer-graphics/16-geometry-and-meshes|Geometry and Meshes]]: how 3D shapes are stored as many small triangles, and other ways to describe them.
17. [[computer-graphics/17-animation-and-simulation|Animation and Simulation]]: making things move: turning smoothly, bending characters, and simple physics.

### Exam support (SSG 511)

20. [[computer-graphics/20-ssg-511-question-bank|SSG 511 Question Bank]]: the exam paper and every assignment question, without answers, each pointing to the note that teaches it.
21. [[computer-graphics/21-comsol-ink-jet-breakup|COMSOL: Modelling Ink Jet Breakup]]: the model answer to exam question 3. It's about fluids, not graphics, so skip it unless you need it.
22. [[computer-graphics/22-ssg-511-formula-sheet|SSG 511 Formula Sheet]]: every Part 1 formula on one page.

## Practice

- [[computer-graphics/18-practice-exercises|Practice Exercises]]: twelve exercises, from colouring a shape by hand to writing a small program that draws a picture.
- [[computer-graphics/19-practice-exercises-solutions|Solutions]]: worked answers. Try first.
- [[computer-graphics/20-ssg-511-question-bank|SSG 511 Question Bank]]: Part 1's practice. Notes 03, 05 and 07 have small programs to check your answers.
- [[build-your-own-shit/22-your-own-ray-tracer|Build your own ray tracer]]: a step-by-step project. You write a program that draws a 3D scene with realistic light, from scratch.

## Key ideas to remember

Once you've read the notes, these are the points worth keeping. Each links to where it's explained.

1. **Drawing a line is a choice between two pixels at every step:** which one is closer to the true line? A computer answers that using only whole numbers, which is fast. → [[computer-graphics/03-line-drawing-and-antialiasing|02]]
2. **Always step along the longer direction of a line,** or it comes out with gaps. → [[computer-graphics/03-line-drawing-and-antialiasing|02]]
3. **In clipping, a "maybe" isn't a "yes".** When a line's codes don't rule it out, you still have to cut it and check again. → [[computer-graphics/05-clipping|04]]
4. **Moving a shape can't be done by multiplying with a 2 × 2 grid.** That's why graphics adds an extra coordinate, so moving, turning and resizing all become one multiplication. → [[computer-graphics/06-2d-and-3d-transformations|05]]
5. **A smooth curve can be split in half at any point** using a simple averaging trick, which is how computers draw curves. → [[computer-graphics/07-curves-bezier-and-b-splines|06]]
6. **There are two ways to draw a 3D scene.** Fill in triangles one at a time (fast; used by games), or follow rays of light (slow but realistic; used by films). → [[computer-graphics/09-how-rendering-works|08]]
7. **The depth buffer won because it needs no sorting.** Each pixel remembers how far away its colour came from, and a nearer object simply replaces it. → [[computer-graphics/11-rasterisation|10]]
8. **Do lighting maths before converting colours for the screen,** or the picture comes out too dark with washed-out highlights. → [[computer-graphics/12-shading-and-lighting|11]]
9. **To find out what's slowing a game down, lower the resolution.** If it doesn't get faster, the graphics card isn't the problem. → [[computer-graphics/14-the-gpu-graphics-pipeline|13]]
10. **Move physics forward in fixed steps,** not "however long the last frame took", or the simulation behaves differently on fast and slow machines. → [[computer-graphics/17-animation-and-simulation|16]]

## Where to go next

- **[*Ray Tracing in One Weekend*](https://raytracing.github.io)**: free, short, and you finish with a real picture made by your own program. The best first project in graphics.
- **[LearnOpenGL](https://learnopengl.com)**: free lessons on drawing 3D scenes with a graphics card.
- **[Shadertoy](https://shadertoy.com)**: write a small program in your browser and see the picture change instantly.
- **Books:** *Fundamentals of Computer Graphics* (Marschner and Shirley) for the basics. After that, *Physically Based Rendering* (Pharr, Jakob and Humphreys), which is free online.

## Related

- [[gpu-and-parallel-computing/index|GPU and Parallel Computing]]: graphics cards were invented for this work.
- [[mathematics/07-applied-and-computational/01-numerical-methods/index|Numerical Methods]]: the maths behind curves and light calculations.
- [[ai-ml/02-ml-engineer/06-computer-vision/index|Computer Vision]]: the reverse problem, getting a scene back from a picture.

---

## About this course

- **Size:** 21 notes, about 40,000 words, including practice, solutions, a question bank and a formula sheet.
- **History:** Part 2 (modern 3D, notes 09–19) was written in August 2026. Part 1 (drawing on the screen, notes 01–08) and the exam notes (20–22) were added in November 2026 from the SSG 511 course notes, and the notes were renumbered so the beginner part comes first.
- **Not covered yet:** colour science in depth, smoke and fog, light passing through skin, generating content procedurally, VR and AR, video compression, and drawing text and fonts.
