#!/usr/local/bin/python3

import os
import argparse
import numpy as np
from PIL import Image
import tqdm
import random

def hex_to_rgb(value):
    # Convert hex color to RGB
    value = value.lstrip('#')
    length = len(value)
    return tuple(int(value[i:i+length//3], 16) for i in range(0, length, length//3))

def interpolate_color(color1, color2, factor):
    return tuple(np.array(color1) * (1 - factor) + np.array(color2) * factor)

def create_gradient_frames(output_folder, colors, num_frames, img_size, randomize):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Find the last batch and index used in the output folder
    last_batch = 0
    for filename in os.listdir(output_folder):
        if filename.endswith('.png'):
            batch = filename.split('.')[0].split('_')[0]  # Get the batch from the filename
            last_batch = max(last_batch, int(batch))

    # Set next batch
    next_batch = last_batch + 1

    # Initialize random seed
    random.seed(randomize)

    # Iterate over each frame
    for frame in tqdm.tqdm(range(num_frames), desc="generating frames"):
        # Create a new image with the given size
        img = Image.new('RGB', img_size)

        # Use a color from the spectrum
        hue = (frame / (num_frames - 1)) * (len(colors) - 1)  # Hue value, from 0 to len(colors) - 1
        lower_color = colors[int(hue)]  # Lower bound color
        upper_color = colors[min(int(hue) + 1, len(colors) - 1)]  # Upper bound color

        # Interpolate color for this frame
        color = interpolate_color(lower_color, upper_color, hue - int(hue))

        # Randomize the color if enabled
        if randomize:
            randomized_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            color = interpolate_color(color, randomized_color, random.random())

        # Fill the image with the color
        for i in range(img_size[0]):
            for j in range(img_size[1]):
                img.putpixel((i, j), tuple(map(int, color)))

        # Save the image with a batch prefix and a 5-digit index
        img.save(os.path.join(output_folder, f'{next_batch:02d}_{frame + 1:05d}.png'))

def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Generate gradient frames from a palette")
    parser.add_argument('-o', '--output_folder', type=str, default='data/gradient_from_palette', help="Folder to output frames")
    parser.add_argument('-p', '--palette', type=str, nargs='+', default=['#FF0000', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF'], help="List of hex colors")
    parser.add_argument('-n', '--num_frames', type=int, default=100, help="Number of frames to generate")
    parser.add_argument('-s', '--img_size', type=int, nargs=2, default=[3840, 2160], help="Image size [width, height]")
    parser.add_argument('-r', '--randomize', type=int, default=0, help="Enable color randomization (0: disabled, 1: enabled)")

    # Parse the arguments
    args = parser.parse_args()

    # Normalize the colors to 0-255
    colors = [hex_to_rgb(color) for color in args.palette]


    # Call the function to create the frames
    create_gradient_frames(args.output_folder, colors, args.num_frames, tuple(args.img_size), args.randomize)

if __name__ == "__main__":
    main()
