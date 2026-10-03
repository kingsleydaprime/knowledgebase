package btree;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** The model checks, then the PostgreSQL checks through JDBC. Run through ../shared/with-postgres.sh, with -ea. */
public final class BTreeCheck {
    private BTreeCheck() {}

    public static void main(String[] args) throws Exception {
        assert Math.ceil(Math.log(1e8) / Math.log(2)) == 27;
        assert BTree.levels(100_000_000, 367, 400) == 4 && BTree.levels(1_000_000, 367, 400) == 3;

        var small = new BTree.BPlusTree(3);
        for (int k = 1; k <= 10; k++) small.insert(k, "v" + k);
        assert small.height == 3;
        assert small.search(7).equals(new BTree.Found("v7", 3)) && small.search(99).equals(new BTree.Found(null, 3));
        assert small.range(4, 8).equals(new BTree.Ranged(List.of("v4", "v5", "v6", "v7", "v8"), 6)) : small.range(4, 8);

        var big = new BTree.BPlusTree(400);
        for (int i = 0; i < 1_000_000; i++) big.insert((int) ((long) i * 7919 % 1_000_000), ""); // i * 7919 overflows an int
        assert big.height == 3 && big.search(424_242).pages() == 3;

        var index = List.of("a", "b", "c");
        assert BTree.usablePrefix(index, Set.of("a"), Set.of()).equals(List.of("a"));
        assert BTree.usablePrefix(index, Set.of("a", "b", "c"), Set.of()).equals(index);
        assert BTree.usablePrefix(index, Set.of("b"), Set.of()).isEmpty();
        assert BTree.usablePrefix(index, Set.of("a", "c"), Set.of()).equals(List.of("a"));
        assert BTree.usablePrefix(index, Set.of("b"), Set.of("a")).equals(List.of("a"));
        assert BTree.usablePrefix(index, Set.of("a"), Set.of("b")).equals(List.of("a", "b"));

        // pgjdbc connects over TCP; with-postgres.sh listens on 127.0.0.1 as well as its socket.
        String url = "jdbc:postgresql://127.0.0.1:" + System.getenv("PGPORT") + "/postgres?user=postgres";
        try (Connection db = DriverManager.getConnection(url); Statement s = db.createStatement()) {
            for (String statement : Files.readString(Path.of("../shared/orders.sql")).split(";\n")) {
                if (!statement.replaceAll("(?m)^--.*$", "").isBlank()) s.execute(statement); // one at a time, for VACUUM
            }
            try (ResultSet r = s.executeQuery("SELECT level FROM bt_metap('orders_pkey')")) {
                r.next();
                assert r.getLong(1) == 2;
            }
            var lookup = explain(s, "SELECT * FROM orders WHERE id = 424242");
            assert lookup.getFirst().get("Node Type").asString().equals("Index Scan") && pages(lookup) == 4;

            s.execute("CREATE INDEX orders_customer_created ON orders (customer_id, created_at)");
            var both = explain(s, "SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'");
            assert both.stream().anyMatch(n -> n.path("Index Name").asString("").equals("orders_customer_created"));
            var hour = explain(s, "SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'");
            assert hour.getFirst().get("Node Type").asString().equals("Seq Scan");
            s.execute("DROP INDEX orders_customer_created");

            s.execute("CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)");
            s.execute("VACUUM orders");
            var clean = explain(s, "SELECT total FROM orders WHERE customer_id = 42");
            assert clean.getFirst().get("Node Type").asString().equals("Index Only Scan") && clean.getFirst().get("Heap Fetches").asInt() == 0;
            s.execute("UPDATE orders SET total = total + 1 WHERE customer_id = 42");
            assert explain(s, "SELECT total FROM orders WHERE customer_id = 42").getFirst().get("Heap Fetches").asInt() > 0;
        }
        System.out.println("all b-tree checks passed");
    }

    private static List<JsonNode> explain(Statement s, String sql) throws SQLException {
        try (ResultSet r = s.executeQuery("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) " + sql)) {
            r.next();
            List<JsonNode> out = new ArrayList<>();
            collect(JsonMapper.shared().readTree(r.getString(1)).get(0).get("Plan"), out); // JDBC hands json over as text
            return out;
        }
    }

    private static void collect(JsonNode node, List<JsonNode> out) {
        out.add(node);
        node.path("Plans").forEach(child -> collect(child, out));
    }

    private static int pages(List<JsonNode> plan) {
        return plan.getFirst().get("Shared Hit Blocks").asInt() + plan.getFirst().get("Shared Read Blocks").asInt();
    }
}
