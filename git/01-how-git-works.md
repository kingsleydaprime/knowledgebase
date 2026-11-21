---
id: de75a8c6-3d63-41e7-8a95-97497bcc3e5f
---

# How Git Actually Works

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

```
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

```
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

## Related
<!-- bite: d028184a-1e4a-4844-afe8-1839643e13ff -->
- [[git/03-the-three-trees|The Three Trees]] — the model layered on top of the object store
- [[git/06-rebasing|Rebasing]] — why replayed commits get new SHAs makes sense only from here
- [[git/10-undoing-things|Undoing Things]] — the reflog is just a log of ref movements
- [[git/index|Git course map]]

## About this lesson
<!-- bite: 92dfd1dc-3f98-48f3-9a21-b72fdbe2f887 -->

**Level:** Beginner → Intermediate. **Covers:** The object model underneath every command: blobs, trees, commits and tags, the refs that name them, and what is actually inside `.git/`. Every later note is easier once this one lands.
