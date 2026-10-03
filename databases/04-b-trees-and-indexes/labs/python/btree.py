"""A B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule of composite indexes.
A teaching model: one node is one "page", and every node visited counts as one page read."""
import math
from dataclasses import dataclass, field
from typing import Any


def levels(rows: int, keys_per_leaf: int, fanout: int) -> int:
    """How many levels a B+ tree needs: one level of leaves, then enough internal levels to point at them all."""
    leaves = math.ceil(rows / keys_per_leaf)
    return 1 + max(0, math.ceil(math.log(leaves, fanout) - 1e-12))  # tiny slack so exact powers don't round up


@dataclass
class Leaf:
    keys: list = field(default_factory=list)
    values: list = field(default_factory=list)
    next: "Leaf | None" = None  # the leaves form a linked list, for range scans


@dataclass
class Internal:
    keys: list = field(default_factory=list)  # routing only: children[i] holds keys < keys[i]
    children: list = field(default_factory=list)


class BPlusTree:
    """Keys and values live only in the leaves. A node holds at most `max_keys` keys; one more and it splits."""

    def __init__(self, max_keys: int):
        if max_keys < 3:
            raise ValueError("max_keys must be at least 3")
        self.max_keys = max_keys
        self.root: Leaf | Internal = Leaf()
        self.height = 1

    def search(self, key) -> tuple[Any, int]:
        """(value or None, pages read). Always reads exactly `height` pages: every leaf is at the same depth."""
        node, pages = self.root, 1
        while isinstance(node, Internal):
            node, pages = node.children[self._child(node, key)], pages + 1
        i = self._find(node.keys, key)
        return (node.values[i] if i < len(node.keys) and node.keys[i] == key else None), pages

    def range(self, lo, hi) -> tuple[list, int]:
        """Values for lo <= key <= hi, and pages read: down the tree once, then along the leaf chain."""
        node, pages = self.root, 1
        while isinstance(node, Internal):
            node, pages = node.children[self._child(node, lo)], pages + 1
        found = []
        while node is not None:
            for k, v in zip(node.keys, node.values):
                if k > hi:
                    return found, pages
                if k >= lo:
                    found.append(v)
            node = node.next
            if node is not None:
                pages += 1
        return found, pages

    def insert(self, key, value) -> None:
        split = self._insert(self.root, key, value)
        if split:  # the root split: the only way the tree grows a level
            separator, right = split
            self.root = Internal([separator], [self.root, right])
            self.height += 1

    def _insert(self, node, key, value):
        if isinstance(node, Leaf):
            i = self._find(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.values[i] = value  # an existing key: replace
                return None
            node.keys.insert(i, key)
            node.values.insert(i, value)
            if len(node.keys) <= self.max_keys:
                return None
            mid = len(node.keys) // 2  # split in half; the right half's first key is copied up
            right = Leaf(node.keys[mid:], node.values[mid:], node.next)
            node.keys, node.values, node.next = node.keys[:mid], node.values[:mid], right
            return right.keys[0], right
        i = self._child(node, key)
        split = self._insert(node.children[i], key, value)
        if not split:
            return None
        separator, right = split
        node.keys.insert(i, separator)
        node.children.insert(i + 1, right)
        if len(node.keys) <= self.max_keys:
            return None
        mid = len(node.keys) // 2  # an internal split moves the middle key up, rather than copying it
        up = node.keys[mid]
        sibling = Internal(node.keys[mid + 1:], node.children[mid + 1:])
        node.keys, node.children = node.keys[:mid], node.children[:mid + 1]
        return up, sibling

    @staticmethod
    def _find(keys: list, key) -> int:
        lo, hi = 0, len(keys)
        while lo < hi:
            mid = (lo + hi) // 2
            if keys[mid] < key:
                lo = mid + 1
            else:
                hi = mid
        return lo

    @staticmethod
    def _child(node: Internal, key) -> int:
        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i += 1
        return i


def usable_prefix(index: tuple[str, ...], equal: set[str], ranges: set[str]) -> list[str]:
    """The index columns that narrow the search: equality columns from the left, then at most one range column.
    Columns after a range, or after a gap, can only filter rows the index has already found."""
    used = []
    for column in index:
        if column in equal:
            used.append(column)
        elif column in ranges:
            used.append(column)
            break  # after a range, the next column isn't sorted within it
        else:
            break  # a gap: nothing to the right can be used to narrow
    return used
