package isolation;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Set;

/** A session stepped one statement at a time, and the retry loop, over JDBC. */
public final class Isolation {
    private Isolation() {}

    // PostgreSQL's error codes (SQLSTATE) for the outcomes concurrency makes normal. JDBC exposes them as getSQLState().
    public static final String SERIALIZATION_FAILURE = "40001";
    public static final String DEADLOCK_DETECTED = "40P01";
    public static final String LOCK_NOT_AVAILABLE = "55P03";
    private static final Set<String> RETRYABLE = Set.of(SERIALIZATION_FAILURE, DEADLOCK_DETECTED);

    public static Connection connect() throws SQLException {
        // Auto-commit is JDBC's default: with it on, the explicit BEGIN and COMMIT in the checks are the only ones.
        return DriverManager.getConnection("jdbc:postgresql://127.0.0.1:" + System.getenv("PGPORT") + "/postgres?user=postgres");
    }

    public static void run(Connection c, String sql) throws SQLException {
        try (Statement s = c.createStatement()) {
            s.execute(sql);
        }
    }

    /** A statement with parameters: values travel separately from the SQL, so they can't change its meaning. */
    public static void run(Connection c, String sql, Object... params) throws SQLException {
        try (var s = c.prepareStatement(sql)) {
            for (int i = 0; i < params.length; i++) s.setObject(i + 1, params[i]);
            s.execute();
        }
    }

    public static long number(Connection c, String sql) throws SQLException {
        try (Statement s = c.createStatement(); ResultSet r = s.executeQuery(sql)) {
            r.next();
            return r.getLong(1);
        }
    }

    /** The SQLSTATE an action fails with, or null if it succeeds. */
    public static String failure(Action action) {
        try {
            action.run();
            return null;
        } catch (SQLException e) {
            return e.getSQLState();
        }
    }

    @FunctionalInterface
    public interface Action {
        void run() throws SQLException;
    }

    /** Runs work again while PostgreSQL says the transaction should be retried, backing off each time. */
    public static void withRetry(int attempts, Action work) throws SQLException, InterruptedException {
        for (int attempt = 1; ; attempt++) {
            try {
                work.run();
                return;
            } catch (SQLException e) {
                if (attempt == attempts || !RETRYABLE.contains(e.getSQLState())) throw e;
                Thread.sleep(10L << attempt);
            }
        }
    }
}
