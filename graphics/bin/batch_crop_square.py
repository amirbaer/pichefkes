#!/usr/local/bin/python3

import os
import sys

from PIL import Image

# trick for making local package imports work
sys.path.append(os.path.abspath(os.path.curdir))

from common import get_image_files_by_folder

def crop_all_square():
    if not len(sys.argv) == 2:
        print("usage: %s <folder>" % sys.argv[0])
        print("this script takes a folder of images, creates a new 'cropped' folder inside it,")
        print("and then generates inside it square crops of all the original images (based on the shorter side's length)")
        sys.exit(1)

    folder = sys.argv[1]
    image_files = get_image_files_by_folder(folder)

    new_folder = os.path.join(folder, "cropped")
    if image_files:
        os.mkdir(new_folder)

    for ifi in image_files:
        orig_image = Image.open(ifi)

        w, h = orig_image.size
        nw = nh = min(w, h)

        new_image = Image.new('RGB', (nw, nh))
        new_image.paste(orig_image, (0, 0))

        new_image.save(os.path.join(new_folder, os.path.basename(ifi)), "PNG")
        print(".", sep="", end="", flush=True)


if __name__ == "__main__":
    crop_all_square()
