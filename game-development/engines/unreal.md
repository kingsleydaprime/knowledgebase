# Unreal Engine

> **[Advanced]** · C++ and Blueprints, AAA-grade rendering out of the box, and an engine with strong opinions you should not fight.

## The model

**Actor + Component**, similar in shape to Unity, with a heavier framework around it:

- **`AActor`** — anything placeable in a level
- **`UActorComponent`** — behaviour attached to an actor
- **`APawn`** — an actor that can be possessed by a controller
- **`ACharacter`** — a pawn with a capsule, movement component and networking already wired
- **`AController`** / **`APlayerController`** — the "brain", separate from the body
- **`AGameMode`** — the rules; server-authoritative
- **`UGameInstance`** — persists across level loads

**The pawn/controller split is the design worth understanding.** It exists so that a body can be driven by a player *or* by AI without changing the body — and because in multiplayer the controller is where authority lives → [[game-development/06-multiplayer-and-networking|networking]].

## The C++ is a dialect

**This is not the C++ in [[languages/05-cpp/README|the C++ course]].** Unreal uses its own macro-driven system:

```cpp
UCLASS()
class MYGAME_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
    float Health = 100.f;

    UFUNCTION(BlueprintCallable)
    void TakeDamage(float Amount);
};
```

- **`UCLASS`/`UPROPERTY`/`UFUNCTION`** feed a reflection system C++ doesn't natively have — that's what makes properties editable in the editor, serialisable, garbage-collected and network-replicated
- **`UObject`-derived classes are garbage collected** — you don't `delete` them. Raw pointers to `UObject`s must be `UPROPERTY` or the GC will collect underneath you
- **`FString`, `TArray`, `TMap`** replace the STL
- **Header/source split, plus generated headers**, with `#include "MyActor.generated.h"` last — always

**Practical consequence: your C++ knowledge transfers about half.** The language is the same; the idioms, memory model and standard library are not.

## Blueprints

A visual scripting graph, and **not a toy** — shipped AAA games use them heavily.

**The mature convention:** systems and performance-critical work in **C++**, then expose it (`BlueprintCallable`, `BlueprintImplementableEvent`) so designers compose gameplay in **Blueprints**.

**Why that split:** it's the [[game-development/07-tools-and-production|iteration-time argument]] — designers change behaviour without a programmer and without a 10-minute compile.

**Where Blueprints go wrong:** large graphs become unreadable ("blueprint spaghetti"), they diff badly in version control (binary assets → [[game-development/07-tools-and-production|why games broke git]]), and tight per-frame loops are meaningfully slower than C++.

## What you get for free

**This is the actual reason to choose Unreal:** the default visual quality is extremely high before you configure anything.

**Lumen** (real-time global illumination), **Nanite** (virtualised micropolygon geometry — film-quality meshes without manual LODs), **Chaos** physics, a mature animation and cinematics toolset, and a **networking/replication system** that is genuinely the best available out of the box.

If the goal is photorealism, you would spend years reproducing that.

## What it does badly, honestly

**It is enormous.** The engine download is tens of GB; a project's derived data is more. Compile times are long, and a full shader compile can take hours.

**The learning curve is steep and wide** — the C++ dialect, the framework's opinions, the asset pipeline, and the editor all at once.

**Overkill for 2D and for small games.** Paper2D exists and is not competitive with Godot or Unity for 2D work.

**Build sizes are large**, which matters for mobile and web.

**The royalty:** 5% of gross revenue above a threshold (currently $1M per title), after which it's a real cost — and worth modelling in the trade study rather than discovering later → [[foundations/systems-engineering/05-trade-studies|trade studies]].

## Related
- [[game-development/engines/README|engines/]] · [[game-development/engines/unity|Unity]]
- [[languages/05-cpp/README|C++]] — the language it deviates from
- [[game-development/03-graphics-for-games|graphics for games]] — what Lumen and Nanite are solving

*Source: [reference] — from the Unreal Engine documentation, Aug 2026.*
