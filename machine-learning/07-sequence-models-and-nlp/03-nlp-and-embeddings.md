---
id: 0898f6fd-0363-46bc-a2b6-0098570e7d43
---

# NLP & Embeddings

NLP is teaching computers to work with human language.

## What NLP and embeddings are
<!-- bite: 64b9298f-56bb-4c40-9a97-f27646a67a9a -->

Natural language processing (NLP) is teaching computers to work with human language, such as reading, sorting and writing text. Computers only do maths on numbers, so an embedding is a list of numbers that stands for a word or sentence and captures its meaning. Search boxes, autocorrect and chatbots all depend on this.

Next: the core problem, that text isn't numbers.

## The core problem: text isn't numbers
<!-- bite: 0e744de0-e73f-4261-93a2-e586e24b91af -->

Models do math on numbers ([[machine-learning/00-foundations/03-mathematics/01-linear-algebra/index|vectors]]); language is symbols. NLP is largely the pipeline that bridges that gap: turn raw text into numeric input, and turn model output back into text.

## Text preprocessing
<!-- bite: d8a5af43-01aa-4d7b-a7a8-5c8b447889ee -->

The classic steps that prepare text (still relevant, though modern LLMs subsume some):

- **Tokenization** — split text into units (tokens). Word-level is simple but has a huge vocabulary and can't handle unseen words; **subword tokenization** (BPE, WordPiece) — splitting rare words into pieces — is what modern models use, balancing vocabulary size against coverage ([[ai-engineering/02-how-llms-work/index|tokens]] in the applied view).
- **Normalization** — lowercasing, removing punctuation, handling Unicode.
- **Stemming** — chop words to a crude root (`running` → `run`, `studies` → `studi`) by rules; fast, imprecise.
- **Lemmatization** — reduce to the real dictionary form (`better` → `good`, `studies` → `study`) using vocabulary/grammar; slower, correct.
- **Stop-word removal** — drop very common words (`the`, `is`) for some classical tasks.

For classical NLP (e.g. [[machine-learning/03-classical-ml/11-naive-bayes|Naive Bayes]] spam filtering), text was then turned into **bag-of-words** or **TF-IDF** vectors — counts weighted by how distinctive a word is. These ignore word order and meaning, which embeddings fixed.

## Embeddings — representing meaning
<!-- bite: 6ceb18ee-f474-405f-8dc1-5deabbc25f63 -->

An **embedding** maps a token (or sentence, or document) to a dense [[machine-learning/00-foundations/03-mathematics/01-linear-algebra/01-vectors|vector]] such that **similar meanings land near each other** in the vector space. Unlike bag-of-words, embeddings capture semantics: "king" and "queen" are close; the famous `king − man + woman ≈ queen` vector arithmetic showed these spaces encode real relationships.

- **Word embeddings** (Word2Vec, GloVe) — one fixed vector per word, learned from co-occurrence. Limitation: "bank" gets one vector regardless of river-vs-money context.
- **Contextual embeddings** (from [[machine-learning/07-sequence-models-and-nlp/02-transformers-and-attention|transformers]] like BERT) — a word's vector depends on its sentence, so "bank" differs by context. This is what modern embedding models produce.

Embeddings are learned as a byproduct of training (the input layer of any language model is an embedding table) or from dedicated embedding models.

## Why embeddings matter downstream
<!-- bite: 7c10702c-2b9e-4ebd-9b7b-892e1347ab1f -->

Embeddings are the bridge from the modeling side to the applied side: they power **semantic search**, **clustering**, **classification**, and **recommendation** ([[machine-learning/08-other-architectures/02-recommendation-systems|recsys]]) by turning "is this similar in meaning?" into "are these vectors close?" ([[machine-learning/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|cosine similarity]]). This is exactly the foundation the AI-engineer [[ai-engineering/06-rag-and-embeddings/index|RAG]] system is built on — same embeddings, put to work retrieving relevant context for an LLM.

## Modern NLP
<!-- bite: 71021d35-b704-4085-ac57-9503d3d94c42 -->

The field has largely collapsed into "use a pretrained [[machine-learning/07-sequence-models-and-nlp/02-transformers-and-attention|transformer]]": fine-tune BERT-family models for classification/NER, or prompt an LLM for generation. The classical preprocessing above still matters for lightweight/classical pipelines, for understanding tokenization costs, and for the intuition of *why* embeddings work — but you rarely hand-build a TF-IDF pipeline anymore when a pretrained model is a few lines away.

## Check your understanding
<!-- bite: 09c55e71-72a7-47b2-9a22-7d5eb84798cb -->

Try each one before you open the answer.

1. <!-- q: mcq id="6983a5b0" -->
   Which turns "studies" into "study", using vocabulary and grammar?

   - [ ] Stemming
   - [x] Lemmatization
   - [ ] Tokenization

   <details><summary>Answer</summary>

   Lemmatization, which gives the real dictionary form. Stemming chops by rules and gives "studi".

   </details>

2. <!-- q: gap id="a106c08f" answers="queen" -->
   Fill in the gap. The famous embedding arithmetic is king − man + woman ≈ ___.

   <details><summary>Answer</summary>

   Queen. It showed that embedding spaces encode real relationships between meanings.

   </details>

3. <!-- q: mcq id="371967af" -->
   "Bank" gets the same vector in "river bank" and "bank account". Which kind of embedding does that?

   - [x] Word embeddings like Word2Vec or GloVe
   - [ ] Contextual embeddings from a transformer like BERT

   <details><summary>Answer</summary>

   Word embeddings: one fixed vector per word. Contextual embeddings give "bank" a different vector depending on its sentence.

   </details>

4. <!-- q: mcq id="b26c197d" -->
   What do modern language models use to split text into tokens?

   - [ ] Whole words only
   - [x] Subword tokenization, such as BPE or WordPiece
   - [ ] Single characters only

   <details><summary>Answer</summary>

   Subword tokenization. It splits rare words into pieces, which keeps the vocabulary small while still handling unseen words.

   </details>

5. <!-- q: open id="f45ad9c3" -->
   What did bag-of-words and TF-IDF miss that embeddings fixed?

   <details><summary>Answer</summary>

   They ignore word order and meaning: they only count words. Embeddings place similar meanings near each other, so "is this similar in meaning?" becomes "are these vectors close?".

   </details>

## Related
<!-- bite: ccccdd6a-6aae-49b7-b367-34a457fb39e2 -->
- [[machine-learning/07-sequence-models-and-nlp/02-transformers-and-attention|Transformers & Attention]] — what produces contextual embeddings
- [[ai-engineering/06-rag-and-embeddings/index|RAG & Embeddings]] — embeddings applied in production
- [[ai-engineering/02-how-llms-work/index|How LLMs Work]] — tokens in the applied view

## About this lesson
<!-- bite: 672f64bb-7311-4ea1-b5a7-a0ce3405e6ce -->

**Level:** reference. **Covers:** from the roadmap.sh `machine-learning` roadmap. How text becomes something a model can process, and how models represent meaning.
