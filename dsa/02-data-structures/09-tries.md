# Module: Tries / Prefix Trees (Shared Prefix Search)

Welcome to the **Trie** (pronounced *"try"*, short for re**TRIE**val) module. A Trie is a tree-based data structure optimized for storing strings by sharing common letter prefixes.

Tries trade extra memory to grant a superpower that [[03-hash-maps|Hash Maps]] cannot match: **answering "Does any word start with this prefix?" in $O(L)$ time**, where $L$ is the length of the prefix, regardless of whether the dictionary contains 10 words or 10,000,000 words!

---

## Before you start

- You understand tree structure. See [[01-trees|trees]].
- You understand hash maps and what they give up. See [[03-hash-maps|hash maps]].

**What you will be able to do after this lesson:**

1. Explain how a key becomes a path rather than something stored at a node.
2. Explain why lookup is O(length) and independent of how many words are stored.
3. Explain why a hash map cannot do prefix search at all.
4. State the memory tradeoff and when a trie is the wrong choice.

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

## 1. Real-World Motivation & Physical Metaphors

Imagine using the **Search Bar Autocomplete** on your phone:

```
User types "app"  --->  Trie follows path: 'a' -> 'p' -> 'p'
                             |
         +-------------------+-------------------+
         |                                       |
    [ "apple" ]                             [ "application" ]
```

- If you stored 1,000,000 words in a [[03-hash-maps|Hash Set]], asking *"Are there any words starting with 'app'?"* would force the computer to scan all 1,000,000 entries one-by-one ($O(N)$).
- A **Trie** stores words by sharing letter paths. The characters `'a' -> 'p' -> 'p'` are stored **once**, and all words starting with `"app"` branch off from that exact node!

### Production Use Cases:
1. **Search Engine Autocomplete**: Instant word predictions as you type.
2. **Spell-Checkers & Predictive Text (T9)**: Validating dictionary words.
3. **IP Router Routing Tables**: Longest prefix matching for IP addresses.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **Root Node** | The empty starting node of the Trie. | Represents the empty string `""`. |
| **Character Edge** | The link between nodes representing a single letter. | Edge labeled `'a'` or `'b'`. |
| **`is_end` Flag** | A boolean flag marking if a full word terminates at this node. | Differentiates `"app"` (valid word) from `"appl"` (just a prefix). |
| **Alphabet Size ($\Sigma$)** | The number of possible child branches per node. | $\Sigma = 26$ for lowercase English letters. |

---

## 3. Visual Anatomy of a Trie

Below is a Trie containing the words **`"app"`, `"apple"`, `"apt"`, and `"cat"`**:

```
                  ( Root )
                 /        \
               'a'        'c'
               /            \
             'p'            'a'
            /   \             \
          'p'*  't'*          't'*
          /
        'l'
        /
      'e'*

(* indicates is_end = True)
```

Notice how `"app"`, `"apple"`, and `"apt"` all share the initial path `'a' -> 'p'`!

---

## 4. Technical Deep Dive: Trie Implementation

### Python Code: `TrieNode` & `Trie` Class
```python
class TrieNode:
    """Node representing a single character step in the Trie."""
    def __init__(self):
        self.children = {}  # Maps character -> TrieNode (e.g. {'a': Node})
        self.is_end = False  # True if a complete word ends at this node


class Trie:
    """Prefix Tree data structure."""
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """Inserts a word into the trie. Time Complexity: O(L)"""
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        current.is_end = True  # Flag the end of the word

    def search(self, word: str) -> bool:
        """Returns True if the exact word exists in the trie. Time Complexity: O(L)"""
        node = self._walk(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        """Returns True if any word in the trie starts with prefix. Time Complexity: O(L)"""
        return self._walk(prefix) is not None

    def _walk(self, text: str) -> TrieNode:
        """Helper to walk the trie path for a given string."""
        current = self.root
        for char in text:
            if char not in current.children:
                return None
            current = current.children[char]
        return current
```

---

## 5. Hash Set vs. Trie Comparison

| Feature | Hash Set / Hash Map | Trie (Prefix Tree) |
| :--- | :--- | :--- |
| **Exact Word Match (`"apple"`)** | **$O(L)$** (Hash calculation) | **$O(L)$** (Node traversal) |
| **Prefix Match (`startsWith("app")`)** | $O(N \cdot L)$ (Must scan all keys) | **$O(L)$** (Walk prefix length only!) |
| **Memory Consumption** | Compact ($O(N \cdot L)$) | Higher due to node pointers ($O(N \cdot L \cdot \Sigma)$) |
| **Sorted Lexicographical Traversal**| Requires sorting all keys ($O(N \log N)$) | **$O(N)$ for free** (Preorder traversal of tree) |

---

## 6. Advanced Pattern: Wildcard Search (`.`)

When a query string includes a wildcard `.` (matching any character), the single-path lookup transforms into a **Depth-First Search (DFS)** over all child branches:

```python
def search_wildcard(self, word: str) -> bool:
    """Searches for a word where '.' matches any character."""
    def dfs(node: TrieNode, index: int) -> bool:
        if index == len(word):
            return node.is_end
            
        char = word[index]
        if char == '.':
            # Wildcard: Recurse down ALL existing child nodes!
            return any(dfs(child, index + 1) for child in node.children.values())
        else:
            if char not in node.children:
                return False
            return dfs(node.children[char], index + 1)

    return dfs(self.root, 0)
```

---

## 7. Complexity & Memory Trade-Offs

Let $L$ = Length of the target word/prefix, and $\Sigma$ = Alphabet size (e.g. 26).

| Operation | Time Complexity | Notes |
| :--- | :--- | :--- |
| **Insert Word** | **$O(L)$** | Completely independent of total words stored ($N$). |
| **Search Exact Word** | **$O(L)$** | Checks `is_end == True`. |
| **Prefix Match (`startsWith`)**| **$O(L)$** | The key operation a Hash Map cannot match! |
| **Space Overhead** | $O(N \cdot L \cdot \Sigma)$ | Shared prefixes save space, but pointer overhead is high. |

---

## 8. Common Pitfalls & Traps

1. **Forgetting `is_end`**: If you forget to flag `is_end = True`, your Trie cannot distinguish between an actual word (`"app"`) and a prefix of a longer word (`"apple"`).
2. **Memory Overuse**: Using fixed arrays of size 26 for Unicode/multilingual inputs wastes massive RAM. Use a dynamic dictionary `self.children = {}` instead.
3. **Complex Deletions**: Deleting a word from a Trie requires recursively pruning unneeded nodes only if they have no other children and are not marked as `is_end` for another word.

---

## Implementation - complete runnable example

**Runnable example:** save as `tries_lab.py` and run `python3 tries_lab.py`. Standard library only; writes no files. Everything is counted rather than timed, so your output will match this exactly.

```python
"""Tries: the structure where the KEY is the path, not something stored."""

class Trie:
    class Node:
        __slots__ = ("children", "is_word")
        def __init__(self):
            self.children, self.is_word = {}, False

    def __init__(self):
        self.root, self.nodes = Trie.Node(), 1

    def insert(self, word):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = Trie.Node()
                self.nodes += 1
            node = node.children[ch]
        node.is_word = True

    def _walk(self, prefix):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def contains(self, word):
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

    def with_prefix(self, prefix):
        """The operation a hash map cannot do at all."""
        node, out = self._walk(prefix), []
        if node is None:
            return out
        def collect(n, path):
            if n.is_word: out.append(prefix + path)
            for ch in sorted(n.children):
                collect(n.children[ch], path + ch)
        collect(node, "")
        return out

if __name__ == "__main__":
    words = ["car", "card", "care", "careful", "cat", "dog", "do"]
    t = Trie()
    for w in words: t.insert(w)

    print("THE KEY IS THE PATH")
    print(f"  inserted: {words}")
    print()
    print("  root")
    print("   ├── c ── a ── r*  ── d*")
    print("   │              │    └── e* ── f ── u ── l*")
    print("   │              └── t*")
    print("   └── d ── o* ── g*")
    print("  (* marks the end of a real word)")
    print()
    print("  'car', 'card' and 'care' SHARE the nodes c-a-r. The common")
    print("  prefix is stored once, not three times.")
    print()

    print("LOOKUP IS O(length), NOT O(number of words)")
    print(f"  {'query':>10s} {'contains':>10s} {'is a prefix':>13s}")
    for q in ["car", "care", "ca", "cart", "do", "dog"]:
        print(f"  {q:>10s} {str(t.contains(q)):>10s} {str(t.starts_with(q)):>13s}")
    print("  -> 'ca' is a valid PREFIX but not a WORD. A trie distinguishes")
    print("     them; that is what the is_word flag is for.")
    print()

    print("PREFIX SEARCH -- what a hash map simply cannot do")
    for p in ["car", "ca", "d", "z"]:
        print(f"  words starting {p!r:6s}: {t.with_prefix(p)}")
    print("  -> a hash map hashes the WHOLE key, so it destroys the")
    print("     relationship between 'car' and 'card'. Autocomplete needs")
    print("     that relationship, which is why tries exist.")
    print()

    print("THE COST -- nodes versus characters stored")
    total_chars = sum(len(w) for w in words)
    print(f"  {len(words)} words, {total_chars} characters total")
    print(f"  trie nodes: {t.nodes}  (shared prefixes save {total_chars + 1 - t.nodes} nodes)")
    print("  -> tries trade memory per node for prefix operations. With")
    print("     little shared prefix, they are far heavier than a hash map.")

    assert t.contains("car") and t.contains("careful")
    assert not t.contains("ca") and t.starts_with("ca")
    assert not t.contains("cart") and not t.starts_with("cart")
    assert t.with_prefix("car") == ["car", "card", "care", "careful"]
    assert t.with_prefix("z") == []
    assert sorted(t.with_prefix("")) == sorted(words)
    print()
    print("tries_lab: passed")
```

Expected output:

```
THE KEY IS THE PATH
  inserted: ['car', 'card', 'care', 'careful', 'cat', 'dog', 'do']

  root
   ├── c ── a ── r*  ── d*
   │              │    └── e* ── f ── u ── l*
   │              └── t*
   └── d ── o* ── g*
  (* marks the end of a real word)

  'car', 'card' and 'care' SHARE the nodes c-a-r. The common
  prefix is stored once, not three times.

LOOKUP IS O(length), NOT O(number of words)
       query   contains   is a prefix
         car       True          True
        care       True          True
          ca      False          True
        cart      False         False
          do       True          True
         dog       True          True
  -> 'ca' is a valid PREFIX but not a WORD. A trie distinguishes
     them; that is what the is_word flag is for.

PREFIX SEARCH -- what a hash map simply cannot do
  words starting 'car' : ['car', 'card', 'care', 'careful']
  words starting 'ca'  : ['car', 'card', 'care', 'careful', 'cat']
  words starting 'd'   : ['do', 'dog']
  words starting 'z'   : []
  -> a hash map hashes the WHOLE key, so it destroys the
     relationship between 'car' and 'card'. Autocomplete needs
     that relationship, which is why tries exist.

THE COST -- nodes versus characters stored
  7 words, 26 characters total
  trie nodes: 13  (shared prefixes save 14 nodes)
  -> tries trade memory per node for prefix operations. With
     little shared prefix, they are far heavier than a hash map.

tries_lab: passed
```

## 9. Check Your Understanding (University Self-Assessment)

1. **Question**: Why can't a Hash Set perform prefix searches (`startsWith("app")`) in $O(L)$ time?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A Hash Set hashes the entire string to compute an index. Searching for a prefix gives a completely different hash than the full word (e.g., <code>hash("app") != hash("apple")</code>). To check prefixes, a Hash Set must scan every key one-by-one (<b>O(N)</b>).</details>

2. **Question**: What is the purpose of the `is_end` boolean flag in a `TrieNode`?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The <code>is_end</code> flag indicates that a valid word terminates at that node. Without it, searching for <code>"app"</code> in a Trie containing only <code>"apple"</code> would incorrectly return <code>True</code>.</details>

3. **Question**: How does a Trie automatically provide sorted (alphabetical) word output?
   - <details><summary>Click for Answer</summary><b>Answer:</b> By performing a <b>Preorder Traversal</b> over the Trie while iterating child keys in alphabetical order ('a' to 'z'), words are visited in strictly sorted lexicographical order.</details>

---

## Practice - independent task

Implement **autocomplete with ranking** - the actual product feature.

- Extend the trie so each word carries a frequency count.
- `suggest(prefix, k)` returns the `k` most frequent completions.
- The naive version collects every completion and sorts. For a prefix like `"a"` on a large dictionary that is very slow.
- Improve it: store at each node the best score in its subtree, then explore with a priority queue ([[08-heaps|heap]]), always expanding the most promising branch first.
- Test on at least 500 words with varied frequencies.

**Done when:** ranked suggestions are correct, and you can show your improved version visits far fewer nodes than the collect-everything approach for a short prefix.

<details><summary>Hint - open only after an attempt</summary>
Store <code>best_below</code> at each node: the highest frequency of any word in that subtree. Then a best-first search using a max-heap keyed on <code>best_below</code> expands only branches that could still contain a top-k answer.<br>
This is the same idea as branch-and-bound: <strong>an upper bound on what a branch could yield lets you skip it entirely</strong>. Without the bound you must explore everything to be sure.
</details>

## Before moving on

You are done with this module when you can, closed-book:

- [ ] Explain how the path from the root spells the key.
- [ ] Explain why lookup cost depends on key length, not on the number of keys.
- [ ] Explain why a hash map destroys the prefix relationship.
- [ ] State when a trie costs more memory than it is worth.

**Recap:** A trie stores keys as paths, so common prefixes are shared rather than duplicated and lookup costs O(length) regardless of how many keys exist. A separate flag marks which paths are complete words, distinguishing a prefix from a key. Because a hash map hashes the whole key, it destroys any relationship between similar keys - which is why prefix search and autocomplete need a trie. The cost is memory per node, so tries are a poor choice when keys share little.

**Next:** [[10-union-find|Union-Find]] - the last structure here, and the one that answers a question none of the others can.

## Related Modules
- [[03-hash-maps|Hash Maps]] — The $O(1)$ exact-match alternative
- [[01-trees|Trees]] — General tree hierarchies
- [[02-dfs|Depth-First Search (DFS)]] — Traversing Tries for wildcard and grid search (Word Search II)
