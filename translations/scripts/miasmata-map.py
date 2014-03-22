#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

font = Font('Neu Phollick Alpha', 20.0, True)

radius = 8.0

def add_map_text(image, file, x, y, xalign=CENTER, yalign=CENTER):
    txt = read_text(file)
    shadow = add_text(image, txt, font, colour=(0, 0, 0))
    place_text(shadow, x, y, xalign=xalign, yalign=yalign)
    pdb.gimp_layer_resize(shadow, shadow.width + 2*radius, shadow.height + 2*radius, radius, radius)
    blur_layer(image, shadow, radius=radius)
    mask = pdb.gimp_layer_create_mask(shadow, ADD_ALPHA_TRANSFER_MASK)
    pdb.gimp_layer_create_mask(shadow, ADD_ALPHA_TRANSFER_MASK)
    pdb.gimp_layer_add_mask(shadow, mask)
    pdb.gimp_levels(mask, HISTOGRAM_VALUE, 0, 128, 1.0, 0, 255)
    pdb.gimp_layer_remove_mask(shadow, MASK_APPLY)
    layer = add_text(image, txt, font, colour=(255, 255, 255))
    blur_layer(image, layer, 0.5)
    place_text(layer, x, y, xalign=xalign, yalign=yalign)

def compose_overlay_map(source_blank_image, output_basename, include_text):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    if include_text:
        add_map_text(image, 'outpost_draco.txt', 1975, 2357)
        add_map_text(image, 'outpost_sirius.txt', 2722, 2528)
        add_map_text(image, 'outpost_rigel.txt', 3000, 2930)
        add_map_text(image, 'outpost_vega.txt', 522, 1850)
        add_map_text(image, 'ruin_b.txt', 835, 2626)
        add_map_text(image, 'ruin_c.txt', 2344, 1488)
        add_map_text(image, 'outpost_polaris.txt', 3590, 925)
        add_map_text(image, 'ruin_a.txt', 1487, 795)
        add_map_text(image, 'outpost_tau.txt', 1517, 517, xalign=RIGHT)
        add_map_text(image, 'boat_landing.txt', 92, 65)

    save(image, output_basename)

register(
    "miasmata_map",
    "Compose the Miasmata overlay map",
    "Compose the Miasmata overlay map",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Map",
    None,
    [
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
        (PF_BOOL, "include_text", "Add text. If false, just copy (convenience for Map_FilledIn)", None),
    ],
    [],
    compose_overlay_map,
)

main()
