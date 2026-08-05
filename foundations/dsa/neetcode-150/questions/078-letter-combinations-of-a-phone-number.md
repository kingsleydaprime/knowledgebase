# Letter Combinations of a Phone Number

**LeetCode 17** · Backtracking · concept: [[14-backtracking|backtracking]]

## Problem

Given digits `2`–`9`, return all letter combinations they could spell (old phone keypad mapping).

```
"23"  ->  ["ad","ae","af","bd","be","bf","cd","ce","cf"]
```

## Approach — backtracking over digit positions (optimal)

Map each digit to its letters, then build strings one digit at a time: for the current digit, try each of its letters and recurse to the next digit. It's a **Cartesian product** expressed as a recursion tree.

```python
def letterCombinations(digits):
    if not digits:
        return []
    keypad = {"2":"abc","3":"def","4":"ghi","5":"jkl",
              "6":"mno","7":"pqrs","8":"tuv","9":"wxyz"}
    res = []
    path = []
    def backtrack(i):
        if i == len(digits):
            res.append("".join(path))
            return
        for ch in keypad[digits[i]]:       # each letter of the current digit
            path.append(ch)
            backtrack(i + 1)               # move to the next digit
            path.pop()
    backtrack(0)
    return res
```

**Time O(4ⁿ · n), space O(n)** recursion (n digits, up to 4 letters each).

## Product as a recursion tree

Each level of recursion fixes one digit's letter; a root-to-leaf path spells one combination. This "one choice per position, recurse to the next position" is the simplest backtracking shape — no pruning, no constraint, just the full product. A good baseline for seeing the skeleton without distractions.

## Key insight

**Cartesian product of choice-sets → backtracking with one level per position.** When every position independently ranges over a fixed set and you want all combinations, the recursion tree *is* the product. Constraints (as in the other backtracking problems) just prune branches of this same tree.

## Related
- concept: [[14-backtracking|backtracking]]
- prev: [[077-palindrome-partitioning|Palindrome Partitioning]] · next: [[079-n-queens|N-Queens]]
