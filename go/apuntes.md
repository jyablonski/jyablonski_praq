# Go
1. **Simplicity**: Go is designed to be simple and easy to understand. It has a clean syntax and minimalistic approach, making it easier to read and maintain.

2. **Efficiency**: Go is a compiled language, which means it can be very fast. It's well-suited for system programming, networking programming, and other tasks that require high performance.

3. **Concurrency Support**: Go has built-in support for concurrency, making it easy to write programs that do many things simultaneously. Goroutines, lightweight threads managed by the Go runtime, and channels, a powerful feature for communication between goroutines, are central to Go's approach to concurrency.

4. **Garbage Collection**: Go has automatic memory management through garbage collection. This feature helps developers avoid many common programming errors that can occur in languages without garbage collection.

5. **Static Typing**: Go is statically typed, which means that variable types are checked at compile time, reducing the chances of runtime errors. This also helps in maintaining code.

6. **Standard Library**: Go comes with a rich standard library that provides support for various common tasks like reading and writing files, networking, cryptography, and more. 

7. **Cross-Platform**: Go is a cross-platform language, meaning that it's possible to compile a Go program on one type of computer and run it on another. 


## Common Commands
``` sh
# this just runs 1 file
go run main.go
go run file1.go file2.go

# this will run an entire project
go run ./

# this will run tests when they use the `testing` module
go test

# verbose mode
go test -v

# show coverage
go test -cover

go build -o myprogram
./myprogram
```

## Tests
