# Gaming, Social and the Rest

**[Intermediate]** — the non-financial applications, what's genuinely working, and a method for judging the next proposal.

## Gaming

**The theory:** players own their items, trade them without the publisher's permission, and carry them between games. Items outlive the game.

**What happened:** the 2021 "play-to-earn" wave, led by **Axie Infinity**, produced games where the earning *was* the gameplay. Player growth was needed to pay existing players — **the reward economy depended on new entrants, which is a structure with a known ending.** When growth stopped, earnings collapsed, and with them the player base. Axie's daily active users fell by well over 90% from peak.

**The lesson is specific and useful:** *if the economy is the game, the game ends when the economy does.* Players arrived to earn, not to play, and left when earning stopped.

**What's genuinely promising:**

- **Ownership in games people would play anyway.** The blockchain is a settlement layer for a trading economy, not the point of the game. The games taking this approach are slower and better
- **True item scarcity and open markets** — trade without a publisher taking a cut or banning your account
- **On-chain worlds** (Dark Forest, autonomous worlds) — the entire game state on-chain, so it's modifiable, extensible, and outlives its creators. **Genuinely novel**, and Dark Forest's use of zk proofs for fog-of-war — proving you moved legally without revealing where — is a legitimately elegant piece of design
- **Session keys and sponsored gas** finally make on-chain interaction playable → [[web3/06-building-dapps/07-account-abstraction|account abstraction]]

**The honest constraints:** blockchains are far too slow and expensive for real-time gameplay, so only ownership and settlement go on-chain; **cross-game interoperability is mostly aspiration**, because it requires games to agree what an item *means*, which is a game-design problem no chain solves; and players have been consistently hostile to NFTs in mainstream games, with several major publishers reversing announcements after backlash.

## Social

**The pitch:** own your social graph, so you can leave a platform without losing your followers.

**Farcaster** is the most credible attempt — a sufficiently-decentralised protocol with on-chain identity and off-chain message storage. **It has a real, active community**, which puts it ahead of everything else here. **Lens Protocol** puts the graph on-chain more fully, with profiles and follows as NFTs.

**The genuine insight:** platform lock-in comes from the social graph. Make it portable and the platform must compete on quality. **That's a real diagnosis of a real problem.**

**The genuine difficulty:** network effects are the product. A protocol with 50,000 users doesn't compete with one that has hundreds of millions, and "you own your data" has repeatedly failed to move ordinary users. **Moderation is also unsolved** — a censorship-resistant network is also a network that can't remove abuse, and every deployment discovers this.

## Real-world assets

Tokenising treasuries, real estate, invoices and commodities. **This is where serious institutional money has actually gone** — tokenised money-market funds run into the billions, and BlackRock's BUIDL is the flagship.

**Why it works when other things haven't:** it's a genuine efficiency gain — 24/7 settlement, programmable compliance, fractional ownership, instant transfer — applied to assets whose value comes from *outside* the chain rather than from the chain's own speculation.

**The unavoidable caveat:** a token representing a house is only worth something if a legal system agrees. **The chain settles the token; the courts settle the asset.** These systems are therefore permissioned, KYC'd and centralised by necessity — which is fine, and is not what the field originally promised.

## Supply chain, credentials, provenance

The perennial enterprise pitch: track goods on a blockchain for tamper-proof provenance.

**The unavoidable problem is the oracle problem in physical form.** A blockchain guarantees that a *record* wasn't altered. It cannot guarantee the record was true when written. **Someone scanning a QR code onto a pallet can lie, and the blockchain faithfully preserves the lie forever** → [[web3/06-building-dapps/06-oracles|oracles]].

**This is why the 2016–2020 enterprise blockchain wave largely ended in signed database projects.** Where the participants are known and a consortium runs the nodes, a replicated database with signed writes gives the same guarantees at a fraction of the cost. **Most of those pilots quietly concluded exactly that.**

Where it does work: **credentials whose issuer is the authority** — a university issuing a degree, where the issuer's signature is the truth and the chain provides permanent, verifiable, revocable publication. That's a genuine fit.

## The test to apply to anything new

When someone proposes a blockchain application, four questions resolve it:

1. **Who are the participants, and do they distrust each other?** If they trust each other, use a database
2. **Is there an administrator who could be trusted to run it?** If yes, use a database
3. **Does the data originate on-chain, or does someone type it in?** If someone types it in, **the chain guarantees nothing about its truth**
4. **What breaks if a company shuts down?** If nothing, you didn't need it

**Applications that pass all four are rarer than the field pretends, and genuinely valuable when they exist** → [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|what blockchains are actually good for]].

## Key insight

**The non-financial applications that work share one property: the thing being tracked is *born* on-chain.** ENS names, on-chain game state, DAO membership and tokens are created and live entirely within the system, so the chain's guarantees fully apply. Everything that tracks a physical or legal object depends on someone honestly typing it in — and at that point the chain is an expensive, permanent record of whatever they typed.

## Related
- [[web3/08-the-honest-assessment/01-what-blockchains-are-actually-good-for|what blockchains are actually good for]] — the full argument
- [[web3/06-building-dapps/06-oracles|oracles]] — why supply chain doesn't work
- [[game-development/README|game development]] — how games are actually built
- [[web3/07-the-application-layer/04-identity-and-naming|identity and naming]]
