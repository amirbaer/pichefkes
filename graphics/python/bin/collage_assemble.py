#!/usr/local/bin/python3

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
    def __init__(self, cell_images, empty_cell_image, cols, rows, num_empty_cells=0, mode="random"):
        self.cell_images = cell_images
        self.empty_cell_image = empty_cell_image
        self.cols = cols
        self.rows = rows
        self.ncells = self.cols * self.rows
        self.num_empty_cells = num_empty_cells
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
        self._empty_cell_image = Image.open(self.empty_cell_image)

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

        


def collage_assemble():
    if not len(sys.argv) in (5, 6, 7):
        print("usage: %s <output> <cell folder> <cols> <rows> [<num empty cells>] [<mode>]" % sys.argv[0])
        print("this script creates a (%dx%dpx) collage in the specified dimensions (cols x rows)" % OUTPUT_SIZE)
        print("it fills the collage with images from the cell folder")
        print("- num cells = cols X rows")
        print("- each cell will contain an image (except for empty cells)")
        print("- all images are resized to the size of a cell")
        print("- assuming last image in cell folder is an empty cell")
        sys.exit(1)

    output = sys.argv[1]
    
    cell_folder = sys.argv[2]
    if not os.path.isdir(cell_folder):
        print("not a folder: %s" % cell_folder)
        sys.exit(1)

    cell_images = get_image_files_by_folder(cell_folder)
    empty_cell_image = cell_images.pop()

    cols = int(sys.argv[3])
    rows = int(sys.argv[4])

    num_empty_cells = 0
    if len(sys.argv) >= 6:
        num_empty_cells = int(sys.argv[5])

    mode = "random"
    if len(sys.argv) == 7:
        mode = sys.argv[6]
        if not mode in MODES:
            print("bad mode: %s" % mode)
            sys.exit(1)

    pop_collage = PopulationCollage(cell_images, empty_cell_image, cols, rows, num_empty_cells, mode)

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
    collage_assemble()

