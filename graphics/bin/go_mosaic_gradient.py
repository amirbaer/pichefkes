#!/usr/local/bin/python3

import os
import sys

import numpy as np

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

from mosaic import get_parser
from mosaic import save_figure

def get_data_linear(n):
    data = np.array(range(n*n))
    return data.reshape((n,n))

def get_data_squared(n):
    data = np.array([i**2 for i in range(n*n)])
    return data.reshape((n,n))

def get_data_transpose(n):
    data = np.arange(n*n).reshape((n,n))
    return np.transpose(data)

def get_data_sin(n):
    return np.array([np.sin(i) for i in range(n*n)]).reshape((n,n))

def get_data_sin_2(n):
    return np.array([np.sin(i/2) for i in range(n*n)]).reshape((n,n))

def get_data_sin_3(n):
    return np.array([np.sin(i)/i for i in range(n*n)]).reshape((n,n))

def get_data_sin_4(n):
    return np.array([np.sin(i)/20 for i in range(n*n)]).reshape((n,n))

def get_data_square_spiral(n, bug=False):
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

def square_mosaic_gradient(output, n, cmap, size, dpi, interpolation, bug=False):
    data = get_data_square_spiral(n, bug)
    save_figure(data, output, cmap, size, dpi, interpolation)

def square_it_up():
    parser = get_parser()

    parser.add_argument("n", help="size of matrix (n x n)", type=int)
    parser.add_argument("--bug", help="change one thing (only for odd n's)", action="store_true",
            default=False)

    args = parser.parse_args()

    if args.tsn:
        tech_spec_name = "-".join(("%d" % args.n, "%dx%dinch" % args.size, "%ddpi" % args.dpi, args.cmap, args.interpolation, "bug" if args.bug else ""))
        filename, ext = os.path.splitext(args.output)
        args.output = "%s-%s%s" % (filename, tech_spec_name, ext)

    print(args.output, args.n, args.cmap, args.size, args.dpi, args.interpolation, args.bug)
    square_mosaic_gradient(args.output, args.n, args.cmap, args.size, args.dpi, args.interpolation,
            args.bug)

if __name__ == "__main__":
    square_it_up()


