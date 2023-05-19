#!/usr/local/bin/python3

import argparse
from PIL import Image
import numpy as np
import os
import tqdm

def create_gradient_gif(output_folder, img_size, shape, palette, gradient_start, num_frames):
    circle_size = 0.95

    # Calculate the circle/square radius as 90% of the image size
    radius = img_size * circle_size // 2

    # Normalize the palette colors to 0-1 range
    palette = [np.array(color) / 255 for color in palette]

    # Set up coordinate system
    y, x = np.ogrid[-img_size//2:img_size//2, -img_size//2:img_size//2]
    mask = np.ones_like(x, dtype=bool)
    if shape == 'circle':
        mask = x**2 + y**2 <= radius**2

    # List to hold each frame of the GIF
    frames = []

    for frame in tqdm.tqdm(range(num_frames), desc="generating frames"):
        # Create an array to hold the image data
        img_data = np.ones((img_size, img_size, 3))

        # Calculate the angle for each pixel
        angle = np.arctan2(y, x) + (2 * np.pi / num_frames) * frame

        # Calculate the gradient value for each pixel
        gradient = np.where(mask, (angle + np.pi) % (2 * np.pi) / (2 * np.pi), 0)
        gradient = np.where(gradient < gradient_start, gradient_start, gradient)
        gradient = (gradient - gradient_start) / (1 - gradient_start)

        # Apply the gradient colors
        for i, color in enumerate(palette):
            img_data[..., 0] = np.where(mask, color[0] * gradient + img_data[..., 0] * (1 - gradient), img_data[..., 0])
            img_data[..., 1] = np.where(mask, color[1] * gradient + img_data[..., 1] * (1 - gradient), img_data[..., 1])
            img_data[..., 2] = np.where(mask, color[2] * gradient + img_data[..., 2] * (1 - gradient), img_data[..., 2])

        # Convert to an 8-bit PIL image and append to frames list
        frames.append(Image.fromarray((img_data * 255).astype('uint8')))

    # Determine the index of the last saved file in the output folder
    index = 1
    while os.path.exists(os.path.join(output_folder, f"{index:02d}.gif")):
        index += 1

    # Save frames as a GIF
    frames[0].save(os.path.join(output_folder, f"{index:02d}.gif"), save_all=True, append_images=frames[1:], optimize=False, duration=100, loop=0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a gradient animation.')
    parser.add_argument('--output_folder', type=str, default='data/gradient_circle_square', help='Output folder for the frames and GIF')
    parser.add_argument('--img_size', type=int, default=1000, help='Size of the image')
    parser.add_argument('--shape', type=str, choices=['circle', 'square'], default='circle', help='Shape of the main element')
    parser.add_argument('--palette', nargs='+', default=['#0000FF', '#FFFFFF'], help='Palette of colors (hex values)')
    parser.add_argument('--gradient_start', type=float, default=0.5, help='Percentage of the shape where the gradient should start')
    parser.add_argument('--num_frames', type=int, default=144, help='Number of frames in the GIF')

    args = parser.parse_args()

    # Convert hex values to RGB tuples
    palette = [tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for color in args.palette]

    # Create the output folder if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)

    create_gradient_gif(args.output_folder, args.img_size, args.shape, palette, args.gradient_start, args.num_frames)
