---
id: 73b1dfd1-c1d0-4bfa-89b0-f89361b2b36d
---

# Storage Layout and the State Trie

Contract storage is the place where an Ethereum program keeps its data, set out as a huge row of numbered boxes. The compiler decides which box each piece of data goes in by counting them in the order you wrote them. So moving one line of code around can make a live program read the wrong data, and this lesson shows how to avoid that.

## The kid version first
<!-- bite: 77d63fa8-586c-4f72-8f8e-4a468dd2a026 -->

A contract's storage is **not** a set of named variables. It's a giant array of numbered boxes — 2²⁵⁶ of them, all initially zero. The compiler decides which box each variable lives in, **by counting declarations in order.**

Which means: **if you reorder your variable declarations, the same data is now in different boxes** — and to a contract that was already deployed with data in it, that's catastrophic.

## Slots, and packing
<!-- bite: 8fe6a0de-c4eb-436d-ab18-745e612436da -->

Storage is `mapping(uint256 slot => bytes32 value)`. Variables are assigned slots in declaration order, and **the compiler packs multiple small variables into one slot when they fit**:

```solidity
contract Example {
    uint256 a;      // slot 0 — full slot
    uint128 b;      // slot 1, bytes 0-15   ┐ packed together
    uint128 c;      // slot 1, bytes 16-31  ┘
    bool    d;      // slot 2, byte 0       ┐
    address e;      // slot 2, bytes 1-20   ┘ packed (1 + 20 = 21 ≤ 32)
    uint256 f;      // slot 3 — doesn't fit in slot 2, starts fresh
}
```

**This is the single highest-leverage gas optimisation available**, because it's free: reorder declarations so small types are adjacent, and you save 20,000 gas per slot you avoid creating. The above uses 4 slots; declared as `uint256, uint128, bool, address, uint128, uint256` it would use 6.

Two caveats worth knowing: packing costs a little extra gas to *read* (a mask and shift), so it wins only when you're saving whole slots; and **variables packed together are read and written together**, so writing one member of a packed slot reads-modifies-writes the whole slot.

## Mappings and arrays — where hashing comes in
<!-- bite: 6ff5ac62-9989-4663-b8b8-15dbb9309825 -->

Dynamic structures can't be laid out sequentially, so their locations are **derived by hashing**:

```text
mapping at slot p, key k        →  keccak256(abi.encode(k, p))
dynamic array at slot p         →  length lives at p
                                   element i lives at keccak256(p) + i
nested mapping                  →  keccak256(k2, keccak256(k1, p))
```

Consequences that matter:

- **Mapping storage is not enumerable.** There is no "list all keys" — the slots are scattered pseudo-randomly across the 2²⁵⁶ space. If you need iteration you must maintain a separate array yourself, and pay for both
- **A mapping's slot `p` itself stores nothing.** It's only an input to the hash
- **Collisions are cryptographically impossible**, which is what makes this safe. It's the same argument that makes content addressing work → [[web3/01-foundations/03-cryptographic-primitives|primitives]]

## Why this destroys upgrades
<!-- bite: 74788866-f7d2-4430-b37d-7aadd4701dfb -->

A [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxy]] uses `DELEGATECALL`: the proxy holds the storage, the implementation supplies the code. **The implementation's variable declarations decide which slots it reads — but it reads the proxy's storage.**

```text
V1:  address owner;   // slot 0
     uint256 total;   // slot 1

V2:  uint256 total;   // slot 0  ← now reads the OWNER slot as a number
     address owner;   // slot 1  ← now reads the TOTAL slot as an address
```

Deploy V2 and `owner` becomes whatever integer was in `total`, reinterpreted as an address. **The contract is now owned by nobody, or by an attacker who can compute the value.** This is not hypothetical; storage-collision bugs have bricked live protocols.

The rules that follow, and they are hard rules:
1. **Never reorder, never change the type of, and never remove an existing variable.** Append only
2. **Reserve gap space** — `uint256[50] private __gap;` at the end of base contracts, so inheritance can grow without shifting children
3. **Use unstructured storage for the proxy's own fields.** ERC-1967 places the implementation address at `keccak256("eip1967.proxy.implementation") - 1` — a slot no compiler will ever assign, so it cannot collide with application variables
4. **Run a storage-layout diff in CI.** OpenZeppelin's upgrades plugin and `forge inspect <C> storageLayout` both do this, and it is the check that actually prevents the bug

## The state trie — how it's all committed
<!-- bite: 681423d2-d25f-42ed-a53f-73ef44a91663 -->

Ethereum's global state is a **Merkle Patricia Trie**: a radix trie whose nodes are addressed by hash. Each account's storage is its own trie, whose root sits in the account, which sits in the global trie, whose root sits in the block header.

```text
block header
   └─ stateRoot
        └─ account (keyed by keccak(address))
             ├─ nonce, balance, codeHash
             └─ storageRoot
                  └─ storage slots (keyed by keccak(slot))
```

Why a *Patricia* trie rather than a plain Merkle tree: it's a **map**, so it proves "key K has value V" *and* proves **absence** — "no account exists at this address." Absence proofs are what let a light client trust a negative answer, and a plain Merkle tree cannot give you one.

The cost is real and openly acknowledged: every state write updates a path of nodes up to the root, so a single `SSTORE` touches multiple database nodes and causes heavy random I/O. **This is the main reason archive nodes are enormous and syncing is slow**, and it's why Verkle trees — with far smaller proofs, enabling stateless clients — have been on Ethereum's roadmap for years → [[web3/02-ethereum-and-the-evm/06-the-ethereum-roadmap|the roadmap]].

## Inspecting it yourself
<!-- bite: 5401d000-1a6f-474e-8bf1-8dde8a6b0e2d -->

```bash
forge inspect MyContract storageLayout      # slot-by-slot map, use this in CI
cast storage <address> <slot> --rpc-url $RPC   # read a live slot
```

Reading the layout of a contract you wrote is a five-minute exercise that makes this note concrete, and it's worth doing once.

## Key insight
<!-- bite: 276dd02d-e414-492f-b844-079263051aa5 -->

**Solidity's variables are a naming convention over a numbered array, and the numbering is positional.** Everything downstream — why packing saves thousands of gas, why mappings can't be iterated, why upgrades have an append-only rule enforced by CI — follows from the compiler assigning slots by counting declarations rather than by name.

## Related
<!-- bite: 7350760d-b52b-4108-aa4a-3a414a64031c -->
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]] — the cost of touching storage
- [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|upgradeability and proxies]] — where this becomes dangerous
- [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]]
- [[dsa/02-data-structures/06-trees/01-trees|trees and tries]]

## About this lesson
<!-- bite: aa3a7ffe-fa48-434d-964d-f970cfd2751e -->

**Level:** Advanced. **Covers:** where a contract's variables physically live, and why that determines both your gas bill and whether an upgrade destroys your data.

*Source: [reference] — Aug 2026.*
