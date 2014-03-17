#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font = 'Neu Phollick Alpha'
header_font_size = 45.0
font_size = 40.0
desc_line_spacing = -5.0

def desc_font_size(plant):
    return {
            'Plant_E': 32,
            'Plant_J': 32,
    }.get(plant, font_size)

w = h = 1024

lh_x = 148
lh_w = w - lh_x

header_h = 64

name_templ_x2 = 280
name_x        = 310
name_y2 = 140

function_x = 185
def function_y(plant):
    return {
            'Plant_E': 532,
            'Plant_J': 532,
    }.get(plant, 696)

def desc_y(plant):
    return function_y(plant) + {
            'Plant_E': 50,
            'Plant_J': 50,
    }.get(plant, 62)

desc_x2 = 990

def compose_drug_image(template_txt_file, source_txt_file, source_blank_image, output_basename):
    template = open(template_txt_file, 'rb').read().decode('utf-8').strip()
    (header_txt, name_templ_txt, func_templ_txt) = template.split('\n')

    txt = open(source_txt_file, 'rb').read().decode('utf-8').strip()
    name_txt, desc_txt = map(unicode.strip, txt.split('\n', 1))

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    header = add_text_layer(image, header_txt, font, header_font_size)
    bold_text(header, header_txt)
    header.translate(lh_x + (lh_w - header.width) / 2, (header_h - header.height) / 2)
    # blur_layer(image, header)

    name_templ = add_text_layer(image, name_templ_txt, font, font_size)
    bold_text(name_templ, name_templ_txt)
    name_templ.translate(name_templ_x2 - name_templ.width, name_y2 - name_templ.height)

    name = add_text_layer(image, name_txt, font, font_size)
    bold_text(name, name_txt)
    name.translate(name_x, name_y2 - name.height)

    func_temp = add_text_layer(image, func_templ_txt, font, font_size)
    bold_text(func_temp, func_templ_txt)
    func_temp.translate(function_x, function_y(output_basename))

    desc = add_text_layer(image, desc_txt, font, desc_font_size(output_basename))
    bold_text(desc, desc_txt)
    pdb.gimp_text_layer_set_line_spacing(desc, desc_line_spacing)
    y = desc_y(output_basename)
    desc.translate(function_x, y)
    pdb.gimp_text_layer_resize(desc, desc_x2 - function_x, h - y)

    save(image, output_basename)

register(
    "miasmata_drug",
    "Compose an image for Miasmata's Journal drug synthesis pages",
    "Compose an image for Miasmata's Journal drug synthesis pages",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Drug",
    None,
    [
        (PF_FILE, "template_txt_file", "utf-8 encoded file with the translations of 'Biomedical Research', 'Name:' and 'Function:', one per line", None),
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the text to place on the image", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_drug_image,
)

main()
