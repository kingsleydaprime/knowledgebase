# Binary Tree Traversal Pattern — Question Bank

Micro-questions over [[10-binary-tree-traversal-pattern|the tree traversal pattern]]. Answer in a full sentence before opening the toggle. Format explained in [[dsa/02-data-structures/01-arrays-qb|the arrays bank]].

This bank is about **choosing** an order. The mechanics are in [[dsa/02-data-structures/05-trees/04-traversal/01-depth-first-traversals-qb|the traversal bank]].

---

## A. What this note is for

**1. What question does this pattern answer, as opposed to the traversal module?**

<details><summary>Answer</summary>

**Recognising *when each order is the right tool*** — the mechanics of pre/in/post-order are elsewhere; **choosing between them is the part that shows up as a decision.**

</details>

**2. Give the file-browser illustration of all three.**

<details><summary>Answer</summary>

**Preorder**: list a directory before its contents. **Postorder**: compute a directory's size after all subdirectory sizes. **Inorder**: list values in sorted order (BSTs only).

</details>

---

## B. Preorder

**3. When do you use it?**

<details><summary>Answer</summary>

When you need to process or record a node **before** its children.

</details>

**4. Give the canonical problem.**

<details><summary>Answer</summary>

**Building a root-to-leaf path string**, since you need the ancestors already collected before you reach a leaf.

</details>

**5. What exactly makes `binary_tree_paths` preorder?**

<details><summary>Answer</summary>

**`path` gets the current node appended *before* recursing into children** — so by the time you reach a leaf, `path` already holds the full chain of ancestors.

</details>

**6. What other operations are naturally preorder?**

<details><summary>Answer</summary>

**Copying a tree** and **serialising it**, since the root must come first.

</details>

---

## C. Postorder

**7. When do you use it?**

<details><summary>Answer</summary>

When **a node's answer depends on its children's answers first.**

</details>

**8. Give the canonical problem.**

<details><summary>Answer</summary>

**Maximum path sum through a subtree** — you need the best path from each child before combining at the parent.

</details>

**9. In max path sum, why is `max(dfs(node.left), 0)` used?**

<details><summary>Answer</summary>

**To ignore negative contributions** — a child path that loses value is better not taken at all.

</details>

**10. Why does the function return something different from what it records?**

<details><summary>Answer</summary>

It **records** `node.val + left + right` — a path that turns at this node — but **returns** `node.val + max(left, right)`, because **a path passing through to the parent can only use one side.**

</details>

---

## D. Inorder

**11. When do you use it?**

<details><summary>Answer</summary>

**On a BST, when you need sorted output.**

</details>

**12. Why does inorder on a BST give sorted values?**

<details><summary>Answer</summary>

The BST invariant says everything left of a node is smaller and everything right is larger — so **visiting left, then node, then right emits values in ascending order by construction.**

</details>

**13. Does inorder give sorted output on any binary tree?**

<details><summary>Answer</summary>

**No — only on a BST.** On an arbitrary binary tree it guarantees nothing.

</details>

---

## E. Choosing

**14. Give the four-row choice table.**

<details><summary>Answer</summary>

**Preorder** — copying a tree, building a path string. **Inorder** — BSTs needing sorted output. **Postorder** — a node's answer depends on its children's. **Level-order (BFS)** — processing level by level.

</details>

**15. State the deciding question in one line.**

<details><summary>Answer</summary>

**Does this node's answer depend on what is above it (preorder), below it (postorder), or on its ordering (inorder)?**

</details>

**16. Summarise the pattern in one sentence.**

<details><summary>Answer</summary>

Pick the order by where the information flows — down from ancestors, up from children, or across in sorted sequence.

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

- [[10-binary-tree-traversal-pattern|Binary Tree Traversal Pattern]] — the pattern
- [[dsa/02-data-structures/05-trees/04-traversal/01-depth-first-traversals-qb|Depth-First Traversals — Question Bank]] — the mechanics
- [[11-dfs-pattern-qb|DFS Pattern — Question Bank]]
