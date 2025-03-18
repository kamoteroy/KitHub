import tkinter as tk
from tkinter import ttk

def show_dropdown(event):
    x, y, _, h = dropdown_button.bbox("insert")  # Get button position
    x += dropdown_button.winfo_rootx()
    y += dropdown_button.winfo_rooty() - 100  # Move upwards

    popup = tk.Toplevel(root)
    popup.wm_overrideredirect(True)  # Remove window borders
    popup.geometry(f"100x100+{x}+{y}")  # Position above the button

    for option in ["Option 1", "Option 2", "Option 3"]:
        btn = tk.Button(popup, text=option, command=lambda opt=option: select_option(opt, popup))
        btn.pack(fill="x")

def select_option(option, popup):
    dropdown_button.config(text=option)
    popup.destroy()

root = tk.Tk()
root.geometry("200x200")

dropdown_button = tk.Button(root, text="Select", command=lambda: show_dropdown(None))
dropdown_button.pack(pady=50)

root.mainloop()
