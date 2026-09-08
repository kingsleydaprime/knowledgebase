# Web3 Frameworks

**"How this stack does it."** Sections [[web3/01-foundations/index|01]]–[[web3/08-the-honest-assessment/index|08]] hold true regardless of language; this folder is the per-language implementation layer, copying the [[backend/frameworks/index|backend/frameworks]] convention.

## The languages, and what each is actually for

| Language | Role | Folder |
|---|---|---|
| **Solidity** | **The contract language.** EVM chains — Ethereum and every L2. The default | [[web3/frameworks/solidity/index\|solidity/]] |
| **Rust** | **The other contract language.** Solana, CosmWasm, ink!, NEAR — plus most chain clients | [[web3/frameworks/rust/index\|rust/]] |
| **JS / TS** | **The client layer.** Frontends, indexers, bots, scripts. viem, wagmi, ethers | [[web3/frameworks/javascript/index\|javascript/]] |
| **Python** | **Scripting, analysis, security tooling.** web3.py, Slither, Vyper | [[web3/frameworks/python/index\|python/]] |
| **Go** | **Infrastructure.** Geth, Cosmos SDK, indexers, backend services | [[web3/frameworks/go/index\|go/]] |

## Which to learn, in what order

**If you want to write contracts on EVM chains** — the largest job market by a wide margin:
**Solidity + Foundry**, then TypeScript for the client side. That combination covers most of the field.

**If you want to write contracts on Solana:**
**Rust + Anchor.** Genuinely different mental model, not just a different syntax → [[web3/05-beyond-ethereum/04-solana-and-the-alternative-model|Solana]].

**If you're a frontend developer entering the field:**
**TypeScript + viem + wagmi.** You already have 90% of the skills; the chain is one unusual data source → [[web3/06-building-dapps/index|building dapps]].

**If you want to do security work:**
Solidity deeply, plus Python for tooling, plus enough Rust to read Solana programs.

## The uncomfortable truth about language choice

**Solidity is not a good language.** It has awkward semantics, sharp edges, and a design that leaks its VM everywhere. **It is also where the overwhelming majority of value, tooling, jobs and audited libraries are**, because the EVM became the field's standard target.

Learn the one your target chain uses. **The transferable knowledge is in sections 01–08, not in the syntax** — someone who understands reentrancy, storage layout and oracle manipulation picks up a new contract language in a week.

## Related
- [[web3/index|web3 curriculum map]]
- [[backend/frameworks/index|backend/frameworks]] — the convention this copies
- [[languages/index|languages]] — the languages themselves, properly
