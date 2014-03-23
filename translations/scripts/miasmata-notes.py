#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *
from copy import copy

neu_phollick_alpha = Font('Neu Phollick Alpha', 40.0, True, 5.0)
neu_phollick_alpha_c = Font('Neu Phollick Alpha', 40.0, True, 0.0)
neu_phollick_alpha_l = Font('Neu Phollick Alpha', 45.0, True)
neu_phollick_alpha_lc = Font('Neu Phollick Alpha', 45.0, True, -7.0)
neu_phollick_alpha_t = Font('Neu Phollick Alpha', 55.0, True)
neu_phollick_alpha_s = Font('Neu Phollick Alpha', 30.0, True)
fnt_23rd_street = Font('23rd Street', 40.0, False, 15.0)
fnt_23rd_street_b = Font('23rd Street', 40.0, True, 6.0)
fnt_23rd_street_b_sm = Font('23rd Street', 37.0, True, 6.0, letter_spacing = -1.0)
fnt_23rd_street_c = Font('23rd Street', 36.0, True, 6.0)
fg_norah = Font('FG Norah', 40.0, False, -8.0)
fg_norah_b = Font('FG Norah', 40.0, True, -10.0)
flute = Font('Flute', 40.0, True, -5.0)
flute_s = Font('Flute', 35.0, True, -5.0)
flute_ex_s = Font('Flute Expanded', 30.0, True, -5.0)
flute_l = Font('Flute', 43.0, True, -5.0)
wiki = Font('Wiki', 40.0, True, 5.0)

# I found two variants of this font with different shapes, I believe this is
# the one used in game: http://www.fontsquirrel.com/fonts/architects-daughter
arch_daughter = Font("Architects Daughter", 35.0, True, -13)
arch_daughter_t = Font("Architects Daughter", 45.0, True, -13)

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
    body = add_text_layer_from_file(image, '%s.txt' % note_name, fg_norah)
    place_text(body, 210, 45, 970)

    title = add_text_layer_from_file(image, '%s_title.txt' % note_name, fg_norah)
    underline_text(title)
    place_text(title, 1450, 221, xalign=CENTER)

    statue = add_text_layer_from_file(image, 'statue.txt', fg_norah)
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

def compose_note_10(image, note_name):
    font = arch_daughter

    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, arch_daughter_t)
    underline_text(layer)
    place_text(layer, 600, 307, xalign=CENTER, yalign=CENTER)

    x = 220
    (title, body) = read_text('%s.txt' % note_name).split('\n', 1)
    layer = add_text(image, title, font)
    underline_text(layer)
    place_text(layer, x, 525)
    layer = add_text(image, body, font)
    place_text(layer, x, 625, 980)

    x = 1090
    (title, ingredients) = read_text('%s_rh.txt' % note_name).split('\n', 1)
    layer = add_text(image, title, font)
    underline_text(layer)
    place_text(layer, x, 91)
    layer = add_text(image, ingredients, font, colour=(189, 16, 33))
    place_text(layer, x, 190)

def compose_note_11(image, note_name):
    font = flute_l
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1563, 710)

def compose_note_12(image, note_name):
    font = arch_daughter
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 220, 100, 960)

def compose_note_13(image, note_name):
    font = neu_phollick_alpha_c
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 210, 60, 970)

def compose_note_14(image, note_name):
    font = neu_phollick_alpha_l
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1258, 791, xalign=CENTER)

def compose_note_15(image, note_name):
    font = neu_phollick_alpha_l

    x = 210
    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, neu_phollick_alpha_t)
    underline_text(layer)
    place_text(layer, x, 337)

    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, x, 500, 944)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1092, 52)

def compose_note_16(image, note_name):
    font = neu_phollick_alpha_l
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1135, 39, 1855)

    layer = add_text_layer_from_file(image, '%s_ozwaldt.txt' % note_name, font)
    place_text(layer, 1855, 830, xalign=RIGHT)

def compose_note_17(image, note_name):
    font = fg_norah_b
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1126, 44, 1860)

def compose_note_a1(image, note_name):
    # --- UNTESTED ---
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 572, 127, xalign=CENTER, yalign=CENTER)

    layer = add_text_layer_from_file(image, 'statue.txt', font)
    place_text(layer, 648, 340, yalign=CENTER)

    layer = add_text_layer_from_file(image, '%s_lab.txt' % note_name, font)
    place_text(layer, 713, 869, yalign=CENTER)

def compose_note_a2(image, note_name):
    font = arch_daughter
    txt1, txt2 = read_text('%s.txt' % note_name).split('\n', 1)

    layer = add_text(image, txt1, font)
    place_text(layer, 550, 517, xalign=CENTER, yalign=CENTER)

    layer = add_text(image, txt2, font)
    place_text(layer, 1584, 176, xalign=CENTER, yalign=CENTER)

def compose_note_a3(image, note_name):
    font = arch_daughter
    txt1, txt2 = read_text('%s.txt' % note_name).split('\n', 1)

    layer = add_text(image, txt1, font)
    place_text(layer, 205, 460, yalign=CENTER)

    layer = add_text(image, txt2, font)
    place_text(layer, 1526, 880, xalign=CENTER, yalign=CENTER)

def compose_note_a4(image, note_name):
    font = arch_daughter
    txt1, txt2 = read_text('%s.txt' % note_name).split('\n', 1)

    layer = add_text(image, txt1, font)
    place_text(layer, 205, 320, yalign=CENTER)

    layer = add_text(image, txt2, font)
    place_text(layer, 1590, 741, xalign=CENTER, yalign=CENTER)

def compose_note_a5(image, note_name):
    font = neu_phollick_alpha_c
    font2 = neu_phollick_alpha_s
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 195, 175, 973)

    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, neu_phollick_alpha_lc)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    word_wrap(layer, None, 920 - 260)
    place_text(layer, 575, 140, xalign=CENTER, yalign=BOTTOM)

    layer = add_text_layer_from_file(image, '%s_landmark.txt' % note_name, font2)
    place_text(layer, 1592, 213, yalign=CENTER)

    layer = add_text_layer_from_file(image, '%s_vantage_1.txt' % note_name, font2)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1137, 697, xalign=CENTER)

    layer = add_text_layer_from_file(image, '%s_vantage_2.txt' % note_name, font2)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1785, 697, xalign=CENTER)

def compose_note_a6(image, note_name):
    font = wiki
    txt1, txt2 = read_text('%s.txt' % note_name).split('\n', 1)

    layer = add_text(image, txt1, font)
    place_text(layer, 408, 468, yalign=CENTER)

    layer = add_text(image, txt2, font)
    place_text(layer, 588, 614, xalign=CENTER)

def compose_note_a7(image, note_name):
    font = fnt_23rd_street_b_sm
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 210, 50, 990)
    pdb.gimp_item_transform_shear(layer, ORIENTATION_VERTICAL, -30.0)

def compose_note_a8(image, note_name):
    font = fnt_23rd_street_b_sm
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1124, 110, 1837)
    pdb.gimp_item_transform_shear(layer, ORIENTATION_VERTICAL, -30.0)

def compose_note_a9(image, note_name):
    font = flute_ex_s
    txt = read_text('%s.txt' % note_name)

    x1, x2 = 230, 970
    y1, y2 = 55, 1000
    layer = add_text(image, txt, font)
    place_text(layer, x1, y1)
    txt = bold_word_wrap(layer, txt, x2-x1, y2-y1)

    layer = add_text(image, txt, font)
    place_text(layer, 1115, y1, 1850)

def compose_note_aa(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s_basic_medicine.txt' % note_name, font)
    place_text(layer, 538, 39, 940)

    layer = add_text_layer_from_file(image, '%s_endurance_emphasis.txt' % note_name, font)
    place_text(layer, 208, 270, 720)

    layer = add_text_layer_from_file(image, '%s_muscle_emphasis.txt' % note_name, font)
    place_text(layer, 460, 517, 940)

    layer = add_text_layer_from_file(image, '%s_brain_emphasis.txt' % note_name, font)
    place_text(layer, 215, 820, 805)

    layer = add_text_layer_from_file(image, '%s_energy_stim.txt' % note_name, font)
    place_text(layer, 1113, 41, 1510)

    layer = add_text_layer_from_file(image, '%s_clarity_tonic.txt' % note_name, font)
    place_text(layer, 1267, 268, 1876)

    layer = add_text_layer_from_file(image, '%s_herculean_tonic.txt' % note_name, font)
    place_text(layer, 1200, 520, 1645)

    layer = add_text_layer_from_file(image, '%s_mental_stim.txt' % note_name, font)
    place_text(layer, 1376, 780, 1880)

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

main()
