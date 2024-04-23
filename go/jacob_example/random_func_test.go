package main

import (
	"testing"
)

func TestRandomInt(t *testing.T) {

	// Test random integers between 0 and 9
	for i := 0; i < 1000; i++ {
		randomNumber := RandomInt(0, 9)
		if randomNumber < 0 || randomNumber > 9 {
			t.Errorf("Random number out of range: %d", randomNumber)
		}
	}
}

func TestRandomIntRange(t *testing.T) {

	// Test random integers between 5 and 15
	for i := 0; i < 1000; i++ {
		randomNumber := RandomInt(5, 15)
		if randomNumber < 5 || randomNumber > 15 {
			t.Errorf("Random number out of range: %d", randomNumber)
		}
	}
}
