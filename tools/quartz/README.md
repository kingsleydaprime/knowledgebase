# Quartz

The static site generator that publishes this vault. These notes exist because a real amount of Quartz knowledge had accumulated — in config comments, in a debugging session, in commit messages — with **nowhere to live**. Every other tool touched in this vault got a note; the one rendering the vault didn't.

**Fully grounded.** Nothing here is generic Quartz documentation — it's this site's actual configuration, the decisions behind it, and the things that were only learned by getting them wrong. Quartz ships exhaustive reference docs *inside this repo* at `quartz/docs/`; read those for complete option lists.

> **The most useful habit:** in Quartz v5, plugins are installed npm packages under `node_modules/@quartz-community/`. When the docs are ambiguous, read the shipped source — it's version-matched and unambiguous. That's how the graph link-colour behaviour in note 05 was pinned down, after the docs turned out not to mention it at all.

## Reading order

1. [[tools/quartz/01-how-quartz-works|How Quartz Works]] — **[Intermediate]** — the build pipeline (glob → parse → filter → emit), why some plugins must be emitters, the `"nav"` event, and how v5 differs from every v4 tutorial online
2. [[tools/quartz/02-configuration|Configuration]] — **[Intermediate]** — `quartz.config.yaml` section by section; `order` vs `priority`; the transformer chain and why its sequence matters
3. [[tools/quartz/03-theming-and-styling|Theming and Styling]] — **[Intermediate]** — the eight colour variables and what each *actually* drives, palette choices for long-form reading, and `custom.scss` as the extension point
4. [[tools/quartz/04-layout-and-components|Layout and Components]] — **[Intermediate]** — the eight slots, groups, conditional rendering, per-page-type overrides, and page frames
5. [[tools/quartz/05-the-graph-view|The Graph View]] — **[Intermediate]** — every option, tuning for 855 notes instead of 50, and the link-colour mechanic that makes a working graph look broken
6. [[tools/quartz/06-publishing-this-vault|Publishing This Vault]] — **[Intermediate]** — the symlink layout and its one hazard, the deploy workflow, and the three different ways to keep a note off the site

## The findings worth remembering

Three things here cost real time and aren't in any documentation:

- **`--lightgray` is the graph's link colour**, not just a border colour. The graph paints to canvas and reads CSS variables at draw time, so if `lightgray` sits near the background, every edge is invisible until hovered — and no graph option will fix it, because CSS can't reach a canvas. (Note 05)
- **Never symlink the vault root into `content/`.** Quartz lives inside the vault, so that creates a filesystem cycle. Symlink each top-level folder. (Note 06)
- **`fetch-depth: 0` in the deploy workflow is load-bearing.** Dates come from git history; a shallow clone makes every page claim it was modified today. (Note 06)

## Known gaps

- **No custom component or plugin has been written yet.** That's the next real step — a dedicated `/graph` page is the obvious first one, and it's the thing note 04 stops short of
- **No custom page frame**, for the same reason
- **The `bases` and `canvas` page types are enabled but unused** — Obsidian Bases and Canvas files would render, but this vault has none
- **Search, popovers and SPA routing are used but not studied** — they work, and nobody has looked at how

---

## Related
- [[tools/quartz/01-how-quartz-works|Start here]]
- [[devops/06-ci-cd/02-ci-cd-tools|CI/CD Tools]] — the deploy pipeline dissected as a teaching example
- [[git/15-the-github-cli|The GitHub CLI]] — `gh run watch` for following a deploy
- [[frontend/02-next/README|Next.js]] — static generation with a runtime attached, for contrast
- [[README|Vault README]] — what this site is publishing
