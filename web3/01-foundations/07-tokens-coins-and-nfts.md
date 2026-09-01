# Tokens, Coins and NFTs

**[Beginner → Intermediate]** — what a token *is* at the data level, the difference between a coin and a token, and the sentence about NFTs that most explanations refuse to say.

## The kid version first

A **coin** is built into the chain itself. ETH isn't recorded anywhere except in the protocol's own account balances — it's the chain's native unit, like the chips being part of the casino.

A **token** is just **a spreadsheet inside one program.** Someone deployed a contract containing a table of "address → number", plus rules for moving numbers between rows. That's a token. There is no coin. **There is a row in someone's table with your name on it.**

An **NFT** is the same table where each row is one distinct numbered item instead of a quantity.

## Coins vs tokens — the distinction that matters

| | Native coin (ETH, BTC, SOL) | Token (USDC, UNI, any ERC-20) |
|---|---|---|
| Where the balance lives | In the protocol's own account state | In one contract's storage mapping |
| Who can change the rules | Nobody, without a hard fork | **Whoever controls that contract** |
| Used to pay gas | Yes — this is its structural role | No (barring [[web3/06-building-dapps/07-account-abstraction\|account abstraction]]) |
| If the code is broken | The chain is broken | That token is broken; the chain is fine |

**The second row is the one people miss.** A token's properties are whatever its contract says. It can be pausable, freezable, mintable without limit, or upgradeable to entirely different code tomorrow. **USDC can and does freeze addresses** — Circle has done it, on request from law enforcement. That's not a flaw in the token; it's what the contract was written to do. "Decentralised" is not a property tokens have by default. It's a property specific code either has or doesn't → [[web3/03-smart-contracts-with-solidity/08-upgradeability-and-proxies|upgradeability]].

## What an ERC-20 actually is

Nothing but an agreed function signature list — a Java interface, essentially, that wallets and exchanges know how to call:

```solidity
function totalSupply() external view returns (uint256);
function balanceOf(address account) external view returns (uint256);
function transfer(address to, uint256 amount) external returns (bool);
function approve(address spender, uint256 amount) external returns (bool);
function allowance(address owner, address spender) external view returns (uint256);
function transferFrom(address from, address to, uint256 amount) external returns (bool);

event Transfer(address indexed from, address indexed to, uint256 value);
event Approval(address indexed owner, address indexed spender, uint256 value);
```

The entire implementation is one mapping and some arithmetic:

```solidity
mapping(address => uint256) private _balances;
mapping(address => mapping(address => uint256)) private _allowances;
```

**There is no registry of tokens.** Deploying an ERC-20 requires nobody's permission and costs a few dollars of gas — which is why token scams are trivially cheap to manufacture, and why "it's listed on a DEX" means nothing at all → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]].

**The `approve` pattern is a design wart with real consequences.** Because a contract can't be notified of an incoming transfer, spending on your behalf requires a two-step approve-then-transferFrom dance. Interfaces routinely request *unlimited* approval to avoid a second transaction — so a later bug or malicious upgrade in that spender can drain the full balance, long after you last used it. **Unrevoked infinite approvals are one of the largest practical loss vectors in the ecosystem**, and checking them periodically is basic hygiene.

## Decimals are a lie you have to maintain

There are no fractions on-chain — all arithmetic is integer. A token declares `decimals` purely as **display metadata**, and every contract stores raw integers:

```
1.5 USDC   (6 decimals)  → stored as 1_500_000
1.5 ETH   (18 decimals)  → stored as 1_500_000_000_000_000_000
```

**Assuming 18 decimals is a real and recurring bug class.** USDC and USDT use 6, WBTC uses 8. Protocols that hardcoded 18 have mispriced assets by twelve orders of magnitude in production → [[web3/04-smart-contract-security/04-arithmetic-and-rounding|arithmetic]].

## The standards worth knowing

| Standard | What it is |
|---|---|
| **ERC-20** | Fungible tokens. The one above |
| **ERC-721** | NFTs — each `tokenId` is distinct, with one owner |
| **ERC-1155** | Multi-token: fungible and non-fungible in one contract, with batch transfers. Standard for game items |
| **ERC-4626** | Tokenised vaults — a standard interface for yield-bearing deposits. Prevented a lot of duplicated, subtly wrong accounting |
| **ERC-2612** | `permit` — approve by signature instead of a transaction, removing one step from the approve dance |
| **ERC-777** | Fungible tokens with transfer hooks. **Its hooks re-introduced reentrancy** and caused real exploits; largely abandoned. A good cautionary tale |

## NFTs, said plainly

An ERC-721 is a mapping from `tokenId` to owner address, plus a `tokenURI` function returning a string.

**That string is usually an HTTP or IPFS URL pointing somewhere else. The image is almost never on-chain.** So what you own is:

> a row in a contract's ownership mapping, associating your address with a number, which is associated with a URL, which points at a server that may or may not still be serving that file.

If the URL is plain HTTPS, the project's host going down or its domain lapsing means **your NFT points at nothing** — this has happened repeatedly. IPFS is better because the address is the content hash, so the content can't be silently swapped, **but IPFS only keeps data that someone is actively pinning.** Arweave pays upfront for long-term storage and is the strongest common option. **Fully on-chain NFTs** (SVG generated in the contract) exist and genuinely have no off-chain dependency, at much higher cost → [[web3/06-building-dapps/05-decentralised-storage|decentralised storage]].

**On the legal side:** owning the token conveys, by default, **no copyright, no licence, and no rights to the underlying artwork**. Some projects grant rights explicitly by separate terms; the token itself grants nothing. Treating an NFT as a deed is a category error that no amount of cryptography fixes.

**What the technology does honestly provide** is a public, permissionless, verifiable ownership registry with cheap transfer and provenance you can audit end to end. That's genuinely useful for tickets, credentials, in-game items and access rights. It was oversold as digital art ownership, which it is not → [[web3/07-the-application-layer/02-nfts-in-practice|NFTs in practice]].

## Key insight

**A token is a row in a contract's mapping, and its guarantees are exactly the guarantees that specific contract's code provides — nothing more.** "It's on the blockchain" tells you the *ledger* is tamper-resistant. It tells you nothing about whether the issuer can mint a billion more, freeze your address tomorrow, or upgrade the contract into something else entirely. Read the contract, or accept that you're trusting someone — which is fine, as long as you know you're doing it.

## Related
- [[web3/03-smart-contracts-with-solidity/07-token-standards|token standards]] — implementing these properly
- [[web3/07-the-application-layer/02-nfts-in-practice|NFTs in practice]]
- [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|scams and rugs]]
- [[build-your-own-shit/16-your-own-token-and-wallet|build your own token and wallet]]

*Source: [reference] — Aug 2026.*
