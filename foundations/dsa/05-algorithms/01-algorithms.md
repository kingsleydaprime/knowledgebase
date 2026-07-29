# Algorithms

An algorithm is a finite, well-defined sequence of steps that takes an input and produces an output. That's the whole definition — a recipe, a set of driving directions, and quicksort are all algorithms in the same technical sense. What this note is really about is the vocabulary for comparing them: given two different ways to solve the same problem, how do you say which one is "better" without just running both and hoping your test machine is representative?

## Correctness vs efficiency

An algorithm has to be judged on two separate questions:

1. **Does it produce the right answer for every valid input**, including edge cases (empty input, one element, duplicates, already-sorted data)? This comes first — a fast wrong answer is worthless.
2. **How much time and memory does it use as the input grows?** This is what Big-O notation describes.

## Big-O notation

Big-O describes how an algorithm's resource usage (usually time) grows as input size (`n`) grows, ignoring constant factors and lower-order terms. It answers "what happens as n gets huge," not "how many milliseconds does this take on my laptop."

```python
def contains(arr, target):      # O(n)
    for x in arr:                # loop runs up to n times
        if x == target:
            return True
    return False

def first_two(arr):              # O(1)
    return arr[0], arr[1]        # constant work regardless of len(arr)
```

The reason constants get dropped: an O(n) algorithm running `2n` steps and one running `100n` steps are both "O(n)" — because what actually matters as n grows to a million or a billion is the *shape* of the growth curve, not the multiplier. A O(n²) algorithm will eventually lose to an O(n log n) one no matter how large that constant factor gap is, once n is big enough.

## Common complexity classes, smallest to largest

| Notation | Name | Example |
|---|---|---|
| O(1) | Constant | array index access, hash map lookup |
| O(log n) | Logarithmic | binary search, balanced BST operations |
| O(n) | Linear | single loop over the input |
| O(n log n) | Linearithmic | merge sort, quicksort (average) |
| O(n²) | Quadratic | nested loop over the input (bubble sort, naive pair-checking) |
| O(2ⁿ) | Exponential | brute-force subsets, naive recursive Fibonacci |
| O(n!) | Factorial | brute-force permutations |

```
work
 ^                                                    n!
 |                                            2ⁿ
 |                                  n²
 |                        n log n
 |                n
 |        log n
 |1
 +---------------------------------------------------> n
```

## How to actually derive an algorithm's complexity

The practical method: count nested loops/recursive branching relative to the input.

- One loop over `n` items → O(n).
- A loop inside a loop, both over `n` → O(n²).
- Cutting the problem in half each step (and only recursing into one half) → O(log n).
- Recursing into *two* halves at each level, doing O(n) work to combine them (merge sort's merge step) → O(n log n).
- Branching into 2 recursive calls at every step with no reduction in problem size (naive Fibonacci) → O(2ⁿ).

```python
def fib(n):                  # O(2^n) — two recursive calls per call, no memoization
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
```

## Space complexity

The same notation, applied to memory instead of time — how much *extra* space (beyond the input itself) does the algorithm need? Recursive solutions have a hidden space cost: the call stack. A recursive function that recurses `n` deep uses O(n) space on the call stack even if it never explicitly allocates anything — this is why "just make it recursive" isn't free, and it's a common gotcha for [[02-dfs|dfs]] on very deep or unbalanced structures.

## Why worst-case matters more than you'd expect

Big-O is usually quoted as worst-case unless stated otherwise, because average-case can hide real problems — an algorithm that's O(1) on average but O(n) in an adversarial case (a poorly-hashed [[03-hash-maps|hash map]], say) can be exploited or just get unlucky with real input. In interviews specifically, stating "this is O(n) average, O(n²) worst case" is a stronger answer than just "O(n)."

## Gotchas

- Big-O describes growth rate, not actual speed — an O(n²) algorithm can outrun an O(n log n) one for small n, because the constant factors and lower-order terms that Big-O throws away still cost real time at small scale.
- "O(n) space" usually means *extra* space, not counting the input itself — be explicit about which convention you're using.
- Amortized complexity (see [[02-dynamic-arrays|dynamic-arrays]]) is a different concept from average-case complexity — amortized is about cost *spread over a sequence of operations on the same structure*, average-case is about cost across different possible inputs.

## Related
- [[02-dynamic-arrays|dynamic-arrays]] — amortized analysis
- [[02-dfs|dfs]] — recursive space complexity
- [[04-sorting|sorting]] — where O(n log n) vs O(n²) shows up concretely
