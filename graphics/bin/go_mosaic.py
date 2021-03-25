#!/usr/local/bin/python3

import argparse
import random
import re
import os
import sys


import matplotlib.pyplot as plt
from numpy import random
from shapely.geometry import box
from shapely.geometry import MultiPolygon

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

# Color Maps: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

def square_mosaic(output, n, cmap, size, dpi, interpolation):
    data = random.random((n,n))
    img = plt.imshow(data, interpolation=interpolation)
    img.set_cmap(cmap)
    plt.axis('off')
    fig = plt.gcf()
    fig.set_size_inches(*size)
    fig.set_dpi(dpi)
    fig.savefig(output, bbox_inches='tight')

def size_str(arg_value, pat=re.compile(r"^(\d+)x(\d+)$")):
    match = pat.match(arg_value)
    if not match:
        raise argparse.ArgumentTypeError
    return tuple(map(int, match.groups()))

def get_parser_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("output", help="output file (PNG)", type=str)
    parser.add_argument("n", help="size of matrix (n x n)", type=int)
    parser.add_argument("--cmap", "-c", help="set color map", type=str, choices=plt.cm._cmap_registry.keys())
    parser.add_argument("--dpi", "-d", help="set dots (pixels) per inch", type=int, default=100)
    parser.add_argument("--size", "-s", help="set size in inches", type=size_str, default="30x30")
    parser.add_argument("--interpolation", "-i", help="set interpolation method", type=str, default='nearest', choices=('none', 'antialiased', 'nearest', 'bilinear',
            'bicubic', 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos'))
    parser.add_argument("--tech-spec-name", "-t", help="append run parameters to output name", dest='tsn', action='store_true')


    args = parser.parse_args()
    return args

def square_it_up():
    args = get_parser_args()

    if args.tsn:
        tech_spec_name = "-".join(("%d" % args.n, "%dx%dinch" % args.size, "%ddpi" % args.dpi, args.cmap, args.interpolation))
        filename, ext = os.path.splitext(args.output)
        args.output = "%s-%s%s" % (filename, tech_spec_name, ext)

    print(args.output, args.n, args.cmap, args.size, args.dpi, args.interpolation)
    square_mosaic(args.output, args.n, args.cmap, args.size, args.dpi, args.interpolation)

if __name__ == "__main__":
    square_it_up()

