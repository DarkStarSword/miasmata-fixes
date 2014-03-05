#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font = 'Neu Phollick Alpha'
font_size = 55.0
line_spacing = -7.0
letter_spacing = 0.4

x = 205
w = 995 - x

def bold_text(layer, txt):
    # XXX: Requires a patched GIMP to set text markup
    # See https://bugzilla.gnome.org/show_bug.cgi?id=724101
    markup = '<b>%s</b>' % txt
    pdb.gimp_text_layer_set_markup(layer, markup)

def bold_word_wrap(layer, text, width, start_tag='<b>', end_tag='</b>'):
    # This is a workaround for the lack of a fixed-width + dynamic-height
    # setting for text boxes in the GIMP - otherwise there is no easy way to
    # wrap the text AND have it vertically centered.
    words = text.split(' ')
    if not len(words):
        return
    txt = words[0]
    for word in words[1:]:
        txt1 = '%s %s' % (txt, word)
        markup = '%s%s%s' % (start_tag, txt1, end_tag)
        pdb.gimp_text_layer_set_markup(layer, markup)
        if layer.width > width:
            txt1 = '%s\n%s' % (txt, word)
            markup = '%s%s%s' % (start_tag, txt1, end_tag)
            pdb.gimp_text_layer_set_markup(layer, markup)
            width = max(width, layer.width)
        txt = txt1

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
