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

# -- UNTESTED FONTS --
worstveld = Font('Worstveld Sling', 40.0)
# Some of the tops of the letters are slightly cut off - not very noticeable,
# will have to check if that's in the font or if it's a bug in The GIMP:
newspaper_big_heading = Font('New Yorker', 106.0, True)
newspaper_headline = Font('New Yorker', 52.0, True, -1.0)
# Not sure about this one:
# newspaper_body = Font('FG Norah', 29.0)
newspaper_body = Font('Eutheric', 25.0, letter_spacing=-1.0)

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

# -- UNTESTED FROM HERE --
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

def compose_note_bb(image, note_name):
    font = worstveld
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 205, 70, 915)

    layer = add_text_layer_from_file(image, '%s_pink_spotted_lily.txt' % note_name, font)
    place_text(layer, 880, 907, xalign=RIGHT, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_white_spiked_prairie.txt' % note_name, font)
    place_text(layer, 1250, 100, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_white_mushroom.txt' % note_name, font)
    place_text(layer, 1560, 360, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_white_pink_viola.txt' % note_name, font)
    place_text(layer, 1595, 505, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_pawn_mushroom.txt' % note_name, font)
    place_text(layer, 1250, 870, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_wood_gill_fungus.txt' % note_name, font)
    place_text(layer, 1625, 955, xalign=RIGHT, yalign=CENTER)

def compose_note_cc(image, note_name):
    font = arch_daughter
    font_t = arch_daughter_t
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 215, 435, 970)

    x = 600
    layer = add_text_layer_from_file(image, 'synthesis_of.txt', font)
    place_text(layer, x, 215, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, font_t)
    underline_layer(layer)
    place_text(layer, x, 315, xalign=CENTER, yalign=CENTER)

    layer = add_text_layer_from_file(image, 'primary_materials.txt', font)
    place_text(layer, 1350, 70, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_jungle_flower.txt' % note_name, font)
    place_text(layer, 1455, 520, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_purple_fruit.txt' % note_name, font)
    place_text(layer, 1480, 920, xalign=CENTER, yalign=CENTER)

def compose_note_dd(image, note_name):
    font = arch_daughter
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 215, 390, 970)

    x = 600
    layer = add_text_layer_from_file(image, 'synthesis_of.txt', font)
    place_text(layer, x, 172, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, font_t)
    underline_layer(layer)
    place_text(layer, x, 265, xalign=CENTER, yalign=CENTER)

    x = 1290
    layer = add_text_layer_from_file(image, 'primary_materials.txt', font)
    place_text(layer, x, 70, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_rh_primary.txt' % note_name, font)
    place_text(layer, x, 560)
    layer = add_text_layer_from_file(image, 'secondary_materials.txt', font)
    underline_layer(layer)
    place_text(layer, x, 735)
    layer = add_text_layer_from_file(image, '%s_rh_secondary.txt' % note_name, font)
    place_text(layer, x, 780)

def compose_note_ee(image, note_name):
    font = arch_daughter
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 215, 97, 970)

    layer = add_text_layer_from_file(image, '%s_carnivorous_trap.txt' % note_name, font)
    place_text(layer, 1455, 115, xalign=RIGHT, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_fleshy_root.txt' % note_name, font)
    place_text(layer, 1310, 530, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_red_green_fungus.txt' % note_name, font)
    place_text(layer, 1520, 850, xalign=RIGHT, yalign=CENTER)

def compose_note_ff(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1105, 90, 1865)

    layer = add_text_layer_from_file(image, '%s_fabacea.txt' % note_name, font)
    place_text(layer, 480, 115, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_poisonous_mushroom.txt' % note_name, font)
    place_text(layer, 660, 940, xalign=CENTER, yalign=CENTER)

def compose_note_gg(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1105, 90, 1865)

    layer = add_text_layer_from_file(image, '%s_sunflower.txt' % note_name, font)
    place_text(layer, 1430, 715, xalign=RIGHT, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_orange_prairie.txt' % note_name, font)
    place_text(layer, 545, 320, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_red_yellow_hibiscus.txt' % note_name, font)
    place_text(layer, 640, 885, xalign=RIGHT, yalign=CENTER)

def compose_note_hh(image, note_name):
    font = flute
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 210, 85, 950)

    layer = add_text_layer_from_file(image, '%s_indigo_asteraceae.txt' % note_name, font)
    place_text(layer, 730, 880, xalign=RIGHT, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_tropical_buttercup.txt' % note_name, font)
    place_text(layer, 1395, 95, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_purple_prairie.txt' % note_name, font)
    place_text(layer, 1555, 520, xalign=RIGHT, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_violet_cactus.txt' % note_name, font)
    place_text(layer, 1430, 920, yalign=CENTER)

def compose_note_ii(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 230, 535, 940)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1140, 595, 1825)

def compose_note_jj(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 230, 545, 915)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1150, 540, 1830)

def compose_note_kk(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1155, 555, 1840)

    x1, x2 = 226, 585
    header = add_text_layer_from_file(image, '%s_clip1_heading.txt' % note_name, newspaper_headline)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    place_text(header, x1, 388, x2)
    layer = add_text_layer_from_file(image, '%s_clip1.txt' % note_name, newspaper_body)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_FILL)
    place_text(layer, x1, header.offsets[1]+header.height, x2)

    x1, x2 = 607, 935
    header = add_text_layer_from_file(image, '%s_clip2_heading.txt' % note_name, newspaper_headline)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    place_text(header, x1, 56, x2)
    layer = add_text_layer_from_file(image, '%s_clip2.txt' % note_name, newspaper_body)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_FILL)
    place_text(layer, x1, header.offsets[1]+header.height, x2)

def compose_note_ll(image, note_name):
    font = neu_phollick_alpha
    txt = read_text('%s.txt' % note_name)

    x1, x2 = 208, 965
    y1, y2 = 45, 1000
    layer = add_text(image, txt, font)
    place_text(layer, x1, y1)
    txt = bold_word_wrap(layer, txt, x2-x1, y2-y1)

    layer = add_text(image, txt, font)
    place_text(layer, 1107, y1, 1840)

    layer = add_text_layer_from_file(image, '%s_step1.txt' % note_name, font)
    place_text(layer, 1467, 530, xalign=RIGHT, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_step2.txt' % note_name, font)
    place_text(layer, 1530, 430, xalign=CENTER, yalign=BOTTOM)
    layer = add_text_layer_from_file(image, '%s_step3.txt' % note_name, font)
    place_text(layer, 2705, 495, xalign=CENTER, yalign=CENTER)

def compose_note_mm(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 256, 600, 935)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1158, 573, 1815)

def compose_note_nn(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1470, 510, xalign=CENTER, yalign=CENTER)

def compose_note_oo(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 208, 45, 900)

    layer = add_text_layer_from_file(image, '%s_step1.txt' % note_name, font)
    place_text(layer, 1300, 285, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_step2.txt' % note_name, font)
    place_text(layer, 1550, 155, xalign=CENTER, yalign=CENTER)

def compose_note_pp(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1155, 570, 1815)

    x1, x2 = 273, 710
    header = add_text_layer_from_file(image, '%s_clip_heading.txt' % note_name, newspaper_headline)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    place_text(header, x1, 370, x2)
    layer = add_text_layer_from_file(image, '%s_clip.txt' % note_name, newspaper_body)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_FILL)
    place_text(layer, x1, 690, x2)

def compose_note_qq(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1155, 570, 1815)

    x1, x2 = 226, 972
    layer = add_text_layer_from_file(image, '%s_clip_heading.txt' % note_name, newspaper_big_heading)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, x1+x2/2, 75, xalign=CENTER)
    pdb.gimp_layer_resize(layer, x2-x1, layer.height, x1-layer.offsets[0])

    x1, x2 = 271, 928
    header = add_text_layer_from_file(image, '%s_clip_heading.txt' % note_name, newspaper_headline)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    place_text(header, x1, 250, x2)
    layer = add_text_layer_from_file(image, '%s_clip.txt' % note_name, newspaper_body)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_FILL)
    place_text(layer, x1, 875, x2)

def compose_note_rr(image, note_name):
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s_boat.txt' % note_name, font)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    place_text(layer, 465, 245, xalign=CENTER, yalign=CENTER)

    layer = add_text_layer_from_file(image, '%s_causeway.txt' % note_name, font)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1280, 375, xalign=CENTER, yalign=CENTER)

def compose_note_ss(image, note_name):
    font = worstveld
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1115, 70, 1830)

def compose_note_tt(image, note_name):
    font = neu_phollick_alpha_c
    font2 = neu_phollick_alpha_s

    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, neu_phollick_alpha_lc)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    word_wrap(layer, None, 950 - 225)
    place_text(layer, 575, 140, xalign=CENTER, yalign=BOTTOM)

    x1, x2 = 230, 930
    layer = add_text_layer_from_file(image, '%s_step1.txt' % note_name, font)
    place_text(layer, x1, 170, x2)
    layer = add_text_layer_from_file(image, '%s_step2.txt' % note_name, font)
    place_text(layer, x1, 505, x2)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1108, 670, 1835)

    layer = add_text_layer_from_file(image, '%s_you_are_here.txt' % note_name, font2)
    place_text(layer, 1605, 535, yalign=CENTER)

    txt = read_text('%s_statue.txt')
    layer = add_text(image, txt, font2)
    place_text(layer, 297, 672, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, txt, font2)
    place_text(layer, 1185, 60, xalign=CENTER, yalign=CENTER)

    txt = read_text('%s_tent.txt')
    layer = add_text(image, txt, font2)
    place_text(layer, 655, 670, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, txt, font2)
    place_text(layer, 1545, 60, xalign=CENTER, yalign=CENTER)

    txt = read_text('%s_cabin.txt')
    layer = add_text(image, txt, font2)
    place_text(layer, 877, 760, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, txt, font2)
    place_text(layer, 1760, 90, xalign=CENTER, yalign=CENTER)

def compose_note_uu(image, note_name):
    font = arch_daughter
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 215, 435, 970)

    x = 600
    layer = add_text_layer_from_file(image, 'synthesis_of.txt', font)
    place_text(layer, x, 220, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, font_t)
    underline_layer(layer)
    place_text(layer, x, 313, xalign=CENTER, yalign=CENTER)

    layer = add_text_layer_from_file(image, 'primary_materials.txt', font)
    place_text(layer, 1336, 73, xalign=CENTER, yalign=CENTER)
    x = 1217
    layer = add_text_layer_from_file(image, '%s_sponge_mushroom.txt' % note_name, font)
    place_text(layer, x, 495)
    layer = add_text_layer_from_file(image, '%s_trumpet_mushroom.txt' % note_name, font)
    place_text(layer, x, 900)

def compose_note_vv(image, note_name):
    font = flute_ex_s

    layer = add_text_layer_from_file(image, '%s.txt', font)
    place_text(layer, 240, 40, 980)

    layer = add_text_layer_from_file(image, '%s_rh.txt', font)
    place_text(layer, 1125, 640, 1835)

def compose_note_ww(image, note_name):
    font = flute_ex_s
    txt = read_text('%s.txt' % note_name)

    x1, x2 = 240, 980
    y1, y2 = 35, 1000
    layer = add_text(image, txt, font)
    place_text(layer, x1, y1)
    txt = bold_word_wrap(layer, txt, x2-x1, y2-y1)

    layer = add_text(image, txt, font)
    place_text(layer, 1110, 55, 1850)

def compose_note_xx(image, note_name):
    font = flute_ex_s

    y = 45
    layer = add_text_layer_from_file(image, '%s.txt', font)
    place_text(layer, 240, y, 980)

    layer = add_text_layer_from_file(image, '%s_rh.txt', font)
    place_text(layer, 1125, y, 1845)

def compose_note_yy(image, note_name):
    font = flute_ex_s
    txt = read_text('%s.txt' % note_name)

    x1, x2 = 240, 970
    y1, y2 = 35, 1000
    layer = add_text(image, txt, font)
    place_text(layer, x1, y1)
    txt = bold_word_wrap(layer, txt, x2-x1, y2-y1)

    layer = add_text(image, txt, font)
    place_text(layer, 1120, y1, 1850)

def compose_note_zz(image, note_name):
    font = flute_ex_s

    layer = add_text_layer_from_file(image, '%s.txt', font)
    place_text(layer, 240, 70, 970)

    layer = add_text_layer_from_file(image, '%s_rh.txt', font)
    place_text(layer, 1100, 585, 1845)

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
