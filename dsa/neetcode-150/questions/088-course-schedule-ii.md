# Course Schedule II

**LeetCode 210** · Graphs · concept: [[11-topological-sort|topological-sort]]

## Problem

Same setup as [[087-course-schedule|Course Schedule]], but **return a valid ordering** of courses (any one), or an empty list if impossible.

## Approach — Kahn's algorithm, emit the order

Identical in-degree BFS, but now **record each course as you complete it**. The sequence of removals *is* a topological order. If a cycle blocks some courses, the recorded order is shorter than `numCourses` → return `[]`.

```python
from collections import deque

def findOrder(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses
    for a, b in prerequisites:             # b -> a
        graph[b].append(a)
        indegree[a] += 1

    queue = deque(c for c in range(numCourses) if indegree[c] == 0)
    order = []
    while queue:
        course = queue.popleft()
        order.append(course)               # the topological order, in emission sequence
        for nxt in graph[course]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return order if len(order) == numCourses else []   # incomplete => cycle
```

**Time O(V + E), space O(V + E).**

## Feasibility vs. the order itself

The only change from Course Schedule is capturing `order`. A node is emitted exactly when its last prerequisite is done, so the emission order always respects dependencies. The same length check doubles as the cycle test.

## Key insight

**A topological sort's *by-product* is the ordering** — Kahn's emits nodes in dependency-respecting order for free. Any "sequence things under prerequisite constraints" problem (build order, task scheduling) is this exact algorithm.

## Related
- concept: [[11-topological-sort|topological-sort]]
- builds on: [[087-course-schedule|Course Schedule]]
- prev: [[087-course-schedule|Course Schedule]] · next: [[089-redundant-connection|Redundant Connection]]
