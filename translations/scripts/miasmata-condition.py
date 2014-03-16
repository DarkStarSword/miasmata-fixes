#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font_l = Font('Neu Phollick Alpha', 42.0, True)
font_s = Font('Neu Phollick Alpha', 38.0, True)
font_s1 = Font('Neu Phollick Alpha', 33.0, True)

lx, rx = 491, 526

def save(image, output_basename):
    save_xcf(image, '%s.xcf' % output_basename)
    image2 = pdb.gimp_image_duplicate(image)
    image2.flatten()
    save_dds(image2, '%s.dds' % output_basename, False)
    save_jpg(image2, '%s.jpg' % output_basename)

def compose_condition_page(source_txt_file, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    layer = add_text_layer_from_file(image, source_txt_file, font_l)
    place_text(layer, lx, 275, xalign=RIGHT)

    save(image, output_basename)

def compose_condition_split(source_txt_file, source_blank_image, output_basename):
    if 'Primary' in source_txt_file:
        y = 13
        font = font_l
    else:
        y = 7
        font = font_s

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    (left, right) = map(unicode.strip, read_text(source_txt_file).split(':', 1))
    left = '%s:' % left

    layer = add_text(image, left, font)
    place_text(layer, lx, y, xalign=RIGHT)

    layer = add_text(image, right, font)
    pdb.gimp_layer_set_mode(layer, MULTIPLY_MODE)
    place_text(layer, rx, y)

    save(image, output_basename)

def compose_condition_active(source_txt_file, source_blank_image, output_basename):
    colour = (128, 0, 0)
    if 'ClarityTonic' in source_txt_file:
        colour = (0, 128, 0)
    x1, x2 = 244, 735

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    layer = add_text_layer_from_file(image, source_txt_file, font_s1, colour)
    pdb.gimp_layer_set_mode(layer, MULTIPLY_MODE)
    reduce_text_to_fit(layer, x1, x2)
    place_text(layer, 244, image.height / 2, yalign=CENTER)

    save(image, output_basename)

def compose_condition_small(source_txt_file, source_blank_image, output_basename):
    colour = (0, 128, 0)

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    layer = add_text_layer_from_file(image, source_txt_file, font_s, colour)
    pdb.gimp_layer_set_mode(layer, MULTIPLY_MODE)
    place_text(layer, 48, 25, xalign=CENTER, yalign=CENTER)

    save(image, output_basename)

register(
    "miasmata_condition_page",
    "Compose Miasmata condition page",
    "Compose Miasmata condition page",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/&Condition page",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded text file with the translation of 'Abilities:'", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_condition_page,
)

register(
    "miasmata_condition_small",
    "Compose Miasmata condition active status",
    "Compose Miasmata condition active status",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Small condition",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded text file", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_condition_small,
)

register(
    "miasmata_condition_active",
    "Compose Miasmata condition active status",
    "Compose Miasmata condition active status",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Active condition",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded text file", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_condition_active,
)

register(
    "miasmata_condition_split",
    "Compose Miasmata split condition",
    "Compose Miasmata split condition",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Split condition",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded text file", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_condition_split,
)

main()
