#!/usr/bin/env python

from gimpfu import *

LEFT = TOP = 0
CENTER = 1
RIGHT = BOTTOM = 2

class Font(object):
    def __init__(self, font, size, bold = False, line_spacing = 0.0):
        self.font, self.size, self.bold, self.line_spacing = \
                font, size, bold, line_spacing

def add_text_layer(image, txt, font, font_size, line_spacing = None, colour = (0, 0, 0), name = 'Text', pos = (0, 0)):
    gimp.set_foreground(*colour)
    pdb.gimp_image_set_active_layer(image, image.layers[0])
    text = pdb.gimp_text_fontname(image, None, pos[0], pos[1], txt, 0, True, font_size, PIXELS, font)
    if text is None:
        return
    text.name = name
    if line_spacing is not None:
        pdb.gimp_text_layer_set_line_spacing(text, line_spacing)
    pdb.gimp_text_layer_set_hint_style(text, TEXT_HINT_STYLE_NONE)

    return text

def read_text(filename):
    return open(filename, 'rb').read().decode('utf-8').strip()

def add_text(image, txt, font, colour = (0, 0, 0)):
    layer = add_text_layer(image, txt, font.font, font.size, font.line_spacing, colour)
    if layer is None:
        return None
    pdb.gimp_text_layer_set_markup(layer, txt)
    if font.bold:
        bold_text(layer, txt)
    return layer

def add_text_layer_from_file(image, filename, font, colour=(0, 0, 0)):
    txt = read_text(filename)
    return add_text(image, txt, font, colour)

def place_text(layer, x, y, x2=None, y2=None, w=None, h=None, xalign=LEFT, yalign=TOP):
    if layer is None:
        return
    if x2 is not None:
        w = x2 - x
    if y2 is not None:
        h = y2 - y
    if w is not None:
        if h is None:
            h = layer.image.height - y
        pdb.gimp_text_layer_resize(layer, w, h)
    if xalign == CENTER:
        x = x - layer.width / 2
    elif xalign == RIGHT:
        x = x - layer.width
    if yalign == CENTER:
        y = y - layer.height / 2
    elif yalign == BOTTOM:
        y = y - layer.height
    layer.translate(x, y)

def reduce_text_to_fit(layer, x1, x2):
    (font_size, units) = pdb.gimp_text_layer_get_font_size(layer)
    while layer.width > x2 - x1:
        font_size -= 1
        pdb.gimp_text_layer_set_font_size(layer, font_size, units)

def bold_text(layer, txt=None):
    # XXX: Requires a patched GIMP to set text markup
    # See https://bugzilla.gnome.org/show_bug.cgi?id=724101
    if txt is None:
        txt = pdb.gimp_text_layer_get_markup(layer)
    markup = '<b>%s</b>' % txt
    pdb.gimp_text_layer_set_markup(layer, markup)

def underline_text(layer):
    # XXX: Requires a patched GIMP to set text markup
    # See https://bugzilla.gnome.org/show_bug.cgi?id=724101
    markup = pdb.gimp_text_layer_get_markup(layer)
    markup = '<u>%s</u>' % markup
    pdb.gimp_text_layer_set_markup(layer, markup)

def word_wrap(layer, text, width, max_height = None, start_tag='', end_tag=''):
    # This is a workaround for the lack of a fixed-width + dynamic-height
    # setting for text boxes in the GIMP - otherwise there is no easy way to
    # wrap the text AND have it vertically centered.
    words = text.split(' ')
    if not len(words):
        return ''
    txt = words[0]
    for (i, word) in enumerate(words[1:], 1):
        txt1 = '%s %s' % (txt, word)
        markup = '%s%s%s' % (start_tag, txt1, end_tag)
        try: # Quick hack to avoid splitting up <span> tags
            pdb.gimp_text_layer_set_markup(layer, markup)
        except:
            txt = txt1
            continue
        if layer.width > width:
            txt1 = '%s\n%s' % (txt, word)
            markup = '%s%s%s' % (start_tag, txt1, end_tag)
            pdb.gimp_text_layer_set_markup(layer, markup)
            if max_height is not None and layer.height > max_height:
                markup = '%s%s%s' % (start_tag, txt, end_tag)
                pdb.gimp_text_layer_set_markup(layer, markup)
                return ' '.join([word] + words[1+i:])
            width = max(width, layer.width)
        txt = txt1
    return ''

def bold_word_wrap(layer, text, width, max_height = None):
    return word_wrap(layer, text, width, max_height, start_tag='<b>', end_tag='</b>')

def blur_layer(image, layer, radius = 1.0):
    pdb.plug_in_gauss_rle2(image, layer, radius, radius)

def save_dds(image, filename, alpha):
    alpha = alpha and 3 or 1
    try:
        pdb.file_dds_save(
                image,
                image.active_layer,
                filename, # filename
                filename, # raw_filename
                alpha, # 1 = DXT1 (no alpha), 3 = DXT5 (alpha)
                0, # 1 = generate mipmaps <--- XXX Set this for in-game objects
                0, # 0 = save current layer
                0, # format
                -1, # transparent-index
                0, # DXT compression color-type (Tweaking may help in some cases)
                0, # Dither
                0, # mipmap-filter - maybe try tweaking this for in-game objects
                0, # gamma-correct
                2.2, # gamma
        )
    except:
        # Try newer API
        pdb.file_dds_save(
                image,
                image.active_layer,
                filename, # filename
                filename, # raw_filename
                alpha, # 1 = DXT1 (no alpha), 3 = DXT5 (alpha)
                0, # 1 = generate mipmaps <--- XXX Set this for in-game objects
                0, # 0 = save current layer
                0, # format
                -1, # transparent-index
                0, # mipmap-filter - maybe try tweaking this for in-game objects
                0, # mipmap-wrap
                0, # gamma-correct
                0, # use srgb colorspace for gamma correction
                2.2, # gamma
                0, # use perceptual error metric during DXT compression
                0, # preserve alpha coverage
                0.5, # alpha test threshold
        )

def save_png(image, filename):
    pdb.file_png_save2(image, image.active_layer, filename, filename,
            0, # interlace
            9, # compression
            0, # save background colour
            0, # save gamma
            0, # save layer offset
            1, # save pHYs (resolution?)
            1, # save creation time
            1, # save comment
            1, # preserve colour of transparent pixels
    )

def save_jpg(image, filename):
    pdb.file_jpeg_save(image, image.active_layer, filename, filename,
            0.9, # quality
            0.0, # smoothing
            1, # optimize
            0, # progressive
            "Generated by DarkStarSword's Miasmata translation scripts", # comment
            0, # Subsampling option number. 0 = 4:4:4?
            1, # baseline
            0, # restart
            1, # dct algorithm. 1 = Integer?
    )

def save_xcf(image, filename):
    pdb.gimp_xcf_save(0, image, image.active_layer, filename, filename)
    image.clean_all()
