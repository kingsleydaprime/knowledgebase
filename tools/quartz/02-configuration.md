# Configuration

**[Intermediate]** — `quartz.config.yaml` section by section, grounded in this vault's actual file. In v5 this one file holds site settings, theme, the full plugin list, and the layout.

## The shape of the file

```yaml
configuration:      # site-wide settings and theme
  pageTitle: ...
  theme: ...
plugins:            # every plugin, its options, and where it renders
  - source: "@quartz-community/graph"
    enabled: true
    options: {...}
    layout: {...}
layout:             # groups and per-page-type overrides
  groups: ...
  byPageType: ...
```

The schema is published, so an editor with the YAML language server gives you completion and validation. That's the first line at the top of the file:

```yaml
# yaml-language-server: $schema=./quartz/plugins/quartz-plugins.schema.json
```

Worth keeping — it catches typo'd option names before a build does.

## `configuration:`

```yaml
configuration:
  pageTitle: Kingsley's Knowledge Base   # sidebar title and <title> suffix
  pageTitleSuffix: ""
  enableSPA: true         # client-side navigation, no full page reloads
  enablePopovers: true    # hover an internal link to preview the target
  locale: en-US
  baseUrl: kingsleydaprime.github.io/knowledgebase
```

**`baseUrl` has no protocol and no trailing slash.** It's used for sitemap/RSS generation and for resolving absolute links. Getting it wrong produces a site that works locally and has broken links in production — a classic and annoying failure.

**`enablePopovers`** is doing quiet heavy lifting in a vault this densely cross-linked: it fetches the target page and shows a preview on hover, which turns a wall of `[[wikilinks]]` into something you can skim without navigating.

### `ignorePatterns`

```yaml
  ignorePatterns:
    - private
    - templates
    - .obsidian
    - sources/**        # raw transcripts and course PDFs — inputs, not notes
    - "**/*transcript*"
```

Glob patterns matched against the file path. The `sources/**` entry is the load-bearing one here: without it, raw source material dominates both site search and the graph, drowning the actual notes. An input is not a note.

Note this is *filtering*, not exclusion from parsing — see the pipeline in [[tools/quartz/01-how-quartz-works|How Quartz Works]].

## `plugins:`

Every plugin entry has the same four keys:

```yaml
  - source: "@quartz-community/graph"   # npm package (or github:owner/repo)
    enabled: true                        # toggle without deleting the config
    options: {...}                       # plugin-specific settings
    order: 30                            # transformer order in the parse chain
    layout:                              # where it renders, if it's a component
      position: right
      priority: 10
```

**`order` vs `priority`** confuses people. They're unrelated:

- **`order`** — position in the *build* chain. Matters for transformers, because they mutate the syntax tree in sequence. `obsidian-flavored-markdown` (30) must run before `crawl-links` (60), or the wikilinks it produces won't be resolved into hrefs.
- **`priority`** — position in the *rendered layout*. Lower renders first/higher up within its position. The graph (10) sits above the table of contents (30), which sits above backlinks (50).

Changing `priority` rearranges the sidebar. Changing `order` can break the build in subtle ways. Don't reach for one when you mean the other.

**`enabled: false`** is the right way to turn something off. This vault keeps `citations`, `tag-list`, `comments`, `recent-notes` and `stacked-pages` configured-but-disabled — the config documents what was considered, and re-enabling is a one-word change.

## The transformer chain, in order

The `order` values in this vault's config, and why they're sequenced that way:

| order | plugin | does |
|---|---|---|
| 5 | `note-properties` | render frontmatter as a properties block |
| 10 | `created-modified-date` | resolve dates from frontmatter → git → filesystem |
| 20 | `syntax-highlighting` | Shiki, `github-light` / `github-dark` |
| 30 | `obsidian-flavored-markdown` | wikilinks, callouts, transclusions, tags, mermaid |
| 40 | `github-flavored-markdown` | tables, strikethrough, task lists, autolinks |
| 45 | `unlisted-pages` | |
| 50 | `table-of-contents`, `bases-page`, `excalidraw` | |
| 60 | `crawl-links` | turn resolved wikilinks into real hrefs |
| 70 | `description` | generate meta descriptions for OG tags |
| 80 | `latex` | KaTeX |
| 90 | `hard-line-breaks` | |

`created-modified-date` with `priority: [frontmatter, git, filesystem]` is why pages show sensible "last updated" dates without any frontmatter: it falls back to the git history. It's also why the deploy workflow needs `fetch-depth: 0` — a shallow clone has no history to read, and every page would claim to be modified today.

## `obsidian-flavored-markdown`

The plugin that makes this vault's Markdown work at all:

```yaml
    options:
      wikilinks: true            # [[note]] and [[note|alias]]
      callouts: true             # > [!note] blocks
      mermaid: true              # ```mermaid diagrams
      parseTags: true
      parseArrows: true          # -> becomes →
      parseBlockReferences: true
      enableInHtmlEmbed: false   # do NOT render raw HTML inside markdown
      enableYouTubeEmbed: true
      enableVideoEmbed: true
      enableCheckbox: true
```

`enableInHtmlEmbed: false` is a security-relevant default: raw HTML in a note isn't rendered. Worth remembering if you ever try to drop a `<script>` or a custom `<div>` into a note and nothing happens — that's this setting, working correctly.

## TypeScript overrides — `quartz.ts`

Some options are *functions* and can't be expressed in YAML — sort orders, filters, display-name mappers. Those go in `quartz.ts`, which currently just loads the YAML:

```ts
import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"

const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
```

To customise the explorer's sorting, for instance, you'd call the plugin's override **before** `loadQuartzConfig()`:

```ts
import * as ExternalPlugin from "./.quartz/plugins"

ExternalPlugin.Explorer({
  sortFn: (a, b) => a.displayName.localeCompare(b.displayName, undefined, { numeric: true }),
})
```

The default sort is already `numeric: true`, which is exactly why the numbered-file convention across this vault (`01-`, `02-`, … `10-`) sorts correctly instead of putting `10-` before `2-`. That convention exists for the file tree *and* for this sidebar.

## Checking your work

YAML fails silently in annoying ways. Before rebuilding:

```bash
python3 -c "import yaml; d=yaml.safe_load(open('quartz.config.yaml')); print(len(d['plugins']), 'plugins parsed OK')"
```

---

## Related
- [[tools/quartz/03-theming-and-styling|Theming and Styling]] — the `theme:` block in detail
- [[tools/quartz/04-layout-and-components|Layout and Components]] — the `layout:` block in detail
- [[tools/quartz/01-how-quartz-works|How Quartz Works]] — what `order` actually orders
- [[tools/quartz/README|Quartz notes]]
