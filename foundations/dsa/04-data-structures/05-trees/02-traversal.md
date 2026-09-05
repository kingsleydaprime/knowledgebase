# Module: Tree Traversal (Visiting Every Node)

Welcome to the **Tree Traversal** module. Traversal means systematically visiting every single node in a data structure exactly once.

In linear structures like [[01-arrays|Arrays]] or [[04-linked-lists|Linked Lists]], traversal is simple—you start at the beginning and move in a straight line to the end. In branching structures like [[01-trees|Trees]] and [[06-graphs|Graphs]], traversal requires a defined strategy because each node can have multiple paths leading away from it.

---

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

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: You have a binary search tree (BST). Which traversal order should you use to print all values in ascending order?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>Inorder Traversal</b> (Left -> Node -> Right).</details>

2. **Question**: Why is Postorder traversal preferred over Preorder traversal when deleting nodes or freeing memory allocated for a tree in C/C++?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Postorder visits children <b>before</b> their parent. If you delete the parent node first (Preorder), you lose the pointers to its children, causing memory leaks.</details>

3. **Question**: Which data structure is required to implement Level-Order traversal iteratively, and why?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A <b>FIFO Queue</b>. It ensures nodes are processed in First-In, First-Out order, visiting all nodes at level <code>k</code> before moving to level <code>k+1</code>.</details>

---

## Related Modules
- [[01-trees|Trees]] — Binary Tree definitions, heights, and shapes
- [[02-dfs|Depth-First Search (DFS)]] — DFS algorithms on graphs
- [[03-bfs|Breadth-First Search (BFS)]] — BFS shortest path algorithms
- [[07-stacks-and-queues|Stacks and Queues]] — Detailed queue and stack mechanics
