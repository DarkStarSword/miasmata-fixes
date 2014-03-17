#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

indent_a = 114
indent_b = 156
font_a = Font('Neu Phollick Alpha', 40.0, True, -8.0)
font_b = Font('Neu Phollick Alpha', 38.0, True)

font_note = Font('Neu Phollick Alpha', 22.0, True)
objnote_x1 = 57
objnote_x2 = 200

class Objective(object):
    def __init__(self, indent=indent_a, y=5, wrap=None, font=font_a):
        self.indent, self.y, self.wrap, self.font = indent, y, wrap, font

objectives = {
    'OBJECTIVE_A_Placeholder': Objective(),
    'OBJECTIVE_A': Objective(wrap=865),
    'OBJECTIVE_B': Objective(indent=indent_b),
    'OBJECTIVE_C': Objective(indent=indent_b),
    'OBJECTIVE_D': Objective(indent=indent_b),
    'OBJECTIVE_E': Objective(y=16),
    'OBJECTIVE_F': Objective(y=8, font=font_b),
    'OBJECTIVE_G': Objective(y=8, font=font_b),
    'OBJECTIVE_H': Objective(y=8, font=font_b),
}

def compose_objective_image(objective_name, source_blank_image, output_basename):
    objective = objectives[objective_name]
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    text_layer = add_text_layer_from_file(image, '%s.txt' % objective_name, objective.font)
    place_text(text_layer, objective.indent, objective.y, objective.wrap)

    save(image, output_basename)

def compose_objective_page(source_txt_file, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    (primary, secondary) = read_text(source_txt_file).split('\n', 1)

    layer = add_text(image, primary, font_a)
    place_text(layer, 75, 26)

    layer = add_text(image, secondary, font_a)
    place_text(layer, 75, 655)

    save(image, output_basename)

def compose_objective_note(source_txt_file, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    try:
        pdb.gimp_image_convert_rgb(image)
    except:
        pass

    colour = (128, 0, 0)
    if 'Plant' in source_txt_file:
        colour = (50, 40, 190)

    text_layer = add_text_layer_from_file(image, source_txt_file, font_note, colour=colour)
    pdb.gimp_layer_set_mode(text_layer, MULTIPLY_MODE)
    reduce_text_to_fit(text_layer, objnote_x1, objnote_x2)
    place_text(text_layer, objnote_x1, image.height / 2, yalign=CENTER)

    save(image, output_basename, png=True)

register(
    "miasmata_objective",
    "Compose a Miasmata objective",
    "Compose a Miasmata objective",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Objective",
    None,
    [
        (PF_FILE, "objective_name", "Name of the objective. There must be a utf-8 encoded text file of this name.", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_objective_image,
)

register(
    "miasmata_objective_page",
    "Compose Miasmata objective page",
    "Compose Miasmata objective page",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/Objective _page",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded text file with the translation of Primary Objective: and Secondary Objective: on each line", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_objective_page,
)

register(
    "miasmata_objective_note",
    "Compose Miasmata objective note",
    "Compose Miasmata objective note",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/Ob_jective note",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded text file with the objective note", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_objective_note,
)

main()
