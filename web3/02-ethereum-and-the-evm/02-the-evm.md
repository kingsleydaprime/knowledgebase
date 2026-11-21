---
id: bf72b7f1-6c72-4042-bc38-cf740e851281
---

# The EVM

The EVM, or Ethereum Virtual Machine, is the very simple pretend computer that runs every Ethereum program. Thousands of machines run the same program and must get exactly the same answer, so it is built to be boring and predictable. This lesson looks at how it stores and works with data, and why it was built that way.

## The kid version first
<!-- bite: f84cfe29-213d-4a44-9aa3-f3a68465be41 -->

The EVM is a **very simple pretend computer**. It has no registers — just a stack you push things onto and pop them off. It has a scratchpad that's wiped after every call, and a hard drive that costs a fortune to write to. It counts every instruction and stops you when you run out of budget.

Thousands of machines run the identical program and get the identical answer, or the network breaks. **Boring and predictable is the entire design goal.**

## The unusual choices
<!-- bite: ffa64754-1818-490d-a1bc-b30b0f54fb11 -->

| Choice | Why | What it costs you |
|---|---|---|
| **256-bit words** | Native size for Keccak hashes and addresses; makes big-number arithmetic native | Everything is 32 bytes. A `bool` occupies a full word. Real hardware is 64-bit, so **the EVM is slow to emulate** |
| **Stack machine, no registers** | Trivially simple to specify and reimplement identically | Awkward codegen; a hard **1024-item stack depth** limit, and "stack too deep" is a Solidity error you will meet |
| **No floating point** | IEEE-754 is not bit-identically reproducible across platforms | All maths is fixed-point by hand → [[web3/04-smart-contract-security/04-arithmetic-and-rounding\|arithmetic]] |
| **Metered execution** | Halting problem: you cannot decide in advance if a program terminates, so you charge it until it stops | Every loop is a cost risk |
| **Synchronous calls only** | Determinism — no scheduler, no concurrency | No async, no callbacks, no timers |

## The four data locations — the thing to actually learn
<!-- bite: b6ba6a67-77cd-4ca9-8745-0c1eeafeb58c -->

This is the highest-value section in the folder, because it's where the gas goes and where the bugs are.

| Location | Lifetime | Cost | Notes |
|---|---|---|---|
| **Stack** | One call | ~free (3 gas) | 1024 slots, top 16 reachable |
| **Memory** | One call | Cheap, but **quadratic** when it expands | Wiped between calls. Byte-addressed, word-aligned |
| **Storage** | **Forever** | **Brutal** | The contract's persistent key-value map |
| **Calldata** | One call | Cheapest to read | **Read-only** — the transaction's input bytes |

**Storage costs, which drive most gas optimisation:**

```text
SSTORE  zero → non-zero      20,000 gas   ← creating state
SSTORE  non-zero → non-zero   2,900 gas   ← updating it
SSTORE  non-zero → zero       2,900 gas, plus a 4,800 gas REFUND
SLOAD   first access in a tx  2,100 gas   ("cold")
SLOAD   subsequent            100 gas     ("warm")
MSTORE  memory write              3 gas
```

**Storage is roughly 1000× the cost of memory.** That single ratio explains most of what looks like weird Solidity: packing variables into shared slots, caching a storage value in a local before a loop, emitting an event instead of storing data, and using `calldata` rather than `memory` for function arguments → [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]].

The cold/warm distinction is **EIP-2929**, introduced to price DoS-shaped access patterns correctly. It's why the *first* read of an address or slot in a transaction is much more expensive than the second.

## Opcodes worth knowing by name
<!-- bite: bdddd42b-035e-4ea2-93c8-83997045cf80 -->

You will not write bytecode, but these appear in every stack trace, gas report and audit:

- **`CALL`** — call another contract. Passes value, **gives it a fresh memory and its own storage context**
- **`STATICCALL`** — call, but revert if the callee attempts any state change. This is what `view` compiles to, and it's a genuine safety boundary
- **`DELEGATECALL`** — **run another contract's code in *your* storage, with *your* `msg.sender`.** Powers libraries and every proxy upgrade pattern, and is the single most dangerous opcode in the machine → [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]]
- **`CREATE` / `CREATE2`** — deploy. `CREATE2` derives the address from a salt instead of the nonce, so **the address is known before deployment** — the basis of counterfactual wallets
- **`SELFDESTRUCT`** — largely neutered by EIP-6780 (Dencun, 2024); it no longer deletes code except in the same transaction that created it. Old tutorials are wrong about this
- **`LOG0`–`LOG4`** — emit an event. Written to the receipt, **not readable from any contract**, and far cheaper than storage
- **`REVERT`** — abort, roll back state, return an error, refund remaining gas. `assert`-style failures use `INVALID` and burn everything instead

## Precompiles
<!-- bite: ef21dfc1-e719-4674-84da-07dbefc5e9ce -->

A handful of addresses (`0x01`–`0x0a`) aren't contracts but native implementations, because doing the maths in EVM opcodes would be absurdly expensive:

`0x01 ecrecover` · `0x02 SHA-256` · `0x05 modexp` · `0x06/07/08 BN254 curve ops (the pairing that makes zk verification affordable)` · `0x0a KZG point evaluation (added for blobs)`.

**Precompiles are how expensive cryptography becomes viable on-chain** — a zk-SNARK verifier is practical only because the pairing check is native → [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zero-knowledge proofs]].

## Contract deployment, which surprises people
<!-- bite: 28db04fd-158d-40cb-a875-e05b8047fc44 -->

The `data` of a deployment transaction is **not** the contract's code — it's **init code**, a program that *runs* and whose *return value* becomes the stored code.

```text
deploy tx ──► EVM runs the init code ──► it returns runtime bytecode ──► that gets stored
              (this is where the constructor executes)
```

Two consequences: **the constructor is not part of the deployed contract** (you cannot call it again, and it isn't in the code you see on-chain), and **a contract's own code is not yet stored while its constructor runs** — so `address.code.length == 0` is true for a contract calling out from its constructor. That check has been used to defeat "is this an EOA?" guards, and it's why such guards are a bad idea → [[web3/04-smart-contract-security/03-access-control-and-key-management|access control]].

## Key insight
<!-- bite: b58b1fbf-1302-4918-8579-fa8c0dcdcfb2 -->

**The EVM's strangeness is not accidental — every quirk buys determinism or bounded execution.** 256-bit words, no floats, no concurrency, no I/O, and gas metering are all the same answer to one requirement: *thousands of machines must compute the identical result, and none of them may be made to run forever.* Read the design that way and the awkwardness stops being arbitrary.

## Related
<!-- bite: 7d2dd7ec-28be-4119-a290-370017a32349 -->
- [[web3/02-ethereum-and-the-evm/03-gas-and-fees|gas and fees]] · [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]]
- [[compilers/10-bytecode-and-virtual-machines|bytecode VMs]] · [[compilers/index|compilers]] — Solidity is a compiler target problem
- [[computer-architecture/03-instruction-sets|instruction sets]] — the contrast with real ISAs
- [[build-your-own-shit/15-your-own-smart-contract-vm|build your own smart contract VM]]

## About this lesson
<!-- bite: bb857a63-523a-4a8c-ac69-b9907d076de2 -->

**Level:** Advanced. **Covers:** a 256-bit stack machine with four memory regions and a fuel gauge. What makes it unusual, and why its quirks show up in your Solidity.

*Source: [reference] — from the Yellow Paper, evm.codes, and the execution specs. Aug 2026.*
