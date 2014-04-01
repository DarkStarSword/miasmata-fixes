#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

header_font = Font('Neu Phollick Alpha', 45.0, True)
font = Font('Neu Phollick Alpha', 40.0, True, -5.0)
font_small = Font('Neu Phollick Alpha', 32.0, True, -5.0)
research_font = Font('Neu Phollick Alpha Bold', 40.0, False)

def desc_font(plant):
    return {
            'Plant_E': font_small,
            'Plant_J': font_small,
    }.get(plant, font)

w = h = 1024

rh_x = 0
lh_x = 148
rh_w = lh_w = w - lh_x

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

research_coords = {
    'RESEARCH_0': (rh_x + rh_w/2, 380, None, CENTER),
    'Research_K': (90, 730, 825, LEFT),
}


def add_header(image, header_txt, rh=False):
    layer = add_text(image, header_txt, header_font)
    if rh:
        place_text(layer, rh_x + rh_w / 2, header_h / 2, xalign=CENTER, yalign=CENTER)
    else:
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

def compose_research_image(template_txt_file, source_txt_file, source_conclusion_txt_file, source_blank_image, output_basename):
    import struct

    template = read_text(template_txt_file)
    (header_txt, conclusion_templ_txt) = template.split('\n')

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    try:
        mask = get_layer_by_name(image, 'mask')
        mask.visible = False
        channel = ALPHA_CHANNEL
        test = 1
    except KeyError:
        mask = None
        channel = VALUE_MODE
        test = -1

    image.merge_visible_layers(CLIP_TO_IMAGE)
    layer = image.active_layer
    if mask is None:
        mask = layer

    # Find lines around conclusion text
    x = 250
    y = image.height - 1
    tile = layer.get_tile2(False, x, y)
    lines = []
    at_line = False
    threshold = 64
    while True:
        # XXX: Assumes 32bpp image, ignores alpha
        (r, g, b, a) = struct.unpack("4B", tile[x % tile.ewidth, y % tile.eheight])
        v = (r + g + b) / 3

        if at_line and v > threshold:
            at_line = False
        elif not at_line and v <= threshold:
            print "Found line at %i" % y
            at_line = True
            lines.append(y)
            if len(lines) == 2:
                break
        y -= 1
        if y < 0:
            raise Exception()
        if y % tile.eheight == tile.eheight - 1:
            tile = layer.get_tile2(False, x, y)

    x1, x2 = 110, 825

    add_header(image, header_txt, True)

    # TODO: Wrap around images, manual placement, or whatever solution I end up doing
    y = 85
    text = add_text_layer_from_file(image, source_txt_file, research_font, colour=(105, 105, 105))
    place_text(text, x1, y, x2)
    line_spacing = pdb.gimp_text_layer_get_line_spacing(text)
    while True:
        group = masked_word_wrap(text, mask, x2-x1, channel=channel, test=test)
        if y + group.height < lines[1]:
            break
        pdb.gimp_image_remove_layer(image, group)
        line_spacing -= 1
        pdb.gimp_text_layer_set_line_spacing(text, line_spacing)

    y = lines[1] + 10
    conclusion = read_text(source_conclusion_txt_file)
    layer = add_text(image, '%s\n\n%s' % (conclusion_templ_txt, conclusion), research_font)
    word_wrap(layer, None, x2-x1)
    place_text(layer, x1, y)
    reduce_text_line_spacing_to_fit(layer, lines[0] - y - 10)

    save(image, output_basename)

def compose_research2_image(template_txt_file, source_txt_file, source_blank_image, output_basename):
    template = read_text(template_txt_file)
    (header_txt, conclusion_templ_txt) = template.split('\n')

    image = pdb.gimp_file_load(source_blank_image, source_blank_image)
    add_header(image, header_txt, True)

    (x1, y, x2, xalign) = research_coords[output_basename]
    layer = add_text_layer_from_file(image, source_txt_file, research_font)
    place_text(layer, x1, y, x2, xalign=xalign)

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

register(
    "miasmata_research",
    "Compose an image for Miasmata's Journal plant research pages",
    "Compose an image for Miasmata's Journal plant research pages",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Research",
    None,
    [
        (PF_FILE, "template_txt_file", "utf-8 encoded file with the translations of 'Laboratory Research' and 'My Conclusion:', one per line", None),
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the method text to place on the image", None),
        (PF_FILE, "source_conclusion_txt_file", "utf-8 encoded file with the conclusion text to place on the image", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_research_image,
)

register(
    "miasmata_research2",
    "Compose an image for Miasmata's Journal plant research pages 0 and K - without conclusion)",
    "Compose an image for Miasmata's Journal plant research pages (0 and K - without conclusion)",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Research2",
    None,
    [
        (PF_FILE, "template_txt_file", "utf-8 encoded file with the translations of 'Laboratory Research' and 'My Conclusion:', one per line", None),
        (PF_FILE, "source_txt_file", "utf-8 encoded file with the text to place on the image", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_research2_image,
)

main()
