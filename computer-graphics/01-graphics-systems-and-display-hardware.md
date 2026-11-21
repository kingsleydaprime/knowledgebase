---
id: d6395cf5-aa05-429b-90e7-db03d00eabfc
---

# Graphics Systems and Display Hardware

Computer graphics is the field of making a computer create, store, change and display pictures on a screen, using programming.

## Computer graphics is about interaction
<!-- bite: 43fede41-0eeb-49fe-a45c-eff7c9de36a4 -->

Underneath, a screen is just a grid of tiny dots called pixels. Every picture you’ve ever seen on a computer, whether a photo, a game, an app button or a 3D model, is the computer deciding which pixels to light up and in what colour. Computer graphics is the set of methods for making that decision correctly and quickly.

Computer graphics is about interaction. It’s about systems that help people solve problems visually. When you drag a window, rotate a 3D model or draw in an app, you act and the picture responds immediately, again and again. That continuous back-and-forth is what separates graphics from just “a program that outputs an image.”

Here’s an example. Say you want to draw a diagonal line on the screen. The screen is a grid, so a true diagonal can’t exist. The computer has to pick which pixels come closest to it. Much of this course is about how to make that kind of choice, whether for lines, circles, shapes, curves or 3D objects, and how to move and resize them (transformations).

A one-sentence version for an exam: Computer graphics involves creating, storing, changing and displaying pictures on a computer screen with the help of programming, as a tool for interactive visual problem solving.

It could also be read as: computer graphics is a set of interactive techniques that help people comprehend, conceive and communicate using pictures.

## Visual problem solving
<!-- bite: 7778fe23-6e00-4726-ba6e-8c7a7d9c7e64 -->

Now when we hear visual problem solving, it can make you go like ehn?

But it’s not that deep sha…

A visual problem is any problem where you have to see something to deal with it: a scan, a plan, a map, a diagram, a replay of a game. Visual problem solving is the human ability to handle these problems using sight. So visual problem solving could mean all the visual aspects of human intelligence.

Visual problem solving has 3 parts…

1. Comprehend: Take in the incoming information.
2. Conceive: Come up with a solution to the problem
3. Communicate: Pass the idea on to other people

Take an architect designing a building…

**Comprehend:** She looks at the site, the client’s requirements and the existing drawings. She’s taking in information visually.

**Conceive:** She works out a design, sketching it, then building a 3D model on the computer to test ideas.

**Communicate:** She shows the client a walk-through of the model so they can see what she means, without needing to read a spec.

How does computer graphics enter? It enters because it gives people tools to do that job faster and better.

Looking at the example above, at every step, a picture is doing the thinking. Computer graphics makes those pictures quick to produce, easy to change and pleasant to work with.

## Command based computing and interactive computing
<!-- bite: 83745d06-bae4-4634-9261-f203de19baff -->

Okay!!!!!

So how does computer help in visual problem solving? Well the answer is that it depends on “how” the computer works with you. Does it continuously work alongside you or you give a command and it gets you an answer.

What I mean is that the computer can help in 2 different ways

**1. Command based computing (the old way)**

You give the computer a command. It does the task. Then you see the result. Then you act again. It works in turns: user, computer, user, computer. Only one side is busy at a time, and you only get feedback after the task finishes.

Example: type a command in a terminal, wait, then read the output.

**2. Interactive computing (the way graphics works)**

Here both sides are active at the same time. You are continuously working, and the computer is continuously responding. The feedback never stops.

Example: you drag a shape across the screen and watch it follow your hand as you move.

Remember that visual problem solving is not one step. It is a loop: look, try an idea, see the result, adjust, look again. Imagine the architect typing “move wall 2 meters left”, waiting, then reading the new drawing. Every try costs a full turn, so she cannot think as fast as she sees. But if she drags the wall and the model updates “as she drags”, the tool keeps up with her thinking.

So command-based computing can produce pictures, but it cannot support the loop. Interactive computing can. That is why computer graphics belongs to the interactive side.

Augmentation is the name for what interactive computing does. The computer does not just carry out your orders. It extends what you can do, like a tool that becomes part of how you work. You are not giving orders to a machine anymore. You are working with it, and both of you are active at once.

And this is why graphics cares so much about speed. If the picture cannot be redrawn fast enough, the loop breaks and the tool feels laggy. That is what leads us into display hardware and refresh rate.

GUI is the most familiar example of interactive computing. We use it all day.

A GUI turns using a computer into visual problem solving. Every time you use a phone or laptop, you are solving a small visual problem: finding the right icon, picking a menu item, dragging a window. So the thing we said graphics helps with (comprehend, conceive, communicate) is already happening every time you click.

## GUI (Graphical User Interface)
<!-- bite: d0557f2e-0cd7-4081-803b-ac2dea01af59 -->

Think about what you do when you use your phone. You scan for the right icon, pick an option from a menu, drag something somewhere. Every one of those is a small visual problem. That is exactly what a GUI is: windows, icons, menus and so on, which turn computer use into visual problem solving.

And because it is interactive (you act, the screen responds, continuously), the GUI is the everyday example of augmentation we talked about.

But GUIs can still be improved. The notes list five areas where work has been done:

1. Scrolling interfaces: making it easier to move through large documents
2. Manipulation of desktop icons: better ways to move, arrange and organise icons and files.
3. Pointing by mouse cursor: making the cursor faster and more accurate at reaching small or distant targets
4. Handling of digital ink: working with pen or stylus input (handwriting, sketches) so the computer treats it as useful content and not just a picture
5. Voice interaction techniques: using speech or other sounds to control the computer

**Example: scrolling (speed-dependent automatic zooming)**

Navigating a large document is hard. At a fixed zoom, if you scroll fast the text blurs past too quickly to follow, and you lose your place. The fix: the faster you scroll, the more the view zooms out automatically, so you can see more and keep track of where you are. When you slow down or stop, it zooms back in so you can read.

## Five areas of improvement in GUI operations
<!-- bite: 37b416b3-fdbb-4bcc-b180-1feec73c3483 -->

| # | Area | Short description |
|---|---|---|
| 1 | Scrolling interfaces | Making it easier to move through large documents, for example by zooming out automatically when you scroll fast so you do not lose your place |
| 2 | Manipulation of desktop icons | Better ways to move, arrange and organise the icons and files on the screen |
| 3 | Pointing by mouse cursor | Making the cursor faster and more accurate at reaching small or distant targets |
| 4 | Handling of digital ink | Working with pen or stylus input, such as handwriting and sketches, so the computer treats it as useful content and not just a picture |
| 5 | Techniques for voice interaction | Using speech or other sounds from the voice to control the computer |

Some work has already been done to improve each of these areas.

### Scroll interface: speed dependent automatic zooming

The work is called speed dependent automatic zooming for browsing large documents.

- **The problem:** navigating a large document is difficult.
- **The idea:** the faster you scroll, the more the view zooms out automatically, so you can see more of the document and keep track of where you are. When you slow down or stop, it zooms back in so you can read.
- **Why it helps:** at a fixed zoom level, fast scrolling makes the text blur past too quickly to follow. Zooming out keeps the apparent speed manageable.

## 4. Display hardware: CRT, raster scan and random scan
<!-- bite: 74cc2562-c350-4338-9e6c-7400118c21e8 -->

**DISPLAY HARDWARE AND REFRESH RATE**

We’ve already said that computer graphics is about drawing on a screen…

Before we draw anything, we need to know what we’re drawing on. Remember the feedback loop from lesson 1? The screen is the computer’s half of it.

### CRT

The video monitor is the primary output device of a graphics system. The classic monitor uses a cathode ray tube (CRT). Today’s screens are LCD or LED, but the same ideas carry over: pixels, a frame buffer, and refreshing.

### How a CRT works

1. An electron gun fires a beam of electrons (the cathode ray)
2. The beam passes through focusing and deflection systems, which aim it at specific positions on the phosphor-coated screen.
3. Where the beam hits, the phosphor glows, giving a small spot of light.
4. The glow fades very quickly, so the picture must be redrawn again and again. That is refreshing.

## WAYS OF DRAWING A PICTURE
<!-- bite: 71cffd38-3008-40fa-9fdd-023256c47bf6 -->

There are two ways of drawing pictures on a screen.

1. **Raster scan:** The beam sweeps the whole screen, one row at a time, top to bottom. As it moves along a row, its intensity is switched on and off to make a pattern of lit spots.
    - The picture is stored in the frame buffer (also called the refresh buffer): an intensity value for every screen point
    - Each screen point is a pixel
    - After each row the beam returns to the start of the next row (horizontal retrace). After the last row it returns to the top (vertical retrace). The beam is off during a retrace.
2. **Random scan (vector scan).** The beam goes only where the picture is. It is also called a vector display, stroke-writing display or calligraphic display.
    - The picture is stored as a list of line-drawing commands in the display file (refresh display file).
    - The system cycles through the list and draws each line in turn.
    - It can redraw 30 to 60 times a second

| | Raster scan | Random scan |
|---|---|---|
| **Stored** | Intensity for every pixel | List of line commands |
| **Beam** | Sweeps whole screen | Follows only the lines |
| **Good at** | Filled areas, colour, shading, realistic images | Sharp, smooth lines |
| **Weak at** | Jagged lines (staircase effect) | Filled areas, shading; many lines means slow cycle and flicker |
| **Used today** | Almost every screen | Old vector and CAD displays |

Remember this one: because raster screens are grids, a diagonal line has to be approximated with pixels. That is exactly why DDA and Bresenham exist, and we’ll reach them soon.

## RASTER BASICS
<!-- bite: 039af8fa-6455-4ce8-85f0-2f91b0a56d29 -->

Things we should know…

1. The screen is a 2D array of pixels. In OpenGL the origin (0,0) is the lower-left corner. Upper-left is another common convention.
2. With N bits per pixel, a pixel can show 2^N intensities of colors.
3. In greyscale, there’s only one byte per pixel. 1 byte = 8 bits. So total intensities of colors is 2^8 = 256 shades. For colour, it’s 3 bytes per pixel (RGB). That is 2^24 shades
4. Two primitive (most basic) operations: setpixel(x,y,color): go to the pixel at column x, row y, and put this color there. This is the write operation. getpixel(x,y): look at the pixel at (x,y) and tell me what color it is right now. This is the read operation
5. Scan conversion is turning lines, circles and polygons into pixels. It is usually an approximation, because the grid is discrete.

## Applications
<!-- bite: 6f98b5d0-4d16-4251-9a1e-926d1f6cfe67 -->

1. **Entertainment** — video games, animated films, visual effects.
2. **Design (CAD/CAM)** — engineering, architectural and product design, with models you can rotate and inspect.
3. **User interfaces** — windows, icons and menus on computers and phones.
4. **Medical and scientific visualisation** — CT and MRI scans shown as 3D images, molecular models, weather and flow simulation.
5. **Simulation and training** — flight and driving simulators, surgical practice.
6. **Virtual and augmented reality.**
7. **Data visualisation** — charts, dashboards, maps (GIS).
8. **Education, art and advertising** — diagrams, digital art, presentations.

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

## About this lesson
<!-- bite: 5feac66d-ed2f-4350-b7dc-2bbcf62fdcbf -->

**Level:** Beginner → Intermediate. **Covers:** what computer graphics is for, why it is interactive, and the hardware the picture ends up on: the CRT, raster and random scan, the frame buffer, refresh rate, and bitmap versus vector images.

**Where it sits:** the first lesson of the course. Part 1 (lessons 01–07) teaches how a computer draws lines, circles and shapes out of pixels, by hand, the way a university course such as SSG 511 teaches it. Part 2 (lessons 08–16) is how modern 3D pictures are made. Read 01 to 07 in order, then Part 2.

**Source:** SSG 511 lecture and study notes, cross-checked against standard textbook treatments.

**Before you start:** You need nothing beyond school maths: coordinates, multiplication, and the idea of a grid.

**After this note you will be able to:**
1. Define computer graphics and explain "visual problem solving" with its three parts.
2. Explain how a CRT draws a picture, and compare raster scan with random scan.
3. Work out frame-buffer size and pixel rate for a given resolution and refresh rate.
4. Say when a bitmap is the right representation and when a vector one is.
