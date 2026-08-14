# Git Troubleshooting — Recovery Recipes

**[Reference]** — Symptom-first recovery. Find the sentence that matches your situation, run the fix. Written for the moment you are panicking, not for reading front to back.

## "I committed to the wrong branch"

```bash
# Move the commit to the correct branch
git log --oneline -3              # Note the SHA of the commit you want to move
git checkout correct-branch
git cherry-pick SHA               # Apply it to the right branch
git checkout wrong-branch
git reset --hard HEAD~1           # Remove it from the wrong branch
```

## "I accidentally deleted a branch"

```bash
git reflog                        # Find the last commit SHA on the deleted branch
git checkout -b recovered-branch SHA
```

## "I did git reset --hard and lost work"

```bash
git reflog                        # Find the SHA before the reset
git reset --hard SHA              # Go back
# Or create a branch at that point:
git branch recovered SHA
```

## "My rebase went horribly wrong"

```bash
git rebase --abort                # If still in progress
# If already completed:
git reflog                        # Find the pre-rebase position
git reset --hard HEAD@{N}         # N = the position before rebase started
# Or:
git reset --hard ORIG_HEAD        # Git saves pre-operation position here
```

## "I accidentally committed my .env file"

This is one of the most common Git mistakes. The response depends on whether you've pushed yet.

---

**Scenario A — Not pushed yet (local only)**

Easy. The secret hasn't left your machine.

```bash
# Remove .env from the last commit but keep the file on disk
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit --amend --no-edit       # Amend the commit — .env is gone from it
```

If the .env was committed several commits ago (not just the last one):

```bash
git rebase -i HEAD~N               # N = how many commits back the .env appeared
# Mark the offending commit as 'edit'
# When rebase stops there:
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit --amend --no-edit
git rebase --continue
```

---

**Scenario B — Pushed to a private repo, no one else has pulled**

Act fast. The secret is on GitHub's servers but no one has it yet.

```bash
# Step 1 — Rotate/revoke the secret immediately
# Don't wait. Do this first. Assume the worst.

# Step 2 — Remove .env from the entire git history using BFG (recommended)
# Install BFG: https://rtyley.github.io/bfg-repo-cleaner/

# Clone a fresh mirror of your repo
git clone --mirror https://github.com/you/your-repo.git

# Run BFG to delete the file from all history
java -jar bfg.jar --delete-files .env your-repo.git

# Clean up the repo
cd your-repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push all branches and tags
git push --force

# Step 3 — Add .env to .gitignore in your working repo
cd your-working-repo
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: add .env to gitignore"
git push

# Step 4 — Re-clone locally (your local clone's history is now stale)
cd ..
rm -rf your-working-repo
git clone https://github.com/you/your-repo.git
```

---

**Scenario C — Pushed to a public repo, or others have pulled**

The secret is compromised. Full stop. No amount of Git history rewriting changes this — GitHub indexes public repos, bots scrape them within seconds, and anyone who pulled has the secret in their local history.

```bash
# Step 1 — Rotate/revoke ALL secrets in the .env file IMMEDIATELY
# API keys, database passwords, JWT secrets — everything. Right now.

# Step 2 — Make the repo private immediately (buys time)
# GitHub → Repo Settings → Danger Zone → Change visibility

# Step 3 — Remove from history (same as Scenario B)
git clone --mirror https://github.com/you/your-repo.git
java -jar bfg.jar --delete-files .env your-repo.git
cd your-repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force

# Step 4 — Contact GitHub support
# https://support.github.com/
# Request they clear cached views of the file
# GitHub's API may still serve the blob even after history rewrite

# Step 5 — Notify anyone who cloned the repo
# They need to re-clone — their local history still has the secret

# Step 6 — Add .env to .gitignore in the cleaned repo
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: add .env to gitignore"
git push

# Step 7 — Audit what used those credentials
# Check logs for any unauthorised access using the compromised keys
```

---

**Using git filter-branch instead of BFG (no Java required, slower)**

```bash
# Remove .env from entire history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
git push origin --force --tags
```

---

**How to prevent this happening again**

```bash
# 1. Add .env to .gitignore before creating the file
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: add .env to gitignore"

# 2. Always have a .env.example committed with placeholder values
cp .env .env.example
# Edit .env.example — replace real values with placeholders
git add .env.example
git commit -m "chore: add .env.example"

# 3. Add a pre-commit hook to catch .env before it's committed
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
if git diff --cached --name-only | grep -qE "^\.env$|^\.env\."; then
  echo "ERROR: Attempting to commit a .env file."
  echo "Remove it with: git rm --cached .env"
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit

# 4. Use gitleaks for broader secret detection
# Install: https://github.com/gitleaks/gitleaks
gitleaks protect --staged   # Scan staged changes before commit
```

## "Merge conflict I don't understand"

```bash
git log --merge                   # Show commits causing the conflict
git diff --merge                  # Show conflicting changes
git checkout --conflict=diff3 file.txt  # Re-show conflict markers with base
git mergetool                     # Open visual merge tool
git merge --abort                 # Start over if needed
```

## "Detached HEAD panic"

```bash
git log --oneline -5              # See where you are
git switch main                   # Go back to main (commits made in detached HEAD are orphaned)
# If you made commits in detached HEAD that you want to keep:
git branch my-work                # Create branch at current position (do this FIRST)
git switch main
```

## "Slow git status"

```bash
# Common on large repos or slow filesystems
git config core.fsmonitor true              # Enable filesystem monitor (git 2.37+)
git config core.untrackedCache true         # Cache untracked file info
git update-index --really-refresh           # Refresh the index
git gc                                      # Optimise object storage
```

## "Accidentally staged the wrong thing"

```bash
git restore --staged file.txt               # Unstage specific file
git restore --staged .                      # Unstage everything
git reset HEAD file.txt                     # Older syntax for unstaging
```

## "Need to split a commit into two"

```bash
git rebase -i HEAD~1              # Mark the commit as 'edit'
git reset HEAD~1                  # Unstage everything from that commit
git add -p                        # Stage part 1 interactively
git commit -m "part 1"
git add -p                        # Stage part 2
git commit -m "part 2"
git rebase --continue
```

## "I want to see what changed between my branch and main"

```bash
git log --oneline main..HEAD      # Commits on my branch not on main
git diff main...HEAD              # Changes introduced by my branch (three dots)
git diff main                     # All differences between my branch and main
```

## "git push rejected (non-fast-forward)"

```bash
# Someone else pushed while you were working
git fetch origin
git log --oneline HEAD..origin/main  # See what they pushed
git rebase origin/main              # Rebase your work on top of theirs
git push                            # Now it should work
# Or merge:
git merge origin/main && git push
```

---

*Last updated: 2026 — Built from real Git usage across solo and team projects.*

---

## Related
- [[git/10-undoing-things|Undoing Things]] — the same material organised by intent rather than symptom
- [[git/01-how-git-works|How Git Actually Works]] — the model that makes these fixes obvious instead of magic
- [[git/git-reference|Command reference]] — flags and syntax lookup
- [[git/README|Git course map]]
