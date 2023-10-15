package main

import (
	"database/sql"
	"fmt"
	"log"
	"github.com/lib/pq"
)

func main() {
	// Replace with your PostgreSQL connection information
	connStr := "user=myuser dbname=mydb sslmode=disable"

	// Connect to the PostgreSQL database
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Error opening database connection: %v", err)
	}
	defer db.Close()

	// Query the sales table
	row := db.QueryRow("SELECT * FROM sales.sales LIMIT 1")

	var id int
	var name string
	var amount float64

	// Scan the row values into variables
	err = row.Scan(&id, &name, &amount)
	if err != nil {
		log.Fatalf("Error scanning row: %v", err)
	}

	// Print the results
	fmt.Printf("Row 1: ID=%d, Name=%s, Amount=%f\n", id, name, amount)
}