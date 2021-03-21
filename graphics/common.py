import glob
import os


IMG_EXTS = ["PNG", "JPG", "JPEG"]
IMG_EXTS.extend([ie.lower() for ie in IMG_EXTS])


def get_image_files_by_folder(folder):
    if not os.path.isdir(folder):
        print("not a folder")
        sys.exit(1)

    files = glob.glob(os.path.join(glob.escape(folder), "*"))
    return sorted(filter(lambda f: os.path.splitext(f)[1][1:] in IMG_EXTS, files))
