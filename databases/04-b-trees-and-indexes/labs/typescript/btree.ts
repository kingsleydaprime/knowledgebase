// btree.ts — a B+ tree you can watch, the arithmetic of its height, and the leftmost-prefix rule.
// The same model as the Python lab: one node is one page, and every node visited counts as one page read.

export function levels(rows: number, keysPerLeaf: number, fanout: number): number {
  const leaves = Math.ceil(rows / keysPerLeaf);
  return 1 + Math.max(0, Math.ceil(Math.log(leaves) / Math.log(fanout) - 1e-12));
}

interface Leaf<V> {
  kind: "leaf";
  keys: number[];
  values: V[];
  next?: Leaf<V>; // the leaves form a linked list, for range scans
}

interface Internal<V> {
  kind: "internal";
  keys: number[]; // routing only: children[i] holds keys below keys[i]
  children: Node<V>[];
}

type Node<V> = Leaf<V> | Internal<V>;

/** Keys and values live only in the leaves. A node holds at most `maxKeys` keys; one more and it splits. */
export class BPlusTree<V> {
  root: Node<V> = { kind: "leaf", keys: [], values: [] };
  height = 1;
  #maxKeys: number;

  constructor(maxKeys: number) {
    if (maxKeys < 3) throw new RangeError("maxKeys must be at least 3");
    this.#maxKeys = maxKeys;
  }

  /** The value (or undefined) and the pages read: always `height`, because every leaf is at the same depth. */
  search(key: number): [V | undefined, number] {
    let node = this.root;
    let pages = 1;
    while (node.kind === "internal") {
      node = node.children[child(node, key)];
      pages++;
    }
    const i = find(node.keys, key);
    return [node.keys[i] === key ? node.values[i] : undefined, pages];
  }

  /** Values for lo <= key <= hi, and pages read: down the tree once, then along the leaf chain. */
  range(lo: number, hi: number): [V[], number] {
    let node: Node<V> = this.root;
    let pages = 1;
    while (node.kind === "internal") {
      node = node.children[child(node, lo)];
      pages++;
    }
    const found: V[] = [];
    for (let leaf: Leaf<V> | undefined = node; leaf; ) {
      for (let i = 0; i < leaf.keys.length; i++) {
        if (leaf.keys[i] > hi) return [found, pages];
        if (leaf.keys[i] >= lo) found.push(leaf.values[i]);
      }
      leaf = leaf.next;
      if (leaf) pages++;
    }
    return [found, pages];
  }

  insert(key: number, value: V): void {
    const split = this.#insert(this.root, key, value);
    if (split) {
      this.root = { kind: "internal", keys: [split[0]], children: [this.root, split[1]] }; // the tree grows a level
      this.height++;
    }
  }

  #insert(node: Node<V>, key: number, value: V): [number, Node<V>] | undefined {
    if (node.kind === "leaf") {
      const i = find(node.keys, key);
      if (node.keys[i] === key) {
        node.values[i] = value;
        return undefined;
      }
      node.keys.splice(i, 0, key);
      node.values.splice(i, 0, value);
      if (node.keys.length <= this.#maxKeys) return undefined;
      const mid = node.keys.length >> 1; // the right half's first key is copied up
      const right: Leaf<V> = { kind: "leaf", keys: node.keys.splice(mid), values: node.values.splice(mid), next: node.next };
      node.next = right;
      return [right.keys[0], right];
    }
    const i = child(node, key);
    const split = this.#insert(node.children[i], key, value);
    if (!split) return undefined;
    node.keys.splice(i, 0, split[0]);
    node.children.splice(i + 1, 0, split[1]);
    if (node.keys.length <= this.#maxKeys) return undefined;
    const mid = node.keys.length >> 1; // an internal split moves the middle key up rather than copying it
    const up = node.keys[mid];
    const sibling: Internal<V> = { kind: "internal", keys: node.keys.splice(mid + 1), children: node.children.splice(mid + 1) };
    node.keys.pop(); // remove `up`, which now lives in the parent
    return [up, sibling];
  }
}

function find(keys: number[], key: number): number {
  let lo = 0;
  let hi = keys.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (keys[mid] < key) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

function child<V>(node: Internal<V>, key: number): number {
  let i = 0;
  while (i < node.keys.length && key >= node.keys[i]) i++;
  return i;
}

/** The index columns that narrow a search: equality columns from the left, then at most one range column. */
export function usablePrefix(index: string[], equal: Set<string>, ranges: Set<string>): string[] {
  const used: string[] = [];
  for (const column of index) {
    if (equal.has(column)) used.push(column);
    else if (ranges.has(column)) {
      used.push(column);
      break;
    } else break;
  }
  return used;
}
