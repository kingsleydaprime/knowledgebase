// Structured output with records and System.Text.Json: the record is the type, the parsing target
// and (through JsonSchemaExporter, built in since .NET 9) the schema sent to the model.
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Schema;
using System.Text.Json.Serialization;
using System.Text.Json.Serialization.Metadata;

public enum Currency { GBP, USD, EUR, NGN }

public record LineItem(string Description, int AmountCents);

public record Invoice(string Vendor, string InvoiceNumber, Currency Currency, DateOnly DueDate,
    List<LineItem> LineItems, int TotalCents);

public static class Invoices
{
    /// <summary>System.Text.Json already refuses "450" for an int and 655.5 for an int. These make
    /// missing fields, nulls and extra keys errors too.</summary>
    public static readonly JsonSerializerOptions Json = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,             // DueDate ↔ "due_date"
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,       // extra keys are errors
        RespectRequiredConstructorParameters = true,                       // a missing field is an error, not 0
        RespectNullableAnnotations = true,                                 // "vendor": null is an error for string
        Converters = { new JsonStringEnumConverter(allowIntegerValues: false) },
        TypeInfoResolver = new DefaultJsonTypeInfoResolver(),             // reflection; the schema exporter needs it named
    };

    /// <summary>The schema for the model, generated from the record.</summary>
    public static JsonNode Schema() =>
        JsonSchemaExporter.GetJsonSchemaAsNode(Json, typeof(Invoice),
            new JsonSchemaExporterOptions { TreatNullObliviousAsNonNullable = true });

    /// <summary>JSON, then shape, then the invariant. Throws with a message a model can act on.</summary>
    public static Invoice Parse(string reply)
    {
        int start = reply.IndexOf('{'), end = reply.LastIndexOf('}');
        if (start == -1 || end < start) throw new FormatException("no JSON object in the reply");
        Invoice invoice;
        try
        {
            invoice = JsonSerializer.Deserialize<Invoice>(reply[start..(end + 1)], Json)!;
        }
        catch (JsonException e)
        {
            // e.Path says exactly where ("$.line_items[0].amount_cents"); the message is often just
            // "could not be converted", so say what that means in words a model can act on.
            var where = e.Path?.TrimStart('$', '.');
            var why = e.Message.StartsWith("The JSON value could not be converted")
                ? "wrong type or value for this field (check the schema)"
                : e.Message.Split(" Path:")[0];
            throw new FormatException(string.IsNullOrEmpty(where) ? why : $"{where}: {why}");
        }
        var sum = invoice.LineItems.Sum(item => item.AmountCents);
        if (sum != invoice.TotalCents)
            throw new FormatException($"line items add up to {sum} cents but total_cents is {invoice.TotalCents}");
        return invoice;
    }
}

public record Message(string Role, string Content);

public record Reply(string Text, string FinishReason = "stop", string? Refusal = null);

public record Outcome(Invoice? Invoice, int Attempts, string Reason, string Detail = "");

public static class Extractor
{
    public static Outcome Extract(Func<IReadOnlyList<Message>, Reply> model, string document, int maxAttempts = 3)
    {
        List<Message> messages =
        [
            new("system", "Extract the invoice as JSON matching this schema. Amounts are integers in cents. " +
                          "Reply with only the JSON object.\n" + Invoices.Schema().ToJsonString()),
            new("user", document),
        ];
        var problem = "";
        for (var attempt = 1; attempt <= maxAttempts; attempt++)
        {
            var reply = model([.. messages]);
            if (reply.Refusal is { } refusal) return new(null, attempt, "refused", refusal); // retrying won't help
            if (reply.FinishReason == "length")
                problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object";
            else
            {
                try { return new(Invoices.Parse(reply.Text), attempt, "ok"); }
                catch (FormatException e) { problem = e.Message; }
            }
            messages.Add(new("assistant", reply.Text));
            messages.Add(new("user", $"Your reply had these problems: {problem}. Return the corrected JSON object only."));
        }
        return new(null, maxAttempts, "invalid", problem);
    }
}
