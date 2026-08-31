# Build Your Own Blockchain

> **[Intermediate]** · A proof-of-work chain with transactions, wallets and P2P gossip. **A long weekend, ~800 lines, and the moment two of your nodes disagree and then converge is the whole lesson.**

## What you're building

**A working cryptocurrency**: blocks chained by hash, proof-of-work mining, a UTXO transaction model, ECDSA-signed transfers, peer-to-peer gossip between multiple nodes, and longest-chain fork resolution.

**Two of your nodes will mine competing blocks, disagree, and then agree again without talking about it.** That's the moment worth building this for.

**And what you're deliberately not:** competing with Bitcoin, being efficient, handling adversarial peers, or implementing a script language. **The goal is that "consensus" stops being a word and becomes a rule you watched execute.**

## What you need first

- **Hashing and digital signatures** → [[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing]] · [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures]]
- **The concepts** → [[web3/01-foundations/README|web3/01-foundations]] — notes 02, 04 and 05 in particular
- **Sockets and a request/response loop** → [[foundations/networking/README|networking]]
- Helpful: [[build-your-own-shit/01-http-server|the HTTP server guide]] — you'll want a small HTTP API, and this is the same accept loop

**Python or Go are the natural choices.** Python for speed of writing (`hashlib` and `ecdsa` do the crypto); Go if you want the concurrency to be pleasant, since mining and networking must run simultaneously. **Avoid Rust for this one unless you already know it** — you'll fight the borrow checker over shared mutable chain state and learn less about blockchains.

## The build order

**1. A block, and a chain of them.**
A block is `{index, timestamp, prev_hash, data, nonce}` and its hash is `sha256` of those fields serialised deterministically.

```python
def hash_block(b):
    return hashlib.sha256(json.dumps(b, sort_keys=True).encode()).hexdigest()
```

**`sort_keys=True` is load-bearing** — two nodes must hash the same block identically, and dict ordering will betray you otherwise. Determinism bugs here are maddening later, so fix it now.

*Works when:* you can build a list of 5 blocks and a `validate_chain()` that walks it checking `prev_hash` matches.
*Then:* mutate block 2's data and watch validation fail at block 3. **That's tamper-evidence, and it's the first thing that feels real.**

**2. Proof of work.**
Loop a nonce until the hash has *N* leading zeros.

```python
while not hash_block(b).startswith('0' * difficulty):
    b['nonce'] += 1
```
*Works when:* difficulty 4 takes a noticeable pause, and 5 takes ~16× longer. **Print the hash rate.** Feeling the exponential is the point — this is the cost that secures the chain → [[web3/01-foundations/05-consensus|consensus]].

**3. A JSON-RPC-ish HTTP API.**
`GET /chain`, `POST /mine`, `GET /peers`. Now you can drive it with `curl` and inspect what's happening. **Do this before networking** — debugging a distributed system you can't query is miserable.

*Works when:* `curl localhost:5000/mine` produces a new block and `/chain` shows it.

**4. Wallets and signed transactions.**
Generate an ECDSA keypair (secp256k1). The address is the hash of the public key. A transaction is `{inputs, outputs}` signed with the sender's private key.

*Works when:* you can sign a transaction, verify it with only the public key, **and verify fails after flipping one byte of the amount.**

**This is where "no accounts, just keys" lands.** There is no registration step anywhere → [[web3/01-foundations/03-cryptographic-primitives|primitives]].

**5. The UTXO set, and real balance checking.**
Track unspent outputs. A transaction must consume whole UTXOs and produce new ones; **the sum of inputs must be ≥ the sum of outputs**, with the difference being the fee.

```
inputs:  UTXO_a (3), UTXO_b (2)      = 5
outputs: 4 → Bob, 0.9 → Alice (change)
fee:     0.1
```

*Works when:* you can't spend a UTXO twice, can't spend someone else's, and **change comes back correctly.** Print a wallet's balance by summing spendable outputs — the chain never stores it → [[web3/01-foundations/04-blocks-chains-and-state|UTXO]].

**The change bug will get you.** Forget the change output and you silently pay the whole input as a fee. Everyone does this once.

**6. A mempool, and mining real transactions.**
Pending transactions queue; the miner selects them (fee-ordered is realistic), adds a **coinbase transaction** paying itself the block reward, and mines.

*Works when:* you submit a transaction, mine, and see balances change. **You now have money.**

**7. P2P gossip.**
Nodes register peers and broadcast new blocks and transactions. Start simple: on receiving a block, validate it and forward to peers you haven't heard it from.

*Works when:* two nodes on different ports, one mines, and the other has the block within a second **without being asked.**

**8. Fork choice — the payoff.**
Nodes will inevitably mine competing blocks at the same height. The rule: **on hearing of a longer valid chain, replace yours with it.**

```python
def resolve(self):
    best = self.chain
    for peer in self.peers:
        their = fetch_chain(peer)
        if len(their) > len(best) and valid_chain(their):
            best = their
    self.chain = best
```

*Works when:* **disconnect two nodes, mine 3 blocks on each, reconnect — and one node discards its blocks and adopts the other's.** Watch the orphaned transactions return to the mempool.

**This is the milestone.** Nobody voted, nobody coordinated, and both nodes independently applied a local rule and converged. **That's Nakamoto consensus, and you just watched it happen.**

**9. Difficulty adjustment.**
Every N blocks, compare actual elapsed time to target and adjust difficulty.

*Works when:* start 3 miners and watch difficulty rise; kill 2 and watch it fall back.

**10. Optional: Merkle trees.**
Replace the block's flat transaction list with a Merkle root, then implement a proof that a transaction is in a block **without sending the block**.

*Works when:* you can verify membership in a 1000-transaction block with ~10 hashes. **This is what makes light clients possible** → [[web3/01-foundations/03-cryptographic-primitives|Merkle trees]].

## The parts that will bite you

**Non-deterministic serialisation.** The single biggest time sink. If two nodes serialise a block differently — dict ordering, float formatting, whitespace — they compute different hashes for identical data and reject each other's blocks for no visible reason. **Serialise canonically from the start.**

**Mining blocks your event loop.** Proof-of-work is a tight CPU loop; while it runs, your node stops answering peers. Use a thread or a separate process, and **check for a newly received block periodically so you abandon work on a block someone already found** — real miners do exactly this.

**Signing the wrong bytes.** The signature must cover the whole transaction. Sign a subset and someone can alter the rest. **Sign the canonical serialisation, and verify against the same function** — not a re-implementation.

**Validating the chain you're replacing.** In step 8 it's tempting to trust a longer chain. **Validate every block and every transaction in it**, or a peer feeds you a longer chain of nonsense and you accept it. This is the whole security model.

**Coinbase rules.** Exactly one per block, at a fixed position, with the correct reward, and no inputs. Forget to special-case it and your validator rejects every block you mine.

**Timestamps.** Nodes disagree about time. Bound acceptable drift or a peer can manipulate difficulty.

## How to know it works

1. **Tamper detection** — modify an old block, validation fails at the next one
2. **A double-spend is rejected** — the same UTXO in two transactions
3. **A forged signature is rejected**
4. **Balances are conserved** — total supply equals block rewards issued, always. **Assert this after every block; it's the invariant that catches accounting bugs** → [[web3/03-smart-contracts-with-solidity/10-testing-and-tooling|invariant testing]]
5. **Partition and heal** — the step-8 test, and the one that matters
6. **Three nodes, sustained** — run 3 miners for 10 minutes and confirm all three chains are identical at the end

## Where to stop

**Stop after fork resolution and difficulty adjustment work.** Merkle trees if you want the light-client insight.

**Don't** add a scripting language (that's [[build-your-own-shit/15-your-own-smart-contract-vm|guide 15]]), don't harden against adversarial peers, and don't optimise. Those are large projects that teach much less per hour.

**You will have learned:** why ordering rather than detection is the hard problem, why proof-of-work is expensive *by design*, what "the longest chain wins" actually means as executable code, why immutability is economic rather than physical, and why a UTXO set is a genuinely different data model from an account balance.

**And it recontextualises [[git/01-how-git-works|Git]]** — you'll have built the same content-addressed hash chain, and the only thing Git is missing is the consensus rule.

## Related
- [[web3/01-foundations/README|web3/01-foundations]] — the theory, in full
- [[web3/05-beyond-ethereum/05-bitcoin-and-utxo|Bitcoin and UTXO]] — what you're building a toy of
- [[git/01-how-git-works|how Git works]] — the same hash chain, without consensus
- [[build-your-own-shit/15-your-own-smart-contract-vm|your own smart contract VM]] — the natural next one

*Source: [reference] — build guide, Aug 2026.*
