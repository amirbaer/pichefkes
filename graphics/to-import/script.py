#!/usr/local/opt/python@3.8/bin/python3.8

import glob
import random

from PIL import Image, ImageEnhance
import numpy as np
import colorsys


THUMBNAIL_SIZE = (80, 80)
COLLAGE_SIZE = (34, 33)

MALE_PIC = "pics/male.jpg"
FEMALE_PIC = "pics/female.jpg"
FRIENDS_PIC = "pics/1121 friends.png"


"""
rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

def shift_hue(arr, hout):
    r, g, b, a = np.rollaxis(arr, axis=-1)
    h, s, v = rgb_to_hsv((r, g, b))
    h = (h + hout) % 1
    r, g, b = hsv_to_rgb((h, s, v))
    arr = np.dstack((r, g, b, a))
    return arr
"""

def rgb_to_hsv(rgb):
    # Translated from source of colorsys.rgb_to_hsv
    # r,g,b should be a numpy arrays with values between 0 and 255
    # rgb_to_hsv returns an array of floats between 0.0 and 1.0.
    rgb = rgb.astype('float')
    hsv = np.zeros_like(rgb)
    # in case an RGBA array was passed, just copy the A channel
    hsv[..., 3:] = rgb[..., 3:]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb[..., :3], axis=-1)
    minc = np.min(rgb[..., :3], axis=-1)
    hsv[..., 2] = maxc
    mask = maxc != minc
    hsv[mask, 1] = (maxc - minc)[mask] / maxc[mask]
    rc = np.zeros_like(r)
    gc = np.zeros_like(g)
    bc = np.zeros_like(b)
    rc[mask] = (maxc - r)[mask] / (maxc - minc)[mask]
    gc[mask] = (maxc - g)[mask] / (maxc - minc)[mask]
    bc[mask] = (maxc - b)[mask] / (maxc - minc)[mask]
    hsv[..., 0] = np.select(
        [r == maxc, g == maxc], [bc - gc, 2.0 + rc - bc], default=4.0 + gc - rc)
    hsv[..., 0] = (hsv[..., 0] / 6.0) % 1.0
    return hsv

def hsv_to_rgb(hsv):
    # Translated from source of colorsys.hsv_to_rgb
    # h,s should be a numpy arrays with values between 0.0 and 1.0
    # v should be a numpy array with values between 0.0 and 255.0
    # hsv_to_rgb returns an array of uints between 0 and 255.
    rgb = np.empty_like(hsv)
    rgb[..., 3:] = hsv[..., 3:]
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = (h * 6.0).astype('uint8')
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    conditions = [s == 0.0, i == 1, i == 2, i == 3, i == 4, i == 5]
    rgb[..., 0] = np.select(conditions, [v, q, p, p, t, v], default=v)
    rgb[..., 1] = np.select(conditions, [v, v, v, q, p, p], default=t)
    rgb[..., 2] = np.select(conditions, [v, p, t, v, v, q], default=p)
    return rgb.astype('uint8')

def shift_hue(arr,hout):
    hsv=rgb_to_hsv(arr)
    hsv[...,0]=hout
    rgb=hsv_to_rgb(hsv)
    return rgb

def colorize(image, hue):
    """
    Colorize PIL image `original` with the given
    `hue` (hue within 0-360); returns another PIL image.
    """
    img = image.convert('RGBA')
    arr = np.array(np.asarray(img).astype('float'))
    new_img = Image.fromarray(shift_hue(arr, hue/360.).astype('uint8'), 'RGBA')

    return new_img

def add_frame(image, w, h, background_color=(255,255,255,255)):
    iw, ih = image.size
    nw = iw + 2*w
    nh = ih + 2*h
    new_image = Image.new('RGB', (nw, nh), background_color)
    new_image.paste(image, (w, h))
    return new_image


def create_collage(paths, cols, rows, output, pls_colorize=False, pls_add_frame=False):
    #w, h = Image.open(paths[0]).size
    w, h = THUMBNAIL_SIZE

    collage_width = cols * w
    collage_height = rows * h

    new_image = Image.new('RGB', (collage_width, collage_height))

    cursor = (0,0)
    for path in paths:
        # place image
        image = Image.open(path)
        image = image.resize(THUMBNAIL_SIZE)

        if pls_colorize:
            image = colorize(image, random.randint(0, 360))
            converter = ImageEnhance.Color(image)
            image = converter.enhance(4)

        new_image.paste(image, cursor)

        # move cursor
        y = cursor[1]
        x = cursor[0] + w
        if cursor[0] >= (collage_width - w):
            y = cursor[1] + h
            x = 0
        cursor = (x, y)

    if pls_add_frame:
        new_image = add_frame(new_image, w, h)

    new_image.save(output, "PNG")

def get_mega_group(cols, rows, add_friends=False):
    group_pics = glob.glob("script-output/kilogroups/*.png")

    pics = []
    for c in range(cols):
        for r in range(rows):
            if add_friends and c == 0 and r == 0:
                pics.append(FRIENDS_PIC)
            else:
                pics.append(random.choice(group_pics))
    return pics

def get_kilo_strangers(cols, rows):
    pics = []
    for c in range(cols):
        for r in range(rows):
            pics.append(random.choice([MALE_PIC, FEMALE_PIC]))
    return pics


def generate_kilogroups(cols, rows):
    for i in range(52, 10098):
        output = "script-output/kilogroups-framed-34x33/%d.png" % i
        create_collage(get_kilo_strangers(cols, rows), cols, rows, output, pls_colorize=True, pls_add_frame=True)
        print(".", sep="", end="", flush=True)

    print("\ndone")

def generate_megagroups(cols, rows):
    for i in range(8):
        output = "script-output/megagroups/%d.png" % i
        create_collage(get_mega_group(cols, rows, add_friends=False), cols, rows, output, pls_colorize=False)
        print(".", sep="", end="", flush=True)

    print("\ndone")

def generate_megagroup_with_friends(cols, rows):
    output = "script-output/megagroups/mega-with-friends.png"
    create_collage(get_mega_group(cols, rows, add_friends=True), cols, rows, output, pls_colorize=False)

def frame_friends():
    image = Image.open("pics/1121 friends.png")
    new_image = add_frame(image, *THUMBNAIL_SIZE)

    new_image.save("pics/friends-framed.png", "PNG")


def main():
    cols, rows = COLLAGE_SIZE
    #frame_friends()
    generate_kilogroups(cols, rows)



if __name__ == "__main__":
    main()

