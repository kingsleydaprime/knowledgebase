# Build Your Own Git

**[Intermediate]** — The build that most changes how you use a tool you already use daily. Git's data model is small enough to implement in a weekend and explains every command you've ever been confused by.

## What you're building

A content-addressable object store plus the commands that operate on it: `init`, `hash-object`, `cat-file`, `write-tree`, `commit`, `log`, `branch`, `checkout`, `diff`. By the end, **real Git will be able to read your repository** — that's the test that makes this satisfying.

**What you're deliberately not building:** the network protocol (push/pull/fetch — a separate and much less illuminating project), packfiles and delta compression (an optimisation, not the model), merge strategies beyond a basic three-way, or the full index format.

**Why this one:** you already know Git's *interface*. Implementing it converts that into knowing its *model*, and the model is genuinely elegant — four object types and a pointer.

## What you need first

| You should know | Where |
|---|---|
| **Git's object model** — blobs, trees, commits, refs | [[git/01-how-git-works\|git/01]] — **read this first; it's the spec** |
| **The three trees** — working directory, index, HEAD | [[git/03-the-three-trees\|git/03]] |
| **Hashing** — what SHA-1 gives you | [[cybersecurity/05-cryptography/README\|cryptography]] |
| **Filesystem basics** — paths, permissions, recursion | [[foundations/os/07-filesystems-and-storage\|os/07]] |

[[git/01-how-git-works|How Git Actually Works]] is effectively the specification for this project. Everything below is implementing what that note describes.

You **don't** need: network programming, compression theory (zlib is a library call), or cryptography beyond calling a hash function.

## The build order

### 1. `init` — create the directory structure

```
.mygit/
├── objects/          # the content-addressable store
├── refs/heads/       # branches
└── HEAD              # contains: ref: refs/heads/main
```

**Test:** the directories exist and `HEAD` contains the right text.

**Watch for:** nothing yet. This milestone exists so the next one has somewhere to write.

### 2. `hash-object` — store a blob

The heart of the whole system. Take a file, produce its object, store it by hash.

```
header = "blob " + content_length + "\0"
store  = header + content
hash   = sha1(store)
path   = .mygit/objects/<first 2 hex chars>/<remaining 38>
write zlib-compressed `store` to that path
```

**Test:** `./mygit hash-object file.txt` prints a 40-character hash. Run it twice — **the same content gives the same hash**. Compare against `git hash-object file.txt`: **the hashes must be identical.**

That matching hash is the moment this project becomes real. If it matches, your header format and compression are exactly right.

**Watch for:** the header uses a **NUL byte**, not a space, before the content. The length is the content's byte length, in decimal ASCII. The two-character directory prefix exists to avoid millions of files in one directory.

### 3. `cat-file` — read an object back

Decompress, split at the NUL, verify the type and length, print the content.

**Test:** round-trip a file. Then read an object that **real Git** created — `git hash-object -w file.txt`, then `./mygit cat-file <hash>`. If that works, you're interoperable in both directions.

### 4. `write-tree` — directories as objects

A tree is a directory listing. For each entry, sorted by name:

```
<mode> <name>\0<20-byte raw SHA>
```

Concatenate the entries, wrap in a `tree <len>\0` header, hash and store it — the same procedure as a blob.

Modes: `100644` regular file, `100755` executable, `040000` directory, `120000` symlink.

Recurse: a subdirectory becomes a tree object, and its hash goes in the parent's entry.

**Test:** `git cat-file -p <your-tree-hash>` — real Git should print your tree correctly.

**Watch for:** the SHA in a tree entry is **20 raw bytes, not 40 hex characters**. This is the single most common bug in this project, because everything else uses hex. Entries must be **sorted by name** or your hashes won't match Git's. The mode has no leading zero (`40000`, not `040000`, in the serialised form).

### 5. `commit` — snapshots with history

```
tree <40-hex-sha>
parent <40-hex-sha>          ← omitted for the first commit; repeated for merges
author Name <email> <unix-timestamp> <timezone>
committer Name <email> <unix-timestamp> <timezone>

Commit message here
```

Same header-and-hash procedure. Then **update the ref** — write the new commit's hash into `.mygit/refs/heads/main`.

**Test:** make three commits. `git log` in your repository — **real Git should display your history.**

**Watch for:** the blank line before the message is required. Timezone format is `+0100`, not `+01:00`. A ref file contains the 40-hex hash plus a newline.

**This is the milestone where it clicks.** A commit is a tiny text file pointing at a tree and a parent. The whole DAG is that.

### 6. `log` — walk the graph

Read HEAD → read the ref → read the commit → print it → follow `parent` → repeat.

**Test:** your output matches `git log --format=...` for the same repository.

**Watch for:** HEAD is usually `ref: refs/heads/main` (symbolic) but can be a raw hash (detached). Handle both. For merge commits with two parents you need a proper traversal — a queue ordered by commit date, or you'll print things out of order.

### 7. The index (staging area)

The piece people find most mysterious, and it's just a file listing what will be in the next commit: path, blob hash, mode, and stat metadata for change detection.

Implement `add` (hash the file, record it) and make `commit` build its tree from the index rather than from the working directory.

**Test:** `add` one of two modified files, commit, and confirm only that one changed.

**Watch for:** Git's real index is a binary format with a specific layout. **Use your own simpler format** — a text file of `mode hash path` is fine. Real Git won't read it, but everything else stays interoperable, and implementing the binary format teaches you nothing you don't already know.

The stat metadata (mtime, size, inode) is what makes `git status` fast — it can skip hashing files whose metadata is unchanged. Worth adding once the basics work.

### 8. `branch` and `checkout`

A branch is a **file containing a hash**. Creating one is writing 41 bytes.

```
.mygit/refs/heads/feature     → contains a commit hash
.mygit/HEAD                   → contains "ref: refs/heads/feature"
```

Checkout: read the commit → read its tree → write those files to the working directory → update HEAD.

**Test:** create a branch, commit on it, switch back, confirm the files change.

**Watch for:** you must **delete files that exist in the current tree but not the target** — otherwise switching branches leaves stale files behind. Refuse to switch if there are uncommitted changes that would be overwritten (or you'll destroy work, including your own during development).

### 9. `diff`

Compare two trees, or a tree against the working directory. Recursively walk both; for each path, compare hashes.

For line-level output you need a diff algorithm — **Myers' algorithm** is the standard, and a longest-common-subsequence via dynamic programming is a perfectly good first version. → [[foundations/dsa/06-patterns/15-dynamic-programming|Dynamic Programming]]

**Test:** your diff against `git diff` for the same change.

**Watch for:** comparing hashes tells you *whether* a file changed; producing the line diff is a separate algorithm. Unified diff format has specific hunk headers (`@@ -1,4 +1,6 @@`).

### 10. `merge` (optional, and the real ending)

1. Find the **merge base** — the lowest common ancestor of the two commits
2. Three-way compare: base vs ours vs theirs, per file
3. Only one side changed → take that side. Both changed identically → fine. Both changed differently → **conflict**
4. Write a commit with **two parents**

**Test:** merge two branches that touched different files (clean), then two that touched the same lines (conflict).

**Watch for:** the merge base is a graph problem — LCA on a DAG, not a tree, so a node can have several. → [[foundations/dsa/04-data-structures/06-graphs|Graphs]]

## Per-language toolkit

| Milestone | C | C++ | Rust | Go | Python | JS/Node |
|---|---|---|---|---|---|---|
| **SHA-1** | OpenSSL `libcrypto` | same | `sha1` crate | `crypto/sha1` | `hashlib` | `crypto` |
| **zlib** | `zlib.h` | `zlib.h` | `flate2` | `compress/zlib` | `zlib` | `zlib` |
| **Filesystem** | `dirent.h`, `stat` | `std::filesystem` | `std::fs`, `walkdir` | `os`, `filepath.Walk` | `pathlib`, `os.walk` | `fs`, `fs.promises` |
| **CLI parsing** | by hand | by hand | `clap` | `flag` | `argparse` | `commander` |
| **Diff** | by hand | by hand | `similar` | `go-diff` | `difflib` (built in!) | `diff` |

**Language-specific advice:**

**Python** — the fastest path. `hashlib`, `zlib`, `pathlib` and `difflib` are all standard, so you write only the logic. Excellent for a first pass to understand the model.

**Go** — everything needed is in the standard library, and it produces a single binary. `compress/zlib` and `crypto/sha1` are exactly what you need.

**Rust** — good fit; the type system helps model the four object types as an enum with exhaustive matching. → [[languages/03-rust/06-structs-enums-and-pattern-matching|enums]]

**C** — instructive for the byte-level work (the 20-byte raw SHA, the NUL-separated header), and you'll spend time on string handling rather than on Git.

**JS/Node** — `zlib` and `crypto` are built in. Fine choice.

> **Whatever you choose, verify against real Git at every milestone.** `git cat-file -p <hash>` on objects you created is the tightest feedback loop in this project.

## The parts that will bite you

**The 20-byte raw SHA in tree entries.** Everything else is 40-hex. This one is binary. It's the most common bug.

**Tree entries must be sorted by name**, byte-wise. Unsorted entries produce a different hash than Git would, and interoperability breaks silently.

**The NUL byte in the header** — `blob 12\0`, not `blob 12 `.

**Compression is over the header *and* content**, not just the content. Hash first, then compress.

**Text mode on Windows** will corrupt your objects. Open files in binary mode everywhere.

**The index is binary in real Git.** Don't implement it; use your own format.

**Symlinks and executable bits.** A tree entry's mode encodes them; ignoring modes means checkouts lose the executable bit.

**Empty directories don't exist in Git.** Trees contain files; a directory with no files has nothing to record. This surprises people and it's why `.gitkeep` is a convention.

## How to know it works

**The interoperability test is the whole point:**

```bash
./mygit init
echo "hello" > a.txt
./mygit add a.txt
./mygit commit -m "first"

git log                       # REAL git reads your repository
git cat-file -p HEAD          # real git prints your commit
git status                    # real git understands your state
git fsck                      # real git VALIDATES your object store
```

**`git fsck` is the strongest check available** — it verifies every object's hash, type, and references. If it passes, your objects are correct.

Comparing hashes directly:

```bash
echo "hello" > a.txt
git hash-object a.txt         # 
./mygit hash-object a.txt     # must be IDENTICAL
```

**Unit-test the object codec** separately: serialise → deserialise → compare. And test with awkward content — empty files, files with NUL bytes, filenames with spaces and unicode.

## Where to stop

**Stop after `checkout`, or after `merge` if you want the full satisfaction.** You'll have learned:

- That a commit is a small text file, and history is a linked list of them
- That branches are 41-byte files — which is why branching is instant
- That the same content always has the same hash, so Git deduplicates for free
- What the staging area actually is
- Why `git checkout` can destroy uncommitted work
- Why detached HEAD is a state rather than an error

**Real Git additionally has:** packfiles with delta compression (a repository with 100k objects would be unusably slow otherwise), the smart HTTP and SSH protocols, reflog, hooks, submodules, worktrees, sparse checkout, partial clone, and SHA-256 support alongside SHA-1.

**If you want to go further:** implementing **packfiles** is the natural next step and teaches you real compression engineering — delta encoding against a base object, plus the index that makes random access possible. The **network protocol** is less interesting; it's mostly negotiation.

Compare with what you learned in [[git/README|the git course]] — the difference between having read it and having built it is exactly the point of this folder.

---

## Related
- [[git/01-how-git-works|How Git Actually Works]] — the specification for this project
- [[git/03-the-three-trees|The Three Trees]] — what the index milestone implements
- [[git/16-power-tools|Git: Power Tools]] — what you're choosing not to build
- [[foundations/dsa/04-data-structures/06-graphs|Graphs]] — the merge-base problem
- [[build-your-own-shit/README|build-your-own-shit]]
