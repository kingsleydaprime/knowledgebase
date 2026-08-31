# Ethereum as a State Machine

**[Intermediate]** — the account model in full, what a transaction actually contains, and the mental model that makes everything else in this folder obvious.

## The kid version first

Bitcoin is a ledger: it tracks who has what. **Ethereum is a computer**: it tracks who has what *and* what programs are stored, and it runs those programs when you poke them.

Every node runs the same programs on the same inputs and gets the same answer. That's why they agree. It's a computer with **thousands of copies, one shared memory, and a bill for every instruction.**

## The formal model, which is worth stating once

Ethereum is a **transaction-based state machine**:

```
σ(t+1)  =  Υ( σ(t),  T )
```

State σ, apply transaction T, get a new state. A block is a batch of these applied in order. **That's the entire protocol.** Everything else — gas, the EVM, contracts — is detail about what Υ does.

The consequence to internalise: **there is nothing outside σ.** No filesystem, no clock you can trust, no network calls, no ambient randomness. A contract can only see what's in the state and what the transaction handed it. This single constraint explains [[web3/06-building-dapps/06-oracles|oracles]], explains why on-chain randomness is hard, and explains why nothing is asynchronous.

## The world state

A map from 20-byte addresses to accounts. Two account types, one namespace:

```
EOA (externally owned)              Contract account
┌─────────────────────┐             ┌─────────────────────┐
│ nonce      (tx count)│            │ nonce   (contracts made)│
│ balance    (wei)     │            │ balance (wei)           │
│ storageRoot = empty  │            │ storageRoot ← its data  │
│ codeHash   = empty   │            │ codeHash    ← its code  │
└─────────────────────┘             └─────────────────────┘
   controlled by a private key         controlled by its code
```

**Only an EOA can originate a transaction.** Contracts are entirely reactive — they never wake up, never run on a timer, never poll. A contract that needs to act periodically requires someone to pay gas to call it, which is why "keeper" networks (Chainlink Automation, Gelato) exist as an entire product category.

**The nonce does double duty.** On an EOA it's a strictly incrementing transaction counter that prevents replay and forces ordering. On a contract it counts contracts created — because `CREATE` derives the new address from `keccak(sender, nonce)`, which is what makes contract addresses predictable before deployment.

## A transaction, field by field

```
nonce                 sender's next expected number — enforces ordering, blocks replay
to                    recipient; EMPTY means "deploy a contract"
value                 wei to transfer
data                  calldata — the function selector + arguments, or the init code
gasLimit              max gas you'll allow to be consumed
maxFeePerGas          most you'll pay per gas unit          ┐ EIP-1559
maxPriorityFeePerGas  tip to the proposer                   ┘
chainId               replay protection ACROSS chains
v, r, s               the signature
```

Two fields deserve attention:

**There is no `from` field.** The sender is *recovered* from the signature — a transaction is authenticated by construction, so anyone can relay it without being able to alter it → [[web3/01-foundations/03-cryptographic-primitives|recoverable signatures]].

**`chainId` (EIP-155) is why the same transaction can't be replayed on a forked chain.** Before it existed, a transaction on Ethereum was valid verbatim on Ethereum Classic. People lost money to exactly that.

## What actually happens when a transaction executes

```
1. Validate      signature, nonce matches, balance ≥ gasLimit × maxFee + value
2. Deduct        gasLimit × gasPrice is taken UP FRONT. You have pre-paid the worst case
3. Execute       transfer value; if `to` has code, run it in the EVM
4. Meter         each opcode decrements the gas counter
5a. Success      state changes commit; unused gas is refunded
5b. Revert       ALL state changes roll back — but the gas consumed is NOT refunded
6. Receipt       status, gas used, and logs are written; the receipts root goes in the header
```

**Step 5b is the one to remember: a revert undoes state but not payment.** A failed transaction is atomic with respect to state and non-atomic with respect to cost. That asymmetry funds the network's spam resistance — you cannot make nodes do work for free by deliberately failing.

## Internal transactions aren't transactions

When contract A calls contract B, that's a **message call** — it appears in no transaction list, has no hash of its own, and is only visible by tracing execution. Block explorers show them as "internal transactions," which is a helpful lie.

**This matters practically:** an application that detects incoming ETH by scanning transaction lists will miss every transfer that came from a contract. The reliable approaches are event logs or tracing → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

## Denominations

```
1 ether = 10^18 wei
1 gwei  = 10^9  wei     ← gas prices are quoted here
```

**All on-chain arithmetic is in wei, as integers.** Every float you see is a UI decision. Converting at the wrong layer, or converting twice, is a classic and expensive bug.

## Key insight

**Ethereum is a single-threaded, deterministic, metered computer with one global memory and no I/O.** Nearly everything that feels arbitrary — why contracts can't act on their own, why randomness needs an oracle, why gas exists, why calls are synchronous — is a direct consequence of "every node must compute the identical result, and must be able to stop a program that never halts."

## Related
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]] — what step 3 runs on
- [[web3/02-ethereum-and-the-evm/03-gas-and-fees|gas and fees]] — the metering
- [[web3/01-foundations/04-blocks-chains-and-state|blocks, chains and state]] — the account model vs UTXO
- [[foundations/compilers/09-bytecode-and-virtual-machines|bytecode VMs]] — the general shape of what the EVM is

*Source: [reference] — from the Yellow Paper and the execution specs. Aug 2026.*
