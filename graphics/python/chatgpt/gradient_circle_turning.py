#!/usr/local/bin/python3

import argparse
from PIL import Image
import numpy as np

def create_gradient_gif(img_size, start_color1, start_color2, end_color, gradient_start, num_frames):

    circle_radius = img_size // 2

    # Normalize to 0-1 range
    start_color1, start_color2 = start_color1 / 255, start_color2 / 255
    end_color = end_color / 255

    # Set up coordinate system
    y, x = np.ogrid[-circle_radius:circle_radius, -circle_radius:circle_radius]
    mask = x**2+y**2 <= circle_radius**2

    # Rotation speed
    rotation_speed = 2 * np.pi / num_frames  # full rotation

    # List to hold each frame of the GIF
    frames = []

    for frame in range(num_frames):
        # Interpolate between color sets in a cyclic way
        t = (np.cos((frame / num_frames) * 2 * np.pi) + 1) / 2
        start_color = (1 - t) * start_color1 + t * start_color2
        
        # Create an array to hold the image data
        img_data = np.ones((img_size, img_size, 3))
        
        # Create the gradient
        phi = (np.arctan2(y, x) + rotation_speed * frame + np.pi) % (2 * np.pi) / (2 * np.pi)
        phi = np.where(phi < gradient_start, gradient_start, phi)  # start gradient at gradient_start
        phi = (phi - gradient_start) / (1 - gradient_start)  # rescale phi to 0-1 range

        # Apply the gradient
        for i in range(3):
            img_data[..., i] = np.where(mask, start_color[i] + (end_color[i] - start_color[i]) * phi, 1)

        # Convert to an 8-bit PIL image and append to frames list
        frames.append(Image.fromarray((img_data * 255).astype('uint8')))

    # Save frames as a GIF
    frames[0].save('data/rotating_gradient.gif', save_all=True, append_images=frames[1:], optimize=False, duration=100, loop=0)

    # Display the GIF
    #Image.open('rotating_gradient.gif').show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a gradient circle gif.')
    parser.add_argument('--img_size', type=int, default=1000, help='Size of the image')
    parser.add_argument('--start_color1', type=int, nargs=3, default=[0, 0, 255], help='Start color 1 (RGB)')
    parser.add_argument('--start_color2', type=int, nargs=3, default=[255, 0, 0], help='Start color 2 (RGB)')
    parser.add_argument('--end_color', type=int, nargs=3, default=[255, 255, 255], help='End color (RGB)')
    parser.add_argument('--gradient_start', type=float, default=0.5, help='Percentage of the circle where the gradient should start')
    parser.add_argument('--num_frames', type=int, default=144, help='Number of frames in the GIF')

    args = parser.parse_args()

    create_gradient_gif(args.img_size, np.array(args.start_color1), np.array(args.start_color2), np.array(args.end_color), args.gradient_start, args.num_frames)
