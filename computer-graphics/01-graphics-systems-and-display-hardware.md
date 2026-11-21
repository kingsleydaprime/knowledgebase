---
id: d6395cf5-aa05-429b-90e7-db03d00eabfc
---

# Graphics Systems and Display Hardware

**[Beginner → Intermediate]** — What computer graphics is for, why it is *interactive*, and the hardware the picture ends up on: the CRT, raster and random scan, the frame buffer, refresh rate, and bitmap versus vector images.

> **The first note of the course.** Part 1 (notes 01–07) teaches how a computer draws lines, circles and shapes out of pixels, by hand, the way a university course such as SSG 511 teaches it. Part 2 (notes 08–16) is how modern 3D pictures are made. **If you're new to this, you're in the right place: read 01 to 07 in order, then Part 2.** Source: SSG 511 lecture and study notes, cross-checked against standard textbook treatments.

## Before you start
<!-- bite: ec52d859-5062-48c8-9326-d5d88d51fb61 -->

You need nothing beyond school maths: coordinates, multiplication, and the idea of a grid.

**After this note you will be able to:**
1. Define computer graphics and explain "visual problem solving" with its three parts.
2. Explain how a CRT draws a picture, and compare raster scan with random scan.
3. Work out frame-buffer size and pixel rate for a given resolution and refresh rate.
4. Say when a bitmap is the right representation and when a vector one is.

## The kid version
<!-- bite: 2627f6c9-69aa-4c63-aef9-4cd9be2092bf -->

Imagine a huge wall of tiny light bulbs, each one able to glow any colour. To show a picture, someone has to tell every bulb what colour to be, and they have to keep telling them many times a second, because the bulbs fade. **Computer graphics is the job of deciding what every bulb should show.**

There are two ways a screen can go round the wall lighting bulbs:

1. **Like reading a page of a book.** Start at the top-left bulb and go along the row, setting every bulb to its colour. Then drop to the next row, and so on to the bottom. Then go back to the top and start again. Every bulb gets visited every time, even the ones that stay dark. This is called a **raster** screen, and almost every screen today, including your phone and laptop, works this way.
2. **Like drawing with a pen.** If the picture is a triangle, trace just its three edges and skip the rest of the wall entirely. Old screens called **vector** screens worked like this. They drew sharp, clean lines, but filling in a solid shape meant scribbling over all of it. And the more lines in the picture, the longer each trip round took, until the first lines faded before the last were drawn and the picture flickered.

**Where the analogy stops working.** Modern LCD and LED panels do not fade like the old CRT phosphor: each pixel holds its colour until it is told to change. The "keep telling them" part survives as the refresh rate, but for a different reason (showing *new* pictures, not stopping the old one from vanishing).

## Terms used in display hardware
<!-- bite: b9ceedca-cb4b-4e38-a6db-5081fc58832a -->

1. **Computer graphics**: This is the creating, storing, changing and displaying of pictures on a computer screen with the help of programming. At the lowest level it means deciding which pixels to light up and in what colour.
2. **Pixel**: This is also known as a **picture element**. This is one point of the screen's grid, the smallest thing the display can colour.
3. **Frame buffer**: This is also known as the **refresh buffer**, an **image map** or a **bitmap**. This is the block of memory that holds one colour (intensity) value for every pixel on the screen.
4. **Scan conversion**: This is the process of turning a geometric object such as a line, circle or polygon into the set of pixels that approximates it. It is nearly always an approximation, because the frame buffer is a discrete grid.
5. **Refresh rate**: This is the number of times per second the display redraws the whole picture, measured in hertz (Hz). 60 Hz means sixty redraws a second.
6. **Frame rate**: This is how many new pictures per second the program produces, measured in frames per second (FPS).
7. **Retrace**: This is the return of the electron beam to the start of the next row (horizontal retrace) or to the top of the screen (vertical retrace). The beam is switched off while it retraces.
8. **Display file**: This is also known as the **refresh display file**. This is the list of line-drawing commands a random-scan display cycles through to draw its picture.

## 1. What computer graphics is for
<!-- bite: f0a182bd-fcf6-401d-a100-6106fc1b5b4b -->

**Computer graphics is about interaction — interactive techniques and systems for visual problem solving.**

"Visual problem solving" means all the visual sides of human intelligence, and it has three parts. Take a surgeon:

1. **Comprehend** — take in the incoming information. *The surgeon studies the patient's scans.*
2. **Conceive** — come up with a solution. *The surgeon plans the operation.*
3. **Communicate** — pass the idea on to others. *The surgeon explains the plan to the team.*

Other intensive visual problem solvers: coaches teaching a sport with diagrams and replays, and architects designing buildings with drawings, 3D models and walkthroughs.

**The goal of the field is to make those processes more efficient, more productive and more pleasant**, using computer techniques that lean on interactive computing.

### Applications

1. **Entertainment** — video games, animated films, visual effects.
2. **Design (CAD/CAM)** — engineering, architectural and product design, with models you can rotate and inspect.
3. **User interfaces** — windows, icons and menus on computers and phones.
4. **Medical and scientific visualisation** — CT and MRI scans shown as 3D images, molecular models, weather and flow simulation.
5. **Simulation and training** — flight and driving simulators, surgical practice.
6. **Virtual and augmented reality.**
7. **Data visualisation** — charts, dashboards, maps (GIS).
8. **Education, art and advertising** — diagrams, digital art, presentations.

## 2. Interactive computing
<!-- bite: cb731513-8dd8-4295-a46f-6c479b3bf3a6 -->

There are two styles of computing, and graphics belongs to the second.

**Command-based (old style).** The user gives a command, the system does the task, then the user sees the result. **Turns are taken: only one side is active at a time.** Typing a command in a terminal and waiting for output is the example.

**Interactive computing (augmentation).** The user works on a program continuously and the system gives feedback continuously. **Both sides are active at once.** Dragging a shape and watching it follow your hand is the example.

| | Command based | Interactive (augmentation) |
|---|---|---|
| Who is active | One at a time, taking turns | Both at once |
| Feedback | Only after the task finishes | Continuous |
| Feels like | Giving orders | A tool that extends you |
| Example | Type, wait, read | Drawing, dragging, rotating a model |

In the usual diagram, the command-style user bar rises and falls as turns alternate; the interactive one has both bars running the full length, with arrows both ways between them. **Those arrows are the feedback loop.**

**"Augmentation" means the computer does not just carry out orders — it extends what you can do**, like a tool that becomes part of how you work.

> **Why this matters for graphics.** The screen is the computer's half of the feedback loop. Every time you rotate a model or paint a stroke, the picture must be redrawn fast enough to feel instant. **That is why refresh rate and display hardware are on the syllabus at all.**

## 3. The graphical user interface
<!-- bite: 0adb4af1-6fdb-4be0-8150-068022eaebe4 -->

A graphical user interface (GUI) — windows, icons, menus — **turns using a computer into visual problem solving**: finding the right icon, picking a menu item, dragging a window.

**Five areas of improvement in GUI operations** (areas of research, each with some work already done):

1. **Scrolling interfaces** — making it easier to move through large documents.
2. **Manipulation of desktop icons** — better ways to move, arrange and organise icons and files.
3. **Pointing by mouse cursor** — reaching small or distant targets faster and more accurately.
4. **Handling of digital ink** — treating pen and stylus input (handwriting, sketches) as useful content, not just a picture.
5. **Techniques for voice interaction** — controlling the computer with speech or other vocal sounds.

> Rows 2 to 5 were written from the slide titles; only row 1 is backed by detailed lecture text. **Check them against the lecturer's slides before an exam.**

### Scroll interfaces: speed-dependent automatic zooming

**The problem:** navigating a large document is hard. **The idea:** the faster you scroll, the more the view zooms out automatically, so you see more of the document and keep your place; slow down and it zooms back in so you can read. **Why it helps:** at fixed zoom, fast scrolling makes the text blur past too quickly to follow — zooming out keeps the *apparent* speed manageable.

## 4. The cathode ray tube
<!-- bite: 1f664dd4-b66e-4efc-8c04-c99d5c327155 -->

The primary output device of a graphics system is the **video monitor**, and the classic monitor's main element is the **cathode ray tube (CRT)**. Today's screens are LCD or LED, but the ideas carry over: pixels, a frame buffer, refreshing.

**How a CRT draws:**

1. An **electron gun** emits a beam of electrons (the cathode ray).
2. **Focusing and deflection systems** steer the beam to chosen positions on the phosphor-coated screen.
3. Where the beam hits, the **phosphor emits a small spot of light**.
4. **The glow fades very quickly**, so the picture must be redrawn again and again — *refreshing*.

## 5. Raster scan versus random scan
<!-- bite: ca795426-a208-4248-a75a-99e4e0dc476c -->

A CRT has one beam, so it has to move that beam around the screen to build the whole picture. There are two ways to move it. These are the "reading a page" and "drawing with a pen" pictures from the kid version.

**Raster scan.** The beam sweeps the whole screen one row at a time, top to bottom, switching intensity on and off to make a pattern of spots.

- The picture lives in the **frame buffer** as an intensity value for every screen point.
- The values are read back and "painted" one row at a time.
- After each row, the beam switches off and jumps back to the left edge of the next row, like moving to the start of the next line when you read. This jump is the **horizontal retrace**. After the last row it jumps back to the top-left corner: the **vertical retrace**.

**Random scan.** Also called a **vector display**, **stroke-writing display** or **calligraphic display**. The beam goes **only where the picture is**, instead of scanning everything.

- The picture lives in the **display file** as line-drawing commands.
- The system cycles through the commands, drawing each line in turn.
- It typically redraws the picture **30 to 60 times a second** — that figure is its refresh rate.

**The same triangle on both.** A raster screen sweeps every one of its points, row by row, and lights only the points that fall on the triangle's edges. That's around 2 million points on a modern screen, for three lines. A random-scan screen moves the beam along the three edges and nothing else. That's why random scan drew line pictures so cleanly, and why it couldn't keep up once a picture had thousands of lines or large filled areas.

| | Raster scan | Random scan |
|---|---|---|
| Stored | Intensity per pixel (frame buffer) | Line commands (display file) |
| Beam | Sweeps every row | Follows the picture's lines |
| Good at | Filled areas, colour, shading, realistic images | Sharp, smooth line drawings |
| Weak at | Jagged diagonal lines (the staircase effect) | Filled areas; many lines slow the cycle and it flickers |
| Today | Almost every screen | Old vector and CAD displays |

> **The raster weakness is the reason half of Part 1 exists.** A diagonal line on a grid of dots has to be approximated by pixels — which is exactly why DDA and Bresenham exist ([[computer-graphics/02-line-drawing-and-antialiasing|note 02]]), and why antialiasing exists.

### Raster basics

- The screen is a **2D array of pixels**. OpenGL puts the origin **(0, 0) at the lower left**; upper left is the other common convention. *State which one you use.*
- With **N bits per pixel**, each pixel can show one of $2^N$ intensities or colours.
- Greyscale usually uses one byte per pixel: $2^8 = 256$ levels. Colour usually uses one byte per channel for red, green and blue: 3 bytes (24 bits) per pixel.
- The two primitive operations are **`setpixel(x, y, color)`** and **`getpixel(x, y)`**. Every algorithm in Part 1 is built on them.

**Frame-buffer size is width times height times bits per pixel.**

$$\text{size} = W \times H \times \text{bpp}$$

**Worked:** $1920 \times 1080$ at 24 bpp is $2{,}073{,}600$ pixels $\times$ 3 bytes $= 6{,}220{,}800$ bytes, about **6.2 MB**.

## 6. Refresh rate
<!-- bite: 7df7517f-6cca-459e-9299-7abe0bde7666 -->

**Why refreshing is needed on a CRT:** the phosphor glows only briefly. Unless each spot is redrawn again and again, the picture fades and flickers. **Redrawn fast enough — roughly 50–60 times a second or more — the eye sees a steady image.**

**Raster scan:** every cycle, the hardware reads the *entire* frame buffer and paints it, even if nothing changed. **The pixel rate is pixels per frame times the refresh rate**: $1920 \times 1080 \times 60 \approx 124$ million pixels per second.

**Random scan:** every cycle redraws every line. **More lines means a longer cycle, so the refresh rate drops and the picture flickers** — which is why random scan cannot handle complex pictures.

**Interlaced versus non-interlaced.** Older CRTs and TVs drew odd lines on one pass and even lines on the next, so two passes make one frame. That reduces visible flicker without sending the whole picture each pass. **Non-interlaced (progressive)** scan draws every line in order on every pass.

**Modern LCD and LED panels** have no beam and no fading phosphor: a pixel holds its state until changed. **Refresh rate now means how often the panel can update what it shows.** Common values: 60, 120, 144, 240 Hz.

**The time between refreshes is 1000 divided by the refresh rate, in milliseconds.**

| Refresh rate | 30 Hz | 60 Hz | 120 Hz | 144 Hz | 240 Hz |
|---|---|---|---|---|---|
| Time between refreshes | 33.3 ms | 16.7 ms | 8.3 ms | 6.9 ms | 4.2 ms |

### Refresh rate is not frame rate

- **Refresh rate** (Hz) is what the *display* can do.
- **Frame rate** (FPS) is what the *computer* produces.
- A 60 Hz screen shows at most 60 different pictures a second. **Render 120 FPS on it and the extra frames are never all shown; render 30 FPS and each picture is shown for two refreshes.**

### Double buffering and tearing

If the program writes into the frame buffer *while* the display is reading it, the screen can show the top of the old picture and the bottom of the new one — **tearing**. **The fix is double buffering:** draw the next frame into a hidden **back buffer**, then swap it with the **front buffer** (the one on screen), ideally during vertical retrace — **V-sync**. OpenGL programs commonly use double buffering. → [[computer-graphics/13-the-gpu-graphics-pipeline|The GPU pipeline]] for the modern swap chain.

> **Back to interactive computing.** The delay between your action and the picture changing (latency) depends partly on refresh rate: at most one new picture every 16.7 ms at 60 Hz, every 6.9 ms at 144 Hz. **A low refresh rate makes dragging and drawing feel laggy, which breaks the feedback loop.**

## 7. Bitmap and vector graphics
<!-- bite: 2aeda7b3-a10f-4fe2-aa93-1df283a9e616 -->

**A bitmap is not an algorithm — it is a way of *storing* an image**, and it is the opposite of vector graphics.

**Bitmap (raster) graphics** store the picture as a grid, with a colour (for example RGB values) for every pixel. Used for photographs. **The frame buffer is a bitmap.**

**Vector graphics** store the *shapes* — lines, curves, polygons, with their coordinates, colours and widths — and draw the picture from those instructions. **Random-scan displays worked this way.**

| | Bitmap (raster) | Vector |
|---|---|---|
| Stored as | Grid of pixel colours | List of shapes and coordinates |
| Resizing | Enlarging goes blurry or blocky | Scales cleanly to any size |
| File size | Grows with $W \times H \times$ bpp | Grows with number of shapes |
| Best for | Photographs, realistic images | Logos, diagrams, fonts, technical drawings |
| Formats | BMP, PNG, JPEG | SVG; the shapes inside PDF files |

**Disadvantages of bitmaps:**
1. **They cannot be resized without losing quality.** Enlarging either magnifies pixels into blocks or forces the computer to guess new values (interpolation), which looks blurry. Shrinking throws detail away.
2. **Colour bitmaps are large.** 1920 × 1080 at 24 bpp is about 6.2 MB uncompressed; PNG and JPEG compression reduce that.

**Terminology:** strictly, a **bitmap** has 1 bit per pixel (black or white), and an image with more bits per pixel is a **pixmap**. In everyday use "bitmap" covers both.

## Common pitfalls
<!-- bite: ca212338-6671-48bb-a1bf-c564cedc6ca0 -->

1. **Mixing up refresh rate and frame rate.** One is the display, the other the program.
2. **Forgetting bits versus bytes** in frame-buffer sums. 24 bits per pixel is 3 bytes.
3. **Calling a bitmap a drawing or clipping algorithm.** It is a data representation.
4. **"Video problem solving"** — it is *visual* problem solving.

## Check your understanding
<!-- bite: f25a22c9-33e9-483f-85a7-3a9a47771140 -->

1. A random-scan display is drawing a CAD model, and the designer adds thousands more lines. What happens to the picture, and why?
2. How much memory does a 2560 × 1440 frame buffer need at 32 bits per pixel? At 8 bits?
3. A game renders at 90 FPS on a 60 Hz monitor without V-sync. What artefact might you see, and what fixes it?
4. Why would you store a company logo as a vector image but a holiday photo as a bitmap?

<details><summary>Answers (after your attempt)</summary>

1. Each refresh cycle must redraw every line, so the cycle gets longer, the refresh rate falls, and the picture flickers.
2. $2560 \times 1440 = 3{,}686{,}400$ pixels. At 4 bytes that is 14,745,600 bytes ≈ 14.7 MB; at 1 byte, ≈ 3.7 MB.
3. Tearing — the buffer is overwritten mid-scan. Double buffering with the swap during vertical retrace (V-sync).
4. The logo must scale cleanly to any size and is made of a few shapes; the photo has continuous detail that no small list of shapes describes.

</details>

## Practice
<!-- bite: e51f7236-a4fe-4152-9a79-e4fe255ea709 -->

Write `framebuffer_size(w, h, bpp)` and `pixel_rate(w, h, hz)` in Python. **Done when** they reproduce 6,220,800 bytes and ≈124 million pixels/s for 1080p at 24 bpp and 60 Hz, and you can explain each factor out loud.

## Before moving on
<!-- bite: c32d62a5-7f8f-4514-9d14-1b989a0a81c5 -->

You can explain visual problem solving, raster versus random scan, and why refresh exists. **Next:** [[computer-graphics/02-line-drawing-and-antialiasing|Line Drawing and Antialiasing]] — the first scan-conversion algorithm, and the raster weakness it fights.

## Related
<!-- bite: 1d0d55ca-bc13-442e-a256-df07fb5cea6c -->
- [[computer-graphics/08-how-rendering-works|How Rendering Works]] — the modern view of the same pipeline
- [[computer-graphics/13-the-gpu-graphics-pipeline|The GPU Graphics Pipeline]] — swap chains and presentation today
- [[computer-graphics/index|Computer graphics map]]
