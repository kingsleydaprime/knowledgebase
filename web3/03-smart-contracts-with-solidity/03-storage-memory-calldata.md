---
id: 862c7b7c-f646-4941-ad9d-55a2c829016b
---

# Storage, Memory and Calldata

## The kid version first
<!-- bite: 6c5a9cfd-7cf4-4646-b8a5-f2c475fe82fc -->

Three places a value can live:

- **calldata** — the letter someone posted you. You can read it, you can't edit it, it's gone when you're done
- **memory** — your desk. Write freely, wiped when you leave the room
- **storage** — the filing cabinet. Survives forever, costs a fortune to write to

Confusing the desk with the filing cabinet is the bug. Using the filing cabinet when the desk would do is the waste.

## The reference-vs-copy rule
<!-- bite: 5be8581b-1954-4b11-8c70-f47afbf36de4 -->

This is the whole note in one code block:

```solidity
struct User { uint256 balance; bool active; }
mapping(address => User) public users;

function broken(address a) external {
    User memory u = users[a];   // COPY — u lives on the desk
    u.balance = 100;            // edits the copy
}                               // copy discarded. users[a] IS UNCHANGED.

function works(address a) external {
    User storage u = users[a];  // POINTER into the filing cabinet
    u.balance = 100;            // writes through to state
}
```

**Both compile. Both run. One does nothing.** No warning, no revert — the transaction succeeds and the state is unchanged. This is the single most common "why isn't my contract working" bug, and it's why `storage` vs `memory` on a local variable is worth a second look in every review.

The rule underneath:

| Assignment | Result |
|---|---|
| `storage` → `storage` (local) | **Reference.** Writes go through |
| `storage` → `memory` | **Copy.** Writes are discarded |
| `memory` → `memory` | **Reference.** Both names point at the same data |
| `calldata` → `memory` | **Copy** |
| anything → a state variable | **Copy** — a full deep copy into storage, and expensive |

Note row three: two `memory` variables alias each other. `memory` behaves like a pointer between locals but like a copy when it came from storage — inconsistent-feeling, but it follows from *when* the copy happens (at the storage boundary).

## Function parameters: use `calldata`
<!-- bite: 751ad52e-7e69-4a5e-8c23-ef09498f5e6a -->

```solidity
function a(uint256[] memory data)   external { }   // copies the whole array into memory
function b(uint256[] calldata data) external { }   // reads directly from the tx input
```

**`b` is strictly cheaper for `external` functions** and the difference grows linearly with array size — for a large array it's thousands of gas. Use `calldata` unless you need to mutate the argument.

Constraints: `calldata` is only available for `external` (and `public`, since 0.6.9) function parameters, and it is immutable. `internal` and `public` functions callable internally need `memory`.

## Cache storage reads in loops
<!-- bite: e731c6ec-d608-4929-9c35-7a6f4727e0c4 -->

Each `SLOAD` costs 2100 gas cold, 100 warm. Each `SSTORE` costs 2900–20000. **Reading the same storage variable inside a loop pays every iteration:**

```solidity
// BAD — reads `items.length` and `total` from storage every iteration
for (uint256 i = 0; i < items.length; i++) {
    total += items[i].price;
}

// GOOD — one read, one write
uint256 len = items.length;          // one SLOAD
uint256 sum = total;                 // one SLOAD
for (uint256 i = 0; i < len; ) {
    sum += items[i].price;
    unchecked { ++i; }               // i cannot overflow — provable, so skip the check
}
total = sum;                         // one SSTORE
```

On a 100-item loop this is a five-figure gas saving, and the transformation is mechanical. **This pattern — hoist storage into locals, write back once — is most of practical gas optimisation** → [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]].

## The memory expansion trap
<!-- bite: 1f6461e5-7ba1-4df9-b406-a67e98ac57a7 -->

Memory is cheap **but its cost is quadratic** past 724 bytes:

```
cost ≈ 3 × words + words² / 512
```

For ordinary use it's negligible. For code that allocates large arrays — decoding big calldata, building a large return value, hashing a big buffer — it becomes the dominant cost, and it grows faster than you expect. **Memory is never freed within a call**, so allocating in a loop accumulates.

**Practical consequence:** a function that loops building a `memory` array of user-controlled length is a denial-of-service risk on itself. Bound the length explicitly.

## Transient storage (EIP-1153)
<!-- bite: 10f5da8c-44d9-44fe-bd1e-4bdb9e7a7fb0 -->

Since Dencun (2024), `TSTORE`/`TLOAD` provide storage that is **cleared at the end of the transaction** at roughly memory-like cost (100 gas).

The killer use is **reentrancy guards**: the classic guard costs ~20,000 gas on the first call because it writes a storage slot. A transient guard costs ~200. OpenZeppelin ships `ReentrancyGuardTransient`, and it's a straight upgrade where your toolchain supports the opcode. It's also the right tool for any within-transaction accumulator, such as flash-accounting in a pooled AMM.

## Key insight
<!-- bite: 04e1a56b-d28a-4a8d-ad14-d18e1fedbb9a -->

**`memory` vs `storage` is not a performance hint — it changes program semantics.** One writes to the chain, the other writes to a value about to be thrown away, and the compiler will not tell you which you meant. Read every declaration of a struct or array local and ask *"am I copying this, or pointing at it?"* — that question catches a whole bug class.

## Related
<!-- bite: a7dfe43a-16fe-4441-844a-50c71c8990b6 -->
- [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]] — where storage physically is
- [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]]
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]] — the four data locations at the opcode level

## About this lesson
<!-- bite: ece5d836-5cd7-4e60-9f3e-5c99b602092b -->

**Level:** Intermediate. **Covers:** the distinction that causes the most silent bugs and the most wasted gas in Solidity.

*Source: [reference] — Aug 2026.*
