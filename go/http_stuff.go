package main

// fmt needed to print results
// io/ioutil needed to read the respojnse body
// net/http needed for http requests
import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func main() {
	// URL of the REST API endpoint
	apiURL := "https://api.jyablonski.dev/game_types"

	// Send a GET request to the API endpoint
	resp, err := http.Get(apiURL)
	if err != nil {
		fmt.Printf("Error sending request: %v\n", err)
		return
	}
	defer resp.Body.Close()

	// Check the response status code
	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Error: Unexpected status code %d\n", resp.StatusCode)
		return
	}

	// Read the response body
	body, err := ioutil.ReadAll(resp.Body)

	// if there is an error, it will be stored in err
	// if there is no error, then err = nil
	if err != nil {
		fmt.Printf("Error reading response body: %v\n", err)
		return
	}

	// Print some of the response data
	fmt.Println("Response:")
	fmt.Printf("Status: %s\n", resp.Status)
	fmt.Printf("Response Body: %s\n", body)
}