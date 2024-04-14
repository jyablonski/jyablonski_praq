package main

import (
	"fmt"
)

func main() {
	fmt.Println("Hello, World!")
	var name_one string = "Jacob"
	var name_two = "Yablonski"
	var name_three string
	name_four := "yeehaw"

	fmt.Println("Round 1, Fight! " + name_one + " " + name_two + name_three + "!" + name_four)

	name_one = "boobs"
	name_three = "!"

	fmt.Println("Round 2, Fight! " + name_one + " " + name_two + name_three + "!")

	const name_five string = "kickn"

	fmt.Println(name_five)

	float1 := 3.14159265359

	float1 = float1 / 2
	fmt.Println(float1)

	var my_age int = 27

	// this sets it to 8 bits max, only values -128 to 127
	var num_one int8 = 25
	var num_two int8 = -127

	// uint is unsigned
	var num_three uint8 = 255

	multiplication := num_one * num_two
	fmt.Println(num_three, multiplication, my_age)

	var my_float1 float32 = 1.5
	var my_float2 float64 = 1213213123.11

	fmt.Println(my_float1, my_float2)

	fmt.Print("Hello ")
	fmt.Print("World \n")
}
