import unittest

from decoding import greedy, sample, seeded_random, softmax, top_k, top_p

SCORES = [("Paris", 4.0), ("a", 2.0), ("the", 1.5), ("Lyon", 0.5)]


def rounded(dist):
    return {tok: round(p, 3) for tok, p in dist}


class DecodingTests(unittest.TestCase):
    def test_temperature_reshapes_the_same_scores(self):
        self.assertEqual(rounded(softmax(SCORES, 1)), {"Paris": 0.802, "a": 0.108, "the": 0.066, "Lyon": 0.024})
        self.assertEqual(rounded(softmax(SCORES, 0.5)), {"Paris": 0.975, "a": 0.018, "the": 0.007, "Lyon": 0.001})
        self.assertEqual(rounded(softmax(SCORES, 2)), {"Paris": 0.547, "a": 0.201, "the": 0.157, "Lyon": 0.095})

    def test_top_k_and_top_p(self):
        dist = softmax(SCORES, 1)
        self.assertEqual([t for t, _ in top_k(dist, 2)], ["Paris", "a"])
        self.assertEqual([t for t, _ in top_p(dist, 0.9)], ["Paris", "a"])
        self.assertEqual([t for t, _ in top_p(dist, 0.97)], ["Paris", "a", "the"])

    def test_same_seed_same_numbers_as_every_other_language(self):
        r = seeded_random(42)
        self.assertEqual([r(), r(), r()], [0.6011037519201636, 0.44829055899754167, 0.8524657934904099])

    def test_same_seed_same_tokens(self):
        dist, r = softmax(SCORES, 1), seeded_random(42)
        self.assertEqual(" ".join(sample(dist, r) for _ in range(10)), "Paris Paris a Paris Paris Paris Paris Paris a Paris")
        r = seeded_random(42)
        self.assertEqual(sum(sample(dist, r) == "Paris" for _ in range(1000)), 796)  # about 80.2%, as expected

    def test_greedy(self):
        self.assertEqual(greedy(softmax(SCORES, 2)), "Paris")


if __name__ == "__main__":
    unittest.main()
