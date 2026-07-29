# Rendering — CSR, SSR, SSG, ISR, Hydration

"Rendering" just means turning application code + data into the actual HTML a browser displays — the real architectural question is **where and when** that happens, and the four common answers below trade off differently on speed, SEO, and server cost.

## CSR — Client-Side Rendering

The server sends a nearly empty HTML shell plus a JavaScript bundle; the browser downloads and runs that JavaScript, which then builds the actual page content and fetches any data it needs.

```
Server sends: <div id="root"></div> + app.js
Browser: downloads app.js, executes it, JS builds the DOM, fetches data via API calls
```

Fast subsequent navigation (once the JS bundle is loaded, moving between pages doesn't need a full server round-trip) and clean separation between frontend and backend (the backend is "just an API"). The cost: the user sees a blank page until the JavaScript downloads, parses, and executes — and search engine crawlers historically struggled with content that only exists after JavaScript runs, though modern crawlers have improved here.

## SSR — Server-Side Rendering

The server runs the same rendering logic that would otherwise run in the browser, produces fully-formed HTML for the *specific request*, and sends that — the user sees real content immediately, before any JavaScript has even loaded.

```
Request comes in -> server renders the React/Vue component tree to an HTML string, per-request
                  -> sends fully-formed HTML -> browser displays it immediately
                  -> JavaScript loads afterward and "hydrates" it (see below)
```

Solves CSR's blank-page problem and is much friendlier to search engine crawlers and social media link previews (they see real content immediately, no JavaScript execution required). The cost: every request requires actual server-side rendering work, so server load scales directly with traffic in a way a purely static approach doesn't.

## SSG — Static Site Generation

The HTML for every page is generated once, **at build time**, not per-request — the result is a folder of plain HTML files that can be served directly from a CDN with no server-side rendering work happening live at all.

```
Build time: generate index.html, about.html, blog/post-1.html, ... (once, ahead of time)
Request time: CDN just serves the pre-built file — no rendering work happens live
```

Extremely fast (serving a static file from a CDN edge is about as fast as this gets) and cheap to scale (no per-request compute). The limitation: content is only as fresh as the last build — genuinely dynamic, frequently-changing, or per-user content doesn't fit this model without a rebuild.

## ISR — Incremental Static Regeneration

A middle ground (popularized by Next.js): pages are statically generated like SSG, but can be **regenerated in the background** after a specified time interval, without needing a full site rebuild for every single content change.

```
First request after the revalidation window -> serve the (possibly slightly stale) cached static page immediately
                                             -> trigger a regeneration in the background
Next request -> gets the freshly regenerated version
```

Combines SSG's speed with a practical answer to "what if content changes after build time" — a reasonable default for content that changes occasionally (a blog, a product catalog) but doesn't need to be live-fresh on every single request the way genuinely real-time data does.

## Hydration — where SSR/SSG and CSR meet

After the server sends pre-rendered HTML (SSR or SSG), the client-side JavaScript still needs to "wake up" — attaching event listeners, restoring component state, taking over from the static markup so the page becomes interactive rather than just a static picture of the app. This process is **hydration**, and it's the reason a server-rendered page can show content instantly but still feel briefly unresponsive to clicks until hydration finishes — the visible content and the page's actual interactivity are, for a brief window, out of sync.

```
1. Server sends fully-rendered HTML -> user sees content immediately
2. JavaScript bundle downloads and executes
3. Hydration: JS "attaches" to the existing DOM, making it interactive
   (if this takes a while, clicks during this window may not respond yet)
```

## Choosing between them

| | Best fit |
|---|---|
| CSR | Highly interactive apps behind a login, SEO less critical (dashboards, internal tools) |
| SSR | Public, content-driven pages needing fresh data and good SEO on every request |
| SSG | Content that rarely changes (marketing pages, documentation) |
| ISR | Content that changes occasionally, wants SSG's speed without a full rebuild per change |

Modern meta-frameworks (Next.js, Nuxt) let different pages within the *same* application use different strategies — a marketing homepage as SSG, a user dashboard as CSR, a blog as ISR — rather than forcing one strategy across an entire app.

## Gotchas

- SSR moves rendering cost onto the server per-request — a slow SSR render becomes a slow response for the user, whereas the equivalent CSR cost is spread onto each individual client's own device instead.
- Hydration mismatches (where the server-rendered HTML doesn't exactly match what the client would render) produce confusing console warnings/errors and, in some frameworks, visibly broken UI — a common bug specifically when rendering logic depends on something only available client-side (like `window` or the current date/time) without accounting for the server not having access to it.
- SEO concerns are frequently overstated for CSR in casual conversation — modern search engines execute JavaScript to a meaningful degree — but for content where being crawled reliably and quickly genuinely matters, SSR/SSG remain the safer, more predictable choice.

## Related
- [[02-state-management|state-management]]
- [[01-frontend-best-practices|frontend-best-practices]]
