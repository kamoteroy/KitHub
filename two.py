import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from supabase import Client, create_client

# Supabase connection
url = "https://gzjxxpeofotelxrzblez.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6anh4cGVvZm90ZWx4cnpibGV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcxMDEwODEsImV4cCI6MjA1MjY3NzA4MX0.R_tCibbHI78B0JYvIja4aNam3tltG3M-eDnmQKn15Cg"
supabase: Client = create_client(url, key)

# Fetch items from Supabase
item_list = supabase.table('items').select('*').order('id').execute()
items = item_list.data

# Sample Data (for testing)
if not items:
    items = [
        {'id': 1, 'item_name': 'Ballpen', 'item_photo': 'ballpen.jpg', 'forsale': 0, 'slot': 1},
        {'id': 2, 'item_name': 'Marker', 'item_photo': 'marker.jpg', 'forsale': 0, 'slot': 1},
        {'id': 3, 'item_name': 'Highlighter', 'item_photo': 'highlighter.jpg', 'forsale': 1, 'slot': 1},
        {'id': 4, 'item_name': 'Correction Tape', 'item_photo': 'correction.jpg', 'forsale': 1, 'slot': 2},
        {'id': 5, 'item_name': 'ID Lace', 'item_photo': 'idlace.jpg', 'forsale': 1, 'slot': 3},
        {'id': 6, 'item_name': 'Footmop', 'item_photo': 'footmop.jpg', 'forsale': 1, 'slot': 4}
    ]

# Group items by slot
slot_items = {}
for item in items:
    slot = item['slot']
    if slot not in slot_items:
        slot_items[slot] = []
    slot_items[slot].append(item)

# Create main window
root = tk.Tk()
root.geometry("800x480")
root.title("KitHub")
root.configure(bg="#ffce03")

# Function to update image and name dynamically
def update_selection(event, slot, dropdown_var, image_label, name_label):
    selected_name = dropdown_var.get()
    selected_item = next((i for i in slot_items[slot] if i['item_name'] == selected_name), None)
    
    if selected_item:
        img_path = f"img/{selected_item['item_photo']}"
        if not os.path.exists(img_path):
            img_path = "img/placeholder.jpg"
        
        img = Image.open(img_path).resize((80, 80), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo
        name_label.config(text=selected_item['item_name'])

# Function to switch to Admin Page with confirmation
def show_admin_page():
    if messagebox.askyesno("Confirmation", "Go to Admin Page?"):
        main_frame.place_forget()  # Hide main page
        admin_frame.place(relwidth=1, relheight=1)  # Show admin page

# Function to return to Main Page
def return_to_main():
    if messagebox.askyesno("Confirmation", "Return to Main Page?"):
        admin_frame.place_forget()  # Hide admin page
        main_frame.place(relwidth=1, relheight=1)  # Show main page

# Function for OK button action
def ok_button_action():
    messagebox.askyesno("Confirmation", "Are you sure?")

# Main Page UI
main_frame = tk.Frame(root, bg="#ffce03")
main_frame.place(relwidth=1, relheight=1)

main_label = tk.Label(main_frame, text="Welcome to KitHub", font=("Arial", 20), bg="#ffce03")
main_label.place(relx=0.5, rely=0.3, anchor="center")

admin_button = tk.Button(main_frame, text="Admin Page", font=("Arial", 14), command=show_admin_page)
admin_button.place(relx=0.5, rely=0.5, anchor="center")

# Admin Page UI (Full Screen)
admin_frame = tk.Frame(root, bg="white")

ok_button = tk.Button(admin_frame, text="OK", font=("Arial", 14), command=ok_button_action)
ok_button.place(relx=0.05, rely=0.05)  # Left side of the screen

back_button = tk.Button(admin_frame, text="Back", font=("Arial", 14), command=return_to_main)
back_button.place(relx=0.9, rely=0.05)  # Top-right corner

row_counter = 1
image_refs = []
for slot, items in slot_items.items():
    if not items:
        continue
    
    slot_item_names = [i['item_name'] for i in items]
    default_item = next((i for i in items if i['forsale'] == 1), items[0])
    
    img_path = f"img/{default_item['item_photo']}"
    if not os.path.exists(img_path):
        img_path = "img/placeholder.jpg"
    
    img = Image.open(img_path).resize((80, 80), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    slot_label = tk.Label(admin_frame, text=f'Slot {slot}', font=("Arial", 20), bg="white")
    slot_label.place(relx=0.2 , rely=0.2 * slot,  anchor="center")
    
    img_label = tk.Label(admin_frame, image=photo, bg="white")
    img_label.image = photo
    img_label.place(relx=0.4, rely=0.2 * slot,  anchor="center")
    image_refs.append(photo)
    
    name_label = tk.Label(admin_frame, text=default_item['item_name'], font=("Arial", 12), bg="white")
    name_label.place(relx=0.6 , rely=0.2 * slot,  anchor="center")
    
    selection_var = tk.StringVar(value=default_item['item_name'])
    dropdown = ttk.Combobox(admin_frame, textvariable=selection_var, values=slot_item_names, width=15, state="readonly")
    dropdown.place(relx=0.8 , rely=0.2 * slot,  anchor="center")
    dropdown.bind("<<ComboboxSelected>>", lambda event, s=slot, dv=selection_var, il=img_label, nl=name_label: update_selection(event, s, dv, il, nl))

# Show main page initially
main_frame.place(relwidth=1, relheight=1)

root.mainloop()
