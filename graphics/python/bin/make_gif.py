#!/usr/local/bin/python3

import glob
import sys

import imageio
import natsort


def main(folder, output, duration=0.1, reverse=True):
    with imageio.get_writer(output, mode='I', duration=duration) as writer:
        for filename in natsort.natsorted(glob.glob("%s/*" % folder), reverse=reverse):
            image = imageio.imread(filename)
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
