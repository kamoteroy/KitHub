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

edit_mode = True
default_widgets = {}
current_selections = {}
original_selections = {}


# Function to update image and name dynamically
def update_selection(event, slot, dropdown_var, image_label, name_label, stocks_label):
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
        stocks_label.config(text=selected_item['stocks'])
    current_selections[slot] = selected_name
    print(f"Slot {slot} changed to {selected_name}")
    
    # Compare with original value
    if original_selections.get(slot) != selected_name:
        print(f"Change detected in Slot {slot}: {original_selections[slot]} -> {selected_name}")

# Function to return to Main Page
def return_to_main():
    global edit_mode
    edit_mode = True
    if messagebox.askyesno("Confirmation", "Return to Main Page?"):
        # Remove only dynamically created widgets
        for widget in admin_frame.winfo_children():
            if widget not in {ok_button, back_button, refill_button}:
                widget.destroy()

        admin_frame.place_forget()  # Hide admin page
        main_frame.place(relwidth=1, relheight=1)  # Show main page


# Function for OK button action
def ok_button_action():
    messagebox.askyesno("Confirmation", "Are you sure?")
    print(slot_stock_values)
    print(current_selections)

max_stocks = {1: 15, 2: 6, 3: 7, 4: 7}
def adjust_stock(slot, change):
    """Adjust the stock for the given slot and update the UI."""
    
    # Get the current stocks label for this slot
    stocks_label = default_widgets[slot][1]  # stocks_label is the second element in the default_widgets tuple
    
    # Get the current stock value from the text of the stocks_label
    current_stock = int(stocks_label.cget("text"))  # Convert the text to integer
    
    # Apply the change (either +1 or -1)
    new_stock = current_stock + change
    
    # Ensure the stock stays within valid bounds (0 to max_stocks for the slot)
    if new_stock < 0:
        new_stock = 0  # Can't have negative stocks
    if new_stock > max_stocks.get(slot, 0):
        new_stock = max_stocks.get(slot, 0)  # Can't exceed max_stocks for that slot
    
    # Update the stock label text to reflect the new stock value
    stocks_label.config(text=str(new_stock))  # Update the displayed stock value
    
    # Get the minus and plus buttons
    minus_btn = default_widgets[slot][2]  # minus button is the third element in the default_widgets tuple
    plus_btn = default_widgets[slot][3]  # plus button is the fourth element in the default_widgets tuple
    
    # Disable "-" button if stock is 0
    if new_stock <= 0:
        minus_btn.config(state="disabled")
    else:
        minus_btn.config(state="normal")
    
    # Disable "+" button if stock exceeds max_stocks
    if new_stock >= max_stocks.get(slot, 0):
        plus_btn.config(state="disabled")
    else:
        plus_btn.config(state="normal")

def toggle_refill():
    global edit_mode
    edit_mode = not edit_mode
    for slot, widgets in default_widgets.items():
        dropdown, stocks_label, minus_btn, plus_btn = widgets
        if edit_mode:
            dropdown.place_forget()
            refill_button.config(text="Replace", anchor="center")
            stocks_label.place(relx=0.8, rely=0.2 * slot, anchor="center")
            minus_btn.place(relx=0.75, rely=0.2 * slot, anchor="center")
            plus_btn.place(relx=0.85, rely=0.2 * slot, anchor="center")
        else:
            refill_button.config(text="Refill", anchor="center")
            dropdown.place(relx=0.8333, rely=0.2 * slot, anchor="center")
            minus_btn.place_forget()
            plus_btn.place_forget()

# Create a dictionary to store the stock values for each slot
slot_stock_values = {}

def adjust_stock(slot, change):
    """Adjust the stock for the given slot and update the UI."""
    
    # Get the current stocks label for this slot
    stocks_label = default_widgets[slot][1]  # stocks_label is the second element in the default_widgets tuple
    
    # Get the current stock value from the text of the stocks_label
    current_stock = int(stocks_label.cget("text"))  # Convert the text to integer
    
    # Apply the change (either +1 or -1)
    new_stock = current_stock + change
    
    # Ensure the stock stays within valid bounds (0 to max_stocks for the slot)
    if new_stock < 0:
        new_stock = 0  # Can't have negative stocks
    if new_stock > max_stocks.get(slot, 0):
        new_stock = max_stocks.get(slot, 0)  # Can't exceed max_stocks for that slot
    
    # Update the stock label text to reflect the new stock value
    stocks_label.config(text=str(new_stock))  # Update the displayed stock value
    
    # Store the updated stock value in the slot_stock_values dictionary
    slot_stock_values[slot] = new_stock  # Save the updated stock value for this slot
    
    # Get the minus and plus buttons
    minus_btn = default_widgets[slot][2]  # minus button is the third element in the default_widgets tuple
    plus_btn = default_widgets[slot][3]  # plus button is the fourth element in the default_widgets tuple
    
    # Disable "-" button if stock is 0
    if new_stock <= 0:
        minus_btn.config(state="disabled")
    else:
        minus_btn.config(state="normal")
    
    # Disable "+" button if stock exceeds max_stocks
    if new_stock >= max_stocks.get(slot, 0):
        plus_btn.config(state="disabled")
    else:
        plus_btn.config(state="normal")

def populate_admin_page():
    global image_refs, default_widgets, original_selections, current_selections
    image_refs.clear()
    default_widgets.clear()
    
    for slot, items in slot_items.items():
        if not items:
            continue
        
        slot_item_names = [i['item_name'] for i in items]
        default_item = next((i for i in items if i['forsale'] == 1), items[0])
        original_selections[slot] = default_item['item_name']
        current_selections[slot] = default_item['item_name']
        
        # Initialize stock value for the slot (this is where slot's stock is initially set)
        slot_stock_values[slot] = int(default_item['stocks'])  # Store the stock value in the dictionary
        
        img_path = f"img/{default_item['item_photo']}"
        if not os.path.exists(img_path):
            img_path = "img/placeholder.jpg"
        
        img = Image.open(img_path).resize((80, 80), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        slot_label = tk.Label(admin_frame, text=f'Slot {slot}', font=("Arial", 15), bg="white")
        slot_label.place(relx=0.166 , rely=0.2 * slot, anchor="center")
        
        img_label = tk.Label(admin_frame, image=photo, bg="white")
        img_label.image = photo
        img_label.place(relx=0.366, rely=0.2 * slot, anchor="center")
        image_refs.append(photo)
        
        name_label = tk.Label(admin_frame, text=default_item['item_name'], font=("Arial", 12), bg="white")
        name_label.place(relx=0.55 , rely=0.2 * slot, anchor="center")
        
        stocks_label = tk.Label(admin_frame, text=default_item['stocks'], font=("Arial", 12), bg="white")
        
        selection_var = tk.StringVar(value=default_item['item_name'])
        dropdown = ttk.Combobox(admin_frame, textvariable=selection_var, values=slot_item_names, width=15, state="readonly")
        dropdown.bind("<<ComboboxSelected>>", lambda event, s=slot, dv=selection_var, il=img_label, nl=name_label, sl=stocks_label: update_selection(event, s, dv, il, nl, sl))
        
        minus_btn = tk.Button(admin_frame, text="-", font=("Arial", 14), command=lambda s=slot: adjust_stock(s, -1))
        plus_btn = tk.Button(admin_frame, text="+", font=("Arial", 14), command=lambda s=slot: adjust_stock(s, 1))
        
        current_stock = int(stocks_label.cget("text"))  # Convert text to integer
        
        # Disable the "-" button if stock is 0, else enable
        minus_btn.config(state="disabled" if current_stock <= 0 else "normal")

        # Disable the "+" button if stock exceeds max_stocks, else enable
        plus_btn.config(state="disabled" if current_stock >= max_stocks.get(slot, 0) else "normal")
        
        stocks_label.place(relx=0.8, rely=0.2 * slot, anchor="center")
        minus_btn.place(relx=0.75, rely=0.2 * slot, anchor="center")
        plus_btn.place(relx=0.85, rely=0.2 * slot, anchor="center")
        default_widgets[slot] = (dropdown, stocks_label, minus_btn, plus_btn)



def show_admin_page():
    refill_button.config(text="Replace", anchor="center")
    if messagebox.askyesno("Confirmation", "Go to Admin Page?"):
        main_frame.place_forget()
        admin_frame.place(relwidth=1, relheight=1)
        populate_admin_page()

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
refill_button = tk.Button(admin_frame, text="Replace", font=("Arial", 14), command=toggle_refill, anchor="center")
refill_button.place(relx=0.5, rely=0.05, relwidth=0.1)

row_counter = 1
image_refs = []

main_frame.place(relwidth=1, relheight=1)

root.mainloop()
