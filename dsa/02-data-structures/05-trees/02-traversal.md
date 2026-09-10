# Module: Tree Traversal (Visiting Every Node)

Welcome to the **Tree Traversal** module. Traversal means systematically visiting every single node in a data structure exactly once.

In linear structures like [[01-arrays|Arrays]] or [[04-linked-lists|Linked Lists]], traversal is simple—you start at the beginning and move in a straight line to the end. In branching structures like [[01-trees|Trees]] and [[06-graphs/index|Graphs]], traversal requires a defined strategy because each node can have multiple paths leading away from it.

---

## Before you start

- You understand tree structure and the BST property. See [[01-trees|trees]].
- You know that recursion uses a call stack. See [[07-stacks-and-queues|stacks and queues]].

**What you will be able to do after this lesson:**

1. State what pre-, in- and post-order produce and when each is correct.
2. Choose the right traversal from the direction the data flows.
3. Implement a traversal both recursively and with an explicit stack.
4. Explain why level-order needs a queue rather than a stack.

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

## 1. Why Tree Traversal Strategies Matter (Real-World Motivation)

Imagine inspecting a company's organizational chart:
- **Scenario A (Top-Down Management Briefing)**: You talk to the CEO first, then the VPs, then the engineers. (**Preorder**)
- **Scenario B (Alphabetical / Sorted Roll Call)**: You list all employees in alphabetical order. (**Inorder**)
- **Scenario C (Bottom-Up Expense Report Aggregation)**: Engineers calculate costs, pass them up to Directors, and finally up to the CEO. (**Postorder**)
- **Scenario D (Level-by-Level Audit)**: You inspect everyone at Executive level, then Manager level, then Staff level. (**Level-order / BFS**)

Each scenario visits the exact same people, but the **order of visitation** is tailored to solve a specific problem!

---

## 2. Visual Reference Tree

Throughout this module, we will trace the 4 primary traversal orders using this binary tree:

```
        (1)            <-- Root
       /   \
     (2)   (3)         <-- Level 1
    /   \
  (4)   (5)            <-- Level 2
```

---

## 3. Plain-English Terminology & Concept Table

| Traversal Strategy | Mnemonic Rule | Visited Sequence | Common Use Case |
| :--- | :--- | :--- | :--- |
| **Preorder** | **Node** $\rightarrow$ Left $\rightarrow$ Right | `1, 2, 4, 5, 3` | Cloning/serializing a tree, folder hierarchy printing. |
| **Inorder** | Left $\rightarrow$ **Node** $\rightarrow$ Right | `4, 2, 5, 1, 3` | **BST sorted order retrieval**. |
| **Postorder** | Left $\rightarrow$ Right $\rightarrow$ **Node** | `4, 5, 2, 3, 1` | Deleting nodes bottom-up, evaluating expression trees. |
| **Level-Order** | Level by Level (Left to Right) | `1, 2, 3, 4, 5` | Printing org charts, finding shortest path in unweighted graphs. |

---

## 4. Depth-First Traversals (Preorder, Inorder, Postorder)

The first three traversals are **Depth-First Search (DFS)** strategies. They commit to exploring down a branch as far as possible before backtracking.

### 1. Preorder Traversal (Root $\rightarrow$ Left $\rightarrow$ Right)
Processes the current node **before** inspecting its subtrees.

```python
def preorder(node: TreeNode, result: list):
    """Preorder traversal: Process Node first."""
    if node is None:
        return
    
    result.append(node.val)      # 1. Process current node
    preorder(node.left, result)  # 2. Recurse left
    preorder(node.right, result) # 3. Recurse right

# Visited Order: [1, 2, 4, 5, 3]
```

---

### 2. Inorder Traversal (Left $\rightarrow$ Root $\rightarrow$ Right)
Processes the current node **between** visiting the left and right subtrees.

```python
def inorder(node: TreeNode, result: list):
    """Inorder traversal: Process Node between subtrees."""
    if node is None:
        return
    
    inorder(node.left, result)   # 1. Recurse left
    result.append(node.val)      # 2. Process current node
    inorder(node.right, result)  # 3. Recurse right

# Visited Order: [4, 2, 5, 1, 3]
```
> [!IMPORTANT]
> **The BST Inorder Guarantee**: Running an Inorder traversal on a Binary Search Tree (BST) will ALWAYS produce the values in **strictly sorted ascending order**!

---

### 3. Postorder Traversal (Left $\rightarrow$ Right $\rightarrow$ Root)
Processes children completely **before** processing the parent node.

```python
def postorder(node: TreeNode, result: list):
    """Postorder traversal: Process Node last."""
    if node is None:
        return
    
    postorder(node.left, result)   # 1. Recurse left
    postorder(node.right, result)  # 2. Recurse right
    result.append(node.val)        # 3. Process current node

# Visited Order: [4, 5, 2, 3, 1]
```
*Why Postorder is special*: Essential when a parent node requires calculation results from both of its children before it can compute its own answer (e.g. calculating directory file sizes, freeing memory in C).

---

## 5. Breadth-First Traversal (Level-Order Traversal)

Unlike DFS traversals, **Level-Order Traversal** visits nodes level by level from top to bottom, left to right.

Because recursion uses a LIFO call stack, Level-Order cannot be written recursively. It uses an explicit **Queue (FIFO)** data structure:

```python
from collections import deque

def level_order(root: TreeNode) -> list:
    """Level-order traversal using an explicit Queue."""
    if root is None:
        return []
    
    result = []
    queue = deque([root])  # Initialize FIFO Queue with root
    
    while queue:
        current = queue.popleft()  # Remove next node from queue
        result.append(current.val)
        
        # Enqueue left child if it exists
        if current.left:
            queue.append(current.left)
            
        # Enqueue right child if it exists
        if current.right:
            queue.append(current.right)
            
    return result

# Visited Order: [1, 2, 3, 4, 5]
```

---

## 6. Time & Space Complexity Summary

| Traversal Type | Time Complexity | Space Complexity (Auxiliary Stack/Queue) |
| :--- | :--- | :--- |
| **Preorder (DFS)** | $O(n)$ | $O(h)$ call stack space ($h = \text{height of tree}$). |
| **Inorder (DFS)** | $O(n)$ | $O(h)$ call stack space ($O(\log n)$ balanced, $O(n)$ degenerate). |
| **Postorder (DFS)** | $O(n)$ | $O(h)$ call stack space. |
| **Level-Order (BFS)** | $O(n)$ | $O(w)$ queue space ($w = \text{max width of tree}$, up to $N/2$ leaves). |

---

## 7. Common Pitfalls & Traps

1. **Stack Overflow on Deep Trees**: Recursive DFS uses the CPU call stack. For a degenerate tree of height $10,000$, recursive traversal causes a `RecursionError` / Stack Overflow. Use an explicit iterative stack for deep trees.
2. **Queue vs Stack Trap in BFS**: Level-order requires a **FIFO Queue** (`popleft()`). Accidental use of a LIFO Stack (`pop()`) turns BFS into a bizarre right-to-left DFS traversal!
3. **Inorder Fallacy**: Inorder traversal only produces sorted output on **Binary Search Trees (BSTs)**. On arbitrary binary trees, it does not guarantee sorted order.

---

## Implementation - complete runnable example

**Runnable example:** save as `traversal_lab.py` and run `python3 traversal_lab.py`. Standard library only; writes no files. Everything is counted rather than timed, so your output will match this exactly.

```python
"""Tree traversal: the three depth-first orders, and choosing between them."""
from collections import deque

class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

#         1
#       /   \
#      2     3
#     / \     \
#    4   5     6
TREE = Node(1, Node(2, Node(4), Node(5)), Node(3, None, Node(6)))

def preorder(n):
    return [] if n is None else [n.val] + preorder(n.left) + preorder(n.right)

def inorder(n):
    return [] if n is None else inorder(n.left) + [n.val] + inorder(n.right)

def postorder(n):
    return [] if n is None else postorder(n.left) + postorder(n.right) + [n.val]

def levelorder(root):
    """Breadth-first: a queue instead of the call stack."""
    out, q = [], deque([root] if root else [])
    while q:
        n = q.popleft()
        out.append(n.val)
        if n.left:  q.append(n.left)
        if n.right: q.append(n.right)
    return out

def preorder_iterative(root):
    """Explicit stack. Push right first so left is processed first."""
    out, stack = [], [root] if root else []
    while stack:
        n = stack.pop()
        out.append(n.val)
        if n.right: stack.append(n.right)
        if n.left:  stack.append(n.left)
    return out

# --- the point: which order does a given problem NEED? ---
def depth_of_each(n, depth=0):
    """Top-down: a node's answer depends on its ANCESTORS -> PREORDER."""
    if n is None: return {}
    out = {n.val: depth}
    out.update(depth_of_each(n.left, depth + 1))
    out.update(depth_of_each(n.right, depth + 1))
    return out

def height_of(n):
    """Bottom-up: a node's answer depends on its CHILDREN -> POSTORDER."""
    if n is None: return 0
    return 1 + max(height_of(n.left), height_of(n.right))

def is_bst(n, lo=float("-inf"), hi=float("inf")):
    """In-order on a BST is sorted -- so validity is an ordering check."""
    if n is None: return True
    return (lo < n.val < hi
            and is_bst(n.left, lo, n.val)
            and is_bst(n.right, n.val, hi))

if __name__ == "__main__":
    print("ONE TREE, FOUR ORDERS")
    print("        1")
    print("      /   \\")
    print("     2     3")
    print("    / \\     \\")
    print("   4   5     6")
    print()
    print(f"  pre-order   (node, left, right) : {preorder(TREE)}")
    print(f"  in-order    (left, node, right) : {inorder(TREE)}")
    print(f"  post-order  (left, right, node) : {postorder(TREE)}")
    print(f"  level-order (breadth-first)     : {levelorder(TREE)}")
    print()
    print("  the three depth-first orders differ ONLY in when the node is")
    print("  visited relative to its subtrees. That timing is the choice.")
    print()

    print("CHOOSING THE ORDER -- it is decided by the data flow")
    print(f"  depth of each node (top-down, needs ANCESTORS -> pre-order):")
    print(f"    {depth_of_each(TREE)}")
    print(f"  height of the tree (bottom-up, needs CHILDREN -> post-order):")
    print(f"    {height_of(TREE)}")
    print()
    print("  RULE: if a node's answer depends on what is ABOVE it, go")
    print("  top-down (pre-order). If it depends on what is BELOW it, go")
    print("  bottom-up (post-order). Getting this backwards is why a")
    print("  traversal 'nearly works'.")
    print()

    print("IN-ORDER ON A BST IS SORTED -- so it validates one")
    bst = Node(5, Node(3, Node(1), Node(4)), Node(8, Node(7), Node(9)))
    broken = Node(5, Node(3, Node(1), Node(6)), Node(8))   # 6 > 5, wrong side
    for name, t in (("valid BST", bst), ("broken BST", broken)):
        print(f"  {name:11s} in-order {str(inorder(t)):28s} sorted={inorder(t)==sorted(inorder(t))}  is_bst={is_bst(t)}")
    print()
    print("RECURSION IS JUST AN IMPLICIT STACK")
    print(f"  recursive pre-order : {preorder(TREE)}")
    print(f"  explicit-stack      : {preorder_iterative(TREE)}")
    print("  -> identical. The call stack WAS the stack all along.")

    assert preorder(TREE) == [1, 2, 4, 5, 3, 6]
    assert inorder(TREE) == [4, 2, 5, 1, 3, 6]
    assert postorder(TREE) == [4, 5, 2, 6, 3, 1]
    assert levelorder(TREE) == [1, 2, 3, 4, 5, 6]
    assert preorder_iterative(TREE) == preorder(TREE)
    assert height_of(TREE) == 3 and is_bst(bst) and not is_bst(broken)
    assert preorder(None) == [] and levelorder(None) == []
    print()
    print("traversal_lab: passed")
```

Expected output:

```
ONE TREE, FOUR ORDERS
        1
      /   \
     2     3
    / \     \
   4   5     6

  pre-order   (node, left, right) : [1, 2, 4, 5, 3, 6]
  in-order    (left, node, right) : [4, 2, 5, 1, 3, 6]
  post-order  (left, right, node) : [4, 5, 2, 6, 3, 1]
  level-order (breadth-first)     : [1, 2, 3, 4, 5, 6]

  the three depth-first orders differ ONLY in when the node is
  visited relative to its subtrees. That timing is the choice.

CHOOSING THE ORDER -- it is decided by the data flow
  depth of each node (top-down, needs ANCESTORS -> pre-order):
    {1: 0, 2: 1, 4: 2, 5: 2, 3: 1, 6: 2}
  height of the tree (bottom-up, needs CHILDREN -> post-order):
    3

  RULE: if a node's answer depends on what is ABOVE it, go
  top-down (pre-order). If it depends on what is BELOW it, go
  bottom-up (post-order). Getting this backwards is why a
  traversal 'nearly works'.

IN-ORDER ON A BST IS SORTED -- so it validates one
  valid BST   in-order [1, 3, 4, 5, 7, 8, 9]        sorted=True  is_bst=True
  broken BST  in-order [1, 3, 6, 5, 8]              sorted=False  is_bst=False

RECURSION IS JUST AN IMPLICIT STACK
  recursive pre-order : [1, 2, 4, 5, 3, 6]
  explicit-stack      : [1, 2, 4, 5, 3, 6]
  -> identical. The call stack WAS the stack all along.

traversal_lab: passed
```

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: You have a binary search tree (BST). Which traversal order should you use to print all values in ascending order?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>Inorder Traversal</b> (Left -> Node -> Right).</details>

2. **Question**: Why is Postorder traversal preferred over Preorder traversal when deleting nodes or freeing memory allocated for a tree in C/C++?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Postorder visits children <b>before</b> their parent. If you delete the parent node first (Preorder), you lose the pointers to its children, causing memory leaks.</details>

3. **Question**: Which data structure is required to implement Level-Order traversal iteratively, and why?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A <b>FIFO Queue</b>. It ensures nodes are processed in First-In, First-Out order, visiting all nodes at level <code>k</code> before moving to level <code>k+1</code>.</details>

---

## Practice - independent task

Implement **iterative in-order and post-order** traversals with an explicit stack.

- In-order iteratively is the classic interview question: push left as far as possible, pop, visit, then go right.
- Post-order is genuinely harder. Two approaches: use two stacks, or track the last visited node so you know whether you are descending or returning.
- Verify both against the recursive versions on at least five differently-shaped trees, including a single node, a left-only chain and a right-only chain.
- **Then measure:** build a left-only chain of 2000 nodes and run the recursive version. What happens?

**Done when:** both iterative traversals match the recursive ones on every test tree, and you can state the depth at which the recursive version fails and why.

<details><summary>Hint - open only after an attempt</summary>
For iterative post-order with one stack, the difficulty is knowing whether you are arriving at a node on the way <em>down</em> or on the way back <em>up</em> from its right child. Tracking the previously visited node tells you which.<br>
The two-stack trick avoids that entirely: do a modified pre-order visiting node-right-left, pushing each visited node onto a second stack. Popping that second stack yields left-right-node, which is post-order. <strong>Reversal turns one order into another</strong>, which is worth noticing.
</details>

## Before moving on

You are done with this module when you can, closed-book:

- [ ] State the three depth-first orders and what each produces on a sample tree.
- [ ] Choose the correct order given whether a node's answer depends on ancestors or children.
- [ ] Implement pre-order with an explicit stack and explain the push order.
- [ ] Explain why level-order uses a queue and what that costs in memory.

**Recap:** The three depth-first orders differ only in when the node is visited relative to its subtrees, and that timing is the entire choice. Pre-order suits top-down problems where a node's answer depends on its ancestors; post-order suits bottom-up problems where it depends on its children; in-order on a BST yields sorted output. Level-order uses a queue instead of a stack and visits by distance from the root. Recursion is an implicit stack, so any traversal can be written iteratively - and must be, when depth could overflow.

**Next:** [[06-graphs/index|Graphs]] - a tree is a graph with no cycles - remove that restriction and traversal needs one more thing.

## Related Modules
- [[01-trees|Trees]] — Binary Tree definitions, heights, and shapes
- [[02-dfs|Depth-First Search (DFS)]] — DFS algorithms on graphs
- [[03-bfs|Breadth-First Search (BFS)]] — BFS shortest path algorithms
- [[07-stacks-and-queues|Stacks and Queues]] — Detailed queue and stack mechanics
