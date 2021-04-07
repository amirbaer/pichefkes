import argparse
import random
import re

import matplotlib.pyplot as plt
import numpy as np

# INFO: Color Maps: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html

## Data Arrangement ##

def get_data_linear(n, *args, **kwargs):
    data = np.array(range(n*n))
    return data.reshape((n,n))

def get_data_squared(n, *args, **kwargs):
    data = np.array([i**2 for i in range(n*n)])
    return data.reshape((n,n))

def get_data_transpose(n, *args, **kwargs):
    data = np.arange(n*n).reshape((n,n))
    return np.transpose(data)

def get_data_sin(n, *args, **kwargs):
    return np.array([np.sin(i) for i in range(n*n)]).reshape((n,n))

def get_data_sin_2(n, *args, **kwargs):
    return np.array([np.sin(i/2) for i in range(n*n)]).reshape((n,n))

def get_data_sin_3(n, *args, **kwargs):
    return np.array([np.sin(i)/i for i in range(n*n)]).reshape((n,n))

def get_data_sin_4(n, *args, **kwargs):
    return np.array([np.sin(i)/20 for i in range(n*n)]).reshape((n,n))

def get_data_square_spiral(n, bug=False, *args, **kwargs):
    data = [[0 for i in range(n)] for j in range(n)]
    cur_val = 0

    for k in range(n//2):
        i = k
        # -> across
        for j in range(k, n - k):
            data[i][j] = cur_val
            cur_val += 1
        # down
        for i in range(k + 1, n - 1 - k):
            data[i][j] = cur_val
            cur_val += 1
        # <- back
        i += 1
        for j in range(n - 1 - k, k - 1, -1):
            data[i][j] = cur_val
            cur_val += 1
        # up
        for i in range(n - 2 - k, k, -1):
            data[i][j] = cur_val
            cur_val += 1

    if n % 2 == 1:
        if not bug:
            j += 1
            data[i][j] = cur_val
        else:
            data[2 * k + 1][2 * k + 1] = cur_val 

    return np.array(data)

def get_data_comprehensive_random(n, *args, **kwargs):
    data = list(range(n*n))
    random.shuffle(data)
    return np.array(data).reshape((n,n))

def get_data_random(n, *args, **kwargs):
    return np.random.random((n,n))

DATA_MODES = {
    "linear":                   get_data_linear,
    "squared":                  get_data_squared,
    "transpose":                get_data_transpose,
    "sin":                      get_data_sin,
    "sin2":                     get_data_sin_2,
    "sin3":                     get_data_sin_3,
    "sin4":                     get_data_sin_4,
    "square-spiral":            get_data_square_spiral,
    "random":                   get_data_random,
    "comprehensive-random":     get_data_comprehensive_random,
}

def get_data_modes():
    return DATA_MODES.keys()

def get_data(mode, n, *args, **kwargs):
    if not mode in DATA_MODES:
        raise ValueError("mode must be one of: " + ", ".join(DATA_MODES.keys()))

    return DATA_MODES[mode](n, *args, **kwargs)

## IN / OUT

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

    parser.add_argument("mode", help="data arrangement pattern", type=str, choices=get_data_modes())
    parser.add_argument("n", help="size of matrix (n x n)", type=int)
    parser.add_argument("output", help="output file (PNG)", type=str)
    parser.add_argument("--cmap", "-c", help="set color map", type=str, choices=plt.cm._cmap_registry.keys(), default="viridis")
    parser.add_argument("--dpi", "-d", help="set dots (pixels) per inch", type=int, default=100)
    parser.add_argument("--size", "-s", help="set size in inches", type=size_str, default="30x30")
    parser.add_argument("--interpolation", "-i", help="set interpolation method", type=str, default='nearest', choices=('none', 'antialiased', 'nearest', 'bilinear',
            'bicubic', 'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos'))
    parser.add_argument("--tech-spec-name", "-t", help="append run parameters to output name", dest='tsn', action='store_true')

    return parser

