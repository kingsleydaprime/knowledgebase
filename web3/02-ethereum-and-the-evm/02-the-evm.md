# The EVM

**[Advanced]** — a 256-bit stack machine with four memory regions and a fuel gauge. What makes it unusual, and why its quirks show up in your Solidity.

## The kid version first

The EVM is a **very simple pretend computer**. It has no registers — just a stack you push things onto and pop them off. It has a scratchpad that's wiped after every call, and a hard drive that costs a fortune to write to. It counts every instruction and stops you when you run out of budget.

Thousands of machines run the identical program and get the identical answer, or the network breaks. **Boring and predictable is the entire design goal.**

## The unusual choices

| Choice | Why | What it costs you |
|---|---|---|
| **256-bit words** | Native size for Keccak hashes and addresses; makes big-number arithmetic native | Everything is 32 bytes. A `bool` occupies a full word. Real hardware is 64-bit, so **the EVM is slow to emulate** |
| **Stack machine, no registers** | Trivially simple to specify and reimplement identically | Awkward codegen; a hard **1024-item stack depth** limit, and "stack too deep" is a Solidity error you will meet |
| **No floating point** | IEEE-754 is not bit-identically reproducible across platforms | All maths is fixed-point by hand → [[web3/04-smart-contract-security/04-arithmetic-and-rounding\|arithmetic]] |
| **Metered execution** | Halting problem: you cannot decide in advance if a program terminates, so you charge it until it stops | Every loop is a cost risk |
| **Synchronous calls only** | Determinism — no scheduler, no concurrency | No async, no callbacks, no timers |

## The four data locations — the thing to actually learn

This is the highest-value section in the folder, because it's where the gas goes and where the bugs are.

| Location | Lifetime | Cost | Notes |
|---|---|---|---|
| **Stack** | One call | ~free (3 gas) | 1024 slots, top 16 reachable |
| **Memory** | One call | Cheap, but **quadratic** when it expands | Wiped between calls. Byte-addressed, word-aligned |
| **Storage** | **Forever** | **Brutal** | The contract's persistent key-value map |
| **Calldata** | One call | Cheapest to read | **Read-only** — the transaction's input bytes |

**Storage costs, which drive most gas optimisation:**

```
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

You will not write bytecode, but these appear in every stack trace, gas report and audit:

- **`CALL`** — call another contract. Passes value, **gives it a fresh memory and its own storage context**
- **`STATICCALL`** — call, but revert if the callee attempts any state change. This is what `view` compiles to, and it's a genuine safety boundary
- **`DELEGATECALL`** — **run another contract's code in *your* storage, with *your* `msg.sender`.** Powers libraries and every proxy upgrade pattern, and is the single most dangerous opcode in the machine → [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|proxies]]
- **`CREATE` / `CREATE2`** — deploy. `CREATE2` derives the address from a salt instead of the nonce, so **the address is known before deployment** — the basis of counterfactual wallets
- **`SELFDESTRUCT`** — largely neutered by EIP-6780 (Dencun, 2024); it no longer deletes code except in the same transaction that created it. Old tutorials are wrong about this
- **`LOG0`–`LOG4`** — emit an event. Written to the receipt, **not readable from any contract**, and far cheaper than storage
- **`REVERT`** — abort, roll back state, return an error, refund remaining gas. `assert`-style failures use `INVALID` and burn everything instead

## Precompiles

A handful of addresses (`0x01`–`0x0a`) aren't contracts but native implementations, because doing the maths in EVM opcodes would be absurdly expensive:

`0x01 ecrecover` · `0x02 SHA-256` · `0x05 modexp` · `0x06/07/08 BN254 curve ops (the pairing that makes zk verification affordable)` · `0x0a KZG point evaluation (added for blobs)`.

**Precompiles are how expensive cryptography becomes viable on-chain** — a zk-SNARK verifier is practical only because the pairing check is native → [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zero-knowledge proofs]].

## Contract deployment, which surprises people

The `data` of a deployment transaction is **not** the contract's code — it's **init code**, a program that *runs* and whose *return value* becomes the stored code.

```
deploy tx ──► EVM runs the init code ──► it returns runtime bytecode ──► that gets stored
              (this is where the constructor executes)
```

Two consequences: **the constructor is not part of the deployed contract** (you cannot call it again, and it isn't in the code you see on-chain), and **a contract's own code is not yet stored while its constructor runs** — so `address.code.length == 0` is true for a contract calling out from its constructor. That check has been used to defeat "is this an EOA?" guards, and it's why such guards are a bad idea → [[web3/04-smart-contract-security/03-access-control-and-key-management|access control]].

## Key insight

**The EVM's strangeness is not accidental — every quirk buys determinism or bounded execution.** 256-bit words, no floats, no concurrency, no I/O, and gas metering are all the same answer to one requirement: *thousands of machines must compute the identical result, and none of them may be made to run forever.* Read the design that way and the awkwardness stops being arbitrary.

## Related
- [[web3/02-ethereum-and-the-evm/03-gas-and-fees|gas and fees]] · [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]]
- [[foundations/compilers/09-bytecode-and-virtual-machines|bytecode VMs]] · [[foundations/compilers/README|compilers]] — Solidity is a compiler target problem
- [[foundations/computer-architecture/03-instruction-sets|instruction sets]] — the contrast with real ISAs
- [[build-your-own-shit/15-your-own-smart-contract-vm|build your own smart contract VM]]

*Source: [reference] — from the Yellow Paper, evm.codes, and the execution specs. Aug 2026.*
