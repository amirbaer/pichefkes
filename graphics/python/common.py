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


