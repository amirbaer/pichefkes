#!/usr/local/bin/python3

import argparse
import glob
import math
import os
import random
import re
import sys

from PIL import Image, ImageEnhance
import numpy as np
from termcolor import colored


"""
Usage:

make_collage <output> <folder>
make_collage <output> <list of files>

# set dimensions by size of entire collage
--dimensions [instagram-square(is)|instagram-portrait(ip)|...]
--print-dimensions
--size <width>x<height>

--size-by-tiles <width>x<height>

# set dimensions by size of an individual tile
--tile-size <width>x<height> 

--randomize-order
--colorize


Algorithm:

- Sets canvas size
- Finds all images
- Resizes images (size either explicitly set or derived from canvas size / tile size)
- Applies modifications to images (rotation, color)
- Organizes images in grid
    - if there are too few, that's OK
    - if there are too many, some get left out
"""

IMG_EXTS = ["PNG", "JPG", "JPEG"]
IMG_EXTS.extend([ie.lower() for ie in IMG_EXTS])

CANVAS_SIZES = {
    "instagram-square":     (1080, 1080),
    "is":                   (1080, 1080),
    "instagram-portrait":   (1080, 1350),
    "ip":                   (1080, 1350),
    "facebook-square":      (2048, 2048),
    "fs":                   (2048, 2048),
    "facebook-portrait":    (4096, 2048),
    "fp":                   (4096, 2048),
}




def parse_size_str(sstr):
    match = re.findall(r'(\d+)x(\d+)', sstr)

    if match:
        x, y = match[0]
        return (int(x), int(y))

    raise argparse.ArgumentTypeError("bad size format")

def get_canvas_presets():
    # reverse dict: { (1080, 1080): ["instagram-square", "is"] }
    rev = {}
    for k, v in CANVAS_SIZES.items():
        if v not in rev:
            rev[v] = [k]
        else:
            rev[v].append(k)

    res = "Canvas Size Presets:\n"
    for k, v in rev.items():
        line = v[0]
        if len(v) > 1:
            line += " (%s)" % ("|".join(v[1:]))
        line += ": %sx%s" % k
        res += "%s\n" % line

    return res


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


def create_collage(canvas_size, paths, cols, rows, output):
    w, h = Image.open(paths[0]).size

    collage_width = cols * w
    collage_height = rows * h

    new_image = Image.new('RGB', (collage_width, collage_height))

    cursor = (0,0)
    for path in paths:
        # place image
        image = Image.open(path)
        #image = image.resize(THUMBNAIL_SIZE)

        new_image.paste(image, cursor)

        # move cursor
        y = cursor[1]
        x = cursor[0] + w
        if cursor[0] >= (collage_width - w):
            y = cursor[1] + h
            x = 0
        cursor = (x, y)

    new_image.save(output, "PNG")



def get_wh_by_nr(n, ratio=1):
    # w*h >= n
    # h = ratio * w
    w = math.sqrt(n / ratio)
    h = w * ratio

    return w, h


def get_dimensions_by_num_items(n, ratio):
    w, h = get_wh_by_nr(n, ratio)

    f = math.floor
    c = math.ceil

    if f(w)*f(h) >= n:
        return f(w), f(h)
    elif f(w)*c(h) >= n:
        return f(w), c(h)
    elif c(w)*f(h) >= n:
        return c(w), f(h)
    elif c(w)*c(h) >= n:
        return c(w), c(h)
    else:
        raise Exception("something went wrong, equation might be wrong")

def color_wh_per_n(h, w, n, minimum=None, auto_choose=None):
    num_str = f"{w*h:5}"
    p = w*h
    if auto_choose and p == auto_choose:
        return colored(num_str, "yellow")
    elif minimum and p == minimum:
        return colored(num_str, "blue")
    elif w*h >= n:
        return colored(num_str, "green")
    else:
        return colored(num_str, "red")

def print_table_of_dimension_options(n, ratio, pad=1, minimum=None):
    w, h = get_wh_by_nr(n, ratio)

    print(" ", *(f"{i:5}" for i in range(1, math.ceil(w) + pad))) # heading
    for row in range(1, math.ceil(h) + pad):
        print(row, *(color_wh_per_n(row, col, n, minimum) for col in range(1, math.ceil(w) + pad)))


def print_table_of_dimension_options_highlight_best(n, ratio, pad=1):
    w, h = get_wh_by_nr(n, ratio)

    options = []
    for i in range(math.ceil(h) + pad):
        for j in range(math.ceil(w) + pad):
            if i*j >= n:
                options.append(i*j)

    minimum = sorted(options)[0]
    print_table_of_dimension_options(n, ratio, pad, minimum)


def get_image_files_by_folder(folder):
    if not os.path.isdir(folder):
        print("not a folder")
        sys.exit(1)

    files = glob.glob(os.path.join(glob.escape(folder), "*"))
    return sorted(filter(lambda f: os.path.splitext(f)[1][1:] in IMG_EXTS, files))


def main():

    if not len(sys.argv) >= 2:
        print("usage: %s <folder> [<ratio>] [<pad>]" % sys.argv[0])
        sys.exit(1)

    files = get_image_files_by_folder(sys.argv[1])

    ratio = 1
    if len(sys.argv) >= 3:
        ratio = float(sys.argv[2])
        
    pad = 1
    if len(sys.argv) >= 4:
        pad = int(sys.argv[3])

    nfiles = len(files)
    if nfiles < 1:
        print("not enough images")
        sys.exit(1)

    w, h = get_dimensions_by_num_items(nfiles, ratio)

    print("n: %s, w: %s, h: %s, w*h: %s, h/w: %s, extras: %s" % (nfiles, w, h, w*h, h/w, w*h - nfiles))
    print_table_of_dimension_options_highlight_best(nfiles, ratio, pad)




def crop_all_square():
    if not len(sys.argv) == 2:
        print("usage: %s <folder>" % sys.argv[0])
        sys.exit(1)

    folder = sys.argv[1]
    image_files = get_image_files_by_folder(folder)

    new_folder = os.path.join(folder, "cropped")
    if image_files:
        os.mkdir(new_folder)

    for ifi in image_files:
        orig_image = Image.open(ifi)

        w, h = orig_image.size
        nw = nh = min(w, h)

        new_image = Image.new('RGB', (nw, nh))
        new_image.paste(orig_image, (0, 0))

        new_image.save(os.path.join(new_folder, os.path.basename(ifi)), "PNG")
        print(".", sep="", end="", flush=True)






def cmd_main():
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
    crop_all_square()
