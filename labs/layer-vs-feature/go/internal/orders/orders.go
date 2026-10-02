// Package orders is a feature: handler, service and storage together.
package orders

import (
	"encoding/json"
	"errors"
	"net/http"

	"shop/internal/orders/internal/store"
)

// UserChecker is what orders needs from users — declared here, where it's used.
type UserChecker interface{ Exists(id string) bool }

var errUnknownUser = errors.New("unknown user")

type service struct {
	users UserChecker
	store *store.Memory
}

func (s *service) place(userID string, kobo int) (store.Order, error) {
	if !s.users.Exists(userID) {
		return store.Order{}, errUnknownUser
	}
	return s.store.Insert(userID, kobo), nil
}

// Routes is the feature's public API: the composition root mounts it.
func Routes(users UserChecker) http.Handler {
	svc := &service{users: users, store: &store.Memory{}}
	mux := http.NewServeMux()
	mux.HandleFunc("POST /orders", func(w http.ResponseWriter, r *http.Request) {
		var body struct {
			UserID string `json:"userId"`
			Kobo   int    `json:"totalKobo"`
		}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			http.Error(w, "invalid JSON", http.StatusBadRequest)
			return
		}
		order, err := svc.place(body.UserID, body.Kobo)
		if errors.Is(err, errUnknownUser) {
			http.Error(w, err.Error(), http.StatusUnprocessableEntity)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(order)
	})
	return mux
}
