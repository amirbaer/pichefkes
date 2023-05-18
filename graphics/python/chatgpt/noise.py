#!/usr/local/bin/python3

from PIL import Image
import random

# Define the size of the image
width = 800
height = 800

# Create a new image with the given size
img = Image.new('RGB', (width, height))

# Access the pixel data
pixels = img.load()

# Iterate over each pixel
for i in range(width):
    for j in range(height):
        # Generate random color
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        # Set the color of the pixel
        pixels[i, j] = (r, g, b)

# Save the image
img.save('generative_art.png')

