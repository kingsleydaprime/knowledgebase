# Car Fleet

**LeetCode 853** · Stack · concept: [[06-monotonic-stack|monotonic-stack]]

## Problem

Cars at various `position`s head to a `target` at given `speed`s. A faster car catching a slower one **forms a fleet** and travels at the slower car's speed (no passing). Return the number of fleets that reach the target.

```
target=12, position=[10,8,0,5,3], speed=[2,4,1,1,3]  ->  3
```

## The key reframing — time to target

Sort cars by **position, closest to the target first**. Compute each car's **arrival time** `(target - position) / speed`. Now process from the front car backward: a car behind joins the fleet ahead **iff its arrival time is ≤ the fleet's** (it catches up before the target); otherwise it's slower and starts a **new** fleet.

```python
def carFleet(target, position, speed):
    cars = sorted(zip(position, speed), reverse=True)   # nearest the target first
    fleets = 0
    lead_time = 0                                        # arrival time of the current fleet's front
    for pos, spd in cars:
        time = (target - pos) / spd
        if time > lead_time:                            # can't catch up -> new fleet
            fleets += 1
            lead_time = time
        # else: absorbed into the fleet ahead
    return fleets
```

**Time O(n log n)** (the sort), space O(n).

## Why arrival time decides fleets

Two cars merge iff the behind car would otherwise reach the target *sooner* — i.e. its unobstructed arrival time is ≤ the car ahead's. Since you process nearest-first, `lead_time` is always the arrival time of the fleet currently in front; a car with a strictly larger time can never catch it and becomes a new fleet leader. It's a **monotonic stack of arrival times** in disguise (you only ever compare against the current front).

## Key insight

**Convert a physical "catch up" condition into a comparison of a single scalar (arrival time), then sweep in order.** Sorting by position and reasoning about times turns a messy simulation into one linear pass — the reframing *is* the solution.

## Related
- concept: [[06-monotonic-stack|monotonic-stack]], [[04-sorting|sorting]]
- prev: [[025-daily-temperatures|Daily Temperatures]] · next: [[027-largest-rectangle-in-histogram|Largest Rectangle in Histogram]]
