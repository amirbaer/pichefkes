#!/usr/local/bin/python3

import cv2
import os
import argparse
import tqdm

def create_blurred_images(input_dir, output_dir, output_dimensions):
    # Get all files in the input directory
    files = os.listdir(input_dir)
    # Filter out non-image files
    images = [file for file in files if file.endswith(('jpg', 'png', 'jpeg'))]

    for image_file in tqdm.tqdm(images, desc="generating images"):
        # Load the source image
        source_image = cv2.imread(os.path.join(input_dir, image_file))
        # Blur the image
        image_blurred = cv2.GaussianBlur(source_image, (99, 99), 30)
        # Resize it to the output dimensions
        image_resized = cv2.resize(image_blurred, output_dimensions)  # cv2 uses width x height
        # Write the image
        output_file = f'image_blurred_{image_file}'
        cv2.imwrite(os.path.join(output_dir, output_file), image_resized)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for creating blurred images', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_dir', type=str, help='Directory containing source images')
    parser.add_argument('output_dir', type=str, help='Directory to save the generated images')
    parser.add_argument('--output_dimensions', type=int, nargs=2, default=[3840, 2160], help='Output image dimensions')
    args = parser.parse_args()

    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate blurred images
    create_blurred_images(args.input_dir, args.output_dir, args.output_dimensions)
