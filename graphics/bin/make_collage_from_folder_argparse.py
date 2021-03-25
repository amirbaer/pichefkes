#!/usr/local/bin/python3

import glob
import math
import os
import sys

# trick for making local package imports work
sys.path.append(os.path.abspath(os.path.curdir))

from common import CANVAS_SIZES

from collage import create_collage

def get_parser_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("output", help="output file (PNG)", type=str, nargs=1)
    parser.add_argument("inputs", help="list of input images (individual file or whole folders)", type=str, nargs='+')

    parser.add_argument("--print-canvas-presets", "-pcp", help="print canvas presets", action="version", version=get_canvas_presets())

    dimensions_group = parser.add_mutually_exclusive_group(required=True)
    dimensions_group.add_argument("--canvas-preset", "-cp", help="set collage size from preset", type=str, choices=CANVAS_SIZES.keys())
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

    if args.dimensions in CANVAS_SIZES.keys():
        canvas_size = CANVAS_SIZES[args.dimensions]
    else:
        canvas_size = (args.width, args.height)

    pics = sorted(glob.glob(args.glob))
    count = len(pics)
    print("%d pics found" % count)

    sqrt = math.sqrt(count)
    cols = math.ceil(sqrt)
    rows = cols * (cols - 1) < count and math.floor(sqrt) or math.ceil(sqrt)

    print("sqrt(%d) = %f" % (count, sqrt))
    print("creating an %d x %d collage" % (cols, rows))
    create_collage(canvas_size, pics, cols, rows, output)


if __name__ == "__main__":
    main()
