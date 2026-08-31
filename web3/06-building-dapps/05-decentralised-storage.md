# Decentralised Storage

**[Intermediate]** — where the files go, why "on IPFS" doesn't mean "stored forever", and what NFT metadata actually points at.

## The problem

On-chain storage costs ~20,000 gas per 32 bytes and burdens every node forever. **A single 1MB image would cost tens of thousands of dollars and is simply not an option.** So every file — images, metadata, documents, video — lives somewhere else, and the chain stores a pointer.

**The pointer is the whole design question:** what makes it trustworthy, and what keeps the thing it points at alive?

## HTTP — the default, and the wrong one

```json
{ "name": "Cool NFT #1", "image": "https://myproject.io/images/1.png" }
```

**This is a normal web dependency with none of the chain's guarantees:**

- The server can **swap the image** for anything, at any time, silently
- The domain lapses, the company folds, the S3 bucket is deleted — **your NFT points at nothing**

**This has happened repeatedly**, and it's why "the artwork disappeared" is a recurring NFT story. If a project's `tokenURI` returns an HTTPS URL on a domain they control, **you own a pointer to their server**, and nothing more → [[web3/01-foundations/07-tokens-coins-and-nfts|NFTs, said plainly]].

## IPFS — content addressing

IPFS addresses files **by the hash of their content**:

```
ipfs://QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco
       └─ the CID: a hash of the file itself
```

**This fixes the tampering problem completely.** Change one byte and the CID changes, so the content at a given CID is cryptographically pinned — the same idea as [[git/01-how-git-works|Git objects]] and block hashes.

**It does not fix availability.** IPFS is a distributed *lookup* system, not a storage guarantee:

> **IPFS stores nothing by itself. Files exist only while some node is actively "pinning" them.**

Stop paying your pinning service and the file becomes unretrievable. The CID remains valid forever and resolves to nothing. **"It's on IPFS" means "it's not tampered with", not "it's permanent"** — a distinction the ecosystem is consistently sloppy about.

**Pinning services** (Pinata, web3.storage, Filebase) are how this works in practice, and **they are a subscription** — which means a centralised, ongoing payment relationship underneath a "decentralised" asset.

**Gateways** (`ipfs.io/ipfs/<cid>`, or a dedicated one) let browsers fetch IPFS content over HTTP. **A gateway is a centralisation point and a bottleneck** — public ones are heavily rate-limited and slow. Production apps use a dedicated gateway, which is another vendor.

## Filecoin and Arweave — actual persistence

**Filecoin** adds an incentive layer over IPFS: storage providers post collateral and submit continuous cryptographic proofs that they still hold your data, or get slashed. **Storage becomes a paid contract with enforcement** rather than a favour.

**Arweave** takes a different approach: **pay once, stored forever.** A single upfront payment funds an endowment that pays miners in perpetuity, on the assumption that storage costs keep falling.

**Arweave is the strongest common answer for NFT metadata**, and the economic assumption is worth understanding rather than taking on faith — the model holds if storage costs continue to decline, and it's an assumption, not a proof.

## Fully on-chain

Generate the asset in the contract itself, usually as SVG returned as a data URI:

```solidity
function tokenURI(uint256 id) public view returns (string memory) {
    string memory svg = string.concat(
        '<svg xmlns="http://www.w3.org/2000/svg" ...>', generate(id), '</svg>');
    return string.concat('data:application/json;base64,', Base64.encode(bytes(
        string.concat('{"name":"#', id.toString(), '","image":"data:image/svg+xml;base64,',
                      Base64.encode(bytes(svg)), '"}'))));
}
```

**Genuinely permanent, with zero external dependency** — it lives exactly as long as Ethereum does. Expensive, limited to what you can generate in Solidity, and the honest answer for anyone who actually means "forever." Autoglyphs and Loot are the canonical examples, and their approach has aged far better than most.

## Comparison

| | Guarantee | Cost | Failure mode |
|---|---|---|---|
| **HTTP** | None | Cheap | Silent swap; total disappearance |
| **IPFS** | **Integrity** | Pinning subscription | Unpinned → gone |
| **Filecoin** | Integrity + enforced storage | Ongoing, cheap | Contract expiry |
| **Arweave** | Integrity + permanence | One-off, higher | Endowment model fails |
| **On-chain** | **Absolute** | **Very high** | The chain dies |

## Practical guidance

- **Never use a plain HTTPS URL for anything meant to be permanent.** This is the one hard rule
- **IPFS + a paid pinning service** is the reasonable default for most projects — **and be honest that it's a subscription**
- **Arweave when permanence is a real promise you're making**
- **Fully on-chain for small generative art**, where it's the whole point
- **Pin from multiple providers.** One pinning service is one point of failure
- **Use a dedicated gateway** in production; public ones will rate-limit you
- **Freeze the metadata.** If `tokenURI` is mutable by an owner, buyers are trusting that owner — say so, or make it immutable

## Other pieces

**ENS** maps human names to addresses and content hashes. `yourapp.eth` can resolve to an IPFS CID, so **your frontend can be decentralised too** — Uniswap does this, and it's a genuine censorship-resistance measure that costs little → [[web3/07-the-application-layer/04-identity-and-naming|identity and naming]].

**Ceramic** and similar handle mutable, user-owned documents — profiles and social data — where IPFS's immutability is the wrong shape.

## Key insight

**Content addressing and persistence are different problems, and IPFS solves only the first.** A CID guarantees that what you get is what was committed to; it guarantees nothing about whether anyone still has it. Every "decentralised storage" decision is really the question *who is paying to keep this alive, and what happens when they stop* — and for most NFT projects the honest answer is "a monthly pinning bill nobody has thought about."

## Related
- [[web3/01-foundations/07-tokens-coins-and-nfts|tokens, coins and NFTs]] — what a `tokenURI` is
- [[web3/07-the-application-layer/02-nfts-in-practice|NFTs in practice]]
- [[git/01-how-git-works|how Git works]] — the same content-addressing idea
- [[web3/06-building-dapps/01-the-dapp-architecture|the dapp architecture]]
