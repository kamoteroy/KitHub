import os
import sys
import tkinter as tk

def restart_app():
    """ Restart the entire Python script """
    python = sys.executable  # Get the Python interpreter path
    os.execl(python, python, *sys.argv)  # Restart script

# Tkinter UI
root = tk.Tk()
root.geometry("300x200")

restart_btn = tk.Button(root, text="Restart App", command=restart_app)
restart_btn.pack(pady=20)

root.mainloop()
