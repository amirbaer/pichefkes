#!/usr/local/bin/python3

import cv2
import numpy as np
import os
import argparse
from sklearn.cluster import KMeans
from random import choice
import tqdm

def extract_colors(image, num_colors):
    # Reshape the image to be a list of pixels
    pixels = image.reshape(-1, 3)
    # Perform K-means clustering to find the most dominant colors
    kmeans = KMeans(n_clusters=num_colors)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_
    # Return the colors
    return colors

def create_gradient(colors, output_dimensions, direction):
    # Create an array that goes from 0 to 1 with as many steps as there are colors
    indices = np.linspace(0, 1, len(colors))
    # Create a function that will generate the gradient along one axis
    gradient_func = np.vectorize(lambda x: np.interp(x, indices, colors, axis=0))
    # Create the gradient image
    if direction == 'horizontal':
        gradient = gradient_func(np.linspace(0, 1, output_dimensions[1])).astype(int)
        gradient = np.repeat(gradient[np.newaxis, :], output_dimensions[0], axis=0)
    else:  # vertical
        gradient = gradient_func(np.linspace(0, 1, output_dimensions[0])).astype(int)
        gradient = np.repeat(gradient[:, np.newaxis], output_dimensions[1], axis=1)
    return gradient

def create_images(source_image, num_colors, num_images, output_dimensions, output_dir, blur):
    # Extract the colors from the source image
    colors = extract_colors(source_image, num_colors)

    for i in tqdm.tqdm(range(num_images), desc="generating images"):
        if blur:
            # Blur the image
            image_blurred = cv2.GaussianBlur(source_image, (99, 99), 30)
            # Resize it to the output dimensions
            image_resized = cv2.resize(image_blurred, output_dimensions[::-1])  # cv2 uses width x height
            # Write the image
            cv2.imwrite(os.path.join(output_dir, f'image_blurred_{i}.jpg'), image_resized)
        else:
            # Create a gradient image
            gradient = create_gradient(colors, output_dimensions, direction=choice(['horizontal', 'vertical']))
            # Write the image
            cv2.imwrite(os.path.join(output_dir, f'image_gradient_{i}.jpg'), gradient)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for creating gradient images from a source image', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('source_image', type=str, help='Path to the source image')
    parser.add_argument('output_dir', type=str, help='Directory to save the generated images')
    parser.add_argument('-c', '--num_colors', type=int, default=5, help='Number of colors per gradient')
    parser.add_argument('-n', '--num_images', type=int, default=5, help='Number of variations to create')
    parser.add_argument('--output_dimensions', type=int, nargs=2, default=[3840, 2160], help='Output image dimensions')
    parser.add_argument('--blur', action='store_true', help='If set, apply a blur effect on the source image instead of generating the gradient from scratch')
    args = parser.parse_args()

    # Load the source image
    source_image = cv2.imread(args.source_image)

    # Create the images
    create_images(source_image, args.num_colors, args.num_images, args.output_dimensions, args.output_dir, args.blur)

