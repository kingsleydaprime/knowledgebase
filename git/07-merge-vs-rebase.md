---
id: 7e86d051-fe91-4547-aa1f-aafe434a0f86
---

# Merge vs Rebase — When to Use Which

This is one of the most debated topics in Git. Here's the complete, honest answer.

## The Core Tradeoff
<!-- bite: 2d50d51a-fb24-4d6f-92d4-08e9d53ece1f -->

**Merge** preserves the true history of what happened. The graph shows branches, parallel development, and where things came together. It's honest — this is what actually occurred. But in large teams with many branches, the graph becomes a tangled web.

**Rebase** creates a clean, linear history. It tells a simplified story: "these changes were developed in sequence." Easier to read with `git log`, easier to use `git bisect`, easier to review. But it rewrites commits — the SHA changes, and you lose the context of when something was actually developed.

Neither is universally correct. The right answer depends on context.

## Use Merge When
<!-- bite: 161d4c2b-ac13-4c97-bbec-b276ca36e3b0 -->

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
<!-- bite: 6e6333f4-a138-4316-a276-cd7abba88aa2 -->

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
<!-- bite: 182a89ba-ec51-4ab9-8a86-bfe63cb4bac7 -->

- The branch has been pushed and others have pulled it — rewriting shared history causes chaos
- You're on `main`, `develop`, or any shared branch — these are sacred; their history is immutable
- You need to preserve the exact authorship and timing of commits (auditing, compliance)
- You don't fully understand what the rebase will do — merge is always safer

## The Practical Team Rules
<!-- bite: f65ca41c-1960-4ac1-ae68-42a4ecbf886e -->

```text
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
<!-- bite: efcdff9a-bb80-4fe1-bfc4-df24df29ecb1 -->

```text
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

## Check your understanding
<!-- bite: 8add385e-132f-430f-ab3c-35d039ad76c4 -->

Try each one before you open the answer.

1. <!-- q: mcq id="063fa939" -->
   You are working alone on a local branch and want the latest `main` under your commits before opening a pull request. What should you use?

   - [x] `git rebase main`
   - [ ] `git merge --no-ff main`
   - [ ] `git push --force` to `main`
   - [ ] `git merge --squash main`

   <details><summary>Answer</summary>

   Rebase. The branch is yours and unpushed, so rewriting it is safe, and it gives a clean, straight history with no extra merge commit.

   </details>

2. <!-- q: mcq id="bf7f44c5" -->
   A finished feature branch goes into `main`. Why do many teams use `git merge --no-ff` here?

   - [ ] It is faster than a fast-forward
   - [x] It always makes a merge commit, so the feature shows up as a unit and can be reverted with one commit
   - [ ] It rewrites the feature's commits to be cleaner
   - [ ] It avoids all conflicts

   <details><summary>Answer</summary>

   The merge commit marks where the feature came in. You can see the branch in the graph, and reverting that one merge commit removes the whole feature.

   </details>

3. <!-- q: mcq id="0c1b1ea3" -->
   Which of these situations call for merge rather than rebase? Choose all that apply.

   - [x] Bringing a teammate's pushed commits on `develop` into your copy of `develop`
   - [x] The commits must keep their exact authorship and timing for an audit
   - [ ] Squashing your own "wip" commits before a pull request
   - [ ] Updating your private branch with the latest `main`

   <details><summary>Answer</summary>

   The first two. Shared history must not be rewritten, and an audit needs the true record. The last two are your own unshared commits, which is where rebase belongs.

   </details>

4. <!-- q: exact id="314450ba" answer="git push --force-with-lease" -->
   You rebased your own feature branch, which is already on the remote, so a normal push is rejected. Which push command is the safe way to overwrite it?

   <details><summary>Answer</summary>

   `git push --force-with-lease`. Unlike `--force`, it refuses if the remote has commits you haven't fetched, so you can't wipe out work someone else pushed.

   </details>

5. <!-- q: open id="0bd77717" -->
   Sum up the trade-off between merge and rebase in two or three sentences.

   <details><summary>Answer</summary>

   Merge keeps the true history: branches, parallel work and where they joined. It is honest, but busy teams end up with a tangled graph. Rebase gives a clean, straight history that is easy to read and bisect, but it rewrites commits, so it must only be used on commits nobody else has. When in doubt, merge, because it is always recoverable.

   </details>

## Related
<!-- bite: 60a73032-9d5d-49a3-a99d-e7d99bfcd887 -->
- [[git/05-merging|Merging]] — the mechanics of one option
- [[git/06-rebasing|Rebasing]] — the mechanics of the other
- [[git/13-branching-strategies|Branching Strategies]] — the team context that settles most of these calls
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 0f4f2ab2-b407-45e1-85f2-9ad18ea00b29 -->

**Level:** Intermediate. **Covers:** The honest answer to the most-argued question in Git: the tradeoff, the cases for each, the rules a team can actually hold to, and a decision flowchart.
