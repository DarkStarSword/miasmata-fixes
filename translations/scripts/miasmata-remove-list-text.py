#!/usr/bin/env python

from gimpfu import *

def remove_journal_list_text(source_file, placeholder_file, output_file):
    image = pdb.gimp_file_load(placeholder_file, placeholder_file)

    try:
        gimp.Display(image)
    except:
        pass

    layer = pdb.gimp_file_load_layer(image, source_file)

    image.add_layer(layer, 0)

    x = 205
    y = 20
    w = 1024 - x
    h = 235 - y
    pdb.gimp_rect_select(image, x, y, w, h, CHANNEL_OP_REPLACE, FALSE, 0)

    # pdb.gimp_context_set_antialias(TRUE)
    # pdb.gimp_context_set_feather(FALSE)
    # # pdb.gimp_context_set_feather_radius
    # pdb.gimp_context_set_sample_criterion(SELECT_CRITERION_COMPOSITE)
    # pdb.gimp_context_set_sample_threshold(0.50)

    # pdb.gimp_image_select_color(image, CHANNEL_OP_INTERSECT, layer, (0, 0, 0))

    pdb.gimp_edit_clear(layer)

    image2 = pdb.gimp_image_duplicate(image)
    image2.flatten()

    # pdb.gimp_layer_add_alpha(image2.active_layer)

    pdb.file_png_save2(image2, image2.active_layer, output_file, output_file,
            0, # interlace
            9, # compression
            0, # save background colour
            0, # save gamma
            0, # save layer offset
            1, # save pHYs (resolution?)
            1, # save creation time
            1, # save comment
            1, # preserve colour of transparent pixels
    )

register(
    "miasmata_remove_list_text",
    "Remove the text from a Miasmata Journal index/list image",
    "Remove the text from a Miasmata Journal index/list image",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Remove list Text",
    None,
    [
        (PF_FILE, "source_file", "Journal Index Image", None),
        (PF_FILE, "placeholder_file", "List Placeholder", "LIST_Placeholder1.png"),
        (PF_STRING, "output_file", "Output File", None),
    ],
    [],
    remove_journal_list_text,
)

main()
