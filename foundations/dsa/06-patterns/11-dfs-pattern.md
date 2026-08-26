# Pattern: DFS as a Problem-Solving Pattern

The mechanics — recursive/iterative, `visited` sets, complexity — are covered in [[02-dfs|dfs]]. This note is about the shape of problem where DFS is the right tool: **anything that asks you to explore every path or branch of a tree/graph**, not just find one answer and stop.

## When to reach for it

- "Find **all** paths from root to leaves" — you need to explore every branch, so preorder-style DFS that builds up a path as it descends is a direct fit (see [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]]).
- "Clone a graph" — you need to visit every node and edge exactly once, which is exactly what DFS with a `visited` map guarantees.
- "Order tasks with dependencies" (topological sort) — DFS naturally produces this: finish exploring everything a node depends on before the node itself is considered "done," so appending nodes to a result list as they *finish* (postorder-style) gives a valid ordering.

## Example — all root-to-leaf paths

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

## Example — DFS for topological sort (dependency ordering)

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

## Complexity

O(V + E), same as plain DFS.

## Practice problems

**In the [[foundations/dsa/neetcode-150/README|NeetCode 150]]** — written up here:

1. [[081-clone-graph|Clone Graph]] (LeetCode #133)
2. [[087-course-schedule|Course Schedule]] (LeetCode #207) — cycle detection; the yes/no version of the next one
3. [[088-course-schedule-ii|Course Schedule II]] (LeetCode #210) — topological sort
4. [[063-word-search-ii|Word Search II]] (LeetCode #212) — DFS with a [[09-tries|trie]] to prune; the hard end of this pattern

**Not in the NeetCode 150:**

5. Path Sum II (LeetCode #113)

## Related
- [[02-dfs|dfs]]
- [[14-backtracking|backtracking]]
- [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]]
