# Module: Sorting Algorithms (Comparison & Non-Comparison Sorting)

Welcome to the **Sorting Algorithms** module. Sorting means arranging elements into a defined order (ascending or descending).

Sorting is one of the most thoroughly studied areas of computer science. It serves as a prerequisite for fast searching ([[05-searching|Binary Search]]) and optimization patterns ([[03-sliding-window|Sliding Window]], Two Pointers).

---

## 1. Real-World Motivation & Physical Metaphors

Imagine organizing a **shuffled deck of playing cards** by suit and rank:

```
Unsorted Deck:  [ 9♠, 2♥, K♦, 5♠, 3♣ ]
Sorted Deck:    [ 2♥, 3♣, 5♠, 9♠, K♦ ]
```

- **Elementary Strategy (Insertion Sort)**: Pick one card at a time and slide it into its correct position in your left hand. (Fast for small hands, slow for 1,000 cards).
- **Divide & Conquer Strategy (Merge Sort)**: Split the deck in half, ask a friend to sort each half, then zip the two sorted halves back together.

### Production Use Cases:
1. **Database Queries**: `SELECT * FROM users ORDER BY age DESC` (Engineered using B+ Trees and Timsort).
2. **Search Engines**: Ranking search results by relevance score.
3. **E-Commerce**: Sorting products by price, rating, or release date.

---

## 2. Plain-English Terminology & Concept Table

| Term | Plain-English Definition | Real-World Example |
| :--- | :--- | :--- |
| **Comparison Sort** | Sorting by directly comparing elements pairwise (`if A > B`). | Comparing prices of two items. |
| **In-Place Sort** | Sorting directly inside the input array using **$O(1)$ extra space**. | Rearranging books on a shelf without needing extra tables. |
| **Stable Sort** | A sort that **preserves the relative order** of items with equal keys. | Sorting students by grade while preserving their original sign-up order. |
| **Pivot** | An element chosen in Quicksort to partition items into smaller and larger groups. | Dividing students into height groups above and below 5'10". |

---

## 3. The Information-Theoretic Lower Bound ($O(n \log n)$)

> [!KEY-INSIGHT]
> **Why Comparison Sorts Cannot Beat $O(n \log n)$**:
> An unsorted array of $N$ items has $N!$ possible permutations. Each comparison (`A > B`) provides 1 bit of information (yes/no), halving the remaining possibilities.
> 
> To uniquely identify the 1 correct sorted order out of $N!$ possibilities:
> $$\text{Minimum Comparisons} = \log_2(N!) \approx N \log_2 N - N \log_2 e = \mathbf{\Omega(N \log N)}$$

Any comparison-based algorithm (Merge Sort, Quick Sort, Heap Sort) **cannot beat $O(n \log n)$ in the worst case**!

---

## 4. Technical Deep Dive: The 4 Core Sorting Families

### 1. Insertion Sort ($O(n^2)$ Elementary, $O(n)$ Best)
Builds a sorted prefix one element at a time by sliding each item leftward into place.

```python
def insertion_sort(arr: list) -> list:
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # Shift larger elements right to make a slot for key
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```
- *Niche*: Highly efficient ($O(n)$ linear) on **nearly sorted data** and small arrays ($N < 20$).

---

### 2. Merge Sort ($O(n \log n)$ Guaranteed, Stable)
Recursively splits array in half, sorts each half, and merges them using extra memory.

```python
def merge_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
        
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # Merge sorted halves
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= maintains Stability!
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
            
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

---

### 3. Quick Sort ($O(n \log n)$ Average, In-Place)
Picks a **pivot**, partitions elements into $< \text{pivot}$ and $> \text{pivot}$, then recurses.

```python
def quicksort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

---

### 4. Counting Sort ($O(n + k)$ Non-Comparison)
Sidesteps pairwise comparisons entirely by counting frequency of bounded integer values `0..k`.

```python
def counting_sort(arr: list, max_val: int) -> list:
    """Sorts integers in range 0..max_val in O(n + max_val) time!"""
    counts = [0] * (max_val + 1)
    for num in arr:
        counts[num] += 1
        
    sorted_arr = []
    for val, freq in enumerate(counts):
        sorted_arr.extend([val] * freq)
    return sorted_arr
```

---

## 5. Master Comparison Table

| Algorithm | Best Time | Average Time | Worst Time | Space | Stable? | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bubble Sort** | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Yes | Educational concepts only. |
| **Insertion Sort** | **$O(n)$** | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Yes | Small or nearly-sorted datasets. |
| **Merge Sort** | $O(n \log n)$ | **$O(n \log n)$** | **$O(n \log n)$** | $O(n)$ | Yes | Linked lists, guaranteed time requirements. |
| **Quick Sort** | $O(n \log n)$ | **$O(n \log n)$** | $O(n^2)$ | $O(\log n)$ | No | General in-place sorting (fast cache locality). |
| **Counting Sort** | **$O(n + k)$** | **$O(n + k)$** | **$O(n + k)$** | $O(k)$ | Yes | Bounded integers (e.g. age, test scores). |
| **Timsort (Python)**| **$O(n)$** | **$O(n \log n)$** | **$O(n \log n)$** | $O(n)$ | Yes | **Production Standard** (`sorted()`, `Arrays.sort()`). |

---

## 6. Common Pitfalls & Traps

1. **Quicksort Worst-Case Trap**: Naive pivot selection (always picking index 0) on an **already sorted array** causes $O(n^2)$ quadratic degradation! Always randomize pivot selection.
2. **Ignoring Stability**: Sorting complex objects by primary key, then secondary key, requires a **Stable Sort** (like Merge Sort or Timsort). Unstable sorts ruin secondary key ordering.
3. **Re-inventing the Wheel**: Never hand-roll a custom sort in production. Python's built-in `sorted()` uses **Timsort** (C-optimized hybrid of Merge Sort + Insertion Sort).

---

## 7. Check Your Understanding (University Self-Assessment)

1. **Question**: Why can Counting Sort achieve $O(n + k)$ time complexity, beating the $O(n \log n)$ theoretical lower bound?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Counting Sort is a <b>non-comparison sort</b>. It places elements by using their numerical values directly as array indices rather than making pairwise comparisons (<code>A > B</code>). The $O(n \log n)$ lower bound applies strictly to comparison-based sorting algorithms.</details>

2. **Question**: What does it mean for a sorting algorithm to be "Stable"?
   - <details><summary>Click for Answer</summary><b>Answer:</b> A sorting algorithm is <b>Stable</b> if it preserves the original relative order of elements that have equal sorting keys.</details>

3. **Question**: Why does Python's production sort (Timsort) switch to Insertion Sort for small array chunks ($N < 64$)?
   - <details><summary>Click for Answer</summary><b>Answer:</b> Insertion Sort has very low constant overhead and runs in near-linear time <b>O(n)</b> on small or partially sorted arrays, outperforming Merge Sort's recursion overhead at small scale.</details>

---

## Related Modules
- [[05-searching|Searching Algorithms]] — Binary search preconditions
- [[01-algorithms|Algorithms & Complexity Analysis]] — Asymptotic notation bounds
- [[08-heaps|Heaps & Priority Queues]] — Heapsort mechanics
