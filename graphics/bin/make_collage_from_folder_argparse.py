#!/usr/local/bin/python3

import glob
import math
import os
import sys

# trick for making local package imports work
sys.path.append(os.path.abspath(os.path.curdir))

from common import get_parser_args
from common import CANVAS_SIZES

from collage import create_collage


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
