# Git — Command Reference

**[Reference]** — The commands and their flags, grouped by what you're trying to do. For *why* any of it works the way it does, read the course: [[git/README|the reading order starts here]]. For "something has gone wrong", go to [[git/git-troubleshooting|git-troubleshooting]].

Conventions below: `<placeholder>` is yours to fill in, `[optional]` is optional, and anything marked ⚠️ can lose work.

## Everyday loop

```bash
git status                       # what's changed — run this constantly
git status -s                    # short form: XY filename
git add <file>                   # stage a file
git add -p                       # stage interactively, hunk by hunk (the good one)
git add -A                       # stage everything, repo-wide
git add -u                       # stage modifications + deletions, not new files
git restore --staged <file>      # unstage, keep the changes
git restore <file>               # ⚠️ discard working-directory changes
git commit -m "<msg>"
git commit -am "<msg>"           # stage tracked changes and commit in one step
git commit --amend --no-edit     # fold staged changes into the last commit
git push
git pull
```

`git status -s` codes: `??` untracked · `A ` staged new · `M ` staged edit · ` M` unstaged edit · `MM` partially staged · `D ` staged deletion.

## Branching and switching

```bash
git branch                       # list local
git branch -a                    # list local + remote-tracking
git branch -vv                   # list with upstream and ahead/behind
git branch --merged              # branches already merged into HEAD (safe to delete)
git branch --no-merged
git switch <branch>              # modern: switch
git switch -c <branch>           # modern: create + switch
git switch -                     # back to previous branch
git checkout -b <branch> <start>  # create from a branch, tag, or SHA
git branch -m <new-name>         # rename current branch
git branch -d <branch>           # delete (refuses if unmerged)
git branch -D <branch>           # ⚠️ delete regardless
git push origin --delete <branch>  # delete the remote one too
```

## Remotes

```bash
git remote -v                    # list remotes and URLs
git remote add <name> <url>
git remote set-url origin <url>
git remote show origin           # detailed: which branches track what
git fetch --all --prune          # download everything, drop refs to deleted branches
git pull --ff-only               # safest pull — refuses instead of auto-merging a divergence
git pull --rebase
git push -u origin <branch>      # push and set upstream
git push --force-with-lease      # ⚠️ force push, but abort if the remote moved
git push --force                 # ⚠️⚠️ never use this on a shared branch
git push --tags
```

`--force-with-lease` over `--force`, always. The difference is whether you find out that a colleague pushed while you weren't looking.

## Integrating branches

```bash
git merge <branch>               # fast-forward if possible, else a merge commit
git merge --no-ff <branch>       # always create a merge commit (preserves the branch shape)
git merge --ff-only <branch>     # fail rather than create a merge commit
git merge --squash <branch>      # collapse the branch into staged changes; you commit
git merge --abort                # back to pre-merge state

git rebase <branch>              # replay current branch on top of <branch>
git rebase -i <branch|HEAD~n>    # interactive: squash, reword, reorder, drop, edit
git rebase --onto <new-base> <old-base> <branch>
git rebase --continue / --skip / --abort
git cherry-pick <sha>            # replay one commit here
git cherry-pick -n <sha>         # ...without committing
```

Interactive rebase verbs: `pick` · `reword` (change message) · `edit` (stop to amend) · `squash` (merge into previous, keep both messages) · `fixup` (merge into previous, discard message) · `drop` · `exec` (run a shell command) · `break`.

**Conflict resolution:**

```bash
git status                       # lists conflicted files
git checkout --ours <file>       # take our side wholesale
git checkout --theirs <file>     # take their side wholesale
git add <file>                   # mark resolved
git merge --continue             # or: git rebase --continue
```

During a *rebase*, "ours" and "theirs" are reversed from what you'd expect — "ours" is the branch you're replaying onto.

## Reading history

```bash
git log --oneline --graph --decorate --all   # the one worth aliasing to `lg`
git log -<n>                     # last n commits
git log --since="2 weeks ago" --until="2026-01-01"
git log --author="<name>"
git log --grep="<text>"          # search commit MESSAGES
git log -S "<string>"            # search for commits that added/removed a STRING (pickaxe)
git log -G "<regex>"             # search the diffs by regex
git log --follow <file>          # follow a file through renames
git log main..feature            # in feature, not in main
git log main...feature           # in either, not both
git log --stat                   # files changed per commit
git log --no-merges

git show <sha>                   # a commit and its diff
git show <sha>:<file>            # a file's contents at that commit
git blame -L 10,20 <file>        # who last touched lines 10-20
git blame -w <file>              # ignore whitespace-only changes
git shortlog -sn                 # commit counts by author
```

**Commit references:** `HEAD` current · `HEAD~3` three back · `HEAD^` first parent · `HEAD^2` second parent of a merge · `main@{1}` where main pointed last · `@{2.weeks.ago}`.

**Log format specifiers:** `%H` full hash · `%h` short hash · `%an` author · `%ad` date · `%ar` relative date · `%s` subject · `%b` body · `%D` refs.

## Diffing

```bash
git diff                         # working directory vs index
git diff --staged                # index vs HEAD — what you're about to commit
git diff HEAD                    # working directory vs HEAD
git diff main feature            # between branches
git diff <sha1> <sha2>
git diff --stat                  # summary only
git diff --word-diff             # word-level — good for prose
git diff --ignore-whitespace
git diff -- <file>               # scope to one path
```

## Undoing

| Situation | Command |
|---|---|
| Unstage a file, keep the edits | `git restore --staged <file>` |
| ⚠️ Throw away working-directory edits | `git restore <file>` |
| Redo the last commit differently | `git reset --soft HEAD~1` |
| Un-commit *and* unstage | `git reset HEAD~1` (`--mixed`, the default) |
| ⚠️ Un-commit and destroy the changes | `git reset --hard HEAD~1` |
| Undo a commit that's already pushed | `git revert <sha>` |
| Fix the last commit's message or contents | `git commit --amend` |
| Find a commit you thought you lost | `git reflog` |

```bash
git reflog                       # every position HEAD has held, ~30 days
git reset --hard <sha-from-reflog>   # ⚠️ time travel back to it
git stash                        # shelve working-directory changes
git stash -u                     # ...including untracked files
git stash list
git stash pop                    # reapply and drop the stash
git stash apply stash@{2}        # reapply a specific one, keep it in the list
git stash drop / git stash clear # ⚠️ clear removes all stashes
```

`reset` moves the branch pointer. `revert` adds a new commit that undoes an old one. Use `revert` for anything already pushed.

## Finding a bug

```bash
git bisect start
git bisect bad                   # current commit is broken
git bisect good <sha|tag>        # this one was fine
# git checks out a midpoint; test it, then:
git bisect good     # or: git bisect bad
git bisect reset                 # done — return to where you were
git bisect run <script>          # automate it: exit 0 = good, 1 = bad, 125 = skip
```

## Tags and releases

```bash
git tag                          # list
git tag -l "v1.*"                # list matching
git tag -a v1.2.0 -m "<msg>"     # annotated (use this — it's a real object)
git tag -a v1.2.0 <sha>          # tag a past commit
git tag -s v1.2.0 -m "<msg>"     # signed
git tag -d v1.2.0                # delete locally
git push origin v1.2.0           # push one tag
git push --tags                  # push all
git push origin --delete v1.2.0  # delete the remote tag
git describe --tags              # nearest tag + commits since, e.g. v1.2.0-14-g2a3b4c
```

## Configuration

```bash
git config --list --show-origin  # every setting and which file it came from
git config --global <key> <value>
git config --local <key> <value> # this repo only
git config --get-regexp alias    # list your aliases
```

Settings that repay themselves immediately:

```bash
git config --global pull.ff only               # refuse surprise merge commits on pull
git config --global push.autoSetupRemote true  # no more "set upstream" errors
git config --global merge.conflictstyle diff3  # show the common ancestor in conflicts
git config --global rebase.autosquash true     # honour fixup! automatically
git config --global rebase.autoStash true      # stash and restore around a rebase
git config --global diff.algorithm histogram   # noticeably better diffs than the default
git config --global fetch.prune true           # drop refs to deleted remote branches
```

## Inspecting Git itself

```bash
git cat-file -t <sha>            # object type: blob, tree, commit, tag
git cat-file -p <sha>            # pretty-print the object
git cat-file -p HEAD^{tree}      # the root tree of the current commit
git rev-parse HEAD               # resolve a ref to a full SHA
git ls-files                     # everything in the index
git ls-files --ignored --exclude-standard   # what .gitignore is catching
git check-ignore -v <file>       # which rule is ignoring this file, and where it lives
git count-objects -vH            # repository size
git gc                           # garbage collect and repack
git fsck --lost-found            # find dangling objects
```

## Submodules and worktrees

```bash
git clone --recurse-submodules <url>
git submodule update --init --recursive   # after a normal clone
git submodule update --remote             # pull each submodule's latest

git worktree add ../hotfix <branch>       # a second working directory, same repo
git worktree list
git worktree remove ../hotfix
```

## Patches

```bash
git format-patch -1 <sha>        # one commit as a .patch file
git format-patch main            # every commit since main
git apply <file.patch>           # apply without committing
git am <file.patch>              # apply and commit, preserving authorship
git diff > changes.patch         # ad-hoc patch from working directory
```

---

## Related
- [[git/README|Git course]] — the explanations behind all of this
- [[git/git-troubleshooting|git-troubleshooting]] — symptom-first recovery
- [[devops/01-linux/linux-reference|Linux reference]] — the shell these run in
- [[git/12-conventions-and-hygiene|Conventions and Hygiene]] — how to write the messages
