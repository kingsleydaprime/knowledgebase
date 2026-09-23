# Tries / Prefix Trees — Question Bank

Micro-questions over [[09-tries|the tries module]]. Answer in a full sentence before opening the toggle. Format explained in [[01-arrays-qb|the arrays bank]].

---

## A. The object

**1. What is a trie?**

<details><summary>Answer</summary>

A tree where **the path you walk spells out a word**, rather than any single node holding one. Also called a prefix tree.

</details>

**2. Where does the name come from, and how is it pronounced?**

<details><summary>Answer</summary>

From "re**trie**val", and usually pronounced "try".

</details>

**3. What does the root node represent?**

<details><summary>Answer</summary>

The **empty string**. Every word's path begins there.

</details>

**4. What is a character edge?**

<details><summary>Answer</summary>

A link from one node to the next, labelled with a single character. Walking `a` then `p` puts you at the node for the prefix `"ap"`.

</details>

**5. State the trie's defining feature.**

<details><summary>Answer</summary>

**Every prefix is an actual place in the structure** — which is exactly why prefix questions are cheap.

</details>

**6. Draw the trie for `app`, `apple`, `apt`, `cat`.**

<details><summary>Answer</summary>

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
'e'*          (* = is_end)
```

</details>

---

## B. `is_end`

**7. What is the `is_end` flag?**

<details><summary>Answer</summary>

A true/false marker saying "a complete word ends here".

</details>

**8. Why is it necessary?**

<details><summary>Answer</summary>

Because a node can be **passed through** on the way to a longer word without being a word itself. The flag separates `"app"`, which is a word, from `"appl"`, which is only a stop on the way to `"apple"`.

</details>

**9. What breaks if you forget it?**

<details><summary>Answer</summary>

The trie cannot distinguish an actual word from a prefix of a longer one — `search("appl")` returns true.

</details>

---

## C. Alphabet size and memory

**10. What is $\Sigma$, and what are typical values?**

<details><summary>Answer</summary>

The alphabet size — how many characters can follow any node. 26 for lowercase English, 128 for ASCII, over a million for full Unicode.

</details>

**11. Why does $\Sigma$ matter so much?**

<details><summary>Answer</summary>

**It decides how much memory a trie costs**, which is its main drawback. Every node may hold up to $\Sigma$ child pointers, and most sit empty.

</details>

**12. What should `children` be in practice, and why?**

<details><summary>Answer</summary>

A **dictionary**, not a fixed array of size 26. A fixed array over Unicode or multilingual input wastes enormous memory on empty slots.

</details>

---

## D. The ADT

**13. What does $L$ mean in every trie cost, and why is that unusual?**

<details><summary>Answer</summary>

The **length of the word being handled** — *not* the number of words stored. Searching a trie of ten words and a trie of ten million costs the same for a five-letter word.

</details>

**14. List the trie ADT with costs.**

<details><summary>Answer</summary>

`insert(word)` $O(L)$; `search(word)` $O(L)$; `starts_with(prefix)` $O(L)$; `delete(word)` $O(L)$; `words_with_prefix(prefix)` $O(L)$ plus the time to collect what hangs below.

</details>

**15. Which operation is the reason tries exist?**

<details><summary>Answer</summary>

`starts_with(prefix)` — **the operation a hash set cannot do at all.**

</details>

**16. Why can a hash set not do it?**

<details><summary>Answer</summary>

**Hashing destroys the relationship between `"app"` and `"apple"`.** A hash set would have to check every stored word.

</details>

**17. What is `words_with_prefix` in product terms?**

<details><summary>Answer</summary>

**Autocomplete.**

</details>

**18. How does `search` differ from `starts_with` in code?**

<details><summary>Answer</summary>

Both walk the same path. `search` additionally requires `node.is_end`; `starts_with` only requires that the node exists.

</details>

---

## E. The trade

**19. What does a trie gain over a hash set?**

<details><summary>Answer</summary>

Prefix search; **ordered iteration** (walking children alphabetically yields sorted words); and a lookup cost that does not grow with the number of stored words.

</details>

**20. What does it cost?**

<details><summary>Answer</summary>

Far more memory — $O(N \cdot L \cdot \Sigma)$ in the worst case. A trie over full Unicode is impractical without a compressed variant.

</details>

**21. Where does a trie actually lose?**

<details><summary>Answer</summary>

**Plain exact-match lookup in practice.** A hash set is $O(1)$ against the trie's $O(L)$, with much better cache behaviour — trie nodes are scattered like [[04-linked-lists|linked list]] nodes.

</details>

**22. Give the decision rule.**

<details><summary>Answer</summary>

**Use a trie when the question is about prefixes.** If you only ever ask "is this exact word present?", use a hash set.

</details>

**23. Compare sorted traversal cost in each.**

<details><summary>Answer</summary>

Hash set: $O(N \log N)$ — you must sort. Trie: $O(N)$ **for free**, by pre-order traversal visiting children alphabetically.

</details>

---

## F. Wildcard search

**24. What happens to the lookup when the query contains `.`?**

<details><summary>Answer</summary>

The single-path lookup becomes a **depth-first search** over all child branches.

</details>

**25. Write the recursive rule.**

<details><summary>Answer</summary>

At index $i$: if the char is `.`, recurse into **every** child; otherwise recurse into that one child if it exists. At $i = $ len(word), return `node.is_end`.

</details>

**26. What is the cost of a wildcard search?**

<details><summary>Answer</summary>

Up to $O(\Sigma^k \cdot L)$ where $k$ is the number of wildcards — each `.` multiplies the branching. A query of all dots scans the whole trie.

</details>

---

## G. Deletion and traps

**27. Why is deletion the fiddliest operation?**

<details><summary>Answer</summary>

Clearing `is_end` is easy; **pruning** is not. You may only remove a node if it has no other children *and* is not the end of another word — so you prune recursively back up the path.

</details>

**28. What is the memory-overuse trap?**

<details><summary>Answer</summary>

Fixed arrays of size 26 (or 128, or Unicode-sized) at every node. Use a dynamic dictionary instead.

</details>

**29. Summarise the trie in one sentence.**

<details><summary>Answer</summary>

Store words as paths so that every prefix becomes an address — costs $O(L)$ regardless of how many words there are, buys prefix queries and sorted order, and pays in memory.

</details>

---

## Scorecard

| Pass | Date | Got it | Close | Blank | Questions missed |
| :--- | :--- | :----- | :---- | :---- | :--------------- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

---

## Related

- [[09-tries|Tries / Prefix Trees]] — the module
- [[03-hash-maps-qb|Hash Maps — Question Bank]] — the structure this one is measured against
- [[05-trees/01-trees-qb|Trees — Question Bank]] — the shape underneath
