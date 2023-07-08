package main

import (
	"bufio"
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"os"
	"strconv"
	"strings"
)

var sizeSuffixes = map[rune]uint{
	'K': 1000,
	'M': 1_000_000,
	'G': 1_000_000_000}

func must[T any](v T, e error) T {
	if e != nil {
		panic(e)
	}
	return v
}

func getSize(input string) uint {
	input = strings.ToUpper(input)
	// Remove 'B' suffix, e.g KB -> K
	if strings.HasSuffix(input, "B") {
		input = input[:len(input)-1]
	}
	suffix := rune(input[len(input)-1])
	var multiplier uint = 1
	if m := sizeSuffixes[suffix]; m != 0 {
		multiplier = m
		input = input[:len(input)-1]
	}
	size := uint(must(strconv.ParseFloat64(input, 10, 64)))
	return size * multiplier
}

func main() {
	fmt.Println("How big make jason file.?")
	var input string
	fmt.Scanln(&input)
	size := getSize(input)

	fmt.Println("how beeg chunk make")
	fmt.Scanln(&input)
	chunkSize := getSize(input)
	nChunk := size / chunkSize

	// start writing ye olde dick and balls
	file := must(os.Create("fuck.json"))
	w := bufio.NewWriter(file)
	// Open JSON
	w.WriteString("[\n")

	for i := uint(0); i < nChunk; i++ {
		yes := make([]byte, base64.RawURLEncoding.DecodedLen(int(chunkSize)))
		rand.Read(yes)
		encoded := base64.RawURLEncoding.EncodeToString(yes)
		w.WriteString("\"" + encoded + "\",\n")
	}

	// write the last thing
	if finalChunk := size % chunkSize; finalChunk != 0 {
		yes := make([]byte, base64.RawURLEncoding.DecodedLen(int(finalChunk)))
		rand.Read(yes)
		encoded := base64.RawURLEncoding.EncodeToString(yes)
		w.WriteString("\"" + encoded + "\",\n")
	}

	w.WriteString("]\n")
	w.Flush()

	file.Close()
}
