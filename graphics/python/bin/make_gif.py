#!/usr/local/bin/python3

import glob
import os
import sys

import imageio
import natsort
import numpy
from PIL import Image
import random

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

from common import parse_size_str

# Sorters

def naturalized(files, reverse=False):
    return natsort.natsorted(files, reverse=reverse)

def randomized(files):
    random.shuffle(files)
    return files

# Defaults

SIZE = (500, 500)
SORTER = randomized

# Main

def main(folder, output, duration=0.1, size=SIZE, sorter=SORTER):
    with imageio.get_writer(output, mode='I', duration=duration) as writer:
        for filename in sorter(glob.glob("%s/*" % folder)):
            if os.path.isfile(filename):
                image = imageio.imread(filename)
                image = numpy.array(Image.fromarray(image).resize(size))
                writer.append_data(image)
                print(".", sep="", end="", flush=True)

    print("\ndone")



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: %s <folder> <output file> [<duration>] [<size: HxW>]" % sys.argv[0])
        sys.exit(1)

    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], float(sys.argv[3]))
    elif len(sys.argv) == 5:
        main(sys.argv[1], sys.argv[2], float(sys.argv[3]), parse_size_str(sys.argv[4]))
    else:
        main(sys.argv[1], sys.argv[2])
