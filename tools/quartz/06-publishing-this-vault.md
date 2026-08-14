# Publishing This Vault

**[Intermediate]** — The specific setup that turns this Obsidian vault into a site: the symlink layout, the deploy workflow, and the traps that come with putting Quartz *inside* the thing it publishes.

## The layout problem

Most Quartz sites put content inside the Quartz repo. This vault is the opposite — it's an Obsidian vault first, and Quartz lives in a `quartz/` subfolder of it. That's the right call (the notes are the artefact; Quartz is a renderer), but it creates one hazard.

```
knowledgebase/                 ← the Obsidian vault, and the git repo
├── git/  devops/  ai-ml/ …    ← the actual notes
├── .github/workflows/deploy.yml
└── quartz/                    ← Quartz lives INSIDE the vault
    ├── quartz.config.yaml
    ├── content/               ← per-folder symlinks back out to the vault
    │   ├── git -> ../../git
    │   ├── devops -> ../../devops
    │   └── …
    └── public/                ← build output
```

> **Never symlink the vault root into `content/`.** Because `quartz/` sits *inside* the vault, `content/ -> ../..` makes `content/quartz/content/quartz/…` — a filesystem cycle the build walks until it dies. Symlink each top-level folder individually.

The cost is that a new top-level domain needs a new symlink:

```bash
cd quartz/content && ln -s ../../robotics robotics
```

Forget it and the folder silently doesn't publish. Worth checking after adding a domain:

```bash
# every top-level vault folder that ISN'T symlinked into content/
cd /home/kingsleydaprime/code/personal/knowledgebase
for d in */; do
  d=${d%/}
  [ "$d" = "quartz" ] && continue
  [ -e "quartz/content/$d" ] || echo "NOT PUBLISHED: $d"
done
```

## The landing page is not the README

`quartz/content/index.md` is the published site's landing page and is **its own file** — it used to symlink to the vault `README.md`, and that was wrong. A repo README and a site landing page want genuinely different things: the README orients someone reading source on GitHub, the landing page welcomes a visitor with no context.

Edit both when the vault's shape changes. This is the easiest thing in the whole setup to forget.

## The deploy workflow

`.github/workflows/deploy.yml` — a real, working pipeline, and the grounding example the [[devops/06-ci-cd/02-ci-cd-tools|CI/CD tools note]] dissects.

```yaml
on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write        # OIDC — no stored deploy key

concurrency:
  group: "pages"
  cancel-in-progress: false
```

The build job, with the vault-specific bits called out:

```yaml
    defaults:
      run:
        working-directory: quartz     # Quartz isn't at the repo root
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0              # full history — see below
      - uses: actions/setup-node@v6
        with: { node-version: 24 }
      - uses: actions/cache@v5        # npm cache, keyed on package-lock
      - uses: actions/cache@v5        # plugin cache, keyed on quartz.lock.json
      - run: npm ci
      - run: npx quartz plugin install
      - run: npx quartz build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: quartz/public         # NOT affected by working-directory
```

Three things worth remembering:

**`fetch-depth: 0` is load-bearing.** The `created-modified-date` plugin resolves dates via frontmatter → git → filesystem. A shallow clone has no history, so every page would claim to be modified today. This is the single most common "why are all my dates wrong" cause.

**`working-directory` does not apply to `uses:` steps.** Only `run:` steps. That's why the artifact path is `quartz/public` while the build commands assume `quartz/` as cwd. Mixing this up produces "no files found" at the upload step.

**Two caches, keyed differently.** `~/.npm` on `package-lock.json`, and `.quartz/plugins` on `quartz.lock.json`. The plugin cache matters in v5 because plugins are separate packages fetched at install time.

## Deploying, in practice

Nothing to run by hand — push to `main` and Actions builds and deploys. To watch it:

```bash
gh run watch                    # follow the current run live
gh run view --log-failed        # only the failed steps, if it breaks
```

(From [[git/15-the-github-cli|The GitHub CLI]].)

## Local preview

```bash
cd quartz && npx quartz build --serve      # http://localhost:8080
```

Hot reload covers content edits (fast, incremental) and config/style edits (full module rebuild). Two caveats:

- Config hot-reload leaks ~350kB per reload by design — restart occasionally during heavy config work.
- `public/` is **not** cleaned by `--serve` in a way that removes deleted pages. After renaming or deleting notes, a stale `public/` can still serve the old URLs locally. A fresh `npx quartz build` clears the output directory first.

## Keeping notes out of the site

Three separate mechanisms, easy to confuse:

| Mechanism | Where | Effect |
|---|---|---|
| `ignorePatterns` | `quartz.config.yaml` | never enters the site at all |
| `remove-draft` plugin | frontmatter `draft: true` | dropped at filter stage |
| `.gitignore` | repo root | never reaches the runner, so never builds |

This vault uses all three: `sources/**` and `**/*transcript*` via `ignorePatterns` (raw inputs, and they'd otherwise dominate search and the graph), and `blog-drafts/` plus `blog-ideas.md` via `.gitignore` (local drafts, deliberately never published).

The `.gitignore` route is the only one that keeps content off *GitHub* as well as off the site. Worth knowing which problem you're solving.

---

## Related
- [[devops/06-ci-cd/02-ci-cd-tools|CI/CD Tools]] — this workflow annotated line by line
- [[devops/06-ci-cd/03-github-actions-fundamentals|GitHub Actions Fundamentals]] — the syntax it's written in
- [[git/15-the-github-cli|The GitHub CLI]] — watching the deploy from the terminal
- [[tools/quartz/02-configuration|Configuration]] — `ignorePatterns` and the plugin list
- [[tools/quartz/README|Quartz notes]]
