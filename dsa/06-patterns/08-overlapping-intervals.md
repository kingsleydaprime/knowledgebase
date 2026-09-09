# Pattern: Overlapping Intervals

**[Intermediate]** — A university-level introduction to the overlapping intervals pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand arrays and basic loops. See [[01-arrays|arrays]] if needed.
- You should understand sorting. See [[04-sorting|sorting]] if needed.

**What you will be able to do after this lesson:**

1. Define the overlapping intervals pattern and explain why sorting by start time first makes everything linear.
2. Implement merging overlapping intervals.
3. Apply the pattern to related problems like inserting intervals and counting non-overlapping intervals.
4. Explain the overlap condition and why it works.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're scheduling meetings and you have a list of available time slots. You want to merge overlapping slots to find the continuous blocks of time you have free. The naive approach is to check every pair of intervals for overlap: for each interval, loop through all later intervals and see if they overlap. That's O(n²) — for 1,000 intervals, that's 500,000 pair checks.

If the intervals are sorted by start time, you can do better. Think of it like finding overlapping appointments: if you sort by start time, you can process them in order and merge as you go. The first interval sets the initial merged block, and each subsequent interval either extends the current block (if it overlaps) or starts a new block (if it doesn't overlap).

This is the overlapping intervals pattern: sort by start time, then process in a single linear pass. It turns O(n²) into O(n log n) — the sorting dominates, but the merge itself is linear.

---

## 2. Definitions and terminology

| Term                          | Plain-English definition                                | Example / analogy                                      |
| ----------------------------- | ------------------------------------------------------- | ------------------------------------------------------ |
| **Overlapping intervals**     | Two intervals `[a, b]` and `[c, d]` overlap if `b >= c` | Meeting slots that overlap in time                     |
| **Merge intervals**           | Combine overlapping intervals into a single interval    | Merge overlapping meeting times into continuous blocks |
| **Non-overlapping intervals** | Intervals that don't overlap with each other            | Disjoint time slots                                    |
| **Interval**                  | A range defined by a start and end point                | `[start, end]` where `start <= end`                    |

---

## 3. How it works — step by step

### Overlap condition

Once sorted by start time, two intervals `[a, b]` and `[c, d]` (with `c` coming after `a`) overlap exactly when `b >= c` — the first interval hasn't ended before the second one begins.

### Merge algorithm

```python
def merge_intervals(intervals):
    intervals.sort(key=lambda pair: pair[0])   # sort by start time — the step that makes this linear after
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:                   # overlaps with the last merged interval
            merged[-1] = [last_start, max(last_end, end)]
        else:
            merged.append([start, end])
    return merged
```

**Concrete example:**

```
intervals = [[1,3], [2,6], [8,10], [15,18]]
sorted (already is)

[1,3] -> merged=[[1,3]]
[2,6] -> 2 <= 3, overlaps -> merged=[[1,6]]
[8,10] -> 8 > 6, no overlap -> merged=[[1,6],[8,10]]
[15,18] -> 15 > 10, no overlap -> merged=[[1,6],[8,10],[15,18]]
```

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `overlapping_intervals_lab.py` and run `python3 overlapping_intervals_lab.py`. It uses only Python's standard library and creates no external files.

```python
def merge_intervals(intervals):
    """Merge overlapping intervals."""
    if not intervals:
        return []

    intervals.sort(key=lambda pair: pair[0])   # sort by start time
    merged = [intervals[0]]

    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:                   # overlaps with the last merged interval
            merged[-1] = [last_start, max(last_end, end)]
        else:
            merged.append([start, end])

    return merged


def insert_interval(intervals, new_interval):
    """Insert a new interval and merge if necessary."""
    intervals.append(new_interval)
    return merge_intervals(intervals)


def erase_overlap_intervals(intervals):
    """Find the minimum number of intervals to remove to make the rest non-overlapping."""
    if not intervals:
        return 0

    intervals.sort(key=lambda pair: pair[1])   # sort by end time

    count = 0
    end = intervals[0][1]

    for start, finish in intervals[1:]:
        if start < end:                         # overlaps with previous interval
            count += 1
        else:
            end = finish

    return count


def can_attend_all_meetings(intervals):
    """Check if a person can attend all meetings (no overlaps)."""
    intervals.sort(key=lambda pair: pair[0])   # sort by start time

    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i-1][1]:  # overlaps
            return False

    return True


if __name__ == "__main__":
    # Test case 1: merge intervals
    intervals1 = [[1,3], [2,6], [8,10], [15,18]]
    result1 = merge_intervals(intervals1)
    print(f"Test 1 - merge intervals:")
    print(f"intervals={intervals1} -> {result1}")
    expected1 = [[1,6], [8,10], [15,18]]
    assert result1 == expected1, f"Expected {expected1}, got {result1}"

    # Test case 2: insert interval
    intervals2 = [[1,3], [6,9]]
    result2 = insert_interval(intervals2, [2,5])
    print(f"\nTest 2 - insert interval:")
    print(f"intervals={intervals2}, new=[2,5] -> {result2}")
    expected2 = [[1,5], [6,9]]
    assert result2 == expected2, f"Expected {expected2}, got {result2}"

    # Test case 3: erase overlap intervals
    intervals3 = [[1,2], [2,3], [3,4], [1,3]]
    result3 = erase_overlap_intervals(intervals3)
    print(f"\nTest 3 - erase overlap intervals:")
    print(f"intervals={intervals3} -> {result3}")
    assert result3 == 1, f"Expected 1, got {result3}"

    # Test case 4: can attend all meetings
    intervals4 = [[0,30], [5,10], [15,20]]
    result4 = can_attend_all_meetings(intervals4)
    print(f"\nTest 4 - can attend all meetings:")
    print(f"intervals={intervals4} -> {result4}")
    assert result4 == False, f"Expected False, got {result4}"

    intervals5 = [[7,10], [2,4]]
    result5 = can_attend_all_meetings(intervals5)
    print(f"\nTest 5 - can attend all meetings (no overlap):")
    print(f"intervals={intervals5} -> {result5}")
    assert result5 == True, f"Expected True, got {result5}"

    print("\noverlapping_intervals_lab: passed")
```

Expected output:

```
Test 1 - merge intervals:
intervals=[[1,3], [2,6], [8,10], [15,18]] -> [[1,6], [8,10], [15,18]]

Test 2 - insert interval:
intervals=[[1,3], [6,9]], new=[2,5] -> [[1,5], [6,9]]

Test 3 - erase overlap intervals:
intervals=[[1,2], [2,3], [3,4], [1,3]] -> 1

Test 4 - can attend all meetings:
intervals=[[0,30], [5,10], [15,20]] -> False

Test 5 - can attend all meetings (no overlap):
intervals=[[7,10], [2,4]] -> True

overlapping_intervals_lab: passed
```

---

## 5. Related patterns and extensions

### Meeting Rooms II (minimum meeting rooms required)

```python
def min_meeting_rooms(intervals):
    if not intervals:
        return 0

    starts = sorted([i[0] for i in intervals])
    ends = sorted([i[1] for i in intervals])

    rooms = 0
    end_ptr = 0

    for start in starts:
        if start < ends[end_ptr]:
            rooms += 1
        else:
            end_ptr += 1

    return rooms
```

### Non-overlapping Intervals (minimum removals to make non-overlapping)

Same as `erase_overlap_intervals` above.

### Employee Free Time (find common free time)

```python
def employee_free_time(schedules):
    # Flatten all intervals and merge
    all_intervals = []
    for schedule in schedules:
        all_intervals.extend(schedule)

    merged = merge_intervals(all_intervals)

    # Find gaps between merged intervals
    free_time = []
    for i in range(1, len(merged)):
        free_time.append([merged[i-1][1], merged[i][0]])

    return free_time
```

---

## 6. Complexity

O(n log n) — dominated by the initial sort; the merge pass itself is O(n). This is the same shape as most patterns that need sorted input first: see [[09-modified-binary-search|modified-binary-search]] and [[04-sorting|sorting]].

---

## 7. Tradeoffs and limitations

- **Overlap check must compare against the last merged interval.** After a merge, the effective end time may have grown past what the original list showed.
- **`start <= last_end` (not `<`)** — intervals that touch exactly at the boundary (`[1,3]` and `[3,5]`) count as overlapping in most problem definitions; check the specific problem's definition since this is a common off-by-one trap.
- **Sorting by start time vs end time.** Different problems require different sorting orders: merging needs start time, minimum removals needs end time.

---

## 8. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given `intervals = [[1,3], [2,6], [8,10], [15,18]]`, trace through the merge intervals algorithm step by step.
2. **Question:** Why does sorting by start time work for merging intervals but sorting by end time works for finding minimum removals?
3. **Question:** What happens if intervals are `[[1,4], [2,3]]`? Does the algorithm merge them correctly?

### Answers — after your attempt

1. `intervals = [[1,3], [2,6], [8,10], [15,18]]` (already sorted)
   `[1,3] -> merged=[[1,3]]`
   `[2,6] -> 2 <= 3, overlaps -> merged=[[1,6]]`
   `[8,10] -> 8 > 6, no overlap -> merged=[[1,6],[8,10]]`
   `[15,18] -> 15 > 10, no overlap -> merged=[[1,6],[8,10],[15,18]]`
2. Sorting by start time works for merging because we process intervals in order and extend the current merged interval whenever the next interval overlaps. Sorting by end time works for minimum removals because we want to remove as few intervals as possible: by sorting by end time, we always keep the interval that ends earliest, leaving more room for other intervals.
3. Yes, the algorithm merges them correctly: `[1,4]` and `[2,3]` overlap because `3 <= 4`, so they merge into `[1,4]`.

---

## 9. Practice — independent task

**Task:** Implement a function `can_attend_all_meetings(intervals)` that returns `True` if a person can attend all meetings (no overlaps), `False` otherwise. Use the overlapping intervals pattern. Test it with the following cases:

- `intervals = [[0,30], [5,10], [15,20]]` → expected `False` (overlaps)
- `intervals = [[7,10], [2,4]]` → expected `True` (no overlap)

**Done when:** your function returns the correct results for both test cases.

---

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] Explain why sorting by start time makes a single pass sufficient.
- [ ] State the merge condition precisely, including the touching-but-not-overlapping case.
- [ ] Implement interval merging independently.
- [ ] Handle the empty input and the fully-nested-interval cases.

**Recap:** Sorting intervals by start time means any interval that overlaps the current one must come next, so a single linear pass can merge everything. The whole difficulty is in the comparison: decide once whether `[1,2]` and `[2,3]` count as overlapping, and apply it consistently.

**Next:** [[09-modified-binary-search|modified-binary-search]] — the other pattern where sorted input unlocks a fundamentally faster algorithm — this time logarithmic rather than linear.

## 10. Related

- [[04-sorting|sorting]] — prerequisite for this pattern
- [[01-arrays|arrays]] — the underlying data structure
- [[01-algorithms|algorithms]] — where the O(n log n) vs O(n²) comparison comes from
- [[08-overlapping-intervals|overlapping-intervals]] — this note

---

## 11. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Calendar applications:** Merging overlapping time slots
- **Resource allocation:** Finding available time blocks
- **Network scheduling:** Allocating time slots for transmissions
- **Project management:** Identifying overlapping project phases

The core idea — sorting by start time and merging as you go — is a fundamental algorithmic technique that appears whenever you need to combine overlapping ranges into continuous blocks.
