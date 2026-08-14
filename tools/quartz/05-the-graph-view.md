# The Graph View

**[Intermediate]** — Every option, what it does at 855 notes rather than at 50, and the colour mechanic that makes links look broken when they aren't.

## Local vs global

Two graphs, configured separately:

- **Local** — the panel in the right sidebar. Shows the current note and everything within `depth` hops.
- **Global** — every note in the vault. Opens as a **modal** via the small network icon at the top-right of the local panel. It has no URL of its own; see [[tools/quartz/04-layout-and-components|Layout and Components]] for what a real `/graph` page would require.

Node radius is proportional to total links in + out, so hubs are visibly bigger. Visited notes render in a different colour, like browser link history.

The graph requires the `content-index` emitter — it needs the whole link map, which only exists after every file is parsed.

## Options

```yaml
options:
  localGraph:
    depth: 2            # hops from the current note; -1 = everything
    scale: 1.1          # initial zoom (higher = closer)
    repelForce: 0.6     # how hard nodes push each other apart
    centerForce: 0.3    # how hard they're pulled to the middle
    linkDistance: 35    # target edge length
    fontSize: 0.5       # label size
    opacityScale: 1.2   # how fast labels fade with zoom
    showTags: false
    focusOnHover: true  # dim everything not connected to the hovered node
    enableRadial: false
    drag: true
    zoom: true
    removeTags: []
```

## Tuning for a large vault

The defaults are built for a ~100-note garden. At 855 densely cross-linked notes they collapse into an unreadable blob. What actually mattered here:

**`enableRadial: false`** — the single biggest change. Radial layout forces every node into a ring, which destroys the domain clustering that makes a large graph legible in the first place. Force-directed layout lets `git/`, `devops/`, `ai-ml/` settle into visible clusters. The default is `true` for the global graph; turning it off is what makes the global view worth opening.

**`repelForce` up (0.9 global, 0.6 local)** — at scale, default repulsion leaves nodes overlapping.

**`linkDistance` up (45 global, 35 local)** — more room between connected nodes, fewer crossing edges.

**`fontSize` down (0.45 global, 0.5 local)** — 855 labels at the default 0.6 is a solid mat of overlapping text.

**`showTags: false`** — no note in this vault uses frontmatter tags, so tag nodes would be pure noise. If you never tag, turn this off everywhere.

**`scale` down for global (0.65)** — start zoomed out enough to see the shape.

`focusOnHover: true` earns its place at this size: hovering dims everything not connected, which is the only practical way to trace one note's neighbourhood in a dense graph.

## The link-colour mechanic

The thing that looks like a bug and isn't — or rather, is a *palette* bug that looks like a *graph* bug.

Reading the shipped source:

```js
// @quartz-community/graph — link rendering
function Ve() {
  for (...) { l.alpha = 1; l.color = l.active ? ee : te }
}
// ee = --gray        (hovered)
// te = --lightgray   (normal)
```

**Links are drawn at full opacity all the time.** Hovering changes only the colour. So if `--lightgray` is close to `--light` (the page background), every edge is invisible until hovered, and it reads as "the graph only shows paths on hover."

That was exactly this vault's symptom: `lightgray: #2f2d33` against `light: #17161a` is roughly **1.3:1** contrast. The fix was lifting `--lightgray`, not touching any graph option.

Two things follow:

1. **`opacityScale` is not the knob.** It governs how labels fade with zoom, not link visibility.
2. **CSS cannot fix it.** The graph paints to a PIXI canvas and reads the variables off `document.documentElement` at draw time. There is no DOM element per link to style. The only lever is the variable — see [[tools/quartz/03-theming-and-styling|Theming and Styling]] for the compensating trick.

The node-dimming path is separate and *does* respect `focusOnHover`:

```js
function Ke() { ... _u !== null && Oe && (F = l.active ? 1 : .2); l.gfx.alpha = F }
//                              ^^ Oe = focusOnHover
```

Note the link function has no `focusOnHover` guard — links dim on hover regardless of that setting. Only nodes respect it.

## Sizing the panel

Neither the panel height nor the modal size is configurable in YAML. Both are CSS:

```scss
.graph .graph-outer { height: 320px; }          // default 250px

.graph > .global-graph-outer > .global-graph-container {
  width: 92vw;   // default 80vw
  height: 90vh;  // default 80vh
}
```

Worth raising the panel height whenever `localGraph.depth` is above 1 — depth 2 pulls in far more nodes than 250px can show.

## Debugging it

The rendered config is inlined into the HTML as a `data-cfg` attribute, which is the fastest way to confirm your YAML actually took effect:

```bash
grep -o 'class="graph-container" data-cfg="[^"]*"' public/git/README.html
```

If those values are the plugin defaults rather than yours, the likely cause is a **stale build** — `public/` isn't regenerated until you run a build, and an old `public/` will happily show you settings from weeks ago.

---

## Related
- [[tools/quartz/03-theming-and-styling|Theming and Styling]] — why `--lightgray` is the load-bearing variable
- [[tools/quartz/04-layout-and-components|Layout and Components]] — what a dedicated graph page would take
- [[tools/quartz/01-how-quartz-works|How Quartz Works]] — why the graph must be an emitter, not a transformer
- [[tools/quartz/README|Quartz notes]]
