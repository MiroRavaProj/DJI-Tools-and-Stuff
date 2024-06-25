import sys
import os
import customtkinter
import subprocess
from CTkMessagebox import CTkMessagebox

customtkinter.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.geometry("640x630")
app.title("DJI IMAGE PROCESSOR 1.4")

import webbrowser


def popup():
    # Show some positive message with the checkmark icon
    app.clipboard_append("contact@miro-rava.com")
    CTkMessagebox(width=200, height=130, message="Email Copied To Clipboard!", title="Thanks For Contacting Me!",
                  icon="check", option_1="Thanks")


def popup_folder():
    # Show some positive message with the checkmark icon
    CTkMessagebox(width=200, height=130, message="Select a Folder!!", title="Error!!!",
                  icon="cancel", option_1="Understood")


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


def start_batch_video():
    if entry_1.get() == "":
        al = "0"
    else:
        al = entry_1.get()

    if entry_2.get() == "":
        fps = "1"
    else:
        fps = entry_2.get()
    
    if folder_path_video.get() == "No Folder Selected":
        popup_folder()
    else:
        # subprocess.Popen(["elaborator.exe", folder_path_video.get(), "2", al, entry_2.get()])  # , drone_var.get()])
        subprocess.Popen(["python", "elaborator.py", folder_path_video.get(), "2", al, fps, str(switch_quality.get())])  # , drone_var.get()])


def start_batch_image():
    if entry_1_image.get() == "":
        al_im = "0"
    else:
        al_im = entry_1_image.get()
    if folder_path_image.get() == "No Folder Selected":
        popup_folder()
    else:
        # subprocess.Popen(["elaborator.exe", folder_path_image.get(), "3", al_im])
        subprocess.Popen(["python", "elaborator.py", folder_path_image.get(), "3", al_im])


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
    if folder_path_thermal.get() == "No Folder Selected":
        popup_folder()
    else:
        # subprocess.Popen(["elaborator.exe", folder_path_thermal.get(), "1", em, dist, hu, ref, str(switch.get()), str(switch2.get())])
        subprocess.Popen(["python", "elaborator.py", folder_path_thermal.get(), "1", em, dist, hu, ref, str(switch.get()),
                          str(switch2.get())])


def browse_folder_video():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path_video
    filename = customtkinter.filedialog.askdirectory()
    folder_path_video.set(filename)


def browse_folder_image():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path_image
    filename = customtkinter.filedialog.askdirectory()
    folder_path_image.set(filename)


def browse_folder_thermal():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path_thermal
    filename = customtkinter.filedialog.askdirectory()
    folder_path_thermal.set(filename)


# create tabview
tabview = customtkinter.CTkTabview(master=app, width=600, height=600)
tabview.grid(row=0, column=2, padx=(20, 0), pady=(0, 0), sticky="nsew")
tabview.add("DJI Thermal Converter")
tabview.add("Geotagged Video Frame Extractor")
tabview.add("Batch Image Coordinate Editor")
tabview.add("INFO")
tabview.tab("Geotagged Video Frame Extractor").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
tabview.tab("INFO").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs

folder_path_thermal = customtkinter.StringVar()
folder_path_thermal.set("No Folder Selected")

folder_path_video = customtkinter.StringVar()
folder_path_video.set("No Folder Selected")

folder_path_image = customtkinter.StringVar()
folder_path_image.set("No Folder Selected")


button_1 = customtkinter.CTkButton(text="Chose Video Folder", master=tabview.tab("Geotagged Video Frame Extractor"),
                                   command=browse_folder_video)
button_1.pack(pady=10, padx=10)

label_2 = customtkinter.CTkLabel(master=tabview.tab("Geotagged Video Frame Extractor"), textvariable=folder_path_video,
                                 justify=customtkinter.LEFT)
label_2.pack(pady=8, padx=8)

entry_1 = customtkinter.CTkEntry(master=tabview.tab("Geotagged Video Frame Extractor"),
                                 placeholder_text="Starting Altitude in m (default: 0)")
entry_1.pack(pady=10, padx=10)

entry_2 = customtkinter.CTkEntry(master=tabview.tab("Geotagged Video Frame Extractor"),
                                 placeholder_text="FPS (default: 1)")
entry_2.pack(pady=10, padx=10)

switch_quality = customtkinter.CTkSwitch(master=tabview.tab("Geotagged Video Frame Extractor"), text="Higher Quality (slower: PNG instead of JPG)")
switch_quality.pack(pady=8, padx=8)

button_2 = customtkinter.CTkButton(text="Start Batch Processing", master=tabview.tab("Geotagged Video Frame Extractor"),
                                   command=start_batch_video)
button_2.pack(pady=10, padx=10)
label_0 = customtkinter.CTkLabel(master=tabview.tab("Geotagged Video Frame Extractor"),
                                 text="\nInfo: \n\n- Each video in the folder will be considered only if there\n  is an .srt file with the same name in the folder.\n\n- The starting altitude is necessary if you need the ASL  \n  value as metadata of your frames and you know that your \n drone saves relative altitude in the .srt file.",
                                 justify=customtkinter.LEFT)
label_0.pack(pady=8, padx=8)

tabview.tab("DJI Thermal Converter").grid_columnconfigure(0, weight=1)

'''format = customtkinter.StringVar(value="Format - TIFF")  # set initial value
combobox = customtkinter.CTkOptionMenu(master=tabview.tab("DJI Thermal Converter"),
                                       values=["Format - TIFF", "Format - RJPG (slower)"],
                                       variable=format)
combobox.pack(padx=8, pady=8)'''
frame0 = customtkinter.CTkFrame(master=tabview.tab("DJI Thermal Converter"))
frame0.pack(pady=8, padx=8)

button_1_1 = customtkinter.CTkButton(text="Chose Image Folder", master=frame0,
                                     command=browse_folder_thermal)
button_1_1.grid(row=0, column=0, padx=8, pady=8)

switch = customtkinter.CTkSwitch(master=frame0, text="Mantain Originals")
switch.grid(row=0, column=1, padx=8, pady=8)
switch.select()

switch2 = customtkinter.CTkSwitch(master=frame0, text="Maintain RTK data (slower)")
switch2.grid(row=0, column=2, padx=8, pady=8)

label_2_1 = customtkinter.CTkLabel(master=tabview.tab("DJI Thermal Converter"), textvariable=folder_path_thermal,
                                   justify=customtkinter.LEFT)
label_2_1.pack(pady=0, padx=8)

'''switch3 = customtkinter.CTkSwitch(master=tabview.tab("DJI Thermal Converter"), text="Undistort M3T & M2T images (slower & experimental)")
switch3.pack(padx=8, pady=8)'''
# Create a new frame in the "DJI Thermal Converter" tab
frame = customtkinter.CTkFrame(master=tabview.tab("DJI Thermal Converter"))
frame.pack(pady=8, padx=8)  # Use pack here to place the frame in the tab

# Now use grid within this frame
emissivity_label = customtkinter.CTkLabel(master=frame, text="Emissivity")
emissivity_label.grid(row=1, column=0, padx=10, pady=10)

emissivity = customtkinter.CTkEntry(master=frame, placeholder_text="Default: 0.95")
emissivity.grid(row=1, column=1, padx=10, pady=10)

distance_label = customtkinter.CTkLabel(master=frame, text="Distance")
distance_label.grid(row=0, column=0, padx=10, pady=10)

distance = customtkinter.CTkEntry(master=frame, placeholder_text="Default: 5.0")
distance.grid(row=0, column=1, padx=10, pady=10)

humidity_label = customtkinter.CTkLabel(master=frame, text="Humidity")
humidity_label.grid(row=0, column=2, padx=10, pady=10)

humidity = customtkinter.CTkEntry(master=frame, placeholder_text="Default: 50")
humidity.grid(row=0, column=3, padx=10, pady=10)

reflectance_label = customtkinter.CTkLabel(master=frame, text="Reflectance")
reflectance_label.grid(row=1, column=2, padx=10, pady=10)

reflectance = customtkinter.CTkEntry(master=frame, placeholder_text="Default: 25")
reflectance.grid(row=1, column=3, padx=10, pady=10)

info_text = customtkinter.CTkLabel(master=tabview.tab("DJI Thermal Converter"),
                                   text="Distance: 1 to 25 (if exceeding 25, input 25), The distance of the target being"
                                        " measured. Measurement accuracy decreases beyond 25 meters. Calibration distance"
                                        " is typically fixed at factory shipment for infrared cameras. Accuracy diminishes"
                                        " if the distance is too close or too far.\n\nHumidity: 20 to 100, The relative humidity "
                                        "of the air in the target measurement environment. Setting according to the actual "
                                        "measurement environment impacts temperature measurement accuracy minimally.\n\n"
                                        "Emissivity: 0.10 to 1.00, The object's surface ability to emit energy as radiation. "
                                        "Configured with reference to a table of common substances' emissivity. Accuracy affects "
                                        "temperature measurement precision, with potential discrepancies between actual and "
                                        "reference emissivity values due to object surface conditions.\n\nReflectance:"
                                        " -40.0 to 500.0, Surrounding objects' energy can reflect from the target surface"
                                        " being measured, affecting temperature measurement accuracy. If no objects with"
                                        " extreme temperatures are nearby, reflected temperature can be set as ambient "
                                        "temperature. Accurate configuration impacts temperature measurement precision, "
                                        "with higher deviations from ambient temperature causing greater effects.",
                                   justify=customtkinter.LEFT, wraplength=520)
info_text.pack(pady=8, padx=8)

button_2_1 = customtkinter.CTkButton(text="Start Batch Processing", master=tabview.tab("DJI Thermal Converter"),
                                     command=start_batch_flir)
button_2_1.pack(pady=10, padx=10)
tabview.tab("Batch Image Coordinate Editor").grid_columnconfigure(0, weight=1)

button_1_image = customtkinter.CTkButton(text="Chose Image Folder", master=tabview.tab("Batch Image Coordinate Editor"),
                                         command=browse_folder_image)
button_1_image.pack(pady=10, padx=10)

label_2_image = customtkinter.CTkLabel(master=tabview.tab("Batch Image Coordinate Editor"),
                                       textvariable=folder_path_image,
                                       justify=customtkinter.LEFT)
label_2_image.pack(pady=8, padx=8)

entry_1_image = customtkinter.CTkEntry(master=tabview.tab("Batch Image Coordinate Editor"),
                                       placeholder_text="Offset Altitude in m")
entry_1_image.pack(pady=10, padx=10)

'''entry_2_image = customtkinter.CTkEntry(master=tabview.tab("Batch Image Coordinate Editor"),
                                       placeholder_text="Offset Altitude in m")
entry_2_image.pack(pady=10, padx=10)
entry_3_image = customtkinter.CTkEntry(master=tabview.tab("Batch Image Coordinate Editor"),
                                       placeholder_text="Offset Altitude in m")
entry_3_image.pack(pady=10, padx=10)'''

button_2_image = customtkinter.CTkButton(text="Start Batch Processing",
                                         master=tabview.tab("Batch Image Coordinate Editor"),
                                         command=start_batch_image)
button_2_image.pack(pady=10, padx=10)

label_0_image = customtkinter.CTkLabel(master=tabview.tab("Batch Image Coordinate Editor"),
                                       text="\n\n\n\nInfo: \n\n- The offset altitude is the amount you want to offset     \n  the ASL value in the metadata of your photos.",
                                       justify=customtkinter.LEFT)
label_0_image.pack(pady=11, padx=8)

label_info = customtkinter.CTkLabel(master=tabview.tab("INFO"),
                                    text="\n\nThis Program was custom made by Miro Rava\n\nIf you have suggestions for any improvement, contact me!\n\nAvailable also on Github:",
                                    justify=customtkinter.LEFT)
label_info.pack(pady=8, padx=8)
link3 = customtkinter.CTkLabel(master=tabview.tab("INFO"),
                               text="https://github.com/MiroRavaProj/DJI-Tools-and-Stuff       ", text_color="blue")
link3.pack(pady=0, padx=8)
link3.bind("<Button-1>", lambda e: callback("https://github.com/MiroRavaProj/DJI-Tools-and-Stuff"))
label_info_2 = customtkinter.CTkLabel(master=tabview.tab("INFO"),
                                      text="\n\nThanks also to:\n\nPhil Harvey for Exiftool                                                                  ",
                                      justify=customtkinter.LEFT)
label_info_2.pack(pady=8, padx=8)
info = customtkinter.CTkFrame(master=app, fg_color="transparent")
info.grid(row=1, column=2)
link = customtkinter.CTkLabel(master=info, text="www.miro-rava.com", text_color="blue")
link.grid(row=0, column=1, padx=10)
link.bind("<Button-1>", lambda e: callback("https://www.miro-rava.com"))

link2 = customtkinter.CTkLabel(master=info, text="contact@miro-rava.com", text_color="blue")
link2.grid(row=0, column=2, padx=10)
link2.bind("<Button-1>", lambda e: popup())

if __name__ == '__main__':
    app.mainloop()
