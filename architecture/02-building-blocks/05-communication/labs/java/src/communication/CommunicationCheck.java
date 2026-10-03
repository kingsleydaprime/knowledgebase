package communication;

import static communication.Communication.Selection.FIELD;

import communication.Communication.Selection;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.stream.IntStream;
import tools.jackson.databind.JsonNode;

/** The same checks as every other language. Run with -ea so assert statements are on. */
public final class CommunicationCheck {
    private CommunicationCheck() {}

    public static void main(String[] args) throws Exception {
        JsonNode shop = Communication.JSON.readTree(Files.readString(Path.of("../shared/shop.json")));
        var screenQuery = Selection.of("id", FIELD, "totalPence", FIELD, "customer", Selection.of("name", FIELD),
                "items", Selection.of("quantity", FIELD, "product", Selection.of("name", FIELD)));

        var api = new Communication.RestApi(new Communication.Db(shop));
        var rest = Communication.orderScreenRest(api, "o1");
        assert rest.screen().get("customer").get("name").asString().equals("Gbenga Ali");
        assert api.requests == 5 && rest.roundTrips() == 2 && api.bytes == 912 : api.bytes;
        assert Communication.size(rest.screen()) == 203 : Communication.size(rest.screen());

        for (boolean batched : new boolean[] {false, true}) {
            var db = new Communication.Db(shop);
            var order = db.find("orders", List.of("o1"));
            var screen = Communication.execute(order, screenQuery, Communication.resolvers(db, batched), "Order").getFirst();
            assert screen.equals(rest.screen()) && Communication.size(screen) == 203 : screen;
            assert db.queries == (batched ? 3 : 5) : db.queries;
        }

        for (boolean batched : new boolean[] {false, true}) {
            var db = new Communication.Db(shop);
            var orders = db.find("orders", IntStream.rangeClosed(1, 10).mapToObj(i -> "o" + i).toList());
            var listQuery = Selection.of("id", FIELD, "customer", Selection.of("name", FIELD), "items", Selection.of("product", Selection.of("name", FIELD)));
            var page = Communication.execute(orders, listQuery, Communication.resolvers(db, batched), "Order");
            assert page.size() == 10 && page.getFirst().get("customer").get("name").asString().equals("Gbenga Ali");
            assert db.queries == (batched ? 3 : 41) : db.queries;
        }

        var hex = HexFormat.ofDelimiter(" ");
        assert hex.formatHex(Communication.varint(1)).equals("01");
        assert hex.formatHex(Communication.varint(150)).equals("96 01");
        assert hex.formatHex(Communication.varint(300)).equals("ac 02");
        assert hex.formatHex(Communication.varint(1L << 35)).equals("80 80 80 80 80 01");
        try {
            Communication.varint(-1);
            throw new AssertionError("expected a refusal");
        } catch (IllegalArgumentException expected) {
            // negative
        }
        assert hex.formatHex(Communication.encodeOrderSummary(150, "testing", 1)).equals("08 96 01 12 07 74 65 73 74 69 6e 67 18 01");

        assert Communication.encodeOrderSummary(1, "Gbenga Ali", 8996).length == 17;
        var summary = Communication.JSON.createObjectNode().put("id", 1).put("customer", "Gbenga Ali").put("totalPence", 8996);
        assert Communication.size(summary) == 50;

        var c = Communication.chain(java.util.Collections.nCopies(5, new Communication.Call(0.999, 20)));
        assert String.format(Locale.ROOT, "%.2f", c.availability() * 100).equals("99.50") && c.sequentialMs() == 100;
        assert Communication.chain(List.of(new Communication.Call(1, 30), new Communication.Call(1, 50), new Communication.Call(1, 20))).parallelMs() == 50;
        System.out.println("all communication checks passed");
    }
}
