#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

import os

def heal_text(source_file, output_basename):
    image = pdb.gimp_file_load(source_file, source_file)

    try:
        gimp.Display(image)
    except:
        pass

    original_layer = image.layers[0]
    pdb.gimp_layer_add_alpha(original_layer)
    healed_layer = pdb.gimp_layer_copy(original_layer, TRUE)
    mask_layer = pdb.gimp_layer_copy(original_layer, TRUE)

    original_layer.name = os.path.basename(source_file)
    mask_layer.name = 'mask'
    healed_layer.name = 'healed'

    original_layer.visible = False
    image.add_layer(mask_layer, 1)
    image.add_layer(healed_layer, 2)

    pdb.gimp_context_set_antialias(TRUE)
    pdb.gimp_context_set_feather(FALSE)
    pdb.gimp_context_set_sample_merged(FALSE)
    pdb.gimp_context_set_sample_criterion(SELECT_CRITERION_COMPOSITE)
    pdb.gimp_context_set_sample_threshold(15.0 / 255.0)
    pdb.gimp_context_set_sample_transparent(TRUE)
    pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, original_layer, (255, 255, 255))

    pdb.gimp_selection_grow(image, 1)

    pdb.gimp_edit_clear(mask_layer)
    # pdb.python_fu_heal_selection(image, healed_layer, 50, "All around", "Outwards from center")
    pdb.python_fu_heal_selection(image, healed_layer, 50, 0, 2)

    save_xcf(image, '%s.xcf' % output_basename)
    image.flatten()
    save_jpg(image, '%s.jpg' % output_basename)

register(
    "miasmata_heal_text",
    "Remove black text from an arbitrary image by healing selection",
    "Remove black text from an arbitrary image by healing selection",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Heal Text",
    None,
    [
        (PF_FILE, "source_file", "Input Image", None),
        (PF_STRING, "output_basename", "Output basename", None),
    ],
    [],
    heal_text,
)

main()
