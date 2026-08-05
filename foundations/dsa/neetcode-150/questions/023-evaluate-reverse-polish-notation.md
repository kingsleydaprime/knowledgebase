# Evaluate Reverse Polish Notation

**LeetCode 150** · Stack · concept: [[07-stacks-and-queues|stacks-and-queues]]

## Problem

Evaluate an arithmetic expression in **Reverse Polish (postfix)** notation, where each operator follows its operands.

```
["2", "1", "+", "3", "*"]  ->  9    ( (2+1) * 3 )
["4", "13", "5", "/", "+"] ->  6    ( 4 + (13/5) )
```

## Approach — stack (optimal)

Postfix is *built* to be evaluated with a stack: push numbers; on an operator, pop the top two operands, apply, push the result back. At the end, the lone stack value is the answer.

```python
def evalRPN(tokens):
    stack = []
    ops = {"+", "-", "*", "/"}
    for tok in tokens:
        if tok in ops:
            b = stack.pop()                  # second operand (popped first)
            a = stack.pop()                  # first operand
            if tok == "+": stack.append(a + b)
            elif tok == "-": stack.append(a - b)
            elif tok == "*": stack.append(a * b)
            else: stack.append(int(a / b))   # truncate toward zero
        else:
            stack.append(int(tok))
    return stack[0]
```

**Time O(n), space O(n).**

## Two gotchas

- **Operand order** — the *first* popped value is the **right** operand. It matters for `-` and `/`: `a - b`, `a / b`, not reversed.
- **Division truncates toward zero** — `int(a / b)`, not `//` (which floors toward −∞ and gives wrong results for negatives, e.g. `-7 // 2 == -4` but the problem wants `-3`).

## Key insight

**Postfix evaluation is the archetypal stack algorithm** — operands wait on the stack until their operator arrives. (Infix expressions are handled by the shunting-yard algorithm, which converts to postfix first.) The pattern generalizes to any "process operands, apply pending operations" evaluation.

## Related
- concept: [[07-stacks-and-queues|stacks-and-queues]]
- prev: [[022-min-stack|Min Stack]] · next: [[024-generate-parentheses|Generate Parentheses]]
