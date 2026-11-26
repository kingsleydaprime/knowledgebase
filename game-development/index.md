# Game Development

## What game development is

**Game development is making video games: designing how they play, then writing the software that draws the world, moves things, runs the characters and responds to the player, dozens of times every second.**

What makes games special as software is the clock. To look smooth, a game must draw a new picture about 60 times a second, which gives it roughly **16 milliseconds** per frame to read the controls, move everything, work out collisions, decide what the enemies do and draw the scene. Every frame, without exception. One slow frame is a visible stutter, so in games the *worst* case is what the player feels. Most of game programming is techniques for fitting a world into that budget: faking things that look right instead of calculating them exactly, skipping anything off screen, and laying out data so the computer can process it fast.

Games pull together almost every other subject in this vault, from graphics and physics to AI, networking and maths. That's also why the skills carry over into simulation, robotics and film.

## What you'll be able to do

By the end you will be able to:
- explain what a game engine does, and choose between Unity, Unreal and Godot;
- write a game loop that runs the same on fast and slow computers;
- find out what's slowing a game down, and fix it;
- add physics and collisions that stay stable;
- write enemy behaviour that feels smart and fun;
- explain how online multiplayer hides the delay between players;
- plan a game you can actually finish.

## Where to start

**Before you start:** basic programming ([[programming-fundamentals/index|Programming Fundamentals]]) and some [[mathematics/04-linear-algebra/index|vectors]].

Read 01 and 02 first. **New to making games?** Read 08 (Getting Started) straight after 01; it's the practical path from your first tiny game upward. Notes 03–06 are the technical areas and can be read in any order. Note 07 is about how games actually get made.

1. [[game-development/01-what-game-development-actually-is|What Game Development Actually Is]]: the 16 ms budget, the different jobs in game making, the maths you actually need, and an honest picture of the industry.
2. [[game-development/02-engines-and-the-game-loop|Engines and the Game Loop]]: the loop every game runs, keeping the game the same speed on every computer, organising game objects for speed, and choosing an engine.
3. [[game-development/03-graphics-for-games|Graphics for Games]]: fitting drawing into the frame budget, skipping what can't be seen, and the many tricks that look real but aren't.
4. [[game-development/04-game-physics|Game Physics]]: detecting collisions, moving things so they stay stable, fast objects passing through walls, and when not to use a physics engine.
5. [[game-development/05-game-ai|Game AI]]: ways to program enemy behaviour, finding paths around a level, and why a perfect opponent isn't fun.
6. [[game-development/06-multiplayer-and-networking|Multiplayer and Networking]]: hiding the delay between players by predicting, smoothing and correcting, and why games use UDP.
7. [[game-development/07-tools-and-production|Tools and Production]]: getting art and levels into the game, why fast iteration matters most, and keeping the scope small.
8. [[game-development/08-getting-started|Getting Started]]: the ladder from Pong upward, game jams, and what to skip.

## Engines

The course teaches the ideas; these pages show how each engine names and does them. Start with the [[game-development/engines/index|engines overview]].

- [[game-development/engines/godot|Godot]]: free and open source, small enough to understand. The recommendation for learning.
- [[game-development/engines/unity|Unity]]: uses C#, and has the most job openings.
- [[game-development/engines/unreal|Unreal]]: uses C++ and visual scripting, with top-quality graphics included.
- [[game-development/engines/from-scratch|From scratch]]: building your own engine, layer by layer, and an honest look at whether that's really what you want to do.

## Practice

- **Do a game jam:** make one finished game in 48 hours. It tests keeping things small, finishing, and whether you enjoy it, all for the price of a weekend.
- [[game-development/projects|Projects]]: graded tasks, from Pong upward.
- [[game-development/interview/index|Game development interview prep]].

## Key ideas to remember

1. **The slowest frame is what players feel.** → [[game-development/01-what-game-development-actually-is|01]]
2. **Believable at full speed beats correct.** Game physics fakes reality rather than simulating it. → [[game-development/04-game-physics|04]]
3. **Building an engine while believing you're building a game** is the most common way an ambitious first project dies. → [[game-development/01-what-game-development-actually-is|01]]
4. **Run the game's logic in fixed time steps,** separately from drawing, so it behaves the same on every computer. → [[game-development/02-engines-and-the-game-loop|02]]
5. **Find out whether the processor or the graphics card is the bottleneck before optimising.** Guessing wrong wastes days. → [[game-development/03-graphics-for-games|03]]
6. **Don't use realistic physics for the player character.** Good controls are designed, not simulated. → [[game-development/04-game-physics|04]]
7. **Never trust the player's computer in multiplayer.** The server decides; each player's game predicts. → [[game-development/06-multiplayer-and-networking|06]]
8. **Estimate your game, then cut it to a third.** A finished Pong online beats an unfinished RPG on your laptop. → [[game-development/08-getting-started|08]]

## Related

These courses go deeper into what games use:

- [[computer-graphics/index|Computer Graphics]]: drawing 3D worlds, including [[computer-graphics/22-the-transform-pipeline|transforms]].
- [[gpu-and-parallel-computing/index|GPU and Parallel Computing]]: shaders and graphics cards.
- [[computer-architecture/index|Computer Architecture]]: why data layout makes games fast.
- [[networking/index|Networking]]: the internet underneath multiplayer.
- [[dsa/index|Data Structures and Algorithms]]: pathfinding and the trees used to find collisions quickly.
- [[robotics/04-rigid-body-transforms|Rigid Body Transforms]]: rotations in 3D.

---

## About this course

- **Size:** 8 notes, 4 engine pages and interview prep, about 12,550 words. Written in August 2026, checked against the [roadmap.sh game developer roadmap](https://roadmap.sh/game-developer).
- **Why it's short:** most of what game developers need is already taught in other courses here, so this course points to them rather than repeating them.
- **Where it came from:** reference sources. The author hasn't shipped a game or used these engines for real, so treat the industry section in note 01 as reported, not lived.
