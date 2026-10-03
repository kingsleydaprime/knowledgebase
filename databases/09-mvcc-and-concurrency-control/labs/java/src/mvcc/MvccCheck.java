package mvcc;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.concurrent.Executors;

/** MVCC through JDBC: snapshots, blocked vacuum and a deadlock. Run through ../shared/with-postgres.sh, with -ea. */
public final class MvccCheck {
    private MvccCheck() {}

    static final String DEADLOCK_DETECTED = "40P01";
    static final String LOCK_NOT_AVAILABLE = "55P03";
    static final String BALANCE = "SELECT balance FROM accounts WHERE id = 1";

    static Connection connect() throws SQLException {
        return DriverManager.getConnection("jdbc:postgresql://127.0.0.1:" + System.getenv("PGPORT") + "/postgres?user=postgres");
    }

    static void run(Connection c, String sql) throws SQLException {
        try (Statement s = c.createStatement()) {
            s.execute(sql);
        }
    }

    static long number(Connection c, String sql) throws SQLException {
        try (Statement s = c.createStatement(); ResultSet r = s.executeQuery(sql)) {
            r.next();
            return r.getLong(1);
        }
    }

    /** The SQLSTATE a statement fails with, or null if it succeeds. */
    static String failure(Connection c, String sql) {
        try {
            run(c, sql);
            return null;
        } catch (SQLException e) {
            return e.getSQLState();
        }
    }

    static int pid(Connection c) throws SQLException {
        return (int) number(c, "SELECT pg_backend_pid()");
    }

    static void waitUntilBlocked(Connection watcher, int pid) throws SQLException, InterruptedException {
        try (PreparedStatement s = watcher.prepareStatement("SELECT wait_event_type FROM pg_stat_activity WHERE pid = ?")) {
            s.setInt(1, pid);
            for (int i = 0; i < 500; i++) {
                try (ResultSet r = s.executeQuery()) {
                    if (r.next() && "Lock".equals(r.getString(1))) return;
                }
                Thread.sleep(10);
            }
        }
        throw new AssertionError("session " + pid + " never waited for a lock");
    }

    static void reset(Connection a) throws SQLException {
        run(a, """
            CREATE EXTENSION IF NOT EXISTS pgstattuple;
            DROP TABLE IF EXISTS accounts;
            CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL);
            INSERT INTO accounts SELECT i, 100 FROM generate_series(1, 1000) i""");
        run(a, "VACUUM accounts"); // alone: VACUUM can't run inside a multi-statement call's transaction
    }

    public static void main(String[] args) throws Exception {
        try (Connection a = connect(); Connection b = connect(); Connection watcher = connect()) {
            reset(a); // readers don't block writers
            run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
            assert number(a, BALANCE) == 100;
            run(b, "SET lock_timeout = '100ms'");
            run(b, "UPDATE accounts SET balance = 50 WHERE id = 1");
            assert number(a, BALANCE) == 100;
            run(a, "COMMIT");
            assert number(a, BALANCE) == 50;

            reset(a); // writers block writers
            run(a, "BEGIN");
            run(a, "UPDATE accounts SET balance = 90 WHERE id = 1");
            assert LOCK_NOT_AVAILABLE.equals(failure(b, "UPDATE accounts SET balance = 80 WHERE id = 1"));
            run(a, "COMMIT");

            reset(a); // an open snapshot stops vacuum
            run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
            run(a, "SELECT 1");
            run(b, "UPDATE accounts SET balance = balance + 1");
            run(b, "VACUUM accounts");
            assert number(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')") == 1000;
            run(a, "COMMIT");
            run(b, "VACUUM accounts");
            assert number(b, "SELECT dead_tuple_count FROM pgstattuple('accounts')") == 0;

            reset(a); // a deadlock: exactly one victim
            run(b, "RESET lock_timeout");
            run(a, "SET deadlock_timeout = '100ms'");
            run(b, "SET deadlock_timeout = '100ms'");
            run(a, "BEGIN");
            run(b, "BEGIN");
            run(a, "UPDATE accounts SET balance = 1 WHERE id = 1");
            run(b, "UPDATE accounts SET balance = 2 WHERE id = 2");
            int aPid = pid(a);
            try (var threads = Executors.newVirtualThreadPerTaskExecutor()) {
                var aWantsRow2 = threads.submit(() -> failure(a, "UPDATE accounts SET balance = 1 WHERE id = 2"));
                waitUntilBlocked(watcher, aPid);
                String bResult = failure(b, "UPDATE accounts SET balance = 2 WHERE id = 1");
                long victims = List.of(String.valueOf(aWantsRow2.get()), String.valueOf(bResult)).stream().filter(DEADLOCK_DETECTED::equals).count();
                assert victims == 1 : aWantsRow2.get() + " " + bResult;
            }
            run(a, "ROLLBACK");
            run(b, "ROLLBACK");
        }
        System.out.println("all mvcc checks passed");
    }
}
