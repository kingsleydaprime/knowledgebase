# Module: Depth-First Traversals (Pre-order, In-order, Post-order)

**[Intermediate]** — three orders that differ by one line, and the different jobs each one is right for.

## Before you start

- You know what a binary tree is — [[../02-binary-trees|binary trees]].
- You can trace a recursive call, and you know what a stack does — [[../../07-stacks-and-queues|stacks and queues]].

**After this lesson you will be able to:**

1. Perform all three depth-first traversals by hand on a given tree.
2. Say which job each order is right for, and why.
3. Write each one recursively **and** iteratively with an explicit stack.
4. Explain why in-order traversal of a binary search tree comes out sorted.

**Study route:** read the orders, trace each on the reference tree by hand, then run the lab.

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

## Terms used with tree traversal

1. **Traversal**: This means visiting every node in a tree exactly once, in some definite order. The tree itself does not change; what changes is the **sequence** in which you see the nodes.

2. **Visit**: This is the moment you actually do something with a node — print it, add it to a list, compare it. The whole difference between the traversal orders is *when* the visit happens relative to the recursive calls.

3. **Depth-first traversal**: This means going as deep as possible down one branch before backing up and trying another. It uses a stack, either an explicit one or the call stack that recursion provides.

4. **Breadth-first traversal**: This means visiting every node at one depth before moving to the next depth down. It uses a queue. It is also called **level-order traversal**.

5. **Pre-order**: Visit the node **first**, then its left subtree, then its right subtree. The root comes out first, which is what makes it right for copying a tree or writing it out to a file.

6. **In-order**: Visit the left subtree, then the node, then the right subtree. On a [[../03-binary-search-trees|binary search tree]] this produces the values in **sorted order**, which is its main use.

7. **Post-order**: Visit the left subtree, then the right subtree, then the node **last**. A node is only visited after everything beneath it, which is what makes it right for deleting a tree or evaluating an expression.

8. **Level-order**: Visit all nodes at depth 0, then all at depth 1, and so on. This is [[../../../03-algorithms/03-bfs|breadth-first search]] applied to a tree.

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

You can perform all three orders by hand, write each recursively and iteratively, and say what each is for.

**Recap:** all three are depth-first and all three cost $O(n)$ time and $O(h)$ space; they differ only in **when the node is visited** relative to its subtrees — **pre-order** visits the node first and is for copying or serialising, **in-order** visits it in the middle and yields sorted output on a binary search tree, **post-order** visits it last and is for deleting or evaluating. The recursive versions are three lines each; the iterative versions replace the call stack with an explicit one, and post-order is the awkward one.

**Next:** [[02-level-order-traversal|Level-Order Traversal]] — the one that is not depth-first.

## Related

- [[index|the traversal folder]]
- [[../03-binary-search-trees|Binary Search Trees]] — where in-order matters most
- [[../../../03-algorithms/02-dfs|Depth-First Search]] — the same idea on a general graph, where you also need a visited set
