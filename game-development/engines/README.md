# game-development/engines/ — Ways of Building a Game

**Same convention as [[backend/frameworks/README|backend/frameworks/]]:** the concepts live in the numbered course; this is *"how **this** engine does what the course already explained."* Read [[game-development/02-engines-and-the-game-loop|note 02]] first and these become short.

**Not numbered** — there's no reading order. Pick the one you're using.

## The map

| Engine | Language | Rendering | Licence | Best at |
|---|---|---|---|---|
| **[[game-development/engines/godot\|Godot]]** | **GDScript**, C# | Forward+/Mobile/Compat | **MIT — genuinely free** | 2D, small teams, **learning** |
| **[[game-development/engines/unity\|Unity]]** | **C#** | URP / HDRP / Built-in | Per-seat / revenue tiers | Indie, mobile, VR, **the job market** |
| **[[game-development/engines/unreal\|Unreal]]** | **C++** + Blueprints | Deferred, Lumen/Nanite | 5% royalty over a threshold | **AAA visuals**, large teams |
| **[[game-development/engines/from-scratch\|From scratch]]** | C, C++, Rust, Zig | Yours | — | **Learning how engines work** |

## The one axis that decides it

**Not features — how much the engine has already decided for you**, exactly as in [[backend/frameworks/python/README|backend frameworks]]:

- **From scratch** — nothing decided. You write the loop, the renderer, the asset pipeline. **Maximum learning, minimum shipping**
- **Godot** — decided but small enough to read. The editor is itself a Godot application
- **Unity** — decided, enormous, and fragmented by history (three render pipelines, two input systems)
- **Unreal** — decided *hard*. The engine has strong opinions about your architecture, and fighting them is a losing project

## The same concepts, per engine

The course's vocabulary, translated. **This table is most of what "learning a new engine" actually is:**

| Course concept | Godot | Unity | Unreal |
|---|---|---|---|
| **Game object** | `Node` | `GameObject` | `Actor` |
| **Component** | child node / `Resource` | `MonoBehaviour` | `UActorComponent` |
| **Scene / level** | `Scene` (a node tree) | `Scene` | `Level` / `World` |
| **Prefab** | **scene instance** | `Prefab` | `Blueprint Class` |
| **Per-frame hook** | `_process(delta)` | `Update()` | `Tick(DeltaTime)` |
| **Fixed-step hook** | `_physics_process(delta)` | `FixedUpdate()` | substepping / timers |
| **Collision volume** | `CollisionShape` | `Collider` | `Collision Component` |
| **Asset** | `Resource` | `Asset` | `UObject` asset |
| **Messaging** | signals | events / `UnityEvent` | delegates |

**Notice the shape is identical.** A tree of objects, components attached, a per-frame callback and a fixed-step physics callback. **Once you've internalised the loop and the fixed timestep** → [[game-development/02-engines-and-the-game-loop|note 02]], a new engine is a fortnight of vocabulary, not a new discipline.

**And notice the fixed-step row.** Every engine separates `Update` from `FixedUpdate` for the reason note 02 gives: physics must be deterministic and frame-rate independent. **Putting physics code in `Update` is the most common beginner bug in all three engines**, and it's the same bug in each.

## Which to pick

**Learning, or 2D, or you want to read the engine you're using** → **Godot**. MIT, small, GDScript is close enough to [[languages/06-python/README|Python]] to be productive on day one.

**A job, or mobile/VR, or the largest asset ecosystem** → **Unity**. It has the deepest job market by a wide margin, and C# is a genuinely good language → [[languages/07-csharp/README|C#]].

**Photorealism, or AAA employment** → **Unreal**. Accept the C++ dialect and the engine's opinions.

**Understanding how any of it works** → **from scratch**, and be honest that it's a study project → [[game-development/engines/from-scratch|from-scratch]].

**Don't agonise.** The transferable skills — the loop, vectors, state machines, and finishing something — are identical in all four → [[game-development/08-getting-started|getting started]].

## How to add an engine here

Keep it to what the course doesn't already cover:
- Which language and what that implies
- How it names the concepts above
- Its idioms and its specific gotchas
- What it does badly, honestly

**Don't restate the course.** If you're explaining what a fixed timestep is, that belongs in [[game-development/02-engines-and-the-game-loop|note 02]].

## Related
- [[game-development/README|game-development/]] — the course
- [[backend/frameworks/README|backend/frameworks/]] — the convention this copies
