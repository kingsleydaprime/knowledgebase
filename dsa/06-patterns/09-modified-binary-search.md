# Pattern: Modified Binary Search

**[Advanced]** — A university-level introduction to the modified binary search pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand binary search. See [[05-searching|binary search]] if needed.
- You should understand arrays and basic loops. See [[01-arrays|arrays]] if needed.

**What you will be able to do after this lesson:**

1. Define the modified binary search pattern and explain why it adapts binary search to non-sorted data.
2. Implement binary search on rotated sorted arrays.
3. Apply the pattern to binary search on the answer (e.g., Koko eating bananas, minimum ship capacity).
4. Explain the key insight that makes modified binary search work.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're searching for a target value in a sorted array, but the array has been rotated at some unknown pivot point. The array `[4, 5, 6, 7, 0, 1, 2]` is sorted, but rotated at index 4. Standard binary search won't work because the array isn't fully sorted.

However, even when the whole array isn't sorted, at least one of the two halves around any `mid` is guaranteed to be sorted. This insight lets us adapt binary search: we can check which half is sorted, then determine if the target could be in that sorted half's range, and search there; otherwise, the target must be in the other (still-rotated) half.

This is the modified binary search pattern: adapt the halving logic of binary search to arrays that aren't fully sorted in the plain sense — most commonly, a sorted array that's been **rotated** at some unknown pivot. The core trick: even when the whole array isn't sorted, at least one of the two halves around any `mid` always is, and you can use that fact to decide which half to search.

There's another variant worth knowing separately: **binary search on the answer** — instead of binary searching over an array, you binary search over the space of possible answers. This applies when a problem asks for the optimal value satisfying some condition, and "is candidate value X good enough?" is cheap to check and has a **monotonic** answer (every value below some threshold fails, every value at or above it works, with no flip-flopping).

---

## 2. Definitions and terminology

| Term                            | Plain-English definition                                                       | Example / analogy                                                           |
| ------------------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| **Modified binary search**      | Adapt binary search to arrays that aren't fully sorted but have some structure | Search in a rotated sorted array                                            |
| **Rotated sorted array**        | A sorted array that's been rotated at some unknown pivot point                 | `[4, 5, 6, 7, 0, 1, 2]` (sorted `[0, 1, 2, 4, 5, 6, 7]` rotated at index 4) |
| **Binary search on the answer** | Binary search over the space of possible answers, not array indices            | Find minimum eating speed for Koko to finish bananas in H hours             |
| **Monotonic predicate**         | A condition that, once true, stays true for all larger values                  | "Can Koko eat at speed X in H hours?" (true for X >= some threshold)        |

---

## 3. How it works — step by step

### Binary search on rotated sorted array

At each step, first figure out which half is the "normal" sorted one (compare `nums[left]` to `nums[mid]`), then check whether the target could be in that sorted half's range — if so, search there; otherwise, the target must be in the other (still-rotated) half.

```python
def search_rotated(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:            # left half is normally sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:                                   # right half is normally sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

**Concrete example:** `nums = [4, 5, 6, 7, 0, 1, 2], target = 0`

```
left=0 right=6 mid=3  nums[3]=7
  nums[0]=4 <= 7 -> left half [4,5,6,7] is sorted
  is 0 in [4, 7)? no -> search right half: left=4
left=4 right=6 mid=5  nums[5]=1
  nums[4]=0 <= 1 -> left half [0,1] is sorted
  is 0 in [0, 1)? yes -> search left half: right=4
left=4 right=4 mid=4  nums[4]=0 == target -> found at index 4
```

### Binary search on the answer

The rotated-array case above still binary-searches _over the array_. A distinct and very commonly tested variant instead binary-searches **over the space of possible answers**:

**Example:** given `n` holes in a roof and `k` boards, find the minimum board size that lets all holes be covered using at most `k` boards.

```python
def min_board_size(holes, k):
    def boards_needed(size):          # greedy check: how many boards of this size are needed?
        count, last_covered = 0, -1
        for i, has_hole in enumerate(holes):
            if has_hole and last_covered < i:
                count += 1
                last_covered = i + size - 1
        return count

    lo, hi, result = 1, len(holes), -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if boards_needed(mid) <= k:     # mid is "good enough" — try to do better
            result = mid
            hi = mid - 1
        else:                            # mid isn't enough — need a bigger size
            lo = mid + 1
    return result
```

The shape to recognize: `lo`/`hi` bound a range of **candidate answers**, not array indices; the "check" function (`boards_needed` here) is usually its own separate O(n) pass; and the overall complexity becomes **O(n log n)** — an O(n) check repeated O(log n) times — rather than the plain O(log n) of searching an already-built array.

Other classic problems in this exact shape: "minimum ship capacity to deliver packages within D days," "Koko eating bananas" (minimum eating speed to finish within h hours), "split array into k parts minimizing the largest part's sum."

The tell that a problem wants this pattern: it asks for a minimum/maximum value satisfying a constraint, and you can imagine a "does value X work?" check that's monotonic (works for X implies works for every value past X in the same direction) — that monotonicity is precisely what makes binary search valid here, same as sortedness is what makes it valid on an array.

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `modified_binary_search_lab.py` and run `python3 modified_binary_search_lab.py`. It uses only Python's standard library and creates no external files.

```python
from typing import List


def search_rotated(nums: List[int], target: int) -> int:
    """Search in a rotated sorted array."""
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:            # left half is normally sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:                                   # right half is normally sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


def min_eating_speed(piles: List[int], h: int) -> int:
    """Find minimum eating speed for Koko to finish all piles in h hours."""
    def can_finish(speed: int) -> bool:
        hours = 0
        for pile in piles:
            hours += (pile + speed - 1) // speed  # ceiling division
            if hours > h:
                return False
        return True

    lo, hi = 1, max(piles)
    result = hi
    while lo <= hi:
        mid = (lo + hi) // 2
        if can_finish(mid):      # mid is "good enough" — try to do better
            result = mid
            hi = mid - 1
        else:                    # mid isn't enough — need a bigger speed
            lo = mid + 1
    return result


def min_ship_capacity(weights: List[int], days: int) -> int:
    """Find minimum ship capacity to ship all weights in given days."""
    def can_ship(capacity: int) -> bool:
        days_needed, current_load = 1, 0
        for weight in weights:
            if weight > capacity:        # a single package cannot be split
                return False
            if current_load + weight > capacity:
                days_needed += 1         # start a new day
                current_load = 0
            current_load += weight
        return days_needed <= days

    lo, hi = max(weights), sum(weights)
    result = hi
    while lo <= hi:
        mid = (lo + hi) // 2
        if can_ship(mid):       # mid is "good enough" — try to do better
            result = mid
            hi = mid - 1
        else:                   # mid isn't enough — need a bigger capacity
            lo = mid + 1
    return result


if __name__ == "__main__":
    # Test case 1: search in rotated sorted array
    nums1 = [4, 5, 6, 7, 0, 1, 2]
    target1 = 0
    result1 = search_rotated(nums1, target1)
    print(f"Test 1 - search in rotated sorted array:")
    print(f"nums={nums1}, target={target1} -> index {result1}")
    assert result1 == 4, f"Expected 4, got {result1}"

    # Test case 2: Koko eating bananas
    piles2 = [3, 6, 7, 11]
    h2 = 8
    result2 = min_eating_speed(piles2, h2)
    print(f"\nTest 2 - Koko eating bananas:")
    print(f"piles={piles2}, h={h2} -> speed {result2}")
    assert result2 == 4, f"Expected 4, got {result2}"

    # Test case 3: ship capacity
    weights3 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    days3 = 5
    result3 = min_ship_capacity(weights3, days3)
    print(f"\nTest 3 - ship capacity:")
    print(f"weights={weights3}, days={days3} -> capacity {result3}")

    print("\nmodified_binary_search_lab: passed")
```

Expected output:

```
Test 1 - search in rotated sorted array:
nums=[4, 5, 6, 7, 0, 1, 2], target=0 -> index 4

Test 2 - Koko eating bananas:
piles=[3, 6, 7, 11], h=8 -> speed 4

Test 3 - ship capacity:
weights=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], days=5 -> capacity 15

modified_binary_search_lab: passed
```

---

## 5. Related patterns and extensions

### Search a 2D Matrix

Treat the 2D matrix as one flat sorted array:

```python
def search_2d_matrix(matrix, target):
    if not matrix or not matrix[0]:
        return False

    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1

    while left <= right:
        mid = (left + right) // 2
        row, col = divmod(mid, n)
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] < target:
            left = mid + 1
        else:
            right = mid - 1

    return False
```

### Median of Two Sorted Arrays

Binary search on the partition point:

```python
def find_median_sorted_arrays(nums1, nums2):
    # Ensure nums1 is the smaller array
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    lo, hi = 0, m

    while lo <= hi:
        partition1 = (lo + hi) // 2
        partition2 = (m + n + 1) // 2 - partition1

        max_left1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        min_right1 = float('inf') if partition1 == m else nums1[partition1]
        max_left2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        min_right2 = float('inf') if partition2 == n else nums2[partition2]

        if max_left1 <= min_right2 and max_left2 <= min_right1:
            # Found the correct partition
            if (m + n) % 2 == 0:
                return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
            else:
                return max(max_left1, max_left2)
        elif max_left1 > min_right2:
            hi = partition1 - 1
        else:
            lo = partition1 + 1

    return 0
```

---

## 6. Complexity

- **Rotated array search:** O(log n) — same as standard binary search; the extra "which half is sorted" check is O(1) work added to each step.
- **Binary search on the answer:** O(n log n) — an O(n) check repeated O(log n) times (where n is the size of the input to the check function).

---

## 7. Tradeoffs and limitations

- **Rotated array search:** Requires the array to be sorted and rotated (not arbitrary unsorted data). The algorithm assumes exactly one rotation point.
- **Binary search on the answer:** Requires the predicate to be monotonic (once true, stays true for larger values). Not all optimization problems have this property.
- **Rotated array search:** The "which half is sorted" check can be confusing; understanding why it works is key.

---

## 8. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given `nums = [4, 5, 6, 7, 0, 1, 2]` and `target = 0`, trace through the rotated array search algorithm step by step.
2. **Question:** Why does the "which half is sorted" check work for rotated arrays?
3. **Question:** What makes a problem suitable for binary search on the answer?

### Answers — after your attempt

1. `left=0 right=6 mid=3 nums[3]=7`
   `nums[0]=4 <= 7 -> left half [4,5,6,7] is sorted`
   `is 0 in [4, 7)? no -> search right half: left=4`
   `left=4 right=6 mid=5 nums[5]=1`
   `nums[4]=0 <= 1 -> left half [0,1] is sorted`
   `is 0 in [0, 1)? yes -> search left half: right=4`
   `left=4 right=4 mid=4 nums[4]=0 == target -> found at index 4`
2. Even when the whole array isn't sorted, at least one of the two halves around any `mid` is guaranteed to be sorted. This is because the array was originally sorted and then rotated at some point. The sorted half's range is contiguous, so we can check if the target could be in that range.
3. A problem is suitable for binary search on the answer if:
   - It asks for a minimum/maximum value satisfying some constraint.
   - You can imagine a "does value X work?" check that's monotonic (once true, stays true for larger values).
   - The check function is relatively efficient (usually O(n) or better).

---

## 9. Practice — independent task

**Task:** Implement a function `min_eating_speed(piles, h)` that returns the minimum eating speed for Koko to finish all piles in h hours. Use the binary search on the answer pattern. Test it with the following cases:

- `piles = [3, 6, 7, 11], h = 8` → expected `4`
- `piles = [30, 11, 23, 4, 20], h = 5` → expected `30`

**Done when:** your function returns the correct minimum eating speed for both test cases.

---

## Practice problems

**In the [[foundations/dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[028-binary-search|Binary Search]] (LeetCode #704) — the baseline — settle your loop invariant here, once.
2. [[029-search-a-2d-matrix|Search a 2D Matrix]] (LeetCode #74) — index arithmetic turns the grid into one sorted array.
3. [[030-koko-eating-bananas|Koko Eating Bananas]] (LeetCode #875) — binary search on the **answer**, with a feasibility predicate.
4. [[031-find-minimum-in-rotated-sorted-array|Find Minimum in Rotated Sorted Array]] (LeetCode #153) — compare mid against the right end, not the left.
5. [[032-search-in-rotated-sorted-array|Search in Rotated Sorted Array]] (LeetCode #33) — identify which half is sorted, then decide.
6. [[033-time-based-key-value-store|Time Based Key-Value Store]] (LeetCode #981) — search for the largest timestamp not exceeding the query.
7. [[034-median-of-two-sorted-arrays|Median of Two Sorted Arrays]] (LeetCode #4) — binary search on the partition point; the hardest in the set.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they drill boundary-finding and search-on-the-answer separately:

8. Capacity To Ship Packages Within D Days (#1011) — the problem the lab's `min_ship_capacity` solves — do it after reading section 3.
9. First Bad Version (#278) — the minimal find-the-boundary template.
10. Search Insert Position (#35) — where the two loop conventions visibly differ.
11. Find First and Last Position of Element in Sorted Array (#34) — two boundary searches in one problem.
12. Find Peak Element (#162) — binary search with no sorted order at all, only a local condition.
13. Split Array Largest Sum (#410) — search-on-the-answer again, with a harder predicate.

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] Write a binary search with correct bounds and no infinite loop.
- [ ] Explain how to decide which half of a *rotated* array is sorted.
- [ ] Implement search-in-rotated-array independently.
- [ ] Explain why `low + (high - low) // 2` is preferred over `(low + high) // 2`.

**Recap:** Binary search halves the search space each step by exploiting an ordering invariant. The variants keep that invariant while the data is transformed — in a rotated array, at least one half is always properly sorted, so you test which and recurse into the half that could contain the target. The bugs are almost always in the boundary conditions rather than the idea.

**Next:** [[10-binary-tree-traversal-pattern|binary-tree-traversal-pattern]] — the same divide-and-conquer instinct applied to a branching structure instead of a linear one.

## 10. Related

- [[05-searching|searching]] — the baseline binary search algorithm
- [[04-sorting|sorting]] — prerequisite for rotated array search
- [[01-algorithms|algorithms]] — where the O(log n) vs O(n log n) comparison comes from
- [[09-modified-binary-search|modified-binary-search]] — this note

---

## 11. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Optimization problems:** Finding optimal parameters in engineering design
- **Resource allocation:** Determining optimal allocation of limited resources
- **Production planning:** Finding optimal production rates
- **Network routing:** Finding optimal path costs

The core idea — using binary search over a space of possible answers when you have a monotonic predicate — is a fundamental algorithmic technique that appears whenever you need to find an optimal value efficiently.
