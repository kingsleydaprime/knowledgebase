# Git — Projects

*A 17-note course on a tool you use every day. The reps are unusual here: **most of them are recoveries from disasters you cause on purpose**, in a throwaway repo, so the real one is never the first time.*

Difficulty: 🟢 starter (hours–days) · 🟡 intermediate (a week or two) · 🔴 ambitious / portfolio-grade. ⭐ = highest signal.

## The ladder

- 🟢 ⭐ **The disaster drill** — in a scratch repo, cause and then recover from each of: a bad `reset --hard`, a force-push over a colleague's work, a commit on the wrong branch, a deleted branch, a botched rebase, a lost stash. **Done when:** you've recovered all six using `reflog`, and it took under a minute each. **Do this once and you stop being afraid of git**, which is worth more than any other rep here. Exercises: [[git/10-undoing-things|undoing things]], [[git/git-troubleshooting|troubleshooting]].

- 🟢 **Inspect the object store by hand** — `git cat-file -p` your way from a commit to a tree to a blob. **Done when:** you've walked a commit to file contents without any porcelain command. Exercises: [[git/01-how-git-works|how git works]].

- 🟢 **Rewrite a messy branch** — take a branch with 15 "wip" commits and interactive-rebase it into 4 meaningful ones. **Done when:** each commit builds and does one thing. Exercises: [[git/06-rebasing|rebase]].

- 🟡 **Bisect a real bug** — introduce a subtle bug 30 commits back in a project, then find it with `git bisect run` and a test script. **Done when:** bisect finds it automatically. Exercises: [[git/09-investigating-history|searching history]].

- 🟡 **Write hooks that earn their keep** — a pre-commit hook that formats and lints, and a commit-msg hook enforcing Conventional Commits. **Done when:** they run on your real projects and you haven't disabled them after a week. Exercises: [[git/17-hooks-and-signing|hooks]].

- 🟡 **Run a proper PR workflow on yourself** — branch protection, required checks, a real review pass on your own PR a day later. **Done when:** you've rejected your own PR for a good reason. Exercises: [[git/13-branching-strategies|team workflow]], [[concepts/04-best-practices/README|code review]].

- 🔴 ⭐ **Build your own git** — the guide: [[build-your-own-shit/02-your-own-git|02-your-own-git]]. **Done when:** real `git log` reads a repository your program created.

## If you only do one

**The disaster drill.** An hour, and it permanently removes the low-grade fear that makes people avoid rebase, avoid history rewriting, and commit `-m "stuff"` to main.

## Related
- [[git/README|the git course]] · [[git/git-reference|command reference]]
- [[build-your-own-shit/02-your-own-git|build your own git]]
- [[project-ideas|Project Ideas]] — the vault-wide index
