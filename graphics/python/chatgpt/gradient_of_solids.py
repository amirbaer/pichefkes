#!/usr/local/bin/python3

import os
from PIL import Image
#from IPython.display import display
import colorsys
import tqdm

# Define the size of the image
width = 3840
height = 2160

# Define the number of frames
num_frames = 100

# Define the colors for the first 10 frames
first_colors = [
    (1, 0, 0),          # Red
    (1, 1, 0),          # Yellow
    (0, 1, 0),          # Green
    (0, 1, 1),          # Cyan
    (0, 0, 1),          # Blue
    (1, 0, 1),          # Magenta
    (1, 165/255, 0),    # Orange
    (128/255, 0, 128/255), # Purple
    (1, 192/255, 203/255), # Pink
    (75/255, 0, 130/255)   # Indigo
]

# Define the output folder name
output_folder = 'data/gradient_of_solids'

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

    # Determine the color for this frame
    if frame < len(first_colors):
        # Use one of the first colors
        color = first_colors[frame]
    else:
        # Use a color from the spectrum
        hue = (frame - len(first_colors)) / (num_frames - len(first_colors))  # Hue value, from 0 to 1
        color = colorsys.hsv_to_rgb(hue, 1, 1)  # Convert hue to RGB

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

