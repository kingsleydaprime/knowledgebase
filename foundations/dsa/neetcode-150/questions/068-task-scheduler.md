# Task Scheduler

**LeetCode 621** · Heap / Priority Queue · concept: [[08-heaps|heaps]]

## Problem

Given task labels and a cooldown `n` (the same task must be ≥ `n` intervals apart), return the **minimum** number of intervals (including idles) to finish all tasks.

```
tasks = ["A","A","A","B","B","B"], n = 2  ->  8   (A B _ A B _ A B)
```

## Approach — greedy: most-frequent-available first, via a heap

Each interval, run the **most frequent remaining** task ([[08-heaps|max-heap]] of counts). After running it, it's on cooldown, so park it in a queue with the time it becomes available; return it to the heap when its cooldown expires.

```python
import heapq
from collections import deque, Counter

def leastInterval(tasks, n):
    heap = [-c for c in Counter(tasks).values()]   # max-heap of counts
    heapq.heapify(heap)
    cooldown = deque()                              # (available_time, -count)
    time = 0
    while heap or cooldown:
        time += 1
        if heap:
            cnt = heapq.heappop(heap) + 1           # run one (count was negative)
            if cnt != 0:
                cooldown.append((time + n, cnt))    # becomes available later
        if cooldown and cooldown[0][0] == time:
            heapq.heappush(heap, cooldown.popleft()[1])
    return time
```

**Time O(total tasks · log(unique)), space O(unique).**

## Why greedy-by-frequency is optimal

The bottleneck is the **most frequent** task — its copies force the widest spacing, so scheduling it as early and often as its cooldown allows minimizes idle time. Filling gaps with the *next* most frequent tasks keeps the machine busy. (There's a closed-form: `(maxCount - 1) * (n + 1) + (# tasks tied for maxCount)`, but the heap simulation is the intuitive derivation.)

## Key insight

**Greedy scheduling → always run the highest-count available job (max-heap) + a cooldown queue.** The heap surfaces the current bottleneck; the queue enforces the timing constraint. This heap+queue pairing generalizes to rate-limited/cooldown scheduling.

## Related
- concept: [[08-heaps|heaps]], [[10-greedy-algorithms|greedy]]
- prev: [[067-kth-largest-element-in-an-array|Kth Largest in an Array]] · next: [[069-design-twitter|Design Twitter]]
