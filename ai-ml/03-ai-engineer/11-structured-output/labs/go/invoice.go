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
