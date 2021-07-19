#!/usr/local/bin/python3

import glob
import os
import sys

import imageio
import natsort
import numpy
from PIL import Image


def main(folder, output, duration=0.1, reverse=False):
    with imageio.get_writer(output, mode='I', duration=duration) as writer:
        for filename in natsort.natsorted(glob.glob("%s/*" % folder), reverse=reverse):
            if os.path.isfile(filename):
                image = imageio.imread(filename)
                image = numpy.array(Image.fromarray(image).resize((500,500)))
                writer.append_data(image)
                print(".", sep="", end="", flush=True)

    print("\ndone")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: %s <folder> <output file> [<duration>]" % sys.argv[0])
        sys.exit(1)

    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], float(sys.argv[3]))
    else:
        main(sys.argv[1], sys.argv[2])
