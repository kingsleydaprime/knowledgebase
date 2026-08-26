# Linked Lists

A linked list is a sequence of nodes where each node holds a value and a pointer to the next node. Unlike an [[01-arrays|array]], the nodes don't have to sit next to each other in memory — they can be scattered anywhere, connected purely by pointers. That one difference flips almost every tradeoff an array has.

## Why it exists

Arrays need one contiguous block, which means inserting or removing in the middle means shifting every element after the change — O(n). A linked list never shifts anything: to insert a node you repoint a couple of pointers, O(1), *if you already have a reference to the node it goes next to*. The cost is that you lose direct indexing — to reach the 5th node you walk from the head, one pointer at a time.

That "if you already have a reference" clause is doing enormous work, and it's the thing most people miss on first read. **A linked list is only fast at the position you're already standing on.** Getting to an arbitrary position is O(n), so an insert "in the middle" is O(n) to find the spot plus O(1) to splice — no better than an array. The structure pays off when something *else* is already holding the node reference for you, which is exactly the arrangement in an LRU cache.

## The anatomy of a node

A node is just a small object holding a value and one or more pointers:

```python
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None       # a doubly linked node adds: self.prev = None
```

The list itself is usually a thin wrapper holding a `head` pointer (and often a `tail`). **The list *is* the head pointer** — lose it and every node becomes unreachable.

## The variants

The differences come down to two independent choices: **how many pointers per node** (one or two), and **whether the ends join up** (linear or circular). That gives four combinations, and each exists for a specific reason.

### Singly linked — one pointer, linear

Each node points only forward. The last node points to `None`, which is how you know you've hit the end.

```
head -> [10 | *] -> [22 | *] -> [7 | *] -> [41 | None]
```

The default, and the cheapest: one pointer per node. The limitation is that **you can only move forward** — which means deleting a node requires a reference to the node *before* it, so you have to walk from the head to find the predecessor even if you already hold the node you want gone.

### Doubly linked — two pointers, linear

Each node points forward and backward:

```
None <- [10 |*|*] <-> [22 |*|*] <-> [7 |*|*] -> None
```

Costs an extra pointer per node, and every operation has to maintain two pointers instead of one — twice the chances to get it wrong. What you buy is significant: **traversal in either direction**, and **O(1) deletion given only the node itself**, because the node already knows its own predecessor. No walk from the head required.

That single property is why the LRU cache uses a doubly linked list. The hash map hands you a node directly; if the list were singly linked you'd still have to walk O(n) to find what comes before it, and the whole point of the structure would collapse.

### Circular singly linked — one pointer, joined

The last node points back to the first instead of to `None`:

```
   ┌─────────────────────────────────────┐
   └─> [10 | *] -> [22 | *] -> [7 | *] ──┘
```

There is no end, so **there's no "start over" logic** — you just keep walking. That makes it the natural fit for anything that cycles indefinitely: round-robin CPU scheduling (each process gets a slice, then the next, forever), turn order in a game, a repeating playlist, or a ring buffer of connections handed out in rotation.

Termination changes shape: you can't loop `while cur is not None`, because that never fires. You loop until you arrive back where you began (`while cur is not start`), which means **you must remember your starting node** before you begin.

### Circular doubly linked — two pointers, joined

Both at once: every node has `prev` and `next`, and the ends join up, so `head.prev` is the tail and `tail.next` is the head.

```
   ┌──────────────────────────────────────────┐
   └─> [10 |*|*] <-> [22 |*|*] <-> [7 |*|*] <─┘
```

The most capable and the most pointer-bookkeeping. Its quiet advantage: **the tail is free** — `head.prev` reaches it in O(1) with no separate tail pointer to maintain. Combined with a sentinel (below), this is the variant with the fewest special cases in the code, which is why it's what the Linux kernel's `list_head` actually is, and what most production deque implementations use internally.

### Picking one

| | Pointers/node | Walk backward | Delete given a node | Reach tail | Typical use |
|---|---|---|---|---|---|
| **Singly** | 1 | ✗ | O(n) — need the predecessor | O(n), or O(1) with a tail pointer | Stacks, simple queues, memory-tight code |
| **Doubly** | 2 | ✓ | **O(1)** | O(n), or O(1) with a tail pointer | LRU caches, deques, undo/redo, text editors |
| **Circular singly** | 1 | ✗ | O(n) | O(1) — it's `head.prev`'s job in the doubly case; here, walk | Round-robin scheduling, turn order, playlists |
| **Circular doubly** | 2 | ✓ | **O(1)** | **O(1)** — `head.prev` | Kernel lists, production deques, buffer pools |

Default to **singly** unless you need backward movement or O(1) delete-by-node; default to **doubly** the moment you do. Reach for circular only when the data genuinely has no beginning or end — using it for merely convenient tail access is a common way to introduce infinite loops for no reason.

## The sentinel (dummy head) trick

Most linked-list bugs live in the special cases: inserting into an empty list, deleting the head, deleting the only node. Each one needs its own `if`, and forgetting one is the standard failure.

**A sentinel is a permanent dummy node that sits before the real head and holds no data.** The list is never empty — it always has at least the sentinel — so the "insert into an empty list" case stops existing, and the real first node has a predecessor like every other node, so "delete the head" stops being special either.

```python
def remove(head, target):                 # without a sentinel
    if head and head.value == target:     # special case: deleting the head
        return head.next
    cur = head
    while cur and cur.next:
        if cur.next.value == target:
            cur.next = cur.next.next
            break
        cur = cur.next
    return head

def remove(head, target):                 # with a sentinel
    dummy = Node(None)
    dummy.next = head
    cur = dummy
    while cur.next:
        if cur.next.value == target:
            cur.next = cur.next.next      # one path, no head special case
            break
        cur = cur.next
    return dummy.next                     # the real head, whatever it ended up being
```

The second version has one branch instead of two and can't mishandle an empty list. **Reach for a sentinel any time a problem involves deleting or inserting at an unknown position** — it's the single highest-leverage habit in linked-list code, and it's why `dummy = ListNode(0)` opens so many accepted solutions.

## Complexity

| Operation | Time | Why |
|---|---|---|
| Access by index | O(n) | must walk from the head — there's no address arithmetic |
| Search | O(n) | same reason |
| Insert/delete at head | O(1) | just repoint `head` |
| Insert/delete given a node reference | O(1) singly*, O(1) doubly | *singly needs the *predecessor*, not the node |
| Insert/delete at tail | O(n), or O(1) with a tail pointer | walking to the end is the cost; caching the tail removes it |
| Space overhead | O(n) pointers | 1 pointer per node singly, 2 doubly — on top of the data itself |

Compare directly against [[01-arrays|arrays]]: linked lists win at insert/delete near a position you already hold, arrays win at random access and cache locality. Neither is strictly better — pick based on which operation dominates.

## Example

```python
class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None                   # cached, so append is O(1)

    def push_front(self, value):           # O(1)
        node = Node(value)
        node.next = self.head
        self.head = node
        if self.tail is None:              # first node is both head and tail
            self.tail = node

    def append(self, value):               # O(1) thanks to the tail pointer
        node = Node(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node

    def find(self, value):                 # O(n)
        cur = self.head
        while cur:
            if cur.value == value:
                return cur
            cur = cur.next
        return None
```

Note what the tail pointer costs: **every mutation now has to keep it correct.** Delete the last node and forget to move `tail` back, and it points at a node no longer in the list. Cached state is a maintenance obligation, not free speed.

## Where they're actually used

- **LRU caches** — doubly linked list + hash map, the classic combination. The map gives O(1) lookup of *which* node; the list gives O(1) reordering (unlink it, splice it to the front). Neither structure can do it alone, and the list must be doubly linked for the unlink to be O(1).
- **The Linux kernel** — `struct list_head` is a circular doubly linked list, embedded *inside* the structs it links rather than wrapping them. Processes, files, and pretty much every kernel object live on one.
- **Memory allocators** — the free list is a linked list of available blocks. Nodes get spliced out on `malloc` and back in on `free`, always at a position the allocator already holds.
- **Round-robin schedulers** — a circular list of runnable tasks; advancing is one pointer hop and never needs a wraparound check.
- **Undo/redo**, **text editor buffers** (gap buffers and piece tables are cousins), and **implementing deques**.

For everyday application code, **dynamic arrays usually win anyway** because of cache locality — see [[01-arrays|arrays]]. Chasing pointers around scattered memory costs a cache miss per node, and a cache miss is worth hundreds of instructions. This is one of the clearest cases where real hardware behaviour beats asymptotic complexity: an O(n) array scan routinely outruns an O(1) linked-list splice in practice.

## Gotchas

- **Losing the head reference is fatal.** Overwrite `head` before saving a pointer to the old first node and the rest of the list becomes unreachable — a conceptual leak in a garbage-collected language, a real one in C.
- **Order of pointer reassignment.** Off-by-one errors on `.next` during insert/delete are the single most common bug here. Draw the before/after picture (`A -> B -> C` becoming `A -> X -> B -> C`) and reassign in an order that doesn't overwrite a pointer you still need — the classic reversal bug is doing `cur.next = prev` before saving `cur.next`.
- **Circular lists break every termination condition you know.** `while cur:` never ends, and printing one in a debugger hangs. Always loop against your remembered start node, and be aware that a circular list will hang naive code written for a linear one.
- **Doubly linked deletion has two pointers to fix, not one** — both `node.prev.next` and `node.next.prev`. Fixing one and forgetting the other leaves a list that traverses correctly forward and corruptly backward, which is a genuinely nasty bug to find.
- **Singly linked lists can't be traversed backward.** If you need that, use a doubly linked list, or reverse the list first — see [[05-linked-list-reversal|linked-list reversal]].
- **Cycle detection needs its own technique.** A `.next` chain that loops back into itself can't be found by walking and hoping — see [[04-fast-slow-pointers|fast/slow pointers]].

## Related
- [[01-arrays|arrays]] — the contiguous alternative, and why it usually wins in practice
- [[02-dynamic-arrays|dynamic arrays]] — what you actually use instead, most of the time
- [[07-stacks-and-queues|stacks and queues]] — commonly built on a linked list when you only touch the ends
- [[05-linked-list-reversal|linked-list reversal]] — the in-place pointer-rewiring pattern
- [[04-fast-slow-pointers|fast/slow pointers]] — cycle detection in O(1) space
- [[02-traversal|traversal]]
