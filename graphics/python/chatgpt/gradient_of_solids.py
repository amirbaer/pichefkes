#!/usr/local/bin/python3

import os
import argparse
import colorsys
from PIL import Image
from tqdm import tqdm

def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Generate color gradient frames",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--output_folder', type=str, default='data/gradient_of_solids', help="Folder to output frames")
    parser.add_argument('--num_frames', type=int, default=100, help="Number of frames to generate")
    parser.add_argument('--img_size', type=int, nargs=2, default=[3840, 2160], help="Image size [width, height]")

    # Parse the arguments
    args = parser.parse_args()

    # Create the output folder if it doesn't exist
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    # Find the last batch and index used in the output folder
    last_index = 0
    for filename in os.listdir(args.output_folder):
        if filename.endswith('.png'):
            index = filename.split('.')[0]
            last_index = max(last_index, int(index))
    
    current_index = last_index + 1

    # Iterate over each frame
    for frame in tqdm(range(args.num_frames), desc="generating frames"):
        # Create a new image with the given size
        img = Image.new('RGB', tuple(args.img_size))

        # Use a color from the spectrum
        hue = frame / (args.num_frames - 1)  # Hue value, from 0 to 1
        color = colorsys.hsv_to_rgb(hue, 1, 1)  # Convert hue to RGB

        # Convert to 8-bit RGB
        r, g, b = [int(c * 255) for c in color]

        # Fill the image with the color
        for i in range(args.img_size[0]):
            for j in range(args.img_size[1]):
                img.putpixel((i, j), (r, g, b))

        # Save the image with a frame index
        img.save(os.path.join(args.output_folder, f'{current_index:05d}.png'))
        current_index += 1

if __name__ == "__main__":
    main()
