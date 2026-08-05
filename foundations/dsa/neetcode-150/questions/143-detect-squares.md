# Detect Squares

**LeetCode 2013** · Math & Geometry · concepts: [[14-math-and-geometry|math-and-geometry]], [[03-hash-maps|hash-maps]]

## Problem

Design a structure with `add(point)` and `count(point)` — the number of axis-aligned **squares** with positive area that can be formed using the query point and three previously added points.

## Approach — count points, enumerate diagonal partners (optimal)

Keep a **count map** of points (duplicates allowed) plus a list of points. For a `count(qx, qy)` query, iterate stored points that could be the **diagonal** corner — those with `|px − qx| == |py − qy|` and `px != qx` (a real square). The other two corners are then determined: `(qx, py)` and `(px, qy)`. Multiply their counts.

```python
from collections import defaultdict

class DetectSquares:
    def __init__(self):
        self.count = defaultdict(int)      # (x, y) -> occurrences
        self.points = []

    def add(self, point):
        self.count[tuple(point)] += 1
        self.points.append(tuple(point))

    def count(self, point):
        qx, qy = point
        total = 0
        for px, py in self.points:
            if abs(px - qx) == abs(py - qy) and px != qx:   # valid diagonal corner
                total += self.count[(px, qy)] * self.count[(qx, py)]
        return total
```

**`add` O(1); `count` O(n), space O(n).**

## Geometry reduced to hashing

An axis-aligned square is fixed by one diagonal pair: pick the opposite corner `(px, py)`, and the other two corners `(qx, py)` and `(px, qy)` are forced. The count map gives their multiplicities in O(1), and multiplying counts handles duplicate points. So the "geometry" is really a hash-map lookup once you see which corners a diagonal determines.

## Key insight

**Counting geometric configurations → fix the defining points (here a diagonal), derive the rest, and multiply their hashed counts.** Detect Squares is a [[03-hash-maps|hashing]] problem wearing a geometry costume — the insight is which points *determine* a square.

## Related
- concepts: [[14-math-and-geometry|math-and-geometry]], [[03-hash-maps|hash-maps]]
- prev: [[142-multiply-strings|Multiply Strings]] — end of Math & Geometry
- next category: Bit Manipulation
