#!/usr/local/bin/python3

import cv2
import numpy as np
import os
import argparse
from sklearn.cluster import KMeans
from random import choice
from numpy.random import shuffle
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

def create_gradient(colors, output_dimensions):
    # Randomly shuffle the colors to create variance in the proportions of the colors
    shuffle(colors)
    # Create an array that goes from 0 to 1 with as many steps as there are colors
    indices = np.linspace(0, 1, len(colors))
    # Create a function that will generate the gradient along one axis
    gradient_func = lambda x: np.array([np.interp(x, indices, colors[:, i]) for i in range(3)])
    gradient_func = np.vectorize(gradient_func, signature='()->(n)')
    # Create the gradient image
    gradient = gradient_func(np.linspace(0, 1, output_dimensions[1])).astype(int)
    gradient = np.repeat(gradient[np.newaxis, :], output_dimensions[0], axis=0)
    return np.rot90(gradient)

def create_images(input_dir, output_dir, num_colors, num_images, output_dimensions):
    # Get all files in the input directory
    files = os.listdir(input_dir)
    # Filter out non-image files
    images = [file for file in files if file.endswith(('jpg', 'png', 'jpeg'))]

    for image_file in tqdm.tqdm(images, desc="generating images"):
        # Load the source image
        source_image = cv2.imread(os.path.join(input_dir, image_file))
        image_basename, ext = os.path.splitext(image_file)
        # Extract the colors from the source image
        colors = extract_colors(source_image, num_colors)

        for i in range(num_images):
            # Create a gradient image
            gradient = create_gradient(colors, output_dimensions)
            # Write the image
            output_file = f'image_gradient_{image_basename}_{i}.{ext}'
            cv2.imwrite(os.path.join(output_dir, output_file), gradient)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script for creating gradient images from source images', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_dir', type=str, help='Directory containing source images')
    parser.add_argument('output_dir', type=str, help='Directory to save the generated images')
    parser.add_argument('-c', '--num_colors', type=int, default=5, help='Number of colors per gradient')
    parser.add_argument('-n', '--num_images', type=int, default=5, help='Number of variations to create')
    parser.add_argument('--output_dimensions', type=int, nargs=2, default=[3840, 2160], help='Output image dimensions')
    args = parser.parse_args()

    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate gradient images
    create_images(args.input_dir, args.output_dir, args.num_colors, args.num_images, args.output_dimensions)
