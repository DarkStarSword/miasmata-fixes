#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

def convert_image(source_image, output_basename):
    image = pdb.gimp_file_load(source_image, source_image)
    image.merge_visible_layers(CLIP_TO_IMAGE)
    save_dds(image, '%s.dds' % output_basename, False)
    save_jpg(image, '%s.jpg' % output_basename)

register(
    "miasmata_to_dds_jpg",
    "Convert an already translated image to dds+jpg",
    "Convert an already translated image to dds+jpg",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Convert Image to DDS + JPG",
    None,
    [
        (PF_FILE, "source_image", "Input blackboard image", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    convert_image,
)

main()
