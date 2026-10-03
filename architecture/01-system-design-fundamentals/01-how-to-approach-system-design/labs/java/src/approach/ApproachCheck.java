package approach;

import java.util.List;
import java.util.OptionalInt;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class ApproachCheck {
    private ApproachCheck() {}

    public static void main(String[] args) {
        var game = Approach.estimate(new Approach.Assumptions(10_000_000, 5, 10, 3, 50, 365, 2_000));
        assert Math.round(game.writesPerSecond().average()) == 579;
        assert Math.round(game.writesPerSecond().peak()) == 1736;
        assert Math.round(game.readsPerSecond().peak()) == 3472;
        assert game.readsPerWrite() == 2;
        assert Approach.humanBytes(game.storageBytes()).equals("910 GB") : Approach.humanBytes(game.storageBytes());
        assert Approach.humanBytes(game.peakEgressBytesPerSecond()).equals("6.9 MB");

        // Why the scan can't work. In int arithmetic the product wraps round silently to a wrong number.
        int peakReads = (int) Math.round(game.readsPerSecond().peak());
        int players = 50_000_000;
        assert peakReads * players == 1_801_308_160; // wrong, and no error
        assert (long) peakReads * players == 173_600_000_000L; // widen first
        try {
            Math.multiplyExact(peakReads, players);
            throw new AssertionError("expected an overflow");
        } catch (ArithmeticException expected) {
            // multiplyExact refuses instead of wrapping
        }
        assert Approach.humanBytes(players * 100.0).equals("5 GB");

        var board = new Approach.Leaderboard(1_000);
        board.submit("ada", 100);
        board.submit("bo", 250);
        board.submit("cy", 250);
        board.submit("di", 90);
        assert ranks(board, "bo", "cy", "ada", "di").equals(List.of(1, 1, 3, 4));
        assert !board.submit("ada", 80);
        assert board.submit("ada", 300);
        assert ranks(board, "ada", "bo", "cy", "di").equals(List.of(1, 2, 2, 4));
        assert board.rank("nobody").equals(OptionalInt.empty());
        try {
            board.submit("ed", 1_001);
            throw new AssertionError("expected a rejected score");
        } catch (IllegalArgumentException expected) {
            // above the maximum
        }

        int maxScore = 1_000_000;
        var big = new Approach.Leaderboard(maxScore);
        int[] scores = new int[200_000];
        for (int i = 0; i < scores.length; i++) {
            scores[i] = i * 7_919 % (maxScore + 1); // at most 1.6 billion: fits in an int
            big.submit("p" + i, scores[i]);
        }
        for (int i : new int[] {0, 1, 12_345, 199_999}) {
            var scan = Approach.rankByScan(scores, scores[i]);
            assert big.rank("p" + i).getAsInt() == scan.rank();
            assert big.steps <= 20 : big.steps;
            assert scan.steps() == 200_000;
        }
        System.out.println("all approach checks passed");
    }

    private static List<Integer> ranks(Approach.Leaderboard board, String... names) {
        return java.util.Arrays.stream(names).map(n -> board.rank(n).getAsInt()).toList();
    }
}
