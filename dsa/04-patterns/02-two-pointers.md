---
id: 799a1dac-c75c-4a83-8b4c-e1b73918862d
---

# Pattern: Two Pointers

Two pointers is a technique where you keep two positions in a list and move them towards each other, or in the same direction, to solve a problem in one pass. It often replaces a slow check of every pair. It is like two people searching a row of shelves from both ends and meeting in the middle.

## Before you start
<!-- bite: 374f1843-1572-4f29-8142-4f99c1d0efcf -->

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
<!-- bite: ff2388e6-ec04-48c7-8366-69a1627701e3 -->

Imagine you have a list of bank deposits and withdrawals, and you want to find two transactions that exactly cancel each other out (sum to zero). The naive approach is to check every pair of transactions: for each transaction, loop through all later transactions and see if they sum to zero. That's O(n²) — for 1,000 transactions, that's 500,000 pair checks.

If the list is sorted, you can do better. Think of it like finding two people at a party who have exactly the same amount of money: if one person has too little, you need to find someone with more money to balance it out. You can start with the person who has the least money and the person who has the most money, and based on whether their combined total is too much or too little, move one of them inward.

This is the two-pointer pattern: walk two positions through a sorted structure at once, letting their relative movement do the work that a nested loop would otherwise do. It turns O(n²) into O(n) when the data is sorted and you need to find pairs (or a small fixed number of elements) satisfying some condition on their sum/difference.

---

## 2. Definitions and terminology
<!-- bite: 108ff508-c686-4227-8178-a98d46eb7fbe -->

| Term                    | Plain-English definition                                                                                                     | Example / analogy                                                               |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Two-pointer pattern** | Walk two indices through a sorted structure simultaneously, moving them based on a condition rather than checking every pair | Finding two people with matching money by starting with the poorest and richest |
| **Sorted array**        | Elements arranged in non-decreasing order                                                                                    | `[1, 3, 5, 7, 9]`                                                               |
| **Pair search**         | Find two elements that satisfy a condition (usually sum equals a target)                                                     | Find two numbers that sum to 10                                                 |
| **Convergence**         | The two pointers moving toward each other until they meet or cross                                                           | The poorest and richest person walking toward the center of the room            |

---

## 3. How it works — step by step
<!-- bite: 5a9d63a2-cdfa-49a7-b39f-c25568e011e6 -->

Given a sorted array `nums` and a target sum `target`:

```text
nums = [1, 2, 3, 4, 6], target = 6
```

Start one pointer at the beginning (`left = 0`) and one at the end (`right = len(nums) - 1`):

```text
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
<!-- bite: fd6526d3-47d5-4951-b6b7-35832f4ece5f -->

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
    target2 = 11
    result2 = two_sum_sorted(nums2, target2)
    print(f"nums={nums2}, target={target2} -> indices {result2}")
    assert result2 == [-1, -1], f"Expected [-1, -1], got {result2}"

    # Test case 3: duplicate values
    nums3 = [2, 2, 3, 4]
    target3 = 4
    result3 = two_sum_sorted(nums3, target3)
    print(f"nums={nums3}, target={target3} -> indices {result3}")
    assert result3 == [0, 1], f"Expected [0, 1], got {result3}"

    print("two_pointers_lab: passed")
```

Expected output:

```text
nums=[1, 2, 3, 4, 6], target=6 -> indices [1, 3]
nums=[1, 3, 5, 7], target=11 -> indices [-1, -1]
nums=[2, 2, 3, 4], target=4 -> indices [0, 1]
two_pointers_lab: passed
```

---

## 5. Related patterns and extensions
<!-- bite: a6f3a1ab-dc89-498a-8140-252906aa5e6d -->

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
<!-- bite: c4d3d7df-ede2-457e-abf0-a082ced99642 -->

- **Requires sorted input.** Sorting costs O(n log n), which may be more expensive than the O(n²) pair check for small n. For unsorted data, a hash-map version exists (O(n) time, O(n) space) but loses the space efficiency.
- **Only finds pairs (or fixed small number of elements).** The pattern naturally extends to three-sum, four-sum, etc., but the complexity grows with the number of pointers.
- **Works best for sum/difference conditions.** For other conditions (e.g., product, ratio), the pattern may not apply directly.

---

## Check your understanding
<!-- bite: 4981a114-4067-4b13-bc80-64a519368361 -->

Try each one before you open the answer.

1. <!-- q: mcq id="98d3d977" -->
   The two-pointer pair search starts one pointer at each end of the array and moves them inward. What must be true of the array for this to work?

   - [ ] It has no duplicates
   - [x] It is sorted
   - [ ] Its length is even
   - [ ] All values are positive

   <details><summary>Answer</summary>

   It must be sorted. Sorting is what tells you that moving left raises the sum and moving right lowers it.

   </details>

2. <!-- q: gap id="4b5567ef" answers="left;right" -->
   Fill in the gaps. In the two-pointer pair search on a sorted array, if the sum is too small you move the ___ pointer, and if the sum is too large you move the ___ pointer.

   <details><summary>Answer</summary>

   Too small: move left up to a bigger number. Too large: move right down to a smaller number.

   </details>

3. <!-- q: mcq id="37b3ef16" -->
   In "container with most water", the area between two lines is width × the shorter height. After checking a pair, which pointer moves inward?

   - [ ] Always the left one
   - [ ] The taller line
   - [x] The shorter line
   - [ ] Both at once

   <details><summary>Answer</summary>

   The shorter line. The width can only shrink, and the shorter line caps the height, so keeping it can never give a bigger area.

   </details>

4. <!-- q: mcq id="a2e9ff9c" -->
   Three-sum sorts the array, fixes one element, then runs two pointers over the rest. What is its time complexity?

   - [ ] O(n)
   - [ ] O(n log n)
   - [x] O(n²)
   - [ ] O(n³)

   <details><summary>Answer</summary>

   O(n²). The sort costs O(n log n), then for each of the n fixed elements the two-pointer pass costs O(n).

   </details>

5. <!-- q: open id="bd1cb5ed" -->
   In a sorted array, nums[left] + nums[right] is smaller than the target, so you move left up by one. Why is it safe to skip every other pair that uses the old left value?

   <details><summary>Answer</summary>

   The old left value paired with right was already too small, and right is the biggest value still in play. Pairing the old left with any smaller value can only give an even smaller sum. So no pair using the old left can hit the target, and one step rules them all out.

   </details>

## Check your understanding: worked problems
<!-- bite: b2acd057-3c64-4c7b-affd-402394d5f0bd -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="b81d70a1" answers="2;3;5" -->
   Fill in the gaps. Run the two-pointer pair search on nums = [1, 3, 4, 6, 8, 11] with target 10. left starts at index 0 and right at index 5. It finds the pair at left = ___ and right = ___, after checking ___ sums.

   <details><summary>Answer</summary>

   left = 2, right = 3, after 5 sums. 1+11 = 12 (right down), 1+8 = 9 (left up), 3+8 = 11 (right down), 3+6 = 9 (left up), 4+6 = 10, found.

   </details>

2. <!-- q: gap id="0f30b097" answers="12;9;11" -->
   Fill in the gaps. Two-pointer pair search on nums = [1, 3, 4, 6, 8, 11], target 10. The first three sums checked are ___, ___ and ___.

   <details><summary>Answer</summary>

   12, 9, 11. Start with 1 + 11 = 12, too big, so right moves to 8. Then 1 + 8 = 9, too small, so left moves to 3. Then 3 + 8 = 11.

   </details>

3. <!-- q: exact id="f33536c6" answer="36" -->
   Container with most water: the line heights are [2, 3, 10, 5, 7, 8, 9] at indices 0 to 6. The area between lines i and j is (j − i) × min(height i, height j). What is the largest area?

   <details><summary>Answer</summary>

   36, from lines 2 and 6: width 4 × min(10, 9) = 36. The two-pointer scan finds it by always moving the shorter line inward.

   </details>

4. <!-- q: exact id="f5d5a6ba" answer="3" -->
   How many unique triplets in [−2, 0, 1, 1, 2, −1, −4] sum to 0? Count each set of values once.

   <details><summary>Answer</summary>

   3: [−2, 0, 2], [−2, 1, 1] and [−1, 0, 1]. Sorting first and skipping repeated values stops the same triplet being counted twice.

   </details>

## 8. Practice — independent task
<!-- bite: 2e6c782d-ea76-4515-94a9-9c3f68268337 -->

**Task:** Implement a function `three_sum(nums, target)` that returns all unique triplets that sum to `target`. Use the three-sum extension pattern. Test it with the following cases:

- `nums = [-1, 0, 1, 2, -1, -4], target = 0` → expected `[[-1, -1, 2], [-1, 0, 1]]` (order doesn't matter)
- `nums = [0, 0, 0], target = 0` → expected `[[0, 0, 0]]`

**Done when:** your function returns the correct triplets (order doesn't matter) and handles duplicates correctly.

---

## Practice problems
<!-- bite: 1aca8a07-184a-4850-8d45-2b8ef4689722 -->

**In the [[dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[010-valid-palindrome|Valid Palindrome]] (LeetCode #125) — the simplest form: one pointer from each end, skip what does not count, compare.
2. [[011-two-sum-ii|Two Sum II]] (LeetCode #167) — the sorted-input version the lab implements; the sum tells you which pointer to move.
3. [[012-3sum|3Sum]] (LeetCode #15) — fix one element, then two-pointer the rest; the duplicate-skipping is where it gets fiddly.
4. [[013-container-with-most-water|Container With Most Water]] (LeetCode #11) — start widest and move the **shorter** wall, because moving the taller one can never help.
5. [[014-trapping-rain-water|Trapping Rain Water]] (LeetCode #42) — two pointers carrying running maxima; also solvable with prefix/suffix arrays, which is why it appears in [[01-prefix-sum|prefix-sum]] too.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they isolate the pointer-movement decision more cleanly than the harder problems in the 150 do:

6. Remove Duplicates from Sorted Array (#26) — the read/write two-pointer — a different shape from the converging one.
7. Merge Sorted Array (#88) — merge **backwards** from the end to avoid overwriting.
8. Squares of a Sorted Array (#977) — negatives put the largest values at both ends.
9. Reverse String (#344) — the pattern with nothing else in the way.
10. 3Sum Closest (#16) — 3Sum with "track the best" instead of an exact target.
11. 4Sum (#18) — two fixed elements, two-pointer the rest — the natural generalisation.

## Before moving on
<!-- bite: 81054dcc-7c1b-47d4-9365-77f1a81d7ada -->

You are done with this pattern when you can, closed-book:

- [ ] Explain why sorting is a precondition, and what breaks without it.
- [ ] Trace the two indices on `[2,7,11,15]` for target 9 without running the code.
- [ ] Implement two-sum-on-sorted independently and handle the no-solution case.
- [ ] State why this is O(n) despite examining pairs, and why the naive version is O(n²).

**Recap:** Two pointers converge from both ends of **sorted** data, moving the one whose value is provably wrong. Each index only ever moves forward, so every element is visited at most once and the pass is O(n) with O(1) extra space — replacing the O(n²) nested loop that checks every pair.

**Next:** [[03-sliding-window|sliding-window]] — the same idea with both pointers moving in the *same* direction, which is what you need when the window is contiguous rather than converging.

## 9. Related
<!-- bite: 40c0115e-6c48-4541-95c6-448b4619dee0 -->

- [[01-arrays|arrays]] — the underlying structure
- [[05-sorting/index|sorting]] — prerequisite for this pattern
- [[03-sliding-window|sliding-window]] — a specialization where both pointers move in the same direction
- [[04-fast-slow-pointers|fast-slow-pointers]] — another pointer pattern for cycle detection
- [[03-hash-maps|hash maps]] — alternative for unsorted input (O(n) time, O(n) space)
- [[01-growth-and-asymptotic-notation|algorithms]] — where the O(n²) vs O(n) complexity framing comes from

## About this lesson
<!-- bite: 41102d7a-7298-495d-b82c-5220a9cf198f -->

**Level:** Beginner. **Covers:** A university-level introduction to the two-pointer pattern: what it is, why it exists, how it works, and how to implement it independently.
