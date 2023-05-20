#!/usr/local/bin/python3

import os
import random
import argparse
from PIL import Image, ImageDraw

def get_palette_from_images(folder):
    """Extract the color palette from the image filenames in a folder."""
    palette = []
    for filename in os.listdir(folder):
        color = os.path.splitext(filename)[0]  # remove the extension
        palette.append(color)
    return palette

def generate_gradient(colors, width, height, direction):
    """Generate a gradient image given a list of colors, size and direction."""
    base = Image.new('RGB', (width, height), colors[0])
    top = Image.new('RGB', (width, height), colors[-1])
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            if direction == 'horizontal':
                mask_data.append(int(255 * (x / width)))
            else:  # vertical
                mask_data.append(int(255 * (y / height)))
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def main(args):
    # Get the color palette
    if os.path.isdir(args.palette):
        palette = get_palette_from_images(args.palette)
    else:
        palette = args.palette.split(',')

    # Generate the gradient images
    for i in range(args.num_images):
        chosen_colors = random.sample(palette, args.colors_per_gradient)
        image = generate_gradient(chosen_colors, args.width, args.height, args.direction)
        image.save(f'gradient_{i}.png')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate gradient images.')
    parser.add_argument('--palette', type=str, required=True,
                        help='A comma-separated list of colors, or a folder of single-color images named with their color.')
    parser.add_argument('--num-images', type=int, default=10,
                        help='The number of gradient images to generate.')
    parser.add_argument('--colors-per-gradient', type=int, default=2,
                        help='The number of colors to include in each gradient.')
    parser.add_argument('--direction', type=str, default='horizontal',
                        choices=['horizontal', 'vertical'], 
                        help='The direction of the gradient.')
    parser.add_argument('--width', type=int, default=500,
                        help='The width of the generated images.')
    parser.add_argument('--height', type=int, default=500,
                        help='The height of the generated images.')
    args = parser.parse_args()
    main(args)
