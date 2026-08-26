# What Desktop Development Is

> **[Beginner]** · The constraints web developers don't have — distribution, versions you can't control, and an OS you must integrate with.

Desktop applications were the default, then the web took nearly everything, and then a specific set of things came back: **editors, design tools, developer tooling, communication apps, media production, and anything that needs the filesystem, hardware, or to work offline.**

VS Code, Figma's desktop app, Discord, Slack, Docker Desktop, Obsidian — the vault you're reading this in is a desktop app.

## What actually differs from the web

**1. You cannot update everyone.** A web deploy is instant and universal. A desktop release sits on machines you don't control, and **users on a version from two years ago are your problem**. Hence auto-update as a first-class feature, and hence supporting old versions far longer than you'd like.

**2. The environment is genuinely unknown.** Three operating systems, several versions each, wildly varying hardware, different display scaling, different themes, antivirus that quarantines your binary, corporate policies that block installation.

**3. Distribution is a real project.** Code signing (a paid certificate on Windows and macOS), notarisation on macOS, installers per platform, app stores with review processes, and update infrastructure. **This is often more work than the feature you're shipping**, and it surprises everyone the first time.

**4. You have real access.** The filesystem, USB devices, the system tray, global shortcuts, background execution, native notifications, other processes. **This is the whole reason to build desktop** — it's what the browser sandbox denies you.

**5. Offline is the default assumption**, not a feature you add.

**6. Users expect it to feel native.** Platform conventions differ — menu placement, keyboard shortcuts (`Cmd` vs `Ctrl`), window behaviour, file dialogs. **Getting these wrong is the most common reason a cross-platform app feels cheap**, and users can rarely articulate why.

## The three approaches

**Native per platform** — Swift/SwiftUI on macOS, C#/WinUI on Windows, GTK/Qt on Linux.
✓ Best performance, perfect platform feel, full API access, smallest binaries.
✗ **You write it three times.**

**Cross-platform native toolkit** — Qt, GTK, .NET MAUI, Avalonia. One codebase, compiled to native widgets.
✓ Genuinely native performance, one codebase, small binaries.
✗ Platform feel is approximate; smaller ecosystems; licensing to check (Qt's commercial/LGPL split matters).

**Web technology in a shell** — Electron, Tauri.
✓ **One codebase, and you already know the stack.** Huge ecosystem, fast development, excellent UI flexibility.
✗ Memory and binary size (Electron especially), and it can feel non-native if you don't work at it.

**The market has largely chosen the third**, for one honest reason: **the supply of web developers vastly exceeds the supply of native ones**, and a shipped app in Electron beats an unshipped one in Qt. VS Code, Slack, Discord, Figma, Notion, Obsidian, Postman are all web-in-a-shell.

## The Electron memory argument, fairly

Electron ships a whole Chromium and a whole Node runtime with every app. A trivial app is **~150 MB on disk and ~100–200 MB of RAM before it does anything**, and running five Electron apps means five copies of Chromium.

**This complaint is legitimate and also frequently overstated.** VS Code is Electron and is the most-used editor in the world; users demonstrably accept it. The memory matters on constrained machines and matters less on a 16 GB laptop.

**Tauri is the direct response**: use the OS's *existing* webview (WebKit on macOS, WebView2 on Windows, WebKitGTK on Linux) rather than bundling one, and write the backend in Rust. **Binaries in single-digit MB instead of 150.** The trade is that you're now testing against three different webview engines with different bugs — which is the browser-compatibility problem you thought you'd escaped.

## What this vault gives you already

**Almost all of it, in other folders** — which is why `desktop/` is thin:

| Need | Already here |
|---|---|
| UI, state, components | [[frontend/README\|frontend]] · [[frontend/README\|frontend concepts]] |
| The backend/business layer | [[backend/README\|backend]] |
| Local storage | [[databases/README\|databases]] — SQLite is the usual answer |
| Packaging, signing, CI releases | [[devops/06-ci-cd/README\|CI/CD]] |
| Rust, for Tauri | [[languages/03-rust/README\|Rust]] |
| C++/C#, for Qt/.NET | [[languages/05-cpp/README\|C++]] · [[languages/01-java/README\|Java]] (adjacent) |
| Processes, filesystem, IPC | [[foundations/os/README\|OS]] |

**A desktop app is mostly a frontend and a backend in one process**, with distribution as the genuinely new problem.

## Choosing

**Already know web?** → **Tauri** for new work, **Electron** if you need maximum ecosystem maturity or heavy Node integration.
**Want it small, fast, and native-feeling?** → **Qt** (C++/Python) or **Avalonia** (C#).
**Windows-only, enterprise?** → **.NET / WinUI**.
**macOS-only, best possible feel?** → **SwiftUI**.
**A developer tool with a CLI already?** → **consider not building a GUI at all.** A good CLI plus a web UI on localhost is often the right answer, and it's how much developer tooling ships.

## Related
- [[desktop/frameworks/README|frameworks/]] — the options, compared
- [[frontend/README|frontend]] — the UI half
- [[foundations/software-engineering/04-the-kinds-of-software-engineering|kinds of software engineering]] — where desktop sits
- [[foundations/os/README|OS]] — what you're integrating with

*Source: [reference] — written Aug 2026. No roadmap.sh roadmap covers desktop.*
