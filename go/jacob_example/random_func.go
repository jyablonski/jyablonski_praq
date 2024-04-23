package main

import (
	"math/rand"
)

// RandomInt returns a random integer between min and max (inclusive).
func RandomInt(min, max int) int {
	return rand.Intn(max-min+1) + min
}
