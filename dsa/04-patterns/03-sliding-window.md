---
id: 2b1d6684-a301-434a-8190-f41fb401fb79
---

# Pattern: Sliding Window

A sliding window is a technique where you look at a run of items next to each other in a list, and slide that run along one step at a time instead of starting again each time. It is useful for questions like "what is the best total over any 7 days?". A fitness app showing your step count for the last 7 days, updated each day, works this way.

## Before you start
<!-- bite: 267fc1cb-0f4a-46cd-a7c3-4f7a5add016d -->

- You should understand arrays and basic loops. See [[01-arrays|arrays]] if needed.
- You should know what a hash map is. See [[03-hash-maps|hash maps]] for the variant below.
- You should understand the two-pointer pattern. See [[02-two-pointers|two-pointers]] if needed.

**What you will be able to do after this lesson:**

1. Define the sliding-window pattern and explain why it turns "recompute something over every contiguous subarray/substring" from O(n·k) or O(n²) into O(n).
2. Implement fixed-size and variable-size sliding windows independently.
3. Apply the pattern to classic problems like longest substring without repeating characters and minimum window substring.
4. Explain the amortized O(n) analysis despite nested-looking loops.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)
<!-- bite: dea1e89e-8fbf-4744-9ee8-e00be0370564 -->

Imagine you're building a real-time analytics dashboard that needs to track the maximum sum of any 3-day window in a time series of stock prices. You could check every possible 3-day window:

```python
# O(n·k) naive approach
max_sum = -inf
for i in range(len(prices) - 2):
    window_sum = prices[i] + prices[i+1] + prices[i+2]
    max_sum = max(max_sum, window_sum)
```

That's fine for a single query, but a dashboard needs to answer many questions: "maximum 3-day sum," "minimum 5-day sum," "average 7-day window," etc. Each query recomputes the same sliding sums over and over.

The sliding-window pattern solves this: compute the first window's sum once, then slide it one step at a time, updating the sum by adding the new element and subtracting the element that falls out. This turns O(n·k) into O(n) — each element enters and leaves the window at most once.

Codility's course material calls this the **"caterpillar method"** — same technique (a front and back index, each only ever moving forward), different name — worth recognizing if it comes up under that label.

---

## 2. Definitions and terminology
<!-- bite: b6327999-2582-4152-a813-49775abe1dcf -->

| Term                     | Plain-English definition                                                                                                                        | Example / analogy                                                                      |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Sliding window**       | A contiguous subarray/substring that moves one element at a time, maintaining a fixed or variable size                                          | A camera panning across a scene, one pixel at a time                                   |
| **Fixed-size window**    | Window size `k` is constant; slide it one step at a time, removing the element that falls out the back and adding the one that enters the front | A 3-day moving average in finance                                                      |
| **Variable-size window** | Window grows and shrinks depending on a condition — expand the right edge to include more, shrink the left edge when a constraint is violated   | Longest substring without repeating characters                                         |
| **Amortized O(1)**       | The average cost per operation across a long sequence of calls, even though some individual operations are expensive                            | Resizing a dynamic array: most appends are O(1), but resizing is O(n) — amortized O(1) |

---

## 3. How it works — step by step
<!-- bite: b77c7343-c405-40f1-90cb-2325b0e93157 -->

### Fixed-size window

Window size `k` is constant; slide it one step at a time:

```python
def max_subarray_sum(nums, k):
    window_sum = sum(nums[:k])  # compute first window
    best = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # add new, drop oldest — O(1) per step
        best = max(best, window_sum)
    return best
```

**Concrete example:** `nums = [2, 1, 5, 1, 3, 2], k = 3`

```text
window [2,1,5] sum=8
        ^    ^    ^
slide:  [1,5,1] sum=8-2+1=7
        ^    ^    ^
slide:  [5,1,3] sum=7-1+3=9   <- best
        ^    ^    ^
slide:  [1,3,2] sum=9-5+2=6
        ^    ^    ^
```

### Variable-size window

Window grows and shrinks depending on a condition:

```python
def length_of_longest_substring(s):
    seen = set()
    left = 0
    best = 0
    for right in range(len(s)):
        while s[right] in seen:          # constraint violated -> shrink from the left
            seen.remove(s[left])
            left += 1
        seen.add(s[right])
        best = max(best, right - left + 1)
    return best
```

Each character is added to `seen` at most once and removed at most once across the whole run — that's what keeps this O(n) despite the nested-looking `while` inside the `for`.

---

## 4. Implementation — complete runnable example
<!-- bite: 5f99d786-2ea0-420e-8fcf-2191d533e9c1 -->

**Runnable example:** save as `sliding_window_lab.py` and run `python3 sliding_window_lab.py`. It uses only Python's standard library and creates no external files.

```python
def fixed_size_sliding_window(nums, k):
    """Maximum sum of any contiguous subarray of size k."""
    if len(nums) < k:
        return None
    window_sum = sum(nums[:k])  # compute first window
    best = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]  # add new, drop oldest
        best = max(best, window_sum)
    return best


def variable_size_sliding_window(nums):
    """Length of longest subarray with all unique elements."""
    seen = set()
    left = 0
    best = 0
    for right in range(len(nums)):
        while nums[right] in seen:          # constraint violated -> shrink from the left
            seen.remove(nums[left])
            left += 1
        seen.add(nums[right])
        best = max(best, right - left + 1)
    return best


if __name__ == "__main__":
    # Test case 1: fixed-size window
    nums1 = [2, 1, 5, 1, 3, 2]
    k1 = 3
    result1 = fixed_size_sliding_window(nums1, k1)
    print(f"nums={nums1}, k={k1} -> max sum {result1}")
    assert result1 == 9, f"Expected 9, got {result1}"

    # Test case 2: variable-size window
    nums2 = [1, 2, 3, 1, 2, 3, 1]
    result2 = variable_size_sliding_window(nums2)
    print(f"nums={nums2} -> longest unique substring length {result2}")
    assert result2 == 3, f"Expected 3, got {result2}"

    # Test case 3: edge case - all unique
    nums3 = [1, 2, 3, 4, 5]
    result3 = variable_size_sliding_window(nums3)
    print(f"nums={nums3} -> longest unique substring length {result3}")
    assert result3 == 5, f"Expected 5, got {result3}"

    print("sliding_window_lab: passed")
```

Expected output:

```text
nums=[2, 1, 5, 1, 3, 2], k=3 -> max sum 9
nums=[1, 2, 3, 1, 2, 3, 1] -> longest unique substring length 3
nums=[1, 2, 3, 4, 5] -> longest unique substring length 5
sliding_window_lab: passed
```

---

## 5. Why it's O(n) despite nested-looking loops
<!-- bite: a52afc34-a63d-440b-b281-fb4a9c6b2463 -->

The key insight: **each element enters and leaves the window at most once across the entire run.**

- In fixed-size windows, each element is added once (when it enters the window) and removed once (when it leaves the window).
- In variable-size windows, each element is added to `seen` at most once and removed at most once.

This means the total number of operations is bounded by `2n`, not `n²`. The same amortized argument as [[02-dynamic-arrays|dynamic array resizing]]: the loop looks nested, but the total work across the whole run is linear.

---

## 6. Related patterns and extensions
<!-- bite: 521aedf6-ea0d-4a74-af43-c3ae46a3365e -->

### Sliding window maximum (harder variant)

Fixed window where the aggregate _isn't_ invertible, so it needs a [[06-monotonic-stack|monotonic]] deque instead of the add-one-drop-one update:

```python
def sliding_window_maximum(nums, k):
    from collections import deque
    dq = deque()  # stores indices, values decreasing
    result = []
    for i, num in enumerate(nums):
        # remove indices out of window
        while dq and dq[0] < i - k + 1:
            dq.popleft()
        # maintain decreasing order
        while dq and nums[dq[-1]] <= num:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
```

### Minimum window substring (harder variant)

```python
def min_window_substring(s, t):
    from collections import Counter
    need = Counter(t)
    missing = len(t)
    left = 0
    min_len = float('inf')
    min_start = 0
    for right, ch in enumerate(s):
        if ch in need:
            if need[ch] > 0:
                missing -= 1
            need[ch] -= 1
        while missing == 0:  # window satisfies t
            if right - left + 1 < min_len:
                min_len = right - left + 1
                min_start = left
            left_ch = s[left]
            if left_ch in need:
                need[left_ch] += 1
                if need[left_ch] > 0:
                    missing += 1
            left += 1
    return s[min_start:min_start + min_len] if min_len != float('inf') else ""
```

---

## 7. Tradeoffs and limitations
<!-- bite: 09b641f0-afd1-46ca-b4b4-2b4f0d4c0746 -->

- **Fixed-size windows only work for invertible operations.** The add-one-drop-one update assumes you can compute the new sum from the old sum, the new element, and the element that fell out. For non-invertible aggregates (max, min, median), you need a different data structure (deque, heap, etc.).
- **Variable-size windows need careful condition handling.** The `while` loop inside the `for` can be confusing; understanding why it's still O(n) is key.
- **Not all contiguous subarray problems fit this pattern.** Some problems require checking every possible window (e.g., "find all subarrays with sum equals k") — prefix sums are better there.

---

## Check your understanding
<!-- bite: a9456f03-38bc-4b69-b915-b22ee240162b -->

Try each one before you open the answer.

1. <!-- q: mcq id="7d40f32b" -->
   A fixed-size window of size k slides one step right, so nums[i] enters and nums[i − k] leaves. How is the window sum updated?

   - [ ] Re-add all k elements
   - [x] window_sum += nums[i] − nums[i − k]
   - [ ] window_sum −= nums[i] + nums[i − k]
   - [ ] window_sum = max(window_sum, nums[i])

   <details><summary>Answer</summary>

   Add the new element and take off the one that fell out. That is O(1) per step instead of O(k).

   </details>

2. <!-- q: mcq id="d6961e56" -->
   In the variable-size window for "longest substring without repeating characters", when does the left edge move?

   - [ ] After every step of the right edge
   - [x] While the new character is already in the window
   - [ ] Only when the window reaches size k
   - [ ] Never; only the right edge moves

   <details><summary>Answer</summary>

   The window shrinks from the left while the rule is broken, here while s[right] is already in the set. Then it adds s[right] and records the length.

   </details>

3. <!-- q: mcq id="c7e9421a" -->
   The variable-size window has a while loop inside a for loop. What is its total running time on n elements?

   - [x] O(n)
   - [ ] O(n log n)
   - [ ] O(n²)
   - [ ] O(n · k)

   <details><summary>Answer</summary>

   O(n). Each element is added to the window at most once and removed at most once, so the total work is at most about 2n steps.

   </details>

4. <!-- q: mcq id="ebf6b177" -->
   Which window values can NOT be kept up to date by "add the new one, take off the old one"? Choose all that apply.

   - [ ] Sum
   - [x] Maximum
   - [x] Minimum
   - [ ] Count of odd numbers

   <details><summary>Answer</summary>

   Max and min. When the old maximum leaves, you can't work out the new one from the old value, so these need a monotonic deque or a heap.

   </details>

5. <!-- q: open id="c1dfa65c" -->
   Why does a fixed-size window still work when the array has negative numbers, while a variable-size "shrink when the sum is too big" window does not?

   <details><summary>Answer</summary>

   The fixed window never decides when to move; it always adds one and drops one, and that sum update is true for any numbers. The variable window shrinks because it assumes adding elements only makes the sum bigger. A negative number breaks that, so shrinking can throw away a window that would have worked.

   </details>

## Check your understanding: worked problems
<!-- bite: 53db191a-bd8a-4bb6-ba32-d1e597fd8430 -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="520c31af" answers="6;8;7;9" -->
   Fill in the gaps. Slide a window of size k = 3 across nums = [4, −1, 3, 6, −2, 5]. The four window sums, left to right, are ___, ___, ___ and ___.

   <details><summary>Answer</summary>

   6, 8, 7, 9. Start with 4 − 1 + 3 = 6. Then 6 − 4 + 6 = 8, 8 − (−1) + (−2) = 7, and 7 − 3 + 5 = 9. The best is 9.

   </details>

2. <!-- q: exact id="223a9dd9" answer="6" -->
   What is the length of the longest substring of "abcbdeafb" with no repeated letter? Use the variable-size window.

   <details><summary>Answer</summary>

   6, for "cbdeaf". When the second b arrives the left edge jumps past the first b, and the window then grows until the last b repeats.

   </details>

3. <!-- q: gap id="25c99677" answers="12;12;12;8;8" -->
   Fill in the gaps. Sliding window maximum with k = 3 on nums = [4, 2, 12, 3, 8, 1, 7]. The five window maxima, left to right, are ___, ___, ___, ___, ___.

   <details><summary>Answer</summary>

   12, 12, 12, 8, 8. The windows are [4,2,12], [2,12,3], [12,3,8], [3,8,1] and [8,1,7]. The deque keeps 12 at the front until it leaves the window.

   </details>

4. <!-- q: exact id="e0a1e9ff" answer="4" -->
   Minimum window substring: s = "CABWEFGEWCWAEFGCF" and t = "CAE". How long is the shortest run of s that contains C, A and E?

   <details><summary>Answer</summary>

   4, for "CWAE". The window grows until it holds all three letters, then shrinks from the left as far as it can, recording the shortest length seen.

   </details>

## 9. Practice — independent task
<!-- bite: 50341160-e010-4533-82a6-735e5f6ab90a -->

**Task:** Implement a function `longest_substring_without_repeating(s)` that returns the length of the longest substring without repeating characters. Use the variable-size sliding window pattern. Test it with the following cases:

- `s = "abcabcbb"` → expected `3` (substring "abc")
- `s = "bbbbb"` → expected `1` (substring "b")
- `s = "pwwkew"` → expected `3` (substring "wke")

**Done when:** your function returns the correct lengths for all test cases.

---

## Practice problems
<!-- bite: 3e56e5cc-cd30-4dd5-ab15-19561793fe70 -->

**In the [[dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[015-best-time-to-buy-and-sell-stock|Best Time to Buy and Sell Stock]] (LeetCode #121) — the degenerate window: track the minimum so far.
2. [[016-longest-substring-without-repeating-characters|Longest Substring Without Repeating Characters]] (LeetCode #3) — grow on the right, shrink from the left the moment a repeat appears.
3. [[017-longest-repeating-character-replacement|Longest Repeating Character Replacement]] (LeetCode #424) — the window is valid while length minus the most frequent count is at most $k$.
4. [[018-permutation-in-string|Permutation in String]] (LeetCode #567) — a fixed-size window and a character-count comparison.
5. [[019-minimum-window-substring|Minimum Window Substring]] (LeetCode #76) — the hardest of the family: expand to satisfy, then contract to minimise.
6. [[020-sliding-window-maximum|Sliding Window Maximum]] (LeetCode #239) — a monotonic **deque** — where this pattern meets [[06-monotonic-stack|monotonic-stack]].

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they drill the window-validity predicate, which is the part that generalises:

7. Minimum Size Subarray Sum (#209) — variable window on a numeric constraint; the cleanest drill of the pattern.
8. Find All Anagrams in a String (#438) — fixed window, same counting as #567.
9. Max Consecutive Ones III (#1004) — "at most $k$ zeros" is a window-validity predicate.
10. Longest Substring with At Most K Distinct Characters (#340) — the general form the others specialise.
11. Maximum Number of Vowels in a Substring of Given Length (#1456) — fixed window, minimal distraction.

## Before moving on
<!-- bite: bf68ca85-460f-4101-aebf-4b640fcd8a91 -->

You are done with this pattern when you can, closed-book:

- [ ] Distinguish a fixed-size from a variable-size window and say when each applies.
- [ ] Explain the amortised O(n) argument despite the nested-looking `while` inside a `for`.
- [ ] Implement longest-substring-without-repeats independently.
- [ ] State which aggregates a fixed window can update in O(1), and which cannot.

**Recap:** A sliding window maintains a summary of a contiguous range and updates it incrementally as the range moves, turning O(n·k) recomputation into O(n). Fixed windows add the entering element and subtract the leaving one, which requires an invertible aggregate; variable windows grow the right edge and shrink the left when a constraint breaks. Each element enters and leaves at most once, which is the amortisation.

**Next:** [[04-fast-slow-pointers|fast-slow-pointers]] — two pointers moving at *different speeds* over the same structure — the third way to arrange the same two-index idea.

## 10. Related
<!-- bite: 1608f8cd-f724-4e25-a26c-a7e69e539c9a -->

- [[02-two-pointers|two-pointers]] — sliding window is a specialization where both pointers move in the same direction
- [[03-hash-maps|hash maps]] — used in variable-size windows for fast membership testing
- [[06-monotonic-stack|monotonic-stack]] — alternative for sliding window maximum
- [[01-growth-and-asymptotic-notation|algorithms]] — where the amortized O(n) framing comes from
- [[03-sliding-window|sliding-window]] — this note

---

## 11. Further reading
<!-- bite: 7764e625-3074-4b58-93b3-9e2338cb9dbb -->

The pattern appears in many contexts beyond LeetCode:

- **Time series analysis:** moving averages, rolling statistics
- **Network traffic monitoring:** bandwidth usage over sliding time windows
- **Genomics:** sliding window alignment in sequence analysis
- **Financial engineering:** risk calculations over rolling periods

The core idea — maintain a summary of the current window and update it incrementally — is a fundamental algorithmic technique that appears whenever you need to process data in chunks that slide across a larger dataset.

## About this lesson
<!-- bite: 6f9dc048-a7ba-4966-aa2a-83e9c62dea88 -->

**Level:** Intermediate. **Covers:** A university-level introduction to the sliding-window pattern: what it is, why it exists, how it works, and how to implement it independently.
