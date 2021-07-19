from PIL import Image
import random

img = Image.new( 'RGB', (255,255), "black") # create a new black image
pixels = img.load() # create the pixel map

for i in range(img.size[0]):    # for every pixel:
    for j in range(img.size[1]):
        b = (i * j) % 256
        pixels[i,j] = (i, j, b) # set the colour accordingly

img.show()
