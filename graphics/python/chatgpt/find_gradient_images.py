#!/usr/local/bin/python3

import cv2
import numpy as np
import os
import argparse

def is_gradient(image):
    # Convert the image to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Get the difference between adjacent pixels
    gradient_x = np.diff(image, axis=1)
    gradient_y = np.diff(image, axis=0)
    # If all differences are close to each other, the image is likely a gradient
    return np.allclose(gradient_x, gradient_x[0, 0]) and np.allclose(gradient_y, gradient_y[0, 0])

def process_images(input_dir, output_dir):
    # Get all files in the directory
    files = os.listdir(input_dir)
    # Filter out all non-images
    images = [file for file in files if file.endswith(('jpg', 'png', 'jpeg'))]

    # Analyze each image
    for image_file in images:
        # Load the image
        image = cv2.imread(os.path.join(input_dir, image_file))
        # Check if it's a gradient
        if is_gradient(image):
            # Save it to the output directory
            cv2.imwrite(os.path.join(output_dir, image_file), image)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for filtering gradient images', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_dir', type=str)
    parser.add_argument('output_dir', type=str)
    args = parser.parse_args()

    process_images(args.input_dir, args.output_dir)
