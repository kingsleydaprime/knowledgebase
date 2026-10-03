package joins;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.IntStream;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** The model checks, then the PostgreSQL checks through JDBC. Run through ../shared/with-postgres.sh, with -ea. */
public final class JoinsCheck {
    private JoinsCheck() {}

    public static void main(String[] args) throws Exception {
        List<Joins.Row> orders = IntStream.range(0, 10_000).mapToObj(i -> new Joins.Row(1 + i % 1_000, "order " + i)).toList();
        List<Joins.Row> customers = IntStream.rangeClosed(1, 1_000).mapToObj(c -> new Joins.Row(c, "customer " + c)).toList();
        List<Joins.Row> sortedOrders = orders.stream().sorted(Comparator.comparingInt(Joins.Row::key)).toList(); // a stable sort

        var expected = canonical(Joins.nestedLoop(orders, customers).rows());
        assert expected.size() == 10_000;
        assert canonical(Joins.indexNestedLoop(orders, customers).rows()).equals(expected);
        assert canonical(Joins.hashJoin(orders, customers).rows()).equals(expected);
        assert canonical(Joins.mergeJoin(sortedOrders, customers).rows()).equals(expected);

        var work = List.of(Joins.nestedLoop(orders, customers).work(), Joins.indexNestedLoop(orders, customers).work(),
                Joins.hashJoin(orders, customers).work(), Joins.mergeJoin(sortedOrders, customers).work());
        assert work.equals(List.of(10_000_000, 99_780, 11_000, 10_999)) : work;
        var one = orders.stream().filter(o -> o.key() == 42).toList();
        assert Joins.indexNestedLoop(one, customers).work() == 100 && Joins.hashJoin(one, customers).work() == 1_010;

        assert Math.round(Joins.independentEstimate(30_000, 0.1, 0.3)) == 900 && Math.round(Joins.independentEstimate(30_000, 0.1)) == 3_000;
        assert Joins.rowsReadForPage(100_000, 20, false) == 100_020 && Joins.rowsReadForPage(100_000, 20, true) == 20;

        String url = "jdbc:postgresql://127.0.0.1:" + System.getenv("PGPORT") + "/postgres?user=postgres";
        try (Connection db = DriverManager.getConnection(url); Statement s = db.createStatement()) {
            for (String statement : Files.readString(Path.of("../shared/shop.sql")).split(";\n")) {
                if (!statement.replaceAll("(?m)^--.*$", "").isBlank()) s.execute(statement);
            }
            String join = "SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id";
            assert hashBatches(s, join) == 1;
            s.execute("SET work_mem = '64kB'");
            assert hashBatches(s, join) == 16;
            s.execute("RESET work_mem");

            String query = "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'";
            var before = explain(s, query).getFirst();
            assert before.get("Plan Rows").asInt() == 900 && before.get("Actual Rows").asInt() == 3000;
            s.execute("CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses");
            s.execute("ANALYZE addresses");
            assert explain(s, query).getFirst().get("Plan Rows").asInt() == 3000;

            assert explain(s, "SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20").get(1).get("Actual Rows").asInt() == 100_020;
            assert explain(s, "SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20").get(1).get("Actual Rows").asInt() == 20;
        }
        System.out.println("all join checks passed");
    }

    private static List<String> canonical(List<Joins.Pair> rows) {
        return rows.stream().map(p -> p.outer() + "|" + p.inner()).sorted().toList();
    }

    private static int hashBatches(Statement s, String sql) throws SQLException {
        return explain(s, sql).stream().filter(n -> n.get("Node Type").asString().equals("Hash")).findFirst().orElseThrow().get("Hash Batches").asInt();
    }

    private static List<JsonNode> explain(Statement s, String sql) throws SQLException {
        try (ResultSet r = s.executeQuery("EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) " + sql)) {
            r.next();
            List<JsonNode> out = new ArrayList<>();
            collect(JsonMapper.shared().readTree(r.getString(1)).get(0).get("Plan"), out);
            return out;
        }
    }

    private static void collect(JsonNode node, List<JsonNode> out) {
        out.add(node);
        node.path("Plans").forEach(child -> collect(child, out));
    }
}
