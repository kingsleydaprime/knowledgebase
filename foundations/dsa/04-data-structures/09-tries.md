# Tries (Prefix Trees)

A trie (pronounced "try", from re**trie**val) is a tree specialized for storing strings by their **shared prefixes**. Every path from the root spells out a prefix; every stored word is a path ending at a node flagged as a word-end. It trades memory for a superpower a [[03-hash-maps|hash map]] can't match: answering "does any stored word *start with* this prefix?" in time proportional to the prefix length, independent of how many words are stored.

## Why it exists

A hash set of words answers "is this exact word present?" in O(L) (you hash the whole L-character string). What it *can't* do is prefix queries — "how many words start with `app`?", or "walk every word beginning with `pre`" — without scanning every key. A trie makes prefixes first-class: because words that share a prefix share the same path, a prefix lookup is just a walk down that one path. This is why autocomplete, spell-checkers, IP routing tables, and word-search-on-a-grid all reach for tries.

## The structure

Each node holds:

- a map from **next character → child node** (a dict of size ≤ alphabet, or a fixed array of 26 for lowercase English),
- a boolean `is_end` marking whether a word terminates *at this node*.

The root represents the empty prefix and stores no character itself. The characters live on the **edges** (equivalently, are the keys into the children map) — a node "is" the prefix formed by the path taken to reach it.

```python
class TrieNode:
    def __init__(self):
        self.children = {}      # char -> TrieNode
        self.is_end = False     # True if a word ends here

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):                 # O(L)
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word):                 # O(L) — full word must exist AND end here
        node = self._walk(word)
        return node is not None and node.is_end

    def startsWith(self, prefix):            # O(L) — path just has to exist
        return self._walk(prefix) is not None

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

The one subtlety is `is_end`. `search("app")` and `startsWith("app")` walk the identical path; the *only* difference is that `search` also checks the flag. Without `is_end` you couldn't tell that `app` is a stored word while `appl` is merely a prefix of `apple`.

## Complexity

Let L = length of the word/prefix, and Σ = alphabet size.

| Operation | Time | Note |
|---|---|---|
| Insert | O(L) | independent of the number of stored words |
| Search (exact) | O(L) | |
| startsWith (prefix) | O(L) | the operation a hash map can't do |
| Space | O(total characters · Σ) worst case | shared prefixes reclaim much of this |

The headline is that **every operation is O(L), not O(L · n)** — adding a millionth word doesn't slow down lookups. The cost is space: each node carries a children container, so a trie is memory-hungry compared to a hash set, especially when words share few prefixes. The array-of-26 layout is fast but wasteful; the dict layout is compact but has hashing overhead per step.

## Wildcard search — the `.` that matches any character

The moment a search allows a wildcard, the single-path walk becomes a **branching DFS**: at a `.`, recurse into *every* child; at a concrete character, recurse into just that one. This is *Design Add and Search Words*:

```python
def search(self, word):
    def dfs(node, i):
        if i == len(word):
            return node.is_end
        ch = word[i]
        if ch == ".":
            return any(dfs(child, i + 1) for child in node.children.values())
        return ch in node.children and dfs(node.children[ch], i + 1)
    return dfs(self.root, 0)
```

Worst case (`word` is all dots) this degrades toward exploring the whole trie — but on realistic inputs the concrete characters prune aggressively.

## Trie + grid backtracking — the killer combination

*Word Search II* (find which of many words appear in a character grid) is the reason tries earn their keep. The brute force — run a grid DFS separately for each word — is hopeless. Instead, **build one trie of all the words**, then run a single [[14-backtracking|backtracking]] DFS over the grid that walks the trie in lockstep: at each cell, only continue if the current character is a child in the trie. The trie prunes dead ends across *all* words simultaneously, and matched words get pruned out of the trie so they aren't re-reported. This "trie guides the search" idea generalizes to any multi-pattern matching on a search space.

## Complexity vs. a hash map — when to actually use a trie

| Need | Reach for |
|---|---|
| Exact membership only | [[03-hash-maps\|hash set]] — simpler, less memory |
| Prefix queries / autocomplete | **trie** |
| Multi-pattern search over a grid/text | **trie** + DFS |
| Sorted iteration of keys | trie (a pre-order walk yields words in lexicographic order) — or a balanced [[01-trees\|BST]] |

If you never ask a prefix question, a hash set beats a trie on every axis. The trie is worth its memory precisely when the *prefix* is the query.

## Gotchas

- **Forgetting `is_end`** collapses `search` and `startsWith` into the same (wrong) answer — the flag is the whole point.
- **Deletion is fiddly**: you can't just unset `is_end` and prune, because the node may sit on the path of a longer word. Prune a node only if it has no children *and* isn't another word's end.
- **Memory blows up with a large alphabet** using fixed arrays — prefer a dict for Unicode or sparse alphabets.
- A trie's pre-order traversal yields keys **in sorted order for free** — occasionally the reason to pick it over a hash map even without prefix queries.

## Canonical problems (NeetCode Tries)

- **Implement Trie (Prefix Tree)** — `insert` / `search` / `startsWith`, the structure above.
- **Design Add and Search Words Data Structure** — the wildcard `.` DFS.
- **Word Search II** — trie + grid backtracking.

## Related
- [[03-hash-maps|Hash maps]] — the alternative that can't do prefixes
- [[01-trees|Trees]] — the general tree structure a trie specializes
- [[14-backtracking|Backtracking]] — pairs with a trie for Word Search II
- [[02-dfs|DFS]] — how wildcard and grid searches traverse a trie
