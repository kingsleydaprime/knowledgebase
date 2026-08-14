# How Quartz Works

**[Intermediate]** — What actually happens between a `.md` file in this vault and an HTML page on the internet. Worth knowing before touching config, because almost every "why isn't my change showing up" question is answered somewhere in this pipeline.

## The one-sentence version

Quartz is a static site generator: it reads Markdown, runs it through a chain of plugins, and writes HTML to `public/`. There is no server, no database, and nothing dynamic — the output is files.

That's why it's fast, and also why every change requires a rebuild. If you edited config and the site looks the same, you almost certainly haven't rebuilt.

## The build pipeline

Running `npx quartz build` walks a fixed sequence. Understanding the *stages* matters because plugins slot into specific ones, and a plugin can only do what its stage allows.

```
content/*.md
   │
   ├─ 1. GLOB      recursively find all files, respecting .gitignore
   │
   ├─ 2. PARSE     for each file (in worker threads if >128 files):
   │                 read into a vfile
   │                 apply text transformations       ← plugin hook
   │                 slugify the path
   │                 Markdown → mdast   (remark-parse)
   │                 apply mdast transformations      ← plugin hook
   │                 mdast → hast       (remark-rehype)
   │                 apply hast transformations       ← plugin hook
   │
   ├─ 3. FILTER    drop unwanted content                ← plugin hook
   │                 (drafts, explicit-publish, ignorePatterns)
   │
   └─ 4. EMIT      write output files                   ← plugin hook
                     hast → JSX (Preact) → static HTML
                     assemble the layout from quartz.config.yaml
                     minify CSS via Lightning CSS
                     split JS into beforeDOMLoaded / afterDOMLoaded
                            │
                        public/*.html
```

Three consequences worth internalising:

**Parsing is per-file and parallel.** A transformer plugin sees one file at a time and can't know about the others. Anything needing global knowledge — backlinks, the graph, search — has to be an *emitter*, running after every file is parsed. That's why `content-index` is a required dependency of the graph view.

**Filtering happens after parsing.** An ignored file still gets read and parsed before being dropped. Adding `sources/**` to `ignorePatterns` keeps it off the site, but doesn't make the build meaningfully faster.

**HTML is rendered by Preact, statically.** `preact-render-to-string` runs the components once and throws away the runtime. `useState` and `useEffect` do nothing. Interactivity comes from separate client-side scripts (`*.inline.ts`) that components declare, which get bundled into `prescript.js` / `postscript.js` and re-attached on each navigation.

## The client side

Once the page loads, Quartz dispatches a custom `"nav"` event. Every interactive component listens for it and wires up its own handlers.

This exists because of `enableSPA: true` (set in this vault's config). With SPA routing on, clicking an internal link swaps the page content *without* a full browser reload — so `DOMContentLoaded` never fires again, and any component that relied on it would silently break after the first navigation. `"nav"` fires on every navigation instead.

If you ever write a custom component and its behaviour works on first load but dies after clicking a link, this is why.

## The CLI

```bash
npx quartz build                 # build once into public/
npx quartz build --serve         # build + local server on :8080 + hot reload
npx quartz build --serve -d docs # build a different content directory
npx quartz plugin install        # install plugins pinned in quartz.lock.json
npx quartz plugin install --latest   # refresh plugins to their newest versions
npx quartz plugin add github:owner/name
npx quartz create                # first-time setup wizard
npx quartz sync                  # commit and push content (not used here — git is run by hand)
```

`--serve` starts two servers: an HTTP file server on 8080, and a WebSocket on 3001 that pushes rebuild signals. Content edits (`.md`) trigger a fast incremental rebuild, debounced 250ms. Config and source edits (`.ts`, `.scss`) trigger a full module rebuild via esbuild.

## Version 5 vs version 4

This matters because most Quartz material online is still v4:

| | v4 | v5 |
|---|---|---|
| Config | `quartz.config.ts` (TypeScript) | `quartz.config.yaml` |
| Layout | `quartz.layout.ts` | `layout:` section in the same YAML |
| Plugins | imported from Quartz's own source | separate npm packages under `@quartz-community/*` |
| Custom code | edit `quartz.config.ts` | `quartz.ts` TS overrides, for callbacks YAML can't express |

If a tutorial tells you to edit `quartz.config.ts`, it's for v4 and the file won't exist. See [[tools/quartz/02-configuration|Configuration]] for the v5 equivalents.

The plugin split is the bigger change. In v5 components like the explorer, graph and search are **installed packages** in `node_modules/@quartz-community/`, not vault source. That's a real advantage when debugging: you can read the actual implementation.

```bash
# When docs are ambiguous, read the shipped code — it's the ground truth
ls node_modules/@quartz-community/
grep -o "focusOnHover[^;]\{0,200\}" node_modules/@quartz-community/graph/dist/index.js
```

That technique is how the graph link-colour behaviour in [[tools/quartz/05-the-graph-view|The Graph View]] was pinned down — the docs don't mention it, but the source is unambiguous.

## Where the real documentation is

Quartz ships its own docs *inside this repo* at `quartz/docs/`. That's the authoritative reference and it's version-matched to the installed Quartz, unlike anything on the web.

```bash
cd quartz && npx quartz build --serve -d docs   # read them as a site
grep -rl "graph" quartz/docs/                    # or just grep them
```

These notes cover what's specific to *this* vault and what was non-obvious in practice. For exhaustive option lists, read `quartz/docs/`.

---

## Related
- [[tools/quartz/02-configuration|Configuration]] — the YAML this pipeline reads
- [[tools/quartz/04-layout-and-components|Layout and Components]] — how the emit stage assembles a page
- [[tools/quartz/06-publishing-this-vault|Publishing This Vault]] — the deploy side
- [[frontend/02-next/README|Next.js]] — the same static-generation idea, with a runtime attached
- [[tools/quartz/README|Quartz notes]]
