# Pattern: Monotonic Stack

A stack that's kept strictly increasing or strictly decreasing from bottom to top, by popping off anything that would break that order before pushing a new element. It turns "for each element, find the next greater/smaller element" from an O(n²) brute-force scan into O(n).

## When to use it

Problems asking for the **next (or previous) greater/smaller element** for every position in an array — or anything that reduces to that shape, like "how many days until a warmer temperature" or "widest rectangle under a histogram."

## How it works

Walk the array once. For each new element, pop everything off the stack that's smaller than it (those elements just found their "next greater element" — the current one) — then push the current element.

```python
def next_greater_elements(nums):
    result = [-1] * len(nums)
    stack = []                      # holds indices, kept in decreasing value order
    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            result[stack.pop()] = num   # current num is the "next greater" for stack.pop()
        stack.append(i)
    return result
```

```
nums = [2, 1, 2, 4, 3]

i=0 num=2  stack=[]        -> push -> stack=[0]
i=1 num=1  stack=[0]        -> 2 not < 1, push -> stack=[0,1]
i=2 num=2  stack=[0,1]      -> nums[1]=1 < 2, pop, result[1]=2
                             -> nums[0]=2 not < 2, push -> stack=[0,2]
i=3 num=4  stack=[0,2]      -> nums[2]=2 < 4, pop, result[2]=4
                             -> nums[0]=2 < 4, pop, result[0]=4
                             -> push -> stack=[3]
i=4 num=3  stack=[3]        -> nums[3]=4 not < 3, push -> stack=[3,4]

result = [4, 2, 4, -1, -1]
```

## Why it's O(n) despite the nested while loop

Every index gets pushed onto the stack exactly once and popped at most once across the *entire* run — so the total number of push/pop operations is bounded by 2n, not n². Same amortized argument as [[02-dynamic-arrays|dynamic array resizing]]: the loop looks nested, but the total work across the whole run is linear.

## Complexity

O(n) time, O(n) space (worst case, if the array is already in an order that never triggers a pop, e.g. strictly decreasing).

## Practice problems
1. Next Greater Element I (LeetCode #496)
2. Daily Temperatures (LeetCode #739)
3. Largest Rectangle in Histogram (LeetCode #84) — the classic hard variant

## Related
- [[01-algorithms|algorithms]] — amortized analysis
- [[01-arrays|arrays]]
