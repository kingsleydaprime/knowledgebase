# Layout and Components

**[Intermediate]** — Where things appear on the page: the eight layout slots, how plugins claim one, groups, per-page-type overrides, and page frames.

## The slots

Every page is assembled from named regions. A component plugin declares which one it wants:

```
┌──────────────────────────────────────────────────┐
│ head  (metadata only — not visible)              │
├──────────┬───────────────────────────┬───────────┤
│          │ header                    │           │
│          ├───────────────────────────┤           │
│  left    │ beforeBody                │  right    │
│          ├───────────────────────────┤           │
│          │ pageBody                  │           │
│          ├───────────────────────────┤           │
│          │ afterBody                 │           │
├──────────┴───────────────────────────┴───────────┤
│ footer                                           │
└──────────────────────────────────────────────────┘
```

- `left` — vertical on desktop/tablet, horizontal on mobile
- `right` — vertical on desktop, horizontal on tablet and mobile
- `beforeBody` / `afterBody` — stacked vertically, full content width
- `head` — the `<head>` tag; metadata, scripts, styles

## Claiming a slot

```yaml
  - source: "@quartz-community/graph"
    enabled: true
    layout:
      position: right
      priority: 10
```

**Lower `priority` renders first** (higher up the column). This vault's right sidebar:

| priority | component |
|---|---|
| 10 | graph |
| 30 | table-of-contents |
| 50 | backlinks |

Reordering the sidebar is just changing those numbers. Note the priorities are declared on *each plugin's own* config block, not in one central list — so to understand a column you have to read them all. `grep -A3 "position: right" quartz.config.yaml` is the quick way.

## Groups

Groups pack several components into one flex container, which is how the search box, dark-mode toggle and reader-mode button sit on a single row instead of stacking:

```yaml
plugins:
  - source: "@quartz-community/search"
    layout:
      position: left
      priority: 20
      group: toolbar
      groupOptions:
        grow: true          # search takes the leftover width
  - source: "@quartz-community/darkmode"
    layout:
      position: left
      priority: 30
      group: toolbar

layout:
  groups:
    toolbar:
      priority: 35         # where the whole group sits in the column
      direction: row
      gap: 0.5rem
```

The group has its own `priority` for placement in the column; members' priorities order them *within* the group.

## Conditional rendering

```yaml
  - source: "@quartz-community/breadcrumbs"
    layout:
      position: beforeBody
      priority: 5
      condition: not-index
```

Two built-in conditions: `not-index` (hidden on the root landing page) and `has-tags`. There's also `display` for viewport targeting:

```yaml
  - source: "@quartz-community/spacer"
    layout:
      display: mobile-only
```

Breadcrumbs use `not-index` for a good reason — a breadcrumb trail on the home page reads as "Home ❯" and nothing else, which is noise.

## Per-page-type overrides

Not every page type wants the same furniture:

```yaml
layout:
  byPageType:
    "404":
      positions:
        beforeBody: []
        left: []
        right: []        # strip everything — a 404 needs no sidebars
    folder:
      exclude:
        - reader-mode    # meaningless on an auto-generated index
      positions:
        right: []
    tag:
      exclude: [reader-mode]
      positions:
        right: []
```

Page types are a fixed set: `content`, `folder`, `tag`, `404`, `canvas`, `bases`. `exclude` removes named components; `positions: { x: [] }` empties a whole slot.

Folder and tag pages drop the right sidebar because a graph and a table of contents for a generated list of links is filler.

## Page frames

A frame controls the outer HTML skeleton — how the slots are arranged. Three ship with Quartz:

| Frame | Layout | Used by |
|---|---|---|
| `default` | three columns: left sidebar, centre, right sidebar | content, folder, tag, bases |
| `full-width` | no sidebars, single centre column | — |
| `minimal` | no sidebars, no header chrome; content and footer only | 404 |

Override per page type:

```yaml
layout:
  byPageType:
    canvas:
      template: minimal
```

Frames are applied as `data-frame` on `.page`, so they're targetable in CSS:

```scss
.page[data-frame="my-frame"] > #quartz-body { /* custom grid */ }
```

Custom frames go in `quartz/components/frames/` implementing the `PageFrame` interface, or ship from a plugin. **This is the mechanism you'd need for a dedicated full-screen graph page** — the global graph only renders inside a modal, so a real `/graph` URL needs a custom component plus a frame. Not a config change.

## Resolution order

When a page renders, its frame is picked by:

1. `layout.byPageType.<name>.template` in YAML
2. a frame registered by a plugin
3. the `frame` property in the page-type plugin's source
4. fallback: `default`

## Reading the rendered output

When a layout question is genuinely ambiguous, the built HTML answers it faster than the docs:

```bash
python3 -c "
import re,pathlib
h=pathlib.Path('public/git/README.html').read_text()
for c in ['left sidebar','right sidebar','page-header','page-footer']:
    print(c, '->', h.count(c))"
```

---

## Related
- [[tools/quartz/02-configuration|Configuration]] — where all of this is declared
- [[tools/quartz/03-theming-and-styling|Theming and Styling]] — `data-slug` and `data-frame` scoping
- [[tools/quartz/01-how-quartz-works|How Quartz Works]] — the emit stage that assembles these slots
- [[tools/quartz/README|Quartz notes]]
