---
id: 7c08c550-6fca-4f0c-a064-2c8c416af9f7
---

# Pattern: Backtracking

Backtracking is solving a problem by building an answer one choice at a time, and undoing the last choice as soon as it leads to a dead end.

## Before you start
<!-- bite: b3231de8-fb76-4123-9aef-bb65a95fdd48 -->

- You should understand DFS. See [[01-depth-first-search|dfs]] if needed.
- You should understand recursion. See [[languages/06-python/04-functions-and-scope|Python functions and scope]] if needed.

**What you will be able to do after this lesson:**

1. Define the backtracking pattern and explain why it's DFS with an explicit "undo" step.
2. Implement backtracking to generate all valid combinations/permutations/subsets.
3. Apply the pattern to related problems like permutations, subsets, and N-Queens.
4. Explain the difference between backtracking and plain DFS.

**Study route:** read the motivation and mechanism first, trace the worked example by hand, then attempt the independent task before looking at the hints.

## What backtracking is
<!-- bite: bba76282-417a-4686-a3b7-61270a09c379 -->

Backtracking builds an answer step by step and steps back whenever a choice goes wrong. It tries every possibility without wasting time on ones that are already wrong. Solving a Sudoku by pencilling in a number and rubbing it out when it breaks a rule is backtracking.

---

## 1. Why this pattern exists (real-world motivation)
<!-- bite: 30162ac3-1134-47a3-b939-3e7734f3a0d5 -->

Imagine you're solving a Sudoku puzzle. You fill in a number, check if it's valid, and if it is, you move to the next cell. If you reach a dead end (no valid number for a cell), you undo your last choice and try a different number. This is exactly what backtracking does: explore every possible choice at each step, and the moment a choice leads somewhere invalid (or you've fully explored it), undo it and try the next option.

Backtracking is DFS with one addition: an explicit "undo" step after each recursive call returns, so the same shared state (a path, a partial solution) can be reused across branches instead of being copied.

---

## 2. Definitions and terminology
<!-- bite: 558d0923-1951-4daf-a01c-c26847d5ef12 -->

| Term             | Plain-English definition                                                             | Example / analogy                                                 |
| ---------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| **Backtracking** | Explore every possible choice, undo invalid choices, try the next option             | Solving a Sudoku puzzle by trying numbers and undoing when stuck  |
| **DFS**          | Depth-first search: explore as far as possible along each branch before backtracking | Exploring a maze by going as deep as possible before backtracking |
| **Pruning**      | Cutting off branches that can't lead to a valid solution                             | Eliminating invalid Sudoku placements early                       |
| **State**        | The current configuration of the solution being built                                | The current board state in Sudoku                                 |

---

## 3. How it works — step by step
<!-- bite: b12d4d95-c0f9-4cf2-8038-674b17000f64 -->

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

## 3. How it works: example, permutations
<!-- bite: a77dc213-4506-465d-b596-c65df3d7c525 -->

The first example lists every order of a few numbers.

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

## 3. How it works: the permutation search as a tree
<!-- bite: 632b0646-c38c-4c78-9f93-14770cd2d56e -->

Here is the whole search for nums = [1, 2, 3] as a tree. Going down an edge is `path.append`; coming back up is `path.pop()`. The search walks it left to right and records each green leaf.

![The decision tree for permutations of 1, 2, 3: the empty path at the top branches into choose 1, 2 or 3; each of those branches into the two numbers left, then the last one; the six green leaves are recorded in order: 1 2 3, 1 3 2, 2 1 3, 2 3 1, 3 1 2, 3 2 1.](../images/pat-backtrack-permutations.svg)

Every branch shares the same `path` list — it's mutated forward on the way down and unmutated on the way back up, which is why this is asymptotically cheaper than rebuilding a new list at every recursive call.

## 3. How it works: why "record a copy" matters
<!-- bite: 939b0b05-6c7f-4108-b509-1e2e71053bdb -->

One small detail in the code decides whether the results come out right.

`result.append(path[:])`, not `result.append(path)` — since `path` is the same mutable list object being reused across the whole search, appending a reference to it (instead of a copy) means every entry in `result` would end up pointing at the same, now-empty-again list once backtracking finishes. This is a direct instance of the reference-type aliasing trap covered in [[programming-fundamentals/15-how-types-actually-work|data-type-classification]].

---

## 4. Implementation — complete runnable example
<!-- bite: b75f1b76-e2cd-49a0-84fa-f7abdb7514f4 -->

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

## Backtracking lab: what it prints
<!-- bite: 3510aaa6-685d-48b1-8851-2b935c8aab2a -->

When you run the lab, this is what it prints.

Expected output:

```text
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
<!-- bite: f4663331-d9fe-42ac-8ac4-34efb32e3f55 -->

Typically exponential ($O(n!)$ for permutations, $O(2^n)$ for subsets) — this is inherent to enumerating every valid arrangement, not a sign of an inefficient implementation. The main lever for speeding up backtracking in practice is **pruning**: checking `is_valid` early to cut off whole invalid branches before recursing into them (this is the entire trick behind solving N-Queens efficiently — reject a queen placement immediately instead of completing the board and checking at the end).

---

## 6. Tradeoffs and limitations
<!-- bite: 653b02e8-842b-4f3f-a4fd-8b4896b67938 -->

- **Exponential time.** Backtracking is inherently exponential for enumeration problems. Pruning helps, but worst-case complexity is still exponential.
- **Recursion depth.** For large inputs, the recursive backtracking may hit Python's recursion limit. Use an iterative approach with an explicit stack instead.
- **State management.** The "undo" step is crucial. Forgetting to undo a choice is a common bug that leads to incorrect results.

---

## Check your understanding
<!-- bite: e49873dc-e18b-449d-933c-c31ca34a9641 -->

Try each one before you open the answer.

1. <!-- q: mcq id="93362626" -->
   In the backtracking template, what does `path.pop()` after the recursive call do?

   - [ ] Records the finished answer
   - [x] Undoes the last choice so the next sibling branch starts from the right state
   - [ ] Ends the search
   - [ ] Removes duplicates

   <details><summary>Answer</summary>

   It undoes the choice. One path list is shared by every branch, so each choice must be taken back before trying the next one.

   </details>

2. <!-- q: mcq id="13a020e3" -->
   Why record a finished answer with `result.append(path[:])` and not `result.append(path)`?

   - [ ] path[:] is faster
   - [x] path is one shared list that keeps changing; without a copy every entry ends up pointing at the same, finally empty, list
   - [ ] path[:] sorts the list
   - [ ] append(path) raises an error

   <details><summary>Answer</summary>

   Lists are stored by reference. Appending path itself would save the same list object many times, and backtracking empties it by the end.

   </details>

3. <!-- q: gap id="f47ebbbd" answers="24;32" -->
   Fill in the gaps. Backtracking makes ___ permutations of 4 different items and ___ subsets of 5 different items (counting the empty one).

   <details><summary>Answer</summary>

   4! = 24 permutations and 2⁵ = 32 subsets. These counts are why backtracking is exponential.

   </details>

4. <!-- q: mcq id="2b6e7958" -->
   In N-Queens, the code checks is_valid before placing a queen instead of filling the board and checking at the end. What is this called?

   - [ ] Memoisation
   - [x] Pruning
   - [ ] Tabulation
   - [ ] Level-order search

   <details><summary>Answer</summary>

   Pruning: cutting off a branch as soon as it can't lead to a valid answer, so none of the boards below it are ever built.

   </details>

5. <!-- q: open id="7802744a" -->
   What is the difference between plain DFS and backtracking?

   <details><summary>Answer</summary>

   Backtracking is DFS over choices with an explicit undo step. Plain DFS visits nodes and marks them; backtracking makes a choice, explores everything after it, then takes the choice back so the same shared state can be reused for the next option.

   </details>

## Check your understanding: worked problems
<!-- bite: b89a4a86-e5aa-415a-8e5f-1b566224342b -->

Work each one out on paper first, then type your answer.

1. <!-- q: gap id="f8657f59" answers="a;b;c;d;a;d" -->
   Fill in the gaps. This code records subsets in the order it finds them:

   ```python
   def subsets(nums):
       result = []
       def backtrack(start, path):
           result.append(path[:])
           for i in range(start, len(nums)):
               path.append(nums[i])
               backtrack(i + 1, path)
               path.pop()
       backtrack(0, [])
       return result
   ```

   For nums = ['a', 'b', 'c', 'd'], the 5th subset recorded is [___, ___, ___, ___] and the 9th is [___, ___].

   <details><summary>Answer</summary>

   5th is [a, b, c, d] and 9th is [a, d]. The order runs [], [a], [a,b], [a,b,c], [a,b,c,d], [a,b,d], [a,c], [a,c,d], [a,d], …

   </details>

2. <!-- q: gap id="84fdee6e" answers="2;3;4;1" -->
   Fill in the gaps. This code records permutations in the order it finds them:

   ```python
   def permute(nums):
       result = []
       def backtrack(path, remaining):
           if not remaining:
               result.append(path[:])
               return
           for i in range(len(remaining)):
               path.append(remaining[i])
               backtrack(path, remaining[:i] + remaining[i+1:])
               path.pop()
       backtrack([], nums)
       return result
   ```

   For nums = [1, 2, 3, 4], the 10th permutation recorded is [___, ___, ___, ___].

   <details><summary>Answer</summary>

   [2, 3, 4, 1]. The first 6 start with 1. Starting with 2 they go [2,1,3,4], [2,1,4,3], [2,3,1,4], [2,3,4,1], which is the 10th.

   </details>

3. <!-- q: gap id="16a8c018" answers="10;4" -->
   Fill in the gaps. N-Queens places n queens on an n × n board so no two share a row, column or diagonal. There are ___ solutions for n = 5 and ___ solutions for n = 6.

   <details><summary>Answer</summary>

   10 and 4. More squares doesn't mean more solutions: the 6 × 6 board is tighter than the 5 × 5.

   </details>

4. <!-- q: exact id="fa10ffea" answer="2" -->
   Generate every subset of [2, 3, 5, 6, 8] with backtracking. How many of them add up to exactly 10?

   <details><summary>Answer</summary>

   2: [2, 3, 5] and [2, 8].

   </details>

5. <!-- q: sketch id="d37c4a74" -->
   Run the subsets code from the lab on nums = [7, 8, 9]. It records `path` at the start of every call, then loops i from `start`, appends nums[i], recurses with i + 1, and pops. On paper, draw the recursion tree: one box per call showing its path, an edge for each "add" choice, and next to each box the order in which it was recorded.

   <details><summary>Answer</summary>

   ![The subsets recursion tree for 7, 8, 9: the empty set at the root (record 1) with children add 7, add 8 and add 9; under 7 come 7 8 (record 3, with child 7 8 9 as record 4) and 7 9 (record 5); under 8 comes 8 9 (record 7); 7 is record 2, 8 is record 6 and 9 is record 8.](../images/pat-backtrack-subsets-answer.svg)

   What to check:
   - There are 8 boxes, one for every subset, and every box is recorded, not just the leaves.
   - A box only adds numbers to the right of its last one, so there is no [8, 7] or [9, 8].
   - The record order is [], [7], [7, 8], [7, 8, 9], [7, 9], [8], [8, 9], [9].

   </details>

## 8. Practice — independent task
<!-- bite: 9d2dc0e4-a446-49be-baca-1f4f89b7aa0a -->

**Task:** Implement a function `combination_sum(candidates, target)` that returns all unique combinations of `candidates` where the chosen numbers sum to `target`. Each number in `candidates` may be used unlimited times. Use the backtracking pattern. Test it with the following cases:

- `candidates = [2, 3, 6, 7], target = 7` → expected `[[2, 2, 3], [7]]`
- `candidates = [2, 3, 5], target = 8` → expected `[[2, 2, 2, 2], [2, 3, 3], [3, 5]]`

**Done when:** your function returns the correct combinations for both test cases.

---

## Practice problems
<!-- bite: 8c975447-49d7-4393-8cbb-36c6606af512 -->

**In the [[dsa/neetcode-150/index|NeetCode 150]]** — solved and written up here:

1. [[071-subsets|Subsets]] (LeetCode #78) — include or exclude — the template for the whole family.
2. [[074-subsets-ii|Subsets II]] (LeetCode #90) — sort, then skip duplicate siblings: the standard duplicate fix.
3. [[072-combination-sum|Combination Sum]] (LeetCode #39) — reuse allowed, so recurse on the *same* index.
4. [[075-combination-sum-ii|Combination Sum II]] (LeetCode #40) — each element once, duplicates skipped — compare carefully with #39.
5. [[073-permutations|Permutations]] (LeetCode #46) — order matters; swap in place, or track a used set.
## Practice problems: harder backtracking in the NeetCode 150
<!-- bite: e4b39290-1827-4a95-be3c-e7178d218a9a -->

These six from the same list add pruning, grids and tries.

6. [[024-generate-parentheses|Generate Parentheses]] (LeetCode #22) — the constraint prunes the tree, which is the whole point of backtracking over brute force.
7. [[076-word-search|Word Search]] (LeetCode #79) — backtracking on a grid; undo the visited mark as you return.
8. [[077-palindrome-partitioning|Palindrome Partitioning]] (LeetCode #131) — cut at every palindromic prefix.
9. [[078-letter-combinations-of-a-phone-number|Letter Combinations of a Phone Number]] (LeetCode #17) — a product, written recursively.
10. [[079-n-queens|N-Queens]] (LeetCode #51) — the classic; column and diagonal sets make the pruning cheap.
11. [[063-word-search-ii|Word Search II]] (LeetCode #212) — a trie plus grid backtracking, where pruning is what makes it feasible at all.

## Practice problems: outside the NeetCode 150
<!-- bite: c181c065-a835-4733-81b8-fb852252bb53 -->

These come straight from LeetCode.

**Not in the NeetCode 150** — worth doing on LeetCode directly, since they give more duplicate-handling and constraint-checking practice:

12. Permutations II (#47) — permutations with duplicates — the sibling-skip again.
13. Combinations (#77) — $n$ choose $k$, the plainest version.
14. Combination Sum III (#216) — fixed size and fixed sum together.
15. Restore IP Addresses (#93) — backtracking with a validity constraint at every cut.
16. Sudoku Solver (#37) — constraint propagation plus backtracking.
17. N-Queens II (#52) — count only — a good check that your pruning is right.

## Before moving on
<!-- bite: 905ba819-568d-4694-b1c3-b4f029ac17ea -->

You are done with this pattern when you can, closed-book:

- [ ] Explain what distinguishes backtracking from plain DFS.
- [ ] State why the undo step is essential and what happens without it.
- [ ] Generate all subsets or permutations independently.
- [ ] Add one pruning condition and explain what it saves.

**Recap:** Backtracking is DFS over a space of partial solutions, with an explicit undo after each branch so the shared state is restored. The choose–explore–unchoose shape is the whole pattern. Complexity is exponential by nature, so pruning — abandoning a branch that provably cannot succeed — is what makes it usable.

**Next:** [[15-dynamic-programming|dynamic-programming]] — what to do when the recursion tree repeats the same subproblem, which is exactly when backtracking becomes unaffordable.

## 9. Related
<!-- bite: 2e2ff2ce-a94d-4241-8040-5257db620267 -->

- [[11-dfs-pattern|dfs-pattern]] — DFS as a problem-solving pattern
- [[01-growth-and-asymptotic-notation|algorithms]] — exponential complexity classes
- [[programming-fundamentals/15-how-types-actually-work|data-type-classification]] — why copying matters when recording a mutable path
- [[14-backtracking|backtracking]] — this note

---

## 10. Further reading
<!-- bite: 96bf67cc-eb9d-4633-a9be-3909b9d95fe5 -->

The pattern appears in many contexts beyond LeetCode:

- **Constraint satisfaction:** Solving Sudoku, crossword puzzles
- **Combinatorial optimization:** Finding optimal arrangements
- **Game AI:** Exploring game trees with alpha-beta pruning
- **Cryptography:** Breaking codes by trying all possible keys

The core idea — explore every possible choice, undo invalid choices, try the next option — is a fundamental algorithmic technique that appears whenever you need to find all valid arrangements that satisfy some constraint.

## About this lesson
<!-- bite: f515790c-70bc-440d-ab8b-e003ecefe15f -->

**Level:** Advanced. **Covers:** A university-level introduction to the backtracking pattern: what it is, why it exists, how it works, and how to implement it independently.
