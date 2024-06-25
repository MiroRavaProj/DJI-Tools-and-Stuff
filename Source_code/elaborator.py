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
                subprocess.run(
                    ["exiftool.exe", "-TagsFromFile", ir_img_path, "-IPTC:all", "-exif:all", "-xmp:all", "-jfif:all",
                     "-all:all>all:all", dest_path, "-overwrite_original"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            os.remove(new_raw_path)
            print(f" --> Converted from R-JPEG to Tiff : {filename}")
            if sys.argv[7] == "0":
                os.remove(ir_img_path)

        except FileNotFoundError:
            print(f" --> This image is not a Thermal DJI Image: {filename}")
    else:
        print(f" --> This is not a readable Thermal DJI Image: {filename}")


def parse_srt_file(srt_path):
    with open(srt_path, 'r') as file:
        srt_content = file.read()

    altitudes = []
    latitudes = []
    longitudes = []

    pattern = (
        r"(?:latitude:\s*([+-]?\d+(?:\.\d+)?).*?longitude:\s*([+-]?\d+(?:\.\d+)?).*?(?:abs_alt|altitude):\s*([+-]?\d+(?:\.\d+)?))|"
        r"(?:GPS\s*\(\s*([+-]?\d+(?:\.\d+)?),\s*([+-]?\d+(?:\.\d+)?),\s*([+-]?\d+(?:\.\d+)?))|"
        r"(?:\[latitude\s*:\s*([+-]?\d+(?:\.\d+)?)\]\s*\[longtitude\s*:\s*([+-]?\d+(?:\.\d+)?)\])"
    )
    if "abs_alt" in srt_content:
        is_abs_alt = True
    else:
        is_abs_alt = False

    matches = re.findall(pattern, srt_content)
    if len(matches) == 0:
        latitudes = None
        longitudes = None
        altitudes = None
    for match in matches:
        if match[0]:  # Original format
            latitude = float(match[0])
            longitude = float(match[1])
            altitude = float(match[2])
        elif match[3]:  # GPS format without 'M'
            latitude = float(match[3])
            longitude = float(match[4])
            altitude = float(match[5]) if match[5] else None
        else:  # GPS format with 'M'
            latitude = float(match[6])
            longitude = float(match[7])
            altitude = 0

        altitudes.append(altitude)
        latitudes.append(latitude)
        longitudes.append(longitude)

    return latitudes, longitudes, altitudes, is_abs_alt


# Convert the latitude and longitude to the required format (Rational)
def degrees_to_rational(number):
    degrees = int(abs(number))
    minutes = int((abs(number) - degrees) * 60)
    seconds = int(((abs(number) - degrees - minutes / 60) * 3600) * 100)

    return [(degrees, 1), (minutes, 1), (seconds, 100)]


def process_video_frames(videoPath, input_directory, altitude_offset, time_interval,img_format):
    """
    Processes video frames to extract images at specified intervals, updates their EXIF data with GPS information from a corresponding SRT file.

    Parameters:
    videoPath (str): The filename of the video.
    input_directory (str): The directory where the video and SRT files are located.
    altitude_offset (int): The altitude offset to be added if the altitude is not absolute.
    time_interval (float): The interval between frames to extract, as a multiplier of the video's FPS.
    parse_srt_file (function): A function to parse the SRT file and return GPS data.
    degrees_to_rational (function): A function to convert GPS coordinates from degrees to rational numbers for EXIF data.
    """
    if videoPath[-4:] in [".MOV", ".mov", ".MP4", ".mp4"]:
        video_path = os.path.join(input_directory, videoPath)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        srt_path = os.path.join(input_directory, video_name + ".srt")
        try:
            latitudes, longitudes, altitudes, is_abs_alt = parse_srt_file(srt_path)
            if latitudes is None and longitudes is None and altitudes is None:
                print(f"WARNING ---> Skipping Video: {video_name} ---> NO valid GPS data found in the .SRT file, contact@miro-rava.com for help and .srt file to be added")
                return
        except FileNotFoundError:
            print(f"WARNING ---> Skipping Video: {video_name} ---> NO valid .SRT File found for {video_name} (be shure to have the same name for both files)")
            return
        os.makedirs(f'{input_directory}/{video_name}_frames', exist_ok=True)
        process = subprocess.Popen(['ffmpeg_local.exe', '-i', video_path, '-vf', f'fps={time_interval}', '-q:v', '1', f'{input_directory}/{video_name}_frames/{video_name}_frame_%d.{img_format}'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE , universal_newlines=True)
        frame_pattern = re.compile(r"frame=\s*(\d+)")
    
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Match frame number
                frame_match = frame_pattern.search(output)
                if frame_match:
                    frame_number = int(frame_match.group(1))
                    sys.stdout.write(f'\rExtracted frame: {frame_number} from {video_name}')
                    sys.stdout.flush()
    
        # Wait for the process to complete
        process.wait()

        print("\nFrame extraction completed. Wait for GPS data to be added.")

        total_coordinates = len(latitudes)  # assuming latitudes, longitudes, and altitudes are of the same length
        print(f'{total_coordinates} GPS coordinates found in the .SRT file.')
        step_size = total_coordinates / frame_number

        #for i in range(0, total_coordinates, step_size):
        frame_counter = 0
        frame_index=1
        while frame_index <= frame_number:
            i = round(frame_counter)
            frame_path = os.path.abspath(os.path.join(input_directory, f'{video_name}_frames/{video_name}_frame_{frame_index}.{img_format}'))

            try:
                frame_latitude = latitudes[i]
                frame_longitude = longitudes[i]
                if is_abs_alt:
                    frame_altitude = altitudes[i]
                else:
                    frame_altitude = altitudes[i] + float(altitude_offset)

                if frame_latitude is not None and frame_longitude is not None and frame_altitude is not None:
                    image = Image.open(frame_path)
                    exif_dict = piexif.load(frame_path)

                    new_lat_rational = degrees_to_rational(frame_latitude)
                    new_lon_rational = degrees_to_rational(frame_longitude)

                    exif_dict["GPS"] = {
                        piexif.GPSIFD.GPSLatitudeRef: 'N' if frame_latitude >= 0 else 'S',
                        piexif.GPSIFD.GPSLatitude: new_lat_rational,
                        piexif.GPSIFD.GPSLongitudeRef: 'E' if frame_longitude >= 0 else 'W',
                        piexif.GPSIFD.GPSLongitude: new_lon_rational,
                        piexif.GPSIFD.GPSAltitude: Fraction.from_float(frame_altitude).limit_denominator().as_integer_ratio(),
                        piexif.GPSIFD.GPSAltitudeRef: 0,
                    }

                    exif_bytes = piexif.dump(exif_dict)
                    image.save(frame_path, exif=exif_bytes)
                    print(f"GPS data added to frame: {video_name}_frame_{frame_index}")
                else:
                    print(f"No GPS data found for frame: {frame_path}")
            except Exception as e:
                print(f"Image not processed because ----> {e}")
            frame_index += 1
            frame_counter += step_size


if sys.argv[2] == "2":
    print("Elaborating Videos with Timestamps if present:")
    if sys.argv[5] == "0":
        img_form = "jpg"
    else:
        img_form = "png"
    for videoPath in files1:
        process_video_frames(videoPath, sys.argv[1], sys.argv[3], sys.argv[4], img_form)
    print('Done', flush=True)
elif sys.argv[2] == "3":
    print("Elaborating Images:")

    for imagePath in files1:
        if imagePath[-4:] in [".JPG", ".PNG", ".jpg", ".png"]:
            percentage += 100 / len(files1)
            full_imagePath = os.path.join(sys.argv[1], imagePath)
            with open(full_imagePath, 'rb') as image_file:
                img = exif.Image(image_file)
                img.gps_altitude = img.gps_altitude + int(sys.argv[3])
            ext = full_imagePath[-4:]
            tempPath = full_imagePath[:-4]
            with open(f"{tempPath}_mod{ext}", 'wb') as test_image_file:
                test_image_file.write(img.get_file())
            os.remove(full_imagePath)
            print(f"{percentage:.2f}%  --> Changed GPS Altitude of: {full_imagePath[-12:-4]}")
    print("100.00% --> Done!!")
elif sys.argv[2] == "1":
    for imagePath in files:
        percentage += 100 / len(files)
        full_imagePath = imagePath
        print(f"{percentage:.2f}%", end="")
        process_one_th_picture(full_imagePath, float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]),
                               float(sys.argv[6]))
    input("Press any key to exit: ")
