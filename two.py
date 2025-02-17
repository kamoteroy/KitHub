import tkinter as tk
from PIL import Image, ImageTk
import socket

# Create the main window
root = tk.Tk()
root.geometry("800x480")
root.title("KitHub")
root.configure(bg="#800000")

# Global variables
reconnecting_page = None
current_page = None  # Keeps track of the currently displayed page

# Function to check if connected to the internet
def is_connected():
    try:
        # Try connecting to a known host (Google's public DNS server) on port 53
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except (socket.timeout, socket.error):
        return False

# Function to show the reconnecting page
def show_reconnecting_page():
    global reconnecting_page, current_page

    # Clear the current page if it exists
    if current_page:
        current_page.pack_forget()

    # Create the reconnecting page if it doesn't already exist
    if reconnecting_page is None:
        reconnecting_page = tk.Frame(root, bg="blue")

        # Display "Reconnecting..." message
        reconnecting_label = tk.Label(reconnecting_page, text="Reconnecting...", font=("Arial", 24), fg="white", bg="#800000")
        reconnecting_label.place(relx=0.5, rely=0.5, anchor="center")

        # Load the "no internet" GIF
        recon = Image.open("no_internet.gif")
        reconFrames = []
        for frame in range(recon.n_frames):
            recon.seek(frame)
            frame_image = recon.convert("RGBA")
            frame_image = frame_image.resize((300, 200))
            reconFrames.append(ImageTk.PhotoImage(frame_image))

        # Create a label to display the GIF
        recon_gif = tk.Label(reconnecting_page, image=reconFrames[0], bg="#800000")
        recon_gif.place(relx=0.5, rely=0.6, anchor="center")

        # Function to animate the GIF
        def recon_animate(frame_index=0):
            recon_gif.config(image=reconFrames[frame_index])
            frame_index = (frame_index + 1) % len(reconFrames)
            root.after(400, recon_animate, frame_index)

        # Start the GIF animation
        recon_animate()

    # Show the reconnecting page
    reconnecting_page.pack(fill="both", expand=True)
    current_page = reconnecting_page

# Function to show the main page
def show_main_page():
    global current_page

    # Create the main page if it doesn't already exist
    main_page = tk.Frame(root, bg="#800000")

    # Display a message on the main page
    main_label = tk.Label(main_page, text="Main Page - Connected to the Internet!", font=("Arial", 24), fg="white", bg="#800000")
    main_label.place(relx=0.5, rely=0.4, anchor="center")

    # Button to navigate to the second page
    navigate_button = tk.Button(main_page, text="Go to Second Page", command=show_second_page, font=("Arial", 16), bg="white")
    navigate_button.place(relx=0.5, rely=0.6, anchor="center")

    # Clear the current page if it is displayed
    if current_page:
        current_page.pack_forget()

    # Show the main page
    main_page.pack(fill="both", expand=True)
    current_page = main_page

# Function to show the second page
def show_second_page():
    global current_page

    # Create the second page
    second_page = tk.Frame(root, bg="#004080")

    # Display a message on the second page
    second_label = tk.Label(second_page, text="Second Page - Connected to the Internet!", font=("Arial", 24), fg="white", bg="#004080")
    second_label.place(relx=0.5, rely=0.5, anchor="center")

    # Button to go back to the main page
    back_button = tk.Button(second_page, text="Back to Main Page", command=show_main_page, font=("Arial", 16), bg="white")
    back_button.place(relx=0.5, rely=0.7, anchor="center")

    # Clear the current page if it is displayed
    if current_page:
        current_page.pack_forget()

    # Show the second page
    second_page.pack(fill="both", expand=True)
    current_page = second_page

# Function to check the internet connection every second
def check_connection():
    if is_connected():
        if current_page == reconnecting_page:
            show_main_page()  # Always return to the main page when internet reconnects
    else:
        show_reconnecting_page()

    # Schedule the next connection check in 1 second
    root.after(1000, check_connection)

# Start by checking the connection
check_connection()

# Run the Tkinter event loop
root.mainloop()
