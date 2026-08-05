# Copy List with Random Pointer

**LeetCode 138** · Linked List · concept: [[03-hash-maps|hash-maps]]

## Problem

Deep-copy a linked list where each node has a `next` **and** a `random` pointer (to any node or null).

## The challenge

You can't set a clone's `random` on the first pass — the target clone may not exist yet. Two clean solutions:

## Approach 1 — hash map old → new (two passes)

Pass 1: create every clone, mapping original → clone. Pass 2: wire up `next` and `random` using the map to translate an original's pointer into the corresponding clone.

```python
def copyRandomList(head):
    if not head:
        return None
    clones = {}                          # original node -> its clone
    curr = head
    while curr:                          # pass 1: create clones
        clones[curr] = Node(curr.val)
        curr = curr.next
    curr = head
    while curr:                          # pass 2: connect via the map
        clones[curr].next = clones.get(curr.next)
        clones[curr].random = clones.get(curr.random)
        curr = curr.next
    return clones[head]
```

**Time O(n), space O(n).**

## Approach 2 — interleave clones (O(1) space)

Weave each clone right after its original (`A→A'→B→B'→…`). Now a clone's random is `original.random.next`. Finally unweave the two lists. **O(n) time, O(1) extra space** — the elegant follow-up.

## Key insight

**When you must reference a not-yet-created copy, map original → copy first, then wire in a second pass.** The hash map is a translation table from old-world pointers to new-world pointers — a general technique for cloning any linked structure (it's exactly how *Clone Graph* works too).

## Related
- concept: [[03-hash-maps|hash-maps]], [[04-linked-lists|linked-lists]]
- prev: [[038-remove-nth-node-from-end|Remove Nth Node From End]] · next: [[040-add-two-numbers|Add Two Numbers]]
