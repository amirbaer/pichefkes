#!/usr/bin/env python3

from datetime import datetime, timedelta
import exifread
import os
import subprocess
import sys

TIME_FORMAT = '%Y:%m:%d %H:%M:%S'

def shift_exif_timestamps(directory, years=0, months=0, days=0, hours=0, minutes=0):
    # Get list of JPEG files in the directory
    jpg_files = [file for file in os.listdir(directory) if file.lower().endswith('.jpg')]

    # Calculate the timedelta for the shift
    delta = timedelta(
        days=days,
        seconds=hours * 3600 + minutes * 60,
        weeks=years * 52 + months * 4  # Assuming 1 month ≈ 4 weeks
    )

    for jpg_file in jpg_files:
        file_path = os.path.join(directory, jpg_file)
        
        # Open the image file for reading EXIF data
        f = open(file_path, 'rb')
        tags = exifread.process_file(f)

        # Check if EXIF data contains datetime information
        original_time = new_time = None
        if 'EXIF DateTimeOriginal' in tags:
            for tag in tags.keys():
                if tag.startswith('EXIF DateTime') or tag == 'File Modification Date/Time' or tag == 'Modify Date' or tag == 'Create Date':
                    original_time = datetime.strptime(str(tags[tag]), TIME_FORMAT)
                    new_time = original_time + delta

                    # Update EXIF timestamp
                    tags[tag] = new_time.strftime(TIME_FORMAT)

            # Construct new EXIF data string
            exif_string = ''.join(f"{tag}: {tags[tag]}\n" for tag in tags.keys())
            f.close()

            f = open(file_path, 'wb')
            f.write(exif_string.encode('utf-8'))
            f.close()
            print(f"Timestamp shifted for {jpg_file}: %s -> %s" % (original_time.strftime(TIME_FORMAT), new_time.strftime(TIME_FORMAT)))


def shift_exif_timestamps_cmd(directory, years=0, months=0, days=0, hours=0, minutes=0):
    # Get list of JPEG files in the directory
    jpg_files = [file for file in os.listdir(directory) if file.lower().endswith('.jpg')]

    # Calculate the timedelta for the shift
    delta = timedelta(
        days=days,
        seconds=hours * 3600 + minutes * 60,
        weeks=years * 52 + months * 4  # Assuming 1 month ≈ 4 weeks
    )

    for jpg_file in jpg_files:
        file_path = os.path.join(directory, jpg_file)
        
        # Construct the exiftool command
        command = [
            'exiftool',
            '-AllDates+=',
            f'{delta.days}d{delta.seconds//3600}h{delta.seconds%3600//60}m',
            file_path
        ]

        # Execute the command
        subprocess.run(command)

        print(f"Timestamp shifted for {jpg_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <directory> <years> <months> <days> <hours> <minutes>")
        sys.exit(1)

    directory = sys.argv[1]
    years = int(sys.argv[2])
    months = int(sys.argv[3])
    days = int(sys.argv[4])
    hours = int(sys.argv[5])
    minutes = int(sys.argv[6])

    if not os.path.isdir(directory):
        print("Error: Directory does not exist.")
        sys.exit(1)

    shift_exif_timestamps(directory, years, months, days, hours, minutes)

