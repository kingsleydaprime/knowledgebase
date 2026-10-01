// Package orders: three layers. Domain errors are values; the handler maps them to HTTP.
package orders

import (
	"errors"
	"fmt"
	"net/http"
)

type Item struct {
	SKU      string
	Quantity int
}

// A sentinel error for a fixed condition, and a type for one that carries data.
var ErrEmptyOrder = errors.New("an order needs at least one item")

type OutOfStockError struct{ SKU string }

func (e *OutOfStockError) Error() string { return fmt.Sprintf("out of stock: %s", e.SKU) }

// Repository: the only code that knows how data is stored.
type Repository struct {
	Stock  map[string]int
	orders [][]Item
}

func (r *Repository) create(items []Item) int {
	r.orders = append(r.orders, items)
	return len(r.orders)
}

// Service: business rules. It returns errors; it never chooses a status code.
type Service struct{ Repo *Repository }

func (s *Service) Place(items []Item) (int, error) {
	if len(items) == 0 {
		return 0, ErrEmptyOrder
	}
	for _, it := range items {
		if s.Repo.Stock[it.SKU] < it.Quantity {
			return 0, &OutOfStockError{SKU: it.SKU}
		}
	}
	for _, it := range items {
		s.Repo.Stock[it.SKU] -= it.Quantity
	}
	return s.Repo.create(items), nil
}

// StatusFor is the one place domain errors become HTTP statuses.
func StatusFor(err error) int {
	var oos *OutOfStockError
	switch {
	case err == nil:
		return http.StatusCreated
	case errors.Is(err, ErrEmptyOrder):
		return http.StatusBadRequest
	case errors.As(err, &oos):
		return http.StatusConflict
	default:
		return http.StatusInternalServerError
	}
}
