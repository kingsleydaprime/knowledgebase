# NFTs in Practice

**[Intermediate]** — what the 2021 boom got wrong, what the technology genuinely provides, and where it's actually being used.

## What happened

2021–22 saw tens of billions of dollars trade in profile-picture collections. By 2023 most of it was worth a small fraction of peak, and trading volume fell by well over 90%.

**Worth being precise about what failed.** The technology worked exactly as designed: ownership was tracked, transfers settled, provenance was verifiable. **What failed was the thesis** — that a public ownership record of a JPEG creates durable value in the JPEG.

**Three things the boom got wrong:**

1. **Conflating the token with the artwork.** The token is a row in a mapping pointing at a URL. **It is not the image, and it conveys no copyright** unless separately granted by licence → [[web3/01-foundations/07-tokens-coins-and-nfts|tokens said plainly]]
2. **Assuming scarcity creates value.** Anyone can mint 10,000 of anything for a few dollars. **Artificial scarcity of an infinitely reproducible thing is a coordination game**, and coordination games end when the coordination does
3. **Treating a thin, reflexive market as a price.** Floor prices were set by a handful of trades against near-zero liquidity, with substantial wash trading — much of it driven by marketplaces' token incentives

## What the technology actually provides

Strip out the speculation and the useful properties are real:

- **Verifiable, permissionless ownership** — anyone can check who owns what, without asking a company
- **Transferability without an intermediary** — no platform approval, no settlement window
- **Provenance** — the complete chain of custody, publicly auditable, forever
- **Composability** — other applications can read and build on your ownership record without permission
- **Persistence beyond the issuer** — the record survives the issuing company

**That's a genuinely useful primitive.** It's a *registry*, and it's most valuable where the underlying thing is a right, a credential or an access grant — not where it's an image.

## Where it's actually working

**Ticketing.** The strongest fit. Transferable, verifiable, with resale rules enforceable in the contract and a permanent record against counterfeiting. Adopted in production, quietly.

**Domain names.** ENS is an NFT, and it's arguably the field's most successful — because **the token *is* the asset**, not a pointer to one. `vitalik.eth` doesn't reference a name elsewhere; the on-chain record is the whole thing → [[web3/07-the-application-layer/04-identity-and-naming|identity and naming]].

**In-game items.** Genuine when the game is genuine. Items that outlive the game, are tradeable without the publisher's marketplace, and are usable across games. **The last one is mostly still aspiration** — cross-game interoperability requires games to agree on meaning, which is a design problem, not a blockchain problem.

**Credentials and memberships.** Certifications, event attendance, DAO membership, club access. Often better as **soulbound** (non-transferable) tokens, where transferability would defeat the purpose.

**Real-world asset tokenisation.** Deeds, invoices, carbon credits. **Legally uncertain and heavily dependent on off-chain enforcement** — the token means what a legal system says it means, and no chain can make a court recognise it. Real work is happening here; treat claims carefully.

**Art, honestly.** A smaller, calmer market persists. Fully on-chain generative art (Art Blocks, Autoglyphs) has held up best, which is unsurprising: those pieces have no external dependency and the artwork genuinely is the token.

## The design decisions that matter

If you're building with NFTs, these are the ones that determine whether it ages well:

**1. Where is the metadata?** A plain HTTPS URL means the project's server is a permanent dependency. **Use IPFS with real pinning, Arweave, or fully on-chain** → [[web3/06-building-dapps/05-decentralised-storage|storage]].

**2. Is the metadata frozen?** If the owner can change `tokenURI`, holders are trusting them. Freeze it, or say clearly that you haven't.

**3. What rights come with it?** Nothing, by default. **If you intend to grant licence rights, do it explicitly in terms you publish.** CC0 and the Nouns/Loot approach — abandoning rights entirely — has produced more durable ecosystems than restrictive licensing.

**4. Royalties are not enforceable on-chain.** ERC-2981 is *advisory*; marketplaces choose whether to honour it, and most stopped when competition on fees intensified. **Attempts to enforce via transfer blocklists fragment liquidity and mostly failed.** Build a business model that doesn't assume perpetual royalties.

**5. Reentrancy in mints.** `safeMint` calls `onERC721Received`, handing control to the minter mid-transaction — **used repeatedly to bypass per-wallet limits.** Apply Checks-Effects-Interactions and a guard → [[web3/04-smart-contract-security/02-reentrancy|reentrancy]].

**6. Fair distribution.** On-chain randomness is manipulable, so naive reveals get sniped for rares. **Use Chainlink VRF, or reveal after minting closes** → [[web3/06-building-dapps/06-oracles|randomness]].

## Key insight

**NFTs are a good ownership registry attached to a bad story about digital art.** The registry — permissionless, verifiable, transferable, outliving the issuer — is genuinely useful for tickets, names, credentials and game items, where the token *is* the right rather than a pointer to a file on someone's server. The 2021 boom tested the story, not the technology, and it's the story that failed.

## Related
- [[web3/01-foundations/07-tokens-coins-and-nfts|tokens, coins and NFTs]] — the data model
- [[web3/06-building-dapps/05-decentralised-storage|decentralised storage]] — where the image lives
- [[web3/07-the-application-layer/04-identity-and-naming|identity and naming]] — ENS, the success case
- [[web3/08-the-honest-assessment/README|the honest assessment]]
