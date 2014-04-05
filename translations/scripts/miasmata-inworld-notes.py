#!/usr/bin/env python

from gimpfu import *
from miasmata_gimp import *

in_world_notes = (
    ('Notes', 2048, 36, (
        ('NOTE_8', 'NOTE_16'),
        ('NOTE_7', 'NOTE_15'),
        ('NOTE_5', 'NOTE_14'),
        ('NOTE_4', 'NOTE_13'),
        ('NOTE_3', 'NOTE_12'),
        ('NOTE_2', 'NOTE_11'), # Note 2 has no map, left page on right
        ('NOTE_1', 'NOTE_10'),
        ('NOTE_0', 'NOTE_9', 'NOTE_17') # Note 0 only has left page, on right
    )), ('InWorldNotesz_Set2', 2048, 0, (
        ('NOTE_AA',  None,     'NOTE_NN', 'NOTE_YY'),
        ('NOTE_BB',  None,     'NOTE_RR', 'Note_A1'),
        ('NOTE_CC', 'NOTE_KK', 'NOTE_SS', 'NOTE_ZZ'),
        ('NOTE_DD', 'NOTE_LL', 'NOTE_UU', 'NOTE_A2'),
        ('NOTE_EE',  None,     'NOTE_TT', 'NOTE_A3'),
        ('NOTE_FF', 'NOTE_OO', 'NOTE_VV', 'NOTE_A4'),
        ('NOTE_GG', 'NOTE_PP', 'NOTE_WW', 'NOTE_A5'),
        ('NOTE_HH', 'NOTE_QQ', 'NOTE_XX', 'NOTE_A6'),
              # ^^ clippings - will need special handling
              # II, JJ, MM don't have text, can just copy from originals
              # KK contains some text cut off from the large image
              # PP, QQ appears to contains earlier edit vs large image!
              # LL, OO are normal
                    # ^^ NN coords differ
    )), ('InWorldNotesz_Set3', 1024, 0, (
        ('NOTE_A7', ),
        ('NOTE_A8', ),
        ('NOTE_A9', ),
    ))
)

extra_note_shift = {
    'NOTE_1': 2,
    'NOTE_NN': -2,
}

note_scale = 4
note_w = 2048 / note_scale
note_h = 1024 / note_scale
border_width = 148 / note_scale
page_width = 1024 / note_scale - border_width

binder_x = (978 / note_scale, 1035 / note_scale)
binder_y = (75 / note_scale, 494 / note_scale, 912 / note_scale)
binder_w = binder_h = 36 / note_scale

binder_x = (244, 259)
binder_y = (18, 123, 228)
binder_w = 9
binder_h = 10

def clip_note_borders(layer):
    image = layer.image
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE,
            0, 0,
            border_width, layer.height)
    pdb.gimp_edit_clear(layer)
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE,
            layer.width - border_width, 0,
            border_width, layer.height)
    pdb.gimp_edit_clear(layer)
    pdb.gimp_selection_clear(image)

def remove_binder_holes(layer, mask_layer):
    image = layer.image
    pdb.gimp_selection_clear(image)
    for y in binder_y:
        for x in binder_x:
            pdb.gimp_image_select_ellipse(image, CHANNEL_OP_ADD,
                    x, y, binder_w, binder_h)
    pdb.python_fu_heal_selection(image, layer, 50, 0, 2)

    # Alternatively:
    # pdb.gimp_edit_clear(mask_layer)

    pdb.gimp_selection_clear(image)

def note_n(layer):
    pdb.gimp_layer_resize(layer,
            page_width, layer.height,
            -note_w / 2, 0)
    layer.set_offsets(0, 0)

def left_hand_page(layer):
    pdb.gimp_layer_resize(layer,
            layer.width, layer.height,
            page_width, 0)
    layer.set_offsets(0, 0)

def translate_clip(layer,
        ((fx1, fy1), (fx2, fy2)),
        ((tx1, ty1), (tx2, ty2))):
    ((fx1, fy1), (fx2, fy2)) = \
           ((fx1 / note_scale, fy1 / note_scale),
            (fx2 / note_scale, fy2 / note_scale))
    ((tx1, ty1), (tx2, ty2)) = \
           ((tx1 % note_w, ty1 % note_h),
            (tx2 % note_w, ty2 % note_h))
    pdb.gimp_layer_resize(layer, fx2 - fx1, fy2 - fy1, -fx1, -fy1)
    layer.scale(tx2 - tx1, ty2 - ty1, FALSE)
    layer.set_offsets(tx1, ty1)

def note_k(layer):
    # Could potentially do something smarter here and remove the clipping
    # obscuring some text
    layer2 = layer.copy(True)
    layer.image.add_layer(layer2, 0)

    translate_clip(layer,
            ((221, 382), (590, 987)),
            ((524, 602), (610, 743)))
    yield layer
    translate_clip(layer2,
            ((560,  50), (970, 570)),
            ((647, 556), (758, 700)))
    yield layer2

def note_p(layer):
    translate_clip(layer,
            ((263,  365), (717,  968)),
            ((600, 1623), (719, 1783)))

def note_q(layer):
    translate_clip(layer,
            ((227,   87), (972,  963)),
            ((542, 1801), (747, 2043)))

manipulate_note = {
        'NOTE_0': left_hand_page,
        'NOTE_2': left_hand_page,
        'NOTE_NN': note_n,
        'NOTE_KK': note_k,
        'NOTE_PP': note_p,
        'NOTE_QQ': note_q,
}

def update_in_world_note(image, note, (x, y), mask_layer, offset):
    if note is None:
        return
    x *= note_w
    y *= note_h
    print 'update_in_world_note %s @ %ix%i' % (note, x, y)
    try:
        try:
            note_filename = '%s.xcf' % note
            note_image = pdb.gimp_file_load(note_filename, note_filename)
        except:
            note_filename = '%s.png' % note
            note_image = pdb.gimp_file_load(note_filename, note_filename)
    except RuntimeError:
        print 'SKIPPING IN-WORLD VERSION OF %s - LARGE VERSION NOT FOUND' % note
        return
    layer = pdb.gimp_layer_new_from_visible(note_image, image, note)
    image.add_layer(layer, 0)
    layer.scale(note_w, note_h)

    clip_note_borders(layer)
    remove_binder_holes(layer, mask_layer)
    layers = (layer, )
    if note in manipulate_note:
        layers = manipulate_note[note](layer)
        if layers is None:
            layers = (layer, )

    shift = extra_note_shift.get(note, 0)
    for layer in layers:
        layer.translate(offset + shift + x, y)
        pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, mask_layer)
        pdb.gimp_selection_invert(image)
        pdb.gimp_edit_clear(layer)
        pdb.gimp_selection_clear(image)

def generate_in_world_notes(input_dir):
    import os

    try:
        pdb.gimp_context_set_interpolation(INTERPOLATION_LANCZOS)
    except:
        pdb.gimp_context_set_interpolation(INTERPOLATION_NOHALO)


    for (name, dimensions, offset, notes) in in_world_notes:
        filename = os.path.join(input_dir, '%s.xcf' % name)
        # image = gimp.Image(dimensions, dimensions, RGB)
        image = pdb.gimp_file_load(filename, filename)
        mask_layer = image.layers[0]

        for (y, row) in enumerate(notes):
            for (x, note) in enumerate(row):
                update_in_world_note(image, note, (x, y), mask_layer, offset)

        mask_layer.visible = False

        save_xcf(image, '%s.xcf' % name)
        image2 = pdb.gimp_image_duplicate(image)
        image2.merge_visible_layers(CLIP_TO_IMAGE)
        pdb.gimp_layer_resize_to_image_size(image2.active_layer)
        save_dds(image2, '%s.dds' % name, True, mipmaps=True)
        save_png(image2, '%s.png' % name)

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
        (PF_STRING, "input_dir", "Directory with the blank templates to use", None),
    ],
    [],
    generate_in_world_notes,
)

main()
