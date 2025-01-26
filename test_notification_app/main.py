import os
import subprocess
import tkinter as tk
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image


# Path to the WAV file for the button actions
wav_file = "test_notification_app/applause.wav"


# Function to run the bash command
def run_bash_command():
    try:
        # Run the bash command using subprocess
        subprocess.run(
            "sudo apt-get update && sudo apt-get -y upgrade", shell=True, check=True
        )
        print("System update and upgrade completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error while updating and upgrading: {e}")


# Functions to handle button presses
def button2_action():
    os.system(f"aplay {wav_file}")
    print("Button 2 pressed!")


def run_updates_button():
    run_bash_command()


def button3_action():
    print("Button 3 pressed!")


def button4_action():
    print("Button 4 pressed!")


# Function to quit the system tray icon
def quit_action(icon, item):
    icon.stop()


# Create the window
root = tk.Tk()
root.title("Simple GUI with Buttons")

# Set the window size to 800x600
root.geometry("800x600")

# Set window icon for the tkinter window (this can be any image format like PNG)
root.iconphoto(True, tk.PhotoImage(file="test_notification_app/infernal.png"))

# Create a frame for the title and buttons
left_frame = tk.Frame(root)
left_frame.pack(side="left", padx=20, pady=20)

# Create the title label
title_label = tk.Label(left_frame, text="Operations", font=("Helvetica", 16))
title_label.pack(pady=10)

# Create button widgets
button1 = tk.Button(left_frame, text="Run Updates", command=run_updates_button)
button1.pack(pady=5)

button2 = tk.Button(left_frame, text="Run Updates", command=button2_action)
button2.pack(pady=5)

button3 = tk.Button(left_frame, text="Button 3", command=button3_action)
button3.pack(pady=5)

button4 = tk.Button(left_frame, text="Button 4", command=button4_action)
button4.pack(pady=5)

# Load the custom PNG for the tray icon (from file)
tray_icon_image = Image.open("test_notification_app/infernal.png")

# Create a menu for the system tray
menu = Menu(MenuItem("Quit", quit_action))


# Function to set up the system tray
def create_tray_icon():
    icon = Icon("Simple GUI", tray_icon_image, menu=menu)
    icon.run()


# Run the system tray icon in a separate thread
tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
tray_thread.start()

# Start the Tkinter GUI
root.mainloop()
