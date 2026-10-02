// Package memory holds driven adapters. It imports the domain — never the other way round.
package memory

import "shop/domain"

type Orders struct{ Saved []domain.Order }

func (o *Orders) Save(order domain.Order) error {
	o.Saved = append(o.Saved, order)
	return nil
}

type Payments struct{ DeclineAbove int64 }

func (p Payments) Charge(_ string, kobo int64) (bool, error) { return kobo <= p.DeclineAbove, nil }
