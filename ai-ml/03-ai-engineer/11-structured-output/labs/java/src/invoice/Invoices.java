package invoice;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.databind.cfg.CoercionAction;
import com.fasterxml.jackson.databind.cfg.CoercionInputShape;
import com.fasterxml.jackson.databind.json.JsonMapper;
import com.fasterxml.jackson.databind.type.LogicalType;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.github.victools.jsonschema.generator.Option;
import com.github.victools.jsonschema.generator.OptionPreset;
import com.github.victools.jsonschema.generator.SchemaGenerator;
import com.github.victools.jsonschema.generator.SchemaGeneratorConfigBuilder;
import com.github.victools.jsonschema.generator.SchemaVersion;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

/** Structured output with records and Jackson: the record is the type, the parsing target and the schema source. */
public final class Invoices {
    private Invoices() {}

    public enum Currency { GBP, USD, EUR, NGN }

    public record LineItem(String description, int amountCents) {}

    public record Invoice(String vendor, String invoiceNumber, Currency currency, LocalDate dueDate,
                          List<LineItem> lineItems, int totalCents) {}

    /**
     * Jackson is lenient by default: 655.5 becomes 655, "450" becomes 450, and a missing int becomes 0.
     * For model output every one of those hides a mistake, so turn them off.
     */
    static final ObjectMapper JSON = JsonMapper.builder()
            .addModule(new JavaTimeModule())                                    // LocalDate from "2026-10-15"
            .propertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE)              // dueDate ↔ "due_date"
            .enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)          // the default, said out loud
            .enable(DeserializationFeature.FAIL_ON_MISSING_CREATOR_PROPERTIES)  // a missing field is an error, not 0
            .enable(DeserializationFeature.FAIL_ON_NULL_CREATOR_PROPERTIES)
            .disable(DeserializationFeature.ACCEPT_FLOAT_AS_INT)                // 655.5 is not a number of cents
            .withCoercionConfig(LogicalType.Integer, c -> c.setCoercion(CoercionInputShape.String, CoercionAction.Fail))
            .withCoercionConfig(LogicalType.Textual, c -> c.setCoercion(CoercionInputShape.Integer, CoercionAction.Fail))
            .build();

    /** The schema for the model, generated from the record (victools). */
    public static JsonNode schema() {
        var config = new SchemaGeneratorConfigBuilder(SchemaVersion.DRAFT_2020_12, OptionPreset.PLAIN_JSON)
                .with(Option.FORBIDDEN_ADDITIONAL_PROPERTIES_BY_DEFAULT)
                .with(Option.FLATTENED_ENUMS);
        config.forFields().withRequiredCheck(field -> true);  // every component of the record is required
        config.forFields().withPropertyNameOverrideResolver(field -> toSnake(field.getName()));
        config.forTypesInGeneral().withStringFormatResolver(scope ->
                scope.getType().getErasedType() == LocalDate.class ? "date" : null);
        return new SchemaGenerator(config.build()).generateSchema(Invoice.class);
    }

    static String toSnake(String camel) {
        return camel.replaceAll("([a-z])([A-Z])", "$1_$2").toLowerCase();
    }

    /** JSON, then shape, then the invariant. Throws with a message a model can act on. */
    public static Invoice parse(String reply) {
        int start = reply.indexOf('{'), end = reply.lastIndexOf('}');
        if (start == -1 || end < start) throw new IllegalArgumentException("no JSON object in the reply");
        Invoice invoice;
        try {
            invoice = JSON.readValue(reply.substring(start, end + 1), Invoice.class);
        } catch (JsonMappingException e) {
            String field = e.getPath().stream().map(r -> r.getFieldName() != null ? "." + r.getFieldName() : "[" + r.getIndex() + "]")
                    .collect(Collectors.joining()).replaceFirst("^\\.", ""); // line_items[0].amount_cents
            throw new IllegalArgumentException((field.isEmpty() ? "" : field + ": ") + e.getOriginalMessage().lines().findFirst().orElse(""));
        } catch (Exception e) {
            throw new IllegalArgumentException("that was not valid JSON (" + e.getMessage().lines().findFirst().orElse("") + ")");
        }
        int sum = invoice.lineItems().stream().mapToInt(LineItem::amountCents).sum();
        if (sum != invoice.totalCents())
            throw new IllegalArgumentException("line items add up to " + sum + " cents but total_cents is " + invoice.totalCents());
        return invoice;
    }

    public record Message(String role, String content) {}

    public record Reply(String text, String finishReason, String refusal) {
        public static Reply of(String text) { return new Reply(text, "stop", null); }
    }

    public record Outcome(Invoice invoice, int attempts, String reason, String detail) {}

    public static Outcome extract(Function<List<Message>, Reply> model, String document, int maxAttempts) {
        List<Message> messages = new ArrayList<>(List.of(
                new Message("system", "Extract the invoice as JSON matching this schema. Amounts are integers in cents. "
                        + "Reply with only the JSON object.\n" + schema()),
                new Message("user", document)));
        String problem = "";
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            Reply reply = model.apply(List.copyOf(messages));
            if (reply.refusal() != null) return new Outcome(null, attempt, "refused", reply.refusal());
            if (reply.finishReason().equals("length")) {
                problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object";
            } else {
                try {
                    return new Outcome(parse(reply.text()), attempt, "ok", "");
                } catch (IllegalArgumentException e) {
                    problem = e.getMessage();
                }
            }
            messages.add(new Message("assistant", reply.text()));
            messages.add(new Message("user", "Your reply had these problems: " + problem + ". Return the corrected JSON object only."));
        }
        return new Outcome(null, maxAttempts, "invalid", problem);
    }
}
