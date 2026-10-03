package isolation;

import static isolation.Isolation.LOCK_NOT_AVAILABLE;
import static isolation.Isolation.SERIALIZATION_FAILURE;
import static isolation.Isolation.failure;
import static isolation.Isolation.number;
import static isolation.Isolation.run;

import java.sql.Connection;
import java.sql.SQLException;

/** The anomalies and their fixes through JDBC. Run through ../shared/with-postgres.sh, with -ea. */
public final class IsolationCheck {
    private IsolationCheck() {}

    private static final String BALANCE = "SELECT balance FROM accounts WHERE id = 1";

    private static void reset(Connection a) throws SQLException {
        run(a, """
            DROP TABLE IF EXISTS accounts, doctors;
            CREATE TABLE accounts (id int PRIMARY KEY, balance int NOT NULL CHECK (balance >= 0));
            INSERT INTO accounts VALUES (1, 100), (2, 50);
            CREATE TABLE doctors (name text PRIMARY KEY, on_call boolean NOT NULL);
            INSERT INTO doctors VALUES ('alice', true), ('bob', true)""");
    }

    private static void goOffCall(Connection c, String name) throws SQLException {
        run(c, "BEGIN ISOLATION LEVEL SERIALIZABLE");
        if (number(c, "SELECT count(*) FROM doctors WHERE on_call") >= 2) run(c, "UPDATE doctors SET on_call = false WHERE name = ?", name);
    }

    public static void main(String[] args) throws Exception {
        try (Connection a = Isolation.connect(); Connection b = Isolation.connect()) {
            reset(a); // a lost update at Read Committed
            run(a, "BEGIN");
            run(b, "BEGIN");
            long seenA = number(a, BALANCE);
            long seenB = number(b, BALANCE);
            run(a, "UPDATE accounts SET balance = ? WHERE id = 1", seenA - 10);
            run(a, "COMMIT");
            run(b, "UPDATE accounts SET balance = ? WHERE id = 1", seenB - 20);
            run(b, "COMMIT");
            assert number(a, BALANCE) == 80;

            reset(a); // Repeatable Read refuses the second write
            run(a, "BEGIN ISOLATION LEVEL REPEATABLE READ");
            run(b, "BEGIN ISOLATION LEVEL REPEATABLE READ");
            long seen = number(b, BALANCE);
            run(a, "UPDATE accounts SET balance = balance - 10 WHERE id = 1");
            run(a, "COMMIT");
            assert SERIALIZATION_FAILURE.equals(failure(() -> run(b, "UPDATE accounts SET balance = ? WHERE id = 1", seen - 20)));
            run(b, "ROLLBACK");

            reset(a); // FOR UPDATE makes the second reader wait
            run(a, "BEGIN");
            run(a, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE");
            run(b, "BEGIN");
            run(b, "SET LOCAL lock_timeout = '100ms'");
            assert LOCK_NOT_AVAILABLE.equals(failure(() -> run(b, "SELECT balance FROM accounts WHERE id = 1 FOR UPDATE")));
            run(b, "ROLLBACK");
            run(a, "COMMIT");

            reset(a); // write skew: Serializable aborts one, and the retry keeps the rule
            goOffCall(a, "alice");
            goOffCall(b, "bob");
            run(a, "COMMIT");
            assert SERIALIZATION_FAILURE.equals(failure(() -> run(b, "COMMIT")));
            Isolation.withRetry(5, () -> {
                try {
                    goOffCall(b, "bob");
                    run(b, "COMMIT");
                } catch (SQLException e) {
                    run(b, "ROLLBACK");
                    throw e;
                }
            });
            assert number(a, "SELECT count(*) FROM doctors WHERE on_call AND name = 'bob'") == 1;
            assert number(a, "SELECT count(*) FROM doctors WHERE on_call") == 1;
        }
        System.out.println("all isolation checks passed");
    }
}
