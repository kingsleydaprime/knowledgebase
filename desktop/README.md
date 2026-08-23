# Desktop

Applications that install on a machine — and the constraints the web removed and desktop kept.

**~2,750 words: 1 note + a frameworks index + 5 scaffolds.** Built August 2026. `[reference]`.

> **The one idea:** you're not shipping to a server you control — **you're shipping to machines you don't**, that run versions you didn't choose, and that you cannot update on demand. Distribution, not UI, is the discipline's real problem.

## Why this exists, and why it's small

Requested directly: *"same way there's backend then frameworks for different languages, we can have desktop/frameworks/..."* — and the shape was right, so it copies [[backend/frameworks/README|backend/frameworks/]] exactly.

**It's deliberately thin, because a desktop app is mostly a [[frontend/README|frontend]] and a [[backend/README|backend]] living in one process.** The genuinely new material is distribution, platform integration and the UI/logic process split. Everything else is already in this vault.

## Contents

1. [[desktop/01-what-desktop-development-is|What Desktop Development Is]] — **[Beginner]** — what differs from the web, the three approaches, **the Electron memory argument fairly**, and choosing
2. [[desktop/frameworks/README|frameworks/]] — the map, and the one axis they differ on

**The frameworks, all `scaffold`:** [[desktop/frameworks/tauri|Tauri]] · [[desktop/frameworks/electron|Electron]] · [[desktop/frameworks/qt|Qt]] · [[desktop/frameworks/dotnet|.NET]] · [[desktop/frameworks/native|Native]]

## The things worth carrying

1. **You cannot update everyone.** Auto-update is a feature, not an afterthought → [[desktop/01-what-desktop-development-is|01]]
2. **Distribution is often more work than the feature** — signing, notarisation, installers, stores → [[desktop/01-what-desktop-development-is|01]]
3. **Platform conventions are why cross-platform apps feel cheap**, and users can't tell you why → [[desktop/01-what-desktop-development-is|01]]
4. **The market chose web-in-a-shell** because developer supply decided it, not because it's technically best → [[desktop/01-what-desktop-development-is|01]]
5. **The one axis is where the UI renders**: web engine, native widgets, or custom-drawn — and custom-drawn means accessibility is your problem → [[desktop/frameworks/README|frameworks/]]
6. **UI process + logic process over IPC** is the shared architecture, and it's a security boundary → [[desktop/frameworks/README|frameworks/]]
7. **Electron security is opt-in.** `contextIsolation: true`, always → [[desktop/frameworks/electron|Electron]]
8. **Tauri trades one bundled browser for three OS webviews to test** → [[desktop/frameworks/tauri|Tauri]]
9. **Check Qt's licence before you build a product on it** → [[desktop/frameworks/qt|Qt]]

## Where this connects

| | |
|---|---|
| [[frontend/README\|frontend]] | The UI half — most of a desktop app |
| [[backend/README\|backend]] | The logic half, in the same process |
| [[databases/README\|databases]] | SQLite is the usual local store |
| [[devops/06-ci-cd/README\|CI/CD]] | Building, signing and releasing for three platforms |
| [[languages/03-rust/README\|Rust]] · [[languages/06-python/README\|Python]] · [[languages/05-cpp/README\|C++]] | Tauri · PySide · Qt |
| [[foundations/software-engineering/04-the-kinds-of-software-engineering\|kinds of software engineering]] | Where desktop sits in the tree |

## The honest note

**`[reference]`, and the thinnest domain in this vault** — I have not shipped a desktop application, signed a binary, been through App Store review, or maintained an auto-updater. **The distribution material is exactly the part I'd trust least**, because it's the part that's learned by being burned.

**What would close the gap:**

1. **Ship one tiny Tauri app to all three platforms.** Not the app — **the pipeline.** Build, sign, install it on a machine that isn't yours. That single exercise teaches most of note 01
2. **Then break it deliberately:** ship v2 and make auto-update work from v1
3. **Read the notarisation docs once**, and note how much of the work is neither frontend nor backend

**What's missing:** the framework pages are scaffolds by design; also absent are packaging in practice, code signing and notarisation step by step, auto-update architectures, app-store requirements, native menus/tray/shortcuts, offline sync and conflict resolution, and accessibility.

**Note on roadmap.sh:** there is **no desktop roadmap** — the site covers web, mobile, data and infrastructure roles. Nothing to cross-reference against, which is itself a signal about where the industry's attention is.

→ [[PRIMETECHIE|Reading is not a rank.]]

## Related
- [[desktop/frameworks/README|frameworks/]]
- [[backend/frameworks/README|backend/frameworks/]] — the convention this copies
- [[BUILD-PLAN|Build Plan]]
