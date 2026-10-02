// Package fees: Go favours the open design — a map of functions, or small interfaces.
package fees

// Open for extension: a new method is a new entry.
var OpenRules = map[string]func(amountKobo int64) int64{
	"card":     func(a int64) int64 { return a * 29 / 1000 },
	"transfer": func(int64) int64 { return 50 },
}

// Closed: Go has no enums or exhaustive switch — constants of a named type are the convention,
// and a forgotten case compiles. The default branch is the only safety net.
type Method int

const (
	Card Method = iota
	Transfer
)

func Fee(m Method, amountKobo int64) (int64, bool) {
	switch m {
	case Card:
		return amountKobo * 29 / 1000, true
	case Transfer:
		return 50, true
	default:
		return 0, false
	}
}
