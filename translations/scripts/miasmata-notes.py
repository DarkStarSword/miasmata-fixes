#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *
from copy import copy

neu_phollick_alpha = Font('Neu Phollick Alpha', 40.0, True, 5.0)
neu_phollick_alpha_c = Font('Neu Phollick Alpha', 40.0, True, 0.0)
neu_phollick_alpha_c2 = Font('Neu Phollick Alpha', 40.0, True, -4.0)
neu_phollick_alpha_c3 = Font('Neu Phollick Alpha', 40.0, True, -7.0)
neu_phollick_alpha_c4 = Font('Neu Phollick Alpha', 40.0, True, -8.0)
neu_phollick_alpha_l = Font('Neu Phollick Alpha', 45.0, True)
neu_phollick_alpha_poem = Font('Neu Phollick Alpha', 42.0, True, line_spacing = 64)
neu_phollick_alpha_lc = Font('Neu Phollick Alpha Bold', 45.0, False, -7.0)
neu_phollick_alpha_lc2 = Font('Neu Phollick Alpha Bold', 45.0, False, -10.0)
neu_phollick_alpha_lc3 = Font('Neu Phollick Alpha Bold', 45.0, False, -5.0)
neu_phollick_alpha_xl = Font('Neu Phollick Alpha', 50.0, True)
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
flute_ex_s = Font('Flute Expanded', 31.0, True, -5.0)
flute_ex_s2 = Font('Flute Expanded', 31.0, True, -1.0)
flute_ex_xs = Font('Flute Expanded', 30.0, True, -5.0)
flute_l = Font('Flute', 43.0, True, -5.0)
flute_xl = Font('Flute', 45.0, True, -8.0)
wiki = Font('Wiki', 40.0, True, 5.0)
worstveld = Font('Worstveld Sling Bold', 60.0)

# I found two variants of this font with different shapes, I believe this is
# the one used in game: http://www.fontsquirrel.com/fonts/architects-daughter
arch_daughter = Font("Architects Daughter", 35.0, True, -13)
arch_daughter_t = Font("Architects Daughter", 45.0, True, -13)
arch_daughter_t2 = Font("Architects Daughter Bold", 40.0)
arch_daughter_s = Font("Architects Daughter Bold", 30.0, False, -13)

# I modified this font from the original to add accented characters.
# Some of the tops of the letters are slightly cut off - not very noticeable,
# will have to check if that's in the font or if it's a bug in The GIMP:
newspaper_big_heading = Font('New Yorker Accented', 105.0, True)
newspaper_headline = Font('New Yorker Accented', 52.0, True, -1.0)

newspaper_body = Font('OldNewspaperTypes Medium', 24.0, True, -1.0)

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
    font = neu_phollick_alpha
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1130, 90, 1830)
    layer = add_text_layer_from_file(image, 'sirius.txt', font)
    place_text(layer, 623, 331, xalign=RIGHT)

def compose_note_8(image, note_name):
    font = flute
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1457, 250, xalign=CENTER, yalign=CENTER)
    txt = read_text('sirius.txt').upper()
    layer = add_text(image, txt, font)
    place_text(layer, 1837, 903, xalign=RIGHT)

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
    layer = add_text_layer_from_file(image, '%s_to_sirius.txt' % note_name, font)
    place_text(layer, 1590, 60, xalign=CENTER)

def compose_note_12(image, note_name):
    font = arch_daughter
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 220, 100, 960)

def compose_note_13(image, note_name):
    font = neu_phollick_alpha_c
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    word_wrap(layer, None, 970 - 210)
    place_text(layer, 210, 60)
    reduce_text_line_spacing_to_fit(layer, 1000 - 60)

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
    font = neu_phollick_alpha_l
    font_t = neu_phollick_alpha_xl
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font_t)
    underline_text(layer)
    place_text(layer, 575, 127, xalign=CENTER, yalign=CENTER)

    layer = add_text_layer_from_file(image, 'statue.txt', font)
    place_text(layer, 682, 340, yalign=CENTER)

    layer = add_text_layer_from_file(image, '%s_lab.txt' % note_name, font)
    place_text(layer, 713, 875, yalign=CENTER)

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
    font_t = neu_phollick_alpha_lc
    font2 = neu_phollick_alpha_s
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    word_wrap(layer, None, 973 - 195)
    place_text(layer, 195, 175)
    reduce_text_line_spacing_to_fit(layer, 1000 - 175)

    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, font_t)
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
    font = flute_ex_s2
    txt = read_text('%s.txt' % note_name)

    x1, x2 = 230, 970
    y1, y2 = 55, 1000
    layer = add_text(image, txt, font)
    place_text(layer, x1, y1)
    txt = bold_word_wrap(layer, txt, x2-x1, y2-y1)

    layer = add_text(image, txt, font)
    place_text(layer, 1115, y1, 1850)

def compose_note_aa(image, note_name):
    font = arch_daughter_s
    def place_drug_text(drug, x1, y, x2):
        yoff = font.line_spacing * -0.5
        (title, desc) = read_text('%s_%s.txt' % (note_name, drug)).split('\n', 1)
        layer = add_text(image, title, font)
        word_wrap_reverse(layer, x2-x1)
        place_text(layer, x1, int(y + yoff), yalign=BOTTOM)
        layer = add_text(image, desc, font)
        place_text(layer, x1, int(y - yoff), x2)

    place_drug_text('basic_medicine', 538, 77, 956)
    place_drug_text('endurance_emphasis', 230, 310, 735)
    place_drug_text('muscle_emphasis', 460, 556, 965)
    place_drug_text('brain_emphasis', 240, 858, 810)
    place_drug_text('energy_stim', 1113, 77, 1572)
    place_drug_text('clarity_tonic', 1267, 310, 1876)
    place_drug_text('herculean_tonic', 1220, 559, 1705)
    place_drug_text('mental_stim', 1376, 821, 1880)

def compose_note_bb(image, note_name):
    font = worstveld
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 205, 70, 915)

    layer = add_text(image, get_plant_name('pink spotted lily'), font)
    place_text(layer, 880, 907, xalign=RIGHT, yalign=CENTER)
    layer = add_text(image, get_plant_name('white spiked prairie flower'), font)
    word_wrap_balanced(layer, 1860 - 1250)
    place_text(layer, 1250, 65)
    layer = add_text(image, get_plant_name('common white mushroom'), font)
    place_text(layer, 1560, 365, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, get_plant_name('white/pink viola'), font)
    place_text(layer, 1645, 445, 1880 )
    layer = add_text(image, get_plant_name('pawn-shaped mushroom'), font)
    x = max(1250 - layer.width/2, 1035)
    place_text(layer, x, 870, yalign=CENTER)
    layer = add_text(image, get_plant_name('wood gill fungus'), font)
    place_text(layer, 1625, 955, xalign=RIGHT, yalign=CENTER)

def compose_note_cc(image, note_name):
    font = arch_daughter
    font_t = arch_daughter_t2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 215, 390, 970)

    x = 590
    layer = add_text_layer_from_file(image, 'synthesis_of.txt', font)
    place_text(layer, x, 215, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, font_t)
    underline_text(layer)
    place_text(layer, x, 316, xalign=CENTER, yalign=CENTER)

    layer = add_text_layer_from_file(image, 'primary_materials.txt', font)
    place_text(layer, 1350, 70, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, '1. %s' % get_plant_name('large jungle flower'), font)
    place_text(layer, 1455, 520, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, '2. %s' % get_plant_name('fleshy purple fruit'), font)
    place_text(layer, 1460, 920, xalign=CENTER, yalign=CENTER)

def compose_note_dd(image, note_name):
    font = arch_daughter
    font_t = arch_daughter_t2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 215, 350, 970)

    x = 585
    layer = add_text_layer_from_file(image, 'synthesis_of.txt', font)
    place_text(layer, x, 172, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, font_t)
    underline_text(layer)
    place_text(layer, x, 269, xalign=CENTER, yalign=CENTER)

    txt = '1. %s\n2. %s' % (get_plant_name('giant bloom'), get_plant_name('blue-capped toadstool'))
    x = 1105
    layer = add_text_layer_from_file(image, 'primary_materials.txt', font)
    place_text(layer, 1088, 74, yalign=CENTER)
    layer = add_text(image, txt, font)
    place_text(layer, x, 550)
    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, x, 725)

def compose_note_ee(image, note_name):
    font = arch_daughter
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 215, 94, 970)

    layer = add_text(image, get_plant_name('carnivorous trap plant'), font)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_RIGHT)
    place_text(layer, 1095, 105, 1435, xalign=RIGHT)
    layer = add_text(image, get_plant_name('fleshy rooted plant'), font)
    place_text(layer, 1310, 480, 1625)
    layer = add_text(image, get_plant_name('red-green tree fungus'), font)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_RIGHT)
    place_text(layer, 1100, 820, 1420, xalign=RIGHT)

def compose_note_ff(image, note_name):
    font = neu_phollick_alpha_l
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1105, 90, 1865)

    layer = add_text(image, get_plant_name('fabaceae'), font)
    place_text(layer, 480, 115, yalign=CENTER)
    layer = add_text(image, get_plant_name('red toadstool'), font)
    place_text(layer, 660, 940, xalign=CENTER, yalign=CENTER)

def compose_note_gg(image, note_name):
    font = neu_phollick_alpha_l
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1105, 50, 1865)

    layer = add_text(image, get_plant_name('sunflower'), font)
    # place_text(layer, 1430, 715, xalign=RIGHT, yalign=CENTER)
    place_text(layer, 1662, 910, yalign=CENTER)
    layer = add_text(image, get_plant_name('orange prairie flower'), font)
    place_text(layer, 545, 320, yalign=CENTER)
    # TODO - MASK WORD WRAP
    layer = add_text(image, get_plant_name('red and yellow hibiscus'), font)
    place_text(layer, 640, 885, xalign=RIGHT, yalign=CENTER)

def compose_note_hh(image, note_name):
    font = flute_xl
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 210, 85, 950)

    layer = add_text(image, get_plant_name('indigo asteraceae'), font)
    place_text(layer, 730, 880, xalign=RIGHT, yalign=CENTER)
    layer = add_text(image, get_plant_name('tropical buttercup'), font)
    place_text(layer, 1395, 95, yalign=CENTER)
    layer = add_text(image, get_plant_name('pink-white prairie flower'), font)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_RIGHT)
    place_text(layer, 1230, 540, 1600, xalign=RIGHT)
    layer = add_text(image, get_plant_name('violet cactus'), font)
    place_text(layer, 1430, 920, yalign=CENTER)

def compose_note_ii(image, note_name):
    font = neu_phollick_alpha_lc2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 230, 530, 892)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1140, 595, 1825)

def compose_note_jj(image, note_name):
    font = neu_phollick_alpha_lc2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 230, 540, 915)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1150, 540, 1830)

def compose_note_kk(image, note_name):
    font = neu_phollick_alpha_lc2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1155, 555, 1840)

    clip_1_mask = get_layer_by_name(image, 'clip1_mask')
    clip_2_mask = get_layer_by_name(image, 'clip2_mask')
    clip_2_tape = get_layer_by_name(image, 'clip2_tape')
    clip_1_mask.visible = False
    clip_2_mask.visible = False

    gap = 18

    x1, x2 = 226, 585
    header = add_text_layer_from_file(image, '%s_clip1_heading.txt' % note_name, newspaper_headline)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    word_wrap(header, None, x2-x1)
    place_text(header, x1 + (x2-x1)/2, 390, xalign=CENTER)
    add_layer_mask_from_other_layer_alpha(header, clip_1_mask)
    txt = read_text('%s_clip1.txt' % note_name)
    # Add no breaking spaces to force final line to justify as well:
    layer = add_text(image, '%s %s' % (txt, u'\u00a0'*100), newspaper_body)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_FILL)
    place_text(layer, x1, header.offsets[1]+header.height + gap, x2)
    add_layer_mask_from_other_layer_alpha(layer, clip_1_mask)

    layer = add_text_layer_from_file(image, '%s_under.txt' % note_name, newspaper_body)
    if layer is not None:
        place_text(layer, 604, 558)
        add_layer_mask_from_other_layer_alpha(layer, clip_1_mask)

    x1, x2 = 607, 935
    y2 = 572
    header = add_text_layer_from_file(image, '%s_clip2_heading.txt' % note_name, newspaper_headline)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    word_wrap(header, None, x2-x1)
    place_text(header, x1 + (x2-x1)/2, 56, xalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_clip2.txt' % note_name, newspaper_body)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_FILL)
    place_text(layer, x1, header.offsets[1]+header.height + gap, x2)
    add_layer_mask_from_other_layer_alpha(layer, clip_2_mask)
    pdb.gimp_image_reorder_item(image, clip_2_tape, None, 0)

def compose_note_ll(image, note_name):
    font = neu_phollick_alpha_lc3
    font2 = neu_phollick_alpha_c2

    x1, x2 = 208, 965
    y1, y2 = 40, 1000

    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    word_wrap(layer, None, x2-x1)
    place_text(layer, x1, y1)
    y = int(y1 + layer.height + font.line_spacing)

    layer = add_text_layer_from_file(image, '%s_or.txt' % note_name, font)
    place_text(layer, x1 + (x2-x1)/2, y, xalign=CENTER)
    y = int(y + layer.height + font.line_spacing)

    layer = add_text_layer_from_file(image, '%s_b.txt' % note_name, font)
    place_text(layer, x1, y, x2)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1107, y1, 1840)

    layer = add_text_layer_from_file(image, '%s_step1.txt' % note_name, font2)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1467, 570, xalign=RIGHT, yalign=BOTTOM)
    layer = add_text_layer_from_file(image, '%s_step2.txt' % note_name, font2)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1530, 430, xalign=CENTER, yalign=BOTTOM)
    layer = add_text_layer_from_file(image, '%s_step3.txt' % note_name, font2)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1700, 500, xalign=CENTER, yalign=CENTER)

def compose_note_mm(image, note_name):
    font = neu_phollick_alpha_lc
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 256, 595, 935)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1158, 570, 1815)

def compose_note_nn(image, note_name):
    font = neu_phollick_alpha_poem
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1475, 475, xalign=CENTER, yalign=CENTER)

def compose_note_oo(image, note_name):
    font = neu_phollick_alpha_lc3
    font2 = neu_phollick_alpha_c2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 208, 45, 930)

    layer = add_text_layer_from_file(image, '%s_step1.txt' % note_name, font2)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1300, 285, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_step2.txt' % note_name, font2)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1550, 155, xalign=CENTER, yalign=CENTER)

def compose_note_pp(image, note_name):
    font = neu_phollick_alpha_lc2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1155, 570, 1815)

    clip_mask = get_layer_by_name(image, 'mask')
    clip_mask.visible = False
    gap = 18

    x1, x2 = 270, 707
    header = add_text_layer_from_file(image, '%s_clip_heading.txt' % note_name, newspaper_headline)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    word_wrap(header, None, x2-x1)
    place_text(header, x1 + (x2-x1)/2, 375, xalign=CENTER)
    y = header.offsets[1] + header.height

    txt = read_text('%s_clip.txt' % note_name)
    # Add no breaking spaces to force final line to justify as well:
    layer = add_text(image, '%s %s' % (txt, u'\u00a0'*100), newspaper_body)

    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_FILL)
    place_text(layer, x1, y  + gap, x2)
    add_layer_mask_from_other_layer_alpha(layer, clip_mask)

    w = 330
    layer = gimp.Layer(image, 'line', w, 1, RGB_IMAGE, 100.0, NORMAL_MODE)
    image.add_layer(layer, 0)
    gimp.set_background(0, 0, 0)
    layer.fill(BACKGROUND_FILL)
    layer.set_offsets(x1 + (x2-x1-w)/2, y + gap/3)


def compose_note_qq(image, note_name):
    font = neu_phollick_alpha_lc2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1155, 570, 1815)

    clip_mask = get_layer_by_name(image, 'mask')
    clip_mask.visible = False

    x1, x2 = 226, 972
    layer = add_text_layer_from_file(image, '%s_newspaper_name.txt' % note_name, newspaper_big_heading)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 645, 82, xalign=CENTER)
    # pdb.gimp_layer_resize(layer, x2-x1, layer.height, -(x1-layer.offsets[0]), 0)
    add_layer_mask_from_other_layer_alpha(layer, clip_mask)

    x1, x2 = 271, 928
    header = add_text_layer_from_file(image, '%s_clip_heading.txt' % note_name, newspaper_headline)
    pdb.gimp_text_layer_set_justification(header, TEXT_JUSTIFY_CENTER)
    reduce_text_to_fit(header, x1, x2)
    place_text(header, x1 + (x2-x1)/2, 305, xalign=CENTER, yalign=CENTER)

    txt = read_text('%s_clip.txt' % note_name)
    # Add no breaking spaces to force final line to justify as well:
    layer = add_text(image, '%s %s' % (txt, u'\u00a0'*100), newspaper_body)

    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_FILL)
    place_text(layer, x1, 875, x2)
    add_layer_mask_from_other_layer_alpha(layer, clip_mask)

def compose_note_rr(image, note_name):
    font = neu_phollick_alpha_l
    layer = add_text_layer_from_file(image, '%s_boat.txt' % note_name, font)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 465, 195, xalign=CENTER)

    layer = add_text_layer_from_file(image, '%s_causeway.txt' % note_name, font)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    place_text(layer, 1280, 390, xalign=CENTER, yalign=BOTTOM)

def compose_note_ss(image, note_name):
    font = worstveld
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 1115, 70, 1830)

def compose_note_tt(image, note_name):
    font = neu_phollick_alpha_c3
    font2 = neu_phollick_alpha_s
    font3 = neu_phollick_alpha_c4
    font_t = neu_phollick_alpha_lc

    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, font_t)
    pdb.gimp_text_layer_set_justification(layer, TEXT_JUSTIFY_CENTER)
    word_wrap(layer, None, 950 - 225)
    place_text(layer, 575, 140, xalign=CENTER, yalign=BOTTOM)

    x1, x2 = 230, 930
    layer = add_text_layer_from_file(image, '%s_step1.txt' % note_name, font)
    place_text(layer, x1, 170, x2)
    layer = add_text_layer_from_file(image, '%s_step2.txt' % note_name, font)
    place_text(layer, x1, 505, x2)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font3)
    place_text(layer, 1108, 630, 1835)

    layer = add_text_layer_from_file(image, '%s_you_are_here.txt' % note_name, font2)
    place_text(layer, 1610, 540, yalign=CENTER)

    txt = read_text('%s_statue.txt' % note_name)
    layer = add_text(image, txt, font2)
    place_text(layer, 297, 672, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, txt, font2)
    place_text(layer, 1185, 60, xalign=CENTER, yalign=CENTER)

    txt = read_text('%s_tent.txt' % note_name)
    layer = add_text(image, txt, font2)
    place_text(layer, 655, 670, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, txt, font2)
    place_text(layer, 1545, 60, xalign=CENTER, yalign=CENTER)

    txt = read_text('%s_cabin.txt' % note_name)
    layer = add_text(image, txt, font2)
    place_text(layer, 877, 760, xalign=CENTER, yalign=CENTER)
    layer = add_text(image, txt, font2)
    place_text(layer, 1760, 90, xalign=CENTER, yalign=CENTER)

def compose_note_uu(image, note_name):
    font = arch_daughter
    font_t = arch_daughter_t2
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 215, 390, 970)

    x = 585
    layer = add_text_layer_from_file(image, 'synthesis_of.txt', font)
    place_text(layer, x, 220, xalign=CENTER, yalign=CENTER)
    layer = add_text_layer_from_file(image, '%s_title.txt' % note_name, font_t)
    underline_text(layer)
    place_text(layer, x, 316, xalign=CENTER, yalign=CENTER)

    layer = add_text_layer_from_file(image, 'primary_materials.txt', font)
    place_text(layer, 1336, 73, xalign=CENTER, yalign=CENTER)
    x = 1470
    layer = add_text(image, '1. %s' % get_plant_name('sponge-like fungus'), font)
    place_text(layer, x, 480, xalign=CENTER)
    layer = add_text(image, '2. %s' % get_plant_name('trumpet mushroom'), font)
    place_text(layer, x, 900, xalign=CENTER)

def compose_note_vv(image, note_name):
    font = flute_ex_s

    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 240, 40, 980)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1120, 640, 1835)

def compose_note_ww(image, note_name):
    font = flute_ex_xs
    txt = read_text('%s.txt' % note_name)

    x1, x2 = 220, 970
    y1, y2 = 35, 1000
    layer = add_text(image, txt, font)
    line_spacing = pdb.gimp_text_layer_get_line_spacing(layer)
    while True:
        place_text(layer, x1, y1)
        txt_rh = bold_word_wrap(layer, txt, x2-x1, y2-y1)

        layer_rh = add_text(image, txt_rh, font)
        pdb.gimp_text_layer_set_line_spacing(layer_rh, line_spacing)
        place_text(layer_rh, 1110, y1)
        overflow = bold_word_wrap(layer_rh, txt_rh, 740, y2-y1)

        if not overflow:
            break

        # try again with less line spacing:
        line_spacing -= 1
        image.remove_layer(layer)
        image.remove_layer(layer_rh)
        layer = add_text(image, txt, font)
        pdb.gimp_text_layer_set_line_spacing(layer, line_spacing)


def compose_note_xx(image, note_name):
    font = flute_ex_s

    y = 45
    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 240, y, 965)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
    place_text(layer, 1100, y, 1845)

def compose_note_yy(image, note_name):
    font = flute_ex_s2
    txt = read_text('%s.txt' % note_name)

    x1, x2 = 240, 960
    y1, y2 = 45, 1000
    layer = add_text(image, txt, font)
    place_text(layer, x1, y1)
    txt = bold_word_wrap(layer, txt, x2-x1, y2-y1)

    layer = add_text(image, txt, font)
    place_text(layer, 1120, y1, 1850)

def compose_note_zz(image, note_name):
    font = flute_ex_s2

    layer = add_text_layer_from_file(image, '%s.txt' % note_name, font)
    place_text(layer, 240, 70, 970)

    layer = add_text_layer_from_file(image, '%s_rh.txt' % note_name, font)
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
