#!/usr/local/bin/python3

import os
import sys

import numpy as np

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

from mosaic import get_parser
from mosaic import save_figure


def square_mosaic_random(output, n, cmap, size, dpi, interpolation):
    data = np.random.random((n,n))
    save_figure(data, output, cmap, size, dpi, interpolation)

def square_it_up():
    parser = get_parser()

    parser.add_argument("n", help="size of matrix (n x n)", type=int)

    args = parser.parse_args()

    if args.tsn:
        tech_spec_name = "-".join(("%d" % args.n, "%dx%dinch" % args.size, "%ddpi" % args.dpi, args.cmap, args.interpolation))
        filename, ext = os.path.splitext(args.output)
        args.output = "%s-%s%s" % (filename, tech_spec_name, ext)

    print(args.output, args.n, args.cmap, args.size, args.dpi, args.interpolation)
    square_mosaic_random(args.output, args.n, args.cmap, args.size, args.dpi, args.interpolation)

if __name__ == "__main__":
    square_it_up()

