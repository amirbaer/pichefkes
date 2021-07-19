from PIL import Image
import random

img = Image.new( 'RGB', (2550,2550), "black") # create a new black image
pixels = img.load() # create the pixel map

for i in range(img.size[0]):    # for every pixel:
    for j in range(img.size[1]):
        r = (i + j) % 256
        g = (i * 3 + j * 2) % 256
        b = (i**2 * j) % 256
        pixels[i,j] = (r, g, b) # set the colour accordingly

img.show()
