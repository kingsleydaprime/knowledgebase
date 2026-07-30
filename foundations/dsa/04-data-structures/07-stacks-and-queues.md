# Stacks and Queues

> Added after reviewing Codility's own course PDFs in `pdfs/` (Chapter 7, `5-Stacks.pdf`) — this data structure had no dedicated note in this vault at all, despite [[06-monotonic-stack|monotonic-stack]] in `patterns/` already assuming you know what a stack is.

Part of [[foundations/dsa/README|DSA fundamentals]]. Both structures below support the same two core operations — **push** (insert) and **pop** (remove) — the entire difference between them is *which end* each operation happens at.

---

## Stack — last in, first out (LIFO)

Both insertion and removal happen at the same end, the **top**. Picture a stack of plates: you can only take a plate off the top, and any new plate goes on top too — the last one you put down is the first one you'll pick back up.

```python
stack = [0] * N
size = 0

def push(x):
    global size
    stack[size] = x
    size += 1

def pop():
    global size
    size -= 1
    return stack[size]
```
Both operations are **O(1)** — no shifting of other elements required, since nothing but the top ever changes. Real code almost always reaches for a language's built-in dynamic array for this (Python's `list.append`/`list.pop`, exactly the interface above) rather than hand-rolling a fixed-size array — the fixed-size version above is what makes the O(1)/no-shifting behavior explicit to see.

**Where a stack actually shows up:** undo/redo history, matching balanced brackets/parentheses, tracking function call frames (the literal "call stack"), depth-first traversal (see [[foundations/dsa/05-algorithms/02-dfs|dfs]]), and the monotonic-stack pattern ([[foundations/dsa/06-patterns/06-monotonic-stack|monotonic-stack]]) for "next greater/smaller element" problems.

---

## Queue — first in, first out (FIFO)

Insertion happens at the **back** (tail), removal happens at the **front** (head) — a grocery-store line: new people join the back, and whoever's been waiting longest (the front) gets served next.

```python
queue = [0] * N
head, tail = 0, 0

def push(x):
    global tail
    tail = (tail + 1) % N
    queue[tail] = x

def pop():
    global head
    head = (head + 1) % N
    return queue[head]

def size():
    return (tail - head + N) % N

def empty():
    return head == tail
```
Also O(1) for push/pop — the `% N` (modulo) on both `head` and `tail` is what makes this work in a *fixed-size* array without ever shifting elements: once `tail` reaches the end of the array, it wraps back around to index 0 instead of needing to grow. This wraparound technique is called a **circular buffer** — worth recognizing the name, since it comes up anywhere a fixed-size FIFO buffer is needed (network packet buffers, audio buffers, producer/consumer queues), not just here.

**Where a queue actually shows up:** breadth-first traversal (see [[foundations/dsa/05-algorithms/03-bfs|bfs]] — BFS is *defined* by using a queue instead of a stack, that's the entire mechanical difference from DFS), task scheduling, rate limiting, any "process in the order things arrived" scenario.

---

## Worked example: minimum starting queue size

**Problem:** given a sequence of events where `0` = a person joins the back of a queue and `1` = the person at the front is served and leaves, find the minimum number of people who must *already* have been in line for the whole sequence to be valid (you can't serve someone from an empty queue).

```python
def min_starting_queue_size(events):
    size = result = 0
    for event in events:
        if event == 0:
            size += 1
        else:
            size -= 1
            result = max(result, -size)
    return result
```
The trick: simulate the queue's size as a running counter rather than an actual queue of people. Every time a "serve" event would drive the count negative, that negative amount is exactly how many people had to already be waiting to make that serve valid — track the most negative point reached across the whole sequence, and that's the answer. **O(n) time, O(1) space** — the win from not needing an actual queue/array to hold "people," just a single running integer.

---

## Related
- [[foundations/dsa/06-patterns/06-monotonic-stack|monotonic-stack]] — a stack used in a specific pattern, not just raw push/pop
- [[foundations/dsa/05-algorithms/02-dfs|dfs]] / [[foundations/dsa/05-algorithms/03-bfs|bfs]] — stack-driven vs. queue-driven traversal, the mechanical reason they explore in different orders
