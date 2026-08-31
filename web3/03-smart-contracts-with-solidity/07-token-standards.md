# Token Standards

**[Intermediate]** — ERC-20, 721, 1155 and 4626, the non-compliant tokens that break integrations, and why `SafeERC20` exists.

## What a "standard" is here

An ERC is **a function signature list plus expected events**. There is no registry, no certification, no enforcement — a contract "is" an ERC-20 because it exposes those functions and emits those events, and wallets and exchanges recognise it on that basis.

**Which means a token can be almost-compliant, and almost is where the bugs live.**

## ERC-20 — and the four ways real tokens break it

The interface is in [[web3/01-foundations/07-tokens-coins-and-nfts|foundations/07]]. What matters here is that widely-used tokens violate it, and integrations that assume compliance lose money:

**1. No return value.** The spec says `transfer` returns `bool`. **USDT and BNB return nothing.** A Solidity call expecting a `bool` from a function returning nothing reverts on decode — so naive integrations simply cannot transfer USDT. This is the single most common integration bug in DeFi.

**2. Fee-on-transfer.** Some tokens take a cut in `transfer`, so the recipient receives less than was sent. Any contract that assumes `balanceAfter == balanceBefore + amount` is wrong. **Measure the actual delta:**

```solidity
uint256 before = token.balanceOf(address(this));
token.safeTransferFrom(msg.sender, address(this), amount);
uint256 received = token.balanceOf(address(this)) - before;   // use THIS, not `amount`
```

**3. Rebasing.** Balances change without a `Transfer` event (stETH, AMPL). Any contract caching a balance, or accounting in absolute rather than proportional terms, silently desynchronises.

**4. The approve race (and USDT's response).** Changing a non-zero allowance to another non-zero value lets the spender front-run and spend both. **USDT reverts** if you set a non-zero allowance while one is outstanding — so integrations must approve to zero first. `SafeERC20.forceApprove` handles this.

Others worth knowing: tokens with blocklists (USDC, USDT can freeze addresses), tokens with more than 18 or fewer than 6 decimals, and **ERC-777's transfer hooks, which re-introduce reentrancy into what everyone assumes is a safe operation** — the imBTC/Uniswap V1 exploit of April 2020 was exactly this.

**The answer to all of it:**

```solidity
using SafeERC20 for IERC20;
token.safeTransfer(to, amount);          // handles missing return values, reverts on failure
token.safeTransferFrom(from, to, amount);
token.forceApprove(spender, amount);     // handles the USDT approve quirk
```

**Use `SafeERC20` for every external token interaction, without exception.** It exists because of exactly the list above.

## ERC-721 — NFTs

```solidity
function ownerOf(uint256 tokenId) external view returns (address);
function safeTransferFrom(address from, address to, uint256 tokenId) external;
function approve(address to, uint256 tokenId) external;
function setApprovalForAll(address operator, bool approved) external;
function tokenURI(uint256 tokenId) external view returns (string memory);
```

**`safeTransferFrom` calls `onERC721Received` on the recipient if it's a contract** — a callback intended to prevent tokens being sent to contracts that can't handle them. It is also **a reentrancy vector**: the recipient gets control mid-transfer, before your function has finished. Multiple NFT mints have been exploited by re-entering through this callback to bypass a per-wallet limit. **Guard it, and apply Checks-Effects-Interactions** → [[web3/04-smart-contract-security/02-reentrancy|reentrancy]].

**`setApprovalForAll` grants control over your entire collection**, to one operator, indefinitely. Marketplace phishing overwhelmingly targets this signature rather than individual approvals, because one signature takes everything.

## ERC-1155 — multi-token

One contract, many token IDs, each fungible or not. `balanceOf(account, id)`, plus batch operations:

```solidity
function safeBatchTransferFrom(address from, address to,
                               uint256[] calldata ids,
                               uint256[] calldata amounts,
                               bytes calldata data) external;
```

**Batching is the point** — transferring 50 game items costs far less than 50 ERC-721 transfers. Standard for games and editioned collectibles. Same `onERC1155Received` callback, same reentrancy consideration.

## ERC-4626 — tokenised vaults

A standard interface for "deposit an asset, receive shares that accrue yield":

```solidity
function deposit(uint256 assets, address receiver) external returns (uint256 shares);
function redeem(uint256 shares, address owner, address receiver) external returns (uint256 assets);
function convertToShares(uint256 assets) external view returns (uint256);
function totalAssets() external view returns (uint256);
```

It exists because every yield protocol had reimplemented share accounting, and **many had done it wrong in the same way** — the **inflation / donation attack**, where the first depositor donates assets directly to an empty vault to skew the share price and steal subsequent depositors' funds through rounding.

**The standard doesn't fix that by itself.** The mitigations are seeding the vault with a small initial deposit at deployment, or OpenZeppelin's **virtual shares and assets** offset. A 4626 vault that does neither is exploitable, and this has happened repeatedly in production → [[web3/04-smart-contract-security/04-arithmetic-and-rounding|rounding]].

**Rounding direction is normatively specified**: deposits round shares *down*, withdrawals round assets *down*. **Always round in the protocol's favour** — every "off by one wei" exploit is a rounding direction chosen in the user's favour, compounded a million times.

## Others worth knowing

- **ERC-2612 `permit`** — approve by signature. Removes the separate approval transaction, and is why "one-click" swaps are possible. Note it uses [[web3/06-building-dapps/02-wallets-and-connection|EIP-712 typed signatures]]
- **ERC-2981** — a royalty *info* interface. Advisory only; marketplaces choose whether to honour it, and most stopped
- **ERC-165** — interface detection: `supportsInterface(bytes4)`. How a contract asks another what it implements

## Key insight

**"It implements ERC-20" is a claim about function signatures, not about behaviour.** Real tokens return nothing, take fees, rebase, freeze accounts and call you back mid-transfer. Every safe integration measures actual balance deltas, uses `SafeERC20`, and treats an incoming token contract as adversarial code — because roughly half the DeFi exploit surface is integrations that assumed otherwise.

## Related
- [[web3/01-foundations/07-tokens-coins-and-nfts|tokens, coins and NFTs]] — what a token is
- [[web3/04-smart-contract-security/02-reentrancy|reentrancy]] — the callbacks above
- [[web3/07-the-application-layer/01-defi-primitives|DeFi primitives]] — what gets built on these
- [[build-your-own-shit/16-your-own-token-and-wallet|build your own token and wallet]]

*Source: [reference] — Aug 2026.*
