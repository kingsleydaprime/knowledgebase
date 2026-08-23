# Tauri — scaffold

**[Intermediate]** · Rust backend, OS webview frontend. The current recommendation for new desktop work by a web developer.

## The shape

```
your web frontend (React/Svelte/vanilla — any of them)
        ↕  invoke()  /  events
Rust backend  — #[tauri::command] functions
        ↕
OS webview: WebKit (macOS) · WebView2 (Windows) · WebKitGTK (Linux)
```

```rust
#[tauri::command]
fn read_config(path: String) -> Result<String, String> {
    std::fs::read_to_string(path).map_err(|e| e.to_string())
}
```
```js
const cfg = await invoke("read_config", { path: "app.toml" });
```

## The things to know

**Binaries are ~5–15 MB**, against Electron's 120–200 — because the webview is already on the machine.

**Security is allowlist-based by design.** The frontend can call *only* the commands you expose. This is stronger than Electron's `contextIsolation`, which is opt-in and frequently misconfigured.

**The real cost: three webview engines.** You've swapped "bundle one browser" for "test against three", and WebKitGTK on Linux is the weakest of them. **This is the browser-compatibility problem you thought you'd left behind** — and it's the honest counterweight to the size argument.

**You need some Rust** → [[languages/03-rust/README|Rust]]. Not deep Rust — commands, `Result`, serde — but the learning curve is real if you've only written TypeScript.

**v2 (2024) added mobile targets** (iOS/Android), which changes the calculus if you want one codebase across desktop and mobile.

## Related
- [[desktop/frameworks/electron|Electron]] — the incumbent it targets
- [[desktop/frameworks/README|frameworks/]] · [[languages/03-rust/README|Rust]]

*Source: [reference] — scaffold, from the Tauri documentation.*
