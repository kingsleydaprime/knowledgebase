# Module: Leader Algorithm & Boyer-Moore Voting (Majority Element)

Welcome to the **Leader Algorithm** module. The Leader (or **Majority Element**) problem asks: given a sequence, find the single value that appears in **more than half** of the positions—or determine that no such element exists.

This problem is a masterclass in progressive algorithmic thinking. We'll walk through three genuinely different solutions, each teaching a distinct idea rather than being a minor tweak of the last.

---

## 1. Real-World Motivation & Physical Metaphors

Imagine a **National Election with Proportional Voting**:

```
Votes Cast:  [ A, B, A, A, C, A, B, A, A ]
                                         ↑
                          A appears 6 out of 9 times (> 50%!)
                          → A is the WINNER (the Leader)
```

### Real-World Applications:
1. **Distributed Systems Consensus**: In fault-tolerant systems like **Apache Raft**, servers identify a "leader" node that receives votes from the majority of the cluster.
2. **Data Stream Majority Detection**: Finding the most common network packet type in a high-throughput data stream without buffering all packets.
3. **Sensor Fusion**: Identifying the "consensus" sensor reading among multiple sensors where the majority is expected to agree.

> [!KEY-INSIGHT]
> A sequence can have **at most one leader**. If two values each appeared more than half the time, their combined count would exceed 100% of the array length—impossible!

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Analogy |
| :--- | :--- | :--- |
| **Leader / Majority Element** | A value appearing **strictly more than $\lfloor N/2 \rfloor$** times in the sequence. | An election candidate winning over 50% of votes. |
| **Majority Threshold** | The count that must be exceeded: $\lfloor N/2 \rfloor$. | The 50% vote threshold. |
| **Boyer-Moore Cancellation** | Pairing opposing values and canceling them out; the survivor is the candidate. | In a voting contest, matching each "Against" vote with a "For" vote and discarding both. |

---

## 3. Technical Deep Dive: Three Solutions (Naive → Optimal)

### Approach 1: Brute Force ($O(n^2)$) — Check Every Candidate

For every candidate value in the array, scan the entire array to count its occurrences:

```python
def leader_brute_force(A: list) -> int:
    """O(n²) brute force: re-scans array for every candidate element."""
    n = len(A)
    for candidate in A:
        count = sum(1 for x in A if x == candidate)
        if count > n // 2:
            return candidate
    return -1  # No leader exists
```

**Why it's slow**: For each of the $N$ candidates, we scan all $N$ elements → $O(N^2)$ total.

---

### Approach 2: Sort First ($O(n \log n)$) — The Middle Index Trick

After sorting, all identical values become adjacent. If a leader exists, it **must** occupy the middle index `A[n // 2]` of the sorted array, because there are not enough other elements to push it out:

```python
def leader_sort(A: list) -> int:
    """O(n log n): Sort array, check the mandatory middle position."""
    n = len(A)
    sorted_A = sorted(A)  # Avoids mutating original input
    candidate = sorted_A[n // 2]
    count = sum(1 for x in A if x == candidate)
    return candidate if count > n // 2 else -1
```

**Why this works**: A leader occupying more than $N/2$ positions must be present at the middle index when values are packed together by sorting.

---

### Approach 3: Boyer-Moore Voting ($O(n)$, $O(1)$ Space) — The Elegant Solution

> [!KEY-INSIGHT]
> **The Core Insight**: If you remove any pair of two *different* values from the sequence, the leader remains the leader of what's left. A matched pair contains at most one leader occurrence—so the leader's proportion only grows.

Simulate the "remove mismatched pairs" process using just a running count:

```python
def leader_boyer_moore(A: list) -> int:
    """O(n) time, O(1) space: Boyer-Moore Voting Algorithm."""
    # Phase 1: Find the candidate via pairwise cancellation
    candidate = None
    count = 0
    
    for value in A:
        if count == 0:
            candidate = value  # Start fresh with this value
            count = 1
        elif value == candidate:
            count += 1         # Same value: reinforce the candidate
        else:
            count -= 1         # Different value: cancel one occurrence
            
    # Phase 2: Verify the candidate is a true majority (MANDATORY!)
    # Boyer-Moore finds a candidate even when NO leader exists!
    if candidate is None:
        return -1
        
    actual_count = sum(1 for x in A if x == candidate)
    return candidate if actual_count > len(A) // 2 else -1
```

**Step-by-step visualization** on `[A, B, A, A, C, A, B, A, A]`:
```
Value:     A   B   A   A   C   A   B   A   A
Count:     1   0   1   2   1   2   1   2   3
Candidate: A   _   A   A   A   A   A   A   A

→ Candidate: A (count=3), confirmed: A appears 6/9 times > 4. Leader = A ✓
```

---

## 4. Algorithm Comparison

| Approach | Time | Space | Key Idea |
| :--- | :--- | :--- | :--- |
| **Brute Force** | $O(n^2)$ | $O(1)$ | Re-scan array for every candidate. |
| **Sort + Check Middle** | $O(n \log n)$ | $O(1)$ | Leader must land at sorted midpoint. |
| **Boyer-Moore Voting** | **$O(n)$** | **$O(1)$** | Pairwise cancellation; survivor = candidate. |

---

## 5. Common Pitfalls & Traps

1. **Skipping the Verification Pass**: Boyer-Moore **always produces a candidate** even when no majority element exists! The second pass confirming `count > n // 2` is **not optional**.
2. **Confusing Leader with Mode**: A "leader" requires *strict majority* (> 50%). The most common element ("mode") might appear only 30% of the time.
3. **Integer vs. General Values**: Boyer-Moore works for any comparable type, not just integers.

---

## 6. Check Your Understanding (University Self-Assessment)

1. **Question**: Why must a leader always appear at index `A[n // 2]` in the sorted version of the array?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A leader occupies more than <code>N/2</code> positions. Even if all remaining elements are packed to the left, there aren't enough of them to push the leader past the midpoint. The sorted midpoint <b>must</b> contain a leader occurrence.</details>

2. **Question**: Why is the second verification pass in Boyer-Moore required?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The cancellation process reduces the problem iteratively, always producing a survivor. But if NO majority element exists, the survivor is just whatever element happened to win the cancellation game by chance. The verification pass checks whether the survivor actually meets the <code>> N/2</code> threshold.</details>

3. **Question**: What is the minimum number of times a leader must appear in an array of length 10?
   - <details><summary>Click for Answer</summary><b>Answer:</b> At least <b>6 times</b> (strictly more than <code>10 // 2 = 5</code>).</details>

---

## Related Modules
- [[10-greedy-algorithms|Greedy Algorithms]] — Boyer-Moore is a greedy approach
- [[04-sorting/index|Sorting Algorithms]] — $O(n \log n)$ sort-based solution
