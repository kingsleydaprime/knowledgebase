# Pattern: Backtracking

Explore every possible choice at each step, and the moment a choice leads somewhere invalid (or you've fully explored it), undo it and try the next option. It's [[02-dfs|DFS]] with one addition: an explicit "undo" step after each recursive call returns, so the same shared state (a path, a partial solution) can be reused across branches instead of being copied.

## When to use it

Generating **all** valid combinations/permutations/subsets/arrangements that satisfy some constraint — anywhere the answer isn't "find one solution" but "find every solution" (or "does any solution exist," explored the same way but stopping early on the first hit).

## The template

```python
def backtrack(path, choices):
    if is_complete(path):
        record(path)
        return
    for choice in choices:
        if not is_valid(choice, path):
            continue
        path.append(choice)          # make the choice
        backtrack(path, next_choices(choices, choice))
        path.pop()                    # undo the choice — this is the "backtrack"
```

That `path.pop()` after the recursive call is the entire idea — without it, `path` would keep accumulating across sibling branches that have nothing to do with each other.

## Example — permutations

```python
def permute(nums):
    result = []
    def backtrack(path, remaining):
        if not remaining:
            result.append(path[:])          # copy — path keeps mutating after this
            return
        for i in range(len(remaining)):
            path.append(remaining[i])
            backtrack(path, remaining[:i] + remaining[i+1:])
            path.pop()                        # undo before trying the next i
    backtrack([], nums)
    return result
```

```
nums = [1, 2, 3]

choose 1 -> path=[1]
  choose 2 -> path=[1,2]
    choose 3 -> path=[1,2,3] -> complete, record
    -> pop back to path=[1,2] -> no more choices -> pop to path=[1]
  choose 3 -> path=[1,3]
    choose 2 -> path=[1,3,2] -> complete, record
    ...
```

Every branch shares the same `path` list — it's mutated forward on the way down and unmutated on the way back up, which is why this is asymptotically cheaper than rebuilding a new list at every recursive call.

## Why "record a copy" matters

`result.append(path[:])`, not `result.append(path)` — since `path` is the same mutable list object being reused across the whole search, appending a reference to it (instead of a copy) means every entry in `result` would end up pointing at the same, now-empty-again list once backtracking finishes. This is a direct instance of the reference-type aliasing trap covered in [[foundations/programming-fundamentals/15-how-types-actually-work|data-type-classification]].

## Complexity

Typically exponential (O(n!) for permutations, O(2ⁿ) for subsets) — this is inherent to enumerating every valid arrangement, not a sign of an inefficient implementation. The main lever for speeding up backtracking in practice is **pruning**: checking `is_valid` early to cut off whole invalid branches before recursing into them (this is the entire trick behind solving N-Queens efficiently — reject a queen placement immediately instead of completing the board and checking at the end).

## Practice problems

All three are written up in the [[foundations/dsa/neetcode-150/README|NeetCode 150]]:

1. [[073-permutations|Permutations]] (LeetCode #46)
2. [[071-subsets|Subsets]] (LeetCode #78)
3. [[079-n-queens|N-Queens]] (LeetCode #51) — pruning is the whole game here

Then the duplicate-handling variants, also in the 150, which is where most backtracking bugs actually live: [[072-combination-sum|Combination Sum]] (#39), [[074-subsets-ii|Subsets II]] (#90), and [[075-combination-sum-ii|Combination Sum II]] (#40).

## Related
- [[11-dfs-pattern|dfs-pattern]]
- [[01-algorithms|algorithms]] — exponential complexity classes
- [[foundations/programming-fundamentals/15-how-types-actually-work|data-type-classification]] — why copying matters when recording a mutable path
