# Pattern: Backtracking

**[Advanced]** — A university-level introduction to the backtracking pattern: what it is, why it exists, how it works, and how to implement it independently.

## Before you start

- You should understand DFS. See [[02-dfs|dfs]] if needed.
- You should understand recursion. See [[languages/06-python/04-functions-and-scope|Python functions and scope]] if needed.

**What you will be able to do after this lesson:**

1. Define the backtracking pattern and explain why it's DFS with an explicit "undo" step.
2. Implement backtracking to generate all valid combinations/permutations/subsets.
3. Apply the pattern to related problems like permutations, subsets, and N-Queens.
4. Explain the difference between backtracking and plain DFS.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

---

## 1. Why this pattern exists (real-world motivation)

Imagine you're solving a Sudoku puzzle. You fill in a number, check if it's valid, and if it is, you move to the next cell. If you reach a dead end (no valid number for a cell), you undo your last choice and try a different number. This is exactly what backtracking does: explore every possible choice at each step, and the moment a choice leads somewhere invalid (or you've fully explored it), undo it and try the next option.

Backtracking is DFS with one addition: an explicit "undo" step after each recursive call returns, so the same shared state (a path, a partial solution) can be reused across branches instead of being copied.

---

## 2. Definitions and terminology

| Term             | Plain-English definition                                                             | Example / analogy                                                 |
| ---------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| **Backtracking** | Explore every possible choice, undo invalid choices, try the next option             | Solving a Sudoku puzzle by trying numbers and undoing when stuck  |
| **DFS**          | Depth-first search: explore as far as possible along each branch before backtracking | Exploring a maze by going as deep as possible before backtracking |
| **Pruning**      | Cutting off branches that can't lead to a valid solution                             | Eliminating invalid Sudoku placements early                       |
| **State**        | The current configuration of the solution being built                                | The current board state in Sudoku                                 |

---

## 3. How it works — step by step

### The template

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

### Example — permutations

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

### Why "record a copy" matters

`result.append(path[:])`, not `result.append(path)` — since `path` is the same mutable list object being reused across the whole search, appending a reference to it (instead of a copy) means every entry in `result` would end up pointing at the same, now-empty-again list once backtracking finishes. This is a direct instance of the reference-type aliasing trap covered in [[foundations/programming-fundamentals/15-how-types-actually-work|data-type-classification]].

---

## 4. Implementation — complete runnable example

**Runnable example:** save as `backtracking_lab.py` and run `python3 backtracking_lab.py`. It uses only Python's standard library and creates no external files.

```python
def permute(nums):
    """Generate all permutations of nums."""
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


def subsets(nums):
    """Generate all subsets of nums."""
    result = []
    def backtrack(start, path):
        result.append(path[:])              # copy current subset
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()                        # undo before trying the next i
    backtrack(0, [])
    return result


def n_queens(n):
    """Solve the N-Queens problem."""
    result = []
    board = [['.'] * n for _ in range(n)]

    def is_valid(row, col):
        # Check column
        for i in range(row):
            if board[i][col] == 'Q':
                return False
        # Check upper-left diagonal
        for i, j in zip(range(row - 1, -1, -1), range(col - 1, -1, -1)):
            if board[i][j] == 'Q':
                return False
        # Check upper-right diagonal
        for i, j in zip(range(row - 1, -1, -1), range(col + 1, n)):
            if board[i][j] == 'Q':
                return False
        return True

    def backtrack(row):
        if row == n:
            result.append([''.join(r) for r in board])
            return
        for col in range(n):
            if is_valid(row, col):
                board[row][col] = 'Q'
                backtrack(row + 1)
                board[row][col] = '.'        # undo the choice

    backtrack(0)
    return result


if __name__ == "__main__":
    # Test case 1: permutations
    nums1 = [1, 2, 3]
    result1 = permute(nums1)
    print(f"Test 1 - permutations:")
    print(f"nums={nums1} -> {result1}")
    assert len(result1) == 6, f"Expected 6 permutations, got {len(result1)}"

    # Test case 2: subsets
    nums2 = [1, 2, 3]
    result2 = subsets(nums2)
    print(f"\nTest 2 - subsets:")
    print(f"nums={nums2} -> {result2}")
    assert len(result2) == 8, f"Expected 8 subsets, got {len(result2)}"

    # Test case 3: N-Queens (n=4)
    result3 = n_queens(4)
    print(f"\nTest 3 - N-Queens (n=4):")
    print(f"n=4 -> {len(result3)} solutions")
    assert len(result3) == 2, f"Expected 2 solutions, got {len(result3)}"

    print("\nbacktracking_lab: passed")
```

Expected output:

```
Test 1 - permutations:
nums=[1, 2, 3] -> [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]

Test 2 - subsets:
nums=[1, 2, 3] -> [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]

Test 3 - N-Queens (n=4):
n=4 -> 2 solutions

backtracking_lab: passed
```

---

## 5. Complexity

Typically exponential (O(n!) for permutations, O(2^n) for subsets) — this is inherent to enumerating every valid arrangement, not a sign of an inefficient implementation. The main lever for speeding up backtracking in practice is **pruning**: checking `is_valid` early to cut off whole invalid branches before recursing into them (this is the entire trick behind solving N-Queens efficiently — reject a queen placement immediately instead of completing the board and checking at the end).

---

## 6. Tradeoffs and limitations

- **Exponential time.** Backtracking is inherently exponential for enumeration problems. Pruning helps, but worst-case complexity is still exponential.
- **Recursion depth.** For large inputs, the recursive backtracking may hit Python's recursion limit. Use an iterative approach with an explicit stack instead.
- **State management.** The "undo" step is crucial. Forgetting to undo a choice is a common bug that leads to incorrect results.

---

## 7. Check your understanding (self-assessment)

Attempt these without the note, then compare your reasoning below.

1. **Question:** Given `nums = [1, 2, 3]`, trace through the permutations backtracking algorithm step by step.
2. **Question:** Why is `result.append(path[:])` used instead of `result.append(path)`?
3. **Question:** What's the difference between backtracking and plain DFS?

### Answers — after your attempt

1. Start with empty path. Choose 1, path=[1]. Choose 2, path=[1,2]. Choose 3, path=[1,2,3] -> complete, record. Pop 3, path=[1,2]. No more choices, pop 2, path=[1]. Choose 3, path=[1,3]. Choose 2, path=[1,3,2] -> complete, record. Pop 2, path=[1,3]. No more choices, pop 3, path=[1]. No more choices, pop 1, path=[]. Choose 2, path=[2]. Choose 1, path=[2,1]. Choose 3, path=[2,1,3] -> complete, record. ... and so on for all 6 permutations.
2. `result.append(path[:])` creates a copy of the current path. If you append `path` directly (a reference), all entries in `result` would point to the same list, which gets modified as backtracking continues. By appending a copy, each entry in `result` is independent.
3. DFS explores all paths/branches of a graph. Backtracking is a specific technique where you explore a choice, undo it, and try the next choice. Backtracking uses DFS as its underlying traversal mechanism, but adds the "undo" step.

---

## 8. Practice — independent task

**Task:** Implement a function `combination_sum(candidates, target)` that returns all unique combinations of `candidates` where the chosen numbers sum to `target`. Each number in `candidates` may be used unlimited times. Use the backtracking pattern. Test it with the following cases:

- `candidates = [2, 3, 6, 7], target = 7` → expected `[[2, 2, 3], [7]]`
- `candidates = [2, 3, 5], target = 8` → expected `[[2, 2, 2, 2], [2, 3, 3], [3, 5]]`

**Done when:** your function returns the correct combinations for both test cases.

---

## Before moving on

You are done with this pattern when you can, closed-book:

- [ ] Explain what distinguishes backtracking from plain DFS.
- [ ] State why the undo step is essential and what happens without it.
- [ ] Generate all subsets or permutations independently.
- [ ] Add one pruning condition and explain what it saves.

**Recap:** Backtracking is DFS over a space of partial solutions, with an explicit undo after each branch so the shared state is restored. The choose–explore–unchoose shape is the whole pattern. Complexity is exponential by nature, so pruning — abandoning a branch that provably cannot succeed — is what makes it usable.

**Next:** [[15-dynamic-programming|dynamic-programming]] — what to do when the recursion tree repeats the same subproblem, which is exactly when backtracking becomes unaffordable.

## 9. Related

- [[11-dfs-pattern|dfs-pattern]] — DFS as a problem-solving pattern
- [[01-algorithms|algorithms]] — exponential complexity classes
- [[foundations/programming-fundamentals/15-how-types-actually-work|data-type-classification]] — why copying matters when recording a mutable path
- [[14-backtracking|backtracking]] — this note

---

## 10. Further reading

The pattern appears in many contexts beyond LeetCode:

- **Constraint satisfaction:** Solving Sudoku, crossword puzzles
- **Combinatorial optimization:** Finding optimal arrangements
- **Game AI:** Exploring game trees with alpha-beta pruning
- **Cryptography:** Breaking codes by trying all possible keys

The core idea — explore every possible choice, undo invalid choices, try the next option — is a fundamental algorithmic technique that appears whenever you need to find all valid arrangements that satisfy some constraint.
