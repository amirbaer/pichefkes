#!/usr/local/bin/python3

import argparse
from PIL import Image
import os
import random

def create_modified_image(input_image, rotation_angle, x_offset, y_offset):
    """Create a modified image by rotating and repositioning the input image."""
    image = Image.open(input_image)
    width, height = image.size

    # Calculate the maximum size needed to fit the rotated image
    max_size = max(image.size)
    max_width = max_size if width == max_size else int(max_size * (width / height))
    max_height = max_size if height == max_size else int(max_size * (height / width))

    # Create a blank canvas with the maximum size
    modified_image = Image.new('RGB', (max_width, max_height), color=0)

    # Rotate the input image
    rotated_image = image.rotate(rotation_angle, expand=True)
    rotated_image = rotated_image.resize((width*5, height*2))

    # Calculate the new position based on the offsets
    new_x = int((max_width - rotated_image.width) / 2 + x_offset)
    new_y = int((max_height - rotated_image.height) / 2 + y_offset)

    # Paste the rotated image onto the blank canvas
    modified_image.paste(rotated_image, (new_x, new_y))

    # Resize the modified image to fit the canvas
    modified_image = modified_image.resize((width*2, height*2))

    return modified_image

def main(input_image, rotation_angle, x_offset, y_offset, output_image):
    # Create the modified image with random rotation angle, x-axis offset, and y-axis offset
    modified_image = create_modified_image(input_image, rotation_angle, x_offset, y_offset)

    # Create a blank canvas with the same size as the modified image
    canvas = Image.new('RGB', modified_image.size, color=0)

    # Paste the modified image onto the canvas
    canvas.paste(modified_image, (0, 0))

    # Save the modified image
    canvas.save(output_image)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a modified image by rotating and repositioning an input image.')
    parser.add_argument('input_image', type=str, help='Path to the input image.')
    parser.add_argument('--output_image', type=str, default='', help='Path to the output modified image. Default: modified_image.jpg')
    args = parser.parse_args()

    if not args.output_image:
        fn, ext = os.path.splitext(args.input_image)
        args.output_image = f'{fn}-altered{ext}'

    # Generate random rotation angle between -45 and 45 degrees
    rotation_angle = random.uniform(-45.0, 45.0)

    # Generate random x-axis offset between -10 and 10 pixels
    x_offset = 0 #random.randint(-10, 10)

    # Generate random y-axis offset between -10 and 10 pixels
    y_offset = 0 #random.randint(-10, 10)

    main(args.input_image, rotation_angle, x_offset, y_offset, args.output_image)
