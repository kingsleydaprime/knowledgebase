package outbox;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/** The dual-write problem, and the transactional outbox that fixes it, over JDBC and SQLite. */
public final class Outbox {
    private Outbox() {}

    public static Connection openDb() throws SQLException {
        Connection db = DriverManager.getConnection("jdbc:sqlite::memory:"); // the sqlite-jdbc driver registers itself
        try (Statement s = db.createStatement()) {
            s.executeUpdate("CREATE TABLE orders (id TEXT PRIMARY KEY, total_kobo INTEGER NOT NULL CHECK (total_kobo > 0))");
            s.executeUpdate("""
                CREATE TABLE outbox (
                  seq INTEGER PRIMARY KEY AUTOINCREMENT,
                  event_id TEXT NOT NULL UNIQUE,
                  type TEXT NOT NULL,
                  payload TEXT NOT NULL,
                  published_at TEXT
                )""");
        }
        return db;
    }

    public record Event(String eventId, String type, String orderId) {}

    /** Stands in for RabbitMQ, Kafka or SQS: it records what it was sent. */
    public static final class FakeBroker {
        public final List<Event> sent = new ArrayList<>();

        public void publish(Event e) {
            sent.add(e);
        }
    }

    public static final class Crash extends RuntimeException {
        private static final long serialVersionUID = 1L;

        public Crash(String message) {
            super(message);
        }
    }

    public static int countOrders(Connection db) throws SQLException {
        try (Statement s = db.createStatement(); ResultSet r = s.executeQuery("SELECT COUNT(*) FROM orders")) {
            return r.getInt(1);
        }
    }

    private static void insertOrder(Connection db, String id, int totalKobo) throws SQLException {
        try (PreparedStatement p = db.prepareStatement("INSERT INTO orders (id, total_kobo) VALUES (?, ?)")) {
            p.setString(1, id);
            p.setInt(2, totalKobo);
            p.executeUpdate();
        }
    }

    // ---- The dual write: two systems, no shared transaction ----

    public static void placeOrderSaveThenPublish(Connection db, FakeBroker b, String id, int totalKobo, boolean crashBetween) throws SQLException {
        insertOrder(db, id, totalKobo); // auto-commit is on by default: this is saved at once
        if (crashBetween) throw new Crash("process died after the commit");
        b.publish(new Event("evt-" + id, "OrderPlaced", id));
    }

    public static void placeOrderPublishThenSave(Connection db, FakeBroker b, String id, int totalKobo) throws SQLException {
        b.publish(new Event("evt-" + id, "OrderPlaced", id));
        insertOrder(db, id, totalKobo);
    }

    // ---- The outbox: the event is written in the SAME transaction as the order ----

    public static void placeOrderWithOutbox(Connection db, String id, int totalKobo) throws SQLException {
        db.setAutoCommit(false); // JDBC's way to start a transaction
        try {
            insertOrder(db, id, totalKobo);
            try (PreparedStatement p = db.prepareStatement("INSERT INTO outbox (event_id, type, payload) VALUES (?, ?, ?)")) {
                p.setString(1, "evt-" + id);
                p.setString(2, "OrderPlaced");
                p.setString(3, "{\"orderId\":\"" + id + "\"}"); // the IDs are plain letters and digits; real code uses a JSON library
                p.executeUpdate();
            }
            db.commit();
        } catch (SQLException | RuntimeException e) {
            db.rollback();
            throw e;
        } finally {
            db.setAutoCommit(true);
        }
    }

    /** Publish first, then mark as sent. A crash in between means the event is sent again: at least once. */
    public static int relay(Connection db, FakeBroker b, boolean crashBeforeMark) throws SQLException {
        record Row(long seq, String eventId, String type, String payload) {}
        List<Row> pending = new ArrayList<>();
        try (Statement s = db.createStatement();
                ResultSet r = s.executeQuery("SELECT seq, event_id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY seq")) {
            while (r.next()) pending.add(new Row(r.getLong(1), r.getString(2), r.getString(3), r.getString(4)));
        }
        for (Row row : pending) {
            String orderId = row.payload().replaceAll(".*\"orderId\":\"([^\"]*)\".*", "$1");
            b.publish(new Event(row.eventId(), row.type(), orderId));
            if (crashBeforeMark) throw new Crash("relay died after publishing, before marking");
            try (PreparedStatement p = db.prepareStatement("UPDATE outbox SET published_at = datetime('now') WHERE seq = ?")) {
                p.setLong(1, row.seq());
                p.executeUpdate();
            }
        }
        return pending.size();
    }

    public static final class IdempotentConsumer {
        private final Set<String> seen = new HashSet<>();
        public final List<String> applied = new ArrayList<>();

        public String handle(Event e) {
            if (!seen.add(e.eventId())) return "duplicate"; // add returns false if it was already there
            applied.add(e.orderId());
            return "applied";
        }
    }
}
