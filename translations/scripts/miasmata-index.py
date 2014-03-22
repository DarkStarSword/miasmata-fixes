#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font_s = Font('Neu Phollick Alpha', 55.0, True, -7.0, letter_spacing=0.4)
font_l = Font('Neu Phollick Alpha', 68.0, True, -7.0, letter_spacing=0.4)
font_t = Font('Neu Phollick Alpha', 40.0, True)

x = 205
w = 995 - x

def font(name):
    if name == 'LIST_IAmCured' or name.upper().startswith('LIST_NOTE'):
        return font_l
    return font_s

def compose_index_image(source_txt_file, source_blank_image, output_basename):
    txt = open(source_txt_file, 'rb').read().decode('utf-8').strip()

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    text = add_text(image, txt, font(output_basename))
    pdb.gimp_text_layer_set_justification(text, TEXT_JUSTIFY_CENTER)
    if output_basename in ('LIST_X', 'LIST_Y', 'LIST_Z', 'List_K'):
        pdb.gimp_layer_set_mode(text, MULTIPLY_MODE)
    else:
        pdb.gimp_layer_set_mode(text, BURN_MODE)

    bold_word_wrap(text, txt, w)

    pdb.gimp_layer_translate(text, x + (w - text.width) / 2, (image.height - text.height) / 2)

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
