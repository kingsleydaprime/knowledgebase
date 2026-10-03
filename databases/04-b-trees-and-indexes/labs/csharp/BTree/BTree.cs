// A B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule. Same model as the Python lab.

public static class Sizing
{
    public static int Levels(long rows, int keysPerLeaf, int fanout)
    {
        var leaves = Math.Ceiling((double)rows / keysPerLeaf);
        return 1 + Math.Max(0, (int)Math.Ceiling(Math.Log(leaves) / Math.Log(fanout) - 1e-12));
    }

    /// <summary>The index columns that narrow a search: equality columns from the left, then at most one range.</summary>
    public static List<string> UsablePrefix(IEnumerable<string> index, ISet<string> equal, ISet<string> ranges)
    {
        var used = new List<string>();
        foreach (var column in index)
        {
            if (equal.Contains(column)) used.Add(column);
            else
            {
                if (ranges.Contains(column)) used.Add(column);
                break;
            }
        }
        return used;
    }
}

public abstract class Node
{
    public List<int> Keys { get; } = [];
}

public sealed class Leaf : Node
{
    public List<string> Values { get; } = [];
    public Leaf? Next { get; set; } // the linked list for range scans
}

public sealed class Internal : Node
{
    public List<Node> Children { get; } = []; // Keys route: Children[i] holds keys below Keys[i]
}

public sealed class BPlusTree(int maxKeys)
{
    public Node Root { get; private set; } = new Leaf();
    public int Height { get; private set; } = 1;

    /// <summary>The value (null if absent) and the pages read: always the height.</summary>
    public (string? Value, int Pages) Search(int key)
    {
        var (leaf, pages) = Descend(key);
        var i = leaf.Keys.BinarySearch(key);
        return (i >= 0 ? leaf.Values[i] : null, pages);
    }

    public (List<string> Values, int Pages) Range(int lo, int hi)
    {
        var (leaf, pages) = Descend(lo);
        var found = new List<string>();
        for (Leaf? at = leaf; at is not null;)
        {
            for (var i = 0; i < at.Keys.Count; i++)
            {
                if (at.Keys[i] > hi) return (found, pages);
                if (at.Keys[i] >= lo) found.Add(at.Values[i]);
            }
            at = at.Next;
            if (at is not null) pages++;
        }
        return (found, pages);
    }

    private (Leaf, int) Descend(int key)
    {
        var (node, pages) = (Root, 1);
        while (node is Internal internalNode)
        {
            node = internalNode.Children[Child(internalNode, key)];
            pages++;
        }
        return ((Leaf)node, pages);
    }

    public void Insert(int key, string value)
    {
        if (Insert(Root, key, value) is not var (separator, right)) return;
        var top = new Internal(); // the tree grows a level
        top.Keys.Add(separator);
        top.Children.AddRange([Root, right]);
        Root = top;
        Height++;
    }

    private (int, Node)? Insert(Node node, int key, string value)
    {
        switch (node)
        {
            case Leaf leaf:
            {
                var i = leaf.Keys.BinarySearch(key);
                if (i >= 0)
                {
                    leaf.Values[i] = value;
                    return null;
                }
                leaf.Keys.Insert(~i, key); // BinarySearch returns the complement of the insertion point
                leaf.Values.Insert(~i, value);
                if (leaf.Keys.Count <= maxKeys) return null;
                var mid = leaf.Keys.Count / 2; // the right half's first key is copied up
                var right = new Leaf { Next = leaf.Next };
                right.Keys.AddRange(leaf.Keys[mid..]);
                right.Values.AddRange(leaf.Values[mid..]);
                leaf.Keys.RemoveRange(mid, leaf.Keys.Count - mid);
                leaf.Values.RemoveRange(mid, leaf.Values.Count - mid);
                leaf.Next = right;
                return (right.Keys[0], right);
            }
            case Internal internalNode:
            {
                var i = Child(internalNode, key);
                if (Insert(internalNode.Children[i], key, value) is not var (separator, right)) return null;
                internalNode.Keys.Insert(i, separator);
                internalNode.Children.Insert(i + 1, right);
                if (internalNode.Keys.Count <= maxKeys) return null;
                var mid = internalNode.Keys.Count / 2; // an internal split moves the middle key up
                var up = internalNode.Keys[mid];
                var sibling = new Internal();
                sibling.Keys.AddRange(internalNode.Keys[(mid + 1)..]);
                sibling.Children.AddRange(internalNode.Children[(mid + 1)..]);
                internalNode.Keys.RemoveRange(mid, internalNode.Keys.Count - mid);
                internalNode.Children.RemoveRange(mid + 1, internalNode.Children.Count - mid - 1);
                return (up, sibling);
            }
            default:
                throw new InvalidOperationException("unknown node");
        }
    }

    private static int Child(Internal node, int key)
    {
        var i = 0;
        while (i < node.Keys.Count && key >= node.Keys[i]) i++;
        return i;
    }
}
