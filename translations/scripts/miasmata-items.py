#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

neu_phollick_alpha = Font('Neu Phollick Alpha', 36.0, True, -10.0)
sample_tray_font = Font('Georgia', 42.0, False)
# bottle_font = Font('Century Schoolbook L', 14.0, True)
# bottle_font = Font('Eutheric', 16.0, True)
# bottle_font = Font('Nimbus Mono L', 16.0, True)
# bottle_font = Font('Norlik', 16.0, True)
# bottle_font = Font('Serif', 14.0, True)
bottle_font = Font('URW Bookman L', 14.0, True)

def compose_tags(image, item_name, output_basename):
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
                break

    save(image, output_basename, True)

def compose_lab_sampletrays(image, item_name, output_basename):
    labels = map(unicode.strip, read_text('%s.txt' % item_name).split('\n\n'))

    label_x = (256, 768)
    label_h = 140
    label_y = (image.height - 3*label_h/2, image.height - label_h/2)

    for y in range(2):
        for x in range(2):
            layer = add_text(image, labels.pop(0), sample_tray_font, colour=(255, 255, 255))
            pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
            word_wrap(layer, None, 450)
            place_text(layer, label_x[x], label_y[y], xalign=CENTER, yalign=CENTER)

    save(image, output_basename, False)

def compose_lab_darkbottle(image, item_name, output_basename):
    labels = map(unicode.strip, read_text('%s.txt' % item_name).split('\n'))

    label_x = 64
    label_h = 24
    label_y = (image.height - 3*label_h/2, image.height - label_h/2 + 2)

    for y in range(2):
        layer = add_text(image, labels.pop(0), bottle_font)
        pdb.gimp_text_layer_set_hint_style(layer, TEXT_HINT_STYLE_FULL)
        reduce_text_to_fit(layer, 0, 124)
        place_text(layer, label_x, label_y[y], xalign=CENTER, yalign=CENTER)

    save(image, output_basename, False)

def compose_item_image(item_name, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    globals()['compose_%s' % item_name.lower()](image, item_name, output_basename)

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
