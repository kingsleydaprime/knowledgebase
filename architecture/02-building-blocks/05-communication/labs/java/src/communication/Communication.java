package communication;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;
import tools.jackson.databind.node.ArrayNode;
import tools.jackson.databind.node.ObjectNode;

/** What an API style costs, counted. The same numbers as the TypeScript lab. Java has no JSON built in: this uses Jackson. */
public final class Communication {
    private Communication() {}

    static final JsonMapper JSON = JsonMapper.shared();

    /** JSON as JSON.stringify writes it: Jackson is compact by default and keeps the fields in order. */
    public static int size(JsonNode node) {
        return JSON.writeValueAsString(node).length();
    }

    /** A tiny shop database that counts its queries. */
    public static final class Db {
        public int queries;
        private final Map<String, Map<String, JsonNode>> tables = new HashMap<>();

        public Db(JsonNode shop) {
            for (String table : List.of("customers", "products", "orders")) {
                Map<String, JsonNode> rows = new HashMap<>();
                for (JsonNode row : shop.get(table)) rows.put(row.get("id").asString(), row);
                tables.put(table, rows);
            }
        }

        /** One query for any number of rows: SELECT … WHERE id IN (…). */
        public List<JsonNode> find(String table, List<String> ids) {
            queries++;
            return ids.stream().map(tables.get(table)::get).toList();
        }
    }

    /** One whole resource per URL. Counts requests and bytes sent. */
    public static final class RestApi {
        private final Db db;
        public int requests;
        public int bytes;

        public RestApi(Db db) {
            this.db = db;
        }

        public JsonNode get(String path) {
            String[] parts = path.split("/"); // "/orders/o1" → "", "orders", "o1"
            if (parts.length != 3 || !List.of("orders", "customers", "products").contains(parts[1])) {
                throw new IllegalArgumentException("404 " + path);
            }
            JsonNode body = db.find(parts[1], List.of(parts[2])).getFirst();
            requests++;
            bytes += size(body);
            return body;
        }
    }

    public record Fetched(ObjectNode screen, int roundTrips) {}

    /** The order (round trip 1), then its customer and products together (round trip 2). */
    public static Fetched orderScreenRest(RestApi api, String orderId) {
        JsonNode order = api.get("/orders/" + orderId);
        JsonNode customer = api.get("/customers/" + order.get("customerId").asString());
        ObjectNode screen = JSON.createObjectNode();
        screen.set("id", order.get("id"));
        screen.set("totalPence", order.get("totalPence"));
        screen.putObject("customer").set("name", customer.get("name"));
        ArrayNode items = screen.putArray("items");
        for (JsonNode item : order.get("items")) {
            JsonNode product = api.get("/products/" + item.get("productId").asString());
            ObjectNode line = items.addObject();
            line.set("quantity", item.get("quantity"));
            line.putObject("product").set("name", product.get("name"));
        }
        return new Fetched(screen, 2);
    }

    /** Fields wanted, in order. An empty selection is a plain field; a non-empty one selects inside it. */
    public record Selection(Map<String, Selection> fields) {
        public static final Selection FIELD = new Selection(Map.of());

        public static Selection of(Object... nameThenSelection) {
            var fields = new LinkedHashMap<String, Selection>();
            for (int i = 0; i < nameThenSelection.length; i += 2) {
                fields.put((String) nameThenSelection[i], (Selection) nameThenSelection[i + 1]);
            }
            return new Selection(fields);
        }
    }

    /** A resolver fetches one field for every parent at one level of the query at once. */
    public interface Resolver extends Function<List<JsonNode>, List<JsonNode>> {}

    private static final Map<String, String> FIELD_TYPES = Map.of("Order.customer", "Customer", "Order.items", "Item", "Item.product", "Product");

    /** Runs a selection over every object at one level together, so each resolver sees the whole level. */
    public static List<ObjectNode> execute(List<JsonNode> values, Selection selection, Map<String, Resolver> resolvers, String type) {
        List<ObjectNode> outs = values.stream().map(v -> JSON.createObjectNode()).toList();
        selection.fields().forEach((field, sub) -> {
            Resolver resolver = resolvers.get(type + "." + field);
            List<JsonNode> children = resolver != null ? resolver.apply(values) : values.stream().map(v -> v.get(field)).toList();
            String childType = FIELD_TYPES.get(type + "." + field);
            if (sub.fields().isEmpty()) {
                for (int i = 0; i < outs.size(); i++) outs.get(i).set(field, children.get(i));
            } else if (!children.isEmpty() && children.getFirst().isArray()) { // a list: its elements form the next level
                List<JsonNode> flat = new ArrayList<>();
                children.forEach(c -> c.forEach(flat::add));
                var done = execute(flat, sub, resolvers, childType).iterator();
                for (int i = 0; i < outs.size(); i++) {
                    ArrayNode list = outs.get(i).putArray(field);
                    for (int n = 0; n < children.get(i).size(); n++) list.add(done.next());
                }
            } else {
                var done = execute(children, sub, resolvers, childType);
                for (int i = 0; i < outs.size(); i++) outs.get(i).set(field, done.get(i));
            }
        });
        return outs;
    }

    /** One query per parent (the N+1 problem), or one query for the whole level. */
    public static Map<String, Resolver> resolvers(Db db, boolean batched) {
        Function<String[], Resolver> make = tableAndKey -> parents -> {
            String table = tableAndKey[0];
            String key = tableAndKey[1];
            if (!batched) return parents.stream().map(p -> db.find(table, List.of(p.get(key).asString())).getFirst()).toList();
            var ids = new ArrayList<>(new LinkedHashSet<>(parents.stream().map(p -> p.get(key).asString()).toList())); // each once
            var rows = new HashMap<String, JsonNode>();
            var found = db.find(table, ids);
            for (int i = 0; i < ids.size(); i++) rows.put(ids.get(i), found.get(i));
            return parents.stream().map(p -> rows.get(p.get(key).asString())).toList();
        };
        return Map.of("Order.customer", make.apply(new String[] {"customers", "customerId"}),
                "Item.product", make.apply(new String[] {"products", "productId"}));
    }

    /** Base-128, low bits first, top bit set if more follow. >>> so the shift ignores the sign of a long. */
    public static byte[] varint(long n) {
        if (n < 0) throw new IllegalArgumentException("varint takes a whole number from 0");
        var out = new java.io.ByteArrayOutputStream();
        while ((n & ~0x7FL) != 0) {
            out.write((int) (n & 0x7F) | 0x80);
            n >>>= 7;
        }
        out.write((int) n);
        return out.toByteArray();
    }

    public static byte[] encodeOrderSummary(long id, String customer, long totalPence) {
        byte[] text = customer.getBytes(StandardCharsets.UTF_8); // bytes, not chars: protobuf strings are UTF-8
        var out = new java.io.ByteArrayOutputStream();
        out.writeBytes(varint(1 << 3));
        out.writeBytes(varint(id));
        out.writeBytes(varint(2 << 3 | 2));
        out.writeBytes(varint(text.length));
        out.writeBytes(text);
        out.writeBytes(varint(3 << 3));
        out.writeBytes(varint(totalPence));
        return out.toByteArray();
    }

    public record Call(double availability, double ms) {}

    public record Chain(double availability, double sequentialMs, double parallelMs) {}

    public static Chain chain(List<Call> calls) {
        double availability = 1;
        double sequential = 0;
        double parallel = 0;
        for (Call c : calls) {
            availability *= c.availability();
            sequential += c.ms();
            parallel = Math.max(parallel, c.ms());
        }
        return new Chain(availability, sequential, parallel);
    }
}
