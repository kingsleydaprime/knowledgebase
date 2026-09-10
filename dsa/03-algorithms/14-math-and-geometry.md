# Module: Math & Geometry (In-Place Grids & Number Tricks)

Welcome to the **Math & Geometry** module. This module covers problems where the solution hinges on **direct number manipulation or precise grid coordinate reasoning**, often in-place and with arithmetic tricks that eliminate the need for extra memory.

These problems test whether you understand *how computation works*, not just which data structure to reach for.

---

## 1. Real-World Motivation & Physical Metaphors

These techniques power real production systems:

- **Image Processing**: Rotating a photo, applying a blur filter, or zeroing out corrupted pixel regions in-place without allocating a second image buffer.
- **Game Engines**: Scanning a grid in a spiral order to render tiles from center outward. Simulating physics with fast exponentiation.
- **Data Compression & Encryption**: Fast modular exponentiation (`x^n mod m`) powers RSA public-key cryptography and digital signatures.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Analogy |
| :--- | :--- | :--- |
| **In-Place** | Transforming data directly inside the input structure with $O(1)$ extra space (no copy array). | Rearranging books on a shelf without needing a second shelf. |
| **Transposition** | Swapping matrix element `[i][j]` with `[j][i]` across the main diagonal. | Reflecting a chessboard across its diagonal. |
| **Binary Exponentiation** | Computing $x^n$ in $O(\log n)$ by repeatedly squaring instead of multiplying $n$ times. | Folding paper repeatedly (halving problems). |
| **Cycle Detection (Floyd's)** | Using slow/fast pointers on a sequence to detect whether it loops. | Two runners on a circular track—the faster one laps the slower. |

---

## 3. In-Place Matrix Manipulation

### 3.1 Rotate Image (90° Clockwise, In-Place)

**Key Insight**: A 90° clockwise rotation = **Transpose** (swap across main diagonal) **then Reverse each row**.

```python
def rotate_matrix(matrix: list) -> None:
    """Rotates an n×n matrix 90° clockwise IN-PLACE."""
    n = len(matrix)
    
    # Step 1: Transpose - swap matrix[i][j] with matrix[j][i]
    for i in range(n):
        for j in range(i + 1, n):  # Only above the diagonal (avoid double-swap)
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    
    # Step 2: Reverse each row
    for row in matrix:
        row.reverse()
```

**Visualization**:
```
Original:              After Transpose:       After Row Reversal (= 90° CW):
1  2  3                1  4  7               7  4  1
4  5  6    ─────►      2  5  8    ─────►     8  5  2
7  8  9                3  6  9               9  6  3
```

---

### 3.2 Set Matrix Zeroes (O(1) Space Trick)

**Problem**: If any cell `matrix[i][j] == 0`, set its entire row and column to zero.

**Naïve approach**: Store zero-row and zero-column indices in separate arrays → $O(m + n)$ space.

**O(1) Space Trick**: Use the **first row and first column of the matrix itself** as the marker arrays, with two extra booleans for the first row/column's own zero status.

```python
def set_matrix_zeroes(matrix: list) -> None:
    """Sets rows and columns to zero IN-PLACE using O(1) extra space."""
    m, n = len(matrix), len(matrix[0])
    
    # Track whether the first row/column themselves contain zeros
    first_row_has_zero = any(matrix[0][j] == 0 for j in range(n))
    first_col_has_zero = any(matrix[i][0] == 0 for i in range(m))
    
    # Use first row & column as markers for the rest of the matrix
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0   # Mark row i
                matrix[0][j] = 0   # Mark column j
    
    # Apply zeros based on markers (rows and columns, excluding first)
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    
    # Handle first row and first column separately
    if first_row_has_zero:
        for j in range(n): matrix[0][j] = 0
    if first_col_has_zero:
        for i in range(m): matrix[i][0] = 0
```

---

### 3.3 Spiral Matrix (Shrinking Boundary Walk)

**Strategy**: Maintain four shrinking boundaries (`top`, `bottom`, `left`, `right`). Peel off one edge per direction in rotation, moving each boundary inward after processing:

```python
def spiral_order(matrix: list) -> list:
    """Returns all elements of a matrix in spiral (clockwise) order."""
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # → Right (top row, left to right)
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1
        
        # ↓ Down (right column, top to bottom)
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1
        
        # ← Left (bottom row, right to left) — only if rows remain
        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1
        
        # ↑ Up (left column, bottom to top) — only if columns remain
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1
    
    return result
```

---

## 4. Number Tricks

### 4.1 Fast Power (`Pow(x, n)`) — Binary Exponentiation

**Naïve**: Multiply `x` by itself `n` times → $O(n)$.
**Smart**: $x^n = (x^2)^{n/2}$ when $n$ is even — halving the exponent each step → $O(\log n)$:

```python
def my_pow(x: float, n: int) -> float:
    """O(log n) fast exponentiation by squaring."""
    if n < 0:
        x, n = 1 / x, -n  # Handle negative exponents
    
    result = 1.0
    while n:
        if n & 1:       # If current lowest bit is set, multiply in current x
            result *= x
        x *= x          # Square the base (x^1 → x^2 → x^4 → x^8...)
        n >>= 1         # Drop the lowest bit (shift right)
    return result
```

This leverages [[13-bit-manipulation|bit manipulation]] directly—iterating through the binary digits of the exponent.

### 4.2 Happy Number — Cycle Detection via Floyd's Algorithm

A number is "happy" if repeated replacement with the sum-of-squared-digits eventually reaches 1. Otherwise, it cycles forever.

```python
def is_happy(n: int) -> bool:
    """Detects Happy Number cycle using Floyd's fast/slow pointer algorithm."""
    def digit_square_sum(x):
        total = 0
        while x:
            x, digit = divmod(x, 10)
            total += digit ** 2
        return total
    
    slow, fast = n, digit_square_sum(n)
    while fast != 1 and slow != fast:
        slow = digit_square_sum(slow)
        fast = digit_square_sum(digit_square_sum(fast))
    return fast == 1
```

This treats the sequence of digit-square-sums as a **linked list**. Floyd's cycle detection detects loops with $O(1)$ space instead of a hash set.

---

## 5. Complexity Summary

| Problem | Naïve Approach | Optimized Trick | Optimized Complexity |
| :--- | :--- | :--- | :--- |
| **Rotate Matrix** | $O(n^2)$ space (copy grid) | Transpose + reverse rows | **$O(1)$ space** |
| **Set Matrix Zeroes** | $O(m+n)$ space (marker arrays) | Reuse first row/col as markers | **$O(1)$ space** |
| **Pow(x, n)** | $O(n)$ (multiply n times) | Binary exponentiation | **$O(\log n)$** |
| **Happy Number** | $O(k)$ space (hash set of seen) | Floyd's slow/fast pointers | **$O(1)$ space** |

---

## 6. Common Pitfalls & Traps

1. **Transpose Before Reverse (not after)**: For 90° CW rotation—transpose first, then reverse rows. Doing it in the wrong order gives a 90° CCW rotation.
2. **Spiral Off-By-One**: When only a single row or column remains, the left/right bottom/top boundary checks prevent double-visiting that row/column.
3. **Negative Exponent in `Pow`**: Always handle `n < 0` explicitly by taking the reciprocal of `x` and making `n` positive before the main loop.
4. **Integer Overflow in `Pow`**: In fixed-width languages (Java, C++), intermediate `x * x` can overflow 64-bit integers for large inputs.

---

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: What two-step in-place process achieves a 90° clockwise rotation of an $n \times n$ matrix?
   - <details><summary>Click for Answer</summary><b>Answer:</b> (1) <b>Transpose</b>: swap <code>matrix[i][j]</code> with <code>matrix[j][i]</code> for all <code>i < j</code>. (2) <b>Reverse each row</b>. These two in-place operations together are equivalent to a 90° clockwise rotation.</details>

2. **Question**: Why does binary exponentiation compute `x^n` in $O(\log n)$ instead of $O(n)$?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Instead of multiplying by <code>x</code> exactly <code>n</code> times, binary exponentiation halves the exponent at each step by squaring the base (<code>x^n = (x^2)^{n/2}</code>). This means the loop runs for at most <code>log₂ n</code> iterations.</details>

3. **Question**: In the Set Matrix Zeroes problem, why must you process the first row and column markers *last* rather than *first*?
   - <details><summary>Click for Answer</summary><b>Answer:</b> The first row and column are used as marker storage during the pass over the interior cells. If you zero them out first, you destroy the markers needed to process the interior cells correctly.</details>

---

## Related Modules
- [[13-bit-manipulation|Bit Manipulation]] — Binary exponentiation uses bit-shift operators
- [[07-number-theory-basics|Number Theory Basics]] — Integer arithmetic techniques
