import argparse
import glob
import os


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


def get_image_files_by_folder(folder):
    if not os.path.isdir(folder):
        print("not a folder")
        sys.exit(1)

    files = glob.glob(os.path.join(glob.escape(folder), "*"))
    return sorted(filter(lambda f: os.path.splitext(f)[1][1:] in IMG_EXTS, files))


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

