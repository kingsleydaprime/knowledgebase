# Best Time to Buy and Sell Stock with Cooldown

**LeetCode 309** · 2-D DP · concept: [[15-dynamic-programming|dynamic-programming]]

## Problem

Maximize profit with unlimited transactions, but after **selling** you must **cooldown** one day before buying again.

## The idea — a state machine

Each day you're in one of three states: **holding** a share, **just sold** (in cooldown), or **rest** (free to buy). Track the best profit in each and transition day by day.

- `hold` = max(stay holding, buy today from `rest`) → `max(hold, rest - price)`
- `sold` = sell today → `hold + price`
- `rest` = max(stay resting, come off cooldown from `sold`) → `max(rest, sold)`

```python
def maxProfit(prices):
    hold, sold, rest = float("-inf"), 0, 0
    for price in prices:
        prev_sold = sold
        sold = hold + price                # sell what we held
        hold = max(hold, rest - price)     # keep holding, or buy from rest
        rest = max(rest, prev_sold)        # stay rested, or finish cooldown
    return max(sold, rest)                 # end not holding
```

**Time O(n), space O(1).**

## State-machine DP

The cooldown couples days (you can't buy right after selling), so a single running value can't capture it — you need a value **per state**, with transitions encoding the rules. Modeling the problem as a small automaton and tracking the best profit in each node is the whole technique.

## Key insight

**Constraints that create "modes" (holding / cooldown / free) → a state-machine DP with one value per state.** When "what you can do next depends on what you just did," enumerate the states and write their transitions — far cleaner than trying to force one dimension.

## Related
- concept: [[15-dynamic-programming|dynamic-programming]]
- relative: [[015-best-time-to-buy-and-sell-stock|Best Time to Buy and Sell Stock]] (single transaction)
- prev: [[112-longest-common-subsequence|Longest Common Subsequence]] · next: [[114-coin-change-ii|Coin Change II]]
