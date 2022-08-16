#!/usr/local/bin/python3

import argparse
import os
import sys

from PIL import Image

# trick for making local package imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common import get_image_files_by_folder

def crop_all_square(output_folder, image_files, frame_size=0, background_color="white"):
    for ifi in image_files:
        orig_image = Image.open(ifi)

        fz = frame_size
        w, h = orig_image.size
        nw = nh = min(w, h)
        #cropped_image = orig_image.crop((fz, fz, nw - fz, nh - fz)) # crop from all sides
        cropped_image = orig_image.crop((0, 0, nw - (2 * fz), nh - (2 * fz))) # crop from bottom right
        #cropped_image = orig_image.resize((nw - (2 * fz), nh - (2 * fz)))

        new_image = Image.new('RGB', (nw, nh), color=background_color)
        new_image.paste(cropped_image, (fz, fz, nw - fz, nh - fz))

        new_image.save(os.path.join(output_folder, os.path.basename(ifi)), "PNG")
        print(".", sep="", end="", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(sys.argv[0], description="crop images and add a frame")

    parser.add_argument("-i", "--image", dest="images", nargs="+", required=False, help="input file")
    parser.add_argument("-I", "--image-folder", dest="image_folder", required=False, help="input folder")
    parser.add_argument("-o", "--output", required=True, help="output folder")

    parser.add_argument("-f", "--frame", type=int, default=0, required=False, help="frame size")
    parser.add_argument("-b", "--background", type=str, default="white", required=False, help="background color")

    args = parser.parse_args()

    if not args.images and not args.image_folder:
        print("error: no input files specified")
        sys.exit(1)

    image_files = []
    if args.image_folder:
        image_files += get_image_files_by_folder(args.image_folder)
    if args.images:
        image_files.append(args.images)

    crop_all_square(args.output, image_files, frame_size=args.frame, background_color=args.background)
