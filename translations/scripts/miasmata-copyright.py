#!/usr/bin/env python

from gimpfu import *

from miasmata_gimp import *

font = Font('Candara', 12.0, line_spacing=2.0)

width = 512
height = 64

def add_background(image, opacity=100.0):
    background = gimp.Layer(image, 'Background', width, height, RGB_IMAGE, opacity, NORMAL_MODE)
    image.add_layer(background, -1)

    gimp.set_background(0, 0, 0)
    background.fill(BACKGROUND_FILL)

    return background

def render_intro_slide(source_txt_file, output_basename):
    txt = read_text(source_txt_file)

    image = gimp.Image(width, height, RGB)
    background = add_background(image, 0.0)
    layer = add_text(image, txt, font, colour = (255, 255, 255))
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    center_layer(layer)

    save(image, output_basename, alpha=True)
    background.opacity = 100.0
    image.flatten()
    save_jpg(image, '%s.jpg' % output_basename)

register(
    "miasmata_copyright",
    "Generate Miasmata copyright notice",
    "Generate Miasmata copyright notice",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Copyright",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the text to place on the notice", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    render_intro_slide,
)

main()
