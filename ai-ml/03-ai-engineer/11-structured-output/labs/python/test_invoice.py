import json
import unittest
from datetime import date

from invoice import Invoice, Reply, extract_invoice, json_object_text

GOOD = {
    "vendor": "Brightline Studio Ltd", "invoice_number": "INV-2041", "currency": "GBP", "due_date": "2026-10-15",
    "line_items": [{"description": "Logo design", "amount_cents": 45000},
                   {"description": "Two revisions", "amount_cents": 12000},
                   {"description": "Brand guide PDF", "amount_cents": 8550}],
    "total_cents": 65550,
}


def scripted(*replies: Reply):
    seen = []

    def model(messages):
        seen.append([dict(m) for m in messages])
        return replies[len(seen) - 1]

    return model, seen


class InvoiceTests(unittest.TestCase):
    def test_one_class_gives_the_schema_for_the_model(self):
        schema = Invoice.model_json_schema()
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(schema["properties"]["currency"]["enum"], ["GBP", "USD", "EUR", "NGN"])
        self.assertEqual(schema["properties"]["due_date"]["format"], "date")
        self.assertEqual(set(schema["required"]), set(GOOD))

    def test_and_the_parser_and_type_for_your_code(self):
        invoice = Invoice.model_validate_json(json.dumps(GOOD))
        self.assertEqual(invoice.due_date, date(2026, 10, 15))  # a real date, not a string
        self.assertEqual(invoice.line_items[2].amount_cents, 8550)

    def test_shape_errors_are_specific(self):
        bad = {**GOOD, "currency": "pounds", "total_cents": 655.5, "notes": "thanks"}
        model, _ = scripted(Reply(json.dumps(bad)), Reply("nope"), Reply("nope"))
        outcome = extract_invoice(model, "…", max_attempts=1)
        self.assertEqual(outcome.reason, "invalid")
        self.assertIn("currency: Input should be 'GBP', 'USD', 'EUR' or 'NGN'", outcome.detail)
        self.assertIn("total_cents: Input should be a valid integer", outcome.detail)
        self.assertIn("notes: Extra inputs are not permitted", outcome.detail)

    def test_the_object_is_dug_out_of_chatter_and_bad_json_is_reported(self):
        self.assertEqual(json_object_text('Sure!\n```json\n{"a": 1}\n```'), '{"a": 1}')
        model, _ = scripted(Reply("I can't find an invoice."), Reply('{"vendor": "x",}'))
        self.assertEqual(extract_invoice(model, "…", max_attempts=1).detail, "no JSON object in the reply")
        self.assertIn("invoice: Invalid JSON", extract_invoice(model, "…", max_attempts=1).detail)

    def test_a_wrong_total_is_retried_with_the_error_fed_back(self):
        model, seen = scripted(Reply(json.dumps({**GOOD, "total_cents": 65500})), Reply(json.dumps(GOOD)))
        outcome = extract_invoice(model, "…")
        self.assertEqual((outcome.reason, outcome.attempts), ("ok", 2))
        self.assertIn("line items add up to 65550 cents but total_cents is 65500", seen[1][-1]["content"])

    def test_truncation_is_retried_not_parsed(self):
        model, seen = scripted(Reply('{"vendor": "Bright', "length"), Reply(json.dumps(GOOD)))
        self.assertEqual(extract_invoice(model, "…").reason, "ok")
        self.assertIn("cut off", seen[1][-1]["content"])

    def test_a_refusal_stops_immediately(self):
        model, seen = scripted(Reply("", refusal="I can't help with that."))
        outcome = extract_invoice(model, "…")
        self.assertEqual((outcome.reason, outcome.attempts, len(seen)), ("refused", 1, 1))

    def test_retries_are_capped(self):
        model, _ = scripted(Reply("nope"), Reply("still no"), Reply('{"vendor": 1}'))
        outcome = extract_invoice(model, "…")
        self.assertEqual((outcome.reason, outcome.attempts), ("invalid", 3))
        self.assertIn("vendor: Input should be a valid string", outcome.detail)


if __name__ == "__main__":
    unittest.main()
