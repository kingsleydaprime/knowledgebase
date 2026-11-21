import unittest

from statsmodels.stats.inter_rater import cohens_kappa
from statsmodels.stats.proportion import proportion_confint

from evals import agreement, compare, gate, keywords, load_golden, majority, pairwise, parse_label, run_eval, wilson

GOLDEN = load_golden()
HUMAN = [True, True, False, False, True, False, True, False, False, True]
LENIENT = [True, True, True, True, True, True, True, True, False, True]


def with_change(ticket_part: str, label: str):
    return lambda t: label if ticket_part in t else keywords(t)


class EvalTests(unittest.TestCase):
    def test_the_shared_golden_set(self):
        self.assertEqual(len(GOLDEN), 20)
        self.assertEqual({c["label"] for c in GOLDEN}, {"bug", "billing", "feature", "other"})

    def test_parse_label(self):
        self.assertEqual(parse_label("Category: BUG"), "bug")
        self.assertIsNone(parse_label("bug or billing"))

    def test_hand_written_wilson_matches_statsmodels(self):
        for passed, total in [(17, 20), (170, 200), (8, 20), (20, 20)]:
            ours = wilson(passed, total)
            theirs = proportion_confint(passed, total, alpha=0.05, method="wilson")
            self.assertAlmostEqual(ours[0], theirs[0], places=2)
            self.assertAlmostEqual(ours[1], theirs[1], places=2)
        self.assertEqual([round(x, 2) for x in wilson(17, 20)], [0.64, 0.95])

    def test_the_baselines_give_the_same_numbers_as_every_other_language(self):
        self.assertEqual(run_eval(majority(GOLDEN), GOLDEN).passed, 8)
        rules = run_eval(keywords, GOLDEN)
        self.assertEqual(rules.passed, 15)
        self.assertEqual([f"{r['id']}:{r['got']}" for r in rules.results if not r["pass"]],
                         ["t10:other", "t12:other", "t14:other", "t15:feature", "t20:billing"])
        self.assertEqual(rules.by_tag["other-language"], [0, 2])

    def test_compare_and_gate(self):
        base = run_eval(keywords, GOLDEN)
        self.assertEqual(compare(base, run_eval(with_change("La aplicación", "bug"), GOLDEN)), {"fixed": ["t14"], "broke": []})
        worse = run_eval(with_change("charged twice", "bug"), GOLDEN)
        self.assertEqual(gate(base, 0.6), [])
        self.assertEqual(gate(worse, 0.75, base, ("t02", "t18")),
                         ["pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed"])

    def test_pairwise_exposes_position_bias(self):
        self.assertEqual(pairwise(lambda _: "FIRST", "ticket", "reply A", "reply B"), "inconsistent")
        fair = lambda p: "FIRST" if p.index("reply B") < p.index("reply A") else "SECOND"
        self.assertEqual(pairwise(fair, "ticket", "reply A", "reply B"), "b")

    def test_hand_written_kappa_matches_statsmodels(self):
        agree, kappa = agreement(LENIENT, HUMAN)
        self.assertEqual((round(agree, 2), round(kappa, 2)), (0.6, 0.2))
        table = [[sum(j and h for j, h in zip(LENIENT, HUMAN)), sum(j and not h for j, h in zip(LENIENT, HUMAN))],
                 [sum(h and not j for j, h in zip(LENIENT, HUMAN)), sum(not j and not h for j, h in zip(LENIENT, HUMAN))]]
        self.assertAlmostEqual(cohens_kappa(table).kappa, kappa)


if __name__ == "__main__":
    unittest.main()
