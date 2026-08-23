# Electron — scaffold

**[Intermediate]** · Chromium + Node, bundled. The incumbent: VS Code, Slack, Discord, Obsidian, Postman, Figma desktop.

## The shape

**Main process** (Node) — one per app. Owns windows, menus, the filesystem, native APIs.
**Renderer process** (Chromium) — one per window. Your web UI. **Should have no direct Node access.**
**Preload script** — the bridge, exposing a narrow, explicit API to the renderer.

```js
// preload.js — the ONLY thing the renderer should see
contextBridge.exposeInMainWorld("api", {
  readConfig: (p) => ipcRenderer.invoke("read-config", p),
});
```

## The things to know

**Security is opt-in and this is where apps get compromised.** Set `nodeIntegration: false`, `contextIsolation: true`, `sandbox: true`, and expose a deliberate API through a preload script. **A renderer with Node access plus any XSS is arbitrary code execution on the user's machine** → [[cybersecurity/04-web-security/README|web security]].

**Memory and size are the standing criticism** — a whole Chromium per app. Legitimate, and empirically survivable: the most-used editor in the world ships this way.

**The ecosystem is the real advantage.** Any npm package, mature tooling (electron-builder, electron-updater), enormous prior art for every problem you'll hit, and auto-update that works.

**Chromium is consistent everywhere**, which is Electron's genuine technical win over Tauri: one renderer, one set of bugs, no per-platform CSS surprises.

**Keep Chromium updated.** You are shipping a browser; its CVEs are now your CVEs → [[devops/12-sre-and-platform-engineering/04-devsecops|DevSecOps]].

## Related
- [[desktop/frameworks/tauri|Tauri]] — the lighter alternative
- [[desktop/frameworks/README|frameworks/]] · [[backend/frameworks/javascript/01-node-runtime/README|Node runtime]]

*Source: [reference] — scaffold, from the Electron documentation.*
