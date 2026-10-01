// Package rates: decorators as middleware — a function from RateSource to RateSource,
// the same shape as net/http middleware.
package rates

import (
	"errors"
	"fmt"
	"sync"
)

type RateSource interface {
	Rate(base, quote string) (int, error)
}

// RateFunc adapts a plain function to the interface, like http.HandlerFunc.
type RateFunc func(base, quote string) (int, error)

func (f RateFunc) Rate(base, quote string) (int, error) { return f(base, quote) }

type Middleware func(RateSource) RateSource

type FlakyAPI struct{ Calls, Failures int }

func (a *FlakyAPI) Rate(base, quote string) (int, error) {
	a.Calls++
	if a.Calls <= a.Failures {
		return 0, errors.New("503 from rates API")
	}
	if base == "GBP" && quote == "NGN" {
		return 2000, nil
	}
	return 1, nil
}

func Retrying(attempts int) Middleware {
	return func(next RateSource) RateSource {
		return RateFunc(func(base, quote string) (int, error) {
			var err error
			for range attempts {
				var v int
				if v, err = next.Rate(base, quote); err == nil {
					return v, nil
				}
			}
			return 0, err
		})
	}
}

func Caching() Middleware {
	return func(next RateSource) RateSource {
		var mu sync.Mutex
		cache := map[string]int{}
		return RateFunc(func(base, quote string) (int, error) {
			key := base + "->" + quote
			mu.Lock()
			v, ok := cache[key]
			mu.Unlock()
			if ok {
				return v, nil
			}
			v, err := next.Rate(base, quote)
			if err == nil {
				mu.Lock()
				cache[key] = v
				mu.Unlock()
			}
			return v, err
		})
	}
}

func Logging(log *[]string) Middleware {
	return func(next RateSource) RateSource {
		return RateFunc(func(base, quote string) (int, error) {
			v, err := next.Rate(base, quote)
			*log = append(*log, fmt.Sprintf("%s->%s = %d", base, quote, v))
			return v, err
		})
	}
}

// Chain applies middleware outermost-first: Chain(src, a, b) is a(b(src)).
func Chain(src RateSource, mws ...Middleware) RateSource {
	for i := len(mws) - 1; i >= 0; i-- {
		src = mws[i](src)
	}
	return src
}
