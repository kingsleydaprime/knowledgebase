# Unity

> **[Intermediate]** · C#, the largest job market, the biggest asset ecosystem — and a fragmentation problem you should understand before committing.

## The model

**GameObject + Component.** A `GameObject` is an empty container with a transform; behaviour comes from components attached to it.

```csharp
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [SerializeField] private float speed = 5f;   // shows in the inspector, stays private

    private Rigidbody2D _rb;

    void Awake() => _rb = GetComponent<Rigidbody2D>();

    void FixedUpdate()                            // fixed timestep — physics goes here
    {
        var input = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"));
        _rb.linearVelocity = input.normalized * speed;
    }
}
```

**This is composition over inheritance** → [[foundations/programming-fundamentals/13-objects-and-classes|note 13]], and it's the same argument ECS makes more strictly → [[game-development/02-engines-and-the-game-loop|note 02]].

**The lifecycle hooks, in order:** `Awake` → `OnEnable` → `Start` → [`FixedUpdate`] → `Update` → `LateUpdate` → `OnDestroy`.

- **`Update`** — per frame. Input, timers, non-physics logic
- **`FixedUpdate`** — fixed step. **All `Rigidbody` work.** Putting physics in `Update` makes behaviour frame-rate dependent, which is the most common Unity bug there is
- **`LateUpdate`** — after everything else. **Camera following goes here**, or the camera lags a frame behind the thing it's tracking

## The performance rules that actually matter

**`GetComponent` is a lookup, not a field access.** Calling it in `Update` is a per-frame cost. Cache it in `Awake`.

**Instantiate/Destroy allocate.** Spawning bullets every frame produces garbage, and **GC spikes are visible as stutter** → [[game-development/01-what-game-development-actually-is|the 16 ms budget]]. Use **object pooling** — pre-allocate, deactivate and reuse.

**Avoid `Find` and `SendMessage`** — string-based lookups over the whole scene.

**`Update` on 10,000 objects is 10,000 managed→native calls.** Past a certain count, one manager iterating a list beats per-object `Update`.

**The general shape: Unity's convenience APIs are fine at small scale and are the thing you remove when profiling** → [[game-development/07-tools-and-production|profile on target hardware]].

## The fragmentation problem

**Be aware of this before you commit**, because it's the main source of "the tutorial doesn't match my editor":

**Three render pipelines.** Built-in (legacy), **URP** (the default for most projects), **HDRP** (high-end). **Assets and shaders written for one often don't work in another**, and converting is real work. Choose at project start; changing later is painful.

**Two input systems.** The legacy `Input` manager and the newer Input System package. Tutorials use both.

**Two UI systems.** uGUI (canvas-based) and UI Toolkit.

**DOTS/ECS** exists alongside the GameObject model as a separate, much faster, much less ergonomic path.

**None of this is fatal — it's just historical weight.** The practical advice: pick **URP + the new Input System** for a new 2D/3D project, and filter tutorials by date.

## Licensing, and the 2023 lesson

Unity is free below a revenue threshold, then per-seat subscriptions.

**In September 2023 Unity announced a per-install runtime fee, retroactively applicable.** The backlash was severe, studios publicly announced migrations to Godot and Unreal, and **the policy was substantially reversed and then cancelled** in 2024. Leadership changed.

**The lesson isn't "Unity is bad" — it's that licence terms on a proprietary engine are a dependency you don't control**, and that belongs in the trade study before you build on it → [[foundations/systems-engineering/05-trade-studies|trade studies]]. Godot's MIT licence is the direct answer to exactly this risk.

## What it does badly, honestly

**The fragmentation above** is the main one.

**Build times and iteration** get slow on large projects — domain reload on every script change is a known pain point.

**Source is not available** on standard licences, so when the engine misbehaves you're reading decompiled code or filing a bug.

**Asset Store quality varies enormously.** A cheap asset that "does everything" is frequently a maintenance liability.

## Why it's still usually the right pick for a job

**The job market is the deepest of the three by a wide margin**, especially in mobile, VR/AR and mid-size studios. C# is a genuinely pleasant, well-designed language with excellent tooling → [[languages/07-csharp/README|C#]]. And the asset ecosystem means a prototype that would take a month takes a week.

## Related
- [[game-development/engines/README|engines/]] · [[game-development/engines/godot|Godot]] · [[game-development/engines/unreal|Unreal]]
- [[languages/07-csharp/README|C#]] — the language
- [[game-development/interview/README|game dev interview prep]]

*Source: [reference] — from the Unity documentation; licensing history from public reporting, Aug 2026.*
