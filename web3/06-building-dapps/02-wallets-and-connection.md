# Wallets and Connection

**[Intermediate]** — what a wallet actually is, the connection flow, EIP-712 signatures, and the UX problems that have no good answer yet.

## What a wallet is

**A key manager and a signer.** It holds private keys, derives addresses, and signs messages and transactions. **It does not hold your coins** — those are entries in chain state that reference your address.

```
seed phrase (BIP-39)
    └─ HD derivation (BIP-32/44)
         └─ private keys
              └─ public keys ──► addresses
```

Lose the seed phrase, lose everything, forever. **There is no recovery** because there is no account and no provider → [[web3/01-foundations/03-cryptographic-primitives|key derivation]].

The categories: **browser extension** (MetaMask, Rabby), **mobile** (usually via WalletConnect), **hardware** (Ledger, Trezor — the key never leaves the device), **smart contract wallets** (Safe, and [[web3/06-building-dapps/07-account-abstraction|account abstraction]] wallets), and **embedded/social** (Privy, Dynamic — key shares split between provider and user, trading self-custody for onboarding).

## Connection, and what it actually grants

```
1. User clicks "Connect"
2. Wallet prompts; user picks accounts to expose
3. Your app receives the address and chain ID
4. That's it
```

**Connecting grants read access to an address and the ability to *request* signatures. Nothing more.** It does not authorise transactions, move funds, or persist server-side. Every write still requires an explicit, separate approval.

**Connection is not authentication.** Knowing an address doesn't prove someone controls it — addresses are public. To authenticate, ask for a signature over a nonce you generated: **Sign-In With Ethereum (EIP-4361)** standardises this, and the nonce is what prevents replay → [[cybersecurity/04-web-security/02-secure-authentication|authentication]].

In practice you use a library:

```tsx
import { useAccount, useConnect } from 'wagmi'
const { address, isConnected } = useAccount()
const { connect, connectors } = useConnect()
```

**EIP-6963** fixed a long-standing mess: multiple extensions used to fight over `window.ethereum`, so having two wallets installed broke connection. It's a discovery protocol, wagmi implements it, and you get correct multi-wallet behaviour for free.

## The three signature types

**1. `personal_sign`** — sign arbitrary text. The user sees the message.
```ts
await signMessage({ message: 'Sign in to MyApp. Nonce: abc123' })
```
Free, no gas. **Use for authentication.** Always include a nonce, a domain, and an expiry.

**2. `eth_signTypedData_v4` (EIP-712)** — sign *structured* data with a domain separator:
```ts
await signTypedData({
  domain: { name: 'MyApp', version: '1', chainId: 1, verifyingContract: '0x...' },
  types: { Order: [{ name: 'maker', type: 'address' }, { name: 'amount', type: 'uint256' }] },
  primaryType: 'Order',
  message: { maker: address, amount: 1000n },
})
```

**This is the one to use for anything a contract will verify.** The wallet displays readable fields instead of a hex blob, and the domain — including `chainId` and `verifyingContract` — makes the signature valid **only** for your contract on your chain. Omit that and the signature is replayable everywhere → [[web3/04-smart-contract-security/03-access-control-and-key-management|signature verification]].

**3. A transaction** — costs gas, changes state, needs a receipt.

**The dangerous middle ground:** `personal_sign` over an opaque hash shows the user a meaningless hex string. **That's how signature phishing works** — the victim signs something they cannot read, which turns out to be an order transferring their NFTs. **Never ask users to sign opaque data**, and be suspicious of any site that does.

## Chains, and switching

```ts
const { switchChain } = useSwitchChain()
await switchChain({ chainId: 8453 })     // prompts the user
```

**Always check the connected chain before every write.** A user on Polygon calling your Ethereum contract gets a confusing failure or, worse, sends a transaction to an address that holds a *different* contract on that chain. Contracts deployed at the same address on different chains is common (CREATE2), and it makes this failure mode genuinely dangerous.

## The UX problems with no good answer

Worth stating plainly, because the field routinely pretends these are solved:

**1. Seed phrases.** Twelve words that grant irreversible total control, that must never be typed anywhere, and that no one can help you recover. **This is the single largest barrier to adoption**, and it is inherent to self-custody. Social recovery and account abstraction help; they don't dissolve it.

**2. Gas.** New users must acquire the native token before doing anything — including receiving their first asset. Sponsored transactions (ERC-4337 paymasters, EIP-7702) genuinely fix this, and adoption is still partial.

**3. Approvals.** Two transactions to swap; infinite approvals that persist forever; and no visibility into what you've approved. `permit` (ERC-2612) helps where supported → [[web3/01-foundations/07-tokens-coins-and-nfts|the approve pattern]].

**4. Irreversibility.** Wrong address, wrong chain, wrong amount — gone. **ENS names help; nothing else does.**

**5. Phishing.** A malicious signature request can drain a wallet in one click, and the request looks like every legitimate one. **This is the main way ordinary users actually lose money** — far more than smart contract exploits → [[web3/08-the-honest-assessment/02-scams-rugs-and-the-fraud-surface|the fraud surface]].

## What good practice looks like

- **Show the chain, and switch before writing** rather than failing after
- **Use EIP-712 for anything structured.** Readable signature prompts are a security feature
- **Show the human-readable consequence** of every signature request, in your own UI, before the wallet prompt
- **Request finite approvals**, or exact amounts, and offer a revoke path
- **Handle rejection gracefully** — users cancelling is normal, not an error state
- **Never store a private key or seed phrase.** Not in state, not in `localStorage`, not ever
- **Support ENS** for display and input
- **Don't gate the whole app behind connection.** Let people browse first

## Key insight

**A wallet connection grants read access and the right to ask for signatures — the user approves every single action, individually, forever.** That's the security model, and it's genuinely good. It's also the UX model, and it's genuinely painful, because it pushes every consequence onto a user who often can't read what they're approving. Most dapp UX work is closing that gap.

## Related
- [[web3/06-building-dapps/07-account-abstraction|account abstraction]] — the attempt to fix most of this
- [[web3/06-building-dapps/03-reading-and-writing-chain-state|reading and writing chain state]]
- [[web3/frameworks/javascript/README|JS/TS for web3]] — wagmi, viem, RainbowKit
- [[cybersecurity/04-web-security/02-secure-authentication|secure authentication]]
