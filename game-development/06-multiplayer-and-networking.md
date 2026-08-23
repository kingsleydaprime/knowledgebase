# Multiplayer and Networking

> **[Advanced]** · Why the hard part isn't sending data — it's that every player is looking at a slightly different past.

**Multiplayer is the hardest common problem in game development**, and the reason is physics rather than engineering: information takes time to travel, so **no two players can ever share the same "now".**

At 50 ms one-way latency, you are always seeing where everyone *was* 50 ms ago. Every technique below is about hiding that.

## The authority question

**Peer-to-peer** — clients talk directly, each simulating.
✓ No server cost, lower latency between peers.
✗ **Trivially cheatable** — nothing arbitrates truth. Bad NAT traversal. Doesn't scale past a handful.

**Client-server** — one authoritative simulation; clients send input and receive state.
✓ **Cheat-resistant**, scales, one source of truth.
✗ Server cost, and every action costs a round trip.

**The rule, and it is close to absolute: never trust the client.** A client that reports its own position will report being inside the enemy base with 10,000 health. The server simulates; the client *requests* and *predicts*.

Clients that were once trusted for hit detection produced an entire generation of aimbots. **Treat the client as hostile input** — exactly the posture in [[cybersecurity/04-web-security/01-input-validation-and-output-encoding|input validation]].

## The three techniques that make it playable

**1. Client-side prediction.** Rather than waiting for the server, the client applies your input immediately and *predicts* the result. Movement feels instant.

**2. Server reconciliation.** The server's authoritative state arrives 100 ms later. If it disagrees with what the client predicted, the client **rewinds to the server state, replays every input since**, and snaps to the corrected result. Done well, you never notice; done badly, you get "rubber-banding".

Both require **determinism** — the same inputs must produce the same outputs, or replay diverges → [[game-development/02-engines-and-the-game-loop|the game loop]].

**3. Entity interpolation.** Other players' positions arrive as discrete snapshots (say 20/second). Rendering them directly is jerky. So the client renders them **~100 ms in the past**, smoothly interpolating between two received snapshots.

**Which produces the central trade:** *you* are in the present, *everyone else* is in the past, and the server is somewhere between. All three disagree, deliberately.

**Lag compensation** resolves the resulting unfairness: when you shoot, the server rewinds every other player to where *your client* showed them at the moment you fired, and tests the hit there. **This is why you sometimes die behind cover** — on the shooter's screen you were still exposed, and the server agreed with them. It's a deliberate choice to favour the shooter, and it is why the alternative feels worse.

## Lockstep

The other architecture entirely: **send only inputs; every client simulates identically.**

Used by RTS games — *Age of Empires*, *StarCraft*. With 500 units per player, sending state is impossible; sending a handful of commands per tick is trivial.

**The catch: absolute determinism is required.** Any divergence — a floating-point difference between CPUs, an iteration order over a hash map, an uninitialised value — desynchronises the game permanently. Hence fixed-point arithmetic, ordered containers, and desync-detection checksums.

**It also can't hide latency**, because a command can't execute until everyone has it. RTS games disguise this with acknowledgement animations — the unit salutes immediately, and moves when the command lands.

## Transport

**UDP for game state; TCP for everything else.**

TCP's ordering guarantee is the problem: a lost packet blocks every packet behind it while it retransmits — **head-of-line blocking** → [[foundations/networking/06-tcp-connection-lifecycle|TCP]]. In a game, a 100 ms-old position update is *worthless* — you already have a newer one. Waiting for it delays everything.

So games use UDP and build only what they need on top: sequence numbers, selective reliability (reliable for "you died", unreliable for position), and delta compression against the last acknowledged state.

**This is exactly the reasoning behind [[foundations/networking/13-quic-and-modern-transport|QUIC]]** — independent streams over UDP to avoid head-of-line blocking. Games arrived there twenty years earlier.

**Bandwidth is managed by not sending things:** delta-encode against the last acknowledged state, quantise (positions don't need 32-bit floats), send at 10–30 Hz rather than per frame, and **use relevance filtering** — don't send what a player can't see, which is also an anti-cheat measure, since anything sent to the client can be read by a cheat.

## Scale and topology

**Matchmaking, lobbies, dedicated servers, regions** — and the operational half is ordinary [[devops/README|devops]]: autoscaling instances, placing them near players, session routing, observability → [[devops/00-the-physical-layer/03-data-centres|regions and AZs]].

**Latency is geography.** Nothing beats a server physically closer, which is why regional deployment isn't optional and why cross-region play feels bad no matter how good the netcode.

For MMOs: **sharding** by zone, **interest management** so a server only tracks what matters to nearby players, and handing players between servers at boundaries. This is [[architecture/04-distributed-systems/README|distributed systems]] with a hard latency budget.

## Honest advice

**Don't make your first game multiplayer.** It multiplies the difficulty of everything — debugging is harder (two processes, timing-dependent, non-reproducible), testing needs multiple clients, and every gameplay feature must be re-thought for prediction and authority.

**If you do:** use your engine's networking (Unity Netcode/Mirror, Unreal's replication, Godot's high-level multiplayer) rather than sockets. And read Valve's *Source Multiplayer Networking* and Gabriel Gambetta's *Fast-Paced Multiplayer* — both short, free, and they explain prediction and reconciliation better than anything else available.

## Related
- [[foundations/networking/README|networking]] — **the full course; this note assumes it**
- [[foundations/networking/13-quic-and-modern-transport|QUIC]] — the same head-of-line reasoning
- [[architecture/04-distributed-systems/README|distributed systems]] — consistency under latency
- [[game-development/02-engines-and-the-game-loop|the game loop]] — why determinism matters

*Source: [reference] — cross-referenced against [roadmap.sh game-developer](https://roadmap.sh/game-developer) and Valve/Gambetta's published material.*
