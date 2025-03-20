import tkinter as tk
from PIL import Image, ImageTk

import os

# Get the directory of the current script (app.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set imgPrefix to the img directory
imgPrefix = os.path.join(script_dir, "img/")

logo_img = Image.open(imgPrefix + "icon.png")
backBtn_img = Image.open(imgPrefix + "back.png")
select_img = Image.open(imgPrefix + "selectTitle.png")
checkout_img = Image.open(imgPrefix + "checkout.png")
checkBalance_img = Image.open(imgPrefix + "checkbalance.png")
price_img = Image.open(imgPrefix + "price.png")
plus_img = Image.open(imgPrefix + "+.png")
minus_img = Image.open(imgPrefix + "-.png")
tapID_img = Image.open(imgPrefix + "tapurid.png")
pinframe_original = Image.open(imgPrefix + "pinframe.png")
balanceLabel_original = Image.open(imgPrefix + "balance.png")
power_img = Image.open(imgPrefix + "power.png")
save_img = Image.open(imgPrefix + "save.png")


def datdat_animation2(datdat2, reconnectingPage):
    current_text = datdat2.get()
    if current_text.endswith("..."):
        datdat2.set("Reconnecting")
    else:
        datdat2.set(current_text + ".")
    reconnectingPage.after(500, datdat_animation2, datdat2, reconnectingPage)

######## START PAGE

def resize_logo(event, kithub_logo):
    global logo_resized
    resized_img = logo_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    logo_resized = ImageTk.PhotoImage(resized_img)
    kithub_logo.config(image=logo_resized)

def resize_labels(event, widgets, all_buttons):
    scale_factor = min(event.width, event.height) / 480

    for widget, font_family, base_size, *style in widgets:
        widget.config(font=(font_family, int(base_size * scale_factor), *style))

    for btn in all_buttons:
        btn.config(font=("Arial", int(18 * scale_factor)))

def datdat_animation(datdat, startPage):
    current_text = datdat.get()
    if current_text.endswith("..."):
        datdat.set("Click Anywhere to Start")
    else:
        datdat.set(current_text + ".")
    startPage.after(500, datdat_animation, datdat, startPage)

######## SELECTION PAGE

def resize_backBtn(event, backBtn):
    global backBtn_resized
    resized_img = backBtn_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    backBtn_resized = ImageTk.PhotoImage(resized_img)
    backBtn.config(image=backBtn_resized)

def resize_selectLabel(event, selectItems_label):
    global selectLabel_resized
    resized_img = select_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    selectLabel_resized = ImageTk.PhotoImage(resized_img)
    selectItems_label.config(image=selectLabel_resized)

def resize_checkoutBtn(event, checkoutBtn):
    global checkoutBtn_resized
    resized_img = checkout_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    checkoutBtn_resized = ImageTk.PhotoImage(resized_img)
    checkoutBtn.config(image=checkoutBtn_resized)

def resize_checkBalanceBtn(event, checkBalanceBtn):
    global checkBalanceBtn_resized
    resized_img = checkBalance_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    checkBalanceBtn_resized = ImageTk.PhotoImage(resized_img)
    checkBalanceBtn.config(image=checkBalanceBtn_resized)

def resize_totalLabel(event, total_label):
    scale_factor = min(event.width, event.height) / 48  
    new_font_size = max(1, int(21 * scale_factor))  
    total_label.config(font=("Tahoma", new_font_size, "bold"), wraplength=event.width)

######## TAPID PAGE

def resize_tapID_label(event, tapID_label):
    global tapIDLogo_resized
    resized_img = tapID_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    tapIDLogo_resized = ImageTk.PhotoImage(resized_img)
    tapID_label.config(image=tapIDLogo_resized)

def resize_backBtn2(event, backBtn2):
    global backBtn_resized2
    resized_img = backBtn_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    backBtn_resized2 = ImageTk.PhotoImage(resized_img)
    backBtn2.config(image=backBtn_resized2)

######## CONFIRMATION PAGE

def resize_pinframe(event, pinDisplay):
    global pinframe_resized
    resized_img = pinframe_original.resize((event.width, event.height), Image.Resampling.LANCZOS)
    pinframe_resized = ImageTk.PhotoImage(resized_img)
    pinDisplay.config(image=pinframe_resized)

def resize_backBtn3(event, backBtn3):
    global backBtn_resized3
    resized_img = backBtn_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    backBtn_resized3 = ImageTk.PhotoImage(resized_img)
    backBtn3.config(image=backBtn_resized3)

######### ADMIN PAGE

def resize_backBtn4(event, backBtn4):
    global backBtn_resized4
    resized_img = backBtn_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    backBtn_resized4 = ImageTk.PhotoImage(resized_img)
    backBtn4.config(image=backBtn_resized4)

def resize_powerBtn(event, powerBtn):
    global powerBtn_resized
    resized_img = power_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    powerBtn_resized = ImageTk.PhotoImage(resized_img)
    powerBtn.config(image=powerBtn_resized)

def resize_saveBtn(event, saveBtn):
    global saveBtn_resized
    resized_img = save_img.resize((event.width, event.height), Image.Resampling.LANCZOS)
    saveBtn_resized = ImageTk.PhotoImage(resized_img)
    saveBtn.config(image=saveBtn_resized)