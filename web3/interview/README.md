# Web3 — Interview Prep

From the [[web3/README|web3 course]].

## Files
1. [[web3/interview/01-the-web3-round|The Web3 Round]] — fundamentals, the EVM, Solidity and security, building dapps, and the judgement questions. 🔥 marks what comes up constantly

## The scope note — read this first

**[[INTERVIEW|INTERVIEW.md]] states a principle this bank sits against:** *"an interview bank for a subject you haven't practised would be memorisation, not preparation."*

That principle holds, and this bank exists anyway — **written from the course, not from having sat these interviews, and honestly labelled.** Treat it as a **map of what the round asks**, not as a substitute for reps.

**What actually prepares you for this round is a deployed contract you can talk about.** Web3 hiring weights demonstrated work heavily, because the field is young and credentials are thin. A testnet deployment with a real test suite, an audit you did of someone else's code, or a bug bounty finding all outperform any answer here → [[build-your-own-shit/16-your-own-token-and-wallet|build your own token and wallet]].

## What this round tests

Unusually for a hiring round, **the security questions are the technical core, not a specialism.** You cannot patch, the code is public, and adversaries are funded — so "how would this be attacked?" is the default framing for every question about how something works.

Two failure modes this bank is written against:

1. **Reciting vulnerability classes.** Everyone can define reentrancy. Naming the read-only variant, or knowing that access control and stolen keys have cost more than reentrancy ever did, is what demonstrates understanding
2. **Uncalibrated enthusiasm.** A candidate who can't name what blockchains are bad at reads as someone who has absorbed marketing rather than engineering

## Related
- [[web3/README|the course]] · [[web3/04-smart-contract-security/README|smart contract security]]
- [[cybersecurity/interview/README|security interview bank]] — the adjacent round
- [[INTERVIEW|Interview Prep Index]]
