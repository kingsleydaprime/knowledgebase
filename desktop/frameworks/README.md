# desktop/frameworks/ — Ways of Building a Desktop App

**Same convention as [[backend/frameworks/README|backend/frameworks/]]:** the concepts live in [[desktop/01-what-desktop-development-is|the course note]]; this is "how *this* stack does it."

**Not numbered** — there's no reading order. Pick the one you're using.

## The map

| Framework | Language | Approach | Binary size | Status |
|---|---|---|---|---|
| **[[desktop/frameworks/tauri\|Tauri]]** | **Rust** + any web frontend | OS webview | **~5–15 MB** | scaffold |
| **[[desktop/frameworks/electron\|Electron]]** | **JS/TS** + Node | Bundled Chromium | ~120–200 MB | scaffold |
| **[[desktop/frameworks/qt\|Qt]]** | **C++** or Python (PySide/PyQt) | Native widgets | ~15–40 MB | scaffold |
| **[[desktop/frameworks/dotnet\|.NET]]** | **C#** | Native (WinUI/MAUI/Avalonia) | ~20–80 MB | scaffold |
| **[[desktop/frameworks/native\|Native]]** | Swift / C# / C++ | Platform SDKs | Smallest | scaffold |

**Scaffold means scaffold** — a page with the shape and the things worth knowing, no written course. The vault's convention is to say so rather than imply depth that isn't there.

## The axis they differ on

Exactly one thing, and everything else follows from it: **where the UI is rendered.**

- **Web renderer** (Electron, Tauri) → you get CSS, the web ecosystem, and identical rendering everywhere. You pay in memory, and in a look that isn't native unless you work at it
- **Native widgets** (Qt, WinUI, SwiftUI) → you get the platform's real controls, accessibility and feel for free. You pay in a smaller ecosystem and per-platform quirks
- **Custom-drawn** (Avalonia, Flutter, game engines) → identical everywhere, native to nothing, and accessibility is your problem

**The accessibility point is underrated.** Native widgets are read correctly by screen readers because the OS knows what they are. Custom-drawn UIs must implement accessibility explicitly, and most don't.

## The same concepts, per stack

| Concept | Electron | Tauri | Qt | .NET |
|---|---|---|---|---|
| **UI layer** | Chromium | OS webview | QtWidgets / QML | XAML |
| **Logic layer** | Node (main process) | **Rust** | C++ / Python | C# |
| **UI ↔ logic** | IPC (`ipcRenderer`) | `invoke` → `#[command]` | signals & slots | data binding |
| **Packaging** | electron-builder | `tauri build` | CQtDeployer | `dotnet publish` |
| **Auto-update** | electron-updater | built-in updater | roll your own | Squirrel / MSIX |

**Note the shared shape: a UI process and a logic process, talking over IPC.** Electron's main/renderer split and Tauri's Rust/webview split are the same architecture, and it exists for the same reason as a [[backend/README|client and server]] — the UI must not be able to compromise the privileged side.

**That's also the security model.** In Electron, `nodeIntegration: false` and `contextIsolation: true` are non-negotiable — the renderer displays untrusted content and must not have filesystem access. Tauri enforces the equivalent by construction: the frontend can only call commands you explicitly expose → [[cybersecurity/04-web-security/README|web security]].

## How to add a framework here

Same rule as backend:
- Which rendering approach, and what it implies
- How it names the concepts above
- Its idioms and gotchas
- What it does badly, honestly

**Don't restate [[frontend/README|frontend]] or [[backend/README|backend]].**

## Related
- [[desktop/README|desktop/]] — the domain index
- [[backend/frameworks/README|backend/frameworks/]] — the convention this copies
