package main

import (
	_ "image/png"
	"log"
	"os"
	"os/exec"

	"github.com/getlantern/systray"
)

func runBashCommand() {
	log.Println("Running System Updates")
	cmd := exec.Command("bash", "-c", "sudo apt-get update && sudo apt-get -y upgrade")
	err := cmd.Run()
	if err != nil {
		log.Println("Error while updating and upgrading:", err)
	} else {
		log.Println("System Updates completed successfully!")
	}
}

func quitAction() {
	systray.Quit()
}

func createTrayIcon() {
	iconData, err := os.ReadFile("/home/jacob/Pictures/infernal.png")
	if err != nil {
		log.Fatal("Failed to load icon image: ", err)
	}

	// Set up the systray
	systray.Run(func() {
		systray.SetIcon(iconData)
		systray.SetTitle("Simple GUI")

		// Add menu items
		mRunUpdates := systray.AddMenuItem("Run Updates", "Run system updates")
		mQuit := systray.AddMenuItem("Quit", "Quit the application")

		// Event handling for tray icon menu items
		go func() {
			for {
				select {
				case <-mRunUpdates.ClickedCh:
					runBashCommand()
				case <-mQuit.ClickedCh:
					quitAction()
					return
				}
			}
		}()
	}, quitAction)
}

func main() {
	createTrayIcon()

	// Keep the program running indefinitely to keep the tray icon active
	select {}
}
