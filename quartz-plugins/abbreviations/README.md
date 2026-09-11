# Abbreviations

Wraps known acronyms in `<abbr title="...">` at build time, so the full meaning
appears on hover without putting the expansion into the markdown source.

**Why a plugin rather than writing it inline.** The vault uses roughly 3,100
acronym occurrences. Writing `API (application programming interface)` at every
one would add about 167 KB of markup to the notes and make them unpleasant to
edit in Obsidian. The plugin keeps the source clean and gives every occurrence —
not just the first — its full meaning.

## What it does and does not touch

Expanded: ordinary prose, list items, table cells.

Left alone: `code`, `pre`, `a`, existing `abbr`, `script`, `style`, and every
heading. That matters — a variable named `dfs` or a file called `API.md` must
never be rewritten.

## Editing the list

`glossary.json` is the single source of truth: a flat map of acronym to meaning.
Longer keys win, so `SCCs` is matched before `SCC`. Add an entry and rebuild.

Deliberately excluded, because they are words rather than acronyms in this vault:
`AND`, `OR`, `NOT`, `XOR` as logic gates in prose, `SELECT` as SQL, `II` as a
numeral, `README` and `ID`.

## Install

```shell
npx quartz plugin add ./quartz-plugins/abbreviations
npx quartz build --serve
```

## Limitation

`<abbr title>` shows on hover, which touch devices do not have. The published
[[glossary]] note exists so the same information is reachable on a phone.
