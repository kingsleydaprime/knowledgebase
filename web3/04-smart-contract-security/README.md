# Smart Contract Security

**Read this alongside [[web3/03-smart-contracts-with-solidity/README|section 03]], not after it.** In this domain security isn't an advanced topic bolted onto the language — it's the reason the language is used the way it is.

**If you read one note here, read [[web3/04-smart-contract-security/08-case-studies|08-case-studies]].** It's the fastest way to understand why everything else in this folder is written the way it is — and its table shows that the money went somewhere different from where the field's attention goes.

## Reading order
1. [[web3/04-smart-contract-security/01-why-this-is-different|why-this-is-different]] — **[Intermediate]** — no patching, no perimeter, funded adversaries, composability as attack surface, and what actually reduces risk (ranked)
2. [[web3/04-smart-contract-security/02-reentrancy|reentrancy]] — **[Intermediate]** — the canonical bug, the **three variants people miss** (cross-function, cross-contract, read-only), and why `.transfer()` is not the fix
3. [[web3/04-smart-contract-security/03-access-control-and-key-management|access-control-and-key-management]] — **[Intermediate]** — **the largest category of losses**: `tx.origin`, the initialiser trap, multisig signer independence, and the four signature checks
4. [[web3/04-smart-contract-security/04-arithmetic-and-rounding|arithmetic-and-rounding]] — **[Intermediate]** — 0.8 fixed overflow and not precision; multiply before dividing; **round in the protocol's favour**; the vault inflation attack
5. [[web3/04-smart-contract-security/05-oracle-and-price-manipulation|oracle-and-price-manipulation]] — **[Advanced]** — flash loans make capital rentable, so **spot price as truth is the field's most reliable exploit**. TWAPs, staleness checks, and not needing a price at all
6. [[web3/04-smart-contract-security/06-mev-front-running-and-ordering|mev-front-running-and-ordering]] — **[Advanced]** — sandwiching, PBS, why MEV can't be eliminated, and what actually protects users
7. [[web3/04-smart-contract-security/07-the-audit-process|the-audit-process]] — **[Intermediate]** — what an audit is and isn't, how to prepare, **and how to read someone else's report**
8. [[web3/04-smart-contract-security/08-case-studies|case-studies]] — **[Intermediate]** — The DAO, Parity, Ronin, Wormhole, Nomad, Euler, Curve, Mango — and the pattern across all of them

## Related
- [[web3/README|web3 curriculum map]]
- [[cybersecurity/README|cybersecurity]] — the parent discipline, and what doesn't transfer
- [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|testing and tooling]] — fuzzing and invariants
- [[cybersecurity/06-attacks-and-threats/README|attacks and threats]] — the web equivalents
