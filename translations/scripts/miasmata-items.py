#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

neu_phollick_alpha = Font('Neu Phollick Alpha', 36.0, True, -10.0)

def compose_tags(image, item_name):
    tags = read_text('%s.txt' % item_name).split('\n')
    tag_h = 97
    tag_x = (140, 400)
    tag_w = 180

    for y in range(4):
        for x in range(2):
            layer = add_text(image, tags.pop(0), neu_phollick_alpha)
            pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
            # place_text(layer, tag_x[x], y*tag_h + tag_h/2, w=tag_w, xalign=CENTER, yalign=CENTER)
            place_text(layer, tag_x[x], y*tag_h + 20, w=tag_w, xalign=CENTER)
            if tags == []:
                return

def compose_item_image(item_name, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    globals()['compose_%s' % item_name.lower()](image, item_name)

    save_xcf(image, '%s.xcf' % output_basename)
    image2 = pdb.gimp_image_duplicate(image)
    image2.merge_visible_layers(CLIP_TO_IMAGE)
    save_dds(image2, '%s.dds' % output_basename, True)
    save_png(image2, '%s.png' % output_basename)

register(
    "miasmata_item",
    "Compose an image for an item in Miasmata",
    "Compose an image for an item in Miasmata",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Item",
    None,
    [
        (PF_FILE, "item_name", "Which item to compose. Each item has it's own requirements for where it looks for the input text.", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_item_image,
)

main()
