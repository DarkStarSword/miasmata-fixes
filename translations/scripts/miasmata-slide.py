#!/usr/bin/env python

from gimpfu import *

from miasmata_gimp import *

intro_font = 'Norlik'
end_font = 'Norlik Condensed'
font_size = 36.0
intro_line_spacing = 15.0
end_line_spacing = 20.0

width = height = 1024

def enlarge_first_letter(text, txt):
    # XXX: Requires a patched GIMP to set text markup
    # See https://bugzilla.gnome.org/show_bug.cgi?id=724101
    markup = '<span size=\"55000\">%s</span>%s' % (txt[0], txt[1:])
    pdb.gimp_text_layer_set_markup(text, markup)

def scale_text(image, text):
    try:
        pdb.gimp_context_set_interpolation(INTERPOLATION_LANCZOS)
    except:
        pdb.gimp_context_set_interpolation(INTERPOLATION_NOHALO)
    text.scale(width - 2*170, text.height)
    text.translate(170, (image.height - text.height) / 2)

def center_layer(image, layer):
    layer.translate((image.width - layer.width) / 2, (image.height - layer.height) / 2)

def blur_layer(image, layer):
    pdb.plug_in_gauss_rle2(image, layer, 1.0, 1.0)

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

def render_end_slide(source_txt_file, output_basename):
    txt = open(source_txt_file, 'rb').read().decode('utf-8').strip()

    image = gimp.Image(width, height, RGB)
    background = add_background(image)
    display_image(image)
    text = add_text_layer(image, txt, end_font, font_size,
            line_spacing = end_line_spacing, colour = (255, 255, 255))
    enlarge_first_letter(text, txt)

    scale_text(image, text)
    blur_layer(image, text)

    # center_layer(image, text)

    # image.active_layer = background
    save_xcf(image, '%s.xcf' % output_basename)

    image2 = pdb.gimp_image_duplicate(image)
    image2.flatten()

    save_dds(image2, '%s.dds' % output_basename, False)
    save_png(image2, '%s.png' % output_basename)

def render_intro_slide(source_txt_file, output_basename):
    txt = open(source_txt_file, 'rb').read().decode('utf-8').strip()

    image = gimp.Image(width, height, RGB)
    background = add_background(image, 0.0)
    display_image(image)
    text = add_text_layer(image, txt, intro_font, font_size,
            line_spacing = intro_line_spacing, colour = (255, 255, 255))
    pdb.gimp_text_layer_set_justification(text, TEXT_JUSTIFY_CENTER)
    center_layer(image, text)
    blur_layer(image, text)

    save_xcf(image, '%s.xcf' % output_basename)

    image2 = pdb.gimp_image_duplicate(image)
    image2.merge_visible_layers(CLIP_TO_IMAGE)
    save_dds(image2, '%s.dds' % output_basename, True)
    save_png(image2, '%s.png' % output_basename)

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
