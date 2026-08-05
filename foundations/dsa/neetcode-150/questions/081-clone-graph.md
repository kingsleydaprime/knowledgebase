# Clone Graph

**LeetCode 133** · Graphs · concepts: [[06-graphs|graphs]], [[03-hash-maps|hash-maps]]

## Problem

Deep-copy a connected undirected graph given a reference to one node.

## Approach — DFS/BFS with an old→new map (optimal)

The challenge mirrors [[039-copy-list-with-random-pointer|Copy List with Random Pointer]]: neighbors may not be cloned yet, and there are cycles. A hash map `original → clone` both (a) avoids infinite loops on cycles and (b) lets you wire neighbors to the right clones.

```python
def cloneGraph(node):
    if not node:
        return None
    clones = {}                            # original -> clone
    def dfs(n):
        if n in clones:
            return clones[n]               # already cloned -> reuse (handles cycles)
        copy = Node(n.val)
        clones[n] = copy                   # record BEFORE recursing into neighbors
        for nei in n.neighbors:
            copy.neighbors.append(dfs(nei))
        return copy
    return dfs(node)
```

**Time O(V + E), space O(V).**

## Why record the clone before recursing

Inserting `clones[n] = copy` **before** visiting neighbors is essential: in a cycle, a neighbor will recurse back to `n`, and the map must already hold `n`'s clone to return it instead of looping forever. This "memoize on entry" is the general fix for traversing cyclic structures.

## Key insight

**Cloning any linked/graph structure → traverse with an `original → copy` map that doubles as the visited set.** The map serves triple duty: dedupe, cycle-break, and neighbor-translation. Same technique as copying a linked list with random pointers.

## Related
- concepts: [[06-graphs|graphs]], [[03-hash-maps|hash-maps]], [[02-dfs|dfs]]
- relative: [[039-copy-list-with-random-pointer|Copy List with Random Pointer]]
- prev: [[080-number-of-islands|Number of Islands]] · next: [[082-max-area-of-island|Max Area of Island]]
