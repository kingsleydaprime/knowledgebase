# Serialize and Deserialize Binary Tree

**LeetCode 297** · Trees · concept: [[02-traversal|traversal]]

## Problem

Design `serialize(tree) -> str` and `deserialize(str) -> tree` that round-trip **any** binary tree (arbitrary values, arbitrary shape).

## The idea — preorder with explicit null markers

A traversal alone is ambiguous (many trees share a preorder). Recording **nulls** removes the ambiguity: preorder *with* a marker for every missing child uniquely encodes the shape.

```python
def serialize(root):
    vals = []
    def dfs(node):
        if not node:
            vals.append("#")          # null marker
            return
        vals.append(str(node.val))
        dfs(node.left)
        dfs(node.right)
    dfs(root)
    return ",".join(vals)

def deserialize(data):
    vals = iter(data.split(","))
    def build():
        v = next(vals)
        if v == "#":
            return None
        node = TreeNode(int(v))
        node.left = build()           # consume in the SAME preorder
        node.right = build()
        return node
    return build()
```

**Time O(n), space O(n).**

## Why nulls make it unambiguous

`[1, 2]` could be many trees; `1,2,#,#,#` (preorder with markers) is exactly one. Deserialization consumes the tokens in the **identical preorder** the serializer produced — root, then fully build the left subtree, then the right — so an iterator advancing left-to-right reconstructs the precise shape. Encoder and decoder must agree on traversal order and the null sentinel.

## Key insight

**A traversal + null markers is a complete, reversible encoding of tree shape.** This is the tree analogue of [[006-encode-and-decode-strings|length-prefixed serialization]] — capture enough structure (here, the nulls) that decoding is deterministic. BFS-with-markers works equally well; the preorder recursion is the cleanest.

## Related
- concept: [[02-traversal|traversal]]
- relative: [[006-encode-and-decode-strings|Encode and Decode Strings]] (serialization design)
- prev: [[059-binary-tree-maximum-path-sum|Binary Tree Maximum Path Sum]] — end of Trees
- next category: Tries
