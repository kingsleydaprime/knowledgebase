// Package store is private to orders: Go only lets code under internal/orders import it.
package store

type Order struct {
	ID     int    `json:"id"`
	UserID string `json:"userId"`
	Kobo   int    `json:"totalKobo"`
}

type Memory struct{ orders []Order }

func (m *Memory) Insert(userID string, kobo int) Order {
	o := Order{ID: len(m.orders) + 1, UserID: userID, Kobo: kobo}
	m.orders = append(m.orders, o)
	return o
}
