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

# Get the directory where app.py is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the img directory
imgPrefix = os.path.join(script_dir, "img/")

# Replace with your Supabase URL and API key
url = "https://gzjxxpeofotelxrzblez.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6anh4cGVvZm90ZWx4cnpibGV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzcxMDEwODEsImV4cCI6MjA1MjY3NzA4MX0.R_tCibbHI78B0JYvIja4aNam3tltG3M-eDnmQKn15Cg"

# Create a Supabase client
supabase: Client = create_client(url, key)

#maroonBG = "#893a3f"
maroonBG = "#800000"
goldBG = "#ffce03"
maroonGreyed = "#767676"
goldGreyed = "#bfbfbf"
price_img = Image.open(imgPrefix + "price.png")
plus_img = Image.open(imgPrefix + "+.png")
minus_img = Image.open(imgPrefix + "-.png")
balanceLabel_original = Image.open(imgPrefix + "balance.png")
pinLimit = 6
max_items = 3
display_width = 120
display_height = 120
item_pins = [17, 27, 22, 23]
spring_Duration = 1.5
item_list = None
cart = {}

def get_items():
    global item_list
    try:
        item_list = supabase.table('items').select('*').eq('forsale', 1).order('id').execute()
        print(item_list)
    except Exception as e:
        print(f"An error occurred: {e}")
        item_list = []

get_items()

# Main window
root = tk.Tk()
root.geometry("800x480")
root.title('KitHub')
root.iconphoto(True, ImageTk.PhotoImage(Image.open(imgPrefix + "icon.png")))
#root.attributes('-fullscreen', True)  # Fullscreen mode
'''root.config(cursor="none")
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.attributes("-topmost", True)

# Custom key to close the app
def close_app(event):
    root.destroy()

root.bind("<Control-Shift-Q>", close_app)'''

input_buffer = ""  # A buffer to store input characters

def on_input(event):
    global input_buffer
    char = event.char  # Capture the character
    if char.isdigit():  # Only handle digits
        input_buffer += char
    
    # Check if the buffer contains the target number
    if input_buffer == "0005729339":
        root.destroy()  # Close the app

    # Clear the buffer if it gets too long
    if len(input_buffer) > 10:  # Assuming 10 is the max length
        input_buffer = ""

# Bind all key events to on_input
root.bind("<KeyPress>", on_input)


style = ttk.Style()
style.theme_use("clam")

def initial_values():
    global total_price, total_items, current_item, decrease_buttons, increase_buttons
    global entered_pin, CORRECT_PIN, userName, all_buttons, buffer
    global balanceModal, balance

    # Reset all global variables to their default values
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

initial_values()

def dispense_items(slotNumber):
    
    """Activates the relay on the specified slotNumber for the duration.
    springMotor = OutputDevice(slotNumber)
    try:
        springMotor.on()
        sleep(spring_Duration)
    finally:
        springMotor.off()"""
    increment_item()

def process_items(values_list):
    """Loops through values_list and triggers dispense_items for each non-zero value."""
    for index, count in enumerate(values_list):
        for _ in range(count):  # Run multiple times based on the count
            dispense_items(item_pins[index])
        
def show_modal(message, duration):
    # Create the modal
    modal = tk.Toplevel(root)
    modal_width = 200
    modal_height = 50

    # Get app window position and size
    app_x = root.winfo_x()
    app_y = root.winfo_y()
    app_width = root.winfo_width()
    app_height = root.winfo_height()

    # Calculate modal position (centered horizontally, at 10% of app height)
    x = max(app_x + (app_width // 2) - (modal_width // 2), app_x)  # Center horizontally within the app
    start_y = max(app_y, app_y + int(app_height * 0.15) - modal_height)  # Start just above 10% of app height
    end_y = min(app_y + int(app_height * 0.15), app_y + app_height - modal_height)  # End at 10% of app height

    # Set modal geometry and appearance
    modal.geometry(f"{modal_width}x{modal_height}+{x}+{start_y}")
    modal.overrideredirect(True)  # Remove window decorations
    modal.configure(bg="red")

    # Add modal content
    modal_label = tk.Label(modal, text=message, font=("Arial", 10, "bold"), fg="white", bg="red")
    modal_label.pack(fill="both", expand=True)

    # Ensure the modal stays on top
    modal.lift()
    modal.attributes("-topmost", True)

    # Define the animation function
    def animate_drop(current_y):
        if current_y < end_y:
            # Move the modal down
            current_y += 10  
            modal.geometry(f"{modal_width}x{modal_height}+{x}+{current_y}")
            modal.after(10, animate_drop, current_y)
        else:
            # Ensure modal stops at the exact end position
            modal.geometry(f"{modal_width}x{modal_height}+{x}+{end_y}")
            # Automatically close the modal after n seconds
            modal.after(duration, modal.destroy)

    # Start the animation
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
top_section.place(relx=0, rely=0, relwidth=1, relheight=0.2)

welcomeMsg = tk.Label(top_section, text="Hi! Welcome to", fg="#fff705", bg=maroonBG)
welcomeMsg.place(relx=0.5, rely=0.5, anchor="center")

kithub_logo = tk.Label(startPage, bg=goldBG)
kithub_logo.place(relx=0.5, rely=0.5, relwidth=0.4, relheight=0.6, anchor="center")

bottom_section = tk.Frame(startPage, bg=maroonBG)
bottom_section.place(relx=0, rely=0.8, relwidth=1, relheight=0.2)

datdat = tk.StringVar()                                       
datdat.set("Click Anywhere to Start")

clickStart = tk.Label(bottom_section, textvariable=datdat, fg="white", bg=maroonBG)
clickStart.place(relx=0.5, rely=0.5, anchor="center")

designs.datdat_animation(datdat, startPage)

current_page = reconnectingPage

def show_selectionPage(event):
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
        global total_price, total_items
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
        if(total_items>=max_items):
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

    def resize_canvasLabel(event):
        scale_factor = min(event.width, event.height) / 21
        new_font_size = max(1, int(8 * scale_factor)) 
        nameLabel.config(font=("Arial", new_font_size), wraplength=event.width)

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
    canvas.place(relx=relx, rely=rely+0.01, relwidth=0.2, relheight=0.5, anchor="center")

    # Add an image to the canvas
    image_resized = image.resize((int(display_width * 0.8), int(display_height * 0.6)), Image.Resampling.LANCZOS)
    canvas.image = ImageTk.PhotoImage(image_resized)
    image_id = canvas.create_image(0, 0, image=canvas.image, anchor="center")
    
    # Bind hover events to the canvas
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Configure>", resize_canvas_image)

    # Create the Item Name label
    leftLabel = tk.Label(parent, text=str(stocks) + " left", anchor="center", bg="white", fg="red")
    leftLabel.place(relx=relx, rely=rely + 0.1, relwidth=0.17, relheight=0.07, anchor="center")
    
    # Create the Item Name label
    nameLabel = tk.Label(parent, text=name, anchor="center", bg="white")
    nameLabel.place(relx=relx, rely=rely + 0.15, relwidth=0.17, relheight=0.07, anchor="center")
    
    # Create the value label
    priceLabel = tk.Label(parent, text='₱' + str(price), font=("Tahoma", 12),
                           anchor="center", compound="center", bg="white", fg="#fff705")
    priceLabel.place(relx=relx, rely=rely + 0.22, relwidth=0.065, relheight=0.074, anchor="center")

    # Create the -1 button
    decreaseBtn = tk.Button(parent, text="-", command=decrease, width=35, highlightthickness=0,
                                bg=goldBG, bd=0, activebackground=goldBG, state="disabled")
    decreaseBtn.place(relx=relx - 0.05, rely=rely + 0.305, relwidth=0.04, relheight=0.06, anchor="center")
    decrease_buttons.append(decreaseBtn)
    
    # Create the +1 button
    increaseBtn = tk.Button(parent, text="+", command=increase, width=35, highlightthickness=0,
                                bg=goldBG, bd=0, activebackground=goldBG)
    increaseBtn.place(relx=relx + 0.05, rely=rely + 0.305, relwidth=0.04, relheight=0.06, anchor="center")
    increase_buttons.append(increaseBtn)
    
    # Create the value label
    valueLabel = tk.Label(parent, text="0", font=("Open Sans", 12), width=4, anchor="center", bg="white")
    valueLabel.place(relx=relx, rely=rely + 0.305, relwidth=0.055, relheight=0.07, anchor="center")

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
    buffer += event.char
    
    if event.keysym == "Return":    # press enter
        go_to_confirmationPage(buffer)
        buffer = ""
        
def go_to_tapID_page():
    global current_page
    current_page = tapID_page
    root.bind("<Key>", on_key_press)
    print(cart)
    selectionPage.pack_forget()
    tapID_page.pack(fill="both", expand=True)

##### SELECTION PAGE WIDGETS


selectionPage = tk.Frame(root, bg=goldBG)

top_section = tk.Frame(selectionPage, bg=maroonBG)
top_section.place(relx=0, rely=0, relwidth=1, relheight=0.2)

backBtn = tk.Button(
    top_section,
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
backBtn.place(relx=0.09, rely=0.5, relwidth=0.12, relheight=0.4, anchor="center")  

bottom_section = tk.Frame(selectionPage, bg=maroonBG)
bottom_section.place(relx=0, rely=0.8, relwidth=1, relheight=0.2)   
selectItems_label = tk.Label(top_section, bg=maroonBG, font=("Tahoma", 24))
selectItems_label.place(relx=0.5, rely=0.5, relwidth=0.25, relheight=0.5, anchor="center")


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
total_label.place(relx=0.6, rely=0.9, relwidth=0.25, relheight=0.1, anchor="center")

checkoutBtn = tk.Button(selectionPage , bg=maroonBG, highlightthickness=0,
                            command=go_to_tapID_page, bd=0, activebackground=maroonBG, state=tk.DISABLED)
checkoutBtn.place(relx=0.85, rely=0.9, relwidth=0.25, relheight=0.1, anchor="center")

checkBalanceBtn = tk.Button(selectionPage , bg=maroonBG, highlightthickness=0,
                            command=show_balanceModal, bd=0, activebackground=maroonBG)
checkBalanceBtn.place(relx=0.18, rely=0.9, relwidth=0.3, relheight=0.1, anchor="center")

backBtn.bind("<Configure>", lambda event: designs.resize_backBtn(event, backBtn))
selectItems_label.bind("<Configure>", lambda event: designs.resize_selectLabel(event, selectItems_label))
total_label.bind("<Configure>", lambda event: designs.resize_totalLabel(event, total_label))
checkoutBtn.bind("<Configure>", lambda event: designs.resize_checkoutBtn(event, checkoutBtn))
checkBalanceBtn.bind("<Configure>", lambda event: designs.resize_checkBalanceBtn(event, checkBalanceBtn))


# Function to check if connected to the internet
def is_connected():
    global item_list
    try:
        # Try connecting to a known host (Google's public DNS server) on port 53
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        if item_list ==[]:
            item_list = supabase.table('items').select('*').eq('forsale', 1).order('id').execute()
            display_item_list()
        return True
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

# Start by checking the connection
check_connection()

############################################################################ TAP ID PAGE


tapID_page = tk.Frame(root, bg=goldBG)
tapID_label = tk.Label(tapID_page, bg=goldBG, fg="black", justify="center")
tapID_label.place(relx=0.3, rely=0.5, relwidth=0.33, relheight=0.45, anchor="center")

# Open the GIF file using Pillow
gif_image = Image.open(imgPrefix + "tapID.gif")
frames = [] # for frames
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
    root.unbind("<Key>")
    tapID_page.pack_forget()
    cart = [0,0,0,0]
    selectionPage.pack(fill="both", expand=True)

def go_to_confirmationPage(buffer):
    global username, CORRECT_PIN, balance, current_page
    
    
    userQuery = supabase.table('students').select('*').eq('idcode', buffer).execute()
    if(userQuery.data):
        tapID_page.pack_forget()
        confirmationPage.pack(fill="both", expand=True)
        current_page = confirmationPage
        userData = userQuery.data[0]
        balance = int(userData['balance'])
        CORRECT_PIN = userData['pin']
        greetingsLabel.config(text="Hi, " + userData['fname'] + " " + userData['lname'])
        currentBalance_label.config(text="Current Balance is: " + str(userData['balance']))
        root.unbind("<Key>")
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
backBtn2.place(relx=0.03, rely=0.06, relwidth=0.12, relheight=0.08)  # Place at top-left

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
    print(items_to_dispense)
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
    global balance
    if entered_pin != CORRECT_PIN:
        #messagebox.showerror("Incorrect PIN.", "Try again.")
        show_modal("Incorrect PIN\nPlease Try again.", 1500)
        clear_pin()
        return
        
    if balance < total_price:
        defer = messagebox.askyesno("Insufficient Balance", "Your payment will be added to your tuition")
        if not defer:
            clear_pin()
            return

    clear_pin()
    print(item_list)
    for item_name, cart_quantity in cart.items():
        if cart_quantity > 0:
            # Find the corresponding item in the item_list
            matching_item = next((item for item in item_list.data if item['item_name'] == item_name), None)

            if matching_item:
                # Calculate the new stock
                new_stock = matching_item['stocks'] - cart_quantity

                # Update the stocks in Supabase
                supabase.table('items').update({'stocks': new_stock}).eq('id', matching_item['id']).execute()

                print(f"Updated {item_name}: New stock is {new_stock}")
    
    go_to_dispensePage()

def go_back_to_tapIDPage():
    global current_page
    current_page = tapID_page
    print(entered_pin)
    clear_pin()
    root.bind("<Key>", on_key_press)
    confirmationPage.pack_forget() 
    tapID_page.pack(fill="both", expand=True)


####### CONFIRMATION PAGE WIDGETS


confirmationPage = tk.Frame(root, bg="#ffce03")

backBtn3 = tk.Button(confirmationPage, text="Back", font=("Arial", 12), bg=goldBG, highlightthickness=0, command=go_back_to_tapIDPage, fg='white', activebackground=goldBG, bd=0)
backBtn3.place(relx=0.03, rely=0.06, relwidth=0.12, relheight=0.08)

greetingsLabel = tk.Label(confirmationPage, bg="#ffce03", justify="center")
greetingsLabel.place(relx=0.3, rely=0.25, anchor="center")
currentBalance_label = tk.Label(confirmationPage, bg="#ffce03", justify="center")
currentBalance_label.place(relx=0.3, rely=0.35, anchor="center")
enterPinLabel = tk.Label(confirmationPage, text="Enter\nyour pin", bg="#ffce03", justify="center")
enterPinLabel.place(relx=0.3, rely=0.55, anchor="center")
errorLabel = tk.Label(confirmationPage, text="Not you? Click Here to Report", bg="#ffce03", justify="center", font=("Tahoma", 9, "bold"))
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
    
    # Calculate intermediate color (blend between white and maroon)
    r = int(255 - (255 - 128) * opacity)  # Maroon RGB (128,0,0)
    g = int(255 - (255 - 0) * opacity)
    b = int(255 - (255 - 0) * opacity)
    new_bg = f"#{r:02x}{g:02x}{b:02x}"  # Convert to hex
    
    # Apply new background color
    newOrderBtn.config(bg=new_bg, activebackground=new_bg)

    # Schedule next animation step (slower)
    root.after(100, lambda: show_Btn(opacity + 0.05))  # Slower transition

def increment_item():
    global current_item
    print(current_item)
    if current_item < total_items:
        current_item += 1
        dispensingLabel.config(text=f"Dispensing {current_item}/{total_items}")
    else:
        dispensingLabel.config(text="Done")
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

root.mainloop()
