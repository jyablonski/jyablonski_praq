package main

import "fmt"

func main() {
	fmt.Println("=== Demonstrating pointers with slice appending ===")

	// Original slice
	data := []int{1, 2, 3}
	fmt.Println("Before append, data:", data)
	fmt.Printf("%p\n", &data) // Print address of data slice header

	// Correct: pass pointer to the slice to appendData function
	appendData(&data, 4)
	fmt.Println("After appendData with pointer, data:", data)
	fmt.Printf("%p\n", &data) // Print address of data slice header

	// Reset data
	data = []int{1, 2, 3}
	fmt.Println("\nReset data:", data)

	// Incorrect: pass slice by value (not pointer)
	appendDataWrong(data, 4)
	fmt.Println("After appendDataWrong without pointer, data:", data)

	result := sumInts(data)
	fmt.Println("Sum of data:", result)

	fmt.Printf("%p\n", &data) // Print address of data slice header
}

// appendData correctly modifies the original slice via pointer
// By passing a pointer to the slice (*[]int), you let the function modify the original slice header itself, updating length, capacity, and the pointer to the underlying array — so changes like append are reflected outside the function.
func appendData(data *[]int, val int) {
	fmt.Println("  -> Inside appendData before append, *data:", *data)
	*data = append(*data, val) // dereference pointer, append val
	fmt.Println("  -> Inside appendData after append, *data:", *data)
}

// appendDataWrong modifies a copy of the slice, original remains unchanged
// any modifications to the slice variable inside the function — like appending — affect only that copy.
func appendDataWrong(data []int, val int) {
	fmt.Println("  -> Inside appendDataWrong before append, data:", data)
	data = append(data, val) // modifies local copy only
	fmt.Println("  -> Inside appendDataWrong after append, data:", data)
}

// no pointers or dereferencing here, just a simple function to sum integers in a slice
func sumInts(nums []int) int {
	sum := 0
	for _, num := range nums {
		sum += num
	}
	return sum
}
