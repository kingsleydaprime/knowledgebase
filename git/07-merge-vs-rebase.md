# Merge vs Rebase — When to Use Which

**[Intermediate]** — The honest answer to the most-argued question in Git: the tradeoff, the cases for each, the rules a team can actually hold to, and a decision flowchart.

This is one of the most debated topics in Git. Here's the complete, honest answer.

## The Core Tradeoff

**Merge** preserves the true history of what happened. The graph shows branches, parallel development, and where things came together. It's honest — this is what actually occurred. But in large teams with many branches, the graph becomes a tangled web.

**Rebase** creates a clean, linear history. It tells a simplified story: "these changes were developed in sequence." Easier to read with `git log`, easier to use `git bisect`, easier to review. But it rewrites commits — the SHA changes, and you lose the context of when something was actually developed.

Neither is universally correct. The right answer depends on context.

## Use Merge When

**Merging a completed feature branch into main/develop:**

```bash
git checkout main
git merge --no-ff feature/user-auth
```

Use `--no-ff` to always create a merge commit even if fast-forward is possible. This preserves the fact that these commits came from a feature branch — you can see the branch in the graph and revert the entire feature by reverting one commit.

**Pulling from a shared remote branch:**

```bash
git pull origin main   # = fetch + merge
```

When multiple people are working on the same branch (e.g. `develop`), merge preserves everyone's contribution as-is.

**When working on a public/shared branch:**

Once commits are pushed and others may have pulled them, never rebase. Merge only. Rebasing would rewrite history that others depend on.

**Merging hotfixes into both main and develop:**

```bash
git checkout main && git merge --no-ff hotfix/critical-fix
git checkout develop && git merge --no-ff hotfix/critical-fix
```

## Use Rebase When

**Updating your local feature branch with latest main:**

```bash
git checkout feature/my-feature
git rebase main
```

This is the most common use. You want your feature to be based on the latest main so it merges cleanly. Your commits go on top of main's latest — no merge commit needed, clean linear history.

**Cleaning up your commit history before opening a PR:**

```bash
git rebase -i main
# Squash WIP commits, fix typos in messages, reorder for logical flow
```

Before sharing your work, clean it up. Squash the "fix typo" and "WIP: halfway done" commits. The reviewer should see a clean series of logical commits, not your development stream of consciousness.

**Keeping a long-running feature branch up to date:**

```bash
# Daily or before PR:
git fetch origin
git rebase origin/main
```

Repeatedly merging main into a feature branch creates a noisy history with many merge commits. Rebasing keeps the feature branch clean.

**Splitting a monolithic commit into logical parts:**

```bash
git rebase -i HEAD~1   # Mark the commit as 'edit'
git reset HEAD~1       # Unstage all changes
git add -p             # Selectively stage part 1
git commit -m "part 1"
git add -p             # Stage part 2
git commit -m "part 2"
git rebase --continue
```

## Never Rebase When

- The branch has been pushed and others have pulled it — rewriting shared history causes chaos
- You're on `main`, `develop`, or any shared branch — these are sacred; their history is immutable
- You need to preserve the exact authorship and timing of commits (auditing, compliance)
- You don't fully understand what the rebase will do — merge is always safer

## The Practical Team Rules

```
Rule 1: Main and develop are immutable — never rebase them.

Rule 2: Feature branches are yours until you open a PR.
        Rebase freely on your own branches.

Rule 3: Once a PR is open and others have reviewed/commented,
        avoid rebasing — it makes review harder.
        If you must, warn the team.

Rule 4: Never push --force to a shared branch.
        Use --force-with-lease if you must force-push your own branch.

Rule 5: When in doubt, merge. It's always recoverable.
        A bad rebase can be recovered with reflog but it's painful.
```

## The Decision Flowchart

```
Are you updating your local feature branch with latest from main?
  └─ Yes → rebase (git rebase main)

Are you cleaning up commits before a PR?
  └─ Yes → interactive rebase (git rebase -i main)

Are you merging a completed feature into main/develop?
  └─ Yes → merge with --no-ff (git merge --no-ff feature)

Are these commits already pushed to a remote anyone else has access to?
  └─ Yes → never rebase → merge only

Are you pulling from a shared branch?
  └─ Yes → merge (or configure pull.rebase = false)

Are you working alone on a branch no one else touches?
  └─ Yes → rebase freely
```


---

## Related
- [[git/05-merging|Merging]] — the mechanics of one option
- [[git/06-rebasing|Rebasing]] — the mechanics of the other
- [[git/13-branching-strategies|Branching Strategies]] — the team context that settles most of these calls
- [[git/README|Git course map]]
