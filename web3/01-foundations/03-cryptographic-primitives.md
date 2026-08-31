# The Cryptographic Primitives

**[Intermediate]** — the four pieces every chain is assembled from, and specifically what blockchains do with them that [[cybersecurity/05-cryptography/README|the cryptography course]] doesn't cover.

**This note deliberately does not re-teach cryptography.** Hash functions, asymmetric keys and signatures are covered properly in [[cybersecurity/05-cryptography/README|cybersecurity/05]]. Read that first if any of it is unfamiliar. What's here is **the blockchain-specific usage** — which is narrower and stranger than general crypto use.

## 1. Hash functions — used as identity, not as integrity

General software uses SHA-256 to check a file wasn't corrupted. Blockchains use it for something more aggressive: **the hash of a thing is treated as the thing's name.**

This is **content addressing** — the same idea as [[git/01-how-git-works|Git's object store]] and [[web3/06-building-dapps/05-decentralised-storage|IPFS]]. Consequences:

- **A block's ID is the hash of its contents.** Change one byte of a block and it is a different block with a different name — there is no "editing" a block, only replacing it
- **Referencing by hash is a commitment.** Block *N+1* stores block *N*'s hash. It has thereby fixed the entire history behind it. That's what makes it a *chain*
- **The chain property is transitive and free.** Verifying the tip is correct verifies everything, because each link's name depends on all names before it

Which functions: **Bitcoin** uses SHA-256 (twice, "double-SHA"). **Ethereum** uses Keccak-256 — which is *not* the same as standardised SHA-3 despite the family name, a padding difference that has bitten many implementers. Contract addresses, event topics and storage slots are all Keccak outputs → [[web3/02-ethereum-and-the-evm/05-storage-layout-and-the-state-trie|storage layout]].

## 2. Merkle trees — proving membership without the data

A Merkle tree hashes data in pairs, then hashes the hashes, up to a single **root**.

```
                 root = H(H12 ‖ H34)
                /                    \
        H12 = H(H1‖H2)          H34 = H(H3‖H4)
        /        \               /        \
      H1=H(tx1) H2=H(tx2)    H3=H(tx3)  H4=H(tx4)
```

The point is the **proof**: to convince someone `tx3` is in a block whose root they know, you send `tx3`, `H4`, and `H12` — three values. They recompute the root. **You have proved membership in a million-item set with ~20 hashes instead of a million items.**

That is what makes light clients possible: a phone wallet can hold only block headers (80 bytes each in Bitcoin) and still verify its own transactions were included. Without Merkle proofs, every wallet would need the full chain.

Ethereum uses a variant, the **Merkle Patricia Trie**, which is also a *map* — it proves "account X has balance Y" and, crucially, proves **absence** ("this key is not in the state"), which a plain Merkle tree can't do → [[foundations/dsa/04-data-structures/05-trees/01-trees|trees]].

## 3. Digital signatures — authorisation with no accounts

**There is no signup.** A key pair *is* an account. You generate a private key from randomness; the public key is derived from it; the address is derived from that.

```
random 256 bits ──► private key
        │  (elliptic curve multiplication — one-way)
        ▼
    public key
        │  (Keccak-256, take last 20 bytes — Ethereum)
        ▼
  0x71C7656EC7ab88b098defB751B7401B5f6d8976F
```

Every chain in wide use signs with **elliptic curves**, not RSA — keys and signatures are far smaller, and every byte is stored forever by every node. Bitcoin and Ethereum use **secp256k1** with **ECDSA**; Solana and modern designs prefer **Ed25519**, which is faster and avoids ECDSA's nonce footgun.

**Blockchain-specific properties worth knowing:**

- **The signature covers the whole transaction** — recipient, amount, gas, nonce, and the chain ID. Change any field and the signature fails. This is why a signed transaction can be safely relayed by untrusted parties
- **Ethereum signatures are *recoverable*.** From the signature and the message you can derive the signer's public key (that's what the `v` byte is for, and what the `ecrecover` opcode does). So a transaction doesn't need to carry a "from" field — **the sender is computed, not stated**
- **ECDSA nonce reuse leaks the private key.** Sign two different messages with the same random `k` and anyone can algebraically recover your key. This has drained real wallets, most famously via a broken RNG in an Android wallet in 2013 → [[cybersecurity/05-cryptography/06-cryptographic-attacks-and-best-practices|weak randomness]]

## 4. The key-derivation stack (BIP-32/39/44)

Raw 256-bit keys are unusable by humans, and one key per account doesn't scale. Three standards, layered:

- **BIP-39** — turn entropy into a **12/24-word mnemonic** ("seed phrase"), with a checksum so a typo is detectable. The words map to a fixed 2048-word list
- **BIP-32** — **hierarchical deterministic (HD) derivation.** One seed deterministically generates an unlimited tree of child keys. Back up 12 words, recover every account forever
- **BIP-44** — the **path convention** giving the tree meaning: `m / 44' / 60' / 0' / 0 / 0` — purpose / coin type (60 = Ethereum) / account / change / index. This is why the same seed phrase restores the same addresses in a different wallet app

**The seed phrase is the private key**, in a form that fits on paper. Anyone who reads it owns everything derived from it — which is why every "support agent" who asks for it is stealing from you, without exception → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]].

## What blockchains notably *don't* use

Worth naming, because the absence is informative:

- **No encryption.** Public chain data is plaintext. Signatures authenticate; nothing conceals. "Encrypted on the blockchain" is a marketing phrase, not a description
- **No certificate authorities.** There is no PKI, no chain of trust, no revocation → the [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|PKI]] model is replaced by "the key is the identity, full stop"
- **No password reset.** There is no account recovery because there is no account. [[web3/06-building-dapps/07-account-abstraction|Account abstraction]] exists specifically to bolt recovery back on

## Key insight

**Blockchains use a deliberately tiny cryptographic vocabulary — one hash function, one signature scheme, one tree — because every node must reproduce every operation identically, forever.** Algorithm agility, the good practice everywhere else, is nearly impossible here: changing a primitive means a hard fork of the entire network.

## Related
- [[cybersecurity/05-cryptography/03-hashing-and-integrity|hashing and integrity]] · [[cybersecurity/05-cryptography/04-asymmetric-encryption|asymmetric encryption]] · [[cybersecurity/05-cryptography/05-digital-signatures-and-pki|signatures and PKI]]
- [[web3/01-foundations/04-blocks-chains-and-state|blocks, chains and state]] — these primitives assembled
- [[git/01-how-git-works|how Git works]] — the same content-addressed hash-chain idea, without consensus
- [[build-your-own-shit/14-your-own-blockchain|build your own blockchain]] — implement all four

*Source: [reference] — Aug 2026.*
