#!/usr/bin/env python

from gimpfu import *

from miasmata_gimp import *

# font = Font('Blound', 12.0)
# font = Font('MathJax_SansSerif', 12.0) # ok
# font = Font('Sakkal Majalla', 15.0) # Nah
# font = Font('Pill Gothic 600mg Light', 12.0) # Not right, but reasonable
# font = Font('MoolBoran', 16.0) # Ok w/o hinting
# font = Font('Gill Sans MT', 14.0) # ok
# font = Font('FreesiaUPC', 20.0) # ok
# font = Font('Franklin Gothic Book', 12.0) # Nah
# font = Font('Calibri', 12.0) # kinda ok with full hinting
# font = Font('Britannic', 12.0) # Reasonable

font = Font('EstragonFree', 14.0) # Unless the actual font is identified, I think this is close enough

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
    pdb.gimp_text_layer_set_hint_style(layer, TEXT_HINT_STYLE_FULL)
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
