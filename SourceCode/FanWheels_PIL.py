from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageEnhance, ImageChops, ImageFont


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
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output


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


def glowText(img, text=None, font_size=35, font_set=None, bright=1.0, blur=2, logo=None, use_glow=True):
    brt = int(round(bright * 255))
    if brt > 255:
        brt = 255
    elif brt < 0:
        brt = 0

    tcolor = int(round(((bright - 0.5) * 3 + 0.5) * 255))
    if tcolor > 255:
        tcolor = 255
    elif tcolor < 0:
        tcolor = 0

    width, height = img.size
    ratio = 2
    width = width * ratio
    height = height * ratio
    font_size = font_size * ratio
    blur = blur * ratio

    if font_set is None:
        _font = ImageFont.truetype("Arial.ttf", font_size)
    else:
        _font = ImageFont.truetype(font_set, font_size)

    canvas = Image.new('RGBA', (width, height), (brt, brt, brt, 0))
    draw = ImageDraw.Draw(canvas)
    if text:
        w, h = draw.textsize(text, font=_font)
    else:
        w, h = 0, 0
    xoffset = 0

    if logo is not None:
        lg_w, lg_h = logo.size
        hoffset = 1.2
        lg_nh = round(font_size * hoffset)
        lg_nw = round(lg_w * lg_nh / lg_h)
        logo = logo.resize((lg_nw, lg_nh), Image.ANTIALIAS)
        if text:
            xoffset = lg_nw + font_size / 4
        else:
            xoffset = lg_nw
        w = w + xoffset
        try:
            canvas.paste(logo, (round((width - w) / 2), round(height - 2 * font_size)), logo)
        except:
            canvas.paste(logo, (round((width - w) / 2), round(height - 2 * font_size)))
    if text:
        draw.text(((width - w) / 2 + xoffset, height - 2 * font_size), text, fill=(tcolor, tcolor, tcolor, 255),
                  font=_font)
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
