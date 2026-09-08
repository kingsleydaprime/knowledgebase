# Module: Stacks and Queues (LIFO & FIFO Collections)

Welcome to the **Stacks and Queues** module. Both Stacks and Queues are linear data structures with constrained interfaces: you can only insert and remove elements at specific ends.

Despite their simplicity, Stacks and Queues drive core software systems—from CPU call stacks and browser history to network packet buffers and graph traversal algorithms (**DFS** and **BFS**).

---

## 1. Real-World Motivation & Physical Metaphors

```
STACK (LIFO):                              QUEUE (FIFO):
  [ Plate 3 ]  <-- Top (Push/Pop)           Enqueue -> [ 3 ][ 2 ][ 1 ] -> Dequeue
  [ Plate 2 ]                                           (Tail)   (Head)
  [ Plate 1 ]
```

### 1. Stack — Last-In, First-Out (LIFO)
Imagine a physical **stack of cafeteria trays**:
- The last tray placed on top of the pile is the very first tray picked up by a customer.
- **Key Principle**: Insertions (`Push`) and Deletions (`Pop`) happen at the **same end (The Top)**.

### 2. Queue — First-In, First-Out (FIFO)
Imagine a **supermarket checkout line**:
- New customers join the **back (Tail)** of the line. The customer who has been waiting longest at the **front (Head)** gets served first.
- **Key Principle**: Insertions (`Enqueue`) happen at the **Tail**; Deletions (`Dequeue`) happen at the **Head**.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Example / Analogy |
| :--- | :--- | :--- |
| **LIFO** | Last-In, First-Out (Stack behavior). | Undo history (`Ctrl + Z`). |
| **FIFO** | First-In, First-Out (Queue behavior). | Printer print job queue. |
| **Push / Enqueue** | Adding a new element to the collection. | Adding a plate to top of stack / joining back of line. |
| **Pop / Dequeue** | Removing an element from the collection. | Taking top plate off stack / serving customer at front of line. |
| **Peek (Top / Front)**| Looking at the next element without removing it. | Checking what's at the top of the stack. |
| **Circular Buffer** | Implementing a fixed-capacity FIFO queue in a flat array using modulo `% N`. | Ring buffer for audio streaming. |

---

## 3. Stacks: Mechanics & Applications

### Python Stack Implementation ($O(1)$ Operations)
In Python, a standard `list` functions as a high-performance stack using `.append()` and `.pop()`:

```python
class Stack:
    """LIFO Stack implementation using dynamic array."""
    def __init__(self):
        self.items = []
        
    def push(self, val):
        self.items.append(val)  # O(1) Amortized
        
    def pop(self):
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self.items.pop()  # O(1) from end of array
        
    def peek(self):
        return self.items[-1] if not self.is_empty() else None
        
    def is_empty(self):
        return len(self.items) == 0
```

### Where Stacks Are Used in Production
1. **Function Call Stack**: Tracking active function calls, local variables, and return addresses in memory.
2. **Undo / Redo Mechanisms**: `Ctrl + Z` pops the most recent action off the undo stack.
3. **Balanced Parentheses Validation**: Matching opening `(` and closing `)` brackets.
4. **Depth-First Search (DFS)**: Exploring graph/tree paths using recursive or explicit stacks.

---

## 4. Queues: Mechanics & The `pop(0)` Performance Trap

> [!WARNING]
> **Python Performance Trap**: Writing `queue.pop(0)` on a standard Python list is an **$O(n)$ disaster**! It removes the item at index 0 and shifts every single remaining item left by 1 position in RAM.

### Correct Python Queue Implementation using `collections.deque`
To achieve true **$O(1)$ Dequeue** operations, use a Doubly-Linked List (`collections.deque`):

```python
from collections import deque

class Queue:
    """FIFO Queue implementation using doubly linked deque."""
    def __init__(self):
        self.items = deque()
        
    def enqueue(self, val):
        self.items.append(val)     # Add to Tail: O(1)
        
    def dequeue(self):
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        return self.items.popleft() # Remove from Head: O(1)!
        
    def is_empty(self):
        return len(self.items) == 0
```

---

## 5. Low-Level Circular Buffer (Array Queue)

In low-level systems (C, OS kernels, audio drivers), queues are implemented in a fixed-size array without memory allocations using **modulo arithmetic (`% N`)**:

```python
class CircularQueue:
    """Fixed-capacity Queue using array modulo wraparound."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.head = 0
        self.tail = 0
        self.size = 0
        
    def enqueue(self, val) -> bool:
        if self.size == self.capacity:
            return False  # Queue Full
        self.queue[self.tail] = val
        self.tail = (self.tail + 1) % self.capacity  # Wraparound index
        self.size += 1
        return True
        
    def dequeue(self):
        if self.size == 0:
            return None   # Queue Empty
        val = self.queue[self.head]
        self.queue[self.head] = None
        self.head = (self.head + 1) % self.capacity  # Wraparound index
        self.size -= 1
        return val
```

---

## 6. Time & Space Complexity Summary

| Data Structure | Insertion (Push / Enqueue) | Deletion (Pop / Dequeue) | Lookup Top/Front | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Stack (Array-backed)** | **$O(1)$ Amortized** | **$O(1)$** | **$O(1)$** | $O(n)$ |
| **Queue (`deque`)** | **$O(1)$** | **$O(1)$** | **$O(1)$** | $O(n)$ |
| **Queue (Naive `list.pop(0)`)** | $O(1)$ | **$O(n)$ (SLOW)** | $O(1)$ | $O(n)$ |
| **Circular Buffer** | **$O(1)$** | **$O(1)$** | **$O(1)$** | $O(\text{Capacity})$ |

---

## 7. Common Pitfalls & Traps

1. **`list.pop(0)` in Python**: Always use `collections.deque.popleft()` for $O(1)$ FIFO queues instead of `list.pop(0)`.
2. **Stack Overflow**: Infinite recursive calls fill the call stack memory, throwing a stack overflow error.
3. **Queue Underflow / Empty Pop**: Popping from an empty stack or queue without checking `is_empty()` crashes with index errors.

---

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: What is the difference between LIFO and FIFO? Give one real-world application for each.
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>LIFO</b> (Last-In, First-Out) processes the newest element first (e.g., Undo history <code>Ctrl+Z</code>). <b>FIFO</b> (First-In, First-Out) processes the oldest element first (e.g., Printer queue, supermarket checkout line).</details>

2. **Question**: Why is `list.pop(0)` slow in Python, and what structure should be used instead?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <code>list.pop(0)</code> removes the element at index 0, forcing Python to shift all remaining elements left by 1 position in memory (an <b>O(n)</b> operation). Use <code>collections.deque.popleft()</code> instead, which runs in <b>O(1)</b> time.</details>

3. **Question**: Which data structure is used to implement Depth-First Search (DFS), and which is used for Breadth-First Search (BFS)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>DFS</b> uses a <b>Stack (LIFO)</b> (or recursion call stack). <b>BFS</b> uses a <b>Queue (FIFO)</b>.</details>

---

## Related Modules
- [[01-arrays|Arrays]] — The memory structure backing array-based stacks
- [[04-linked-lists|Linked Lists]] — Node structure backing `collections.deque`
- [[02-dfs|DFS]] & [[03-bfs|BFS]] — Traversals powered by Stacks and Queues
