#!/usr/local/bin/python3

import argparse
from PIL import Image
import os

def create_modified_image(input_image, rotation_angle, x_offset, y_offset):
    """Create a modified image by rotating and repositioning the input image."""
    image = Image.open(input_image)
    width, height = image.size

    # Create a blank canvas with the same size as the input image
    modified_image = Image.new('RGB', (width, height), color=0)

    # Rotate the input image
    rotated_image = image.rotate(rotation_angle, expand=True)

    # Calculate the new position based on the offsets
    new_x = int((width - rotated_image.width) / 2 + x_offset)
    new_y = int((height - rotated_image.height) / 2 + y_offset)

    # Paste the rotated image onto the blank canvas
    modified_image.paste(rotated_image, (new_x, new_y))

    return modified_image

def main(input_image, rotation_angle, x_offset, y_offset, output_image):
    # Create the modified image
    modified_image = create_modified_image(input_image, rotation_angle, x_offset, y_offset)

    # Save the modified image
    modified_image.save(output_image)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a modified image by rotating and repositioning an input image.')
    parser.add_argument('input_image', type=str, help='Path to the input image.')
    parser.add_argument('--rotation_angle', type=float, default=45.0, help='Rotation angle in degrees. Default: 45.0')
    parser.add_argument('--x_offset', type=int, default=10, help='X-axis offset. Default: 10')
    parser.add_argument('--y_offset', type=int, default=10, help='Y-axis offset. Default: 10')
    parser.add_argument('--output_image', type=str, default='', help='Path to the output modified image. Default: modified_image.jpg')
    args = parser.parse_args()

    if not args.output_image:
        fn, ext = os.path.splitext(args.input_image)
        args.output_image = f'{fn}-altered.{ext}'

    main(args.input_image, args.rotation_angle, args.x_offset, args.y_offset, args.output_image)

