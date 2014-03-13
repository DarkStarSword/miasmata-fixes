#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font = 'Neu Phollick Alpha'
font_size = 55.0
line_spacing = -7.0
letter_spacing = 0.4

x = 205
w = 995 - x

def compose_index_image(source_txt_file, source_blank_image, output_basename):
    txt = open(source_txt_file, 'rb').read().decode('utf-8').strip()

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    text = add_text_layer(image, txt, font, font_size)
    pdb.gimp_text_layer_set_justification(text, TEXT_JUSTIFY_CENTER)
    pdb.gimp_text_layer_set_line_spacing(text, line_spacing)
    pdb.gimp_text_layer_set_letter_spacing(text, letter_spacing)

    # bold_text(text, txt)
    # pdb.gimp_text_layer_resize(text, w, text.height)
    bold_word_wrap(text, txt, w)

    pdb.gimp_layer_translate(text, x + (w - text.width) / 2, (image.height - text.height) / 2)

    save_xcf(image, '%s.xcf' % output_basename)
    image2 = pdb.gimp_image_duplicate(image)
    image2.flatten()
    save_dds(image2, '%s.dds' % output_basename, False)
    save_jpg(image2, '%s.jpg' % output_basename)

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

main()