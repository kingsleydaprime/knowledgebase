# Product of Array Except Self

**LeetCode 238** · Arrays & Hashing · concept: [[01-prefix-sum|prefix-sum]]

## Problem

Given `nums`, return `answer` where `answer[i]` is the product of **every element except** `nums[i]`. You must do it **without division** and in **O(n)** time.

```
nums = [1, 2, 3, 4]  ->  [24, 12, 8, 6]
       answer[0] = 2*3*4 = 24, answer[1] = 1*3*4 = 12, ...
```

## Why the obvious answers are banned

- **Divide the total product by `nums[i]`** — O(n), but division is disallowed (and it blows up on a zero in the array).
- **Nested loop** multiplying all others for each i — O(n²), too slow.

The constraint "no division, O(n)" is a hint pointing straight at prefix/suffix products.

## The idea — prefix × suffix

The product of everything except `i` is (product of everything **to the left** of `i`) × (product of everything **to the right** of `i`). Precompute both directions in linear passes.

```python
def productExceptSelf(nums):
    n = len(nums)
    answer = [1] * n

    prefix = 1                      # product of everything left of i
    for i in range(n):
        answer[i] = prefix          # left product goes in first
        prefix *= nums[i]

    suffix = 1                      # product of everything right of i
    for i in range(n - 1, -1, -1):
        answer[i] *= suffix         # multiply in the right product
        suffix *= nums[i]

    return answer
```

**Walkthrough** for `[1,2,3,4]`:

```
after left pass:  answer = [1, 1, 2, 6]     (prefix products)
after right pass: answer = [24, 12, 8, 6]   (× suffix products)
```

## The O(1) extra-space trick

The output array doesn't count against space. Instead of a separate `suffix` array, carry the running suffix product in a **single variable** and fold it into `answer` on the second pass (as above). So beyond the required output, space is **O(1)**.

## Complexity

| | Time | Space (excl. output) |
|---|---|---|
| This solution | **O(n)** | **O(1)** |

Two linear passes, one running variable each.

## Key insight

**"Combine information from the left and the right of each index" → prefix and suffix accumulations.** This is the multiplicative sibling of [[01-prefix-sum|prefix sums]]: precompute directional aggregates so each position is answered in O(1). The same left-meets-right structure underlies *Trapping Rain Water* (left/right max walls) and many range problems — recognizing it is the transferable skill here.

## Related
- concept: [[01-prefix-sum|prefix-sum]]
- prev: [[006-encode-and-decode-strings|Encode and Decode Strings]] · next: [[008-valid-sudoku|Valid Sudoku]]
