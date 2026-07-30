# Maximum Slice Problem (Kadane's Algorithm)

> Added after reviewing Codility's own course PDFs in `pdfs/` (Chapter 9, `7-MaxSlice.pdf`) — not covered anywhere in this vault. Codility calls this the "maximum slice problem"; it's more widely known as **Kadane's algorithm** — same technique, worth recognizing both names since most other material (LeetCode's "Maximum Subarray," textbooks) uses the latter.

Part of [[foundations/dsa/README|DSA fundamentals]]. **Problem:** given a sequence of integers (which may include negatives), find the contiguous slice (subarray) with the largest possible sum. The empty slice is allowed and counts as sum 0 — so the answer is never negative, even if every element in the array is.

Same shape as [[foundations/dsa/05-algorithms/08-leader-algorithm|leader-algorithm]]: three solutions, each a genuine idea rather than a micro-tweak of the last.

---

## O(n³) — check every slice, sum each one from scratch

```python
def slow_max_slice(A):
    n = len(A)
    result = 0
    for p in range(n):
        for q in range(p, n):
            result = max(result, sum(A[p:q+1]))
    return result
```
O(n²) possible slices, each summed in O(n) — the naive nested-loop-plus-recompute approach.

## O(n²) — stop recomputing sums from scratch

Two ways to the same complexity class:
- **Prefix sums**: precompute `pref[i]` = sum of the first `i` elements once, and any slice's sum becomes `pref[q+1] - pref[p]` — O(1) per slice instead of O(n). See [[foundations/dsa/06-patterns/01-prefix-sum|prefix-sum]] for the general technique this borrows directly.
- **Running sum without precomputing**: for a fixed start `p`, extending the slice by one element (`q` → `q+1`) just adds `A[q+1]` to the running sum you already had — no need to re-sum from `p` every time.
```python
def quadratic_max_slice(A):
    n = len(A)
    result = 0
    for p in range(n):
        running_sum = 0
        for q in range(p, n):
            running_sum += A[q]
            result = max(result, running_sum)
    return result
```
Either way: O(n²), an improvement, but still not the ceiling.

---

## O(n) — Kadane's algorithm: the best slice *ending here* determines the best slice *ending one further*

The actual insight, and the reason this is worth sitting with rather than memorizing: define `max_ending_here` as the largest-sum slice that ends **exactly** at the current position. Moving one position forward, there are only two possibilities — extend the previous best-ending-here slice by one element, or (if that would make things worse than starting fresh) discard everything before and start a brand new slice at the current element alone:

```python
def max_slice(A):
    max_ending_here = max_so_far = 0
    for a in A:
        max_ending_here = max(0, max_ending_here + a)
        max_so_far = max(max_so_far, max_ending_here)
    return max_so_far
```
`max(0, max_ending_here + a)` is the whole trick: if the running slice has gone negative enough that adding the current element still leaves you worse off than an empty slice (sum 0), there is *never* a reason to keep carrying that negative baggage forward — reset to 0 and effectively "start over" from the next element. This is why the empty-slice-allowed framing of the problem matters: it's what makes the reset-to-zero move always valid rather than a special case.

**This is dynamic programming**, even though the code doesn't look like the memoized/tabulated DP you might expect (see [[foundations/dsa/06-patterns/15-dynamic-programming|dynamic-programming]]) — the defining DP shape is exactly here: the answer for position `i` is computed directly from the answer at position `i-1`, with no need to ever re-examine earlier positions again once you've folded their result into `max_ending_here`. One pass, O(n) time, O(1) space — no array of subproblem answers needed because each subproblem only ever depends on the *immediately previous* one, not on all of them.

## Related
- [[foundations/dsa/06-patterns/01-prefix-sum|prefix-sum]] — the O(n²) intermediate step borrows this technique directly
- [[foundations/dsa/06-patterns/15-dynamic-programming|dynamic-programming]] — Kadane's is a minimal, O(1)-space example of the same "build the answer from the previous answer" idea
