#!/usr/local/bin/python3

import os
import sys

# trick for making local package imports work
sys.path.append(os.path.abspath(os.path.curdir))

from common import get_image_files_by_folder
from collage import get_dimensions_by_num_items
from collage import print_table_of_dimension_options_highlight_best


def main():

    if not len(sys.argv) >= 2:
        print("usage: %s <folder or nItems> [<ratio>] [<pad table>]" % sys.argv[0])
        sys.exit(1)

    nfiles = 0
    if sys.argv[1].isdigit():
        nfiles = int(sys.argv[1])
    else:
        files = get_image_files_by_folder(sys.argv[1])
        nfiles = len(files)

    if nfiles < 1:
        print("not enough images (<1)")
        sys.exit(1)

    ratio = 1
    if len(sys.argv) >= 3:
        ratio = float(sys.argv[2])
        
    pad = 1
    if len(sys.argv) >= 4:
        pad = int(sys.argv[3])


    w, h = get_dimensions_by_num_items(nfiles, ratio)

    print("n: %s, w: %s, h: %s, w*h: %s, h/w: %s, extras: %s" % (nfiles, w, h, w*h, h/w, w*h - nfiles))
    print_table_of_dimension_options_highlight_best(nfiles, ratio, pad)


if __name__ == "__main__":
    main()
