#!/usr/local/bin/python3

import os
import sys
from PIL import Image
import tqdm

# Get the number of frames and reverse flag from the command line arguments
num_frames = int(sys.argv[1]) if len(sys.argv) > 1 else 16
reverse = sys.argv[2] == 'reverse' if len(sys.argv) > 2 else False

# Define the size of the image
width = 3840
height = 2160

# Define the output folder name
output_folder = 'data/gradient_greyscale'

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
for frame in tqdm.tqdm(range(num_frames), desc="generating frames"):
    # Create a new image with the given size
    img = Image.new('RGB', (width, height))

    # Determine the value for this frame
    value = frame / (num_frames - 1)  # Value in HSV, from 0 to 1
    if reverse:
        value = 1 - value  # Reverse the gradient

    # Convert to 8-bit grayscale
    gray = int(value * 255)

    # Fill the image with the color
    for i in range(width):
        for j in range(height):
            img.putpixel((i, j), (gray, gray, gray))

    # Save the image with a batch prefix and a 5-digit index
    img.save(os.path.join(output_folder, f'01_%s{last_index + frame + 1:05d}.png' % (reverse and "rev_" or "")))

# Display the last frame
#display(img)

