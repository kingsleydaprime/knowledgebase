# Module: Level-Order Traversal (Breadth-First)

**[Intermediate]** — visiting a tree one depth at a time, and the queue that makes it work.

## Before you start

- You know the depth-first orders — [[01-depth-first-traversals|depth-first traversals]].
- You know what a queue does — [[../../07-stacks-and-queues|stacks and queues]].

**After this lesson you will be able to:**

1. Perform a level-order traversal by hand, and implement it with a queue.
2. Produce output **grouped by level**, not just a flat sequence.
3. Say when level-order is the right choice and when depth-first is.
4. Explain why this traversal uses a queue where the others use a stack.

**Study route:** read the mechanism, then the grouped-by-level variant, then the comparison at the end.

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

## Before moving on

You can implement level-order traversal, group its output by level, and say when to prefer it.

**Recap:** level-order visits every node at one depth before moving deeper, using a **queue** rather than a stack; it costs $O(n)$ time and $O(w)$ space where $w$ is the widest level — which for a perfect tree is about $n/2$, so it can use far more memory than a depth-first traversal on the same tree; it is the right choice when the answer depends on depth, such as finding the shallowest node satisfying something, or printing a tree level by level.

## Related

- [[index|the traversal folder]]
- [[01-depth-first-traversals|Depth-First Traversals]] — the other three orders
- [[../../../03-algorithms/03-bfs|Breadth-First Search]] — the same idea on a general graph
