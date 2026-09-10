# Module: Non-Comparison Sorts

**[Intermediate]** — counting, radix and bucket sort, and how they legitimately get under the $\Omega(n\log n)$ bound.

## Before you start

- You know the comparison lower bound and why it applies — [[01-the-lower-bound|the lower bound]].
- You know what stable means — same lesson.

**After this lesson you will be able to:**

1. Implement **counting sort**, and state the condition on the key range that makes it worthwhile.
2. Implement **radix sort**, and explain why it must process digits **least-significant first** and why that requires a stable inner sort.
3. Explain why these do not contradict the lower bound.
4. Choose between them and a comparison sort from the shape of the keys.

**Study route:** read 1–4, attempt the prediction in section 2, then run the lab. Block 3 shows what happens when the inner sort is not stable.

---

## 1. Why this exists

The lower bound says $\Omega(n\log n)$ comparisons. These algorithms sort in $O(n)$, and there is no contradiction — **they never compare two elements**.

Instead they use the key itself as information: as an array index, or as a sequence of digits. That is extra power the decision-tree model does not have. The model assumes the only question you may ask is "is $a < b$?", and these algorithms ask a different question: "what is the value of $a$?"

The cost is a loss of generality. A comparison sort works on anything with an ordering — strings, tuples, custom objects, user-supplied comparators. These need keys that are small non-negative integers, or that can be decomposed into digits.

## 2. Counting sort

For keys in $0..k$:

1. Count occurrences of each key.
2. Turn the counts into a **prefix sum**, so `count[v]` becomes the number of elements $\le v$ — which is the position just past where the $v$s end.
3. Walk the input **backwards**, placing each element at `count[key]-1` and decrementing.

Cost is $O(n + k)$ time and $O(n + k)$ space.

**The condition:** it is worth it when $k$ is $O(n)$. Sorting a million ages ($k=120$) is superb. Sorting a thousand 64-bit integers means $k = 2^{64}$ and an impossible array.

**Why walk backwards?** That is what makes it **stable**. Going backwards places later-occurring equal elements at higher positions, preserving their original order. Forwards, they come out reversed. This matters far more than it looks, because radix sort depends on it.

> [!TIP]
> **Predict before section 3.** Radix sort processes digits one at a time. Would sorting by the **most** significant digit first work just as well as least-significant first? If not, what goes wrong? Decide before opening the answers.

## 3. Radix sort

Counting sort is useless for large key ranges. Radix sort fixes that by sorting on **one digit at a time**, using counting sort for each pass — so $k$ is only the digit base (10, or 256), never the full key range.

**Least significant digit first (LSD):**

```
input:   170 045 075 090 802 024 002 066
by 1s:   170 090 802 002 024 045 075 066
by 10s:  802 002 024 045 066 170 075 090   <- wait, look at 075 and 090
by 100s: 002 024 045 066 075 090 170 802
```

Cost is $O(d(n + b))$ for $d$ digits in base $b$ — linear in $n$ when $d$ is fixed.

**The whole thing rests on stability.** When sorting by the tens digit, two numbers with the same tens digit must stay in the order the units pass left them. A stable inner sort guarantees that; an unstable one destroys the previous pass's work and the final result is simply wrong. Block 3 demonstrates the failure.

**Why least-significant first?** Because it lets each pass build on the last. MSD-first splits into buckets by the top digit, and those buckets must then be sorted *independently and recursively* — which works, and is what you use for variable-length strings, but it is a different, more complex algorithm.

## 4. Bucket sort

Distribute into buckets by value range, sort each bucket (usually with insertion sort), concatenate.

Average $O(n)$ **when the input is uniformly distributed** over the range. That assumption is load-bearing: if everything lands in one bucket you have done a distribution pass and then an $O(n^2)$ insertion sort. Bucket sort is the least robust of the three and the one most dependent on knowing your data.

## Worked example — runnable

**Runnable example:** save as `non_comparison.py` in any empty directory and run `python3 non_comparison.py`. Standard library only; writes no files.

```python
"""Counting, radix and bucket sort - and why radix needs a stable inner sort."""
import random


def counting_sort(xs, k, key=lambda v: v, stable=True):
    """O(n + k). Walk backwards for stability."""
    count = [0] * (k + 1)
    for v in xs:
        count[key(v)] += 1
    for i in range(1, k + 1):
        count[i] += count[i - 1]                 # prefix sums: positions
    out = [None] * len(xs)
    order = reversed(range(len(xs))) if stable else range(len(xs))
    for i in order:
        v = xs[i]
        count[key(v)] -= 1
        out[count[key(v)]] = v
    return out


def radix_sort(xs, base=10, stable_inner=True):
    """LSD radix sort. Each pass MUST be stable or earlier passes are undone."""
    if not xs:
        return []
    passes = 0
    out = list(xs)
    m = max(out)
    exp = 1
    while m // exp > 0:
        out = counting_sort(out, base - 1, key=lambda v: (v // exp) % base,
                            stable=stable_inner)
        exp *= base
        passes += 1
    return out, passes


def bucket_sort(xs, n_buckets=None, value_range=None):
    """value_range fixes the bucket boundaries. Deriving them from the data's own
    min/max would rescale every input to fill the buckets, hiding exactly the
    clustering effect this is meant to show."""
    if not xs:
        return [], []
    n_buckets = n_buckets or len(xs)
    lo, hi = value_range or (min(xs), max(xs))
    span = (hi - lo) or 1
    buckets = [[] for _ in range(n_buckets)]
    for v in xs:
        idx = min(n_buckets - 1, int((v - lo) / span * n_buckets))
        buckets[idx].append(v)
    out = []
    for b in buckets:
        out.extend(sorted(b))                     # insertion sort in practice
    return out, [len(b) for b in buckets]


class Item:
    def __init__(self, key, tag):
        self.key, self.tag = key, tag
    def __repr__(self):
        return f"{self.key}{self.tag}"


if __name__ == "__main__":
    rng = random.Random(20260910)

    print("Block 1 - counting sort, and the condition on k")
    ages = [rng.randint(0, 120) for _ in range(20)]
    print(f"  ages: {ages}")
    print(f"  sorted: {counting_sort(ages, 120)}")
    assert counting_sort(ages, 120) == sorted(ages)
    print("       n        k       n+k    n*log2(n)   counting sort worth it?")
    import math
    for n, k in ((1_000_000, 120), (1000, 1000), (1000, 10 ** 9)):
        worth = (n + k) < n * math.log2(n)
        print(f"  {n:8,} {k:8,} {n+k:9,}   {n*math.log2(n):10,.0f}   {worth}")
    print("  it wins when k is O(n); at k = 10^9 the count array alone is hopeless")

    print()
    print("Block 2 - counting sort is stable only if you walk BACKWARDS")
    items = [Item(1, "a"), Item(0, "b"), Item(1, "c"), Item(0, "d"), Item(1, "e")]
    fwd = counting_sort(items, 1, key=lambda it: it.key, stable=False)
    bwd = counting_sort(items, 1, key=lambda it: it.key, stable=True)
    print(f"  input:              {items}")
    print(f"  forwards  (unstable): {fwd}")
    print(f"  backwards (stable):   {bwd}")
    assert [it.tag for it in bwd if it.key == 1] == ["a", "c", "e"]
    assert [it.tag for it in fwd if it.key == 1] != ["a", "c", "e"]
    print("  going forwards reverses equal elements; backwards preserves them")

    print()
    print("Block 3 - radix sort, and what happens without a stable inner sort")
    data = [170, 45, 75, 90, 802, 24, 2, 66]
    good, passes = radix_sort(list(data), stable_inner=True)
    bad, _ = radix_sort(list(data), stable_inner=False)
    print(f"  input:            {data}")
    print(f"  radix (stable):   {good}   in {passes} passes")
    print(f"  radix (unstable): {bad}   <- WRONG")
    assert good == sorted(data)
    assert bad != sorted(data)
    print("  each pass must preserve the previous pass's ordering of equal digits;")
    print("  an unstable inner sort throws that away and the result is simply not sorted")

    print()
    print("  digit by digit, with a stable inner sort:")
    cur = list(data)
    exp = 1
    while max(data) // exp > 0:
        cur = counting_sort(cur, 9, key=lambda v: (v // exp) % 10)
        print(f"    after the {str(exp).rjust(3)}s pass: {[str(v).zfill(3) for v in cur]}")
        exp *= 10

    print()
    print("Block 4 - radix on a large array, against Python's sort")
    big = [rng.randint(0, 999999) for _ in range(20000)]
    out, passes = radix_sort(list(big))
    assert out == sorted(big)
    print(f"  {len(big):,} six-digit numbers sorted correctly in {passes} passes")
    print(f"  radix does {passes} linear passes; a comparison sort needs about "
          f"{math.log2(len(big)):.0f} levels")
    print(f"  radix touches {passes * len(big):,} elements, "
          f"a comparison sort about {len(big)*math.log2(len(big)):,.0f}")

    print()
    print("Block 5 - bucket sort depends entirely on the distribution")
    uniform = [rng.random() * 1000 for _ in range(10000)]
    clustered = [rng.gauss(500, 3) for _ in range(10000)]
    RANGE = (0, 1000)          # the SAME boundaries for both, so they are comparable
    for label, data in [("uniform  ", uniform), ("clustered", clustered)]:
        out, sizes = bucket_sort(data, n_buckets=100, value_range=RANGE)
        assert out == sorted(data)
        biggest = max(sizes)
        empty = sum(1 for s in sizes if s == 0)
        print(f"  {label}: largest bucket {biggest:6,}   empty buckets {empty:4}"
              f"   ideal {len(data)//100:,}")
    _, sizes_u = bucket_sort(uniform, 100, RANGE)
    _, sizes_c = bucket_sort(clustered, 100, RANGE)
    assert max(sizes_c) > 10 * max(sizes_u)
    print("  clustered data puts almost everything in a few buckets, and the")
    print("  'sort each bucket' step degrades to sorting nearly the whole array")

    print()
    print("non_comparison: passed")
```

Expected output:

```
Block 1 - counting sort, and the condition on k
  ages: [112, 15, 32, 9, 20, 112, 86, 46, 91, 44, 72, 32, 105, 1, 11, 22, 23, 91, 16, 50]
  sorted: [1, 9, 11, 15, 16, 20, 22, 23, 32, 32, 44, 46, 50, 72, 86, 91, 91, 105, 112, 112]
       n        k       n+k    n*log2(n)   counting sort worth it?
  1,000,000      120 1,000,120   19,931,569   True
     1,000    1,000     2,000        9,966   True
     1,000 1,000,000,000 1,000,001,000        9,966   False
  it wins when k is O(n); at k = 10^9 the count array alone is hopeless

Block 2 - counting sort is stable only if you walk BACKWARDS
  input:              [1a, 0b, 1c, 0d, 1e]
  forwards  (unstable): [0d, 0b, 1e, 1c, 1a]
  backwards (stable):   [0b, 0d, 1a, 1c, 1e]
  going forwards reverses equal elements; backwards preserves them

Block 3 - radix sort, and what happens without a stable inner sort
  input:            [170, 45, 75, 90, 802, 24, 2, 66]
  radix (stable):   [2, 24, 45, 66, 75, 90, 170, 802]   in 3 passes
  radix (unstable): [90, 75, 66, 45, 24, 2, 170, 802]   <- WRONG
  each pass must preserve the previous pass's ordering of equal digits;
  an unstable inner sort throws that away and the result is simply not sorted

  digit by digit, with a stable inner sort:
    after the   1s pass: ['170', '090', '802', '002', '024', '045', '075', '066']
    after the  10s pass: ['802', '002', '024', '045', '066', '170', '075', '090']
    after the 100s pass: ['002', '024', '045', '066', '075', '090', '170', '802']

Block 4 - radix on a large array, against Python's sort
  20,000 six-digit numbers sorted correctly in 6 passes
  radix does 6 linear passes; a comparison sort needs about 14 levels
  radix touches 120,000 elements, a comparison sort about 285,754

Block 5 - bucket sort depends entirely on the distribution
  uniform  : largest bucket    122   empty buckets    0   ideal 100
  clustered: largest bucket  4,996   empty buckets   96   ideal 100
  clustered data puts almost everything in a few buckets, and the
  'sort each bucket' step degrades to sorting nearly the whole array

non_comparison: passed
```

Block 3 is the lesson: the same radix sort, with the only difference being whether its inner counting sort walks the input forwards or backwards, and one of them **does not produce a sorted array at all**.

## Common pitfalls and traps

- **Using counting sort with a large key range.** $k = 2^{32}$ means a four-billion-element array. Check that $k$ is $O(n)$ first.
- **An unstable inner sort in radix.** Silently produces wrong output, as block 3 shows. This is the single most important dependency in the algorithm.
- **Walking forwards in counting sort.** Destroys stability, which usually does not matter — until you use it inside radix sort, where it breaks correctness.
- **Assuming bucket sort is $O(n)$.** Only for uniformly distributed input. Clustered data makes it quadratic.
- **Forgetting negative numbers.** Counting sort indexes an array by key, so negatives need an offset. Radix needs sign handling too.
- **Applying these to arbitrary objects.** They need integer keys or digit decompositions. A custom comparator cannot be used.

## Check your understanding

1. Why do these not contradict the $\Omega(n\log n)$ bound?
2. When is counting sort a bad choice?
3. Why must radix sort's inner sort be stable?
4. Why LSD rather than MSD for fixed-width integers?
5. What assumption does bucket sort's $O(n)$ average depend on?

<details><summary>Answers — open only after an attempt</summary>

1. Because the bound applies only to **comparison** sorts. These never compare two elements — they use key values directly as indices or digits, which is information the decision-tree model does not allow.
2. When the key range $k$ is large relative to $n$. Sorting 1,000 arbitrary 32-bit integers would need a count array of four billion entries.
3. Because each pass must preserve the relative order established by the previous, less-significant pass. If two numbers share a tens digit, their relative order must still reflect their units digits. An unstable pass discards that and the final output is not sorted.
4. Because LSD lets each pass build on the last, giving a simple sequence of $d$ stable passes. MSD splits into buckets that must then be sorted independently and recursively — correct but more complex, and worth it mainly for variable-length keys like strings.
5. That the input is roughly **uniformly distributed** across the range, so buckets stay small and balanced. Clustered data puts most elements in a few buckets, and sorting those degrades towards $O(n^2)$.

**And the prediction from section 2:** **no**, MSD-first does not work as a simple sequence of passes. Sorting by the most significant digit first groups correctly at the top level, but a subsequent full-array pass on a lower digit would destroy that grouping. MSD radix sort must instead recurse **within each bucket** independently — a genuinely different algorithm, and the one used for strings of differing lengths.
</details>

## Practice — independent task

Implement `radix_sort_strings(words)` — MSD radix sort for variable-length strings.

1. Bucket by the character at position $d$, using a bucket for "string too short", which must sort **first** (a prefix precedes its extensions: `"go"` before `"gone"`).
2. Recurse into each non-empty bucket at position $d+1$.
3. Switch to insertion sort when a bucket falls below a threshold you choose; justify the threshold.
4. Verify against `sorted(words)` on: a dictionary-like word list; many shared prefixes (`a`, `ab`, `abc`, ...); empty strings; identical strings; mixed case (decide and document your collation).
5. **Compare the work done** against a comparison sort when strings share long prefixes. Comparison sorts re-examine the shared prefix on every comparison; MSD radix examines each character position once. Measure character inspections for both and report the ratio for a list of 10,000 strings sharing a 20-character prefix.

**Edge cases:** the empty list; one string; all strings identical (does your recursion terminate?); non-ASCII characters.

**Done when:** your sort matches `sorted()` on every case, the short-string bucket orders correctly, and your step-5 measurement shows the advantage you predicted for shared prefixes.

## Before moving on

You can implement counting and radix sort, explain their relationship to the lower bound, and say what each requires of the keys.

**Recap:** these avoid the bound by not comparing — they use keys as indices or digits; counting sort is $O(n+k)$, worth it when $k$ is $O(n)$, and stable **only if you walk the input backwards**; radix sort is $O(d(n+b))$ LSD passes and is correct **only** with a stable inner sort; bucket sort is $O(n)$ average **only** for uniformly distributed input.

**Where next:** back to [[index|the sorting index]] for the comparison table, or on to [[05-searching|searching]] — what sorting enables.

## Related

- [[01-the-lower-bound|The Lower Bound]] — the theorem these sidestep
- [[03-merge-sort|Merge Sort]] — where stability is also load-bearing
- [[01-arrays|Arrays]] — the direct indexing these depend on
