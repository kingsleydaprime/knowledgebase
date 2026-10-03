package btree;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/** A B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule. Same model as the Python lab. */
public final class BTree {
    private BTree() {}

    public static int levels(long rows, int keysPerLeaf, int fanout) {
        double leaves = Math.ceil((double) rows / keysPerLeaf);
        return 1 + Math.max(0, (int) Math.ceil(Math.log(leaves) / Math.log(fanout) - 1e-12));
    }

    /** A sealed interface: a node is exactly one of the two records below, and a switch can tell which. */
    sealed interface Node permits Leaf, Internal {}

    static final class Leaf implements Node {
        final List<Integer> keys = new ArrayList<>();
        final List<String> values = new ArrayList<>();
        Leaf next; // the linked list for range scans
    }

    static final class Internal implements Node {
        final List<Integer> keys = new ArrayList<>(); // routing only
        final List<Node> children = new ArrayList<>();
    }

    public record Found(String value, int pages) {}

    public record Ranged(List<String> values, int pages) {}

    public static final class BPlusTree {
        private final int maxKeys;
        Node root = new Leaf();
        public int height = 1;

        public BPlusTree(int maxKeys) {
            if (maxKeys < 3) throw new IllegalArgumentException("maxKeys must be at least 3");
            this.maxKeys = maxKeys;
        }

        /** The value (null if absent) and the pages read: always the height. */
        public Found search(int key) {
            Node node = root;
            int pages = 1;
            while (node instanceof Internal in) {
                node = in.children.get(child(in, key));
                pages++;
            }
            Leaf leaf = (Leaf) node;
            int i = find(leaf.keys, key);
            return new Found(i < leaf.keys.size() && leaf.keys.get(i) == key ? leaf.values.get(i) : null, pages);
        }

        public Ranged range(int lo, int hi) {
            Node node = root;
            int pages = 1;
            while (node instanceof Internal in) {
                node = in.children.get(child(in, lo));
                pages++;
            }
            List<String> found = new ArrayList<>();
            for (Leaf leaf = (Leaf) node; leaf != null; ) {
                for (int i = 0; i < leaf.keys.size(); i++) {
                    if (leaf.keys.get(i) > hi) return new Ranged(found, pages);
                    if (leaf.keys.get(i) >= lo) found.add(leaf.values.get(i));
                }
                leaf = leaf.next;
                if (leaf != null) pages++;
            }
            return new Ranged(found, pages);
        }

        private record Split(int separator, Node right) {}

        public void insert(int key, String value) {
            Split split = insert(root, key, value);
            if (split != null) {
                Internal top = new Internal(); // the tree grows a level
                top.keys.add(split.separator());
                top.children.add(root);
                top.children.add(split.right());
                root = top;
                height++;
            }
        }

        private Split insert(Node node, int key, String value) {
            return switch (node) {
                case Leaf leaf -> {
                    int i = find(leaf.keys, key);
                    if (i < leaf.keys.size() && leaf.keys.get(i) == key) {
                        leaf.values.set(i, value);
                        yield null;
                    }
                    leaf.keys.add(i, key);
                    leaf.values.add(i, value);
                    if (leaf.keys.size() <= maxKeys) yield null;
                    int mid = leaf.keys.size() / 2; // the right half's first key is copied up
                    Leaf right = new Leaf();
                    right.keys.addAll(leaf.keys.subList(mid, leaf.keys.size()));
                    right.values.addAll(leaf.values.subList(mid, leaf.values.size()));
                    leaf.keys.subList(mid, leaf.keys.size()).clear();
                    leaf.values.subList(mid, leaf.values.size()).clear();
                    right.next = leaf.next;
                    leaf.next = right;
                    yield new Split(right.keys.getFirst(), right);
                }
                case Internal in -> {
                    int i = child(in, key);
                    Split split = insert(in.children.get(i), key, value);
                    if (split == null) yield null;
                    in.keys.add(i, split.separator());
                    in.children.add(i + 1, split.right());
                    if (in.keys.size() <= maxKeys) yield null;
                    int mid = in.keys.size() / 2; // an internal split moves the middle key up
                    int up = in.keys.get(mid);
                    Internal sibling = new Internal();
                    sibling.keys.addAll(in.keys.subList(mid + 1, in.keys.size()));
                    sibling.children.addAll(in.children.subList(mid + 1, in.children.size()));
                    in.keys.subList(mid, in.keys.size()).clear();
                    in.children.subList(mid + 1, in.children.size()).clear();
                    yield new Split(up, sibling);
                }
            };
        }
    }

    // keys.get(i) is a boxed Integer. Compared with an int, as everywhere here, it's unboxed and compared by value.
    // Two Integers compared with == are compared as references, which is only right for small values: a classic trap.
    static int find(List<Integer> keys, int key) {
        int lo = 0;
        int hi = keys.size();
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (keys.get(mid) < key) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    static int child(Internal node, int key) {
        int i = 0;
        while (i < node.keys.size() && key >= node.keys.get(i)) i++;
        return i;
    }

    public static List<String> usablePrefix(List<String> index, Set<String> equal, Set<String> ranges) {
        List<String> used = new ArrayList<>();
        for (String column : index) {
            if (equal.contains(column)) used.add(column);
            else if (ranges.contains(column)) {
                used.add(column);
                break;
            } else break;
        }
        return used;
    }
}
