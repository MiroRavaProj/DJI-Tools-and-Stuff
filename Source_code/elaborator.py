def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)


import sys

sys.excepthook = show_exception_and_exit
import os
import numpy
import piexif
import re
import exif
from fractions import Fraction
import subprocess
from PIL import Image
import cv2

files = [os.path.normpath(os.path.join(dirpath, f)) for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]) for f in
         filenames]
files1 = os.listdir(sys.argv[1])
percentage = 0


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# THERMAL PROCESSING
def read_dji_image(img_in, raw_out, em=0.95, dist=5, hu=50, refl=25):
    subprocess.run(
        ["dji_irp.exe", "-s", f"{img_in}", "-a", "measure", "-o", f"{raw_out}", "--measurefmt",
         "float32", "--distance", f"{dist}", "--humidity", f"{hu}", "--reflection", f"{refl}",
         "--emissivity", f"{em}"],
        universal_newlines=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        shell=True
    )
    try:
        image = Image.open(img_in)
        exif = image.info['exif']
        return exif
    except:
        return None


def process_one_th_picture(ir_img_path, em, dist, hu, refl):
    _, filename = os.path.split(str(ir_img_path))
    new_raw_path = str(ir_img_path)[:-4] + '.raw'

    exif = read_dji_image(str(ir_img_path), str(new_raw_path), em=em, dist=dist, hu=hu, refl=refl)

    if exif is not None:
        # read raw dji output
        try:
            fd = open(new_raw_path, 'rb')
            rows = 512
            cols = 640
            f = numpy.fromfile(fd, dtype='<f4', count=rows * cols)
            im = f.reshape((rows, cols))  # notice row, column format
            fd.close()

            dest_path = ir_img_path[:-4] + '.tiff'
            img_thermal = Image.fromarray(im)
            if sys.argv[8] == "0":
                img_thermal.save(dest_path, exif=exif)
            else:
                img_thermal.save(dest_path)
                subprocess.run(["exiftool.exe", "-TagsFromFile", ir_img_path, "-IPTC:all", "-exif:all","-xmp:all","-jfif:all","-all:all>all:all", dest_path, "-overwrite_original"])
            os.remove(new_raw_path)
            print(f" --> Converted from R-JPEG to Tiff : {filename}")
            if sys.argv[7] == "0":
                os.remove(ir_img_path)

        except FileNotFoundError:
            print(f" --> This image is not a Thermal DJI Image: {filename}")
    else:
        print(f" --> This is not a readable Thermal DJI Image: {filename}")


def parse_srt_file(srt_path):
    latitudes = []
    longitudes = []
    altitudes = []

    with open(srt_path, 'r') as file:
        srt_content = file.read()

    pattern = r'\[latitude: ([\d.-]+)\] \[longitude: ([\d.-]+)\] \[altitude: ([\d.-]+)\]'
    matches = re.findall(pattern, srt_content)
    for match in matches:
        latitude = float(match[0])
        longitude = float(match[1])
        altitude = float(match[2])

        altitudes.append(altitude)
        latitudes.append(latitude)
        longitudes.append(longitude)

    return latitudes, longitudes, altitudes


# Convert the latitude and longitude to the required format (Rational)
def degrees_to_rational(number):
    degrees = int(abs(number))
    minutes = int((abs(number) - degrees) * 60)
    seconds = int(((abs(number) - degrees - minutes / 60) * 3600) * 100)

    return [(degrees, 1), (minutes, 1), (seconds, 100)]


if sys.argv[2] == "0":
    print("Elaborating Videos with Timestamps if present:")

    for videoPath in files1:
        if videoPath[-4:] in [".MOV", ".mov", ".MP4", ".mp4"]:
            video_path = os.path.join(sys.argv[1], videoPath)
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            srt_path = os.path.join(sys.argv[1], video_name + ".srt")
            capture = cv2.VideoCapture(video_path)
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            frames_to_extract = range(0, frame_count - 1, int(float(sys.argv[3]) * capture.get(cv2.CAP_PROP_FPS)))
            try:
                latitudes, longitudes, altitudes = parse_srt_file(srt_path)
            except FileNotFoundError:
                print(f"WARNING ---> Skipping Video: {video_name} ---> NO .SRT File found")
                continue
            for frame_index in frames_to_extract:
                capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                success, frame = capture.read()

                if success:
                    frame_path = os.path.normpath(os.path.join(sys.argv[1], f'{video_name}_frame_{frame_index}.jpg'))
                    cv2.imwrite(frame_path, frame)
                    try:
                        frame_latitude = latitudes[frame_index]
                        frame_longitude = longitudes[frame_index]
                        frame_altitude = altitudes[frame_index] + int(sys.argv[2])
                    except Exception as e:
                        print(f"Image not processed because ---> {e}")
                        continue

                    if frame_latitude is not None and frame_longitude is not None and frame_altitude is not None:
                        try:
                            # Open the image file
                            image = Image.open(frame_path)

                            # Get the existing EXIF data
                            exif_dict = piexif.load(frame_path)

                            # Preserve existing GPS data
                            gps_info = exif_dict.get("GPS", {})
                            altitude_ref = gps_info.get(piexif.GPSIFD.GPSAltitudeRef, 0)
                            gps_version = exif_dict.get(piexif.GPSIFD.GPSVersionID, (2, 3, 0, 0))

                            new_lat_rational = degrees_to_rational(frame_latitude)
                            new_lon_rational = degrees_to_rational(frame_longitude)

                            # Update the GPS data in the EXIF metadata
                            exif_dict["GPS"] = {
                                piexif.GPSIFD.GPSLatitudeRef: 'N' if frame_latitude >= 0 else 'S',
                                piexif.GPSIFD.GPSLatitude: new_lat_rational,
                                piexif.GPSIFD.GPSLongitudeRef: 'E' if frame_longitude >= 0 else 'W',
                                piexif.GPSIFD.GPSLongitude: new_lon_rational,
                                piexif.GPSIFD.GPSVersionID: (2, 3, 0, 0),
                                piexif.GPSIFD.GPSAltitude: Fraction.from_float(
                                    frame_altitude).limit_denominator().as_integer_ratio(),
                                piexif.GPSIFD.GPSAltitudeRef: 0,
                            }

                            # Encode the EXIF data and save it back to the image
                            exif_bytes = piexif.dump(exif_dict)
                            image.save(frame_path, exif=exif_bytes)

                            print(f'{video_name}_frame_{frame_index}.jpg')
                        except Exception as e:
                            print(f"Image not processed because ---> {e}")


                    else:
                        print(f"No GPS data found for frame: {frame_path}")
                else:
                    print(f"Error extracting frame at index {frame_index}")

            capture.release()

    print("Elaborating Images:")

    for imagePath in files1:
        if imagePath[-4:] in [".JPG", ".PNG", ".jpg", ".png"]:
            percentage += 100 / len(files1)
            full_imagePath = os.path.join(sys.argv[1], imagePath)
            with open(full_imagePath, 'rb') as image_file:
                img = exif.Image(image_file)
                img.gps_altitude = img.gps_altitude + int(sys.argv[2])
            ext = full_imagePath[-4:]
            tempPath = full_imagePath[:-4]
            with open(f"{tempPath}_mod{ext}", 'wb') as test_image_file:
                test_image_file.write(img.get_file())
            os.remove(full_imagePath)
            print(f"{percentage:.2f}%  --> Changed GPS Altitude of: {full_imagePath[-12:-4]}")
    print("100.00% --> Done!!")
else:
    for imagePath in files:
        percentage += 100 / len(files)
        full_imagePath = imagePath
        print(f"{percentage:.2f}%", end="")
        process_one_th_picture(full_imagePath, float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]),
                               float(sys.argv[6]))
    input("Press any key to exit: ")
