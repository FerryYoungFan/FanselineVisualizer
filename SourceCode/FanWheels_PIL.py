#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageChops, ImageFont
import os, sys


def getPath(fileName):  # for different operating systems
    path = os.path.join(os.path.dirname(sys.argv[0]), fileName)
    return path


def imageOrColor(path, mode):
    if isinstance(path, str):
        try:
            img = Image.open(getPath(path)).convert(mode)
            if img is not None:
                return img
            else:
                raise Exception("Can not open image")
        except:
            return None
    if isinstance(path, tuple):
        try:
            if mode == "RGB":
                img = Image.new(mode, (512, 512), path[:3])
            else:
                img = Image.new(mode, (512, 512), path[:4])
            if img is not None:
                return img
            else:
                raise Exception("Can not generate image")
        except:
            return None
    return None


def openImage(path, mode="RGBA", fallbacks=None):
    img = imageOrColor(path, mode)
    if img is None and isinstance(fallbacks, list):
        for fallback in fallbacks:
            if fallback is None:
                return None
            img = imageOrColor(fallback, mode)
            if img is not None:
                return img
    else:
        return img
    img = Image.new('RGB', (512, 512), (0, 0, 0))
    return img


def cropToCenter(img):
    width, height = img.size
    square = min(width, height)
    left = (width - square) / 2
    top = (height - square) / 2
    right = (width + square) / 2
    bottom = (height + square) / 2
    im = img.crop((left, top, right, bottom))
    return im


def cropCircle(img, size=None):
    img = cropToCenter(img)
    pad_size = 2
    if size is not None:
        img = img.resize((size, size), Image.ANTIALIAS)
    # Antialiasing Drawing
    width, height = img.size
    scale = 4
    size_anti = width * scale, height * scale
    mask = Image.new('L', size_anti, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size_anti, fill=255)
    mask = mask.resize((size, size), Image.ANTIALIAS)
    img.putalpha(mask)
    return img


def resizeRatio(img, ratio):
    width, height = img.size
    width = int(round(width * ratio))
    height = int(round(height * ratio))
    return img.resize((width, height), Image.ANTIALIAS)


def cropBG(img, size):
    width, height = img.size
    if (width < size[0] and height < size[1]) or (width > size[0] and height > size[1]):
        img = resizeRatio(img, size[0] / width)
        width, height = img.size
        if height < size[1]:
            img = resizeRatio(img, size[1] / height)
            width, height = img.size
    elif width < size[0] and height >= size[1]:
        img = resizeRatio(img, size[0] / width)
        width, height = img.size
    elif width >= size[0] and height < size[1]:
        img = resizeRatio(img, size[1] / height)
        width, height = img.size

    left = (width - size[0]) / 2
    top = (height - size[1]) / 2
    right = (width + size[0]) / 2
    bottom = (height + size[1]) / 2
    img = img.crop((left, top, right, bottom))
    return img


def genBG(img, size, blur=41, bright=0.35):
    img = cropBG(img, size)
    img_blur = img.filter(ImageFilter.GaussianBlur(radius=blur))
    enhancer = ImageEnhance.Brightness(img_blur)
    output = enhancer.enhance(bright)
    return output


def pasteMiddle(fg, bg, glow=False, blur=2, bright=1):
    fg_w, fg_h = fg.size
    bg_w, bg_h = bg.size
    offset = ((bg_w - fg_w) // 2, (bg_h - fg_h) // 2)

    if glow:
        brt = int(round(bright * 255))
        if brt > 255:
            brt = 255
        elif brt < 0:
            brt = 0
        canvas = Image.new('RGBA', (bg_w, bg_h), (brt, brt, brt, 0))
        canvas.paste(fg, offset, fg)
        mask = canvas.split()[-1]
        mask = mask.point(lambda i: i * bright)
        ratio = 2
        mask = resizeRatio(mask, ratio)
        mask = mask.filter(ImageFilter.GaussianBlur(radius=blur * ratio))
        mask = mask.resize((bg_w, bg_h))
        if bg.mode == "L":
            canvas = mask
        elif bg.mode == "RGB":
            canvas = Image.merge('RGB', (mask, mask, mask))
        elif bg.mode == "RGBA":
            canvas = Image.merge('RGBA', (mask, mask, mask, mask))
        bg = ImageChops.add(bg, canvas)
    bg.paste(fg, offset, fg)
    return bg


def glowText(img, text=None, font_size=35, font_set=None, color=(255, 255, 255, 255), blur=2, logo=None, use_glow=True,
             yoffset=0):
    width, height = img.size
    ratio = 2
    width = width * ratio
    height = height * ratio
    font_size = font_size * ratio
    blur = blur * ratio

    if font_set is None:
        _font = ImageFont.truetype("arial.ttf", font_size)
    else:
        _font = "arial.ttf"
        for font_i in [font_set, getPath("Source/font.ttf"), getPath("Source/font.otf"), "arial.ttf"]:
            try:
                _font = ImageFont.truetype(font_i, font_size)
                break
            except:
                print("Cannot Use Font: {0}".format(font_i))

    canvas = Image.new('RGBA', (width, height), color[:-1] + (0,))
    draw = ImageDraw.Draw(canvas)
    if text:
        w, h = draw.textsize(text, font=_font)
    else:
        w, h = 0, 0
    xoffset = 0
    if logo is not None:
        lg_w, lg_h = logo.size
        hoffset = 1.1
        lg_nh = round(font_size * hoffset)
        lg_nw = round(lg_w * lg_nh / lg_h)
        logo = logo.resize((lg_nw, lg_nh), Image.ANTIALIAS)
        if text:
            xoffset = lg_nw + font_size / 4
        else:
            xoffset = lg_nw
        w = w + xoffset
        _x_logo = int(round((width - w) / 2))
        _y_logo = int(round(yoffset * ratio - font_size * (hoffset - 1) / 2))
        try:
            canvas.paste(logo, (_x_logo, _y_logo), logo)
        except:
            canvas.paste(logo, (_x_logo, _y_logo))
    if text:
        draw.text(((width - w) / 2 + xoffset, yoffset * ratio), text, fill=color, font=_font)
    if use_glow:
        mask_blur = canvas.split()[-1]
        mask_blur = mask_blur.filter(ImageFilter.GaussianBlur(radius=blur * 2))
        fg_blur = canvas.split()[0]
        fg_blur = fg_blur.filter(ImageFilter.GaussianBlur(radius=blur * 2))
        glow_text = Image.merge("RGBA", (fg_blur, fg_blur, fg_blur, mask_blur))
        glow_text = glow_text.resize(img.size, Image.ANTIALIAS)
        canvas = canvas.resize(img.size, Image.ANTIALIAS)
        img.paste(glow_text, (0, 0), mask=glow_text)
        img.paste(canvas, (0, 0), mask=canvas)
    else:
        canvas = canvas.resize(img.size, Image.ANTIALIAS)
        img.paste(canvas, (0, 0), mask=canvas)
    return img


def hsv_to_rgb(h, s, v):
    if s == 0.0:
        v = int(v * 255)
        return v, v, v
    i = int(h * 6.)
    f = (h * 6.) - i
    p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))))
    v = int(v * 255)
    i %= 6
    if i == 0: return v, t, p
    if i == 1: return q, v, p
    if i == 2: return p, v, t
    if i == 3: return p, q, v
    if i == 4: return t, p, v
    if i == 5: return v, p, q


def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    elif mx == b:
        h = (60 * ((r - g) / df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df / mx
    v = mx
    return h / 360, s, v


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def glowFx(image, radius=0, brt=1.5):
    if radius > 0:
        base = image.copy()
        image = image.filter(ImageFilter.GaussianBlur(radius=radius))
        base = ImageChops.add(image, base)
        return base
    else:
        return image

# def glowFx(image, radius=0, brt=1.5):
#     if radius > 0:
#         base = image.copy()
#         image = image.filter(ImageFilter.BoxBlur(radius=radius))
#         enhancer = ImageEnhance.Brightness(image)
#         image = enhancer.enhance(brt)
#         base.paste(image, (0, 0), image)
#         return base
#     else:
#         return image
