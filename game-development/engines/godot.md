# Godot

> **[Beginner → Intermediate]** · MIT-licensed, small enough to understand, and the engine this vault recommends starting in.

## Why it's the recommendation

**MIT licence, no revenue conditions, no per-seat fee, no royalty.** Nothing you build can be taxed or withdrawn later — which matters more than it sounds after Unity's 2023 runtime-fee episode → [[game-development/02-engines-and-the-game-loop|note 02]].

**The editor is written in Godot.** The engine is legible in a way Unity and Unreal are not: you can read the source of the thing you're using, and the whole download is ~100 MB.

**GDScript is close to Python** → [[languages/06-python/README|Python]], so if you've done [[foundations/programming-fundamentals/README|programming fundamentals]] you can be productive immediately.

## The model: everything is a node

```
Player (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
├── AnimationPlayer
└── Camera2D
```

A **node** does one thing. A **scene** is a tree of nodes — and **a scene can be instanced inside another scene**, which is how Godot does prefabs. There is no separate prefab concept; **a scene *is* the prefab**, which is unusually clean.

```gdscript
extends CharacterBody2D

@export var speed := 300.0        # @export shows it in the inspector

func _physics_process(delta: float) -> void:
    var dir := Input.get_vector("left", "right", "up", "down")
    velocity = dir * speed
    move_and_slide()
```

**`_physics_process` is the fixed-timestep callback; `_process` is per-frame.** Movement and physics go in the first → [[game-development/02-engines-and-the-game-loop|note 02]].

## Signals — the idiom that defines Godot

Godot's observer pattern, and it's a first-class language feature:

```gdscript
signal health_changed(new_value: int)

func take_damage(amount: int) -> void:
    health -= amount
    health_changed.emit(health)      # anyone listening reacts
```

**Why it matters architecturally: signals point *upward*.** A child emits; a parent connects. That keeps children ignorant of their context, so a health bar doesn't need to know what a player is — which is exactly the coupling argument from [[foundations/systems-engineering/04-architecture-and-interfaces|interfaces]].

**The Godot idiom is "call down, signal up."** Get that and the architecture mostly writes itself.

## GDScript vs C#

**GDScript** — built in, fast iteration, tight engine integration, no build step. Typed since 4.0 (`var x: int`), and **use the types** — they catch errors and speed up execution.

**C#** — available via the .NET build, better performance for heavy computation, and a real type system → [[languages/07-csharp/README|C#]]. The cost: a build step, slightly rougher tooling, and **no web export** on some versions.

**Start with GDScript.** Use C# where you have a genuine CPU-bound hotspot, or you already know it.

## What it does badly, honestly

**3D is behind Unity and Unreal.** Godot 4 improved it enormously, but the tooling, rendering features and third-party asset support are not comparable. **For 2D it's arguably the best option available; for 3D it's a real trade.**

**A smaller ecosystem.** Fewer plugins, fewer tutorials, fewer Stack Overflow answers. You'll read the (excellent) docs rather than find someone who hit your exact problem.

**Console export is not first-party** — it goes through third-party porting houses. A real constraint if consoles are the goal.

**Fewer jobs.** Growing, and still far behind Unity → [[game-development/01-what-game-development-actually-is|the industry, honestly]].

## Related
- [[game-development/engines/README|engines/]] · [[game-development/engines/unity|Unity]]
- [[game-development/08-getting-started|getting started]] — the project ladder
- [[languages/06-python/README|Python]] — the closest neighbour to GDScript

*Source: [reference] — from the Godot documentation, Aug 2026.*
