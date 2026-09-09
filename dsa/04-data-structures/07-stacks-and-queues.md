# Module: Stacks and Queues (LIFO & FIFO Collections)

Welcome to the **Stacks and Queues** module. Both Stacks and Queues are linear data structures with constrained interfaces: you can only insert and remove elements at specific ends.

Despite their simplicity, Stacks and Queues drive core software systems—from CPU call stacks and browser history to network packet buffers and graph traversal algorithms (**DFS** and **BFS**).

---

## Before you start

- You understand dynamic arrays and why front removal is O(n). See [[02-dynamic-arrays|dynamic arrays]].
- You have seen DFS and BFS. See [[06-graphs|graphs]].

**What you will be able to do after this lesson:**

1. State the LIFO and FIFO orderings and which problems each suits.
2. Explain why a naive list-based queue is O(n) per dequeue.
3. Implement a queue from two stacks and explain its amortised O(1).
4. Explain why bracket matching is naturally a stack problem.

**Study route:** read the mechanism, run the lab, then attempt the independent task before opening the hint.

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

## Implementation - complete runnable example

**Runnable example:** save as `stacks_queues_lab.py` and run `python3 stacks_queues_lab.py`. Standard library only; writes no files. Everything is counted rather than timed, so your output will match this exactly.

```python
"""Stacks and queues: one restriction each, and what it buys."""

class Stack:
    """LIFO. Only the most recent item is reachable."""
    def __init__(self): self.items = []
    def push(self, x): self.items.append(x)
    def pop(self):
        if not self.items: raise IndexError("pop from empty stack")
        return self.items.pop()
    def peek(self): return self.items[-1] if self.items else None
    def empty(self): return not self.items

class Queue:
    """FIFO built on two stacks -- amortised O(1), no shifting.

    A naive list-based queue uses list.pop(0), which is O(n) because
    every remaining element shifts down."""
    def __init__(self):
        self.inbox, self.outbox, self.moves = [], [], 0
    def enqueue(self, x): self.inbox.append(x)
    def dequeue(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())
                self.moves += 1
        if not self.outbox: raise IndexError("dequeue from empty queue")
        return self.outbox.pop()
    def empty(self): return not self.inbox and not self.outbox

def balanced(text):
    """The classic stack problem: brackets must close in reverse order."""
    pairs, stack = {")": "(", "]": "[", "}": "{"}, Stack()
    for ch in text:
        if ch in "([{":
            stack.push(ch)
        elif ch in pairs:
            if stack.empty() or stack.pop() != pairs[ch]:
                return False
    return stack.empty()

def naive_dequeue_shifts(n):
    """Cost of list.pop(0) n times: every element after index 0 shifts."""
    return sum(range(n))

if __name__ == "__main__":
    print("A STACK IS LIFO -- last in, first out")
    s = Stack()
    for x in "ABC": s.push(x)
    print(f"  pushed A, B, C   ->  pop order: {[s.pop() for _ in range(3)]}")
    print()

    print("A QUEUE IS FIFO -- first in, first out")
    q = Queue()
    for x in "ABC": q.enqueue(x)
    print(f"  enqueued A, B, C ->  dequeue order: {[q.dequeue() for _ in range(3)]}")
    print()

    print("WHY TWO STACKS -- avoiding the O(n) shift")
    print(f"  {'n':>7s} {'list.pop(0) shifts':>20s} {'two-stack moves':>18s}")
    for n in (10, 100, 1000):
        q2 = Queue()
        for i in range(n): q2.enqueue(i)
        for _ in range(n): q2.dequeue()
        print(f"  {n:7d} {naive_dequeue_shifts(n):20,d} {q2.moves:18,d}")
    print("  -> each element moves between stacks at most ONCE, so n")
    print("     dequeues cost n moves: amortised O(1) versus O(n^2).")
    print()

    print("BRACKET MATCHING -- why a stack is the right shape")
    for text in ["([]{})", "(]", "((())", "", "a(b[c]d)e"]:
        print(f"  {text!r:12s} balanced: {balanced(text)}")
    print("  -> brackets must close in REVERSE order of opening, which is")
    print("     exactly LIFO. The data structure encodes the rule.")
    print()

    print("WHERE EACH ONE SHOWS UP")
    print("  stack : function calls, undo, DFS, expression evaluation,")
    print("          backtracking -- anything that must unwind")
    print("  queue : BFS, job scheduling, request buffering, print spooling")
    print("          -- anything that must be fair to arrival order")

    assert balanced("([]{})") and not balanced("(]") and not balanced("((())")
    assert balanced("") and balanced("a(b[c]d)e")
    s2 = Stack(); s2.push(1)
    assert s2.pop() == 1
    try: s2.pop(); raise SystemExit("expected IndexError")
    except IndexError: pass
    q3 = Queue()
    for i in range(5): q3.enqueue(i)
    assert [q3.dequeue() for _ in range(5)] == [0, 1, 2, 3, 4]
    assert q3.moves == 5, "each element should move exactly once"
    print()
    print("stacks_queues_lab: passed")
```

Expected output:

```
A STACK IS LIFO -- last in, first out
  pushed A, B, C   ->  pop order: ['C', 'B', 'A']

A QUEUE IS FIFO -- first in, first out
  enqueued A, B, C ->  dequeue order: ['A', 'B', 'C']

WHY TWO STACKS -- avoiding the O(n) shift
        n   list.pop(0) shifts    two-stack moves
       10                   45                 10
      100                4,950                100
     1000              499,500              1,000
  -> each element moves between stacks at most ONCE, so n
     dequeues cost n moves: amortised O(1) versus O(n^2).

BRACKET MATCHING -- why a stack is the right shape
  '([]{})'     balanced: True
  '(]'         balanced: False
  '((())'      balanced: False
  ''           balanced: True
  'a(b[c]d)e'  balanced: True
  -> brackets must close in REVERSE order of opening, which is
     exactly LIFO. The data structure encodes the rule.

WHERE EACH ONE SHOWS UP
  stack : function calls, undo, DFS, expression evaluation,
          backtracking -- anything that must unwind
  queue : BFS, job scheduling, request buffering, print spooling
          -- anything that must be fair to arrival order

stacks_queues_lab: passed
```

## 8. Check Your Understanding (University Self-Assessment)

1. **Question**: What is the difference between LIFO and FIFO? Give one real-world application for each.
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>LIFO</b> (Last-In, First-Out) processes the newest element first (e.g., Undo history <code>Ctrl+Z</code>). <b>FIFO</b> (First-In, First-Out) processes the oldest element first (e.g., Printer queue, supermarket checkout line).</details>

2. **Question**: Why is `list.pop(0)` slow in Python, and what structure should be used instead?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <code>list.pop(0)</code> removes the element at index 0, forcing Python to shift all remaining elements left by 1 position in memory (an <b>O(n)</b> operation). Use <code>collections.deque.popleft()</code> instead, which runs in <b>O(1)</b> time.</details>

3. **Question**: Which data structure is used to implement Depth-First Search (DFS), and which is used for Breadth-First Search (BFS)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> <b>DFS</b> uses a <b>Stack (LIFO)</b> (or recursion call stack). <b>BFS</b> uses a <b>Queue (FIFO)</b>.</details>

---

## Practice - independent task

Implement a **min-stack**: a stack that also reports its minimum in O(1).

- `push`, `pop`, `peek` and `min` must **all** be O(1). No scanning.
- The obvious approach - keeping a single `min` variable - breaks on `pop`. Discover this: push 3, push 1, pop, then ask for the minimum.
- Fix it. The standard solution keeps a second stack of minima.
- Then optimise: only push to the auxiliary stack when the new value is less than or equal to the current minimum. **Why is the "or equal" necessary?**
- Test against a reference that recomputes the minimum by scanning.

**Done when:** all four operations are O(1), your min-stack agrees with the scanning reference over 500 random operations, and you can explain the "or equal".

<details><summary>Hint - open only after an attempt</summary>
If you only push when strictly less than the current minimum, duplicate minima break it: push 1, push 1, pop. The auxiliary stack recorded 1 once, popping removes it, and the minimum is now wrong even though a 1 is still present.<br>
Pushing on <strong>less than or equal</strong> records each occurrence, so each pop removes exactly one. This is the same off-by-one-duplicate class of bug as forgetting that a multiset is not a set.
</details>

## Before moving on

You are done with this module when you can, closed-book:

- [ ] State LIFO and FIFO and give a real use of each.
- [ ] Explain why removing from the front of an array-backed list is O(n).
- [ ] Explain the two-stack queue and why each element moves at most once.
- [ ] Explain why bracket matching needs a stack specifically.

**Recap:** A stack allows access only at one end (LIFO) and a queue only at opposite ends (FIFO). That single restriction is what makes each useful: brackets must close in reverse order of opening, which is precisely LIFO, while fair processing of arrivals is precisely FIFO. Implementing a queue over a plain array makes dequeue O(n) because everything shifts; two stacks avoid that by moving each element at most once, giving amortised O(1). Stacks drive DFS, function calls and undo; queues drive BFS and scheduling.

**Next:** [[08-heaps|Heaps]] - a third access restriction - not first or last, but smallest.

## Related Modules
- [[01-arrays|Arrays]] — The memory structure backing array-based stacks
- [[04-linked-lists|Linked Lists]] — Node structure backing `collections.deque`
- [[02-dfs|DFS]] & [[03-bfs|BFS]] — Traversals powered by Stacks and Queues
