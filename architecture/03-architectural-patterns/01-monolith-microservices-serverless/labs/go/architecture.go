// Package architecture: the arithmetic behind choosing a monolith, microservices or serverless, and a
// modular-monolith boundary checker. The same numbers as the TypeScript lab.
package architecture

import (
	"math"
	"slices"
	"strings"
)

func CoordinationLinks(people int) int { return people * (people - 1) / 2 }

func ReleaseBreaks(changes int, p float64) float64 { return 1 - math.Pow(1-p, float64(changes)) }

// Extract returns the time added to a request, and the chance all its calls succeed, when a module moves behind the network.
func Extract(callsPerRequest int, networkMs, callAvailability float64) (addedMs, availability float64) {
	return float64(callsPerRequest) * networkMs, math.Pow(callAvailability, float64(callsPerRequest))
}

type Pricing struct{ PerMillionRequests, PerGBSecond float64 }

func ServerlessMonthly(requests, ms, memoryGB float64, p Pricing) float64 {
	return requests/1e6*p.PerMillionRequests + requests*(ms/1000)*memoryGB*p.PerGBSecond
}

func BreakEvenRequests(serverMonthly, ms, memoryGB float64, p Pricing) float64 {
	return serverMonthly / (p.PerMillionRequests/1e6 + (ms/1000)*memoryGB*p.PerGBSecond)
}

func ColdShare(perMinute, warmMinutes float64) float64 { return math.Exp(-perMinute * warmMinutes) }

func SimulateColdShare(perMinute, warmMinutes float64, requests int, seed uint32) float64 {
	a := seed
	random := func() float64 { // mulberry32, as in week 1's lab
		a += 0x6d2b79f5
		t := (a ^ a>>15) * (a | 1)
		t ^= t + (t^t>>7)*(t|61)
		return float64(t^t>>14) / 4294967296
	}
	cold := 0
	for range requests {
		if -math.Log(1-random())/perMinute > warmMinutes {
			cold++
		}
	}
	return float64(cold) / float64(requests)
}

type Module struct {
	Name    string
	Imports []string
}

// BoundaryViolations lists imports that reach inside another module. In real Go code, putting a module's insides
// in an internal/ directory makes the compiler refuse such imports, so this check comes for free.
func BoundaryViolations(modules []Module) []string {
	names := map[string]bool{}
	for _, m := range modules {
		names[m.Name] = true
	}
	var out []string
	for _, m := range modules {
		for _, imp := range m.Imports {
			target, _, inside := strings.Cut(imp, "/")
			if target != m.Name && names[target] && inside {
				out = append(out, m.Name+" → "+imp)
			}
		}
	}
	return out
}

// FindCycle returns a dependency cycle as a path that starts and ends at the same module, or nil. (Go refuses
// import cycles between packages at compile time; between modules of one package, nothing does.)
func FindCycle(modules []Module) []string {
	deps := map[string][]string{}
	for _, m := range modules {
		for _, imp := range m.Imports {
			d, _, _ := strings.Cut(imp, "/")
			if d != m.Name && !slices.Contains(deps[m.Name], d) {
				deps[m.Name] = append(deps[m.Name], d)
			}
		}
	}
	state := map[string]string{}
	var path []string
	var visit func(string) []string
	visit = func(name string) []string {
		switch state[name] {
		case "done":
			return nil
		case "visiting":
			return append(slices.Clone(path[slices.Index(path, name):]), name)
		}
		state[name] = "visiting"
		path = append(path, name)
		for _, d := range deps[name] {
			if cycle := visit(d); cycle != nil {
				return cycle
			}
		}
		path = path[:len(path)-1]
		state[name] = "done"
		return nil
	}
	for _, m := range modules {
		if cycle := visit(m.Name); cycle != nil {
			return cycle
		}
	}
	return nil
}
