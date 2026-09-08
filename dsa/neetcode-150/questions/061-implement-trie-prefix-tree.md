# Implement Trie (Prefix Tree)

**LeetCode 208** · Tries · concept: [[09-tries|tries]]

## Problem

Implement a trie supporting `insert(word)`, `search(word)` (exact), and `startsWith(prefix)`.

## Approach — a tree of character-keyed children (optimal)

Each node has a map `char → child` and an `is_end` flag. All three operations walk the tree one character at a time; the only difference between `search` and `startsWith` is whether you also check `is_end` at the landing node.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):                 # O(L)
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word):                 # O(L) — path exists AND ends here
        node = self._walk(word)
        return node is not None and node.is_end

    def startsWith(self, prefix):           # O(L) — path just has to exist
        return self._walk(prefix) is not None

    def _walk(self, s):
        node = self.root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```

**All operations O(L)** (L = word length), **independent of the number of stored words**. Space O(total characters).

## Why `is_end` is the whole point

`search("app")` and `startsWith("app")` follow the identical path — only `search` additionally checks `is_end`. Without the flag you couldn't distinguish a stored word from a mere prefix of a longer word (`"app"` stored vs. `"app"` as a prefix of `"apple"`).

## Key insight

**Prefix queries → a trie; the `is_end` flag separates "a word ends here" from "just a waypoint."** A [[03-hash-maps|hash set]] does exact membership but *can't* do `startsWith` without scanning every key — the trie's entire reason to exist.

## Related
- concept: [[09-tries|tries]]
- next: [[062-design-add-and-search-words-data-structure|Design Add and Search Words]]
