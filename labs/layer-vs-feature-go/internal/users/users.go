// Package users is a feature. Its exported names are its public API.
package users

import "errors"

var ErrNotFound = errors.New("user not found")

type Service struct{ emails map[string]string }

func NewService() *Service {
	return &Service{emails: map[string]string{"u1": "ada@x.com"}}
}

// Exists is the one thing other features may ask.
func (s *Service) Exists(id string) bool {
	_, ok := s.emails[id]
	return ok
}
