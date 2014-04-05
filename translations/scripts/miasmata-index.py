#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font_s = Font('Neu Phollick Alpha', 55.0, False, -7.0, letter_spacing=2.5)
font_l = Font('Neu Phollick Alpha', 68.0, False, -7.0, letter_spacing=2.5)
font_l2 = Font('Neu Phollick Alpha', 65.0, False, -6.0, letter_spacing=2.5)
font_t = Font('Neu Phollick Alpha', 40.0, True)

x = 210
w = 995 - x

def font(name):
    if name == 'LIST_IAmCured':
        return font_l
    if name.upper().startswith('LIST_NOTE'):
        return font_l2
    return font_s

def compose_index_image(source_txt_file, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    text = add_text_layer_from_file(image, source_txt_file, font(output_basename))
    pdb.gimp_text_layer_set_justification(text, TEXT_JUSTIFY_CENTER)
    word_wrap(text, None, w)

    pdb.gimp_layer_translate(text, x + (w - text.width) / 2, (image.height - text.height) / 2)

    # Try to get closer to the original font weight used in Miasmata than we
    # can achieve simply rendering the font in Bold (the letter spacing must
    # also be increased). Create three copies of the layer - one moves 1px to
    # the left, the second moves 1px to the right, and the third uses a
    # convolution matrix to move 1/2px up & down, then all are merged back
    # together. It would be nice to do the whole thing with a single matrix,
    # but I want to avoid blurring the original (i.e. can't have a divisor and
    # can't have centre < 1) and yet can't allow the matrix values to total > 1
    # as that mucks up the colours (and normalising == adding a divisor).
    layer_l = text.copy(); image.add_layer(layer_l, 0); layer_l.translate(-1, 0)
    layer_r = text.copy(); image.add_layer(layer_r, 0); layer_r.translate(1, 0)
    layer_v = text.copy(); image.add_layer(layer_v, 0)
    # This matrix seems to be transposed compared to the GUI:
    matrix = [  0,   0,   0,   0,   0,
                0,   0,   0,   0,   0,
                0, 0.5,   0, 0.5,   0,
                0,   0,   0,   0,   0,
                0,   0,   0,   0,   0]
    channels = [False, True, True, True, True] # Gray, RGB, Alpha
    pdb.plug_in_convmatrix(image, layer_v, 25, matrix, False, 1, 0, 5, channels, 2)
    layer = pdb.gimp_image_merge_down(image, layer_v, CLIP_TO_IMAGE)
    layer = pdb.gimp_image_merge_down(image, layer, CLIP_TO_IMAGE)
    layer = pdb.gimp_image_merge_down(image, layer, CLIP_TO_IMAGE)

    if output_basename in ('LIST_X', 'LIST_Y', 'LIST_Z', 'List_K'):
        pdb.gimp_layer_set_mode(layer, MULTIPLY_MODE)
    else:
        pdb.gimp_layer_set_mode(layer, BURN_MODE)

    save(image, output_basename)

def compose_index_title_image(source_txt_name, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    layer = add_text_layer_from_file(image, source_txt_name, font_t)
    place_text(layer, 220, 10)
    save(image, output_basename)

register(
    "miasmata_index",
    "Compose an image for Miasmata's Journal index pages",
    "Compose an image for Miasmata's Journal index pages",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Index",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the text to place on the image", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_index_image,
)

register(
    "miasmata_index_title",
    "Compose a title image for Miasmata's Journal index pages",
    "Compose a title image for Miasmata's Journal index pages",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Index",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the text to place on the image", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_index_title_image,
)

main()
