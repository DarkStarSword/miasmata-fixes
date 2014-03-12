#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

default_font = 'Neu Phollick Alpha'
default_font_size = 40.0
default_line_spacing = 5.0

global_w = 2048
global_h = 1024

def read_text(filename):
    return open(filename, 'rb').read().decode('utf-8').strip()

def add_text(image, txt, font=default_font, font_size=default_font_size, line_spacing=default_line_spacing):
    layer = add_text_layer(image, txt, font, font_size)
    pdb.gimp_text_layer_set_line_spacing(layer, line_spacing)
    pdb.gimp_text_layer_set_markup(layer, txt)
    bold_text(layer, txt)
    return layer

def add_text_layer_from_file(image, filename, font=default_font, font_size=default_font_size, line_spacing=default_line_spacing):
    txt = read_text(filename)
    return add_text(image, txt, font, font_size, line_spacing)

def place_text(layer, x, y, x2=None, y2=None, w=None, h=None, xcenter=False, ycenter=False):
    if x2 is not None:
        w = x2 - x
    if y2 is not None:
        h = y2 - y
    if w is not None:
        if h is None:
            h = global_h - y
        pdb.gimp_text_layer_resize(layer, w, h)
    if xcenter:
        x = x - layer.width / 2
    if ycenter:
        y = y - layer.height / 2
    layer.translate(x, y)

def compose_note_0(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name)
    place_text(body, 235, 55, 980)

    def drug_text(filename):
        txt = read_text(filename).split('\n')
        txt[1] = '<span font_size="%i">%s</span>' % (1024 * 30, txt[1])
        txt = '\n'.join(txt)
        layer = add_text(image, txt)
        pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
        return layer

    agentx = drug_text('%s_X.txt' % note_name)
    place_text(agentx, 1478, 172, xcenter=True, ycenter=True)

    agenty = drug_text('%s_Y.txt' % note_name)
    place_text(agenty, 1278, 395, xcenter=True, ycenter=True)

    agentz = drug_text('%s_Z.txt' % note_name)
    place_text(agentz, 1718, 395, xcenter=True, ycenter=True)

    cure = drug_text('%s_cure.txt' % note_name)
    place_text(cure, 1486, 758, xcenter=True, ycenter=True)

def compose_note_image(note_name, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    # getattr(globals(), 'compose_%s' % note_name.lower())(image, note_name)
    globals()['compose_%s' % note_name.lower()](image, note_name)

    save_xcf(image, '%s.xcf' % output_basename)
    image2 = pdb.gimp_image_duplicate(image)
    image2.flatten()
    save_dds(image2, '%s.dds' % output_basename, False)
    save_jpg(image2, '%s.jpg' % output_basename)

register(
    "miasmata_note",
    "Compose an image for a note in Miasmata",
    "Compose an image for a note in Miasmata",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Note",
    None,
    [
        (PF_FILE, "note_name", "Which note to compose. Each note has it's own requirements for where it looks for the input text.", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_note_image,
)

main()
