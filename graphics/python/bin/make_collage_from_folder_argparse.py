#!/usr/local/bin/python3

import argparse
import glob
import math
import os
import re
import sys

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

from common import CANVAS_SIZES
from common import get_canvas_presets
from common import parse_size_str

from collage import create_collage

def get_parser_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("output", help="output file (PNG)", type=str, nargs=None)
    parser.add_argument("inputs", help="list of input images (individual file or whole folders)", type=str, nargs='+')

    parser.add_argument("--print-canvas-presets", "-pcp", help="print canvas presets", action="version", version=get_canvas_presets())

    dimensions_group = parser.add_mutually_exclusive_group(required=True)
    dimensions_group.add_argument("--canvas-preset", "-cp", help="set collage size from preset", type=str, choices=CANVAS_SIZES.keys(), dest="canvas_preset")
    dimensions_group.add_argument("--size", "-s", help="set custom size for collage (<width>x<height>)", type=parse_size_str)

    parser.add_argument("--size-by-tiles", "-sbt", help="set collage size by number of tiles in each column and row (<cols>x<rows>)",
            type=parse_size_str)

    parser.add_argument("--tile-size", "-ts", help="set size for each individual tile (<width>x<height>", type=parse_size_str)

    parser.add_argument("--randomize-order", "-ro", help="shuffle the input files", action="store_true")
    parser.add_argument("--colorize", "-c", help="add a hue to each input image", action="store_true")

    args = parser.parse_args()
    return args



def main():
    args = get_parser_args()

    if args.canvas_preset and args.canvas_preset in CANVAS_SIZES.keys():
        canvas_size = CANVAS_SIZES[args.canvas_preset]
    else:
        canvas_size = args.size

    #pics = sorted(args.inputs, key=lambda f: int(re.sub('\D', '', f[:f.find(" ")])))
    pics = args.inputs
    count = len(pics)
    print("%d pics found" % count)

    sqrt = math.sqrt(count)
    cols = math.ceil(sqrt)
    rows = cols * (cols - 1) < count and math.ceil(sqrt) or math.floor(sqrt)

    print("sqrt(%d) = %f" % (count, sqrt))
    print("creating an %d x %d collage" % (cols, rows))
    create_collage(pics, *canvas_size, cols, rows, args.output)


if __name__ == "__main__":
    main()
