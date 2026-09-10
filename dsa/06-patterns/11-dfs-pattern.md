# Pattern: DFS as a Problem-Solving Pattern

**[Intermediate]** — A university-level introduction to the DFS pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand DFS traversal. See [[02-dfs|dfs]] if needed.
- You should understand recursion. See [[languages/06-python/04-functions-and-scope|Python functions and scope]] if needed.

**What you will be able to do after this lesson:**

1. Define the DFS problem-solving pattern and explain when to reach for it.
2. Implement DFS for exploring all paths/branches of a tree/graph.
3. Apply the pattern to related problems like topological sort and cycle detection.
4. Explain the difference between DFS and backtracking.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're exploring a maze. You could walk down each path until you hit a dead end, then backtrack and try another path. This is exactly what DFS does: explore as far as possible along each branch before backtracking.

The mechanics — recursive/iterative, `visited` sets, complexity — are covered in [[02-dfs|dfs]]. This note is about the shape of problem where DFS is the right tool: **anything that asks you to explore every path or branch of a tree/graph**, not just find one answer and stop.

---

## 2. Definitions and terminology

| Term                 | Plain-English definition                                                             | Example / analogy                                                 |
| -------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| **DFS**              | Depth-first search: explore as far as possible along each branch before backtracking | Exploring a maze by going as deep as possible before backtracking |
| **Backtracking**     | Undo a choice before trying the next option                                          | Reversing steps at a maze dead-end                                |
| **Topological sort** | Ordering tasks so that each task comes after all its dependencies                    | Scheduling courses with prerequisites                             |
| **Cycle detection**  | Finding a loop in a graph                                                            | Finding if a dependency graph has circular dependencies           |

---

## 3. How it works — step by step

### When to reach for DFS

- **"Find all paths from root to leaves"** — you need to explore every branch, so preorder-style DFS that builds up a path as it descends is a direct fit (see [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]]).
- **"Clone a graph"** — you need to visit every node and edge exactly once, which is exactly what DFS with a `visited` map guarantees.
- **"Order tasks with dependencies"** (topological sort) — DFS naturally produces this: finish exploring everything a node depends on before the node itself is considered "done," so appending nodes to a result list as they _finish_ (postorder-style) gives a valid ordering.

### Example — all root-to-leaf paths

```python
def path_sum_ii(root, target):
    result = []
    def dfs(node, remaining, path):
        if node is None:
            return
        path.append(node.val)
        remaining -= node.val
        if node.left is None and node.right is None and remaining == 0:
            result.append(list(path))
        else:
            dfs(node.left, remaining, path)
            dfs(node.right, remaining, path)
        path.pop()                     # undo before returning to the parent call — see backtracking
    dfs(root, target, [])
    return result
```

That `path.pop()` at the end is the backtracking step — see [[14-backtracking|backtracking]] for when this "undo the choice before returning" mechanic becomes the main point of the algorithm instead of a side detail.

### Example — DFS for topological sort (dependency ordering)

```python
def find_order(num_courses, prerequisites):
    graph = {i: [] for i in range(num_courses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    visited, visiting, order = set(), set(), []

    def dfs(node):
        if node in visiting:
            return False            # cycle -> no valid ordering exists
        if node in visited:
            return True
        visiting.add(node)
        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False
        visiting.remove(node)
        visited.add(node)
        order.append(node)          # append on the way back up = postorder
        return True

    for course in range(num_courses):
        if course not in visited:
            if not dfs(course):
                return []
    return order[::-1]              # reverse postorder = valid topological order
```

Note the extra `visiting` set on top of `visited` — this is what catches a cycle (a node reachable from itself) rather than just avoiding redundant work.

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `dfs_pattern_lab.py` and run `python3 dfs_pattern_lab.py`. It uses only Python's standard library and creates no external files.

```python
def find_order(num_courses, prerequisites):
    """Find a valid course ordering using DFS topological sort."""
    graph = {i: [] for i in range(num_courses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    visited, visiting, order = set(), set(), []

    def dfs(node):
        if node in visiting:
            return False            # cycle -> no valid ordering exists
        if node in visited:
            return True
        visiting.add(node)
        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False
        visiting.remove(node)
        visited.add(node)
        order.append(node)          # append on the way back up = postorder
        return True

    for course in range(num_courses):
        if course not in visited:
            if not dfs(course):
                return []
    return order[::-1]              # reverse postorder = valid topological order


if __name__ == "__main__":
    # Test case 1: valid ordering exists
    num_courses1 = 4
    prerequisites1 = [[1, 0], [2, 0], [3, 1], [3, 2]]
    result1 = find_order(num_courses1, prerequisites1)
    print(f"Test 1 - valid ordering:")
    print(f"num_courses={num_courses1}, prerequisites={prerequisites1} -> order {result1}")
    # Valid orderings: [0, 1, 2, 3] or [0, 2, 1, 3]
    assert result1 in [[0, 1, 2, 3], [0, 2, 1, 3]], f"Expected valid ordering, got {result1}"

    # Test case 2: cycle exists (no valid ordering)
    num_courses2 = 2
    prerequisites2 = [[1, 0], [0, 1]]
    result2 = find_order(num_courses2, prerequisites2)
    print(f"\nTest 2 - cycle exists:")
    print(f"num_courses={num_courses2}, prerequisites={prerequisites2} -> order {result2}")
    assert result2 == [], f"Expected [], got {result2}"

    print("dfs_pattern_lab: passed")
```

Expected output:

```
Test 1 - valid ordering:
num_courses=4, prerequisites=[[1, 0], [2, 0], [3, 1], [3, 2]] -> order [0, 2, 1, 3]

Test 2 - cycle exists:
num_courses=2, prerequisites=[[1, 0], [0, 1]] -> order []
dfs_pattern_lab: passed
```

> [!NOTE]
> A topological order is **not unique**. Here `[0, 2, 1, 3]` and `[0, 1, 2, 3]` are both valid — 1 and 2 depend only on 0, so either may come first. Which one you get depends on the order DFS happens to visit neighbours in, so assert that the result is *a* valid ordering rather than one specific list.

---

## 5. Complexity

O(V + E), same as plain DFS.

---

## 6. Tradeoffs and limitations

- **DFS explores deeply before broadly.** If you need the shortest path, use BFS instead.
- **Recursion depth.** For very deep graphs, the recursive DFS may hit Python's recursion limit. Use an iterative DFS with an explicit stack instead.
- **Cycle detection requires extra bookkeeping.** The `visiting` set is needed to detect cycles in directed graphs.

---

## 7. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given a graph with edges `[[0,1], [1,2], [2,3]]`, trace through the DFS topological sort algorithm step by step.
2. **Question:** Why does the `visiting` set catch cycles?
3. **Question:** What's the difference between DFS and backtracking?

### Answers — after your attempt

1. Start at course 0, visit 1, visit 2, visit 3. Course 3 has no prerequisites, so append 3. Backtrack to 2, append 2. Backtrack to 1, append 1. Backtrack to 0, append 0. Reverse postorder: [0, 1, 2, 3].
2. The `visiting` set tracks nodes currently in the recursion stack. If we encounter a node that's already in `visiting`, it means we've found a back edge — a cycle.
3. DFS explores all paths/branches of a graph. Backtracking is a specific technique where you explore a choice, undo it, and try the next choice. Backtracking uses DFS as its underlying traversal mechanism, but adds the "undo" step.

---

## 8. Practice — independent task

**Task:** Implement a function `can_finish(num_courses, prerequisites)` that returns `True` if all courses can be finished (no cycle), `False` otherwise. Use the DFS pattern. Test it with the following cases:

- `num_courses = 2, prerequisites = [[1, 0]]` → expected `True`
- `num_courses = 2, prerequisites = [[1, 0], [0, 1]]` → expected `False`

**Done when:** your function returns the correct results for both test cases.

---

## Practice problems

**In the [[dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[047-maximum-depth-of-binary-tree|Maximum Depth of Binary Tree]] (LeetCode #104) — the smallest complete DFS.
2. [[048-diameter-of-binary-tree|Diameter of Binary Tree]] (LeetCode #543) — return one thing, track another — the pattern for "path through a node".
3. [[049-balanced-binary-tree|Balanced Binary Tree]] (LeetCode #110) — the $-1$ sentinel that avoids recomputing heights.
4. [[059-binary-tree-maximum-path-sum|Binary Tree Maximum Path Sum]] (LeetCode #124) — the hardest version of return-versus-track.
5. [[080-number-of-islands|Number of Islands]] (LeetCode #200) — DFS flood fill on a grid.
6. [[081-clone-graph|Clone Graph]] (LeetCode #133) — DFS with a visited map that doubles as the output.
7. [[087-course-schedule|Course Schedule]] (LeetCode #207) — DFS cycle detection with three colours.
8. [[083-pacific-atlantic-water-flow|Pacific Atlantic Water Flow]] (LeetCode #417) — DFS from the edges inward, twice, then intersect.
9. [[117-longest-increasing-path-in-a-matrix|Longest Increasing Path in a Matrix]] (LeetCode #329) — DFS plus memoisation — which is dynamic programming on a graph.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they exercise carrying state **down** the recursion rather than returning it up:

10. Path Sum (#112) — carrying state **down** instead of returning it up.
11. Path Sum II (#113) — the same, but collecting the paths themselves.
12. Sum Root to Leaf Numbers (#129) — accumulate a value along the path.
13. Number of Provinces (#547) — connected components on an adjacency matrix.
14. Minimum Time to Collect All Apples in a Tree (#1443) — post-order accumulation on a general tree.

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] Explain why graphs need a visited set and trees do not.
- [ ] Implement DFS both recursively and with an explicit stack.
- [ ] Detect a cycle in a directed graph independently.
- [ ] State the space complexity and when recursion depth becomes a real risk.

**Recap:** DFS explores as far as possible along each branch before backtracking. On a graph — unlike a tree — you must track visited nodes, or a cycle sends you round forever. The recursive form is the natural one and costs stack proportional to depth; an explicit stack avoids that ceiling.

**Next:** [[12-bfs-pattern|bfs-pattern]] — the same exploration with a queue instead of a stack, which changes the order enough to solve a different class of problem.

## 9. Related

- [[02-dfs|dfs]] — the underlying traversal algorithm
- [[14-backtracking|backtracking]] — DFS with an explicit "undo" step
- [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]] — tree-specific DFS
- [[01-algorithms|algorithms]] — where the O(V + E) framing comes from
- [[11-dfs-pattern|dfs-pattern]] — this note

---

## 10. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Dependency resolution:** Package managers resolving dependencies
- **Build systems:** Determining build order for projects with dependencies
- **Spreadsheet evaluation:** Evaluating cells in dependency order
- **Game AI:** Exploring game trees

The core idea — exploring as far as possible along each branch before backtracking — is a fundamental algorithmic technique that appears whenever you need to explore all paths or branches of a structure.
