# Indexing and Events

**[Intermediate]** — why you cannot query a blockchain, and the infrastructure everyone ends up building.

## The problem, stated once

**A blockchain has no query language.** It answers exactly two kinds of question:

- "What is the value at this storage slot, right now?"
- "Give me the logs in this block range matching these topics"

It cannot answer *"all NFTs owned by this address"*, *"the 10 largest trades this week"*, *"this user's transaction history"*, or *"total volume by day."* **Every one of those requires reading the whole chain and building your own index.**

This surprises people badly and late. **The chain is a write-optimised append-only log with point lookups — it is not a database**, and every list view in your UI needs infrastructure the chain does not provide → [[web3/01-foundations/04-blocks-chains-and-state|state models]].

## Why not just use `eth_getLogs`?

You can, up to a point, and then you can't:

- **Providers cap the block range** (commonly 2,000–10,000 blocks — hours, not months)
- **Bloom filters produce false positives**, so the node opens and scans candidate blocks anyway → [[web3/03-smart-contracts-with-solidity/05-events-and-logs|the bloom filter]]
- **No aggregation, no joins, no sorting, no pagination.** You get raw logs
- **No historical state.** "What was this balance in March?" needs an archive node and a call per block

Fine for "the last 100 transfers." Hopeless for anything a real product needs.

## The shape of the answer

Every indexer is the same pipeline:

```
   chain
     │ replay historical logs from block N, then follow the head
     ▼
  handler code — decode the event, apply business logic
     │
     ▼
  Postgres  ──►  GraphQL / REST  ──►  your frontend
```

**You are building a read model over an event stream.** It's [[architecture/03-architectural-patterns/README|CQRS/event sourcing]], with the chain as an immutable event log you don't control — which is a genuinely clean fit, and worth recognising because all the usual patterns and pitfalls apply.

## The options

| Option | What it is | When |
|---|---|---|
| **The Graph** | Subgraphs in AssemblyScript, decentralised network. The incumbent | Standard needs, wide chain support, you want it hosted |
| **Ponder** | TypeScript, self-hosted, Postgres, hot reload | **The best DX.** Custom logic, existing TS stack |
| **Envio / SubQuery** | Similar, performance-focused | Very large histories |
| **Alchemy/Moralis APIs** | Prebuilt endpoints for balances, NFTs, transfers | **Fastest start.** Skip building anything if a prebuilt endpoint fits |
| **Roll your own** | Poll logs, write to Postgres | Simple needs; **you will reimplement reorg handling and get it wrong** |

**Start with a prebuilt API.** "All NFTs owned by X" and "all token balances for X" are solved problems available as one HTTP call, and building a subgraph for them is a waste.

A Ponder handler is about as simple as this gets:

```ts
ponder.on('ERC20:Transfer', async ({ event, context }) => {
  await context.db.insert(transfers).values({
    id: event.log.id,
    from: event.args.from,
    to: event.args.to,
    amount: event.args.value,
    timestamp: event.block.timestamp,
  })
})
```

## Reorgs — the part everyone gets wrong

**A block you indexed can be un-happened.** The chain reorganises; your database now contains events that never occurred.

```
index block 100 → credit a user 500 tokens
block 100 is reorged out
your database says they have 500 tokens. The chain says they never did.
```

The strategies:

1. **Wait for finality.** Only index blocks tagged `finalized` (~13 min on Ethereum). Simplest and correct; costs latency
2. **Index optimistically, roll back on reorg.** Track block hashes; when a parent hash doesn't match what you stored, unwind to the fork point and re-index. **This is what good indexers do for you**, and it's the main reason not to roll your own
3. **Two-tier.** Serve finalized data authoritatively and recent data as provisional, marked as such in the UI

**Never ignore `log.removed`.** Handling reorgs is the single strongest argument for using an existing indexer rather than writing a log-polling loop.

## Designing contracts for indexability

**This is a contract-design decision that costs nothing at write time and cannot be fixed after deployment:**

- **Emit an event for every state change.** An unlogged mutation is invisible to every off-chain consumer, permanently
- **Index the fields people will filter by** — addresses and IDs, not amounts. You get three indexed slots; spend them deliberately
- **Emit old *and* new values** on parameter changes, so history is reconstructible
- **Include everything needed to interpret the event.** An indexer shouldn't have to make an archive-node call per event to figure out what happened — that's the difference between an indexer that syncs in minutes and one that takes days
- **Follow the standard event signatures exactly.** Every explorer, wallet and generic indexer watches for the canonical ERC-20/721 events; a token that doesn't emit them is invisible to all of them

## What to index

Not everything. Index what your UI queries:

```
entities:  User, Position, Trade, DailyStats
```

**Compute aggregates at write time**, not query time — running totals, daily rollups, current positions. The handler runs once per event; the query runs on every page load.

## Key insight

**The chain is a log; your product needs a database; the indexer is the thing that turns one into the other — and it's infrastructure you own and operate.** Budget for it from the start, because "how do we show a list of things?" has no answer at the contract layer, and the decisions that make indexing possible (which events, which indexed fields) are made in the contract and become permanent at deployment.

## Related
- [[web3/03-smart-contracts-with-solidity/05-events-and-logs|events and logs]] — the producer side
- [[web3/06-building-dapps/01-the-dapp-architecture|the dapp architecture]]
- [[architecture/03-architectural-patterns/README|architectural patterns]] — CQRS and event sourcing
- [[databases/README|databases]] — where the read model lives
