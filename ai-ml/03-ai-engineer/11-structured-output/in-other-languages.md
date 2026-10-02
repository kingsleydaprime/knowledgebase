# Structured Output in Other Languages

> **[Intermediate]** · A companion to [[ai-ml/03-ai-engineer/11-structured-output/index|structured output]], which writes the invoice schema and validator by hand in TypeScript. In most languages you don't write them by hand: **one type definition gives you the schema for the model, the parser, the validator and the type your code uses.** This page does that in Python (Pydantic), Go (struct tags), Java (records and Jackson), Rust (serde and schemars) and C# (System.Text.Json), each with the same retry loop. The real difference between them turns out to be **how strict each parser is by default**.

## Before you start

You can already:

- Explain the three checks (JSON, shape, invariant) and the retry loop with feedback → [[ai-ml/03-ai-engineer/11-structured-output/index|the main lesson]].
- Read code in at least one language below.

After this lesson you will be able to:

1. Generate a JSON Schema for the model from a type in your language.
2. Configure your language's JSON parser to reject everything a model can get wrong: extra keys, missing fields, wrong types.
3. Say which defaults in your language would quietly accept a wrong reply, and switch them off.

## The kid version

Imagine one stencil that does three jobs. Hold it up, and it shows the model the shape to draw. Lay it over the model's drawing, and it shows anything outside the lines. And your own code can use the stencil to know exactly where everything is. Each language here has its own stencil kit. Some kits are fussy out of the box and complain about every smudge. Others are relaxed, and quietly "fix" a smudge for you — they'll round 655.5 down to 655 without a word. With model output, a relaxed kit is dangerous.

**Where the analogy stops working.** A stencil only checks shapes. None of these kits can check that the line items add up to the total. That invariant is still yours to write, in every language.

## 1. The tools, by ecosystem

| Language | One type → schema, parser, validator | Strict by default? |
|---|---|---|
| TypeScript | **Zod** (`z.object`, then `z.toJSONSchema`), as the AI SDK uses | yes |
| Python | **Pydantic** `BaseModel` (`model_json_schema`, `model_validate_json`); the `openai` and `instructor` libraries take Pydantic classes directly | no: turns `"450"` into `450` unless `strict=True` |
| Go | `encoding/json` + **struct tags**; `go-playground/validator` for rules; `invopop/jsonschema` for the schema | no: ignores extra keys and fills missing ones with zero |
| Java | **records** + **Jackson**; `victools/jsonschema-generator` for the schema; Spring AI's `BeanOutputConverter` wraps both | no: rounds `655.5` to `655`, accepts `"450"`, fills a missing `int` with `0` |
| Rust | **serde** + **schemars** | **yes**: only extra keys need `deny_unknown_fields` |
| C# | **System.Text.Json** + `JsonSchemaExporter` (built in since .NET 9) | partly: rejects wrong types; allows missing and extra keys unless told otherwise |
| C, C++ | no standard JSON library; constrained decoding itself lives here, in **llama.cpp's grammars** | — |

That last column is the point of this page. The model will eventually send `655.5`, `"450"`, a missing field or an extra one. A lenient parser turns each of those into a plausible, wrong value, which no later check can catch. **Make the parser strict, then check the invariant.**

## 2. What each lab switches on

| Mistake in the reply | Python | Go | Java | Rust | C# |
|---|---|---|---|---|---|
| Extra key `"notes"` | `extra="forbid"` | `DisallowUnknownFields()` | on by default | `deny_unknown_fields` | `UnmappedMemberHandling.Disallow` |
| Missing `invoice_number` | error by default | **becomes `""`**; validator's `required` catches it | `FAIL_ON_MISSING_CREATOR_PROPERTIES` | error by default | `RespectRequiredConstructorParameters` |
| `"total_cents": 655.5` | `strict=True` | error by default | **disable `ACCEPT_FLOAT_AS_INT`** | error by default | error by default |
| `"amount_cents": "450"` | `strict=True` | error by default | a `CoercionConfig` | error by default | error by default |
| `"currency": "pounds"` | `Literal[...]` | validator `oneof` | a Java `enum` | a Rust `enum` | an enum + `JsonStringEnumConverter` |
| `"due_date": "15 October 2026"` | `date` | a `Date` type with `time.DateOnly` | `LocalDate` + `JavaTimeModule` | chrono's `NaiveDate` | `DateOnly` |

The **Go** row has the subtlest trap. A key the model leaves out isn't an error at all: the struct field just keeps its zero value. `""` and `0` are often valid-looking values, so Go needs a separate validator to notice.

## Terms used in this lesson

1. **Coercion**: This is a parser converting a value of the wrong type into the right one, such as `"450"` into `450`. It's convenient for forms and dangerous for model output.
2. **Strict mode**: This is a parser setting that turns coercion off, so a value of the wrong type is an error.
3. **Struct tag**: In Go, this is the text in backquotes after a field, such as `` `json:"vendor" validate:"required"` ``, that libraries read to learn how to handle the field.
4. **Zero value**: In Go, this is the value a variable has before anything is assigned: `""` for strings, `0` for numbers.
5. **Record**: In Java and C#, this is a compact class that just holds data, with a constructor, equality and printing generated for you.
6. **Derive macro**: In Rust, this is `#[derive(...)]`, which generates code for a type, such as serde's parser or schemars' schema.
7. **GBNF (GGML Backus–Naur form)**: The letters stand for those words. GGML is the tensor library underneath llama.cpp; the letters are its author Georgi Gerganov's initials plus ML, for machine learning. GBNF is llama.cpp's grammar format: it lists the token sequences that are allowed, and decoding is restricted to them.

## 3. Python — Pydantic

One class. `extra="forbid"` becomes `"additionalProperties": false` in the schema, and `strict=True` turns off coercion. The invariant is a `model_validator`, so a wrong total fails exactly like a wrong type.

```python
"""Structured output with Pydantic: one class is the schema sent to the model, the parser, the
validator and the type your code uses."""
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class LineItem(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)  # strict: 655.5 is not an int, "450" is not an int
    description: str
    amount_cents: int


class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)  # extra="forbid" → "additionalProperties": false
    vendor: str
    invoice_number: str
    currency: Literal["GBP", "USD", "EUR", "NGN"]           # an enum in the schema
    due_date: date = Field(json_schema_extra={"description": "ISO 8601 date, YYYY-MM-DD"})
    line_items: list[LineItem]
    total_cents: int

    @model_validator(mode="after")
    def items_add_up(self) -> "Invoice":
        """The invariant no schema can express."""
        total = sum(item.amount_cents for item in self.line_items)
        if total != self.total_cents:
            raise ValueError(f"line items add up to {total} cents but total_cents is {self.total_cents}")
        return self


def json_object_text(text: str) -> str:
    """Models asked for JSON often wrap it in chatter or a fence. Take the outermost {...}."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("no JSON object in the reply")
    return text[start:end + 1]


def describe(error: ValidationError) -> str:
    """Pydantic's errors, as short sentences a model can act on."""
    return "; ".join(f"{'.'.join(map(str, e['loc'])) or 'invoice'}: {e['msg']}" for e in error.errors())


@dataclass
class Reply:
    text: str
    finish_reason: Literal["stop", "length", "other"] = "stop"
    refusal: str | None = None


@dataclass
class Outcome:
    invoice: Invoice | None
    attempts: int
    reason: Literal["ok", "refused", "invalid"]
    detail: str = ""


SYSTEM = ("Extract the invoice as JSON matching this schema. Amounts are integers in cents. "
          "Reply with only the JSON object.\n" + json.dumps(Invoice.model_json_schema()))


def extract_invoice(model: Callable[[list[dict]], Reply], document: str, max_attempts: int = 3) -> Outcome:
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": document}]
    problem = ""
    for attempt in range(1, max_attempts + 1):
        reply = model(messages)
        if reply.refusal:  # retrying won't change a refusal: check it before parsing
            return Outcome(None, attempt, "refused", reply.refusal)
        if reply.finish_reason == "length":
            problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object"
        else:
            try:
                # validate the JSON text directly: in strict mode, "2026-10-15" is a valid date in JSON
                # (that's how JSON spells a date) but not as a Python string. Bad JSON is a ValidationError too.
                return Outcome(Invoice.model_validate_json(json_object_text(reply.text)), attempt, "ok")
            except ValidationError as e:
                problem = describe(e)
            except ValueError as e:
                problem = str(e)
        # feed back exactly what was wrong; a bare "try again" tends to repeat the mistake
        messages += [{"role": "assistant", "content": reply.text},
                     {"role": "user", "content": f"Your reply had these problems: {problem}. Return the corrected JSON object only."}]
    return Outcome(None, max_attempts, "invalid", problem)
```

```python
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
```

**One surprise worth knowing.** The first version passed a Python dict to `model_validate`, and strict mode rejected `"2026-10-15"` as a date. That's correct: in strict mode a Python *string* isn't a date. But in JSON, a string is how dates are written, so `model_validate_json` on the raw text accepts it. Validate the JSON text, not a dict you've already parsed. As a bonus, invalid JSON then becomes a normal `ValidationError` too.

## 4. Go — struct tags, a validator and a schema reflector

`encoding/json` alone is too forgiving: extra keys are ignored unless you call `DisallowUnknownFields`, and missing keys silently become zero values. So `go-playground/validator` checks the rules in the `validate` tags, and `invopop/jsonschema` builds the schema from the same struct. The validator is set to report fields by their JSON names, because those are the only names the model knows.

```go
// Package invoice: structured output in Go. One struct is the type, the JSON decoder's target,
// the validator's rules (go-playground/validator) and the schema sent to the model (invopop/jsonschema).
package invoice

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"reflect"
	"strings"
	"time"

	"github.com/go-playground/validator/v10"
	"github.com/invopop/jsonschema"
)

type LineItem struct {
	Description string `json:"description" validate:"required"`
	AmountCents int    `json:"amount_cents" validate:"required"`
}

type Invoice struct {
	Vendor        string     `json:"vendor" validate:"required"`
	InvoiceNumber string     `json:"invoice_number" validate:"required"`
	Currency      string     `json:"currency" validate:"oneof=GBP USD EUR NGN" jsonschema:"enum=GBP,enum=USD,enum=EUR,enum=NGN"`
	DueDate       Date       `json:"due_date" validate:"required"`
	LineItems     []LineItem `json:"line_items" validate:"required,min=1,dive"`
	TotalCents    int        `json:"total_cents" validate:"required"`
}

// Date is a calendar date written as "2026-10-15". time.Time alone expects a full timestamp.
type Date struct{ time.Time }

func (d *Date) UnmarshalJSON(b []byte) error {
	var s string
	if err := json.Unmarshal(b, &s); err != nil {
		return err
	}
	t, err := time.Parse(time.DateOnly, s)
	if err != nil {
		return fmt.Errorf("must be a date like 2026-10-15")
	}
	d.Time = t
	return nil
}

func (Date) JSONSchema() *jsonschema.Schema {
	return &jsonschema.Schema{Type: "string", Format: "date", Description: "ISO 8601 date, YYYY-MM-DD"}
}

// Schema is what goes to the model. invopop sets "additionalProperties": false and lists every
// field without omitempty as required.
func Schema() *jsonschema.Schema {
	return (&jsonschema.Reflector{ExpandedStruct: true}).Reflect(&Invoice{})
}

var validate = func() *validator.Validate {
	v := validator.New(validator.WithRequiredStructEnabled())
	// report fields by their JSON names, which are the only names the model knows
	v.RegisterTagNameFunc(func(f reflect.StructField) string { return strings.Split(f.Tag.Get("json"), ",")[0] })
	return v
}()

// Parse turns a model's reply into a checked Invoice: JSON, then shape, then the invariant.
func Parse(reply string) (Invoice, error) {
	start, end := strings.Index(reply, "{"), strings.LastIndex(reply, "}")
	if start == -1 || end < start {
		return Invoice{}, errors.New("no JSON object in the reply")
	}
	decoder := json.NewDecoder(bytes.NewReader([]byte(reply[start : end+1])))
	decoder.DisallowUnknownFields() // without this, extra keys are silently ignored
	var inv Invoice
	if err := decoder.Decode(&inv); err != nil {
		return Invoice{}, fmt.Errorf("invalid JSON for the schema: %w", err)
	}
	// A missing field decodes to its zero value without complaint; the validator catches that.
	if err := validate.Struct(inv); err != nil {
		return Invoice{}, describe(err)
	}
	sum := 0
	for _, item := range inv.LineItems {
		sum += item.AmountCents
	}
	if sum != inv.TotalCents {
		return Invoice{}, fmt.Errorf("line items add up to %d cents but total_cents is %d", sum, inv.TotalCents)
	}
	return inv, nil
}

// describe turns validator errors into short sentences a model can act on.
func describe(err error) error {
	var fieldErrors validator.ValidationErrors
	if !errors.As(err, &fieldErrors) {
		return err
	}
	var problems []string
	for _, f := range fieldErrors {
		switch f.Tag() {
		case "oneof":
			problems = append(problems, fmt.Sprintf("%s must be one of %s", f.Field(), f.Param()))
		default:
			problems = append(problems, fmt.Sprintf("%s is missing", f.Field()))
		}
	}
	return errors.New(strings.Join(problems, "; "))
}

type Message struct{ Role, Content string }

type Reply struct {
	Text         string
	FinishReason string // "stop", "length" or "other"
	Refusal      string
}

type Outcome struct {
	Invoice  Invoice
	Attempts int
	Reason   string // "ok", "refused" or "invalid"
	Detail   string
}

// Extract calls the model, checks the reply, and retries with the specific problem fed back.
func Extract(model func([]Message) Reply, document string, maxAttempts int) Outcome {
	schema, _ := json.Marshal(Schema())
	messages := []Message{
		{"system", "Extract the invoice as JSON matching this schema. Amounts are integers in cents. Reply with only the JSON object.\n" + string(schema)},
		{"user", document},
	}
	var problem string
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		reply := model(messages)
		if reply.Refusal != "" { // retrying won't change a refusal
			return Outcome{Attempts: attempt, Reason: "refused", Detail: reply.Refusal}
		}
		if reply.FinishReason == "length" {
			problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object"
		} else if inv, err := Parse(reply.Text); err == nil {
			return Outcome{Invoice: inv, Attempts: attempt, Reason: "ok"}
		} else {
			problem = err.Error()
		}
		messages = append(messages, Message{"assistant", reply.Text},
			Message{"user", "Your reply had these problems: " + problem + ". Return the corrected JSON object only."})
	}
	return Outcome{Attempts: maxAttempts, Reason: "invalid", Detail: problem}
}
```

```go
package invoice

import (
	"encoding/json"
	"strings"
	"testing"
)

const good = `{"vendor":"Brightline Studio Ltd","invoice_number":"INV-2041","currency":"GBP","due_date":"2026-10-15",
"line_items":[{"description":"Logo design","amount_cents":45000},{"description":"Two revisions","amount_cents":12000},
{"description":"Brand guide PDF","amount_cents":8550}],"total_cents":65550}`

func TestOneStructGivesTheSchemaForTheModel(t *testing.T) {
	var schema map[string]any
	b, _ := json.Marshal(Schema())
	json.Unmarshal(b, &schema)
	props := schema["properties"].(map[string]any)
	if schema["additionalProperties"] != false || len(schema["required"].([]any)) != 6 ||
		len(props["currency"].(map[string]any)["enum"].([]any)) != 4 {
		t.Errorf("schema: %s", b)
	}
}

func TestAndTheTypedValueForYourCode(t *testing.T) {
	inv, err := Parse("Sure! Here it is:\n```json\n" + good + "\n```")
	if err != nil {
		t.Fatal(err)
	}
	if inv.DueDate.Format("2 January 2006") != "15 October 2026" || inv.LineItems[2].AmountCents != 8550 {
		t.Errorf("got %+v", inv)
	}
}

// with returns the good invoice with one field changed (or added).
func with(field string, value any) string {
	var inv map[string]any
	json.Unmarshal([]byte(good), &inv)
	inv[field] = value
	b, _ := json.Marshal(inv)
	return string(b)
}

func TestEachKindOfProblemIsReportedInTheModelsTerms(t *testing.T) {
	for _, c := range []struct{ reply, want string }{
		{with("currency", "pounds"), "currency must be one of GBP USD EUR NGN"},
		{with("invoice_number", ""), "invoice_number is missing"}, // a missing key decodes to "" silently; the validator notices
		{with("due_date", "15 October 2026"), "must be a date like 2026-10-15"},
		{with("total_cents", 655.5), "cannot unmarshal number 655.5"},
		{with("notes", "thanks"), `unknown field "notes"`},
		{with("total_cents", 65500), "line items add up to 65550 cents but total_cents is 65500"},
	} {
		if _, err := Parse(c.reply); err == nil || !strings.Contains(err.Error(), c.want) {
			t.Errorf("got %v, want %q", err, c.want)
		}
	}
}

func scripted(replies ...Reply) (func([]Message) Reply, *[][]Message) {
	var seen [][]Message
	return func(m []Message) Reply {
		seen = append(seen, append([]Message(nil), m...))
		return replies[len(seen)-1]
	}, &seen
}

func TestAWrongTotalIsRetriedWithTheErrorFedBack(t *testing.T) {
	model, seen := scripted(Reply{Text: with("total_cents", 65500)}, Reply{Text: good})
	out := Extract(model, "…", 3)
	last := (*seen)[1][len((*seen)[1])-1].Content
	if out.Reason != "ok" || out.Attempts != 2 || !strings.Contains(last, "total_cents is 65500") {
		t.Errorf("got %+v; feedback %q", out, last)
	}
}

func TestTruncationIsRetriedRefusalStopsAndRetriesAreCapped(t *testing.T) {
	model, seen := scripted(Reply{Text: `{"vendor": "Bright`, FinishReason: "length"}, Reply{Text: good})
	if out := Extract(model, "…", 3); out.Reason != "ok" || !strings.Contains((*seen)[1][3].Content, "cut off") {
		t.Errorf("truncation: %+v", out)
	}
	model, seen = scripted(Reply{Refusal: "I can't help with that."})
	if out := Extract(model, "…", 3); out.Reason != "refused" || len(*seen) != 1 {
		t.Errorf("refusal: %+v", out)
	}
	model, _ = scripted(Reply{Text: "nope"}, Reply{Text: "still no"}, Reply{Text: `{"vendor": 1}`})
	if out := Extract(model, "…", 3); out.Reason != "invalid" || out.Attempts != 3 || !strings.Contains(out.Detail, "cannot unmarshal number") {
		t.Errorf("cap: %+v", out)
	}
}
```

## 5. Java — records and a stricter Jackson

Jackson's defaults suit hand-written JSON from people. For model output, four of them hide mistakes: `655.5` is rounded to `655`, `"450"` is turned into `450`, a missing `int` becomes `0`, and a missing object becomes `null`. The `JsonMapper` builder switches each one off. The schema comes from victools' generator, which reads the record. `check.sh` downloads the jars from Maven Central.

```java
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
```

```java
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
```

## 6. Rust — serde and schemars

Serde is strict without being asked: wrong types, unknown enum variants and missing fields are all errors. Only extra keys need `#[serde(deny_unknown_fields)]`, and schemars turns that into `"additionalProperties": false`. Its error messages are already in words a model can act on, such as ``unknown variant `pounds`, expected one of `GBP`, `USD`, `EUR`, `NGN` ``. Doc comments become schema descriptions.

```rust
//! Structured output with serde and schemars: one struct is the type, the parsing target and the
//! schema sent to the model. Serde is strict by default: wrong types and missing fields are errors.

use chrono::NaiveDate;
use schemars::{JsonSchema, schema_for};
use serde::{Deserialize, Serialize};

#[derive(Debug, PartialEq, Serialize, Deserialize, JsonSchema)]
pub enum Currency {
    GBP,
    USD,
    EUR,
    NGN,
}

#[derive(Debug, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)] // → "additionalProperties": false, and an error on extra keys
pub struct LineItem {
    pub description: String,
    pub amount_cents: i64,
}

#[derive(Debug, PartialEq, Serialize, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct Invoice {
    pub vendor: String,
    pub invoice_number: String,
    pub currency: Currency,
    /// ISO 8601 date, YYYY-MM-DD
    pub due_date: NaiveDate,
    pub line_items: Vec<LineItem>,
    pub total_cents: i64,
}

/// The schema for the model, generated from the struct. Doc comments become descriptions.
pub fn schema() -> serde_json::Value {
    serde_json::to_value(schema_for!(Invoice)).expect("a schema is always valid JSON")
}

/// JSON, then shape, then the invariant. The error is a message a model can act on.
pub fn parse(reply: &str) -> Result<Invoice, String> {
    let (Some(start), Some(end)) = (reply.find('{'), reply.rfind('}')) else {
        return Err("no JSON object in the reply".into());
    };
    if end < start {
        return Err("no JSON object in the reply".into());
    }
    // serde_json's messages name the problem and where: "invalid type: floating point `655.5`,
    // expected i64 at line 1 column 25"
    let invoice: Invoice = serde_json::from_str(&reply[start..=end]).map_err(|e| e.to_string())?;
    let sum: i64 = invoice
        .line_items
        .iter()
        .map(|item| item.amount_cents)
        .sum();
    if sum != invoice.total_cents {
        return Err(format!(
            "line items add up to {sum} cents but total_cents is {}",
            invoice.total_cents
        ));
    }
    Ok(invoice)
}

#[derive(Clone, Debug)]
pub struct Message {
    pub role: &'static str,
    pub content: String,
}

pub struct Reply {
    pub text: String,
    pub finish_reason: &'static str, // "stop", "length" or "other"
    pub refusal: Option<String>,
}

#[derive(Debug, PartialEq)]
pub enum Outcome {
    Ok { invoice: Invoice, attempts: u32 },
    Refused { detail: String, attempts: u32 },
    Invalid { detail: String, attempts: u32 },
}

pub fn extract(
    mut model: impl FnMut(&[Message]) -> Reply,
    document: &str,
    max_attempts: u32,
) -> Outcome {
    let mut messages = vec![
        Message {
            role: "system",
            content: format!(
                "Extract the invoice as JSON matching this schema. Amounts are integers in cents. \
                 Reply with only the JSON object.\n{}",
                schema()
            ),
        },
        Message {
            role: "user",
            content: document.into(),
        },
    ];
    let mut problem = String::new();
    for attempt in 1..=max_attempts {
        let reply = model(&messages);
        if let Some(detail) = reply.refusal {
            return Outcome::Refused {
                detail,
                attempts: attempt,
            }; // retrying won't change a refusal
        }
        if reply.finish_reason == "length" {
            problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object".into();
        } else {
            match parse(&reply.text) {
                Ok(invoice) => {
                    return Outcome::Ok {
                        invoice,
                        attempts: attempt,
                    };
                }
                Err(e) => problem = e,
            }
        }
        messages.push(Message {
            role: "assistant",
            content: reply.text,
        });
        messages.push(Message {
            role: "user",
            content: format!(
                "Your reply had these problems: {problem}. Return the corrected JSON object only."
            ),
        });
    }
    Outcome::Invalid {
        detail: problem,
        attempts: max_attempts,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::{Value, json};

    fn good() -> Value {
        json!({"vendor": "Brightline Studio Ltd", "invoice_number": "INV-2041", "currency": "GBP",
               "due_date": "2026-10-15",
               "line_items": [{"description": "Logo design", "amount_cents": 45000},
                              {"description": "Two revisions", "amount_cents": 12000},
                              {"description": "Brand guide PDF", "amount_cents": 8550}],
               "total_cents": 65550})
    }

    /// The good invoice with one field changed, added (Some) or removed (None).
    fn with(field: &str, value: Option<Value>) -> String {
        let mut invoice = good();
        match value {
            Some(v) => invoice[field] = v,
            None => {
                invoice.as_object_mut().unwrap().remove(field);
            }
        }
        invoice.to_string()
    }

    fn reply(text: impl Into<String>) -> Reply {
        Reply {
            text: text.into(),
            finish_reason: "stop",
            refusal: None,
        }
    }

    #[test]
    fn one_struct_gives_the_schema_for_the_model() {
        let schema = schema();
        assert_eq!(schema["additionalProperties"], json!(false));
        assert_eq!(schema["required"].as_array().unwrap().len(), 6);
        assert_eq!(schema["properties"]["due_date"]["format"], "date");
        assert_eq!(
            schema["properties"]["due_date"]["description"],
            "ISO 8601 date, YYYY-MM-DD"
        );
    }

    #[test]
    fn and_the_typed_value_for_your_code() {
        let invoice = parse(&format!("Sure! Here it is:\n```json\n{}\n```", good())).unwrap();
        assert_eq!(
            invoice.due_date,
            NaiveDate::from_ymd_opt(2026, 10, 15).unwrap()
        );
        assert_eq!(
            (invoice.currency, invoice.line_items[2].amount_cents),
            (Currency::GBP, 8550)
        );
    }

    #[test]
    fn strict_by_default() {
        let problem = |text: String| parse(&text).unwrap_err();
        assert!(
            problem(with("total_cents", Some(json!(655.5))))
                .starts_with("invalid type: floating point `655.5`, expected i64")
        );
        assert!(
            problem(with("vendor", Some(json!(1))))
                .starts_with("invalid type: integer `1`, expected a string")
        );
        assert!(
            problem(with("invoice_number", None)).starts_with("missing field `invoice_number`")
        );
        assert!(problem(with("notes", Some(json!("thanks")))).starts_with("unknown field `notes`"));
        assert!(
            problem(with("currency", Some(json!("pounds")))).starts_with(
                "unknown variant `pounds`, expected one of `GBP`, `USD`, `EUR`, `NGN`"
            )
        );
        assert!(
            problem(with("due_date", Some(json!("15 October 2026"))))
                .starts_with("input contains invalid characters")
        );
        assert_eq!(
            problem(with("total_cents", Some(json!(65500)))),
            "line items add up to 65550 cents but total_cents is 65500"
        );
        assert_eq!(
            problem("I can't find an invoice.".into()),
            "no JSON object in the reply"
        );
    }

    #[test]
    fn the_retry_loop() {
        let mut seen = Vec::new();
        let mut replies = vec![
            reply(with("total_cents", Some(json!(65500)))),
            reply(good().to_string()),
        ]
        .into_iter();
        let outcome = extract(
            |m: &[Message]| {
                seen.push(m.to_vec());
                replies.next().unwrap()
            },
            "…",
            3,
        );
        assert!(matches!(outcome, Outcome::Ok { attempts: 2, .. }));
        assert!(
            seen[1]
                .last()
                .unwrap()
                .content
                .contains("total_cents is 65500")
        );

        let mut seen = Vec::new();
        let mut replies = vec![
            Reply {
                text: r#"{"vendor": "Bright"#.into(),
                finish_reason: "length",
                refusal: None,
            },
            reply(good().to_string()),
        ]
        .into_iter();
        let outcome = extract(
            |m: &[Message]| {
                seen.push(m.to_vec());
                replies.next().unwrap()
            },
            "…",
            3,
        );
        assert!(
            matches!(outcome, Outcome::Ok { .. })
                && seen[1].last().unwrap().content.contains("cut off")
        );

        let mut calls = 0;
        let outcome = extract(
            |_: &[Message]| {
                calls += 1;
                Reply {
                    text: String::new(),
                    finish_reason: "stop",
                    refusal: Some("I can't help with that.".into()),
                }
            },
            "…",
            3,
        );
        assert_eq!(
            (outcome, calls),
            (
                Outcome::Refused {
                    detail: "I can't help with that.".into(),
                    attempts: 1
                },
                1
            )
        );

        let mut replies = vec![
            reply("nope"),
            reply("still no"),
            reply(with("vendor", Some(json!(1)))),
        ]
        .into_iter();
        let outcome = extract(|_: &[Message]| replies.next().unwrap(), "…", 3);
        assert!(
            matches!(&outcome, Outcome::Invalid { attempts: 3, detail } if detail.starts_with("invalid type: integer `1`"))
        );
    }
}
```

## 7. C# — System.Text.Json

System.Text.Json already refuses `"450"` and `655.5` for an `int`. Three options make missing fields, nulls and extra keys errors too. `JsonSchemaExporter`, built in since .NET 9, generates the schema from the same options, so the schema and the parser can't disagree. Its error *messages* are vague ("could not be converted"), but its error *paths* are precise (`$.line_items[0].amount_cents`), so the feedback to the model is built from the path.

```csharp
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
```

```csharp
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
```

## 8. C and C++ — where constrained decoding actually happens

There's no lab here: neither language has a standard JSON library, and typed decoding is what this page is about. (In C++, `nlohmann/json` is the common choice.)

But the *other* half of structured output, constrained decoding from the main lesson's §3, is C++ code when a model runs locally. llama.cpp restricts generation with **GBNF grammars**, and it can turn a JSON Schema into one. At each step, tokens the grammar doesn't allow are removed before sampling. That's the "set the probability of invalid tokens to zero" step, as real code. If you ever want to read how constrained decoding is implemented, llama.cpp's grammar code is the place to start.

**Labs:** every version is in [`ai-ml/03-ai-engineer/11-structured-output/labs/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/11-structured-output/labs), one folder per language. From the vault root, `python3 labs/run.py structured-output` runs them all and checks this page still shows the same code. Python runs through `uv` with Pydantic; Java downloads its jars on the first run; C# runs in the .NET SDK container, through podman.

## Common pitfalls

1. **Trusting a parser's defaults.** Go, Java, and Python without `strict`, all accept replies that are wrong. Test each mistake from §2 against your parser.
2. **A missing field that becomes a zero.** In Go especially, `total_cents: 0` and "no total" look the same after decoding. Validate required fields separately.
3. **A schema and a parser that disagree.** Writing the schema by hand while the parser is configured somewhere else lets them drift apart. Generate one from the other.
4. **Error messages in your language's names.** "InvoiceNumber is missing" means nothing to a model that wrote `invoice_number`. Report JSON names.
5. **Forgetting the invariant.** No schema library checks that the items add up. Write the check in every language.
6. **Validating a dict instead of the text** (Pydantic). In strict mode, dates and other JSON-encoded types only parse from JSON text.

## Check your understanding

1. Which of the five parsers would accept `"total_cents": 655.5` with default settings, and what value would your code see?
2. Why does Go need a separate validator to notice a missing `invoice_number`?
3. What does `deny_unknown_fields` add to a Rust struct, both when parsing and in the generated schema?
4. Why does the C# lab build its feedback from `JsonException.Path` instead of the message?
5. Where in the stack does schema-constrained decoding happen when you call a local model through Ollama, and in what language?

<details>
<summary>Answers — after your attempt</summary>

1. Java's Jackson, by default. Your code would see `655`, and the invariant check would then report a confusing mismatch, or pass by coincidence.
2. Go's decoder doesn't treat a missing key as an error. The field keeps its zero value, `""`, which looks like a real value. Only a separate check that the field isn't empty (the validator's `required`) notices.
3. Parsing fails on any key the struct doesn't have, and the generated schema gets `"additionalProperties": false`, so the model is told about the rule too.
4. The message for most type errors is just "could not be converted to Invoice", which doesn't say which field. The path says exactly where the problem is, such as `line_items[0].amount_cents`, and that's what the model needs to fix it.
5. In the inference engine, llama.cpp, which is C++. It turns the schema into a grammar and removes disallowed tokens before each sampling step.

</details>

## Practice — independent task

**Harden your language's parser against a list of bad replies.**

1. Take your language's lab and add one test per row of the table in §2, plus `null` for a required string.
2. Comment out each strictness setting in turn, run the tests, and note which mistake gets through.
3. Then run the main lesson's `live.ts` comparison through your language: send the generated schema to Ollama's `format` field, and run your parser on three replies with and three without it.

**Done when:** every row of §2 has a failing-then-passing test in your language, you have a one-line note per setting saying what it stopped, and you have six real replies parsed.

## Before moving on

You can generate a schema from a type in your language, configure its parser to reject every mistake in §2, and say which of your language's defaults would have let one through.

**Recap.** In most languages, one type gives you the schema, the parser, the validator and the type your code uses. The differences are in default strictness. Rust is strict out of the box; C# is strict on types; Python needs `strict=True`; Go needs `DisallowUnknownFields` and a validator; Java's Jackson needs four lenient defaults switched off. In every language, the invariant is still your own code. Constrained decoding itself, for local models, is C++ in llama.cpp.

## Related
- [[ai-ml/03-ai-engineer/11-structured-output/index|Structured output]] — the main lesson
- [[ai-ml/03-ai-engineer/04-calling-models/in-other-languages|Calling models in other languages]] — the clients these parsers sit behind
- [[ai-ml/03-ai-engineer/02-how-llms-work/in-other-languages|How LLMs work in other languages]] — llama.cpp and sampling, by language
