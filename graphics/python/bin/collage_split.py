#!/usr/local/bin/python3

import os
import sys

from PIL import Image

# trick for making local package imports work
sys.path.append(os.path.abspath(os.path.curdir))

def collage_split():
    if not len(sys.argv) == 4:
        print("usage: %s <image> <cols> <rows>" % sys.argv[0])
        print("this script takes an image (collage) and splits it into cells")
        print("each cell is saved as an image into an 'output' folder")
        sys.exit(1)

    image_filename = sys.argv[1]
    cols = int(sys.argv[2])
    rows = int(sys.argv[3])

    new_folder = os.path.join(os.path.dirname(image_filename), "output")
    if not os.path.isdir(new_folder):
        os.mkdir(new_folder)

    orig_image = Image.open(image_filename)
    w, h = orig_image.size
    cw = int(w / cols)
    ch = int(h / rows)

    for r in range(rows):
        for c in range(cols):
            cell = orig_image.crop((cw * c, ch * r, cw * (c+1), ch * (r+1)))

            new_image = Image.new('RGB', (cw, ch))
            new_image.paste(cell, (0, 0))
            new_image.save(os.path.join(new_folder, "%d.png" % (r * cols + c)))

            print(".", sep="", end="", flush=True)


if __name__ == "__main__":
    collage_split()

