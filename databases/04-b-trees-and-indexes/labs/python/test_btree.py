import math
import random
import unittest

from btree import BPlusTree, Internal, Leaf, levels, usable_prefix


class Model(unittest.TestCase):
    def test_why_not_a_binary_tree(self):
        self.assertEqual(math.ceil(math.log2(10**8)), 27)  # a balanced binary tree over 100 million keys: 27 levels
        self.assertEqual(levels(10**8, 367, 400), 4)  # a B+ tree: 4, and the top two or three stay in memory
        self.assertEqual(levels(10**6, 367, 400), 3)  # a million rows: 3, as Postgres reports below

    def test_splits_keep_every_leaf_at_the_same_depth(self):
        tree = BPlusTree(max_keys=3)
        for k in range(1, 11):
            tree.insert(k, f"v{k}")
        self.assertEqual(tree.height, 3)
        self.assertIsInstance(tree.root, Internal)
        self.assertEqual(tree.root.keys, [7])  # the separator that last moved up
        leaves, node = [], tree.root
        while isinstance(node, Internal):
            node = node.children[0]
        while node:
            leaves.append(node.keys)
            node = node.next
        self.assertEqual(leaves, [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])  # linked, in order

    def test_a_lookup_reads_one_page_per_level(self):
        tree = BPlusTree(max_keys=3)
        for k in range(1, 11):
            tree.insert(k, f"v{k}")
        self.assertEqual(tree.search(7), ("v7", 3))
        self.assertEqual(tree.search(99), (None, 3))  # a miss costs the same
        self.assertEqual(tree.range(4, 8), (["v4", "v5", "v6", "v7", "v8"], 6))  # down once, then along the leaves

    def test_a_million_keys_three_pages(self):
        keys = list(range(1_000_000))
        random.Random(1).shuffle(keys)
        tree = BPlusTree(max_keys=400)
        for k in keys:
            tree.insert(k, k)
        self.assertEqual((tree.height, tree.search(424_242)), (3, (424_242, 3)))

    def test_the_leftmost_prefix_rule(self):
        index = ("a", "b", "c")
        self.assertEqual(usable_prefix(index, {"a"}, set()), ["a"])
        self.assertEqual(usable_prefix(index, {"a", "b", "c"}, set()), ["a", "b", "c"])
        self.assertEqual(usable_prefix(index, {"b"}, set()), [])  # no leading column: can't narrow
        self.assertEqual(usable_prefix(index, {"a", "c"}, set()), ["a"])  # a gap at b: c only filters
        self.assertEqual(usable_prefix(index, {"b"}, {"a"}), ["a"])  # a range on a: b only filters
        self.assertEqual(usable_prefix(index, {"a"}, {"b"}), ["a", "b"])  # equality first, then the range


if __name__ == "__main__":
    unittest.main()
