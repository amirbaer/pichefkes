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

import math
from termcolor import colored

from PIL import Image


DEFAULT_CANVAS_SIZE = (3000, 3000)


def create_collage(paths, canvas_width, canvas_height, cols, rows, output):
    canvas_width, canvas_height = DEFAULT_CANVAS_SIZE
    cell_width, cell_height = get_cell_size_by_canvas_and_grid(canvas_width, canvas_height, cols, rows)

    new_image = Image.new('RGB', DEFAULT_CANVAS_SIZE)
    cursor = (0,0)
    for path in paths:
        # place image
        image = Image.open(path)
        image = image.resize((cell_width, cell_height))

        new_image.paste(image, cursor)

        # move cursor
        y = cursor[1]
        x = cursor[0] + cell_width
        if cursor[0] >= (canvas_width - cell_width):
            y = cursor[1] + cell_height
            x = 0
        cursor = (x, y)

    new_image.save(output, "PNG")



# DIMENSIONS #

"""
3 types of metrics for the size and shape of the collage:
# grid dimensions = num cols, num rows
# cell size = cell_width, cell_height
# canvas dimensions = width_px, height_px

they are inter-dependent
so if you configure 2 the 3rd is derived from them

3 ways of deriving 

# cell size, grid dimensions -> canvas dimensions
# canvas_height = cell_height * num_rows
# canvas_width = cell_width * num_cols

# canvas dimensions, grid dimensions -> cell_size
# cell_height = canvas_height / num_rows
# cell_width = canvas_width / num_cols

# canvas dimensions, cell size -> grid dimensions
# num_rows = canvas_height / cell_height
# num_cols = canvas_width / cell_width
"""

def get_cell_size_by_canvas_and_grid(canvas_width, canvas_height, grid_cols, grid_rows):
    cell_width = int(canvas_width / grid_cols)
    cell_height = int(canvas_height / grid_rows)
    return (cell_width, cell_height)


def get_wh_by_nr(n, ratio=1):
    # w*h >= n
    # h = ratio * w
    w = math.sqrt(n / ratio)
    h = w * ratio

    return w, h

def get_dimensions_by_num_items(n, ratio=1):
    "determine width & height from num of cells & desired h/w ratio"
    w, h = cols, rows = get_wh_by_nr(n, ratio)

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

