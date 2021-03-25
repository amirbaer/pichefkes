import argparse
import re

import matplotlib.pyplot as plt

# INFO: Color Maps: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

def save_figure(data, output, cmap, size, dpi, interpolation):
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

def get_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("output", help="output file (PNG)", type=str)
    parser.add_argument("--cmap", "-c", help="set color map", type=str, choices=plt.cm._cmap_registry.keys())
    parser.add_argument("--dpi", "-d", help="set dots (pixels) per inch", type=int, default=100)
    parser.add_argument("--size", "-s", help="set size in inches", type=size_str, default="30x30")
    parser.add_argument("--interpolation", "-i", help="set interpolation method", type=str, default='nearest', choices=('none', 'antialiased', 'nearest', 'bilinear',
            'bicubic', 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos'))
    parser.add_argument("--tech-spec-name", "-t", help="append run parameters to output name", dest='tsn', action='store_true')


    return parser
