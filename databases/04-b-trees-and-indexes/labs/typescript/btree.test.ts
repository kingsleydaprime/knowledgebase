import { test } from "node:test";
import assert from "node:assert/strict";
import { BPlusTree, levels, usablePrefix } from "./btree.ts";

test("why not a binary tree", () => {
  assert.equal(Math.ceil(Math.log2(1e8)), 27);
  assert.deepEqual([levels(1e8, 367, 400), levels(1e6, 367, 400)], [4, 3]);
});

test("splits keep every leaf at the same depth, and a lookup reads one page per level", () => {
  const tree = new BPlusTree<string>(3);
  for (let k = 1; k <= 10; k++) tree.insert(k, `v${k}`);
  assert.equal(tree.height, 3);
  assert.deepEqual(tree.root.keys, [7]);
  assert.deepEqual(tree.search(7), ["v7", 3]);
  assert.deepEqual(tree.search(99), [undefined, 3]);
  assert.deepEqual(tree.range(4, 8), [["v4", "v5", "v6", "v7", "v8"], 6]);
});

test("a million keys, three pages", () => {
  const tree = new BPlusTree<number>(400);
  for (let i = 0; i < 1_000_000; i++) tree.insert((i * 7919) % 1_000_000, i); // every key once, in a scrambled order
  assert.equal(tree.height, 3);
  assert.equal(tree.search(424_242)[1], 3);
});

test("the leftmost prefix rule", () => {
  const index = ["a", "b", "c"];
  const check = (eq: string[], ranges: string[]) => usablePrefix(index, new Set(eq), new Set(ranges));
  assert.deepEqual(check(["a"], []), ["a"]);
  assert.deepEqual(check(["a", "b", "c"], []), ["a", "b", "c"]);
  assert.deepEqual(check(["b"], []), []);
  assert.deepEqual(check(["a", "c"], []), ["a"]);
  assert.deepEqual(check(["b"], ["a"]), ["a"]);
  assert.deepEqual(check(["a"], ["b"]), ["a", "b"]);
});
