# Module: Tries / Prefix Trees (Shared Prefix Search)

Welcome to the **Trie** (pronounced *"try"*, short for re**TRIE**val) module. A Trie is a tree-based data structure optimized for storing strings by sharing common letter prefixes.

Tries trade extra memory to grant a superpower that [[03-hash-maps|Hash Maps]] cannot match: **answering "Does any word start with this prefix?" in $O(L)$ time**, where $L$ is the length of the prefix, regardless of whether the dictionary contains 10 words or 10,000,000 words!

---

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

## 9. Check Your Understanding (University Self-Assessment)

1. **Question**: Why can't a Hash Set perform prefix searches (`startsWith("app")`) in $O(L)$ time?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A Hash Set hashes the entire string to compute an index. Searching for a prefix gives a completely different hash than the full word (e.g., <code>hash("app") != hash("apple")</code>). To check prefixes, a Hash Set must scan every key one-by-one (<b>O(N)</b>).</details>

2. **Question**: What is the purpose of the `is_end` boolean flag in a `TrieNode`?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The <code>is_end</code> flag indicates that a valid word terminates at that node. Without it, searching for <code>"app"</code> in a Trie containing only <code>"apple"</code> would incorrectly return <code>True</code>.</details>

3. **Question**: How does a Trie automatically provide sorted (alphabetical) word output?
   - <details><summary>Click for Answer</summary><b>Answer:</b> By performing a <b>Preorder Traversal</b> over the Trie while iterating child keys in alphabetical order ('a' to 'z'), words are visited in strictly sorted lexicographical order.</details>

---

## Related Modules
- [[03-hash-maps|Hash Maps]] — The $O(1)$ exact-match alternative
- [[01-trees|Trees]] — General tree hierarchies
- [[02-dfs|Depth-First Search (DFS)]] — Traversing Tries for wildcard and grid search (Word Search II)
