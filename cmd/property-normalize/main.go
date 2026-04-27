package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("usage: property-normalize <input-json-file>")
		os.Exit(1)
	}

	inputPath := os.Args[1]

	fmt.Println("Input file:", inputPath)
}
