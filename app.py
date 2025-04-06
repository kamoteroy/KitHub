import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from supabase import create_client, Client
from gpiozero import OutputDevice
from time import sleep
import designs
import socket
import os
from datetime import datetime
#import RPi.GPIO as GPIO
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
imgPrefix = os.path.join(script_dir, "img/")

# db
url = "https://gzjxxpeofotelxrzblez.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6anh4cGVvZm90ZWx4cnpibGV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcxMDEwODEsImV4cCI6MjA1MjY3NzA4MX0.R_tCibbHI78B0JYvIja4aNam3tltG3M-eDnmQKn15Cg"
supabase: Client = create_client(url, key)

#maroonBG = "#893a3f"
maroonBG = "#800000"
goldBG = "#ffce03"
maroonGreyed = "#767676"
goldGreyed = "#bfbfbf"
price_img = Image.open(imgPrefix + "price.png")
plus_img = Image.open(imgPrefix + "+.png")
minus_img = Image.open(imgPrefix + "-.png")
calibrate_img = Image.open(imgPrefix + "calibrate.png")
balanceLabel_original = Image.open(imgPrefix + "balance.png")
pinLimit = 6
display_width = 120
display_height = 120
item_pins = [17, 27, 22, 23]
adminCards = ['3', '0005624496'] # add admincards here
item_list = []
all_item_list = {}
all_items = {}
slot_items = {}
cart = {}
defer = False
max_items = 12
lock_img_tk = None
unlock_img_tk = None
is_locked = True
lock_img = Image.open(imgPrefix + "lock.png")
unlock_img = Image.open(imgPrefix + "unlock.png")
blank_img = Image.open(imgPrefix + "blank.png")
replace_img = Image.open(imgPrefix + "replace.png")
refill_img = Image.open(imgPrefix + "refill.png")
edit_mode = True
default_widgets = {}
current_selections = {}
original_selections = {}
slot_stock_values = {}
max_stocks = {1: 6, 2: 7, 3: 6, 4: 15}
row_counter = 1
image_refs = []


def get_items():
    global item_list, all_item_list, all_items, slot_items
    try:
        all_item_list = supabase.table('items').select('*').order('id').execute()
        all_items = all_item_list.data
        slot_items = {}
        for item in all_items:
            slot = item['slot']

            if slot not in slot_items:
                slot_items[slot] = []

            if not any(existing_item['id'] == item['id'] for existing_item in slot_items[slot]):
                slot_items[slot].append(item)
        item_list = supabase.table('items').select('*').eq('forsale', 1).order('slot').execute()
        #print(item_list)
    except Exception as e:
        # print(f"An error occurred: {e}")
        item_list = []


# Main window
root = tk.Tk()
root.geometry("800x480")
root.title('KitHub')
root.iconphoto(True, ImageTk.PhotoImage(Image.open(imgPrefix + "icon.png")))
root.option_add("*TCombobox*Listbox.Font", ("Arial", 17))
#root.attributes('-fullscreen', True)
root.config(cursor="none")
#root.protocol("WM_DELETE_WINDOW", lambda: None)
#root.attributes("-topmost", True)

def disable_buttons():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(cursor="none")

disable_buttons()

input_buffer = ""

def on_input(event):
    global input_buffer
    char = event.char 
    if char.isdigit():
        input_buffer += char
    
    if input_buffer == "0005729339":
        root.destroy()

    if len(input_buffer) > 10:
        input_buffer = ""

root.bind("<KeyPress>", on_input)

style = ttk.Style()
style.theme_use("clam")

def initial_values():
    global total_price, total_items, current_item, decrease_buttons, increase_buttons
    global entered_pin, CORRECT_PIN, userName, all_buttons, buffer
    global balanceModal, balance

    total_price = 0
    total_items = 0
    current_item = 1
    decrease_buttons = []
    increase_buttons = []
    entered_pin = ""
    CORRECT_PIN = ""
    userName = ''
    all_buttons = []
    buffer = ""
    balanceModal = None
    balance = 0
    defer = False

initial_values()

'''GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(item_pins, GPIO.OUT)
for pin in item_pins:
    GPIO.output(pin, GPIO.HIGH)'''


def dispense_items(slotNumber):
    global spring_Duration

    if(slotNumber==17):
        spring_Duration = 2.09
    elif(slotNumber==27):
        spring_Duration = 1.9
    elif(slotNumber==22):
        spring_Duration = 2
    elif(slotNumber==23):
        spring_Duration = 2.11
    
    '''GPIO.output(slotNumber, GPIO.LOW) 
    time.sleep(spring_Duration)
    GPIO.output(slotNumber, GPIO.HIGH)    # Call the increment_item function (replace this with your actual function)'''
    increment_item()

def process_items(values_list):
    print(values_list)
    for index, count in enumerate(values_list):
        for _ in range(count): 
            dispense_items(item_pins[index])
            time.sleep(1)
    deduct()
        
def show_modal(message, duration):
    modal = tk.Toplevel(root)
    modal_width = 200
    modal_height = 50

    app_x = root.winfo_x()
    app_y = root.winfo_y()
    app_width = root.winfo_width()
    app_height = root.winfo_height()

    # Calculate modal position (centered horizontally, at 10% of app height)
    x = max(app_x + (app_width // 2) - (modal_width // 2), app_x)
    start_y = max(app_y, app_y + int(app_height * 0.15) - modal_height)
    end_y = min(app_y + int(app_height * 0.15), app_y + app_height - modal_height)

    modal.geometry(f"{modal_width}x{modal_height}+{x}+{start_y}")
    modal.overrideredirect(True)
    modal.configure(bg="red")

    modal_label = tk.Label(modal, text=message, font=("Arial", 10, "bold"), fg="white", bg="red")
    modal_label.pack(fill="both", expand=True)

    modal.lift()
    modal.attributes("-topmost", True)

    def animate_drop(current_y):
        if current_y < end_y:
            current_y += 10  
            modal.geometry(f"{modal_width}x{modal_height}+{x}+{current_y}")
            modal.after(10, animate_drop, current_y)
        else:
            modal.geometry(f"{modal_width}x{modal_height}+{x}+{end_y}")
            modal.after(duration, modal.destroy)

    animate_drop(start_y)

reconnectingPage = tk.Frame(root, bg="#800000")
reconnectingPage.pack(fill="both", expand=True)
datdat2 = tk.StringVar()                                       
datdat2.set("Reconnecting")

designs.datdat_animation2(datdat2, reconnectingPage)

reconnectingLabel = tk.Label(reconnectingPage, textvariable=datdat2, fg=goldBG, bg=maroonBG, font=("Arial", 24))
reconnectingLabel.place(relx=0.5, rely=0.8, anchor="center")

recon = Image.open(imgPrefix + "no_internet.gif")
reconFrames = []
for frame in range(recon.n_frames):
    recon.seek(frame)
    frame_image = recon.convert("RGBA")
    frame_image = frame_image.resize((280, 200))
    reconFrames.append(ImageTk.PhotoImage(frame_image))

recon_gif = tk.Label(reconnectingPage, image=reconFrames[0], bg="#800000")
recon_gif.place(relx=0.5, rely=0.4, anchor="center")

def recon_animate(frame_index=0):
    recon_gif.config(image=reconFrames[frame_index])
    frame_index = (frame_index + 1) % len(reconFrames)
    root.after(400, recon_animate, frame_index)

recon_animate()


####### START PAGE


startPage = tk.Frame(root, bg=goldBG)

top_section = tk.Frame(startPage, bg=maroonBG)
top_section.place(relx=0, rely=0, relwidth=1, relheight=0.15)

welcomeMsg = tk.Label(top_section, text="Hi! Welcome to", fg="#fff705", bg=maroonBG)
welcomeMsg.place(relx=0.5, rely=0.5, anchor="center")

kithub_logo = tk.Label(startPage, bg=goldBG)
kithub_logo.place(relx=0.5, rely=0.5, relwidth=0.4, relheight=0.6, anchor="center")

bottom_section = tk.Frame(startPage, bg=maroonBG)
bottom_section.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)

datdat = tk.StringVar()                                       
datdat.set("Tap Anywhere to Start")

clickStart = tk.Label(bottom_section, textvariable=datdat, fg="white", bg=maroonBG)
clickStart.place(relx=0.5, rely=0.5, anchor="center")

designs.datdat_animation(datdat, startPage)

current_page = reconnectingPage

def show_selectionPage(event):
    global cart, total_items
    print(cart)
    print(total_items)
    global current_page
    current_page = selectionPage
    startPage.pack_forget()
    selectionPage.pack(fill="both", expand=True)

def bind_all_startPage(frame, event, handler):
    frame.bind(event, handler)
    for child in frame.winfo_children():
        child.bind(event, handler) 

bind_all_startPage(startPage, "<Button-1>", show_selectionPage)
kithub_logo.bind("<Configure>", lambda event: designs.resize_logo(event, kithub_logo))

def navigate_to_startPage():
    global total_price, total_items, cart, current_page
    cart = {key: 0 for key in cart}
    total_price = 0
    total_items = 0

    backBtn.place(relx=0.025, rely=0.04, relwidth=0.12, relheight=0.08)
    
    if 'total_label' in globals():
        total_label.config(text="Total: ₱" + str(total_price))

    for widget in selectionPage.winfo_children():
        if isinstance(widget, tk.Label):
            try:
                if str(widget.cget("text")).isdigit():
                    widget.config(text="0")
            except Exception as e:
                pass
        if isinstance(widget, tk.Button) and widget.cget("text") == "-":
            widget.config(state="disabled")
    
    for btn in decrease_buttons:
        btn.config(state="disabled")

    for btn in increase_buttons:
        btn.config(state="normal")

    if 'checkoutBtn' in globals():
        checkoutBtn.config(state=tk.DISABLED)
    
    if current_page:
        current_page.pack_forget()

    startPage.pack(fill="both", expand=True)
    current_page = startPage

    if 'newOrderBtn' in globals():
        newOrderBtn.place_forget()

def listing_widget(parent, relx, rely, item):
    image = Image.open(imgPrefix + item['item_photo'])
    name = item['item_name']
    price = item['item_price']
    stocks = item['stocks']
    cart[name] = 0


    def on_enter(event):
        canvas.config(highlightbackground="#ed0514", highlightthickness=2)

    def on_leave(event):
        canvas.config(highlightbackground="white", highlightthickness=0.5)
        
    def resize_canvas_image(event):
        canvas_width = event.width
        canvas_height = event.height
        image_resized = image.resize((int(canvas_width * 0.8), int(canvas_height * 0.6)), Image.Resampling.LANCZOS)
        image_photo = ImageTk.PhotoImage(image_resized)
        canvas.image = image_photo
        canvas.coords(image_id, canvas_width / 2, canvas_height / 3)
        canvas.itemconfig(image_id, image=canvas.image)

    def flicker(label, count=2):
        if count > 0:
            current_bg = label.cget("bg")
            new_bg = "red" if current_bg != "red" else "white"
            new_fg = "white" if current_bg != "red" else "black"
            label.config(bg=new_bg, fg=new_fg)
            label.after(200, flicker, label, count - 1)
        else:
            label.config(bg="white", fg="black")
            
    def update_checkoutBtn_state():
        if total_items > 0:
            checkoutBtn.config(state=tk.NORMAL)
        else:
            checkoutBtn.config(state=tk.DISABLED)
    
    def decrease():
        global total_price, total_items, max_items
        current_value = int(valueLabel["text"])
        
        if current_value > 0: 
            total_price -= price
            total_items -=1
            cart[name] -= 1 
            valueLabel.config(text=current_value - 1)
            update_checkoutBtn_state()
            
        if int(valueLabel["text"]) == 0:
            decreaseBtn.config(state="disabled")
        else:
            decreaseBtn.config(state="normal")
            
        total_label.config(text="Total: ₱" + str(total_price))
        if(total_items<max_items):
            increaseBtn.config(state="disable")
        increaseBtn.config(state="normal")
        
    def increase():
        global total_price, total_items
        current_value = int(valueLabel["text"])
        print(stocks)
        if(current_value >= stocks or total_items>=max_items):
            flicker(valueLabel)
        else:
            total_items +=1
            total_price += price
            cart[name] += 1
            valueLabel.config(text=current_value + 1)
            increaseBtn.config(state="normal")
            update_checkoutBtn_state()
            
        total_label.config(text="Total: ₱" + str(total_price))
        if(int(valueLabel["text"])>0):
            decreaseBtn.config(state="normal")
        else:
            decreaseBtn.config(state="disabled")
        if(int(valueLabel["text"])>=stocks or total_items==max_items):
            increaseBtn.config(state="disabled")

    def resize_canvasLabel(event):
        scale_factor = min(event.width, event.height) / 25
        new_font_size = max(1, int(8 * scale_factor)) 
        nameLabel.config(font=("Arial", new_font_size + 5), wraplength=event.width)
        leftLabel.config(font=("Arial", new_font_size + 2), wraplength=event.width)

    def resize_priceLabel(event):
        scale_factor = min(event.width, event.height) / 35
        new_font_size = max(1, int(11 * scale_factor))
        resized_img = price_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
        event.widget.price_img_resized = ImageTk.PhotoImage(resized_img) 
        event.widget.config(image=event.widget.price_img_resized, font=("Arial", new_font_size)) 

    def resize_valueLabel(event):
        scale_factor = min(event.width, event.height) / 34
        new_font_size = max(1, int(11 * scale_factor))
        resized_img = price_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
        event.widget.price_img_resized = ImageTk.PhotoImage(resized_img)
        event.widget.config(font=("Arial", new_font_size))

    def resize_minus(event):
        resized_img = plus_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
        event.widget.price_img_resized = ImageTk.PhotoImage(resized_img) 
        event.widget.config(image=event.widget.price_img_resized)
    
    def resize_add(event):
        resized_img = minus_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
        event.widget.price_img_resized = ImageTk.PhotoImage(resized_img) 
        event.widget.config(image=event.widget.price_img_resized)

    # Create the canvas
    canvas = tk.Canvas(parent, width=display_width + 20, height=display_height + 80, 
                       bg="white", bd=3, highlightthickness=0)
    canvas.place(relx=relx, rely=rely-0.015, relwidth=0.23, relheight=0.55, anchor="center")

    # Add an image to the canvas
    image_resized = image.resize((int(display_width * 0.8), int(display_height * 0.6)), Image.Resampling.LANCZOS)
    canvas.image = ImageTk.PhotoImage(image_resized)
    image_id = canvas.create_image(0, 0, image=canvas.image)
    
    # Bind hover events to the canvas
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Configure>", resize_canvas_image)

    # Create the Item Name label
    leftLabel = tk.Label(parent, text=str(stocks) + " left", anchor="center", bg="white", fg="red")
    leftLabel.place(relx=relx, rely=rely + 0.08, relwidth=0.1, relheight=0.043, anchor="center")
    
    # Create the Item Name label
    nameLabel = tk.Label(parent, text=name, anchor="center", bg="white")
    nameLabel.place(relx=relx, rely=rely + 0.125, relwidth=0.22, relheight=0.06, anchor="center")
    
    # Create the value label
    priceLabel = tk.Label(parent, text='₱' + str(price), font=("Tahoma", 12),
                           anchor="center", compound="center", bg="white", fg="#fff705")
    priceLabel.place(relx=relx, rely=rely + 0.21, relwidth=0.078, relheight=0.084, anchor="center")

    # Create the -1 button
    decreaseBtn = tk.Button(parent, text="-", command=decrease, width=35, highlightthickness=0,
                                bg=goldBG, bd=0, activebackground=goldBG, state="disabled")
    decreaseBtn.place(relx=relx - 0.075, rely=rely + 0.33, relwidth=0.08, relheight=0.12, anchor="center")
    decrease_buttons.append(decreaseBtn)
    
    # Create the +1 button
    increaseBtn = tk.Button(parent, text="+", command=increase, width=35, highlightthickness=0,
                                bg=goldBG, bd=0, activebackground=goldBG)
    increaseBtn.place(relx=relx + 0.075, rely=rely + 0.33, relwidth=0.08, relheight=0.12, anchor="center")
    increase_buttons.append(increaseBtn)
    
    # Create the value label
    valueLabel = tk.Label(parent, text="0", font=("Open Sans", 12), width=4, anchor="center", bg="white")
    valueLabel.place(relx=relx, rely=rely + 0.33, relwidth=0.065, relheight=0.1, anchor="center")

    if stocks <= 0:
        increaseBtn.config(state="disabled")
        canvas.config(bg="gray")  # Turn canvas background to gray
        nameLabel.config(bg="gray")  # Change item name label to gray
        leftLabel.config(bg="gray")  # Change stock label to gray
        priceLabel.config(bg="gray")  # Change stock label to gray

    nameLabel.bind("<Configure>", resize_canvasLabel)
    priceLabel.bind("<Configure>", resize_priceLabel)
    decreaseBtn.bind("<Configure>", resize_add)
    increaseBtn.bind("<Configure>", resize_minus)
    valueLabel.bind("<Configure>", resize_valueLabel)

def show_balanceModal():
    global balanceModal

    top_section.config(bg=maroonGreyed)
    total_label.config(bg=maroonGreyed)
    bottom_section.config(bg=maroonGreyed)
    checkBalanceBtn.config(state="disabled")
    checkoutBtn.config(state="disabled")
    backBtn.config(state="disabled")
    selectItems_label.place_forget()

    if balanceModal:
        return  # If already open, do nothing

    def resize_balanceLabel(event):
        global balanceLabel_resized
        resized_img = balanceLabel_original.resize((event.width, event.height), Image.Resampling.LANCZOS)
        balanceLabel_resized = ImageTk.PhotoImage(resized_img)
        balanceLabel.config(image=balanceLabel_resized)

    balanceModal = tk.Frame(root, bg=maroonBG, bd=2)
    balanceModal.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)

    balanceLabel = tk.Label(balanceModal, text="", bg="#4c6fd3", font=("Arial", 24), anchor="center")
    balanceLabel.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.92, anchor="center")

    result_label = ttk.Label(balanceModal, text="Tap ID to\nCheck Balance", font=("Arial", 10, "bold"), foreground="white", background="#4c6fd3", justify="center")
    result_label.place(relx=0.585, rely=0.41, anchor="center")

    buffer = ""  # Store scanned/input ID

    def fetch_student(idcode):
        response = supabase.table('students').select('*').eq('idcode', idcode).execute()

        if response.data:
            student = response.data[0]
            balance = student.get('balance', 'N/A')

            # Display student info
            result_label.config(
                text=f"Balance: ₱{balance}"
            )
        else:
            result_label.config(text="Student not found.", foreground="white")

    def on_key_press(event):
        nonlocal buffer
        buffer += event.char 

        if event.keysym == "Return":
            if buffer.strip():
                fetch_student(buffer.strip())  
            buffer = ""


    balanceModal.bind("<KeyPress>", on_key_press)
    balanceModal.focus_set()

    def close_balanceModal(event=None):
        global balanceModal

        top_section.config(bg=maroonBG)
        bottom_section.config(bg=maroonBG)
        checkBalanceBtn.config(state="normal")
        backBtn.config(state="normal")
        selectItems_label.place(relx=0.5, rely=0.5, relwidth=0.25, relheight=0.5, anchor="center")
        total_label.config(bg=maroonBG)
        if(total_items != 0):
            checkoutBtn.config(state="normal")
        selectItems_label.update_idletasks()
        
        if balanceModal:
            balanceModal.destroy()
            balanceModal = None

    root.bind("<Button-1>", lambda event: close_balanceModal() if balanceModal and event.widget not in balanceModal.winfo_children() else None)
    root.bind("<Escape>", close_balanceModal)
    balanceLabel.bind("<Configure>", resize_balanceLabel)

def on_key_press(event):
    global buffer
    
    if(balanceModal==None):
        if event.keysym == "Return":
            if buffer.strip():
                if(current_page==tapID_page):
                    go_to_confirmationPage(buffer)
                elif buffer.strip() in adminCards:  
                    show_admin_page() 
                    
            buffer = ""
            return
        else:
            buffer += event.char
        
def go_to_tapID_page():
    global current_page
    current_page = tapID_page
    #print(cart)
    selectionPage.pack_forget()
    tapID_page.pack(fill="both", expand=True)


##### SELECTION PAGE WIDGETS


selectionPage = tk.Frame(root, bg=goldBG)

top_section = tk.Frame(selectionPage, bg=maroonBG)
top_section.place(relx=0, rely=0, relwidth=1, relheight=0.15)

backBtn = tk.Button(
    selectionPage,
    text="Back",
    command=navigate_to_startPage,
    font=("Arial", 12),
    bg=maroonBG,
    fg=maroonBG,
    activebackground=maroonBG,
    activeforeground="white",
    bd=0,
    highlightthickness=0
)
backBtn.place(relx=0.025, rely=0.04, relwidth=0.12, relheight=0.08)

bottom_section = tk.Frame(selectionPage, bg=maroonBG)
bottom_section.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)   
selectItems_label = tk.Label(top_section, bg=maroonBG, font=("Tahoma", 24))
selectItems_label.place(relx=0.5, rely=0.5, relwidth=0.25, relheight=0.65, anchor="center")

def display_item_list():
    if not item_list or not item_list.data:
        placeholder_count = 4
        for index in range(placeholder_count):
            relx = 0.125 + (index * 0.25)
            listing_widget(
                selectionPage,
                relx=relx,
                rely=0.45,
                item={
                    'item_photo': "path_to_placeholder_image.png",
                    'item_name': f"Item {index + 1}",
                    'item_price': 0
                }
            )
    else:
        for index, item in enumerate(item_list.data):
            relx = 0.125 + (index * 0.25)
            listing_widget(selectionPage, relx=relx, rely=0.45, item=item)


if item_list:
    display_item_list()

total_label = tk.Label(selectionPage, text='Total: ₱' + str(total_price), bg=maroonBG, fg="white")
total_label.place(relx=0.6, rely=0.925, relwidth=0.25, relheight=0.1, anchor="center")

checkoutBtn = tk.Button(selectionPage , bg=maroonBG, highlightthickness=0,
                            command=go_to_tapID_page, bd=0, activebackground=maroonBG, state=tk.DISABLED)
checkoutBtn.place(relx=0.85, rely=0.925, relwidth=0.25, relheight=0.1, anchor="center")

checkBalanceBtn = tk.Button(selectionPage , bg=maroonBG, highlightthickness=0,
                            command=show_balanceModal, bd=0, activebackground=maroonBG)
checkBalanceBtn.place(relx=0.175, rely=0.925, relwidth=0.3, relheight=0.1, anchor="center")

backBtn.bind("<Configure>", lambda event: designs.resize_backBtn(event, backBtn))
selectItems_label.bind("<Configure>", lambda event: designs.resize_selectLabel(event, selectItems_label))
total_label.bind("<Configure>", lambda event: designs.resize_totalLabel(event, total_label))
checkoutBtn.bind("<Configure>", lambda event: designs.resize_checkoutBtn(event, checkoutBtn))
checkBalanceBtn.bind("<Configure>", lambda event: designs.resize_checkBalanceBtn(event, checkBalanceBtn))


# Function to check if connected to the internet
def is_connected():
    global item_list, slot_items
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)

        try:
            all_item_list = supabase.table('items').select('*').order('id').execute()
            all_items = all_item_list.data

            if not item_list:
                item_list = supabase.table('items').select('*').eq('forsale', 1).order('slot').execute()
                display_item_list()

            if not slot_items:
                for item in all_items:
                    slot = item['slot']
                    if slot not in slot_items:
                        slot_items[slot] = []
                    slot_items[slot].append(item)

            return True

        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    except (socket.timeout, socket.error):
        return False

def show_reconnectingPage():
    global reconnectingPage, current_page
    if current_page:
        current_page.pack_forget()

    reconnectingPage.pack(fill="both", expand=True)
    current_page = reconnectingPage

def check_connection():
    if is_connected():
        if current_page == reconnectingPage:
            navigate_to_startPage()
            initial_values()
    else:
        show_reconnectingPage()

    root.after(1000, check_connection)

check_connection()

############################################################################ TAP ID PAGE


tapID_page = tk.Frame(root, bg=goldBG)
tapID_label = tk.Label(tapID_page, bg=goldBG, fg="black", justify="center")
tapID_label.place(relx=0.3, rely=0.5, relwidth=0.33, relheight=0.45, anchor="center")

gif_image = Image.open(imgPrefix + "tapID.gif")
frames = []
for frame in range(gif_image.n_frames):
    
    gif_image.seek(frame)
    frame_image = gif_image.convert("RGBA") 
    
    frame_image = frame_image.resize((480, 480))
    
    frame_image = frame_image.convert("RGBA")
    frame_image_tk = ImageTk.PhotoImage(frame_image)
    
    frames.append(frame_image_tk)

tapID_animation = tk.Label(tapID_page, image=frames[0], bg=goldBG)
tapID_animation.place(relx=0.55, rely=0.1, relwidth=0.45, relheight=0.9)

def animate_tapID(frame_index=0):
    tapID_animation.config(image=frames[frame_index])
    
    frame_index = (frame_index + 1) % len(frames)
    
    root.after(50, animate_tapID, frame_index)

animate_tapID()

def go_back_to_selectionPage():
    global current_page
    current_page = selectionPage
    tapID_page.pack_forget()
    cart = [0,0,0,0]
    selectionPage.pack(fill="both", expand=True)

def go_to_confirmationPage(buffer):
    global userData, CORRECT_PIN, balance, current_page, current_item, total_items
    
    userQuery = supabase.table('students').select('*').eq('idcode', buffer).execute()
    
    if(userQuery.data):
        userData = userQuery.data[0]
        if(userData['deferred']):
            messagebox.showinfo("No Balance Left", "You have balance left to pay")
            return
        tapID_page.pack_forget()
        confirmationPage.pack(fill="both", expand=True)
        current_page = confirmationPage
        
        balance = int(userData['balance'])
        CORRECT_PIN = userData['pin']
        greetingsLabel.config(text="Hi, " + userData['fname'] + " " + userData['lname'])
        currentBalance_label.config(text="Current Balance is: " + str(userData['balance']))
        dispensingLabel.config(text=f"Dispensing {current_item}/{total_items}")
    else:
        show_modal("No Account Found", 750)
    
backBtn2 = tk.Button(
    tapID_page,
    text="Back",
    command=go_back_to_selectionPage,
    font=("Arial", 12),
    bg=goldBG,
    activebackground=goldBG,
    bd=0,
    highlightthickness=0
)
backBtn2.place(relx=0.025, rely=0.04, relwidth=0.12, relheight=0.08)

tapID_label.bind("<Configure>", lambda event: designs.resize_tapID_label(event, tapID_label))
backBtn2.bind("<Configure>", lambda event: designs.resize_backBtn2(event, backBtn2))


######################################################## CONFIRMATION PAGE


def go_to_dispensePage():
    global current_page
    current_page = dispensePage
    confirmationPage.pack_forget() 
    dispensePage.pack(fill="both", expand=True)
    
    root.update_idletasks()
    root.after(1500, wait)

def wait():
    items_to_dispense = extract_values(cart)
    print(cart)
    process_items(items_to_dispense)

def extract_values(item_dict):
    return list(item_dict.values())

def button_click(number):
    global entered_pin
    current_length = len(entered_pin)
    
    if current_length < pinLimit:
        entered_pin += number
        pinDisplay["text"] = "*" * len(entered_pin)

def clear_pin():
    global entered_pin
    entered_pin = ""
    pinDisplay["text"] = ""

def clear_last_character():
    global entered_pin
    current = pinDisplay["text"]
    entered_pin = entered_pin[:-1]
    pinDisplay["text"] = current[:-1]

def check_pin():
    global balance, defer
    if entered_pin != CORRECT_PIN:
        #messagebox.showerror("Incorrect PIN.", "Try again.")
        show_modal("Incorrect PIN\nPlease Try again.", 1500)
        clear_pin()
        return
        
    if balance < total_price:
        defer = messagebox.askyesno("Insufficient Balance", "Payment difference will be added to your tuition")
        if not defer:
            clear_pin()
            return

    clear_pin()
    for item_name, cart_quantity in cart.items():
        if cart_quantity > 0:
            matching_item = next((item for item in item_list.data if item['item_name'] == item_name), None)

            if matching_item:
                new_stock = matching_item['stocks'] - cart_quantity

                supabase.table('items').update({'stocks': new_stock}).eq('id', matching_item['id']).execute()
                #print(f"Updated {item_name}: New stock is {new_stock}")

                for _ in range(cart_quantity):
                    supabase.table('transactions').insert({
                        'student': userData['idnum'],
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'type': item_name,
                        'amount': matching_item['item_price']
                    }).execute()

                    #print(f"Inserted transaction for {item_name} at price {matching_item['item_price']}")
    
    go_to_dispensePage()

def go_back_to_tapIDPage():
    global current_page
    current_page = tapID_page
    clear_pin()
    confirmationPage.pack_forget() 
    tapID_page.pack(fill="both", expand=True)

def deduct():
    global balance, defer
    if defer:
        defer_response = supabase.table('students').update({'balance': 0, 'forwardBalance': total_price - balance, 'deferred': True}).eq('idcode', userData['idcode']).execute()
    else:
        defer_response = supabase.table('students').update({'balance': balance - total_price}).eq('idcode', userData['idcode']).execute()
    print(defer_response)
    defer = False
    balance = 0

####### CONFIRMATION PAGE WIDGETS


confirmationPage = tk.Frame(root, bg=goldBG)

backBtn3 = tk.Button(confirmationPage, text="Back", font=("Arial", 12), bg=goldBG, highlightthickness=0, command=go_back_to_tapIDPage, fg='white', activebackground=goldBG, bd=0)
backBtn3.place(relx=0.025, rely=0.04, relwidth=0.12, relheight=0.08)

greetingsLabel = tk.Label(confirmationPage, bg=goldBG, justify="center")
greetingsLabel.place(relx=0.3, rely=0.25, anchor="center")
currentBalance_label = tk.Label(confirmationPage, bg=goldBG, justify="center")
currentBalance_label.place(relx=0.3, rely=0.35, anchor="center")
enterPinLabel = tk.Label(confirmationPage, text="Enter\nyour pin", bg=goldBG, justify="center")
enterPinLabel.place(relx=0.3, rely=0.55, anchor="center")
errorLabel = tk.Label(confirmationPage, text="Not you? Click Here to Report", bg=goldBG, justify="center", font=("Tahoma", 9, "bold"))
errorLabel.place(relx=0.3, rely=0.9, anchor="center")

# Calculator frame
calcuFrame = tk.Frame(confirmationPage, bg=maroonBG, bd=10, highlightbackground="yellow", highlightcolor="yellow")
calcuFrame.place(relx=0.55, rely=0.05, relwidth=0.4, relheight=0.9)
pinDisplay = tk.Label(calcuFrame, text="", bg=maroonBG, font=("Arial", 24),compound="center")
pinDisplay.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.2)
numpadFrame = tk.Frame(calcuFrame, bg=maroonBG)
numpadFrame.place(relx=0.05, rely=0.3, relwidth=1, relheight=0.65)

# Bind the resize events
pinDisplay.bind("<Configure>", lambda event: designs.resize_pinframe(event, pinDisplay))
backBtn3.bind("<Configure>", lambda event: designs.resize_backBtn3(event, backBtn3))

# NUMPAD
buttons = [
    ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
    ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
    ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
]

for (text, row, col) in buttons:
    button = tk.Button(numpadFrame, text=text, font=("Arial", 18), highlightthickness=0, bg="lightgray", command=lambda num=text: button_click(num))
    button.place(relx=col * 0.3, rely=row * 0.25, relwidth=0.30, relheight=0.25)
    all_buttons.append(button)

clearBtn = tk.Button(numpadFrame, text="✘", font=("Arial", 20), highlightthickness=0,  bg="red", fg="white", command=clear_last_character)
clearBtn.place(relx=0, rely=0.75, relwidth=0.3, relheight=0.25)

zeroBtn = tk.Button(numpadFrame, text="0", font=("Arial", 18), highlightthickness=0, bg="lightgray", command=lambda: button_click("0"))
zeroBtn.place(relx=0.3, rely=0.75, relwidth=0.3, relheight=0.25)

enterBtn = tk.Button(numpadFrame, text="✔", font=("Arial", 20), highlightthickness=0, bg="green", fg="white", command=check_pin)
enterBtn.place(relx=0.6, rely=0.75, relwidth=0.3, relheight=0.25)


############### DISPENSE PAGE WIDGETS


dispensePage = tk.Frame(root, bg='yellow')

gif = Image.open(imgPrefix + "vending.gif")
dispenseFrames = []

for frame in range(gif.n_frames):
    gif.seek(frame)
    frame_image = gif.convert("RGBA")
    frame_image = frame_image.resize((800, 480))
    dispenseFrames.append(ImageTk.PhotoImage(frame_image))

gif_label = tk.Label(dispensePage, image=dispenseFrames[0], bg='yellow')
gif_label.place(relx=0.5, rely=0.5, anchor="center")

def dispense_animate(frame_index=0):
    gif_label.config(image=dispenseFrames[frame_index])
    frame_index = (frame_index + 1) % len(dispenseFrames)
    root.after(50, dispense_animate, frame_index)

dispense_animate()

dispensingLabel = tk.Label(dispensePage, text=f"Dispensing {current_item}/{total_items}", font=("Arial", 18), bg="#ffca05")
dispensingLabel.place(relx=0.5, rely=0.9, relwidth=0.18, relheight=0.1, anchor="center")
dispensingLabel.lift()

newOrderBtn = tk.Button(
    dispensePage, text="New Order", highlightthickness=0,
    command=navigate_to_startPage, bd=0, bg="#ffca05", fg="white",
    font=("Arial", 15, "bold"), activebackground=maroonBG
)

def show_Btn(opacity=0):
    if opacity > 1.0:  # Stop when fully visible
        return
    
    r = int(255 - (255 - 128) * opacity)
    g = int(255 - (255 - 0) * opacity)
    b = int(255 - (255 - 0) * opacity)
    new_bg = f"#{r:02x}{g:02x}{b:02x}"
    
    newOrderBtn.config(bg=new_bg, activebackground=new_bg)

    root.after(100, lambda: show_Btn(opacity + 0.05))  # Slower transition

def increment_item():
    global current_item, total_items
    '''print("Current Item: ")
    print(current_item)
    print("Total Item: ")
    print(total_items)'''
    if current_item < total_items:
        current_item += 1
        dispensingLabel.config(text=f"Dispensing {current_item}/{total_items}")
        dispensingLabel.update_idletasks()
    else:
        dispensingLabel.config(text="Done")
        dispensingLabel.update_idletasks()
        current_item = 1
        newOrderBtn.place(relx=0.5, rely=0.1, relwidth=0.3, relheight=0.1, anchor="center")
        show_Btn()
        get_items()
        display_item_list()
        
widgets = [
    (welcomeMsg, "Arial", 21),
    (reconnectingLabel, "Arial", 18),
    (clickStart, "Arial", 18),
    (greetingsLabel, "Tahoma", 28, "bold"),
    (currentBalance_label, "Tahoma", 15, "bold"),
    (enterPinLabel, "Tahoma", 35, "bold"),
    (errorLabel, "Tahoma", 9, "bold"),
    (zeroBtn, "Tahoma", 18),
    (enterBtn, "Tahoma", 18),
    (clearBtn, "Tahoma", 18),
    (dispensingLabel, "Tahoma", 15),
    (newOrderBtn, "Tahoma", 18),
]
startPage.bind("<Configure>", lambda event: designs.resize_labels(event, widgets, all_buttons))
dispensePage.bind("<Configure>", lambda event: designs.resize_labels(event, widgets, all_buttons))
confirmationPage.bind("<Configure>", lambda event: designs.resize_labels(event, widgets, all_buttons))


################# ADMIN PAGE

replace_img_tk = ImageTk.PhotoImage(replace_img)
refill_img_tk = ImageTk.PhotoImage(refill_img)


def show_admin_page():
    global current_page
    if messagebox.askyesno("Confirmation", "Go to Admin Page?"):
        current_page.pack_forget() 
        refillBtn.config(text="Replace", anchor="center")
        adminPage.pack(fill="both", expand=True)
        current_page = adminPage
        populate_admin_page()

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
    #print(f"Slot {slot} changed to {selected_name}")
    
    if original_selections.get(slot) != selected_name:
        print(f"Change detected in Slot {slot}: {original_selections[slot]} -> {selected_name}")

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

def recalibrate(pin):
    print(pin)

    '''GPIO.output(pin, GPIO.LOW) 
    time.sleep(0.1)
    GPIO.output(pin, GPIO.HIGH)'''

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
    
    def resize_calibrate(event):
        resized_img = calibrate_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
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
        
        slot_stock_values[slot] = int(default_item['stocks'])
        
        script_dir = os.path.dirname(os.path.abspath(__file__))

        img_path = os.path.join(script_dir, "img", default_item["item_photo"])

        if not os.path.exists(img_path):
            img_path = os.path.join(script_dir, "img", "placeholder.png")
        
        img = Image.open(img_path).resize((80, 80), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        slot_label = tk.Label(adminPage, text=f'Slot {slot}', font=("Arial", 15), bg=goldBG, fg='black')
        slot_label.place(relx=0.1 , rely=0.2 * slot, relheight=0.1, relwidth=0.1, anchor="center")
        
        img_label = tk.Label(adminPage, image=photo, bg="red", bd=2)
        img_label.image = photo
        img_label.place(relx=0.27, rely=0.2 * slot, relheight=0.166, relwidth=0.1, anchor="center")
        image_refs.append(photo)
        
        name_label = tk.Label(adminPage, text=default_item['item_name'],
                              font=("Helvetica", 10), bg=goldBG, compound="center",
                              wraplength=90)
        name_label.place(relx=0.46 , rely=0.2 * slot, relwidth=0.15, relheight=0.09, anchor="center")
        
        stocks_label = tk.Label(adminPage, text=default_item['stocks'], bg='white', font=("Arial", 12))
        stocks_label.place(relx=0.71, rely=0.2 * slot, relwidth=0.07, relheight=0.07, anchor="center")

        selection_var = tk.StringVar(value=default_item['item_name'])
        dropdown = ttk.Combobox(adminPage, textvariable=selection_var, values=slot_item_names, width=15, state="readonly")
        dropdown.bind("<<ComboboxSelected>>", lambda event, s=slot, dv=selection_var, il=img_label, nl=name_label, sl=stocks_label: update_selection(event, s, dv, il, nl, sl))
        
        minus_btn = tk.Button(adminPage, text="-", font=("Arial", 14), 
                              command=lambda s=slot: adjust_stock(s, -1),
                              highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG)
        plus_btn = tk.Button(adminPage, text="+", font=("Arial", 14), 
                             command=lambda s=slot: adjust_stock(s, 1),
                             highlightthickness=0, bd=0, bg= goldBG, activebackground=goldBG)
        
        current_stock = int(stocks_label.cget("text"))  # Convert text to integer
        
        minus_btn.config(state="disabled" if current_stock <= 0 else "normal")
        plus_btn.config(state="disabled" if current_stock >= max_stocks.get(slot, 0) else "normal")
        minus_btn.place(relx=0.63, rely=0.2 * slot, relwidth=0.08, relheight=0.12, anchor="center")
        plus_btn.place(relx=0.79, rely=0.2 * slot, relwidth=0.08, relheight=0.12, anchor="center")
        default_widgets[slot] = (dropdown, stocks_label, minus_btn, plus_btn)

        calibrateBtn = tk.Button(adminPage, text="Calibrate", font=("Arial", 10),
                                command=lambda s=slot: recalibrate(item_pins[s-1]),
                                highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG)
        calibrateBtn.place(relx=0.9, rely=0.2 * slot, relwidth=0.08, relheight=0.12, anchor="center")

        name_label.bind("<Configure>", resize_name_label)
        slot_label.bind("<Configure>", resize_slot_label)
        stocks_label.bind("<Configure>", resize_stocks_label)
        plus_btn.bind("<Configure>", lambda event:  resize_add(event))
        minus_btn.bind("<Configure>", lambda event:  resize_minus(event))
        calibrateBtn.bind("<Configure>", lambda event:  resize_calibrate(event))
        img_label.bind("<Configure>", lambda event, il=img_label, ip=img_path: resize_img_label(event, il, ip))

def toggle_refill():
    global edit_mode
    edit_mode = not edit_mode

    for slot, widgets in default_widgets.items():
        dropdown, stocks_label, minus_btn, plus_btn = widgets
        
        if edit_mode:
            dropdown.place_forget()
            refillBtn.config(text="Replace", anchor="center", image=replace_img_tk)
            stocks_label.place(relx=0.71, rely=0.2 * slot, relwidth=0.07, relheight=0.07, anchor="center")
            minus_btn.place(relx=0.63, rely=0.2 * slot, relwidth=0.08, relheight=0.12, anchor="center")
            plus_btn.place(relx=0.79, rely=0.2 * slot, relwidth=0.08, relheight=0.12, anchor="center")
        else:
            refillBtn.config(text="Refill", anchor="center", image=refill_img_tk)
            dropdown.place(relx=0.71, rely=0.2 * slot, relwidth=0.2, relheight=0.12, anchor="center")
            stocks_label.place_forget()
            minus_btn.place_forget()
            plus_btn.place_forget()

def saveBtn_action():
    global current_selections, original_selections, cart
    response = messagebox.askyesno("Changing Items", "Are you sure?")
    if(response):
        for _, item_name in original_selections.items():
            supabase.table("items").update({
                "forsale": 0,
            }).eq("item_name", item_name).execute()

        for slot, item_name in current_selections.items():
            print(item_name)
            print(slot_stock_values[slot])
            stock_value = slot_stock_values[slot]
            
            supabase.table("items").update({
                "forsale": 1,
                "stocks": stock_value
            }).eq("item_name", item_name).execute()
        cart = {}
        get_items()
        display_item_list()
        return_to_main()

def return_to_main():
    global edit_mode
    edit_mode = True
    for widget in adminPage.winfo_children():
        if widget not in {saveBtn, backBtn4, refillBtn, unlockBtn, powerBtn}:
            widget.destroy()

    adminPage.place_forget()
    navigate_to_startPage()

#GPIO.output(24, GPIO.LOW)

def toggle_lock():
    global is_locked

    is_locked = not is_locked 
    # Toggle GPIO based on lock state
    '''if is_locked:
        GPIO.output(24, GPIO.LOW)  # Lock (ON)
    else:
        GPIO.output(24, GPIO.HIGH)  # Unlock (OFF)'''

    unlockBtn.config(image=unlock_img_tk if not is_locked else lock_img_tk)
    unlockBtn.image = unlock_img_tk if not is_locked else lock_img_tk

def resize_unlockBtn(event):
    global lock_img_tk, unlock_img_tk

    resized_lock = lock_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    resized_unlock = unlock_img.resize((event.width, event.height), Image.Resampling.LANCZOS)

    lock_img_tk = ImageTk.PhotoImage(resized_lock)
    unlock_img_tk = ImageTk.PhotoImage(resized_unlock)

    unlockBtn.config(image=lock_img_tk if is_locked else unlock_img_tk)
    unlockBtn.image = lock_img_tk if is_locked else unlock_img_tk

def resize_refillBtn(event):
    global refillBtn_resized
    new_img = (replace_img if edit_mode else refill_img).resize((event.width, event.height), Image.Resampling.LANCZOS)
    refillBtn_resized = ImageTk.PhotoImage(new_img)
    refillBtn.config(image=refillBtn_resized)

def turn_off():
    q = messagebox.askyesno("Turn Off", "Turn off the app?")
    if(q):
        root.destroy()

adminPage = tk.Frame(root, bg=goldBG)

saveBtn = tk.Button(adminPage, text="OK", font=("Arial", 14), command=saveBtn_action,
                     highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG, anchor="center")
saveBtn.place(relx=0.845 , rely=0.88, relwidth=0.115, relheight=0.08)

backBtn4 = tk.Button(adminPage, text="Back", font=("Arial", 14), command=return_to_main, 
                     highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG, anchor="center")
backBtn4.place(relx=0.025, rely=0.04, relwidth=0.12, relheight=0.08)

refillBtn = tk.Button(adminPage, text="Replace", font=("Arial", 14),
                      command=toggle_refill, anchor="center", highlightthickness=0, 
                      bd=0, bg=goldBG, activebackground=goldBG)
refillBtn.place(relx=0.83, rely=0.04, relwidth=0.13, relheight=0.08)

unlockBtn = tk.Button(adminPage, text="Back", font=("Arial", 14), command=toggle_lock, 
                     highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG, anchor="center")
#unlockBtn.place(relx=0.1, rely=0.88, relwidth=0.1, relheight=0.08)

powerBtn = tk.Button(adminPage, text="Back", font=("Arial", 14), command=turn_off, 
                     highlightthickness=0, bd=0, bg=goldBG, activebackground=goldBG, anchor="center")
powerBtn.place(relx=0.06, rely=0.865, relwidth=0.0625, relheight=0.104)

backBtn4.bind("<Configure>", lambda event: designs.resize_backBtn4(event, backBtn4))
powerBtn.bind("<Configure>", lambda event: designs.resize_powerBtn(event, powerBtn))
saveBtn.bind("<Configure>", lambda event: designs.resize_saveBtn(event, saveBtn))
unlockBtn.bind("<Configure>", resize_unlockBtn)
refillBtn.bind("<Configure>", resize_refillBtn)
root.bind("<Key>", on_key_press)

root.mainloop()