package invoice;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import invoice.Invoices.*;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

/** Checks, run with `java -ea`. */
public final class InvoicesCheck {
    static final String GOOD = """
            {"vendor":"Brightline Studio Ltd","invoice_number":"INV-2041","currency":"GBP","due_date":"2026-10-15",
             "line_items":[{"description":"Logo design","amount_cents":45000},{"description":"Two revisions","amount_cents":12000},
                           {"description":"Brand guide PDF","amount_cents":8550}],
             "total_cents":65550}""";

    /** The good invoice with one field changed or added. */
    static String with(String field, Object value) {
        try {
            ObjectNode node = (ObjectNode) Invoices.JSON.readTree(GOOD);
            node.set(field, Invoices.JSON.valueToTree(value));
            return node.toString();
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    static String problem(String reply) {
        try {
            Invoices.parse(reply);
            return "parsed";
        } catch (IllegalArgumentException e) {
            return e.getMessage();
        }
    }

    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static Function<List<Message>, Reply> scripted(List<List<Message>> seen, Reply... replies) {
        return messages -> {
            seen.add(messages);
            return replies[seen.size() - 1];
        };
    }

    public static void main(String[] args) {
        JsonNode schema = Invoices.schema();
        check(!schema.get("additionalProperties").asBoolean(true), schema);
        check(schema.get("required").size() == 6, schema);
        check(schema.at("/properties/currency/enum").size() == 4, schema);
        check(schema.at("/properties/due_date/format").asText().equals("date"), schema);

        Invoice invoice = Invoices.parse("Sure! Here it is:\n```json\n" + GOOD + "\n```");
        check(invoice.dueDate().equals(LocalDate.of(2026, 10, 15)), invoice);
        check(invoice.currency() == Currency.GBP && invoice.lineItems().get(2).amountCents() == 8550, invoice);

        // each lenient default, switched off: without these, every one of these replies would parse
        check(problem(with("total_cents", 655.5)).startsWith("total_cents: Cannot coerce Floating-point value (655.5)"), "float");
        check(problem(with("line_items", List.of(Map.of("description", "Logo", "amount_cents", "450"))))
                .startsWith("line_items[0].amount_cents: Cannot coerce String value (\"450\")"), "string number");
        ObjectNode missing = (ObjectNode) Invoices.JSON.valueToTree(Invoices.parse(GOOD));
        missing.remove("invoice_number");
        check(problem(missing.toString()).startsWith("invoice_number: Missing creator property"), "missing");
        check(problem(with("notes", "thanks")).contains("Unrecognized field \"notes\""), problem(with("notes", "thanks")));
        check(problem(with("currency", "pounds")).startsWith("currency: Cannot deserialize value of type `invoice.Invoices$Currency` from String \"pounds\""), "enum");
        check(problem(with("due_date", "15 October 2026")).startsWith("due_date: Cannot deserialize value of type `java.time.LocalDate`"), "date");
        check(problem(with("total_cents", 65500)).equals("line items add up to 65550 cents but total_cents is 65500"), "sum");
        check(problem("I can't find an invoice.").equals("no JSON object in the reply"), "no JSON");

        List<List<Message>> seen = new ArrayList<>();
        Outcome retried = Invoices.extract(scripted(seen, Reply.of(with("total_cents", 65500)), Reply.of(GOOD)), "…", 3);
        check(retried.reason().equals("ok") && retried.attempts() == 2, retried);
        check(seen.get(1).getLast().content().contains("total_cents is 65500"), seen.get(1).getLast());

        seen.clear();
        Outcome truncated = Invoices.extract(scripted(seen, new Reply("{\"vendor\": \"Bright", "length", null), Reply.of(GOOD)), "…", 3);
        check(truncated.reason().equals("ok") && seen.get(1).getLast().content().contains("cut off"), truncated);

        seen.clear();
        Outcome refused = Invoices.extract(scripted(seen, new Reply("", "stop", "I can't help with that.")), "…", 3);
        check(refused.reason().equals("refused") && seen.size() == 1, refused);

        seen.clear();
        Outcome capped = Invoices.extract(scripted(seen, Reply.of("nope"), Reply.of("still no"), Reply.of(with("vendor", 1))), "…", 3);
        check(capped.reason().equals("invalid") && capped.attempts() == 3 && capped.detail().startsWith("vendor: Cannot coerce Integer value (1)"), capped);

        System.out.println("ok: schema, parsing, strictness and the retry loop all checked");
    }
}
