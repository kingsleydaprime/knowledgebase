// The composition root: the only place that knows every feature.
package main

import (
	"log"
	"net/http"

	"shop/internal/orders"
	"shop/internal/users"
)

func newMux() http.Handler {
	mux := http.NewServeMux()
	mux.Handle("/orders", orders.Routes(users.NewService()))
	return mux
}

func main() {
	log.Fatal(http.ListenAndServe(":8080", newMux()))
}
