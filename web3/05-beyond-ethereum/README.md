# Beyond Ethereum

**The rest of the landscape, and the scaling problem that produced most of it.** Read [[web3/02-ethereum-and-the-evm/README|section 02]] first — most of these designs are best understood as different answers to constraints Ethereum made visible.

## Reading order
1. [[web3/05-beyond-ethereum/01-the-scalability-trilemma|the-scalability-trilemma]] — **[Intermediate]** — why throughput is capped by the weakest verifier, how to deflate a TPS claim, and how rollups escape the constraint (partly)
2. [[web3/05-beyond-ethereum/02-layer-2s-and-rollups|layer-2s-and-rollups]] — **[Advanced]** — optimistic vs zk, rollup vs sidechain, and **the sequencer centralisation everyone glosses over**. Where you should actually be building
3. [[web3/05-beyond-ethereum/03-zero-knowledge-proofs|zero-knowledge-proofs]] — **[Advanced]** — why **succinctness matters more than the zero-knowledge part**, SNARKs vs STARKs, what's deployed, and the under-constraining footgun
4. [[web3/05-beyond-ethereum/04-solana-and-the-alternative-model|solana-and-the-alternative-model]] — **[Advanced]** — parallel execution via declared accounts, Proof of History, rent — and an honest ledger of what the speed costs
5. [[web3/05-beyond-ethereum/05-bitcoin-and-utxo|bitcoin-and-utxo]] — **[Intermediate]** — UTXO properly, why Script's limits are refusals rather than oversights, Taproot and Lightning, and the block-size war
6. [[web3/05-beyond-ethereum/06-bridges-and-interoperability|bridges-and-interoperability]] — **[Advanced]** — **the worst security record in the field, and why it's structural.** How to evaluate one
7. [[web3/05-beyond-ethereum/07-other-chains|other-chains]] — **[Intermediate]** — Cosmos/IBC, Polkadot, Move, Near, Cardano — and a six-question checklist for any chain you've never heard of

## Related
- [[web3/README|web3 curriculum map]]
- [[web3/06-building-dapps/README|06-building-dapps]] — building on top of all this
- [[web3/frameworks/rust/README|Rust for web3]] — Solana, CosmWasm, ink!
- [[architecture/04-distributed-systems/README|distributed systems]]
