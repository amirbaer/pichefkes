#!/usr/local/bin/python3

import argparse
import random
import os
import sys

from PIL import Image

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

from common import get_image_files_by_folder

OUTPUT_SIZE = (3000, 3000)
MODES = ("random", "start-empty", "end-empty", "grouped")

class PopulationCollage:
    def __init__(self, cell_images, cols, rows, num_empty_cells=0, empty_cell_image=None, bg_color="white", mode="random"):
        self.cell_images = cell_images

        self.cols = cols
        self.rows = rows
        self.ncells = self.cols * self.rows

        self.empty_cell_image = empty_cell_image
        self.num_empty_cells = num_empty_cells
        self.bg_color = bg_color

        self.mode = mode

        self.build_collage()

    def get_image(self, col, row):
        i = self.get_index_by_cell(col, row)
        img = self._map[i]
        if img == "empty":
            return self._empty_cell_image
        else:
            return self._image_pool[img]

    def get_index_by_cell(self, col, row):
        return (row * self.cols + col)

    def build_collage(self):
        self._build_image_pool()
        self._build_map()

    def _build_image_pool(self):
        self._image_pool = []
        for ci in self.cell_images:
            self._image_pool.append(Image.open(ci))
        if self.empty_cell_image:
            self._empty_cell_image = Image.open(self.empty_cell_image)
        else:
            self._empty_cell_image = Image.new('RGB', self._image_pool[0].size, self.bg_color)

    def _build_map(self):
        self._map = []
        if self.mode == "random":
            self._map = ["empty"] * self.num_empty_cells
            indices = list(range(len(self._image_pool)))
            for i in range(self.ncells - self.num_empty_cells):
                self._map.append(indices.pop(random.randrange(len(indices))))
            random.shuffle(self._map)

        elif self.mode == "start-empty":
            self._map = ["empty"] * self.num_empty_cells
            for i in range(self.ncells - self.num_empty_cells):
                self._map.append(i)

        elif self.mode == "end-empty":
            for i in range(self.ncells - self.num_empty_cells):
                self._map.append(i)
            self._map += ["empty"] * self.num_empty_cells

        elif self.mode == "grouped":
            self._map = ["empty"] * self.num_empty_cells
            for i in range(self.ncells - self.num_empty_cells):
                self._map.append(i)
            self._map.sort(key=str)

        


def collage_assemble(output, image_files, cols, rows, num_empty_cells, empty_cell_image, bg_color, mode):
    pop_collage = PopulationCollage(image_files, cols, rows, num_empty_cells, empty_cell_image, bg_color, mode)

    out_image = Image.new('RGB', OUTPUT_SIZE)

    w, h = OUTPUT_SIZE
    cw = int(w / cols)
    ch = int(h / rows)

    for r in range(rows):
        for c in range(cols):
            cell = pop_collage.get_image(c, r)
            cell = cell.resize((cw, ch)) #TODO: not scaled
            out_image.paste(cell, (c * cw, r * ch))
            print(".", sep="", end="", flush=True)

    out_image.save(output)
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(sys.argv[0], description="create a (%dx%dpx) collage (photo grid) in the specified dimensions (cols x rows)" % OUTPUT_SIZE)

    parser.add_argument("-i", "--image", dest="images", nargs="+", required=False, help="input file")
    parser.add_argument("-I", "--image-folder", dest="image_folder", required=False, help="input folder")
    parser.add_argument("-o", "--output", required=True, help="output file")
    parser.add_argument("-ei", "--empty-image", dest="empty_image", required=False, help="empty cell image")

    parser.add_argument("-c", "--cols", type=int, required=True, help="number of columns in the photo grid")
    parser.add_argument("-r", "--rows", type=int, required=True, help="number of rows in the photo grid")
    parser.add_argument("-ne", "--num-empty", dest="num_empty_cells", type=int, required=False, default=0, help="how many empty slots to leave in the photo grid")
    parser.add_argument("-bg", "--background", type=str, required=False, default="white", help="color of background (empty cells)")
    parser.add_argument("-m", "--mode", type=str, required=False, choices=MODES, default="random", help="mode of arranging the photos in the grid")

    args = parser.parse_args()

    image_files = []
    if args.image_folder:
        image_files += get_image_files_by_folder(args.image_folder)
    if args.images:
        image_files += args.images

    collage_assemble(args.output, image_files, args.cols, args.rows, args.num_empty_cells, args.empty_image, args.background, args.mode)

