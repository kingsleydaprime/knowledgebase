# Pattern: Matrix Traversal

A 2D grid is an implicit [[06-graphs|graph]] — each cell is a node, and each cell is connected to its (usually 4, sometimes 8) neighbors. Once you see it that way, [[02-dfs|dfs]] and [[03-bfs|bfs]] apply directly; there's no new algorithm here, just a different way of expressing "neighbors."

## When to use it

Problems on a grid involving connectivity or spreading: flood fill, counting connected regions ("islands"), or anything where a cell's fate depends on which region it belongs to.

## How it works

Instead of an adjacency list, neighbors are computed from `(row, col)` using direction offsets:

```python
directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]   # right, left, down, up

def flood_fill(image, sr, sc, new_color):
    old_color = image[sr][sc]
    if old_color == new_color:
        return image
    rows, cols = len(image), len(image[0])

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols):
            return
        if image[r][c] != old_color:
            return
        image[r][c] = new_color
        for dr, dc in directions:
            dfs(r + dr, c + dc)

    dfs(sr, sc)
    return image
```

```
image:            starting at (1,1), old_color=1, new_color=2:
0 0 0 0 0                            0 0 0 0 0
0 0 1 0 0         flood fill  ->     0 0 2 0 0
0 1 1 1 0                            0 2 2 2 0
0 0 1 0 0                            0 0 2 0 0
```

The **bounds check** (`0 <= r < rows and 0 <= c < cols`) is the one thing this pattern adds on top of plain graph DFS/BFS — there's no explicit neighbor list to bound the search, so the traversal has to check for the grid's edges itself. Marking a cell visited (here, by overwriting its value) still serves the same purpose it does in any graph traversal — avoiding revisiting and infinite loops.

## Counting connected regions ("Number of Islands")

Same traversal, but instead of one flood fill from a given start, loop over every cell and start a **new** DFS/BFS from any unvisited land cell — each one you start from is a new island, and the traversal marks everything connected to it as visited so it isn't counted twice.

```python
def num_islands(grid):
    rows, cols = len(grid), len(grid[0])
    visited = set()

    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols): return
        if (r, c) in visited or grid[r][c] == "0": return
        visited.add((r, c))
        for dr, dc in directions:
            dfs(r + dr, c + dc)

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                dfs(r, c)
                count += 1
    return count
```

This "loop over every node, start a fresh traversal from any unvisited one" structure is exactly the disconnected-graph handling described in [[06-graphs|graphs]] — a grid is just a graph that happens to have a lot of disconnected components (the separate islands).

## Complexity

O(rows × cols) — each cell is visited a constant number of times regardless of grid shape.

## Practice problems

**In the [[foundations/dsa/neetcode-150/README|NeetCode 150]]** — written up here:

1. [[080-number-of-islands|Number of Islands]] (LeetCode #200)
2. [[082-max-area-of-island|Max Area of Island]] (LeetCode #695) — the same flood fill, returning a size instead of a count
3. [[084-surrounded-regions|Surrounded Regions]] (LeetCode #130) — the inversion trick: flood inward from the border rather than outward from the interior
4. [[083-pacific-atlantic-water-flow|Pacific Atlantic Water Flow]] (LeetCode #417) — two traversals from opposite edges, intersected

**Not in the NeetCode 150:**

5. Flood Fill (LeetCode #733) — the pattern with nothing built on top of it; start here if the visited-set bookkeeping isn't automatic yet

## Related
- [[02-dfs|dfs]]
- [[12-bfs-pattern|bfs-pattern]]
- [[06-graphs|graphs]]
