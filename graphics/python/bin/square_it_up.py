#!/usr/bin/env python3.12

import random
import os
import sys

import matplotlib.pyplot as plt
from numpy import random
from shapely.geometry import box
from shapely.geometry import MultiPolygon

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

def plot_coords(coords):
    pts = list(coords)
    x,y = zip(*pts)
    plt.plot(x,y)

def plot_polys(polys):
    for poly in polys:
        if (not getattr(poly, "exterior", None)):
            print("got line?")

        plot_coords(poly.exterior.coords)

        for hole in poly.interiors:
            plot_coords(hole.coords)

def babushka_squares(output, n):
    boxes = []
    for i in range(n):
        boxes.append(box(i, i, n - i, n - i))
    boxes = MultiPolygon(boxes)
    plot_polys(boxes)
    plt.axis("off")
    plt.savefig(output)

def square_it_up():
    if not len(sys.argv) == 3:
        print("usage: %s <output> <n>" % sys.argv[0])
        sys.exit(1)

    output = sys.argv[1]
    n = int(sys.argv[2])
    babushka_squares(output, n)

if __name__ == "__main__":
    square_it_up()

