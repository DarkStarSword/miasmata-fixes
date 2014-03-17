#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

header_font = Font('Neu Phollick Alpha', 45.0, True)
font = Font('Neu Phollick Alpha', 40.0, True, -5.0)
font_small = Font('Neu Phollick Alpha', 32.0, True, -5.0)

def desc_font(plant):
    return {
            'Plant_E': font_small,
            'Plant_J': font_small,
    }.get(plant, font)

w = h = 1024

lh_x = 148
lh_w = w - lh_x

header_h = 64

subheader_x2 = 293
subheader_rx = 310
name_y2 = 140
genus_y2 = 203

desc_x, desc_x2 = 185, 990

def desc_header_y(plant):
    return {
            'Plant_E': 532,
            'Plant_J': 532,
    }.get(plant, 696)

def desc_y(plant):
    return desc_header_y(plant) + {
            'Plant_E': 50,
            'Plant_J': 50,
    }.get(plant, 62)


def add_header(image, header_txt):
    layer = add_text(image, header_txt, header_font)
    place_text(layer, lh_x + lh_w / 2, header_h / 2, xalign=CENTER, yalign=CENTER)

def add_subheader(image, left_txt, right_txt, y2):
    layer = add_text(image, left_txt, font)
    place_text(layer, subheader_x2, y2, xalign=RIGHT, yalign=BOTTOM)
    layer = add_text(image, right_txt, font)
    place_text(layer, subheader_rx, y2, yalign=BOTTOM)

def add_desc_header(image, txt, plant):
    layer = add_text(image, txt, font)
    place_text(layer, desc_x, desc_header_y(plant))

def add_desc(image, txt, plant):
    layer = add_text(image, txt, desc_font(plant))
    y = desc_y(plant)
    place_text(layer, desc_x, y, desc_x2)


def compose_drug_image(template_txt_file, source_txt_file, source_blank_image, output_basename):
    template = read_text(template_txt_file)
    (header_txt, name_templ_txt, func_templ_txt) = template.split('\n')

    txt = read_text(source_txt_file)
    name_txt, desc_txt = map(unicode.strip, txt.split('\n', 1))

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    add_header(image, header_txt)
    add_subheader(image, name_templ_txt, name_txt, name_y2)
    add_desc_header(image, func_templ_txt, output_basename)
    add_desc(image, desc_txt, output_basename)

    save(image, output_basename)

def compose_plant_image(template_txt_file, source_txt_file, source_blank_image, output_basename):
    template = read_text(template_txt_file)
    (header_txt, name_templ_txt, genus_templ_txt, observ_templ_txt) = template.split('\n')

    txt = read_text(source_txt_file)
    name_txt, genus_txt, desc_txt = map(unicode.strip, txt.split('\n', 2))

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    add_header(image, header_txt)
    add_subheader(image, name_templ_txt, name_txt, name_y2)
    add_subheader(image, genus_templ_txt, genus_txt, genus_y2)
    add_desc_header(image, observ_templ_txt, output_basename)
    add_desc(image, desc_txt, output_basename)

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

register(
    "miasmata_plant",
    "Compose an image for Miasmata's Journal discovered plant pages",
    "Compose an image for Miasmata's Journal discovered plant pages",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Plant",
    None,
    [
        (PF_FILE, "template_txt_file", "utf-8 encoded file with the translations of 'Specimen Observation', 'Name:', 'Genus:' and 'Observations:', one per line", None),
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the text to place on the image", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_plant_image,
)

main()
