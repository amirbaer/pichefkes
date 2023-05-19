# colors.py
#!/usr/local/bin/python3

import os
import argparse
from PIL import Image
from tqdm import tqdm

# Map a number to an RGB color
def num_to_rgb(num):
    return (num // 65536, (num // 256) % 256, num % 256)

# Map an RGB color to a number
def rgb_to_num(rgb):
    return rgb[0] * 65536 + rgb[1] * 256 + rgb[2]

def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Generate a sequence of color frames",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--output_folder', type=str, default='data/color_frames', help="Folder to output frames")
    parser.add_argument('--range', type=int, nargs=3, default=[0, 16777215, 1], help="Color range [start, end, step] and step size")
    parser.add_argument('--img_size', type=int, nargs=2, default=[3840, 2160], help="Image size [width, height]")

    # Parse the arguments
    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    # Generate the sequence of colors
    for num in tqdm(range(*args.range), desc="generating frames"):
        color = num_to_rgb(num)

        # Create a new image with the given size and fill it with the color
        img = Image.new('RGB', tuple(args.img_size), color=color)

        # Save the image with a frame index
        img.save(os.path.join(args.output_folder, f'{num + 1:05d}.png'))

if __name__ == "__main__":
    main()
