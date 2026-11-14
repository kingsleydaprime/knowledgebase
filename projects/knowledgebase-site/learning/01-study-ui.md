# 01 — The study UI: how the site became something you use

The Quartz site used to read like a journal: filenames as titles, no way forward except the sidebar, nothing to press. This note walks through what was added on 2026-11-14 and how each part works, so you could rebuild it yourself.

## The goal, in one line

Every note gets a real title, a "Mark as done" button and next/previous cards. Folder pages show progress and a Continue button. The home page is a dashboard of subjects. A Subjects button on every page jumps anywhere instantly, all with no login and no server.

## The three pieces

| Piece | File | Runs | Job |
|---|---|---|---|
| Build-time HTML | `quartz/quartz/plugins/transformers/studyNav.ts` | Once, when the site builds | Works out titles, order, next/previous, totals. Writes plain HTML into each page |
| Browser script | `quartz/quartz/components/scripts/interactive-learning.inline.ts` (section 5) | In the reader's browser, on every page | Remembers what you finished (localStorage) and fills in progress bars and Continue buttons |
| Styles | `quartz/quartz/styles/study.scss` | In the browser | Colours, cards, buttons, the sheet, the answer cards |

The split is the main idea. **Anything that's the same for every reader is decided at build time. Only what's personal (what *you* finished) is decided in the browser.** That's why the pager and the Subjects sheet appear instantly: they're already in the HTML, so nothing has to be fetched first.

### Why the sidebar was slow

The explorer draws itself from `static/contentIndex.json`, which holds the full text of every note so search can work. On 2026-11-14 that file was **21 MB**. The explorer can't draw a single folder until all of it has downloaded. The Subjects sheet avoids the problem by being plain HTML in every page.

## Piece 1: the transformer (build time)

Quartz turns each markdown file into HTML through a pipeline of plugins. A **transformer** gets to change each file on the way through. Ours works on the HTML tree (called *hast*, the HTML abstract syntax tree), after the markdown has been converted.

### The note tree

`buildTree()` runs once per build. It goes through `ctx.allFiles` (every file Quartz found) and builds:

1. **`notes`**: every note, keyed by its "node". A node is the slug without a trailing `/index`, so `databases/index` and `databases` are the same thing: the Databases folder.
2. **`children`**: for each node, its child notes in order. The order comes from the number at the start of the filename (`01-`, `02-`, ... `10-`), compared as numbers, so `10` comes after `9`.
3. **`totals`**: how many notes sit under each folder, at any depth. Progress bars use this as their total.

### Titles

Quartz uses the filename as the title unless the frontmatter sets one, which is why pages said `01-what-a-database-is`. `readTitle()` reads the raw file and takes, in order:
1. the frontmatter `title`,
2. else the first `# Heading` that isn't inside a code block (it tracks ``` fences, so a Python comment like `# setup` isn't mistaken for a heading),
3. else a cleaned-up filename.

Then the plugin removes that first `<h1>` from the page, because Quartz already prints the title at the top. Otherwise you'd see it twice.

### Next and previous

`lessonEnd()` finds the note's siblings and picks the ones either side. It has two extra rules:
- **A folder's own page** points "Start →" at its first child.
- **The last note in a folder** points "Next section →" at the folder's next sibling, so you can read straight through a whole course.

### Why it runs last

Quartz has a `crawl-links` plugin that collects every link in a note, for backlinks and the graph. If our pager ran *before* it, every note would appear to link to its neighbours, and the graph would fill with fake connections. So `config-loader.ts` adds `StudyNav` **after** all the other transformers. This was checked across all 915 notes whose next note isn't mentioned in their text: zero pager links leaked into the graph.

## Piece 2: the browser script

The HTML from piece 1 carries `data-*` attributes, such as `data-prefix="databases/"` and `data-total="26"` on a progress bar. The script reads those, plus localStorage, and fills things in.

**What's stored** (localStorage, this browser only):
- `kb_done_v1` maps each finished note's slug to `{ t: when, href: its path }`.
- `kb_last_v1` holds the last note you opened, for the home page's Continue button.

**Counting progress:** for a bar with prefix `databases/`, count the finished slugs that start with `databases/`. Cap the count at the total, because a renamed note can leave an old entry behind.

**SPA navigation:** Quartz doesn't reload the page when you click a link. It swaps the content and fires a `nav` event, so every setup function runs on `nav`. Listeners are removed through `window.addCleanup`, otherwise each navigation would stack another click handler on the page.

**The double-fire bug avoided:** Quartz also fires `render` on the same page. Without the `data-bound` guard, one tap on "Mark as done" would run two handlers: done, then immediately undone.

**The Subjects button** is moved from the article to `<body>` when the page loads. A `position: fixed` element inside a transformed parent stops being fixed to the screen, so moving it out keeps it pinned to the corner.

## Piece 3: the styles

- **Palette:** blue (`--secondary`) and green (`--tertiary`) are set in `quartz.config.yaml`. Every colour in `study.scss` comes from those two, so dark mode works automatically.
- **Subject colours** use one number per group, the *hue* (`--su-hue`). Cards build their background, border and text from `hsl(hue, saturation, lightness)`, and dark mode only changes the lightness values. One number gives a full matching colour set.
- **Answers as flashcards:** lessons already write checks as a question followed by `<details><summary>Answer</summary>`. Styling `details` as a card with "Tap to reveal" turned every existing check into a flashcard without editing a single lesson.

## Things that were switched off, and why

- **`@quartz-themes/core`:** it loaded Obsidian's default theme, about 418 KB of CSS on every page, and replaced the palette with Obsidian purple. That was a big part of the journal look.
- **The `quartz-fonts` defaults:** the fonts are now set explicitly (Plus Jakarta Sans for headings, Inter for text, JetBrains Mono for code), because the plugin ignored the theme's typography setting.

## Bugs fixed on the way

- **Callouts had no colour.** The September commit replaced the default `[data-callout]` rule with the quiz rule, so `[!note]` and every type without its own rule lost its colour. The default is restored in `callouts.scss`.
- **`g h` and `g p` went to the wrong place.** They used `/`, which on GitHub Pages is `kingsleydaprime.github.io`, not `/knowledgebase/`. They now read the home link from the site title.
- **`j` and `k` guessed the next note** from whatever links were on the page. They now press the pager's real next and previous links.

## Try it yourself

1. Run `npx quartz build --serve` in `quartz/` and open a lesson. Press "Mark as done" and watch the Databases card on the home page.
2. In DevTools → Application → Local Storage, look at `kb_done_v1`, delete it, and watch everything reset.
3. **Exercise:** add a "Mark all in this folder as done" button to the folder hero. Hint: the hero already carries every note's slug in `data-order`.
