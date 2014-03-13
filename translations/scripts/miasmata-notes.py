#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

LEFT = TOP = 0
CENTER = 1
RIGHT = BOTTOM = 2

class Font(object):
    def __init__(self, font, size, bold = False, line_spacing = 0.0):
        self.font, self.size, self.bold, self.line_spacing = \
                font, size, bold, line_spacing

neu_phollick_alpha = Font('Neu Phollick Alpha', 40.0, True, 5.0)
fnt_23rd_street = Font('23rd Street', 40.0, False, 15.0)
fnt_23rd_street_b = Font('23rd Street', 40.0, True, 6.0)
fnt_23rd_street_c = Font('23rd Street', 36.0, True, 6.0)
fg_nora = Font('FG Norah', 40.0, False, -8.0)
flute = Font('Flute', 40.0, True, -5.0)
wiki = Font('Wiki', 40.0, True, 5.0)

global_w = 2048
global_h = 1024

def read_text(filename):
    return open(filename, 'rb').read().decode('utf-8').strip()

def add_text(image, txt, font=neu_phollick_alpha):
    layer = add_text_layer(image, txt, font.font, font.size)
    pdb.gimp_text_layer_set_line_spacing(layer, font.line_spacing)
    pdb.gimp_text_layer_set_markup(layer, txt)
    pdb.gimp_layer_set_mode(layer, MULTIPLY_MODE)
    if font.bold:
        bold_text(layer, txt)
    return layer

def add_text_layer_from_file(image, filename, font=neu_phollick_alpha):
    txt = read_text(filename)
    return add_text(image, txt, font)

def place_text(layer, x, y, x2=None, y2=None, w=None, h=None, xalign=LEFT, yalign=TOP):
    if x2 is not None:
        w = x2 - x
    if y2 is not None:
        h = y2 - y
    if w is not None:
        if h is None:
            h = global_h - y
        pdb.gimp_text_layer_resize(layer, w, h)
    if xalign == CENTER:
        x = x - layer.width / 2
    elif xalign == RIGHT:
        x = x - layer.width
    if yalign == CENTER:
        y = y - layer.height / 2
    elif yalign == BOTTOM:
        y = y - layer.height
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
    place_text(agentx, 1478, 172, xalign=CENTER, yalign=CENTER)

    agenty = drug_text('%s_Y.txt' % note_name)
    place_text(agenty, 1278, 395, xalign=CENTER, yalign=CENTER)

    agentz = drug_text('%s_Z.txt' % note_name)
    place_text(agentz, 1718, 395, xalign=CENTER, yalign=CENTER)

    cure = drug_text('%s_cure.txt' % note_name)
    place_text(cure, 1486, 758, xalign=CENTER, yalign=CENTER)

def compose_note_1(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, fnt_23rd_street)
    place_text(body, 1100, 100, 1785)

def compose_note_2(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, fg_nora)
    place_text(body, 210, 45, 970)

    title = add_text_layer_from_file(image, '%s_title.txt' % note_name, fg_nora)
    underline_text(title)
    place_text(title, 1450, 221, xalign=CENTER)

    statue = add_text_layer_from_file(image, '%s_statue.txt' % note_name, fg_nora)
    place_text(statue, 1645, 822, yalign=CENTER)

def compose_note_3(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, fnt_23rd_street_b)
    place_text(body, 205, 55, 970)

    title = add_text_layer_from_file(image, '%s_title.txt' % note_name, fnt_23rd_street_c)
    place_text(title, 1465, 65, xalign=CENTER)

    vega = add_text_layer_from_file(image, 'Vega.txt', fnt_23rd_street_c)
    place_text(vega, 1278, 260, xalign=CENTER, yalign=CENTER)

    algae = add_text_layer_from_file(image, '%s_algae.txt' % note_name, fnt_23rd_street_c)
    place_text(algae, 1556, 898, xalign=RIGHT, yalign=CENTER)

    ruin = add_text_layer_from_file(image, '%s_ruin_site_b.txt' % note_name, fnt_23rd_street_c)
    place_text(ruin, 1630, 940, yalign=CENTER)

def compose_note_4(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, flute)
    place_text(body, 1087, 75, 1880)

def compose_note_5(image, note_name):
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, wiki)
    place_text(layer, 200, 77, 930)

    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, wiki)
    place_text(layer, 1325, 454, xalign=CENTER, yalign=CENTER)

# There is no note 6...

def compose_note_7(image, note_name):
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, neu_phollick_alpha)
    place_text(layer, 1130, 90, 1830)

def compose_note_8(image, note_name):
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, flute)
    place_text(layer, 1457, 250, xalign=CENTER, yalign=CENTER)

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
