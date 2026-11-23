---
id: d6395cf5-aa05-429b-90e7-db03d00eabfc
---

# Introduction to Computer Graphics

Computer graphics is the field of making a computer create, store, change and display pictures on a screen, using programming.

## What computer graphics is
<!-- bite: 43fede41-0eeb-49fe-a45c-eff7c9de36a4 -->

Underneath, a screen is just a grid of tiny dots called pixels. Every picture you’ve ever seen on a computer, whether a photo, a game, an app button or a 3D model, is the computer deciding which pixels to light up and in what colour. Computer graphics is the set of methods for making that decision correctly and quickly.

## Computer graphics is about interaction
<!-- bite: 2f7ee6f9-0cd9-4db7-9603-de9b2f1604b2 -->

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

## Visual problem solving: the architect example
<!-- bite: dcd7c114-16b0-4b35-9f41-9a1220cc8bfe -->

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

## Interactive computing (the way graphics works)
<!-- bite: 6aed0e6d-e361-45ed-922e-f93b97b250bc -->

**2. Interactive computing**

Here both sides are active at the same time. You are continuously working, and the computer is continuously responding. The feedback never stops.

Example: you drag a shape across the screen and watch it follow your hand as you move.

## Why graphics belongs to the interactive side
<!-- bite: 6ce8e6f3-247d-4cd2-bc81-c1f3f0122528 -->

Remember that visual problem solving is not one step. It is a loop: look, try an idea, see the result, adjust, look again. Imagine the architect typing “move wall 2 meters left”, waiting, then reading the new drawing. Every try costs a full turn, so she cannot think as fast as she sees. But if she drags the wall and the model updates “as she drags”, the tool keeps up with her thinking.

So command-based computing can produce pictures, but it cannot support the loop. Interactive computing can. That is why computer graphics belongs to the interactive side.

## Augmentation
<!-- bite: 36fa5817-ae9c-4865-aea0-b104da21c101 -->

Augmentation is the name for what interactive computing does. The computer does not just carry out your orders. It extends what you can do, like a tool that becomes part of how you work. You are not giving orders to a machine anymore. You are working with it, and both of you are active at once.

And this is why graphics cares so much about speed. If the picture cannot be redrawn fast enough, the loop breaks and the tool feels laggy. That is what leads us into display hardware and refresh rate.

GUI is the most familiar example of interactive computing. We use it all day.

A GUI turns using a computer into visual problem solving. Every time you use a phone or laptop, you are solving a small visual problem: finding the right icon, picking a menu item, dragging a window. So the thing we said graphics helps with (comprehend, conceive, communicate) is already happening every time you click.

## GUI (Graphical User Interface)
<!-- bite: d0557f2e-0cd7-4081-803b-ac2dea01af59 -->

Think about what you do when you use your phone. You scan for the right icon, pick an option from a menu, drag something somewhere. Every one of those is a small visual problem. That is exactly what a GUI is: windows, icons, menus and so on, which turn computer use into visual problem solving.

And because it is interactive (you act, the screen responds, continuously), the GUI is the everyday example of augmentation we talked about.

## Where GUIs can still be improved
<!-- bite: ff9050ce-5cfc-4b4c-9395-66be5f329382 -->

But GUIs can still be improved. The notes list five areas where work has been done:

1. Scrolling interfaces: making it easier to move through large documents
2. Manipulation of desktop icons: better ways to move, arrange and organise icons and files.
3. Pointing by mouse cursor: making the cursor faster and more accurate at reaching small or distant targets
4. Handling of digital ink: working with pen or stylus input (handwriting, sketches) so the computer treats it as useful content and not just a picture
5. Voice interaction techniques: using speech or other sounds to control the computer

## Example: scrolling (speed-dependent automatic zooming)
<!-- bite: 0bb406aa-1fa4-4b5b-a28a-9e28615f2e0b -->

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

## Scroll interface: speed dependent automatic zooming
<!-- bite: 5b87f1d5-9c53-448d-999b-c9398ca6c9dc -->

The work is called speed dependent automatic zooming for browsing large documents.

- **The problem:** navigating a large document is difficult.
- **The idea:** the faster you scroll, the more the view zooms out automatically, so you can see more of the document and keep track of where you are. When you slow down or stop, it zooms back in so you can read.
- **Why it helps:** at a fixed zoom level, fast scrolling makes the text blur past too quickly to follow. Zooming out keeps the apparent speed manageable.

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

## Common pitfalls
<!-- bite: f2f8a860-6091-43dd-9c9d-ba81d4077f8b -->

1. **"Video problem solving"** — it is *visual* problem solving.

## Check your understanding
<!-- bite: 9c6d3f09-6c46-4949-9766-f98213e70e1b -->

Try each one before you open the answer.

1. <!-- q: gap id="d2832081" answers="comprehend;conceive;communicate" -->
   Fill in the gaps. Visual problem solving has three parts: ___ (take in the information), ___ (come up with a solution) and ___ (pass the idea on to other people).

   <details><summary>Answer</summary>

   Comprehend, conceive, communicate. In the architect example, she looks at the site, designs and models the building, then shows the client a walk-through.

   </details>

2. <!-- q: mcq id="d4fe7b8d" -->
   You type a command in a terminal, wait, then read the output. Which kind of computing is that?

   - [x] Command based computing
   - [ ] Interactive computing

   <details><summary>Answer</summary>

   Command based. It works in turns, and only one side is busy at a time. In interactive computing, both you and the computer are active at once, and the feedback never stops.

   </details>

3. <!-- q: gap id="8238a3f7" answers="augmentation" -->
   Fill in the gap. When the computer extends what you can do and works alongside you, instead of just carrying out orders, it is called ___.

   <details><summary>Answer</summary>

   Augmentation. The GUI is the everyday example of it.

   </details>

4. <!-- q: mcq id="c635beb0" -->
   In speed dependent automatic zooming, what happens when you scroll fast?

   - [ ] The view zooms in so you can read
   - [x] The view zooms out so you can see more and keep your place
   - [ ] Scrolling stops until you slow down

   <details><summary>Answer</summary>

   It zooms out. At a fixed zoom, fast scrolling blurs the text past too quickly to follow. When you slow down, it zooms back in.

   </details>

5. <!-- q: mcq id="b5d26ec3" -->
   Which of these are among the five areas of improvement in GUI operations? Choose all that apply.

   - [x] Scrolling interfaces
   - [x] Pointing by mouse cursor
   - [x] Handling of digital ink
   - [ ] Faster hard drives

   <details><summary>Answer</summary>

   The first three. The other two are manipulation of desktop icons and voice interaction techniques.

   </details>

6. <!-- q: open id="7c20d2a2" -->
   Why does computer graphics belong to interactive computing rather than command based computing?

   <details><summary>Answer</summary>

   Visual problem solving is a loop: look, try an idea, see the result, adjust, look again. With commands, every try costs a full turn, so the tool can't keep up with your thinking. Interactive computing updates the picture as you act, which supports the loop.

   </details>

## Before moving on
<!-- bite: 0a6e3e8d-995e-45d6-907a-17f1de51aeff -->

You can say what computer graphics is, explain visual problem solving and its three parts, and say why graphics belongs to interactive computing. **Next:** [[computer-graphics/02-graphics-systems-and-display-hardware|Graphics Systems and Display Hardware]]: before we draw anything, we need to know what we're drawing on.

## Related
<!-- bite: 4b992d2a-5a4a-4f4f-9fc4-ff6802b4c796 -->

- [[computer-graphics/index|Computer graphics map]]

## About this lesson
<!-- bite: de2d6723-cb1b-4088-8a3d-594261452b32 -->

**Level:** Beginner. **Covers:** what computer graphics is, why it is about interaction, visual problem solving (comprehend, conceive, communicate), command-based versus interactive computing, augmentation, and the GUI.

**Where it sits:** the first lesson of the course. Part 1 (lessons 01–08) teaches how a computer draws lines, circles and shapes out of pixels, by hand, the way a university course such as SSG 511 teaches it. Part 2 (lessons 09–17) is how modern 3D pictures are made. Read 01 to 08 in order, then Part 2.

**Source:** the author's own SSG 511 notes.

**Before you start:** nothing beyond using a phone or laptop.

**After this lesson you will be able to:**
1. Define computer graphics and explain "visual problem solving" with its three parts.
2. Explain the difference between command-based and interactive computing, and why graphics needs the second.
