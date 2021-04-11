#!/usr/local/bin/python3

import argparse
import re
import os
import sys


import matplotlib.pyplot as plt
import numpy as np

# INFO: Color Maps: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

from collage import get_dimensions_by_num_items
from mosaic import get_parser
from mosaic import save_figure


def square_mosaic_file_data(output, input_file, cmap, size, dpi, interpolation):
    data = np.frombuffer(open(input_file, 'rb').read(), "uint8")
    rows, cols = get_dimensions_by_num_items(len(data))
    ncells = rows * cols
    data = np.concatenate((data, np.array([0] * (ncells - len(data)))))
    data = data.reshape((rows, cols))
    save_figure(data, output, cmap, size, dpi, interpolation)

def square_it_up():
    parser = get_parser()

    parser.add_argument("input", help="input file as data for mosaic", type=str)

    args = parser.parse_args()

    if args.tsn:
        tech_spec_name = "-".join(("%s" % os.path.basename(args.input), "%dx%dinch" % args.size, "%ddpi" % args.dpi,
            args.cmap, args.interpolation))
        filename, ext = os.path.splitext(args.output)
        args.output = "%s-%s%s" % (filename, tech_spec_name, ext)

    print(args.output, args.input, args.cmap, args.size, args.dpi, args.interpolation)
    square_mosaic_file_data(args.output, args.input, args.cmap, args.size, args.dpi, args.interpolation)

if __name__ == "__main__":
    square_it_up()

