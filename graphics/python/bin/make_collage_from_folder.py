#!/usr/local/bin/python3

import glob
import math
import os
import sys

# trick for making local package imports work
sys.path.append(os.path.abspath(os.path.curdir))

from common import get_image_files_by_folder

from collage import create_collage
from collage import get_dimensions_by_num_items
from collage import DEFAULT_CANVAS_SIZE


def main():
    if not len(sys.argv) >= 2:
        print("usage: %s <folder> [<hw-ratio>]" % sys.argv[0])
        sys.exit(1)

    ratio = 1
    if len(sys.argv) >= 3:
        ratio = float(sys.argv[2])

    files = get_image_files_by_folder(sys.argv[1])
    nfiles = len(files)
    print("%d pics found" % nfiles)

    canvas_width, canvas_height = DEFAULT_CANVAS_SIZE
    cols, rows = get_dimensions_by_num_items(nfiles, ratio)
    print("canvas size (w X h): %d x %d px" % (canvas_width, canvas_height))
    print("grid dimensions (c X r) %d x %d" % (cols, rows))
    print("ratio: %.2f" % (rows/cols))


    output = "collage.png"
    create_collage(files, canvas_width, canvas_height, cols, rows, output)


if __name__ == "__main__":
    main()
