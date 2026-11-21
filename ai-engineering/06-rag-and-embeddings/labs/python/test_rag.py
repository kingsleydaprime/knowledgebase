import unittest

import numpy as np
from rank_bm25 import BM25Okapi

from rag import (bm25, check_citations, chunk_doc, cosine, docs_of, grounded_prompt, load, mrr, recall_at_k, rrf, tokens,
                 toy_embed, vector_search, with_context)

DOCS = load("help.json")
CHUNKS = [{"id": c["id"], "text": with_context(c, d["title"])} for d in DOCS for c in chunk_doc(d)]
QUESTIONS = load("questions.json")


def rounded(ranked):
    return [(i, round(s, 4)) for i, s in ranked]


class Rag(unittest.TestCase):
    def test_chunks(self):
        self.assertEqual([c["id"] for c in CHUNKS], ["refunds#1", "refunds#2", "refunds#3", "password#1", "password#2",
                                                     "export#1", "export#2", "appearance#1", "shipping#1", "shipping#2"])
        self.assertEqual(CHUNKS[1]["text"], "Refunds > How long a refund takes\nMost refunds arrive within 5 to 10 working days. "
                                            "Your bank may take a few more days to show it.")
        long = {"id": "long", "title": "Long", "body": "## Part\none two three four\n\nfive six seven eight\n\nnine ten eleven twelve"}
        self.assertEqual([c["text"] for c in chunk_doc(long, 8)],
                         ["one two three four\n\nfive six seven eight", "five six seven eight\n\nnine ten eleven twelve"])

    def test_cosine_against_numpy(self):
        self.assertEqual((cosine([1, 0], [5, 0]), cosine([1, 0], [0, 1]), round(cosine([1, 0], [1, 1]), 3), cosine([0, 0], [1, 1])),
                         (1.0, 0.0, 0.707, 0.0))
        a, b = np.array(toy_embed(CHUNKS[3]["text"])), np.array(toy_embed("My login doesn't work any more."))
        self.assertAlmostEqual(cosine(list(a), list(b)), float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b))))

    def test_the_hand_made_embedding(self):
        self.assertEqual(toy_embed("My login doesn't work any more."), [1, 0, 0, 0, 0, 0])
        self.assertEqual(toy_embed("What does E1042 mean?"), [0] * 6)

    def test_the_same_rankings_and_scores_as_typescript(self):
        k = bm25("My login doesn't work any more.", CHUNKS)
        v = vector_search("My login doesn't work any more.", CHUNKS, toy_embed)
        self.assertEqual(rounded(k), [("refunds#2", 1.8951), ("refunds#1", 1.6952)])
        self.assertEqual(rounded(v), [("password#1", 0.9864), ("password#2", 0.9701)])
        self.assertEqual([i for i, _ in rrf([k, v])], ["refunds#2", "password#1", "refunds#1", "password#2"])
        self.assertEqual(rounded(bm25("What does E1042 mean?", CHUNKS)), [("export#2", 2.8115)])
        darker = bm25("Can I make the app darker?", CHUNKS)
        self.assertEqual(rounded(darker)[:3], [("refunds#1", 1.8249), ("appearance#1", 1.2348), ("password#2", 1.1894)])

    def test_bm25_ranks_like_the_rank_bm25_library(self):
        # rank_bm25's Okapi BM25 uses a slightly different idf, so the scores differ but the order agrees.
        corpus = [tokens(c["text"]) for c in CHUNKS]
        library = BM25Okapi(corpus).get_scores(tokens("What does E1042 mean?"))
        self.assertEqual(CHUNKS[int(np.argmax(library))]["id"], bm25("What does E1042 mean?", CHUNKS)[0][0])

    def test_retrieval_metrics(self):
        results = {"keyword": {}, "vector": {}, "hybrid": {}}
        for q in QUESTIONS:
            k, v = bm25(q["question"], CHUNKS), vector_search(q["question"], CHUNKS, toy_embed)
            results["keyword"][q["id"]], results["vector"][q["id"]], results["hybrid"][q["id"]] = docs_of(k), docs_of(v), docs_of(rrf([k, v]))
        score = {n: (recall_at_k(r, QUESTIONS, 1), recall_at_k(r, QUESTIONS, 3), round(mrr(r, QUESTIONS), 3)) for n, r in results.items()}
        self.assertEqual(score, {"keyword": (0.6, 0.8, 0.7), "vector": (0.8, 0.8, 0.8), "hybrid": (0.8, 1.0, 0.9)})

    def test_prompt_and_citations(self):
        prompt = grounded_prompt("How long?", [{"id": "refunds#2", "text": "Most refunds arrive within 5 to 10 working days."}])
        self.assertIn('[S1] (refunds#2)\nMost refunds arrive within 5 to 10 working days.', prompt)
        self.assertEqual(check_citations("Within 5 to 10 working days [S1].", 2), {"ok": True, "problems": []})
        self.assertEqual(check_citations("I don't know.", 2), {"ok": True, "problems": []})
        self.assertEqual(check_citations("Refunds are instant.", 2), {"ok": False, "problems": ["no citations"]})
        self.assertEqual(check_citations("A week [S3].", 2), {"ok": False, "problems": ["cites S3, which wasn't given"]})


if __name__ == "__main__":
    unittest.main()
