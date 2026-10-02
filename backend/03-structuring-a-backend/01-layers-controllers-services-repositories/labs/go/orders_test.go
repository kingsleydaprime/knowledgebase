package orders

import (
	"errors"
	"fmt"
	"testing"
)

func TestServiceReturnsTypedErrors(t *testing.T) {
	svc := &Service{Repo: &Repository{Stock: map[string]int{"mug": 1}}}
	_, err := svc.Place([]Item{{"mug", 2}})
	var oos *OutOfStockError
	if !errors.As(err, &oos) || oos.SKU != "mug" {
		t.Fatalf("err = %v", err)
	}
}

func TestStatusMappingSurvivesWrapping(t *testing.T) {
	stock := map[string]int{"mug": 1}
	svc := &Service{Repo: &Repository{Stock: stock}}
	_, err := svc.Place(nil)
	if StatusFor(err) != 400 {
		t.Fatal("empty order should be 400")
	}
	_, err = svc.Place([]Item{{"mug", 5}})
	if StatusFor(fmt.Errorf("placing order: %w", err)) != 409 { // a wrapped error still maps
		t.Fatal("out of stock should be 409")
	}
	id, err := svc.Place([]Item{{"mug", 1}})
	if StatusFor(err) != 201 || id != 1 || stock["mug"] != 0 {
		t.Fatalf("id=%d err=%v stock=%d", id, err, stock["mug"])
	}
}
