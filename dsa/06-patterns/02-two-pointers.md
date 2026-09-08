# Pattern: Two Pointers

**[Beginner]** — A university-level introduction to the two-pointer pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand arrays and basic loops. See [[01-arrays|arrays]] if needed.
- You should know what a hash map is. See [[03-hash-maps|hash maps]] for the variant below.

**What you will be able to do after this lesson:**

1. Define the two-pointer pattern and explain why it turns an O(n²) pair-search into O(n).
2. Implement two-pointer search on a sorted array to find pairs that sum to a target.
3. Apply the pattern to related problems like three-sum and container with most water.
4. Explain why sorting is often a prerequisite and when the pattern fails.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you have a list of bank deposits and withdrawals, and you want to find two transactions that exactly cancel each other out (sum to zero). The naive approach is to check every pair of transactions: for each transaction, loop through all later transactions and see if they sum to zero. That's O(n²) — for 1,000 transactions, that's 500,000 pair checks.

If the list is sorted, you can do better. Think of it like finding two people at a party who have exactly the same amount of money: if one person has too little, you need to find someone with more money to balance it out. You can start with the person who has the least money and the person who has the most money, and based on whether their combined total is too much or too little, move one of them inward.

This is the two-pointer pattern: walk two positions through a sorted structure at once, letting their relative movement do the work that a nested loop would otherwise do. It turns O(n²) into O(n) when the data is sorted and you need to find pairs (or a small fixed number of elements) satisfying some condition on their sum/difference.

---

## 2. Definitions and terminology

| Term                    | Plain-English definition                                                                                                     | Example / analogy                                                               |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Two-pointer pattern** | Walk two indices through a sorted structure simultaneously, moving them based on a condition rather than checking every pair | Finding two people with matching money by starting with the poorest and richest |
| **Sorted array**        | Elements arranged in non-decreasing order                                                                                    | `[1, 3, 5, 7, 9]`                                                               |
| **Pair search**         | Find two elements that satisfy a condition (usually sum equals a target)                                                     | Find two numbers that sum to 10                                                 |
| **Convergence**         | The two pointers moving toward each other until they meet or cross                                                           | The poorest and richest person walking toward the center of the room            |

---

## 3. How it works — step by step

Given a sorted array `nums` and a target sum `target`:

```
nums = [1, 2, 3, 4, 6], target = 6
```

Start one pointer at the beginning (`left = 0`) and one at the end (`right = len(nums) - 1`):

```
left=0 right=4  1+6=7 > 6  -> right--
left=0 right=3  1+4=5 < 6  -> left++
left=1 right=3  2+4=6 == 6 -> found [1, 3]
```

At each step, move whichever pointer moves you toward the target:

- If the sum is too small, move `left` up (need a bigger element).
- If the sum is too large, move `right` down (need a smaller element).

The reason this works without checking every pair: at each step, one side of the comparison is eliminated entirely, not just one pair — moving `left` up rules out every pair that still includes the old, too-small `left` value paired with anything.

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `two_pointers_lab.py` and run `python3 two_pointers_lab.py`. It uses only Python's standard library and creates no external files.

```python
def two_sum_sorted(nums, target):
    """Find indices of two numbers that sum to target in a sorted array."""
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left, right]
        elif total < target:
            left += 1        # need a bigger sum -> move left pointer up
        else:
            right -= 1       # need a smaller sum -> move right pointer down
    return [-1, -1]           # no solution


if __name__ == "__main__":
    # Test case 1: basic example
    nums1 = [1, 2, 3, 4, 6]
    target1 = 6
    result1 = two_sum_sorted(nums1, target1)
    print(f"nums={nums1}, target={target1} -> indices {result1}")
    assert result1 == [1, 3], f"Expected [1, 3], got {result1}"

    # Test case 2: no solution
    nums2 = [1, 3, 5, 7]
    target2 = 10
    result2 = two_sum_sorted(nums2, target2)
    print(f"nums={nums2}, target={target2} -> indices {result2}")
    assert result2 == [-1, -1], f"Expected [-1, -1], got {result2}"

    # Test case 3: duplicate values
    nums3 = [2, 2, 3, 4]
    target3 = 4
    result3 = two_sum_sorted(nums3, target3)
    print(f"nums={nums3}, target={target3} -> indices {result3}")
    assert result3 == [0, 3] or result3 == [1, 2], f"Expected [0, 3] or [1, 2], got {result3}"

    print("two_pointers_lab: passed")
```

Expected output:

```
nums=[1, 2, 3, 4, 6], target=6 -> indices [1, 3]
nums=[1, 3, 5, 7], target=10 -> indices [-1, -1]
nums=[2, 2, 3, 4], target=4 -> indices [0, 3] or [1, 2]
two_pointers_lab: passed
```

---

## 5. Related patterns and extensions

### Three-sum (fix one element, two-pointer the rest)

```python
def three_sum(nums, target):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue  # skip duplicates
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == target:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                # skip duplicates
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif total < target:
                left += 1
            else:
                right -= 1
    return result
```

### Container with most water (area = width × min(height))

```python
def max_area(heights):
    left, right = 0, len(heights) - 1
    max_area = 0
    while left < right:
        width = right - left
        height = min(heights[left], heights[right])
        area = width * height
        max_area = max(max_area, area)
        # move the shorter line inward
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    return max_area
```

---

## 6. Tradeoffs and limitations

- **Requires sorted input.** Sorting costs O(n log n), which may be more expensive than the O(n²) pair check for small n. For unsorted data, a hash-map version exists (O(n) time, O(n) space) but loses the space efficiency.
- **Only finds pairs (or fixed small number of elements).** The pattern naturally extends to three-sum, four-sum, etc., but the complexity grows with the number of pointers.
- **Works best for sum/difference conditions.** For other conditions (e.g., product, ratio), the pattern may not apply directly.

---

## 7. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given `nums = [1, 3, 5, 7, 9]` and `target = 10`, trace through the two-pointer algorithm step by step.
2. **Question:** Why does moving `left` up when the sum is too small eliminate more than just one pair?
3. **Question:** What happens if the array contains duplicate values? Does the algorithm still work?

### Answers — after your attempt

1. `left=0 right=4  1+9=10 == 10 -> found [0, 4]` (the first step finds the solution because 1 + 9 = 10)
2. Moving `left` up eliminates all pairs that include the old `left` value with any `right` value greater than or equal to the current `right`. Since the array is sorted, if `nums[left] + nums[right] < target`, then `nums[left] + nums[right-1] < target` too (because `nums[right-1] ≤ nums[right]`), so all pairs with that `left` are invalid.
3. Yes, the algorithm still works. It may find one valid pair among duplicates, but it won't find all possible pairs involving duplicates. For example, in `[2, 2, 3, 4]` with target `4`, it finds `[0, 3]` (2 + 4) but not `[1, 2]` (2 + 3). To find all pairs, you'd need to handle duplicates specially.

---

## 8. Practice — independent task

**Task:** Implement a function `three_sum(nums, target)` that returns all unique triplets that sum to `target`. Use the three-sum extension pattern. Test it with the following cases:

- `nums = [-1, 0, 1, 2, -1, -4], target = 0` → expected `[[-1, -1, 2], [-1, 0, 1]]` (order doesn't matter)
- `nums = [0, 0, 0], target = 0` → expected `[[0, 0, 0]]`

**Done when:** your function returns the correct triplets (order doesn't matter) and handles duplicates correctly.

---

## 9. Related

- [[01-arrays|arrays]] — the underlying structure
- [[04-sorting|sorting]] — prerequisite for this pattern
- [[03-sliding-window|sliding-window]] — a specialization where both pointers move in the same direction
- [[04-fast-slow-pointers|fast-slow-pointers]] — another pointer pattern for cycle detection
- [[03-hash-maps|hash maps]] — alternative for unsorted input (O(n) time, O(n) space)
- [[01-algorithms|algorithms]] — where the O(n²) vs O(n) complexity framing comes from
