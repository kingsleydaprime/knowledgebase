# Build Your Own

## What this section is

**Step-by-step guides for building your own simple version of tools you use every day, such as a web server, Git, a database, a shell or even a CPU, so they stop being mysterious.**

Reading about how a database works is useful. Building a small one and watching it survive being killed halfway through a save is when it really sinks in. That's what these guides are for: everywhere else in the vault is reading, and this is where reading turns into building.

Each guide works in any programming language, and follows the same plan:
1. **What you're building,** and what you're deliberately leaving out.
2. **What you need to know first,** with links to the lessons.
3. **The build order:** small steps, each of which runs and can be tested. You always have something working.
4. **Tools in each language:** what C, C++, Rust, Go, Python and JavaScript give you.
5. **What will trip you up,** said in advance so it costs you an hour, not an evening.
6. **How to know it works,** usually by checking against the real tool.
7. **Where to stop,** before a learning project turns into a never-ending one.

## Where to start

**Start with the shell or the web server.** Both take a weekend, both give you something you can show people, and both make several courses click at once. After that, pick by what you're curious about:

| If you want | Build |
|---|---|
| The quickest satisfying result | the web server (01) |
| The smallest project that teaches the most | the shell (07) |
| Something to show someone tonight | the token and wallet (16) |
| A picture you'll want to look at | the ray tracer (22) |
| To stop Docker feeling magical | the container (08): about 200 lines |
| To understand a tool you use daily | Git (02) |
| To stop AI models feeling like magic | the neural network (10), then the LLM (24) |
| To never fear databases again | the database (06) |
| The deepest single lesson | the language (04) |
| To build the computer itself | the CPU (17) |

## The guides

1. [[build-your-own-shit/01-http-server|Web Server]]: a server that answers real browsers: reading requests, sending pages, handling many visitors. The best first project.
2. [[build-your-own-shit/02-your-own-git|Git]]: your own version control. Real Git can read the repository you create.
3. [[build-your-own-shit/03-your-own-redis|Redis]]: an in-memory database server. The real `redis-cli` can connect to it.
4. [[build-your-own-shit/04-your-own-language|Programming Language]]: read code, build its tree, run it, then add functions that remember their surroundings, a virtual machine or a type checker.
5. [[build-your-own-shit/05-your-own-os|Operating System]]: from switching the computer on to running programs and reading files. Weeks, not a weekend, and it boots on real hardware from a USB stick.
6. [[build-your-own-shit/06-your-own-database|Database]]: store rows on disk, find them quickly, understand basic SQL, and survive being killed mid-save.
7. [[build-your-own-shit/07-your-own-shell|Shell]]: the program that runs your terminal commands, with pipes and redirection. A few hundred lines, and you can actually use it.
8. [[build-your-own-shit/08-your-own-container|Container]]: your own mini-Docker, in about 200 lines and one evening.
9. [[build-your-own-shit/09-your-own-regex-engine|Regex Engine]]: your own regular expressions, which can beat Python's on inputs designed to slow it down.
10. [[build-your-own-shit/10-your-own-neural-network|Neural Network]]: a network that learns, built by hand, including the maths of learning from mistakes (backpropagation).
11. [[build-your-own-shit/11-your-own-memory-allocator|Memory Allocator]]: your own `malloc`. A weekend, and ordinary programs like `ls` can run on it.
12. [[build-your-own-shit/12-your-own-physics-engine|Physics Engine]]: moving, colliding and stacking objects. Bugs are easy to spot, because you can see them.
13. [[build-your-own-shit/13-your-own-react|React]]: your own React in about 500 lines, after which the rules of hooks make sense.
14. [[build-your-own-shit/14-your-own-blockchain|Blockchain]]: blocks, mining, wallets and a network of nodes. Watch two of your nodes disagree, then agree on their own.
15. [[build-your-own-shit/15-your-own-smart-contract-vm|Smart Contract VM]]: a machine that runs smart contracts and charges for each step, like Ethereum's.
16. [[build-your-own-shit/16-your-own-token-and-wallet|Token and Wallet]]: a cryptocurrency token on a real test network, and a wallet whose addresses match MetaMask's.
17. [[build-your-own-shit/17-your-own-cpu/index|CPU (PRIME-1)]]: design a simple processor and build it four ways: in a logic simulator, in Verilog, in Python, and on a breadboard. The final project of [[how-computers-work/index|How Computers Work]].
18. [[build-your-own-shit/18-your-own-compiler|Compiler]]: the sequel to guide 4: turn your language into real machine code that runs on your computer.
19. [[build-your-own-shit/19-your-own-tcp-ip-stack|TCP/IP Stack]]: your own internet networking, from raw packets up. `ping` answers, and guide 1's web server runs on top of it.
20. [[build-your-own-shit/20-your-own-raft-kv-store|Raft Key-Value Store]]: a database spread across several machines that keeps every saved value even when the leader machine dies.
21. [[build-your-own-shit/21-your-own-compressor|Compressor]]: your own zip-style compressor. A weekend, and the standard `gunzip` tool can unpack your files.
22. [[build-your-own-shit/22-your-own-ray-tracer|Ray Tracer]]: a program that draws realistic 3D pictures by following rays of light.
23. [[build-your-own-shit/23-your-own-debugger|Debugger]]: pause a running program, step through its code and read its variables. `gdb` is there to check against at every step.
24. [[build-your-own-shit/24-your-own-llm|LLM]]: a small language model, from splitting text into tokens to generating text. The sequel to guide 10.

## Related

- [[project-ideas|Project ideas]]: more things to build.
- [[PRIMETECHIE|The Primetechie Path]]: where these builds fit in the wider path.
- [[HOME|The home page]]: every course these guides make concrete.

---

## About this section

- **The rule for what gets a guide:** build a small version of something you rely on, so the real thing stops being opaque. All 24 guides are written.
- **How it grew:** the first guides came with the original courses. In August 2026 came the neural network, memory allocator, physics engine and React guides, plus three for the web3 course. In September 2026 six more (TCP/IP, Raft, compressor, ray tracer, debugger and LLM) gave courses that had no build guide one.
- **Considered and not written:** a text editor (overlaps the shell), a BitTorrent client (more plumbing than insight), a web browser (too big to finish), and projects that are really just following a tutorial. A CHIP-8 emulator is left out because guide 17's Python emulator already covers it.
