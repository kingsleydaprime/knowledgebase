# Information Theory

## What information theory is

**Information theory is the maths of measuring information: how much a message really tells you, how small it can be squeezed, and how fast it can be sent through a noisy line without errors.**

Its central idea is simple: **information is surprise.** If a friend who's always late texts "I'll be late", you learn almost nothing, because you expected it. If they text "I'm early", you learn a lot. Claude Shannon turned that into a number in 1948, measured in **bits**, and that one number turned out to govern a surprising range of things.

It sets the limit on how small a file can be zipped. It sets the top speed of Wi-Fi and mobile data. It explains the error-correcting codes that let a scratched DVD still play. It measures how strong a password really is. And it's the maths behind the "loss" that almost every AI model is trained to reduce.

## What you'll be able to do

By the end you will be able to:
- measure how much information a source produces, in bits;
- measure how much knowing one thing tells you about another, even when the link isn't a straight line;
- explain the limit on compression, and how real compressors approach it;
- explain why AI models are trained on "cross-entropy", and what that means;
- work out the top speed of a noisy channel, like a Wi-Fi link;
- explain how error-correcting codes fix mistakes in transmitted or stored data.

## Where to start

**Before you start:** [[mathematics/01-core/01-numbers/03-indices-and-logarithms/01-indices-and-logarithms|logarithms]] and basic [[mathematics/05-probability-statistics/index|probability]].

Read notes 01 and 02 first, in order. Notes 03–06 are four separate applications and can be read in any order. Note 07 brings them together.

1. [[information-theory/01-what-information-is|What Information Is]]: surprise, the bit, entropy (the average surprise of a source), and why English carries only about 1.1 bits per letter.
2. [[information-theory/02-entropy-joint-conditional-and-mutual|Joint, Conditional and Mutual Information]]: measuring how much one thing tells you about another, which catches links that ordinary correlation misses.
3. [[information-theory/03-source-coding-and-compression|Source Coding and Compression]]: the hard limit on compression, and the methods that get close to it.
4. [[information-theory/04-cross-entropy-and-kl-divergence|Cross-Entropy and KL Divergence]]: the note the AI material needs. Why models are trained to reduce cross-entropy, and why predicting well and compressing well are the same thing.
5. [[information-theory/05-channel-capacity-and-noise|Channel Capacity and Noise]]: the top speed of any noisy connection, and why Wi-Fi is as fast as it is.
6. [[information-theory/06-error-correcting-codes|Error-Correcting Codes]]: adding a little extra data so mistakes can be found and fixed, and the 50 years it took to reach Shannon's limit.
7. [[information-theory/07-where-information-theory-shows-up|Where It Shows Up]]: the same measure across nine different fields.

## Practice

- [[information-theory/08-practice-exercises|Practice Exercises]]: problems and small programs.
- [[information-theory/09-practice-exercises-solutions|Solutions]]: worked answers. Try first.

## Key ideas to remember

1. **Information is surprise.** Unlikely events carry more information than likely ones. → [[information-theory/01-what-information-is|01]]
2. **No compressor can shrink everything.** Below a certain size, information is genuinely lost; "compresses anything" claims are provably false. → [[information-theory/03-source-coding-and-compression|03]]
3. **Processing data can't add information to it.** No amount of reworking adds signal that wasn't there. → [[information-theory/02-entropy-joint-conditional-and-mutual|02]]
4. **Training an AI model to predict well is the same as training it to compress well.** → [[information-theory/04-cross-entropy-and-kl-divergence|04]]
5. **Below a channel's top speed, errors can be made almost zero; above it, they can't.** It's a sharp line, not a gradual trade. → [[information-theory/05-channel-capacity-and-noise|05]]
6. **A password's strength depends on how it was made, not how random it looks.** `Tr0ub4dor&3` looks random and isn't. → [[information-theory/07-where-information-theory-shows-up|07]]

## Related

- [[ai-ml/index|AI & ML]]: where cross-entropy is used everywhere.
- [[networking/index|Networking]]: where channel capacity sets real speeds.
- [[digital-signal-processing/index|Digital Signal Processing]]: turning signals into numbers.
- [[cybersecurity/05-cryptography/index|Cryptography]]: randomness and key strength.
- [[mathematics/02-discrete-math/index|Discrete Mathematics]]: the counting and number theory behind codes.

---

## About this course

- **Size:** 9 notes, about 11,700 words, including practice and solutions. Written in August 2026, because the AI notes used cross-entropy without ever explaining it, and other parts of the vault leaned on these ideas in pieces.
