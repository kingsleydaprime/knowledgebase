# Generate Parentheses

**LeetCode 22** · Stack / Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Given `n` pairs of parentheses, generate **all** well-formed combinations.

```
n = 3  ->  ["((()))","(()())","(())()","()(())","()()()"]
```

## Approach — backtracking with two counters (optimal)

This is a [[14-backtracking|backtracking]] problem (the "stack" tag is because validity is a bracket-matching property). Build the string one character at a time, maintaining counts of open and close brackets used, and prune illegal branches:

- add `"("` only while `open < n`
- add `")"` only while `close < open` (never close more than you've opened — the validity rule)
- record when the string reaches length `2n`

```python
def generateParenthesis(n):
    res = []
    def backtrack(s, open_count, close_count):
        if len(s) == 2 * n:
            res.append(s)
            return
        if open_count < n:
            backtrack(s + "(", open_count + 1, close_count)
        if close_count < open_count:
            backtrack(s + ")", open_count, close_count + 1)
    backtrack("", 0, 0)
    return res
```

The two `if` guards **prune** invalid prefixes before they're built, so you never generate a string you'd have to discard.

## Complexity

The number of valid strings is the **n-th Catalan number** ≈ 4ⁿ / (n^1.5 √π). Producing each is O(n), so total **O(4ⁿ / √n)** — optimal, since that's the size of the output itself.

## Key insight

**Generate-all-valid-configurations → backtracking with pruning invariants.** The invariant `close < open ≤ n` is what keeps the search inside the space of valid strings instead of generating all 2^(2n) strings and filtering. Encoding validity as guards on the recursion is the transferable skill.

## Related
- concept: [[14-backtracking|backtracking]], [[07-stacks-and-queues|stacks-and-queues]]
- prev: [[023-evaluate-reverse-polish-notation|Evaluate RPN]] · next: [[025-daily-temperatures|Daily Temperatures]]
