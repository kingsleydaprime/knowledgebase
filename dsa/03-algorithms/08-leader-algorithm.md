# Module: Leader Algorithm & Boyer-Moore Voting (Majority Element)

Welcome to the **Leader Algorithm** module. The Leader (or **Majority Element**) problem asks: given a sequence, find the single value that appears in **more than half** of the positions—or determine that no such element exists.

This problem is a masterclass in progressive algorithmic thinking. We'll walk through three genuinely different solutions, each teaching a distinct idea rather than being a minor tweak of the last.

---

## Before you start

- You can scan an array and maintain a running value — [[01-loops-and-what-they-cost|loops and what they cost]].
- You know what a hash map would cost here — [[03-hash-maps|hash maps]].

**After this lesson you will be able to:**

1. Implement **Boyer–Moore voting** in $O(n)$ time and $O(1)$ space.
2. Explain the cancellation argument that makes it work.
3. Say why the **verification pass is not optional**, and demonstrate what happens without it.
4. Generalise it to elements appearing more than $n/3$ times.

**Study route:** read 1–5, attempt the prediction in section 4, then run the lab. Block 3 shows the algorithm confidently returning a non-answer.

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

## Implementation — complete runnable example

**Runnable example:** save as `leader.py` in any empty directory and run `python3 leader.py`. Standard library only; writes no files.

```python
"""Boyer-Moore voting: the candidate, the proof idea, and the mandatory check."""
import random
from collections import Counter


def boyer_moore(xs):
    """Returns a CANDIDATE. It is only the majority if it survives verification."""
    candidate, count = None, 0
    for v in xs:
        if count == 0:
            candidate, count = v, 1
        elif v == candidate:
            count += 1
        else:
            count -= 1
    return candidate


def majority(xs):
    """The complete algorithm: candidate, then verify."""
    if not xs:
        return None
    c = boyer_moore(xs)
    return c if xs.count(c) > len(xs) // 2 else None


def majority_hashmap(xs):
    """The obvious O(n) time, O(n) space version, as an oracle."""
    if not xs:
        return None
    v, n = Counter(xs).most_common(1)[0]
    return v if n > len(xs) // 2 else None


def majority_n3(xs):
    """At most two elements can appear more than n/3 times."""
    c1 = c2 = None
    n1 = n2 = 0
    for v in xs:
        if v == c1:
            n1 += 1
        elif v == c2:
            n2 += 1
        elif n1 == 0:
            c1, n1 = v, 1
        elif n2 == 0:
            c2, n2 = v, 1
        else:
            n1 -= 1
            n2 -= 1
    return sorted(c for c in {c1, c2} if c is not None and xs.count(c) > len(xs) // 3)


def trace(xs):
    rows = []
    candidate, count = None, 0
    for v in xs:
        if count == 0:
            candidate, count = v, 1
            why = "count was 0, adopt"
        elif v == candidate:
            count += 1
            why = "matches, +1"
        else:
            count -= 1
            why = "differs, -1"
        rows.append((v, candidate, count, why))
    return rows


if __name__ == "__main__":
    print("Block 1 - the cancellation, step by step")
    xs = [2, 2, 1, 1, 1, 2, 2]
    print(f"  input {xs}  (2 appears 4 times of 7, so it IS the majority)")
    print("     saw   candidate   count   reason")
    for v, c, n, why in trace(xs):
        print(f"      {v}       {c}         {n}     {why}")
    assert majority(xs) == 2
    print("  the idea: pair each majority element with a different one and discard")
    print("  both. A true majority has more than half, so it cannot be exhausted -")
    print("  whatever survives the pairing must be it.")

    print()
    print("Block 2 - correctness against a hash-map oracle")
    rng = random.Random(20260910)
    for _ in range(2000):
        n = rng.randint(0, 30)
        pool = [rng.randint(0, 4) for _ in range(n)]
        if rng.random() < 0.5 and n:                      # half the time, force a majority
            v = rng.randint(0, 4)
            for i in range(n // 2 + 1):
                pool[i] = v
            rng.shuffle(pool)
        assert majority(pool) == majority_hashmap(pool), pool
    print("  2,000 random arrays: agrees with the hash-map version every time")

    print()
    print("Block 3 - WITHOUT the verification pass, it lies")
    no_majority = [1, 2, 3, 4, 5]
    cand = boyer_moore(no_majority)
    print(f"  input {no_majority} - no element appears more than {len(no_majority)//2} times")
    print(f"    raw candidate: {cand}   <- looks like an answer")
    print(f"    with verification: {majority(no_majority)}")
    assert cand is not None and majority(no_majority) is None
    print("  the voting phase ALWAYS returns something. It only promises that IF a")
    print("  majority exists, it is the candidate. It promises nothing otherwise.")
    print("  Skipping the count is the single most common way to get this wrong.")

    print()
    print("  more cases where the raw candidate is not a majority:")
    for arr in ([1, 2, 3], [1, 1, 2, 2], [7, 8, 8, 7, 9]):
        print(f"    {str(arr):16} candidate {boyer_moore(arr)}   majority {majority(arr)}")
    assert majority([1, 1, 2, 2]) is None

    print()
    print("Block 4 - space, compared")
    big = [rng.randint(0, 100) for _ in range(100000)]
    for i in range(60000):
        big[i] = 42
    rng.shuffle(big)
    print(f"  100,000 elements, 42 appears {big.count(42):,} times")
    print(f"    boyer-moore: {majority(big)}   extra space: 2 variables")
    print(f"    hash map:    {majority_hashmap(big)}   extra space: one entry per distinct value")
    assert majority(big) == majority_hashmap(big) == 42
    print(f"  the hash map would hold {len(set(big))} entries; voting holds 2.")
    print("  That is the whole point: O(1) space on a single pass, so it works on a")
    print("  stream you cannot store.")

    print()
    print("Block 5 - the n/3 generalisation")
    for arr in ([1, 1, 1, 3, 3, 2, 2, 2], [1, 2], [3, 3, 4], [1, 1, 2, 2, 3, 3]):
        got = majority_n3(arr)
        expect = sorted(v for v, c in Counter(arr).items() if c > len(arr) // 3)
        print(f"  {str(arr):26} > n/3: {str(got):12} expected {expect}")
        assert got == expect
    print("  at most 2 elements can exceed n/3, so 2 candidates and 2 counters suffice.")
    print("  In general, at most k-1 elements can exceed n/k - the same trick scales.")

    print()
    print("leader: passed")
```

Expected output:

```
Block 1 - the cancellation, step by step
  input [2, 2, 1, 1, 1, 2, 2]  (2 appears 4 times of 7, so it IS the majority)
     saw   candidate   count   reason
      2       2         1     count was 0, adopt
      2       2         2     matches, +1
      1       2         1     differs, -1
      1       2         0     differs, -1
      1       1         1     count was 0, adopt
      2       1         0     differs, -1
      2       2         1     count was 0, adopt
  the idea: pair each majority element with a different one and discard
  both. A true majority has more than half, so it cannot be exhausted -
  whatever survives the pairing must be it.

Block 2 - correctness against a hash-map oracle
  2,000 random arrays: agrees with the hash-map version every time

Block 3 - WITHOUT the verification pass, it lies
  input [1, 2, 3, 4, 5] - no element appears more than 2 times
    raw candidate: 5   <- looks like an answer
    with verification: None
  the voting phase ALWAYS returns something. It only promises that IF a
  majority exists, it is the candidate. It promises nothing otherwise.
  Skipping the count is the single most common way to get this wrong.

  more cases where the raw candidate is not a majority:
    [1, 2, 3]        candidate 3   majority None
    [1, 1, 2, 2]     candidate 1   majority None
    [7, 8, 8, 7, 9]  candidate 9   majority None

Block 4 - space, compared
  100,000 elements, 42 appears 60,393 times
    boyer-moore: 42   extra space: 2 variables
    hash map:    42   extra space: one entry per distinct value
  the hash map would hold 101 entries; voting holds 2.
  That is the whole point: O(1) space on a single pass, so it works on a
  stream you cannot store.

Block 5 - the n/3 generalisation
  [1, 1, 1, 3, 3, 2, 2, 2]   > n/3: [1, 2]       expected [1, 2]
  [1, 2]                     > n/3: [1, 2]       expected [1, 2]
  [3, 3, 4]                  > n/3: [3]          expected [3]
  [1, 1, 2, 2, 3, 3]         > n/3: []           expected []
  at most 2 elements can exceed n/3, so 2 candidates and 2 counters suffice.
  In general, at most k-1 elements can exceed n/k - the same trick scales.

leader: passed
```

Block 3 is the trap. The voting phase always returns *something*, and that something is meaningless unless a majority actually exists.

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

## Practice — independent task

Implement `heavy_hitters(stream, k)` — every element appearing more than $n/k$ times, in one pass and $O(k)$ space.

1. Generalise the two-candidate version: keep $k-1$ candidates with counts. On a new element, increment if present; else take an empty slot; else decrement **all** counters and drop any that reach zero. This is the Misra–Gries algorithm.
2. Prove to yourself that $k-1$ slots suffice, by arguing about how much "weight" each decrement removes. State the argument in a comment.
3. Verification is again mandatory: a second pass counting only the surviving candidates.
4. Test against a `Counter` oracle on many random streams with varying $k$ and skew.
5. **Then use it as a sketch.** Run it *without* the second pass on a stream you cannot re-read, and measure the error: for each reported candidate, how far is its counter from the true count? There is a known bound — the counter underestimates by at most $n/k$. Confirm it empirically and report the worst case you saw.

**Edge cases:** $k = 2$ (plain majority); $k > n$; an empty stream; every element distinct; a stream where exactly $k-1$ elements qualify.

**Done when:** your two-pass version matches the oracle on every test, and your one-pass error is within the $n/k$ bound across at least a thousand random streams.

## Before moving on

You can implement voting, explain the cancellation, and say why verification is mandatory.

**Recap:** Boyer–Moore finds a **candidate** in $O(n)$ time and $O(1)$ space by pairing off unequal elements; a true majority survives because it has more than half the elements; the algorithm always returns something, so **you must verify with a second count**; at most $k-1$ elements can exceed $n/k$, which is what makes the generalisation work with $k-1$ counters.

**Next:** [[09-max-slice-algorithms|Max Slice]] — another one-pass array algorithm with a running value.

## Related Modules
- [[10-greedy-algorithms|Greedy Algorithms]] — Boyer-Moore is a greedy approach
- [[04-sorting/index|Sorting Algorithms]] — $O(n \log n)$ sort-based solution
