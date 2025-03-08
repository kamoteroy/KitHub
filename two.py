import os
import tkinter as tk
from PIL import Image, ImageTk
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

goldBG = "#ffce03"
# Create main window
root = tk.Tk()
root.geometry("800x480")
root.title("KitHub")
root.configure(bg=goldBG)

script_dir = os.path.dirname(os.path.abspath(__file__))
imgPrefix = os.path.join(script_dir, "img/")
plus_img = Image.open(imgPrefix + "+.png")
minus_img = Image.open(imgPrefix + "-.png")
replace_img = Image.open(imgPrefix + "replace.png")
backBtn_img = Image.open(imgPrefix + "back.png")
save_img = Image.open(imgPrefix + "save.png")
blank_img = Image.open(imgPrefix + "blank.png")
edit_mode = True
default_widgets = {}
current_selections = {}
original_selections = {}
slot_stock_values = {}
max_stocks = {1: 15, 2: 6, 3: 7, 4: 7}


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

def return_to_main():
    global edit_mode
    edit_mode = True
    if messagebox.askyesno("Confirmation", "Return to Main Page?"):
        for widget in admin_frame.winfo_children():
            if widget not in {saveBtn, backBtn4, refillBtn}:
                widget.destroy()

        admin_frame.place_forget()  # Hide admin page
        main_frame.place(relwidth=1, relheight=1)  # Show main page

def saveBtn_action():
    response = messagebox.askyesno("Changing Items", "Are you sure?")
    if(response):

        for _, item_name in original_selections.items():
            supabase.table("items").update({
                "forsale": 0,
            }).eq("item_name", item_name).execute()

        for slot, item_name in current_selections.items():
            stock_value = slot_stock_values[slot]
            
            # Update the selected item (set forsale=1 and update stocks)
            supabase.table("items").update({
                "forsale": 1,
                "stocks": stock_value
            }).eq("item_name", item_name).execute()

def toggle_refill():
    global edit_mode
    edit_mode = not edit_mode
    for slot, widgets in default_widgets.items():
        dropdown, stocks_label, minus_btn, plus_btn = widgets
        if edit_mode:
            dropdown.place_forget()
            refillBtn.config(text="Replace", anchor="center")
            stocks_label.place(relx=0.8, rely=0.2 * slot, relwidth=0.05, relheight=0.05, anchor="center")
            minus_btn.place(relx=0.75, rely=0.2 * slot, anchor="center")
            plus_btn.place(relx=0.85, rely=0.2 * slot, anchor="center")
        else:
            refillBtn.config(text="Refill", anchor="center")
            dropdown.place(relx=0.8, rely=0.2 * slot, anchor="center")
            stocks_label.place_forget()
            minus_btn.place_forget()
            plus_btn.place_forget()

def adjust_stock(slot, change):
    stocks_label = default_widgets[slot][1] 
    current_stock = int(stocks_label.cget("text"))
    new_stock = current_stock + change
    
    if new_stock < 0:
        new_stock = 0
    if new_stock > max_stocks.get(slot, 0):
        new_stock = max_stocks.get(slot, 0) 

    stocks_label.config(text=str(new_stock))
    slot_stock_values[slot] = new_stock
    minus_btn = default_widgets[slot][2]
    plus_btn = default_widgets[slot][3]
    
    if new_stock <= 0:
        minus_btn.config(state="disabled")
    else:
        minus_btn.config(state="normal")
    
    if new_stock >= max_stocks.get(slot, 0):
        plus_btn.config(state="disabled")
    else:
        plus_btn.config(state="normal")

def populate_admin_page():
    global image_refs, default_widgets, original_selections, current_selections
    image_refs.clear()
    default_widgets.clear()

    def resize_add(event):
        resized_img = plus_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
        event.widget.price_img_resized = ImageTk.PhotoImage(resized_img) 
        event.widget.config(image=event.widget.price_img_resized)

    def resize_minus(event):
        resized_img = minus_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
        event.widget.price_img_resized = ImageTk.PhotoImage(resized_img) 
        event.widget.config(image=event.widget.price_img_resized)
    
    def resize_name_label(event):
        scale_factor = min(event.width, event.height) / 35
        new_font_size = max(1, int(10 * scale_factor))
        resized_img = blank_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
        event.widget.price_img_resized = ImageTk.PhotoImage(resized_img) 
        event.widget.config(image=event.widget.price_img_resized, font=("Arial", new_font_size))

    def resize_stocks_label(event):
        scale_factor = min(event.width, event.height) / 35
        new_font_size = max(1, int(20 * scale_factor))
        event.widget.config(font=("Arial", new_font_size))

    def resize_slot_label(event):
        scale_factor = min(event.width, event.height) / 35
        new_font_size = max(1, int(15 * scale_factor))
        event.widget.config(font=("Arial", new_font_size, 'bold'))
    
    for slot, items in slot_items.items():

        def resize_img_label(event, img_label, img_path):
            img = Image.open(img_path)
            new_width, new_height = event.width, event.height  # Get new dimensions
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            img_label.image_resized = ImageTk.PhotoImage(img_resized)
            img_label.config(image=img_label.image_resized)

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
        
        slot_label = tk.Label(admin_frame, text=f'Slot {slot}', font=("Arial", 15), bg=goldBG, fg='black')
        slot_label.place(relx=0.18 , rely=0.2 * slot, relheight=0.1, relwidth=0.1, anchor="center")
        
        img_label = tk.Label(admin_frame, image=photo, bg="red", bd=2)
        img_label.image = photo
        img_label.place(relx=0.366, rely=0.2 * slot, relheight=0.166, relwidth=0.1, anchor="center")
        image_refs.append(photo)
        
        name_label = tk.Label(admin_frame, text=default_item['item_name'],
                              font=("Helvetica", 10), bg=goldBG, compound="center",
                              wraplength=90)
        name_label.place(relx=0.58 , rely=0.2 * slot, relwidth=0.15, relheight=0.09, anchor="center")
        
        stocks_label = tk.Label(admin_frame, text=default_item['stocks'], font=("Arial", 12))
        stocks_label.place(relx=0.8, rely=0.2 * slot, relwidth=0.05, relheight=0.05, anchor="center")

        selection_var = tk.StringVar(value=default_item['item_name'])
        dropdown = ttk.Combobox(admin_frame, textvariable=selection_var, values=slot_item_names, width=15, state="readonly")
        dropdown.bind("<<ComboboxSelected>>", lambda event, s=slot, dv=selection_var, il=img_label, nl=name_label, sl=stocks_label: update_selection(event, s, dv, il, nl, sl))
        
        minus_btn = tk.Button(admin_frame, text="-", font=("Arial", 14), 
                              command=lambda s=slot: adjust_stock(s, -1),
                              highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG)
        plus_btn = tk.Button(admin_frame, text="+", font=("Arial", 14), 
                             command=lambda s=slot: adjust_stock(s, 1),
                             highlightthickness=0, bd=0, bg= goldBG, activebackground=goldBG)
        
        current_stock = int(stocks_label.cget("text"))  # Convert text to integer
        
        minus_btn.config(state="disabled" if current_stock <= 0 else "normal")
        plus_btn.config(state="disabled" if current_stock >= max_stocks.get(slot, 0) else "normal")
        
        
        minus_btn.place(relx=0.75, rely=0.2 * slot, relwidth=0.04, relheight=0.06, anchor="center")
        plus_btn.place(relx=0.85, rely=0.2 * slot, relwidth=0.04, relheight=0.06, anchor="center")
        default_widgets[slot] = (dropdown, stocks_label, minus_btn, plus_btn)

        name_label.bind("<Configure>", resize_name_label)
        slot_label.bind("<Configure>", resize_slot_label)
        stocks_label.bind("<Configure>", resize_stocks_label)
        plus_btn.bind("<Configure>", lambda event:  resize_add(event))
        minus_btn.bind("<Configure>", lambda event:  resize_minus(event))
        img_label.bind("<Configure>", lambda event, il=img_label, ip=img_path: resize_img_label(event, il, ip))

def show_admin_page():
    refillBtn.config(text="Replace", anchor="center")
    if messagebox.askyesno("Confirmation", "Go to Admin Page?"):
        main_frame.place_forget()
        admin_frame.place(relwidth=1, relheight=1)
        populate_admin_page()

def resize_refillBtn(event):
    global replace_resize
    resized_img = replace_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    replace_resize = ImageTk.PhotoImage(resized_img)
    refillBtn.config(image=replace_resize)

def resize_backBtn4(event):
    global backBtn4_resize
    resized_img = backBtn_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    backBtn4_resize = ImageTk.PhotoImage(resized_img)
    backBtn4.config(image=backBtn4_resize)

def resize_saveBtn(event):
    global saveBtn_resize
    resized_img = save_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    saveBtn_resize = ImageTk.PhotoImage(resized_img)
    saveBtn.config(image=saveBtn_resize)

# Main Page UI
main_frame = tk.Frame(root, bg="#ffce03")
main_frame.place(relwidth=1, relheight=1)

main_label = tk.Label(main_frame, text="Welcome to KitHub", font=("Arial", 20), bg="#ffce03")
main_label.place(relx=0.5, rely=0.3, anchor="center")

admin_button = tk.Button(main_frame, text="Admin Page", font=("Arial", 14), command=show_admin_page)
admin_button.place(relx=0.5, rely=0.5, anchor="center")

# Admin Page UI (Full Screen)
admin_frame = tk.Frame(root, bg=goldBG)

saveBtn = tk.Button(admin_frame, text="OK", font=("Arial", 14), command=saveBtn_action,
                     highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG, anchor="center")
saveBtn.place(relx=0.845 , rely=0.88, relwidth=0.115, relheight=0.08)

backBtn4 = tk.Button(admin_frame, text="Back", font=("Arial", 14), command=return_to_main, 
                     highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG, anchor="center")
backBtn4.place(relx=0.03, rely=0.06, relwidth=0.12, relheight=0.08)

refillBtn = tk.Button(admin_frame, text="Replace", font=("Arial", 14),
                      command=toggle_refill, anchor="center", highlightthickness=0, 
                      bd=0, bg=goldBG, activebackground=goldBG)
refillBtn.place(relx=0.83, rely=0.06, relwidth=0.13, relheight=0.08)

row_counter = 1
image_refs = []

main_frame.place(relwidth=1, relheight=1)

backBtn4.bind("<Configure>", resize_backBtn4)
refillBtn.bind("<Configure>", resize_refillBtn)
saveBtn.bind("<Configure>", resize_saveBtn)

root.mainloop()
