# Events and Logs

**[Intermediate]** — the write-only side channel that every frontend, indexer and block explorer depends on.

## The kid version first

Storage is the filing cabinet: expensive, and your contract can read it. **Events are shouting out the window**: cheap, permanently recorded, and **your contract can never hear its own shout.**

Anything the outside world needs to know but your code never needs to re-read should be shouted, not filed.

## Why they exist

Storage costs 20,000 gas per slot and burdens every node forever. Logs cost ~375 gas plus 8 per byte, and — crucially — **are not part of the state trie.** They live in transaction receipts, committed by the receipts root in the block header.

That's the trade: **~50× cheaper, at the cost of being unreadable from inside the EVM.** There is no `LOAD_LOG` opcode and there never will be, because logs aren't state.

## Syntax and the indexing rule

```solidity
event Transfer(address indexed from, address indexed to, uint256 value);

emit Transfer(msg.sender, recipient, amount);
```

An event compiles to `LOG0`–`LOG4`, where the number is how many **topics** it has:

```
topic0 = keccak256("Transfer(address,uint256,address)")  ← the event signature, always
topic1 = indexed param 1        ┐
topic2 = indexed param 2        ├ up to THREE indexed params (topic3 max)
topic3 = indexed param 3        ┘
data   = all non-indexed params, ABI-encoded together
```

**Indexed parameters are filterable; non-indexed are not.** `eth_getLogs` filters on topics only, so the choice of what to index is the choice of what anyone can ever query efficiently:

- **Index** addresses and IDs — the things people filter by ("all transfers to me")
- **Don't index** amounts and timestamps — you rarely filter on an exact amount, and indexing costs 375 extra gas each

**Indexing a dynamic type stores its hash, not its value.** `event Named(string indexed name)` gives you `keccak256(name)` in the topic — you can filter for a known string, but you can never recover the string from the log. If you need the value, emit it unindexed as well.

**Anonymous events** (`event X() anonymous`) drop topic0, freeing a fourth indexed slot and saving a little gas, at the cost of being unfilterable by name. Rare, and mostly seen in heavily gas-optimised code.

## What events are actually for

**1. Frontends.** You cannot subscribe to a storage variable. `eth_subscribe("logs", filter)` on events is how a UI learns something happened → [[web3/06-building-dapps/03-reading-and-writing-chain-state|reading chain state]].

**2. Indexers.** The Graph, Ponder, and every custom indexer build queryable databases by replaying logs. **A chain cannot answer "all transfers involving address X since January" — logs are how that question becomes answerable at all** → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

**3. Cheap historical record.** Data that must be provable later but never read on-chain — audit trails, off-chain-verifiable parameters — belongs in a log, not in storage. This is a real design tool and it's underused.

**4. Debugging.** Emit around suspect logic; the receipt shows the trace. Foundry's `console.log` is nicer during development but doesn't exist on a live chain.

## The bloom filter, and why `eth_getLogs` is slow

Each block header holds a **2048-bit bloom filter** over its logs' addresses and topics. A node checks the bloom to skip blocks that definitely contain no match.

Blooms have **false positives, never false negatives** — so a hit means "maybe," and the node must then open the block and check properly. With a large query range this degenerates into scanning, which is why:

- Public RPC providers cap `eth_getLogs` ranges (commonly 2,000–10,000 blocks)
- Wide historical queries time out
- **Anything beyond trivial history needs a real indexer**, not direct RPC

This is a genuine architectural constraint, and discovering it late is a common cause of rewrites → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

## Reorg safety — the part that bites in production

**Logs from a reorged-away block are gone**, and any consumer must handle it. `eth_getLogs` results carry a `removed: true` flag for exactly this, and most naive indexers ignore it.

```
saw log at block 100 → credited a user
block 100 reorged out → the log never happened → the credit is now fabricated
```

The correct patterns are **wait for N confirmations before acting** (simple, adds latency) or **track block hashes and roll back on mismatch** (correct, more work). The `finalized` block tag from the consensus layer gives an authoritative answer at ~13 minutes on Ethereum.

## Conventions worth following

- **Emit on every state change.** Silent mutations are invisible to every off-chain consumer, and auditors flag them
- **Emit *after* the effect**, at the end of the function, so a revert never leaves a misleading log — though since reverts discard logs entirely, this is about readability more than correctness
- **Include both old and new values** for parameter changes: `event FeeChanged(uint256 oldFee, uint256 newFee)`. Indexers reconstructing history will thank you
- **Follow the standards exactly.** ERC-20's `Transfer` and `Approval` signatures are what every wallet and explorer watches for. A token that doesn't emit them is invisible to the ecosystem, even if it otherwise works

## Key insight

**Events are the chain's only push mechanism, and the only affordable way to record history.** Contracts write them and can never read them — which makes the indexed/non-indexed decision permanent and consequential, because it determines what questions anyone will ever be able to ask about your contract's past.

## Related
- [[web3/06-building-dapps/04-indexing-and-events|indexing and events]] — the consumer side
- [[web3/03-smart-contracts-with-solidity/09-gas-optimisation|gas optimisation]] — logs vs storage as a design tool
- [[web3/02-ethereum-and-the-evm/02-the-evm|the EVM]] — the LOG opcodes

*Source: [reference] — Aug 2026.*
