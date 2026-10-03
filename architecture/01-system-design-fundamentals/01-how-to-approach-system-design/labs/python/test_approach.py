import unittest

from approach import Assumptions, Leaderboard, estimate, human_bytes, rank_by_scan

GAME = estimate(Assumptions(daily_active_users=10_000_000, writes_per_user_per_day=5, reads_per_user_per_day=10,
                            peak_to_average=3, bytes_per_write=50, kept_for_days=365, bytes_per_read=2_000))


def round_half_up(x: float) -> int:
    return int(x + 0.5)  # Python's round() sends halves to the even number; JavaScript's Math.round goes up


class Approach(unittest.TestCase):
    def test_estimate(self):
        self.assertEqual(round_half_up(GAME["writes_per_second"]["average"]), 579)
        self.assertEqual(round_half_up(GAME["writes_per_second"]["peak"]), 1736)
        self.assertEqual(round_half_up(GAME["reads_per_second"]["peak"]), 3472)
        self.assertEqual(GAME["reads_per_write"], 2)
        self.assertEqual(human_bytes(GAME["storage_bytes"]), "910 GB")
        self.assertEqual(human_bytes(GAME["peak_egress_bytes_per_second"]), "6.9 MB")

    def test_why_the_scan_cannot_work(self):
        players = 50_000_000
        self.assertEqual(round_half_up(GAME["reads_per_second"]["peak"]) * players, 173_600_000_000)  # ints never overflow
        self.assertEqual(human_bytes(players * 100), "5 GB")

    def test_ranks_ties_and_best_scores(self):
        board = Leaderboard(1_000)
        for player, score in [("ada", 100), ("bo", 250), ("cy", 250), ("di", 90)]:
            board.submit(player, score)
        self.assertEqual([board.rank(p) for p in ["bo", "cy", "ada", "di"]], [1, 1, 3, 4])
        self.assertFalse(board.submit("ada", 80))
        self.assertEqual(board.rank("ada"), 3)
        self.assertTrue(board.submit("ada", 300))
        self.assertEqual([board.rank(p) for p in ["ada", "bo", "cy", "di"]], [1, 2, 2, 4])
        self.assertIsNone(board.rank("nobody"))
        for bad in [1_001, 2.5, True]:
            with self.assertRaises(ValueError):
                board.submit("ed", bad)

    def test_about_20_steps_instead_of_one_per_player(self):
        max_score = 1_000_000
        board = Leaderboard(max_score)
        scores = [(i * 7_919) % (max_score + 1) for i in range(200_000)]
        for i, score in enumerate(scores):
            board.submit(f"p{i}", score)
        for i in [0, 1, 12_345, 199_999]:
            rank, steps = rank_by_scan(scores, scores[i])
            self.assertEqual(board.rank(f"p{i}"), rank)
            self.assertLessEqual(board.steps, 20)
            self.assertEqual(steps, 200_000)


if __name__ == "__main__":
    unittest.main()
