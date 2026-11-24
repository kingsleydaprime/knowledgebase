---
id: de75a8c6-3d63-41e7-8a95-97497bcc3e5f
---

# How Git Actually Works

Git is a tool that keeps a full history of your project's files, so you can see every saved version and go back to any of them. Each save, called a commit, is a snapshot of all your files at that moment. This lesson looks under the hood at how Git stores those snapshots, which makes the rest of Git much less confusing.

## Git is a Content-Addressable Filesystem
<!-- bite: 3f52c9c8-a308-46f7-ade8-b4658d3017c8 -->

Most version control systems track changes (diffs). Git tracks **snapshots** — complete states of every file at every commit. Understanding this explains why Git is so fast and why operations like branching are nearly instantaneous.

Everything Git stores is an **object**, identified by a **SHA-1 hash** of its content. If two files have identical content, they share one object. If a file doesn't change between commits, the new commit just points to the same object — no duplication.

```bash
# See Git's object store
ls .git/objects/

# Inspect any object
git cat-file -t a1b2c3d    # Type: blob, tree, commit, or tag
git cat-file -p a1b2c3d    # Pretty-print the content
```

## The Four Object Types
<!-- bite: ab4f4d5d-bb4b-46ec-b7b5-c50d6cd1dc1b -->

**Blob** — stores the content of a single file. No filename, no metadata. Just bytes.

**Tree** — stores a directory listing: a list of (mode, name, SHA) entries pointing to blobs (files) and other trees (subdirectories).

**Commit** — stores:
- A pointer to a tree (the root of the snapshot)
- A pointer to the parent commit (or multiple parents for merges)
- Author name, email, timestamp
- Committer name, email, timestamp
- The commit message

**Tag** — stores a pointer to another object (usually a commit) with a name, message, and optional signature.

```bash
# See what a commit actually contains
git cat-file -p HEAD
# tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904
# parent a1b2c3d4e5f6...
# author Kingsley Ihemelandu <k@example.com> 1746000000 +0000
# committer Kingsley Ihemelandu <k@example.com> 1746000000 +0000
#
# feat: add user authentication

# See what a tree contains
git cat-file -p HEAD^{tree}
# 100644 blob a8c3f... README.md
# 040000 tree 9f7d2... src
# 100755 blob b2e4a... deploy.sh
```

## Refs — Human-Readable Names for SHAs
<!-- bite: 0ba59424-561a-4070-942c-53b29f3490da -->

Refs are files in `.git/refs/` that store a SHA. They're just pointers to objects.

```bash
cat .git/refs/heads/main          # The SHA of the latest commit on main
cat .git/refs/remotes/origin/main # What origin/main points to
cat .git/HEAD                     # What's currently checked out

# HEAD is special — it points to the current branch ref (or directly to a SHA in detached HEAD)
cat .git/HEAD
# ref: refs/heads/main   ← on a branch
# or
# a1b2c3d4e5f6...        ← detached HEAD
```

## How a Commit Changes the Graph
<!-- bite: 0523cc09-205d-4fb7-8b9e-018fe69e79d2 -->

When you make a commit, Git:
1. Creates blob objects for any changed files
2. Creates tree objects for affected directories
3. Creates a commit object pointing to the root tree and the parent commit
4. Moves the current branch ref to point at the new commit SHA

```text
Before commit:
  main → C2 → C1

After commit:
  main → C3 → C2 → C1
  HEAD → main (still tracking main)
```

Branching is just creating a new ref file pointing at a commit. It costs nothing — just 41 bytes.

```bash
# What branch creation actually does
cat .git/refs/heads/main      # a1b2c3d4...
git checkout -b feature       # Creates .git/refs/heads/feature with same SHA
cat .git/refs/heads/feature   # a1b2c3d4... (same SHA, new ref)
```

## The .git Directory
<!-- bite: 231b981f-6f67-4d01-9958-2df039c6fd6b -->

```text
.git/
├── HEAD              # Current branch or commit
├── config            # Repo-level config
├── description       # Used by GitWeb (not important)
├── index             # The staging area (binary file)
├── COMMIT_EDITMSG    # Last commit message
├── MERGE_HEAD        # Present during a merge conflict
├── REBASE_HEAD       # Present during a rebase
├── hooks/            # Client-side hook scripts
├── info/             # exclude file (like .gitignore but not tracked)
├── logs/             # Reflog — history of where refs have pointed
│   ├── HEAD
│   └── refs/heads/main
├── objects/          # All objects (blobs, trees, commits, tags)
│   ├── pack/         # Packed objects (efficient storage)
│   └── info/
└── refs/             # Branch, tag, and remote refs
    ├── heads/        # Local branches
    ├── remotes/      # Remote tracking branches
    └── tags/         # Tags
```

---

## Check your understanding
<!-- bite: 598bef93-33bd-4f04-8a93-8b847b19ff44 -->

Try each one before you open the answer.

1. <!-- q: mcq id="b8d3c2bf" -->
   Which Git object holds the content of a single file, with no filename?

   - [x] Blob
   - [ ] Tree
   - [ ] Commit
   - [ ] Tag

   <details><summary>Answer</summary>

   A blob: just the bytes. The filename lives in the tree that points at the blob, which is why two files with identical content share one blob.

   </details>

2. <!-- q: mcq id="f48548d0" -->
   What does a commit object point to? Choose all that apply.

   - [x] A tree, the root of the snapshot
   - [x] Its parent commit, or two parents for a merge
   - [ ] A list of the lines that changed since the parent
   - [ ] Every branch that contains it

   <details><summary>Answer</summary>

   A tree and its parent or parents, plus author, committer and message. Git stores snapshots, not diffs; a diff is worked out when you ask for one. Branches point at commits, not the other way round.

   </details>

3. <!-- q: mcq id="709a05d4" -->
   A project has 200 files. You edit one of them and commit. What does the new commit's snapshot do with the other 199?

   - [ ] Copies all 199 into new blobs
   - [x] Points at the same blobs the previous commit used
   - [ ] Leaves them out, so only the changed file is in the commit
   - [ ] Stores a diff for each of them

   <details><summary>Answer</summary>

   It reuses the existing blobs. Objects are named by the hash of their content, so unchanged content already has an object. Every commit is still a complete snapshot, with no duplication.

   </details>

4. <!-- q: exact id="2e227f31" answer="ref: refs/heads/feature" accept="refs/heads/feature" -->
   You are on a branch called `feature`. What does `cat .git/HEAD` print?

   <details><summary>Answer</summary>

   `ref: refs/heads/feature`. HEAD normally points at a branch, and the branch points at a commit. In detached HEAD it holds a commit SHA directly instead.

   </details>

5. <!-- q: open id="64e084a1" -->
   Why is creating a branch in Git almost instant, no matter how big the project is?

   <details><summary>Answer</summary>

   A branch is only a ref: a small file in `.git/refs/heads/` holding one commit SHA. Creating one writes that file (about 41 bytes) and copies nothing else. The commits, trees and blobs are already there and are shared.

   </details>

## Related
<!-- bite: d028184a-1e4a-4844-afe8-1839643e13ff -->
- [[git/03-the-three-trees|The Three Trees]] — the model layered on top of the object store
- [[git/06-rebasing|Rebasing]] — why replayed commits get new SHAs makes sense only from here
- [[git/10-undoing-things|Undoing Things]] — the reflog is just a log of ref movements
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 92dfd1dc-3f98-48f3-9a21-b72fdbe2f887 -->

**Level:** Beginner → Intermediate. **Covers:** The object model underneath every command: blobs, trees, commits and tags, the refs that name them, and what is actually inside `.git/`. Every later note is easier once this one lands.
