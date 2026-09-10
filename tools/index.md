# Tools

Notes on the software used to do the work, rather than on the work itself. A tool earns a note here once it's been configured deliberately enough that the reasoning is worth keeping — not for every binary that gets installed.

The test: if the config file has opinions in it, the opinions belong here.

## What's here

- [[tools/quartz/index|quartz/]] — **6 notes** — the static site generator publishing this vault. Build pipeline, configuration, theming, layout, the graph view, and the deploy setup. Fully grounded in this site's actual config
- [[tools/agent-skills/index|agent-skills/]] — **1 note** — the `SKILL.md` format, its YAML frontmatter contract, and why a skill silently fails to load
- [[tools/neovim/neovim-setup|neovim-setup]] — editor configuration

## Known gaps

Things used daily with no notes yet:

- **The shell itself** — zsh config, prompt, history behaviour. Adjacent to [[devops/01-linux/12-bash-scripting|Bash Scripting]], but the interactive-shell half is uncovered
- **tmux** — if it's in the workflow
- **Docker as a local dev tool**, as distinct from [[devops/02-docker/index|Docker as deployment infrastructure]]

---

## Related
- [[devops/01-linux/index|Linux]] — the environment these tools run in
- [[git/index|Git]] — the tool with the deepest coverage, promoted out of here into its own course
- [[HOME|Vault README]]
