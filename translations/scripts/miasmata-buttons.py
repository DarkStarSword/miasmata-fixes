#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font = Font('Century Gothic', 24.0, True)

def compose_button(button_txt_file, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    pdb.gimp_image_convert_rgb(image)

    off = 0
    if output_basename.lower().startswith('yes'):
        off = 5
    layer = add_text_layer_from_file(image, button_txt_file, font, colour=(255,255,255))
    pdb.gimp_text_layer_set_letter_spacing(layer, -1.0)
    place_text(layer, off + (image.width - 7) / 2, image.height / 2 - 1, xalign=CENTER, yalign=CENTER)

    save_xcf(image, '%s.xcf' % output_basename)
    image.merge_visible_layers(CLIP_TO_IMAGE)

    # FIXME: Probably need to do something special here:
    # Need to convert back to indexed image and may need to do something
    # special exporting to dds (not using DXT compression)

    save_dds(image, '%s.dds' % output_basename, True)
    save_png(image, '%s.png' % output_basename)

register(
    "miasmata_button",
    "Compose an image for the yes/no buttons in Miasmata",
    "Compose an image for the yes/no buttons in Miasmata",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Button",
    None,
    [
        (PF_FILE, "button_txt_file", "utf-8 encoded file with the text to place on the button.", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_button,
)

main()
