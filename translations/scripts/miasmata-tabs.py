#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font = Font('Georgia', 84.0, False)
max_font_size = 84.0
max_width = 350

# Alternate close match:
# font = Font('Century Schoolbook L Bold', 73.0, True)
# status_size = 84.0
# notes_size = 78.0
# lab_size = 61.0

def compose_tab(tab_txt_file, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    layer = add_text_layer_from_file(image, tab_txt_file, font)
    font_size = max_font_size
    pdb.gimp_text_layer_set_letter_spacing(layer, -2.0)
    while layer.width > max_width:
        font_size -= 1
        pdb.gimp_text_layer_set_font_size(layer, font_size, PIXELS)

    place_text(layer, image.width / 2, image.height / 2, xalign=CENTER, yalign=CENTER)

    save_xcf(image, '%s.xcf' % output_basename)
    image.merge_visible_layers(CLIP_TO_IMAGE)
    save_dds(image, '%s.dds' % output_basename, False)
    save_jpg(image, '%s.jpg' % output_basename)

register(
    "miasmata_journal_tabs",
    "Compose an image for the journal tabs in Miasmata",
    "Compose an image for the journal tabs in Miasmata",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Tabs",
    None,
    [
        (PF_FILE, "tab_txt_file", "utf-8 encoded file with the text to place on the tab.", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_tab,
)

main()
