#!/usr/bin/env python3

import argparse
import os
import sys

import cv2
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageOps

# trick for making local package imports work
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), ".."))

from common import parse_size_str


def load_image(filename):
    """Load image with EXIF rotation applied."""
    image = Image.open(filename)
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")


def stabilize_images(images):
    """Align all images to the first image using translation only, then crop."""
    if len(images) < 2:
        return images

    ref_img = np.array(images[0])
    ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_RGB2GRAY)
    h, w = ref_img.shape[:2]

    shifts = [(0, 0)]  # First image has no shift

    # Calculate shifts for each image using phase correlation
    for img in images[1:]:
        img_arr = np.array(img)
        img_gray = cv2.cvtColor(img_arr, cv2.COLOR_RGB2GRAY)

        # Phase correlation to find shift
        shift, _ = cv2.phaseCorrelate(ref_gray.astype(np.float64), img_gray.astype(np.float64))
        shifts.append((shift[0], shift[1]))
        print(".", end="", flush=True)

    # Calculate crop region to keep only the common area
    max_shift_x = max(abs(s[0]) for s in shifts)
    max_shift_y = max(abs(s[1]) for s in shifts)
    crop_margin = int(max(max_shift_x, max_shift_y)) + 5

    # Apply shifts and crop
    stabilized = []
    for img, (dx, dy) in zip(images, shifts):
        img_arr = np.array(img)

        # Create translation matrix
        matrix = np.float32([[1, 0, dx], [0, 1, dy]])
        shifted = cv2.warpAffine(img_arr, matrix, (w, h))

        # Crop to common area
        cropped = shifted[crop_margin:h-crop_margin, crop_margin:w-crop_margin]
        stabilized.append(Image.fromarray(cropped))

    print(f" (crop margin: {crop_margin}px)", end="")
    return stabilized


def main(output, input_files, duration=0.1, size=None, stabilize=False):
    # Load all images first
    images = []
    for filename in input_files:
        if os.path.isfile(filename):
            images.append(load_image(filename))
            print(".", end="", flush=True)

    if not images:
        print("No valid images found")
        return

    print(f" loaded {len(images)} images")

    # Determine size from first image if not specified
    if size is None:
        size = images[0].size

    # Resize all images
    images = [img.resize(size) for img in images]

    # Stabilize if requested
    if stabilize:
        print("Stabilizing: ", end="", flush=True)
        images = stabilize_images(images)
        print(" done")

    # Write GIF
    print("Writing GIF: ", end="", flush=True)
    duration_ms = int(duration * 1000)  # Convert seconds to milliseconds
    with imageio.get_writer(output, mode='I', duration=duration_ms, loop=0) as writer:
        for image in images:
            writer.append_data(np.array(image))
            print(".", end="", flush=True)

    print(" done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a GIF from input images")
    parser.add_argument("output", help="Output GIF file")
    parser.add_argument("input_files", nargs="+", help="Input image files")
    parser.add_argument("-d", "--duration", type=float, default=0.1, help="Duration per frame in seconds (default: 0.1)")
    parser.add_argument("-s", "--size", type=parse_size_str, default=None, help="Output size as WxH (default: first image size)")
    parser.add_argument("-S", "--stabilize", action="store_true", help="Stabilize images by aligning to first frame")

    args = parser.parse_args()
    main(args.output, args.input_files, args.duration, args.size, args.stabilize)
