#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

neu_phollick_alpha = Font('Neu Phollick Alpha', 40.0, True, 5.0)
fnt_23rd_street = Font('23rd Street', 40.0, False, 15.0)
fnt_23rd_street_b = Font('23rd Street', 40.0, True, 6.0)
fnt_23rd_street_c = Font('23rd Street', 36.0, True, 6.0)
fg_nora = Font('FG Norah', 40.0, False, -8.0)
flute = Font('Flute', 40.0, True, -5.0)
wiki = Font('Wiki', 40.0, True, 5.0)
arch_daughter = Font("Architects Daughter", 38.0, False, -13)

in_world_notes = (
    ('Notes', 2048, (
        ('NOTE_9', 'NOTE_16'),
        ('NOTE_7', 'NOTE_15'),
        ('NOTE_5', 'NOTE_14'),
        ('NOTE_4', 'NOTE_13'),
        ('NOTE_3', 'NOTE_12'),
        ('NOTE_2', 'NOTE_11'), # Note 2 has no map, left page on right
        ('NOTE_1', 'NOTE_10'),
        ('NOTE_0', 'NOTE_9', 'NOTE_17') # Note 0 only has left page, on right
    )), ('InWorldNotesz_Set2', 2048, (
        ('NOTE_AA', 'NOTE_II', 'NOTE_NN', 'NOTE_YY'),
        ('NOTE_BB', 'NOTE_JJ', 'NOTE_RR', 'Note_A1'),
        ('NOTE_CC', 'NOTE_KK', 'NOTE_SS', 'NOTE_ZZ'),
        ('NOTE_DD', 'NOTE_LL', 'NOTE_UU', 'NOTE_A2'),
        ('NOTE_EE', 'NOTE_MM', 'NOTE_TT', 'NOTE_A3'),
        ('NOTE_FF', 'NOTE_OO', 'NOTE_VV', 'NOTE_A4'),
        ('NOTE_GG', 'NOTE_PP', 'NOTE_WW', 'NOTE_A5'),
        ('NOTE_HH', 'NOTE_QQ', 'NOTE_XX', 'NOTE_A6'),
              # ^^ clippings - will need special handling
              # II, JJ, MM don't have text, can just copy from originals
              # KK contains some text cut off from the large image
              # PP, QQ appears to contains earlier edit vs large image!
              # LL, OO are normal
                    # ^^ NN coords differ
    )), ('InWorldNotesz_Set3', 1024, (
        ('NOTE_A7', ),
        ('NOTE_A8', ),
        ('NOTE_A9', ),
    ))
)

translate_left_page_to_right = (
        '0', '2'
)

in_world_note_w = 512
in_world_note_h = 256

def clip_note_borders(layer):
    border_width = 148
    image = layer.image
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE,
            0, 0,
            border_width, image.height)
    pdb.gimp_edit_clear(layer)
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE,
            image.width - border_width, 0,
            border_width, image.height)
    pdb.gimp_edit_clear(layer)
    pdb.gimp_selection_clear(image)

def update_in_world_note(image, note, (x, y)):
    x *= in_world_note_w
    y *= in_world_note_h
    print 'upate_in_world_note %s @ %ix%i' % (note, x, y)
    note_filename = '%s.png' % note
    note_image = pdb.gimp_file_load(note_filename, note_filename)
    layer = pdb.gimp_layer_new_from_visible(note_image, image, note)
    image.add_layer(layer, -1)
    clip_note_borders(layer)
    layer.scale(in_world_note_w, in_world_note_h)
    layer.set_offsets(x, y)

def generate_in_world_notes():
    for (name, dimensions, notes) in in_world_notes:
        image = gimp.Image(dimensions, dimensions, RGB)
        for (y, row) in enumerate(notes):
            for (x, note) in enumerate(row):
                update_in_world_note(image, note, (x, y))

        save_xcf(image, '%s.xcf' % name)
        image2 = pdb.gimp_image_duplicate(image)
        image2.merge_visible_layers(CLIP_TO_IMAGE)
        pdb.gimp_layer_resize_to_image_size(image2.active_layer)
        save_png(image2, '%s.png' % name)

def compose_note_0(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, neu_phollick_alpha)
    pdb.gimp_layer_set_mode(body, MULTIPLY_MODE)
    place_text(body, 235, 55, 980)

    def drug_text(filename):
        txt = read_text(filename).split('\n')
        txt[1] = '<span font_size="%i">%s</span>' % (1024 * 30, txt[1])
        txt = '\n'.join(txt)
        layer = add_text(image, txt, neu_phollick_alpha)
        pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
        return layer

    agentx = drug_text('%s_X.txt' % note_name)
    place_text(agentx, 1478, 172, xalign=CENTER, yalign=CENTER)

    agenty = drug_text('%s_Y.txt' % note_name)
    place_text(agenty, 1278, 395, xalign=CENTER, yalign=CENTER)

    agentz = drug_text('%s_Z.txt' % note_name)
    place_text(agentz, 1718, 395, xalign=CENTER, yalign=CENTER)

    cure = drug_text('%s_cure.txt' % note_name)
    place_text(cure, 1486, 758, xalign=CENTER, yalign=CENTER)

def compose_note_1(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, fnt_23rd_street)
    place_text(body, 1100, 100, 1785)

def compose_note_2(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, fg_nora)
    place_text(body, 210, 45, 970)

    title = add_text_layer_from_file(image, '%s_title.txt' % note_name, fg_nora)
    underline_text(title)
    place_text(title, 1450, 221, xalign=CENTER)

    statue = add_text_layer_from_file(image, '%s_statue.txt' % note_name, fg_nora)
    place_text(statue, 1645, 822, yalign=CENTER)

def compose_note_3(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, fnt_23rd_street_b)
    place_text(body, 205, 55, 970)

    title = add_text_layer_from_file(image, '%s_title.txt' % note_name, fnt_23rd_street_c)
    place_text(title, 1465, 65, xalign=CENTER)

    algae = add_text_layer_from_file(image, '%s_algae.txt' % note_name, fnt_23rd_street_c)
    place_text(algae, 1556, 898, xalign=RIGHT, yalign=CENTER)

    ruin = add_text_layer_from_file(image, '%s_ruin_site_b.txt' % note_name, fnt_23rd_street_c)
    place_text(ruin, 1630, 940, yalign=CENTER)

def compose_note_4(image, note_name):
    body = add_text_layer_from_file(image, '%s.txt' % note_name, flute)
    place_text(body, 1087, 75, 1880)

def compose_note_5(image, note_name):
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, wiki)
    place_text(layer, 200, 77, 930)

    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, wiki)
    place_text(layer, 1325, 454, xalign=CENTER, yalign=CENTER)

# There is no note 6...

def compose_note_7(image, note_name):
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, neu_phollick_alpha)
    place_text(layer, 1130, 90, 1830)

def compose_note_8(image, note_name):
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, flute)
    place_text(layer, 1457, 250, xalign=CENTER, yalign=CENTER)

def compose_note_9(image, note_name):
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, arch_daughter)
    place_text(layer, 1145, 145, 1830)

def compose_note_image(note_name, source_blank_image, output_basename):
    image = pdb.gimp_file_load(source_blank_image, source_blank_image)

    # getattr(globals(), 'compose_%s' % note_name.lower())(image, note_name)
    globals()['compose_%s' % note_name.lower()](image, note_name)

    save_xcf(image, '%s.xcf' % output_basename)
    image2 = pdb.gimp_image_duplicate(image)
    image2.flatten()
    save_dds(image2, '%s.dds' % output_basename, False)
    save_jpg(image2, '%s.jpg' % output_basename)

register(
    "miasmata_note",
    "Compose an image for a note in Miasmata",
    "Compose an image for a note in Miasmata",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/_Note",
    None,
    [
        (PF_FILE, "note_name", "Which note to compose. Each note has it's own requirements for where it looks for the input text.", None),
        (PF_FILE, "source_blank_image", "Background image to use that should have previously had the text removed", None),
        (PF_STRING, "output_basename", "Base output filename", None),
    ],
    [],
    compose_note_image,
)

register(
    "miasmata_notes_in_world",
    "Generate textures used for the in-world notes",
    "Generate textures used for the in-world notes",
    "Ian Munsie",
    "Ian Munsie",
    "2014",
    "<Toolbox>/_Miasmata/In _world notes",
    None,
    [
    ],
    [],
    generate_in_world_notes,
)

main()
