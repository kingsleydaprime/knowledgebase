# Gas and Fees

**[Intermediate]** — why metering exists at all, how EIP-1559 actually works, and the failure modes that cost people money.

## The kid version first

Every instruction has a price. Before your transaction runs, you say **"I'll allow at most this much"** and you pre-pay it. The machine counts down as it works. If it finishes, you get the change back. If it runs out mid-way, **the work is undone but the money is gone.**

The reason is simple: nobody can tell in advance whether a program will ever stop. So instead of asking, you charge it until it does.

## Why gas exists — the halting problem, priced

You cannot decide whether an arbitrary program terminates → [[foundations/theory-of-computation/06-decidability|decidability]]. On a network where every node must execute every program, an infinite loop is a network-wide denial of service.

**Gas converts an undecidable question into an economic one.** Rather than proving termination, you bound it: every operation costs, the budget is finite, and execution halts when the budget is exhausted. Simultaneously it prices resource use — storage costs more than arithmetic because storage burdens every node forever.

## The three numbers, and how they combine

```
gasLimit                max units you'll allow          → you choose
maxFeePerGas            max price per unit you'll pay   → you choose
maxPriorityFeePerGas    tip to the block proposer       → you choose

baseFee                 protocol-set price per unit     → the network sets this
```

The arithmetic when it executes:

```
effectiveGasPrice = min(maxFeePerGas, baseFee + maxPriorityFeePerGas)
total paid        = gasUsed × effectiveGasPrice
    of which        gasUsed × baseFee      is BURNED
                    gasUsed × priorityFee  goes to the proposer

refunded          = (gasLimit − gasUsed) × effectiveGasPrice
```

**`gasLimit` is a cap, not a price.** Setting it higher does not make you pay more and does not make you go faster — you're refunded the difference. Setting it too *low* is what hurts: you run out mid-execution, everything reverts, and **you pay for every unit consumed up to the failure.** Wallets estimate the limit by simulating, then add a margin; the estimate can be wrong when execution depends on state that changes before inclusion.

## EIP-1559 — the fee market that actually works

Before August 2021, fees were a blind first-price auction: guess what everyone else will bid, overpay or wait. EIP-1559 replaced it with an algorithmic price:

```
target = 15M gas per block, limit = 30M (blocks may be up to 2× target)

parent block above target  →  baseFee rises  (up to +12.5% per block)
parent block below target  →  baseFee falls  (up to −12.5% per block)
```

**The base fee is burned, not paid to anyone.** That was the controversial part and it's structurally important: burning removes the proposer's incentive to manufacture congestion, since inflating the base fee earns them nothing.

Three consequences worth carrying:

- **Fee prediction became tractable.** The base fee can change by at most 12.5% per 12-second block, so the next few blocks are predictable. Wallet fee estimates got dramatically better overnight
- **The burn can exceed issuance**, making ETH net-deflationary in busy periods. This is where "ultrasound money" comes from — a real mechanism with a silly name
- **The 2× elastic limit absorbs bursts** while the target keeps average block size sustainable

## Where gas actually goes

For a typical transaction, the split is unintuitive:

```
21,000        base cost of ANY transaction — signature recovery, nonce, overhead
4 / 16        per byte of calldata (zero / non-zero bytes)
20,000        per new storage slot written
2,900         per storage slot updated
2,100 / 100   per storage read (cold / warm)
375 + 375/topic + 8/byte    per event emitted
~3            per arithmetic op
```

**Arithmetic is essentially free; state is everything.** A loop doing ten thousand additions costs less than one `SSTORE`. This is exactly backwards from ordinary performance intuition, and it's why gas optimisation is almost entirely about *touching storage less* rather than *computing less* → [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]].

Since **EIP-4844** (Dencun, March 2024) there is a **second, separate fee market for blobs** — large data attachments used by rollups, priced independently and deleted after ~18 days. It cut L2 costs by an order of magnitude, and it's the reason L2 fees fell off a cliff in 2024 → [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]].

## The failure modes

**Out-of-gas mid-execution.** State rolls back, gas is consumed. The user sees a failed transaction and a real charge. Most common cause: a loop over an unbounded array that grew past the point where iteration fits in a block. **Any loop over user-extendable data is a latent liveness bug** — including one in a `withdraw` function, which can permanently trap funds.

**The block gas limit is a hard ceiling.** A transaction needing more gas than a whole block can never execute, at any price. Migration or settlement functions that loop over all users hit this and become permanently uncallable.

**Underpriced and stuck.** Set `maxFeePerGas` below the base fee and the transaction simply sits in the mempool. Because nonces must be sequential, **it also blocks every later transaction from that account.** The fix is to replace it: resubmit with the same nonce and at least a 10% higher fee (a "speed-up"), or send an empty self-transfer at that nonce to cancel it.

**Gas griefing.** A contract that forwards a fixed, insufficient gas stipend to an untrusted callee can be manipulated into failing in ways the caller didn't anticipate. The 2300-gas stipend from `.transfer()` was the classic case — it broke when smart-contract wallets became common, which is why **`.call{value: x}("")` with a reentrancy guard is now the correct way to send ETH**, and `.transfer()` is deprecated advice you'll still find in old tutorials.

## Key insight

**Gas is not a fee — it's a resource-accounting system that happens to be denominated in money.** Every price in the schedule encodes a real cost imposed on every node in the network, forever. Read the gas table and you're reading Ethereum's opinion about what is expensive, which is why optimising for it teaches you the machine.

## Related
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]] — what's being metered
- [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]] — acting on this
- [[foundations/theory-of-computation/06-decidability|decidability]] — the halting problem this prices around
- [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|rollups]] — the actual answer to high fees

*Source: [reference] — Aug 2026.*
