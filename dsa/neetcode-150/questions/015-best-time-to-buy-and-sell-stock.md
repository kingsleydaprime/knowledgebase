# Best Time to Buy and Sell Stock

**LeetCode 121** · Sliding Window · concepts: [[03-sliding-window|sliding-window]], [[01-prefix-sum|prefix-sum]]

## Problem

Given daily `prices`, buy on one day and sell on a **later** day for maximum profit. Return the best profit, or 0 if none is positive.

```
[7, 1, 5, 3, 6, 4]  ->  5   (buy at 1, sell at 6)
```

## Approach — track the min-so-far (optimal)

The window is buy-day…sell-day. Sweep once, remembering the **cheapest price seen so far** (the best buy). At each day, the profit *if you sold today* is `price − minSoFar`; keep the max.

```python
def maxProfit(prices):
    min_price = float("inf")
    best = 0
    for p in prices:
        min_price = min(min_price, p)      # cheapest buy up to here
        best = max(best, p - min_price)    # best sale ending today
    return best
```

**Time O(n), space O(1).** The brute force (every buy/sell pair) is O(n²); tracking the running min collapses it to one pass.

## Key insight

**"Best pair where the second comes after the first" → carry the best-so-far of the first as you scan.** You never need to look back — the optimal buy for any sell day is just the minimum price before it, maintained incrementally. This left-boundary-as-a-running-extreme idea seeds the sliding-window family.

It's also the [[01-prefix-sum|prefix-sum]] pattern with the aggregate swapped out. Profit on day `j` is `price[j] − min(price[0..j-1])` — a value at `j` combined with an aggregate over everything before it. The reason `min_price` is a single variable rather than an array is that you only ever need the aggregate ending *here*, never an arbitrary range, so there's nothing to store. [[122-maximum-subarray|Maximum Subarray]] is the same move with sums instead of minima.

## Related
- concepts: [[03-sliding-window|sliding-window]], [[01-prefix-sum|prefix-sum]]
- next: [[016-longest-substring-without-repeating-characters|Longest Substring Without Repeating Characters]]
