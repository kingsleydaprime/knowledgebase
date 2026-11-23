---
id: 7e9c10aa-339b-45be-8012-a721555bb7bb
---

# Pattern: DFS as a Problem-Solving Pattern

DFS (depth-first search) as a pattern is solving problems by following one path as far as it goes, then backing up to try the next. Many problems about graphs, grids and choices are really this one idea. It is how you would find your way out of a maze by trying one corridor all the way before turning back.

## Before you start
<!-- bite: ec7d0aa8-a10c-4cbd-a65c-7f08238557ab -->

- You should understand DFS traversal. See [[01-depth-first-search|dfs]] if needed.
- You should understand recursion. See [[languages/06-python/04-functions-and-scope|Python functions and scope]] if needed.

**What you will be able to do after this lesson:**

1. Define the DFS problem-solving pattern and explain when to reach for it.
2. Implement DFS for exploring all paths/branches of a tree/graph.
3. Apply the pattern to related problems like topological sort and cycle detection.
4. Explain the difference between DFS and backtracking.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)
<!-- bite: dad14e8b-8cc9-4ea7-968e-4d11d079d595 -->

Imagine you're exploring a maze. You could walk down each path until you hit a dead end, then backtrack and try another path. This is exactly what DFS does: explore as far as possible along each branch before backtracking.

The mechanics — recursive/iterative, `visited` sets, complexity — are covered in [[01-depth-first-search|dfs]]. This note is about the shape of problem where DFS is the right tool: **anything that asks you to explore every path or branch of a tree/graph**, not just find one answer and stop.

---

## 2. Definitions and terminology
<!-- bite: 6d42ea33-cd37-414e-94b5-12809ca2d1d2 -->

| Term                 | Plain-English definition                                                             | Example / analogy                                                 |
| -------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| **DFS**              | Depth-first search: explore as far as possible along each branch before backtracking | Exploring a maze by going as deep as possible before backtracking |
| **Backtracking**     | Undo a choice before trying the next option                                          | Reversing steps at a maze dead-end                                |
| **Topological sort** | Ordering tasks so that each task comes after all its dependencies                    | Scheduling courses with prerequisites                             |
| **Cycle detection**  | Finding a loop in a graph                                                            | Finding if a dependency graph has circular dependencies           |

---

## 3. How it works — step by step
<!-- bite: 7adbb4a9-779a-43f9-968b-79afff606644 -->

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
<!-- bite: a396d631-c963-4a97-94ea-d4012fcf2c9b -->

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

```text
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
<!-- bite: f8022904-59c3-4b46-b9fa-31e317812458 -->

O(V + E), same as plain DFS.

---

## 6. Tradeoffs and limitations
<!-- bite: 64180525-a9cb-4a57-a0b0-4c12a525b01b -->

- **DFS explores deeply before broadly.** If you need the shortest path, use BFS instead.
- **Recursion depth.** For very deep graphs, the recursive DFS may hit Python's recursion limit. Use an iterative DFS with an explicit stack instead.
- **Cycle detection requires extra bookkeeping.** The `visiting` set is needed to detect cycles in directed graphs.

---

## Check your understanding
<!-- bite: 78f230f4-4336-4bd9-9b45-986119c67b47 -->

Try each one before you open the answer.

1. <!-- q: mcq id="e60f3de9" -->
   In DFS topological sort, nodes are added to `order` when they finish. What do you return?

   - [ ] order as it is
   - [x] order reversed
   - [ ] order sorted
   - [ ] Only the first node of order

   <details><summary>Answer</summary>

   Reversed. A node finishes after everything that depends on it, so reversing the finish order puts each node before its dependants.

   </details>

2. <!-- q: mcq id="f8aa830a" -->
   Topological sort keeps a `visiting` set as well as `visited`. What does `visiting` catch?

   - [ ] Nodes with no edges
   - [x] A cycle: reaching a node that is still on the current DFS path
   - [ ] Nodes visited twice from different starts
   - [ ] The shortest path

   <details><summary>Answer</summary>

   A cycle. `visiting` holds the nodes on the current path; meeting one again means you have looped back to yourself, so no valid order exists.

   </details>

3. <!-- q: mcq id="30e88f17" -->
   You need the fewest steps from A to B in an unweighted graph. Is DFS the right pattern?

   - [ ] Yes, DFS always finds the shortest path first
   - [x] No, use BFS: DFS may find a long path first
   - [ ] Yes, but only on trees
   - [ ] No, use backtracking

   <details><summary>Answer</summary>

   No. DFS dives deep and can reach B by a long route first. BFS explores by distance, so its first arrival is the shortest.

   </details>

4. <!-- q: mcq id="62b6947d" -->
   In path_sum_ii, what job does `path.pop()` at the end of each call do?

   - [ ] Removes the leaf from the tree
   - [x] Undoes adding this node, so the shared path is right for the parent's next branch
   - [ ] Stops the search early
   - [ ] Records a finished path

   <details><summary>Answer</summary>

   It undoes the choice: the backtracking step. One shared list is reused across branches, so each call removes what it added before returning.

   </details>

5. <!-- q: open id="dd3d6c44" -->
   Courses 1 and 2 both need only course 0, and course 3 needs 1 and 2. Why are [0, 1, 2, 3] and [0, 2, 1, 3] both correct orders?

   <details><summary>Answer</summary>

   A topological order only has to put each course after its prerequisites. 1 and 2 don't depend on each other, so either can come first. Which one DFS gives depends on the order it visits neighbours, so tests should check that the order is valid, not that it matches one list.

   </details>

## Check your understanding: worked problems
<!-- bite: 0e1a3239-7746-41d4-a137-36cde8a1e5f4 -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="2ef3200c" answers="1;3;0;2;4" -->
   Fill in the gaps. There are 5 courses, numbered 0 to 4. Each pair [a, b] means course a needs course b first:

   [[3, 1], [0, 3], [2, 0], [2, 3], [4, 2]]

   The only valid order is ___, ___, ___, ___, ___.

   <details><summary>Answer</summary>

   1, 3, 0, 2, 4. 1 needs nothing; 3 needs 1; 0 needs 3; 2 needs 0 and 3; 4 needs 2.

   </details>

2. <!-- q: gap id="1a81246b" answers="4;2;0;3;1" -->
   Fill in the gaps. 5 courses; [a, b] means a needs b, and each edge is stored as b → a:

   [[3, 1], [0, 3], [2, 0], [2, 3], [4, 2]]

   DFS starts at course 0, follows edges in the order listed, and appends a course to `order` when it finishes. Before reversing, `order` is [___, ___, ___, ___, ___].

   <details><summary>Answer</summary>

   [4, 2, 0, 3, 1]. From 0 it goes to 2, then 4; 4 finishes first, then 2, then 0. The loop then starts at 1, which goes to 3 (its other neighbours are done), so 3 finishes, then 1. Reversed, this gives 1, 3, 0, 2, 4.

   </details>

3. <!-- q: mcq id="0b7f2bff" -->
   4 courses; [a, b] means a needs b: [[1, 0], [2, 1], [0, 2], [3, 0]]. What does find_order return?

   - [ ] [0, 1, 2, 3]
   - [ ] [3, 0, 1, 2]
   - [x] [] because there is a cycle
   - [ ] [2, 1, 0, 3]

   <details><summary>Answer</summary>

   []. 0 → 1 → 2 → 0 is a loop: DFS reaches 0 again while it is still in `visiting`, so no order exists.

   </details>

4. <!-- q: exact id="d4d8c49c" answer="2" -->
   How many root-to-leaf paths in this tree (root 3) add up to 8?

   | Node | Left child | Right child |
   | --- | --- | --- |
   | 3 (root) | 1 | 2 |
   | 1 | 4 | 2 |
   | 2 (right child of root) | 1 | 3 |
   | 1 (child of that 2) | 3 | none |
   | all others | none | none |

   <details><summary>Answer</summary>

   2: 3 → 1 → 4 and 3 → 2 → 3. The other paths give 3 + 1 + 2 = 6 and 3 + 2 + 1 + 3 = 9.

   </details>

## 8. Practice — independent task
<!-- bite: 849c4630-17ea-489d-8712-3f4a412ac58a -->

**Task:** Implement a function `can_finish(num_courses, prerequisites)` that returns `True` if all courses can be finished (no cycle), `False` otherwise. Use the DFS pattern. Test it with the following cases:

- `num_courses = 2, prerequisites = [[1, 0]]` → expected `True`
- `num_courses = 2, prerequisites = [[1, 0], [0, 1]]` → expected `False`

**Done when:** your function returns the correct results for both test cases.

---

## Practice problems
<!-- bite: 954e9d21-bda3-453f-ba3e-ba92dcf0680d -->

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
<!-- bite: 67643364-60ab-4376-ac9c-a56eb107e94b -->

You are done with this pattern when you can, closed-book:

- [ ] Explain why graphs need a visited set and trees do not.
- [ ] Implement DFS both recursively and with an explicit stack.
- [ ] Detect a cycle in a directed graph independently.
- [ ] State the space complexity and when recursion depth becomes a real risk.

**Recap:** DFS explores as far as possible along each branch before backtracking. On a graph — unlike a tree — you must track visited nodes, or a cycle sends you round forever. The recursive form is the natural one and costs stack proportional to depth; an explicit stack avoids that ceiling.

**Next:** [[12-bfs-pattern|bfs-pattern]] — the same exploration with a queue instead of a stack, which changes the order enough to solve a different class of problem.

## 9. Related
<!-- bite: 440e213a-dab4-4d6d-bc70-f915286b4755 -->

- [[01-depth-first-search|dfs]] — the underlying traversal algorithm
- [[14-backtracking|backtracking]] — DFS with an explicit "undo" step
- [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]] — tree-specific DFS
- [[01-growth-and-asymptotic-notation|algorithms]] — where the O(V + E) framing comes from
- [[11-dfs-pattern|dfs-pattern]] — this note

---

## 10. Further reading
<!-- bite: f8e57f18-25e1-4d28-b029-fdaceecbd509 -->

The pattern appears in many contexts beyond LeetCode:

- **Dependency resolution:** Package managers resolving dependencies
- **Build systems:** Determining build order for projects with dependencies
- **Spreadsheet evaluation:** Evaluating cells in dependency order
- **Game AI:** Exploring game trees

The core idea — exploring as far as possible along each branch before backtracking — is a fundamental algorithmic technique that appears whenever you need to explore all paths or branches of a structure.

## About this lesson
<!-- bite: 62a9f420-5208-41c1-8d77-470f49cd4519 -->

**Level:** Intermediate. **Covers:** A university-level introduction to the DFS pattern: what it is, why it exists, how it works, and how to implement it independently.
