// Checks.
using System.Text.Json.Nodes;

const string Good = """
    {"vendor":"Brightline Studio Ltd","invoice_number":"INV-2041","currency":"GBP","due_date":"2026-10-15",
     "line_items":[{"description":"Logo design","amount_cents":45000},{"description":"Two revisions","amount_cents":12000},
                   {"description":"Brand guide PDF","amount_cents":8550}],
     "total_cents":65550}
    """;

// The good invoice with one field changed or added (or removed, when value is null).
static string With(string field, JsonNode? value)
{
    var invoice = JsonNode.Parse(Good)!.AsObject();
    if (value is null) invoice.Remove(field);
    else invoice[field] = value;
    return invoice.ToJsonString();
}
static string Problem(string reply)
{
    try { Invoices.Parse(reply); return "parsed"; }
    catch (FormatException e) { return e.Message; }
}
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

var schema = Invoices.Schema();
Check(schema["additionalProperties"]!.GetValue<bool>() == false, schema);
Check(schema["required"]!.AsArray().Count == 6, schema);
Check(schema["properties"]!["currency"]!["enum"]!.AsArray().Count == 4, schema);
Check((string?)schema["properties"]!["due_date"]!["format"] == "date", schema);

var invoice = Invoices.Parse("Sure! Here it is:\n```json\n" + Good + "\n```");
Check(invoice.DueDate == new DateOnly(2026, 10, 15) && invoice.Currency == Currency.GBP, invoice);
Check(invoice.LineItems[2].AmountCents == 8550, invoice);

Check(Problem(With("total_cents", 655.5)) == "total_cents: wrong type or value for this field (check the schema)", "float");
Check(Problem(With("line_items", JsonNode.Parse("""[{"description":"Logo","amount_cents":"450"}]""")))
      == "line_items[0].amount_cents: wrong type or value for this field (check the schema)", "string number");
Check(Problem(With("vendor", 1)).StartsWith("vendor: wrong type"), "int for string");
Check(Problem(With("currency", "pounds")).StartsWith("currency: wrong type"), "enum");
Check(Problem(With("due_date", "15 October 2026")).StartsWith("due_date: wrong type"), "date");
Check(Problem(With("invoice_number", null)) == "JSON deserialization for type 'Invoice' was missing required properties including: 'invoice_number'.", "missing");
Check(Problem(With("notes", "thanks")).StartsWith("notes: The JSON property 'notes' could not be mapped"), "extra");
Check(Problem(With("total_cents", 65500)) == "line items add up to 65550 cents but total_cents is 65500", "sum");
Check(Problem("I can't find an invoice.") == "no JSON object in the reply", "no JSON");

List<List<Message>> seen = [];
Func<IReadOnlyList<Message>, Reply> Scripted(params Reply[] replies) => messages =>
{
    seen.Add([.. messages]);
    return replies[seen.Count - 1];
};

var retried = Extractor.Extract(Scripted(new Reply(With("total_cents", 65500)), new Reply(Good)), "…");
Check(retried is { Reason: "ok", Attempts: 2 } && seen[1][^1].Content.Contains("total_cents is 65500"), retried);

seen.Clear();
var truncated = Extractor.Extract(Scripted(new Reply("""{"vendor": "Bright""", "length"), new Reply(Good)), "…");
Check(truncated.Reason == "ok" && seen[1][^1].Content.Contains("cut off"), truncated);

seen.Clear();
var refused = Extractor.Extract(Scripted(new Reply("", Refusal: "I can't help with that.")), "…");
Check(refused is { Reason: "refused", Attempts: 1 } && seen.Count == 1, refused);

seen.Clear();
var capped = Extractor.Extract(Scripted(new Reply("nope"), new Reply("still no"), new Reply(With("vendor", 1))), "…");
Check(capped is { Reason: "invalid", Attempts: 3 } && capped.Detail.StartsWith("vendor: wrong type"), capped);

Console.WriteLine("ok: schema, parsing, strictness and the retry loop all checked");
