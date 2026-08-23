# Tools and Production

> **[Intermediate]** · The content pipeline, why tools programmers matter most, and how games actually ship.

**Most of a game is not code**, and most engineering effort on a mature project goes into making *other people* productive. This is the least-discussed and most-underestimated part of the field.

## The content pipeline

Between an artist's file and something a game can load at 60 fps:

```
   .blend / .fbx / .psd          author formats
          ↓  import
   intermediate representation
          ↓  process — compress, generate LODs, bake lighting,
          ↓  build collision, pack atlases, compile shaders
   platform-specific binary       optimised, per-platform
          ↓  package
   the shipped build
```

**Nothing an artist authors is what ships.** A 4K PNG becomes a compressed GPU texture (BC7, ASTC) in a format the target hardware samples natively. A 500k-triangle sculpt becomes a 5k-triangle mesh with a normal map baked from the original.

**And every step is a build step that can be slow or wrong**, which is why a game studio has build engineers and why "the build is broken" is an all-hands problem.

## Iteration time is the metric

**The single most important number on a game project is how long it takes to see a change.**

If a designer changes an enemy's health and must wait 4 minutes to test it, they'll try 10 variations a day. At 4 seconds, they'll try 500. **The design quality difference is enormous**, and it compounds over a project's whole life.

So a large fraction of tools work is attacking that number: hot reloading, in-editor play, live-tuning while running, incremental builds, distributed compilation (FASTBuild, Incredibuild), asset caching, and shader-compilation caches.

**This is the same argument as [[devops/12-sre-and-platform-engineering/03-platform-engineering|platform engineering]]** — reduce the cognitive load and waiting time of the people producing value, and treat their productivity as your product. Games understood it decades earlier because the feedback loop is so visibly tied to quality.

## Data-driven design

**Hard-coding values means a programmer is in the loop for every tuning change.** So games push everything into data: JSON, YAML, spreadsheets, custom editors, visual node graphs.

```json
{ "id": "grunt", "health": 100, "speed": 3.5, "behaviour": "aggressive" }
```

**Designers change values; engineers change systems.** The extreme is a full scripting layer — Lua, GDScript, Blueprints — where gameplay is authored without recompiling.

The trade is real: data-driven systems are harder to debug (the logic is in content nobody type-checks), and errors move from compile time to runtime. **Validate your data**, and treat a schema for it as seriously as a type system → [[languages/06-python/08-typing-and-type-hints|typing]].

## Version control, and why games broke git

Games are **large binary assets** — textures, models, audio, video. Git handles this badly:

- Binaries can't be diffed or merged; every version is stored whole
- Repositories reach hundreds of GB
- Two people editing one scene file is an unresolvable conflict

**Hence file locking** — check out a file exclusively so nobody else can edit it. Alien to a git workflow → [[git/README|git]] and completely necessary when merging is impossible.

**Perforce** remains the industry standard for this reason: centralised, handles huge binaries, locking is native. **Git LFS** plus a locking layer works for smaller teams, and **Plastic SCM / Unity Version Control** targets the same problem.

**This is a genuine case where general software's best practice doesn't transfer**, and it's worth noticing why: the constraint isn't culture, it's that the merge operation doesn't exist for the data type.

## How games are actually built

**Vertical slice first.** One level, one enemy, one weapon — *finished to shipping quality*. It proves the game is fun and exposes the real cost per unit of content. **A game that isn't fun as a vertical slice will not become fun with more content**, and finding that out early is the whole point.

**Then the milestones** — prototype → vertical slice → alpha (feature complete) → beta (content complete) → gold. The definitions matter because *feature complete* and *content complete* are different dates and conflating them is a scheduling failure.

**Playtesting is the only real feedback.** Watch someone play without helping them. **What players do bears little relation to what designers expected**, and there's no substitute for the discomfort of watching someone fail at something you thought was obvious. It's [[foundations/systems-engineering/06-verification-and-validation|operational validation]], and the same finding recurs: technically correct systems fail on human factors.

**Scope is the killer.** Almost every failed indie project failed on scope, not skill. The reliable heuristic: **estimate, then cut to a third**, and ship the third.

## Performance culture

Games profile continuously, not at the end — because a frame budget is a hard constraint you can violate at any moment, and finding out late means an expensive redesign.

**Profile on the target hardware.** A game running at 120 fps on a development machine may run at 22 on a base console or a mid-range Android. **The dev machine is the least representative hardware you own.**

Tools: engine profilers, RenderDoc (frame capture), platform vendor tools (PIX, Instruments, Nsight). And the same method as everywhere else — **measure, hypothesise, change one thing, measure again** → [[foundations/computer-architecture/12-performance|performance method]].

## Shipping

**Certification** is real for consoles. Sony, Microsoft and Nintendo each have hundreds of technical requirements — how you handle a controller disconnecting, suspend/resume, save-data corruption, naming conventions, load-time limits. **Failing cert costs weeks**, and it's a fixed, knowable checklist that studios still get wrong.

**Then:** store pages, age ratings, localisation, day-one patches, and live operations if the game continues after launch — which is now most of them, and is a [[devops/README|devops]] job with a different name.

## Related
- [[game-development/08-getting-started|getting started]] — scope, applied to you
- [[devops/12-sre-and-platform-engineering/03-platform-engineering|platform engineering]] — the same productivity argument
- [[git/README|git]] — and where it doesn't fit
- [[foundations/systems-engineering/06-verification-and-validation|V&V]] — playtesting as validation

*Source: [reference] — cross-referenced against [roadmap.sh game-developer](https://roadmap.sh/game-developer).*
