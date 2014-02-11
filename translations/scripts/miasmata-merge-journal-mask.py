#!/usr/bin/env python

from gimpfu import *

def merge_journal_mask(source_file, mask_file, output_file):
    image = pdb.gimp_file_load(source_file, source_file)

    try:
        gimp.Display(image)
    except:
        pass

    layer = pdb.gimp_file_load_layer(image, mask_file)

    image.add_layer(layer, 0)

    pdb.gimp_xcf_save(0, image, image.active_layer, output_file, output_file)
    image.clean_all()

register(
    "miasmata_merge_journal_mask",
    "Add the mask as a new layer on the journal image",
    "Add the mask as a new layer on the journal image",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Mask Journal Page",
    None,
    [
        (PF_FILE, "source_file", "Journal Page", None),
        (PF_FILE, "mask_file", "Journal Mask", "research_left_mask.png"),
        (PF_STRING, "output_file", "Output File", None),
    ],
    [],
    merge_journal_mask,
)

main()
