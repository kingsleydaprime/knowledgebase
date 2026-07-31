# NLP & Embeddings

**[reference]** — from the roadmap.sh `machine-learning` roadmap. How text becomes something a model can process, and how models represent meaning.

## The core problem: text isn't numbers

Models do math on numbers ([[ai-ml/00-foundations/03-mathematics/01-linear-algebra/README|vectors]]); language is symbols. NLP is largely the pipeline that bridges that gap: turn raw text into numeric input, and turn model output back into text.

## Text preprocessing

The classic steps that prepare text (still relevant, though modern LLMs subsume some):

- **Tokenization** — split text into units (tokens). Word-level is simple but has a huge vocabulary and can't handle unseen words; **subword tokenization** (BPE, WordPiece) — splitting rare words into pieces — is what modern models use, balancing vocabulary size against coverage ([[ai-ml/03-ai-engineer/02-how-llms-work|tokens]] in the applied view).
- **Normalization** — lowercasing, removing punctuation, handling Unicode.
- **Stemming** — chop words to a crude root (`running` → `run`, `studies` → `studi`) by rules; fast, imprecise.
- **Lemmatization** — reduce to the real dictionary form (`better` → `good`, `studies` → `study`) using vocabulary/grammar; slower, correct.
- **Stop-word removal** — drop very common words (`the`, `is`) for some classical tasks.

For classical NLP (e.g. [[ai-ml/02-ml-engineer/03-classical-ml/03-svm-knn-naive-bayes|Naive Bayes]] spam filtering), text was then turned into **bag-of-words** or **TF-IDF** vectors — counts weighted by how distinctive a word is. These ignore word order and meaning, which embeddings fixed.

## Embeddings — representing meaning

An **embedding** maps a token (or sentence, or document) to a dense [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/01-vectors|vector]] such that **similar meanings land near each other** in the vector space. Unlike bag-of-words, embeddings capture semantics: "king" and "queen" are close; the famous `king − man + woman ≈ queen` vector arithmetic showed these spaces encode real relationships.

- **Word embeddings** (Word2Vec, GloVe) — one fixed vector per word, learned from co-occurrence. Limitation: "bank" gets one vector regardless of river-vs-money context.
- **Contextual embeddings** (from [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|transformers]] like BERT) — a word's vector depends on its sentence, so "bank" differs by context. This is what modern embedding models produce.

Embeddings are learned as a byproduct of training (the input layer of any language model is an embedding table) or from dedicated embedding models.

## Why embeddings matter downstream

Embeddings are the bridge from the modeling side to the applied side: they power **semantic search**, **clustering**, **classification**, and **recommendation** ([[ai-ml/02-ml-engineer/08-other-architectures/02-recommendation-systems|recsys]]) by turning "is this similar in meaning?" into "are these vectors close?" ([[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|cosine similarity]]). This is exactly the foundation the AI-engineer [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]] system is built on — same embeddings, put to work retrieving relevant context for an LLM.

## Modern NLP

The field has largely collapsed into "use a pretrained [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|transformer]]": fine-tune BERT-family models for classification/NER, or prompt an LLM for generation. The classical preprocessing above still matters for lightweight/classical pipelines, for understanding tokenization costs, and for the intuition of *why* embeddings work — but you rarely hand-build a TF-IDF pipeline anymore when a pretrained model is a few lines away.

## Related
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|Transformers & Attention]] — what produces contextual embeddings
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG & Embeddings]] — embeddings applied in production
- [[ai-ml/03-ai-engineer/02-how-llms-work|How LLMs Work]] — tokens in the applied view
