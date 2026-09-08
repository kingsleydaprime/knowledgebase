# Valid Parentheses

**LeetCode 20** · Stack · concept: [[07-stacks-and-queues|stacks-and-queues]]

## Problem

Given a string of `()[]{}`, return `true` if every bracket is closed by the correct type, in the correct order.

```
"()[]{}"  -> true
"(]"      -> false
"([)]"    -> false   (interleaved, not nested)
```

## Approach — stack (optimal)

Brackets nest **last-opened, first-closed** — exactly LIFO. Push every opening bracket; on a closing bracket, the top of the stack must be its match, else it's invalid. Valid input ends with an empty stack.

```python
def isValid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:                       # a closing bracket
            if not stack or stack.pop() != pairs[ch]:
                return False
            # matched
        else:                                 # an opening bracket
            stack.append(ch)
    return not stack                          # leftover opens = invalid
```

**Time O(n), space O(n).**

## The two failure modes

1. **Wrong / no match** — closing bracket when the stack is empty or its top is the wrong type (`([)]` fails here).
2. **Leftover opens** — string ends with unmatched openers still on the stack (`(((`), caught by the final `not stack`.

## Key insight

**Nested/matched structure → stack.** "The most recent unclosed thing must close first" is the definition of LIFO. This is the gateway stack problem; the whole category is variations on "the stack remembers what's still open / still pending."

## Related
- concept: [[07-stacks-and-queues|stacks-and-queues]]
- next: [[022-min-stack|Min Stack]]
