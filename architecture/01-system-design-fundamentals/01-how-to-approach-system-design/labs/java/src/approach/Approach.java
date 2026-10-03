package approach;

import java.math.BigDecimal;
import java.math.MathContext;
import java.util.HashMap;
import java.util.Map;
import java.util.OptionalInt;

/** Back-of-the-envelope estimates, and a leaderboard that ranks millions of players in about 20 steps. */
public final class Approach {
    private Approach() {}

    public static final double SECONDS_PER_DAY = 86_400;

    public record Assumptions(double dailyActiveUsers, double writesPerUserPerDay, double readsPerUserPerDay,
            double peakToAverage, double bytesPerWrite, double keptForDays, double bytesPerRead) {}

    public record Rate(double average, double peak) {}

    public record Estimate(Rate writesPerSecond, Rate readsPerSecond, double readsPerWrite, double storageBytes,
            double peakEgressBytesPerSecond) {}

    public static Estimate estimate(Assumptions a) {
        double writes = a.dailyActiveUsers() * a.writesPerUserPerDay() / SECONDS_PER_DAY;
        double reads = a.dailyActiveUsers() * a.readsPerUserPerDay() / SECONDS_PER_DAY;
        return new Estimate(
                new Rate(writes, writes * a.peakToAverage()),
                new Rate(reads, reads * a.peakToAverage()),
                a.readsPerUserPerDay() / a.writesPerUserPerDay(),
                a.dailyActiveUsers() * a.writesPerUserPerDay() * a.bytesPerWrite() * a.keptForDays(),
                reads * a.peakToAverage() * a.bytesPerRead());
    }

    /** Two significant figures in powers of 1,000: 912,500,000,000 → "910 GB". */
    public static String humanBytes(double n) {
        String[] units = {"B", "KB", "MB", "GB", "TB", "PB"};
        int i = 0;
        while (n >= 1000 && i < units.length - 1) {
            n /= 1000;
            i++;
        }
        // BigDecimal rounds the exact value to 2 figures; toPlainString avoids "9.1E+2".
        return new BigDecimal(n).round(new MathContext(2)).stripTrailingZeros().toPlainString() + " " + units[i];
    }

    /** Each player's best score, and a Fenwick tree of how many players have each score. */
    public static final class Leaderboard {
        private final int maxScore;
        private final Map<String, Integer> best = new HashMap<>();
        private final int[] tree;
        public int steps; // the work the last rank() did

        public Leaderboard(int maxScore) {
            this.maxScore = maxScore;
            this.tree = new int[maxScore + 2];
        }

        public int players() {
            return best.size();
        }

        /** Only a player's best counts. A score can't be 2.5: the int type rules it out. */
        public boolean submit(String player, int score) {
            if (score < 0 || score > maxScore) {
                throw new IllegalArgumentException("score must be from 0 to " + maxScore + ", got " + score);
            }
            Integer old = best.get(player);
            if (old != null && score <= old) return false;
            if (old != null) add(old, -1);
            add(score, +1);
            best.put(player, score);
            return true;
        }

        public OptionalInt rank(String player) {
            Integer score = best.get(player);
            if (score == null) return OptionalInt.empty();
            steps = 0;
            return OptionalInt.of(1 + players() - countAtMost(score));
        }

        private void add(int score, int delta) {
            for (int i = score + 1; i < tree.length; i += i & -i) tree[i] += delta;
        }

        private int countAtMost(int score) {
            int count = 0;
            for (int i = score + 1; i > 0; i -= i & -i) {
                count += tree[i];
                steps++;
            }
            return count;
        }
    }

    public record Scan(int rank, int steps) {}

    public static Scan rankByScan(int[] scores, int mine) {
        int higher = 0;
        int steps = 0;
        for (int s : scores) {
            steps++;
            if (s > mine) higher++;
        }
        return new Scan(1 + higher, steps);
    }
}
