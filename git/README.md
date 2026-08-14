# Git & Version Control

The tool you touch more often than any other, and the one most people learn only as far as `add`, `commit`, `push`. This course goes down to the object model and back up to team workflow, because almost every confusing thing Git does stops being confusing once you know it's a content-addressable store with a few pointers on top.

**~17,000 words across 17 notes, plus a command reference and a recovery guide.** Split in August 2026 out of a single 3,168-line `git-reference.md` that was really a textbook wearing a reference's filename — the material was good, but there was no reading order and nothing linked to anything.

> **The one rule worth memorising:** never rewrite history that someone else may have pulled. Everything else in Git is recoverable — the reflog holds your commits for 30 days and `git reset --hard` is undoable more often than people think. Rewriting shared history is the one mistake that costs *other people* their afternoon, and no command of yours can fix it for them.

## Reading order

The notes build on each other. Sections 1–11 are Git as a solo tool; 12–15 are Git as a team tool; 16–17 are the things you reach for occasionally.

**Foundations**

1. [[git/01-how-git-works|How Git Actually Works]] — **[Beginner → Intermediate]** — blobs, trees, commits and tags; refs; what's inside `.git/`. Read this first even though it feels like theory — it's what makes the rest cheap to learn
2. [[git/02-configuration-and-setup|Configuration and Setup]] — **[Beginner]** — the three config levels, a `~/.gitconfig` worth stealing, `init` / `clone` / `remote`
3. [[git/03-the-three-trees|The Three Trees]] — **[Beginner]** — working directory, index, HEAD: the model that defines what every other command means. Plus staging, committing, and `.gitignore`
4. [[git/04-branching|Branching]] — **[Beginner]** — creating, switching, tracking branches, and escaping a detached HEAD

**Integrating work**

5. [[git/05-merging|Merging]] — **[Intermediate]** — fast-forward vs three-way, conflict markers, merge strategies
6. [[git/06-rebasing|Rebasing]] — **[Intermediate → Advanced]** — replaying commits, interactive rebase, `fixup!`, `--onto`
7. [[git/07-merge-vs-rebase|Merge vs Rebase]] — **[Intermediate]** — the argument settled, with a decision flowchart. The payoff note for 5 and 6
8. [[git/08-remotes-and-collaboration|Remotes and Collaboration]] — **[Beginner → Intermediate]** — fetch vs pull, safe pushing, forks and upstreams

**Reading and repairing history**

9. [[git/09-investigating-history|Investigating History]] — **[Intermediate]** — `log` and its filters, `show`, `diff`, `blame`, `shortlog`, `bisect`
10. [[git/10-undoing-things|Undoing Things]] — **[Intermediate]** — `reset` vs `revert` vs `restore`, the reflog, stashing. Starts with a decision tree because this is where most Git panic happens
11. [[git/11-tags-and-versioning|Tags and Versioning]] — **[Intermediate]** — annotated tags and the SemVer contract they carry

**Working with other people**

12. [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — **[Beginner → Intermediate]** — Conventional Commits, messages worth reading, and repo hygiene
13. [[git/13-branching-strategies|Branching Strategies]] — **[Intermediate]** — GitHub Flow, GitFlow, trunk-based, forking; and branch naming
14. [[git/14-github-and-ci|GitHub as a Platform, and Git in CI]] — **[Intermediate]** — branch protection, CODEOWNERS, rulesets, PR practice, and how a pipeline talks to your repo
15. [[git/15-the-github-cli|The GitHub CLI (`gh`)]] — **[Intermediate]** — doing all of note 14 from the terminal: PRs, issues, releases, CI runs, and `gh api` for everything without a wrapper

**Occasional tools**

16. [[git/16-power-tools|Power Tools]] — **[Advanced]** — submodules, worktrees, patch files, cherry-pick
17. [[git/17-hooks-and-signing|Hooks and Signing]] — **[Advanced]** — pre-commit automation, Husky, GPG and SSH signatures

**Also here:**
- [[git/git-reference|git-reference]] — the commands themselves, grouped by task, for lookup rather than reading
- [[git/git-troubleshooting|git-troubleshooting]] — symptom-first recovery recipes ("I committed to the wrong branch", "I accidentally committed my .env"). Written for the moment you're panicking

## Where the reps are

Unlike most domains here, this one has an unbroken practice record: every commit in this vault and in [[projects/gees-arise/learning/01-git|Gees Arise]] and [[projects/socioboom/learning/02-git|SocioBoom]] was typed by hand, deliberately, rather than delegated. Those two project logs are the grounded companion to these notes — same commands, but in the context they actually came up in, including the mistakes.

The gap between "I've read about interactive rebase" and "I've used interactive rebase on a branch I cared about" is the whole thing. [[PRIMETECHIE|The path]] treats git fluency as a Rank I gate for exactly that reason: a merge conflict you resolved by *reading* rather than picking a side.

## Known gaps

- **No coverage of Git internals at the packfile level** — delta compression, `git gc`, and repository maintenance are mentioned but not explained
- **Monorepo tooling** (sparse-checkout, partial clone, `git filter-repo`) is absent, and matters at scale
- **GitLab and Bitbucket** are barely mentioned; the platform note is GitHub-shaped because that's what's actually been used here
