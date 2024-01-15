import sys
import os
import customtkinter
import subprocess


customtkinter.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.geometry("440x500")
app.title("DJI IMAGE PROCESSOR")

import webbrowser

def callback(url):
    webbrowser.open_new(url)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def start_batch():

    subprocess.Popen(["python","elaborator.py", folder_path.get(), "0" ,entry_1.get(),entry_2.get()])

def start_batch_flir():

    if emissivity.get() == "":
        em = "0.95"
    else:
        em = emissivity.get()
    if distance.get() == "":
        dist = "5"
    else:
        dist = distance.get()
    if humidity.get() == "":
        hu = "50"
    else:
        hu = humidity.get()
    if reflectance.get() == "":
        ref = "25"
    else:
        ref = reflectance.get()
    '''if format.get() == "Format - TIFF":
        image_format = 0
    else:
        image_format = 1'''
    subprocess.Popen(["python","elaborator.py", folder_path.get(), "1", em, dist, hu, ref, str(switch.get()), str(switch2.get())])

def browse_folder():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    filename = customtkinter.filedialog.askdirectory()
    folder_path.set(filename)


# create tabview
tabview = customtkinter.CTkTabview(master=app, width=400, height=470)
tabview.grid(row=0, column=2, padx=(20, 0), pady=(0, 0), sticky="nsew")
tabview.add("DJI Thermal Converter")
tabview.add("DJI Air 2 - Frame Extractor")
tabview.add("INFO")
tabview.tab("DJI Air 2 - Frame Extractor").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
tabview.tab("INFO").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs


folder_path = customtkinter.StringVar()
folder_path.set("No Folder Selected")

button_1 = customtkinter.CTkButton(text="Chose Image Folder", master=tabview.tab("DJI Air 2 - Frame Extractor"), command=browse_folder)
button_1.pack(pady=10, padx=10)

label_2 = customtkinter.CTkLabel(master=tabview.tab("DJI Air 2 - Frame Extractor"), textvariable=folder_path, justify=customtkinter.LEFT)
label_2.pack(pady=8, padx=8)

entry_1 = customtkinter.CTkEntry(master=tabview.tab("DJI Air 2 - Frame Extractor"), placeholder_text="Enter Altitude in m")
entry_1.pack(pady=10, padx=10)

entry_2 = customtkinter.CTkEntry(master=tabview.tab("DJI Air 2 - Frame Extractor"), placeholder_text="Frames Interval in s")
entry_2.pack(pady=10, padx=10)

button_2 = customtkinter.CTkButton(text="Start Batch Processing", master=tabview.tab("DJI Air 2 - Frame Extractor"), command=start_batch)
button_2.pack(pady=10, padx=10)

tabview.tab("DJI Thermal Converter").grid_columnconfigure(0, weight=1)

button_1_1 = customtkinter.CTkButton(text="Chose Image Folder", master=tabview.tab("DJI Thermal Converter"), command=browse_folder)
button_1_1.pack(pady=10, padx=10)

label_2_1 = customtkinter.CTkLabel(master=tabview.tab("DJI Thermal Converter"), textvariable=folder_path, justify=customtkinter.LEFT)
label_2_1.pack(pady=8, padx=8)

'''format = customtkinter.StringVar(value="Format - TIFF")  # set initial value
combobox = customtkinter.CTkOptionMenu(master=tabview.tab("DJI Thermal Converter"),
                                       values=["Format - TIFF", "Format - RJPG (slower)"],
                                       variable=format)
combobox.pack(padx=8, pady=8)'''

switch = customtkinter.CTkSwitch(master=tabview.tab("DJI Thermal Converter"), text="Mantain Originals")
switch.pack(padx=8, pady=8)
switch.select()

switch2 = customtkinter.CTkSwitch(master=tabview.tab("DJI Thermal Converter"), text="Maintain RTK data (slower)")
switch2.pack(padx=8, pady=8)

'''switch3 = customtkinter.CTkSwitch(master=tabview.tab("DJI Thermal Converter"), text="Undistort M3T & M2T images (slower & experimental)")
switch3.pack(padx=8, pady=8)'''

emissivity = customtkinter.CTkEntry(master=tabview.tab("DJI Thermal Converter"), placeholder_text="Def. Emissivity: 0.95")
emissivity.pack(pady=10, padx=10)

distance = customtkinter.CTkEntry(master=tabview.tab("DJI Thermal Converter"), placeholder_text="Def. Distance: 5")
distance.pack(pady=10, padx=10)

humidity = customtkinter.CTkEntry(master=tabview.tab("DJI Thermal Converter"), placeholder_text="Def. Humidity: 50")
humidity.pack(pady=10, padx=10)

reflectance = customtkinter.CTkEntry(master=tabview.tab("DJI Thermal Converter"), placeholder_text="Def. Reflectance: 25")
reflectance.pack(pady=10, padx=10)

button_2_1 = customtkinter.CTkButton(text="Start Batch Processing", master=tabview.tab("DJI Thermal Converter"), command=start_batch_flir)
button_2_1.pack(pady=10, padx=10)

label_info = customtkinter.CTkLabel(master=tabview.tab("INFO"), text="\n\nThis Program was custom made by Miro Rava\n\nAlso if you have suggestions for other improvements, contact me!\n\n\n\nThanks also to:\n\n\nPhil Harvey for Exiftool", justify=customtkinter.LEFT)
label_info.pack(pady=8, padx=8)

link = customtkinter.CTkLabel(master=app, text="www.miro-rava.com", text_color="blue")
link.grid(row=1, column=2)
link.bind("<Button-1>", lambda e: callback("https://www.miro-rava.com"))

if __name__ == '__main__':
    app.mainloop()
