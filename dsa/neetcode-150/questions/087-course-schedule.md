# Course Schedule

**LeetCode 207** · Graphs · concept: [[11-topological-sort|topological-sort]]

## Problem

Given `numCourses` and `prerequisites` (pairs `[a, b]` meaning "b before a"), return whether you can finish all courses.

## The reframing — cycle detection on a DAG

"Can all courses be completed?" ⇔ "does the prerequisite graph have a **valid ordering**?" ⇔ "is it **acyclic**?" A cycle (`A needs B needs A`) makes completion impossible. So this is [[11-topological-sort|topological sort]] feasibility.

## Approach — Kahn's algorithm (BFS on in-degrees)

Repeatedly take a course with **no unmet prerequisites** (in-degree 0), "complete" it (decrementing its dependents' in-degrees), and continue. If you complete all courses, no cycle exists.

```python
from collections import deque

def canFinish(numCourses, prerequisites):
    graph = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses
    for a, b in prerequisites:             # b -> a
        graph[b].append(a)
        indegree[a] += 1

    queue = deque(c for c in range(numCourses) if indegree[c] == 0)
    completed = 0
    while queue:
        course = queue.popleft()
        completed += 1
        for nxt in graph[course]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return completed == numCourses         # all done <=> acyclic
```

**Time O(V + E), space O(V + E).**

## Why the count detects a cycle

Courses in a cycle never reach in-degree 0 (each waits on another), so they're never dequeued and `completed < numCourses`. A DFS three-color variant works too, but Kahn's is iterative and reads naturally as "keep taking whatever's ready."

## Key insight

**"Can everything be ordered under dependencies?" = "is the dependency graph acyclic?" → topological sort.** Half of graph problems are secretly cycle detection; recognizing the topological-sort framing behind a scheduling story is the move.

## Related
- concept: [[11-topological-sort|topological-sort]], [[06-graphs|graphs]]
- prev: [[086-walls-and-gates|Walls and Gates]] · next: [[088-course-schedule-ii|Course Schedule II]]
