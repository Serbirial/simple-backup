package main

import (
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"os"
	"strconv"
	"strings"
)

var sizeSuffixes = map[rune]float64{
	'K': float64(1024),
	'M': float64(1024 * 1024),
	'G': float64(1024 * 1024 * 1024)}

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
	var multiplier float64 = 1
	if m := sizeSuffixes[suffix]; m != 0 {
		multiplier = m
		input = input[:len(input)-1]
	}
	size := must(strconv.ParseFloat(input, 64))
	return uint(size * multiplier)
}

// write len(data) random bytes to w
func writeRandom(w *os.File, data []byte) {
	rand.Read(data)
	encoded := base64.RawURLEncoding.EncodeToString(data)
	w.WriteString("\"" + encoded + "\",\n")
}

func main() {
	fmt.Println("Total JSON file size (K/M/G):")
	var input string
	fmt.Scanln(&input)
	size := getSize(input)

	fmt.Println("Chunk (JSON item) size (K/M/G):")
	fmt.Scanln(&input)
	chunkSize := getSize(input)
	nChunk := size / chunkSize

	var filename string
	fmt.Println("Filename:")
	fmt.Scanln(&filename)

	// Create file
	file := must(os.Create(filename))

	// Open JSON syntax
	file.WriteString("[\n")
	// Write each chunk
	data := make([]byte, base64.RawURLEncoding.DecodedLen(int(chunkSize)))
	for i := uint(0); i < nChunk; i++ {
		writeRandom(file, data)
	}
	// Write remainder chunk
	if finalChunk := size % chunkSize; finalChunk != 0 {
		data = make([]byte, base64.RawURLEncoding.DecodedLen(int(finalChunk)))
		writeRandom(file, data)
	}
	// Close JSON
	file.WriteString("]\n")

	file.Close()
}