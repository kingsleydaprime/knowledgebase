# Blocks, Chains and State

**[Intermediate]** — what is actually stored, the two rival models for representing ownership, and why "the blockchain stores your balance" is wrong in one of them.

## The kid version first

A blockchain is a **notebook where you can only ever add a new page**, and each new page has a stamp on it that's calculated from the page before. Tear out an old page and every stamp after it is wrong, visibly, to everyone.

The subtle bit: the notebook records **what happened**, not **what is**. "Alice paid Bob 5" — not "Alice has 12." What is true *now* is something you work out by replaying every page.

## A block, anatomically

```
┌─ Block header ────────────────────────────────┐
│  parent hash      ← the chain link            │
│  state root       ← Merkle root of ALL state  │
│  tx root          ← Merkle root of this block │
│  receipts root    ← Merkle root of outcomes   │
│  timestamp, number, difficulty/randomness     │
│  gas limit, gas used, base fee                │
└───────────────────────────────────────────────┘
┌─ Block body ──────────────────────────────────┐
│  [ tx, tx, tx, ... ]                          │
└───────────────────────────────────────────────┘
```

Two things to notice:

**The header is tiny and self-sufficient.** It's ~500 bytes in Ethereum, and it commits — via those Merkle roots — to megabytes of transactions and gigabytes of state. A [[web3/01-foundations/06-networking-and-nodes|light client]] syncs headers only, and can still verify any specific claim on demand.

**The header contains a *state* root, not just a transaction root.** That's an Ethereum design choice Bitcoin doesn't share, and it's what makes "prove account X has balance Y at block N" a cheap, standalone proof. The price is that every node recomputes the full state trie root on every block.

## The chain, and what "immutable" really means

Each block names its parent by hash. Rewriting block *N* changes its hash, which invalidates *N+1*'s parent pointer, which invalidates *N+2*… **you must redo the whole suffix.**

**Immutability is economic, not physical.** Nothing stops you rebuilding history — you simply have to out-produce the honest network while doing it. What makes the chain immutable is that this costs more than it's worth. Say "tamper-*evident* by construction, tamper-*resistant* by economics" and you'll be precise → [[web3/01-foundations/05-consensus|consensus]].

**Reorgs are normal, not exceptional.** Two valid blocks appear at nearly the same height; the network briefly disagrees; one branch wins and the other's blocks are orphaned. Any application reading chain data must handle **the block it just processed being un-happened**. Naïve indexers that treat block *N* as final the instant they see it produce corrupt data on every reorg → [[web3/06-building-dapps/04-indexing-and-events|indexing]].

## The two state models

This is the most important structural distinction in the field, and the one most tutorials skip.

### UTXO — Bitcoin's model

There are no accounts and **no balances stored anywhere.** There are only **unspent transaction outputs**: discrete chunks of value, each locked to a spending condition. A transaction consumes whole UTXOs and creates new ones.

```
Alice has: UTXO_a (3 BTC), UTXO_b (2 BTC)      ← her "balance" of 5 is derived
Alice pays Bob 4:
    inputs :  UTXO_a (3) + UTXO_b (2)  = 5     ← both consumed entirely
    outputs:  UTXO_c (4) → Bob
              UTXO_d (0.9) → Alice             ← "change", back to herself
              (0.1 unaccounted = the fee)
```

Your wallet balance is **a sum your wallet computes** by scanning for outputs it can spend. The chain never stores it.

- **+** Transactions touching disjoint UTXOs have no shared state, so they can be **validated in parallel** and reordered freely
- **+** Better privacy hygiene — a fresh address per output is natural
- **−** Awful for stateful programs. "A contract holding a balance that many users update" has no clean expression
- **−** Change outputs are a persistent source of user-facing bugs, and UTXO sets fragment into dust

### Account model — Ethereum's

A global key-value map from address to `{ nonce, balance, storageRoot, codeHash }`. A transfer **mutates two entries.** Two account types share one namespace:

- **EOA** (externally owned account) — controlled by a private key, no code. Only an EOA can *originate* a transaction
- **Contract account** — has code and storage, no key. It only ever acts when called

- **+** Natural for stateful applications. A token contract is just a mapping it owns
- **+** Balances are directly readable; no scanning
- **−** Transactions touching the same account conflict, so **execution is sequential** — a major reason Ethereum L1 throughput is what it is
- **−** Needs an explicit **nonce** per account (a strictly incrementing counter) to prevent replay, since transactions no longer consume unique inputs. UTXO gets replay protection free, because an output can only be spent once

Solana uses an account model with **declared read/write sets**, which restores parallel execution — the interesting middle path → [[web3/05-beyond-ethereum/04-solana-and-the-alternative-model|Solana]].

## State is derived, and that's the whole trick

**The chain stores transactions. State is what you get by executing them in order.** Everything else follows:

- **Determinism is mandatory.** Every node replays the same inputs and must reach a bit-identical state root. No wall-clock time, no randomness, no floating point, no filesystem, no network calls. This constraint is why the [[web3/02-ethereum-and-the-evm/02-the-evm|EVM]] looks the way it does, and why [[web3/06-building-dapps/06-oracles|oracles]] have to exist
- **Verification is cheap; trust is unnecessary.** Don't trust the state root — replay and check it
- **State grows monotonically and nobody pays for the growth.** This is **state bloat**, arguably Ethereum's hardest unsolved engineering problem: you pay gas once to write a storage slot, and every node stores it forever. Proposals like state expiry and statelessness address it; none has shipped as of 2026

## Key insight

**A blockchain is an append-only log, and the "current state" is a materialised view over it** — exactly the [[architecture/03-architectural-patterns/README|event-sourcing]] pattern, with consensus deciding the log order. Once you see it that way, reorgs, determinism and state bloat all stop being surprises and become the ordinary consequences of that architecture.

## Related
- [[web3/01-foundations/05-consensus|consensus]] — who appends the next block
- [[web3/02-ethereum-and-the-evm/01-the-world-computer|the world computer]] — the account model in full
- [[web3/05-beyond-ethereum/05-bitcoin-and-utxo|Bitcoin and UTXO]] — the other model, in depth
- [[databases/README|databases]] — WAL and MVCC are the same log-and-view shape
- [[build-your-own-shit/14-your-own-blockchain|build your own blockchain]]

*Source: [reference] — Aug 2026.*
