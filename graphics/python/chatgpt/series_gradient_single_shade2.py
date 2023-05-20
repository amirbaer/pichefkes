#!/usr/local/bin/python3

import os
import sys
from PIL import Image
import colorsys

# Get the number of frames from the command line arguments
num_frames = int(sys.argv[1]) if len(sys.argv) > 1 else 100

# Define the size of the image
width = 800
height = 800

# Define the hue for magenta in the HSV color space
magenta_hue = 5 / 6

# Define the output folder name
output_folder = 'gradient_single_shade2'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Find the last index used in the output folder
last_index = 0
for filename in os.listdir(output_folder):
    if filename.endswith('.png'):
        index = int(filename.split('_')[1].split('.')[0])  # Get the index from the filename
        last_index = max(last_index, index)

# Iterate over each frame
for frame in range(num_frames):
    # Create a new image with the given size
    img = Image.new('RGB', (width, height))

    # Determine the value for this frame
    value = 0.5 + frame / (2 * (num_frames - 1))  # Value in HSV, from 0.5 to 1

    # Convert HSV to RGB
    color = colorsys.hsv_to_rgb(magenta_hue, 1, value)

    # Convert to 8-bit RGB
    r, g, b = [int(c * 255) for c in color]

    # Fill the image with the color
    for i in range(width):
        for j in range(height):
            img.putpixel((i, j), (r, g, b))

    # Save the image with a batch prefix and a 5-digit index
    img.save(os.path.join(output_folder, f'01_{last_index + frame + 1:05d}.png'))

# Display the last frame
#display(img)

