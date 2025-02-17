#!/usr/local/bin/python3

import cv2
import os
import argparse
import tqdm

def create_blurred_images(input_dir, output_dir, output_dimensions, blur_strength):
    # Get all files in the input directory
    files = os.listdir(input_dir)
    # Filter out non-image files
    images = [file for file in files if file.endswith(('jpg', 'png', 'jpeg'))]

    for image_file in tqdm.tqdm(images, desc="generating images"):
        image_file_full_path = os.path.join(input_dir, image_file)
        # Load the source image
        source_image = cv2.imread(image_file_full_path)
        # Blur the image
        image_blurred = cv2.GaussianBlur(source_image, (99, 99), blur_strength)
        # Resize it to the output dimensions
        image_resized = cv2.resize(image_blurred, output_dimensions)  # cv2 uses width x height

        # Write the image
        if args.output_dir:
            output_file = os.path.join(output_dir, f'image_blurred_{image_file}')
        else:
            output_file = image_file_full_path
        cv2.imwrite(output_file, image_resized)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for creating blurred images', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_dir', type=str, help='Directory containing source images')
    parser.add_argument('--output_dir', type=str, default="", help='Directory to save the generated images')
    parser.add_argument('--output_dimensions', type=int, nargs=2, default=[3840, 2160], help='Output image dimensions')
    parser.add_argument('-b', '--blur_strength', type=int, default=30, help='Strength of the blur')
    args = parser.parse_args()

    # Create the output directory if it doesn't exist
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)

    # Generate blurred images
    create_blurred_images(args.input_dir, args.output_dir, args.output_dimensions, args.blur_strength)
