#!/usr/bin/env python

from gimpfu import *

from miasmata_gimp import *

intro_font = Font('Norlik', 36.0, False, 15.0)
end_font = Font('Norlik Condensed', 36.0, False, 20.0) #, letter_spacing = -1.0)

width = height = 1024

def enlarge_first_letter(text, txt):
    # XXX: Requires a patched GIMP to set text markup
    # See https://bugzilla.gnome.org/show_bug.cgi?id=724101
    markup = '<span size="%i">%s</span>%s' % (1024 * 50.0, txt[0], txt[1:])
    pdb.gimp_text_layer_set_markup(text, markup)
    return markup

def scale_layer(image, layer, x = 1.0, y = 1.0):
    try:
        pdb.gimp_context_set_interpolation(INTERPOLATION_LANCZOS)
    except:
        pdb.gimp_context_set_interpolation(INTERPOLATION_NOHALO)
    layer.scale(int(layer.width * x), int(layer.height * y))

def add_background(image, opacity=100.0):
    background = gimp.Layer(image, 'Background', width, height, RGB_IMAGE, opacity, NORMAL_MODE)
    image.add_layer(background, -1)

    gimp.set_background(0, 0, 0)
    background.fill(BACKGROUND_FILL)

    return background

def display_image(image):
    try:
        gimp.Display(image)
    except:
        pass

def render_end_slide(source_txt_file, output_basename, first=False):
    txt = read_text(source_txt_file)

    image = gimp.Image(width, height, RGB)
    background = add_background(image)
    display_image(image)
    layer = add_text(image, txt, end_font, colour = (255, 255, 255))
    if first:
        txt = enlarge_first_letter(layer, txt)
    word_wrap(layer, txt, width - 250)
    scale_layer(image, layer, 0.9, 1.1)
    center_layer(layer)
    blur_layer(image, layer)

    save(image, output_basename)

def render_intro_slide(source_txt_file, output_basename):
    txt = open(source_txt_file, 'rb').read().decode('utf-8').strip()

    image = gimp.Image(width, height, RGB)
    background = add_background(image, 0.0)
    display_image(image)
    text = add_text(image, txt, intro_font, colour = (255, 255, 255))
    pdb.gimp_text_layer_set_justification(text, TEXT_JUSTIFY_CENTER)
    center_layer(text)
    blur_layer(image, text)

    save(image, output_basename, alpha=True)
    background.opacity = 100.0
    image.flatten()
    save_jpg(image, '%s.jpg' % output_basename)

register(
    "miasmata_end_slide",
    "Generate an image for Miasmata's end sequence",
    "Generate an image for Miasmata's end sequence",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_End",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the text to place on the slide", None),
        (PF_STRING, "output_basename", "Base output filename", None),
        (PF_BOOL, "first", "First slide - causes first letter to be enlarged slightly", None),
    ],
    [],
    render_end_slide,
)

register(
    "miasmata_intro_slide",
    "Generate an image for Miasmata's intro sequence",
    "Generate an image for Miasmata's intro sequence",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Intro",
    None,
    [
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the text to place on the slide", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    render_intro_slide,
)

main()
