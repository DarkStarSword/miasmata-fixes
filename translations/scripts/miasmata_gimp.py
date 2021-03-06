#!/usr/bin/env python

from gimpfu import *
import re

LEFT = TOP = 0
CENTER = 1
RIGHT = BOTTOM = 2

class Font(object):
    def __init__(self, font, size, bold = False, line_spacing = 0.0, letter_spacing = 0.0):
        self.font, self.size, self.bold, self.line_spacing, self.letter_spacing = \
                font, size, bold, line_spacing, letter_spacing

def get_layer_by_name(image, name):
    for l in image.layers:
        if l.name == name:
            return l
    raise KeyError(name)

def add_layer_mask_from_other_layer_alpha(dest, source):
    image = dest.image
    pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, source)
    mask = pdb.gimp_layer_create_mask(dest, ADD_SELECTION_MASK)
    pdb.gimp_layer_add_mask(dest, mask)
    pdb.gimp_selection_none(image)

def add_text_layer(image, txt, font, font_size, line_spacing = None, colour = (0, 0, 0), name = 'Text', pos = (0, 0), letter_spacing=None):
    gimp.set_foreground(*colour)
    pdb.gimp_image_set_active_layer(image, image.layers[0])
    text = pdb.gimp_text_fontname(image, None, pos[0], pos[1], txt, 0, True, font_size, PIXELS, font)
    if text is None:
        return
    text.name = name
    if line_spacing is not None:
        pdb.gimp_text_layer_set_line_spacing(text, line_spacing)
    if letter_spacing is not None:
        pdb.gimp_text_layer_set_letter_spacing(text, letter_spacing)
    pdb.gimp_text_layer_set_hint_style(text, TEXT_HINT_STYLE_NONE)

    return text

def read_text(filename):
    return open(filename, 'rb').read().decode('utf-8').strip()

def get_plant_name(plant):
    plant_num = {
            'violet cactus': '00',
            'prickly pear': 0,
            'common white mushroom': 1,
            'pawn-shaped mushroom': 2,
            'red toadstool': 3,
            'pearl-blue shelf fungus': 4,
            'yellow mushrooms': 5,
            'grey shelf fungus': 6,
            'brown shelf fungus': 7,
            'sponge-like fungus': 8,
            'wood gill fungus': 9,
            'trumpet mushroom': 10,
            'white spiked prairie flower': 11,
            'pink-white prairie flower': 12,
            'orange prairie flower': 13,
            'white bundle prairie flower': 14,
            'sunflower': 15,
            'indigo asteraceae': 16,
            'red and yellow hibiscus': 17,
            'white/pink viola': 18,
            'blue-capped toadstool': 19,
            'red-green tree fungus': 20,
            'fleshy rooted plant': 21,
            'pink spotted lily': 22,
            'rainbow orchid': 23,
            'titan plant': 24,
            'giant bloom': 25,
            'bulbous, fruit plant': 26,
            'carnivorous pitcher plant': 27,
            'carnivorous trap plant': 28,
            'fabaceae': 29,
            'bio-luminescent algae': 30,
            'blue scaly tree fungus': 31,
            'large jungle flower': 32,
            'tropical buttercup': 33,
            'fleshy purple fruit': 34,


    }
    return read_text('../plants/Plant_%s.txt' % str(plant_num[plant])).split('\n')[0]

def add_text(image, txt, font, colour = (0, 0, 0)):
    layer = add_text_layer(image, txt, font.font, font.size, font.line_spacing, colour, letter_spacing=font.letter_spacing)
    if layer is None:
        return None
    pdb.gimp_text_layer_set_markup(layer, txt)
    if font.bold:
        bold_text(layer, txt)
    return layer

def add_text_layer_from_file(image, filename, font, colour=(0, 0, 0)):
    txt = read_text(filename)
    return add_text(image, txt, font, colour)

def place_text(layer, x, y, x2=None, y2=None, w=None, h=None, xalign=LEFT, yalign=TOP):
    if layer is None:
        return
    if x2 is not None:
        w = x2 - x
    if y2 is not None:
        h = y2 - y
    if w is not None:
        if h is None:
            h = layer.image.height - y
        pdb.gimp_text_layer_resize(layer, w, h)
    if xalign == CENTER:
        x = x - layer.width / 2
    elif xalign == RIGHT:
        if x2 is not None:
            x = x2 - layer.width
        else:
            x = x - layer.width
    if yalign == CENTER:
        y = y - layer.height / 2
    elif yalign == BOTTOM:
        if y2 is not None:
            y = y2 - layer.height
        else:
            y = y - layer.height
    layer.translate(x, y)

def center_layer(layer):
    image = layer.image
    return place_text(layer, image.width/2, image.height/2, xalign=CENTER, yalign=CENTER)

def reduce_text_to_fit(layer, x1, x2):
    (font_size, units) = pdb.gimp_text_layer_get_font_size(layer)
    while layer.width > x2 - x1:
        font_size -= 1
        pdb.gimp_text_layer_set_font_size(layer, font_size, units)

def reduce_and_wrap_text_to_fit(layer, text, font, x1, x2, y1, y2):
    (font_size, units) = pdb.gimp_text_layer_get_font_size(layer)
    while True:
        if font.bold:
            remaining = bold_word_wrap(layer, text, x2 - x1, max_height = y2 - y1)
        else:
            remaining = word_wrap(layer, text, x2 - x1, max_height = y2 - y1)
        if not remaining:
            break
        font_size -= 1
        pdb.gimp_text_layer_set_font_size(layer, font_size, units)
    place_text(layer, x1, y1)

def reduce_text_line_spacing_to_fit(layer, height):
    line_spacing = pdb.gimp_text_layer_get_line_spacing(layer)
    while layer.height > height:
        line_spacing -= 1
        pdb.gimp_text_layer_set_line_spacing(layer, line_spacing)

def get_markup(layer):
    markup = pdb.gimp_text_layer_get_markup(layer)
    if markup.lower().startswith('<markup>') and markup.lower().endswith('</markup>'):
        return markup[8:-9]
    return markup

def bold_text(layer, txt=None):
    # XXX: Requires a patched GIMP to set text markup
    # See https://bugzilla.gnome.org/show_bug.cgi?id=724101
    if txt is None:
        txt = get_markup(layer)
    markup = '<b>%s</b>' % txt
    pdb.gimp_text_layer_set_markup(layer, markup)

def underline_text(layer):
    # XXX: Requires a patched GIMP to set text markup
    # See https://bugzilla.gnome.org/show_bug.cgi?id=724101
    markup = get_markup(layer)
    markup = '<u>%s</u>' % markup
    pdb.gimp_text_layer_set_markup(layer, markup)

# Brackets in the regex make this partition instead of split:
tag_partitions_re = re.compile(r'(\<[^\>]*\>)')
tag_re = re.compile(r'\</?([^\> ]+)[^\>]*\>')
def tag_preserving_split(text, sep=' '):
    tags = []
    ret = []

    # Partition string by tags (the grouping brackets around the entire regular
    # expression cause this to partition instead of split):
    partitions = tag_partitions_re.split(text)
    for partition in partitions:
        # Keep a stack of currently active tags
        if partition.startswith('</'):
            #FIXME: Check popping expected tag
            tags.pop()
            continue
        match = tag_re.match(partition)
        if match:
            #assert(tags == []) # Likely have a bug in this case. Fail now
            tags.append((partition, '</%s>' % match.group(1)))
            continue

        # Not a tag. Split text by sep and add tags around each individual word
        for (i, word) in enumerate(partition.split(sep)):
            # If word is an empty string, it will be joined with a word from
            # another partition. Therefore, only apply tags to actual words:
            if word:
                for (pre, post) in reversed(tags):
                    word = '%s%s%s' % (pre, word, post)

            if i == 0 and ret:
                # First word in a partition is concatenated with the last word
                # of the previous parititon. This allows punctuation outside of
                # tags to be joined with the <i>final word in the tag</i>. If
                # there was a space one of partitions will have an empty
                # string, so this still works.
                ret[-1] += word
            else:
                ret.append(word)
    return ret

def _tag_preserving_join(text_lh, text_rh, sep=''):
    making_progress = True
    while making_progress:
        making_progress = False
        match_rh = tag_re.match(text_rh)
        if not match_rh or text_rh.startswith('</'):
            break
        if not text_lh.endswith('</%s>' % match_rh.group(1)):
            break

        # Found a pair of tags that are a candidate for joining. Since the end
        # tag doesn't include the attributes we can't be sure it's the same tag
        # - scan the left hand string backwards to find the corresponding start
        # tag and check that instead:
        tags = []
        partitions = tag_partitions_re.split(text_lh)
        trim_lh = 0
        for partition in reversed(partitions):
            trim_lh += len(partition)
            match_lh = tag_re.match(partition)
            if match_lh:
                if partition.startswith('</'):
                    tags.append(partition)
                elif partition.startswith('<'):
                    #FIXME: Check popping expected tag
                    tags.pop()
                    if tags == []:
                        # No tags left on stack, so whatever tag we just popped
                        # should match the closed tag - check it:
                        if match_lh.group(0) == match_rh.group(0):
                            text_lh = text_lh[:text_lh.rfind('</')]
                            text_rh = text_rh[match_rh.end():]
                            making_progress = True
                        break
    return '%s%s%s' % (text_lh, sep, text_rh)

def tag_preserving_join(sep, lst):
    if lst == []:
        return ''
    ret = lst.pop(0)
    while len(lst):
        ret = _tag_preserving_join(ret, lst.pop(0), sep)
    return ret

def masked_word_wrap(layer, mask, max_width, channel = VALUE_MODE, threshold = 128, test = -1, hpad = 5, vpad = -2):
    import struct

    def find_room_in_mask(min_x, min_y, max_x, start_x, required_w, required_h, right_justify = False):
        gimp.tile_cache_ntiles((required_h + 2 * vpad + 63) / 64)
        direction = 1
        if right_justify:
            direction = -1
        (x, y) = (start_x, min_y)
        xt = x - hpad*direction
        while True:
            for yt in range(y - vpad, y + required_h + vpad):
                tile = mask.get_tile2(False, xt, yt)
                if tile is None:
                    print 'WARNING find_room_in_mask: No tile for %i x %i!' % (xt, yt)
                    continue
                # FIXME: Assumes 32bpp 8bit channel and ignores alpha
                channels = (r, g, b, a) = struct.unpack('4B', tile[xt % tile.ewidth, yt % tile.eheight])
                if channel == VALUE_MODE:
                    v = (r + g + b) * a / (3 * 255)
                elif channel == ALPHA_CHANNEL:
                    v = a
                else:
                    v = channels[channel]
                if cmp(v, threshold) == test:
                    # print "mask intersected at %i x %i" % (x, y)
                    x = xt + hpad*direction
                    break
            if not right_justify and xt - x >= required_w + hpad:
                return (x, y)
            elif right_justify and x - xt >= required_w + hpad:
                return (x, y)
            xt += direction
            if (not right_justify and xt - hpad > max_x) or (right_justify and xt - hpad < min_x):
                if right_justify:
                    raise IndexError("not enough room")
                y += required_h + int(line_spacing)
                x = min_x
                xt = x - hpad*direction

    image = layer.image
    text = pdb.gimp_text_layer_get_text(layer)
    if not text:
        text = get_markup(layer)
    if not text:
        return
    font = pdb.gimp_text_layer_get_font(layer)
    (font_size, font_units) = pdb.gimp_text_layer_get_font_size(layer)
    line_spacing = pdb.gimp_text_layer_get_line_spacing(layer)
    letter_spacing = pdb.gimp_text_layer_get_letter_spacing(layer)
    (min_x, y) = layer.offsets
    name = layer.name
    layer.visible = False
    group = pdb.gimp_layer_group_new(image)
    group.name = '%s_wrapped' % layer.name
    image.add_layer(group, 0)
    paragraph_spacing = 0

    justification = pdb.gimp_text_layer_get_justification(layer)
    if justification not in [TEXT_JUSTIFY_LEFT, TEXT_JUSTIFY_RIGHT]:
        raise ValueError('Unsupported text justification')
    direction = 1
    if justification == TEXT_JUSTIFY_RIGHT:
        direction = -1

    # FIXME: Probe for this:
    word_spacing = 10

    def place_line(line, x): # Not used for left justification
        # XXX: This is actually a stripped down version of this very outer
        # routine to place the text left justified starting at the calculated x
        # position - I could potentially refactor this code and call it
        # recursively
        while len(line):
            text = line.pop(0)
            if not text:
                x += word_spacing
                continue
            (x, _) = find_room_in_mask(min_x, y, min_x + max_width, x, text.width, text.height)
            text.set_offsets(x, y)
            x += text.width + word_spacing

    for paragraph in text.split('\n'):
        #words = paragraph.split(' ')
        words = tag_preserving_split(paragraph, ' ')
        if justification == TEXT_JUSTIFY_RIGHT:
            x = min_x + max_width
        else:
            x = min_x
        line = [] # Not used for left justification
        for word in words:
            if not word:
                x += word_spacing
                line.append(None)
                continue

            text = pdb.gimp_text_fontname(image, None, x, y, word, 0, True, font_size, font_units, font)
            pdb.gimp_text_layer_set_markup(text, word)

            paragraph_spacing = paragraph_spacing or text.height
            pdb.gimp_image_reorder_item(image, text, group, 0)

            if justification == TEXT_JUSTIFY_RIGHT:
                while True:
                    try:
                        (x, _) = find_room_in_mask(min_x, y, min_x + max_width, x, text.width, text.height, True)
                        line.append(text)
                        break
                    except IndexError:
                        place_line(line, x)
                        y += text.height + int(line_spacing)
                        x = min_x + max_width
            else:
                (x, y) = find_room_in_mask(min_x, y, min_x + max_width, x, text.width, text.height)
                # print 'Placing %s at %i x %i' % (word, x, y)
                text.set_offsets(x, y)

            x += (text.width + word_spacing) * direction
        if justification != TEXT_JUSTIFY_LEFT:
            place_line(line, x)
        y += paragraph_spacing + int(line_spacing)

    if letter_spacing is not None:
        pdb.gimp_text_layer_set_letter_spacing(text, letter_spacing)
    pdb.gimp_text_layer_set_hint_style(text, TEXT_HINT_STYLE_NONE)

    return group

word_wrap_fail_re = re.compile(r"""Element 'markup' was closed, but the currently open element is '(?P<elem>[^']+)'""")

def balance_newlines(layer):
    import sys

    # You can find a generic version of this algorithm in my junk code
    text = pdb.gimp_text_layer_get_text(layer)
    if not text:
        text = get_markup(layer)

    def width(lines):
        missing_tags = ''
        while True: # Hack to avoid splitting up <span> tags
            text = '\n'.join([' '.join(l) for l in lines])
            markup = '%s%s' % (text, missing_tags)
            try:
                pdb.gimp_text_layer_set_markup(layer, markup)
            except RuntimeError as e:
                match = word_wrap_fail_re.search(e.args[0])
                if not match:
                    raise
                missing_tags += '</%s>' % match.group('elem')
                continue
            break
        return layer.width

    lines = [x.split(' ') for x in text.split('\n')]
    for line in lines:
        while True:
            try:
                i = line.index('<span')
            except ValueError:
                break
            else:
                print 'Joining split span tag'
                line[i] = '%s %s' % (line[i], line[i+1])
                del line[i+1]

    print >>sys.stderr, 'Before - max width:',  width(lines)

    making_progress = True
    while making_progress:
        making_progress = False
        for i, l in enumerate(lines):
            if not len(l):
                continue
            if i > 0:
                ow = width(lines[i-1:i+1])
                lines[i-1].append(l.pop(0))
                nw = width(lines[i-1:i+1])
                if nw < ow:
                    making_progress = True
                    break
                l.insert(0, lines[i-1].pop(-1))
            if i < len(lines) - 1:
                ow = width(lines[i:i+2])
                lines[i+1].insert(0, l.pop(-1))
                nw = width(lines[i:i+2])
                if nw < ow:
                    making_progress = True
                    break
                l.append(lines[i+1].pop(0))

    print >>sys.stderr, 'After - max width:', width(lines)
    for l in lines:
        print ' '.join(l)

def word_wrap(layer, text, width, max_height = None, start_tag='', end_tag=''):
    # This is a workaround for the lack of a fixed-width + dynamic-height
    # setting for text boxes in the GIMP - otherwise there is no easy way to
    # wrap the text AND have it vertically centered.
    if not text:
        text = pdb.gimp_text_layer_get_text(layer)
    if not text:
        text = get_markup(layer)
    txt = None
    lines = tag_preserving_split(text, sep='\n')
    while len(lines):
        line = lines.pop(0)
        words = tag_preserving_split(line, sep=' ')
        if not len(words):
            return ''

        if txt is None:
            txt = words.pop(0)
            pdb.gimp_text_layer_set_markup(layer, txt)
        else:
            word = words.pop(0)
            txt1 = tag_preserving_join('\n', [txt, word])
            markup = '%s%s%s' % (start_tag, txt1, end_tag)
            pdb.gimp_text_layer_set_markup(layer, markup)
            if max_height is not None and layer.height > max_height:
                markup = '%s%s%s' % (start_tag, txt, end_tag)
                pdb.gimp_text_layer_set_markup(layer, markup)
                rem_line = tag_preserving_join(' ', [word] + words).strip()
                rem_lines = tag_preserving_join('\n', lines)
                return '\n' + tag_preserving_join('\n', [rem_line, rem_lines]).strip()
            txt = txt1

        while len(words):
            word = words.pop(0)
            txt1 = tag_preserving_join(' ', [txt, word])
            markup = '%s%s%s' % (start_tag, txt1, end_tag)
            # print '\n\nTrying text for word wrap:\n%s' % markup
            pdb.gimp_text_layer_set_markup(layer, markup)
            if layer.width > width:
                txt1 = '%s\n%s' % (txt, word)
                markup = '%s%s%s' % (start_tag, txt1, end_tag)
                pdb.gimp_text_layer_set_markup(layer, markup)
                if max_height is not None and layer.height > max_height:
                    markup = '%s%s%s' % (start_tag, txt, end_tag) # FIXME: Will break if splitting markup!
                    pdb.gimp_text_layer_set_markup(layer, markup)

                    rem_line = tag_preserving_join(' ', [word] + words).strip()
                    rem_lines = tag_preserving_join('\n', lines)
                    return tag_preserving_join('\n', [rem_line, rem_lines]).strip()
                width = max(width, layer.width)
            txt = txt1
    return ''

def word_wrap_balanced(layer,  width):
    text = pdb.gimp_text_layer_get_text(layer)
    if not text:
        text = get_markup(layer)
    lines = text.split('\n')
    # print lines
    out = []
    while len(lines):
        line = lines.pop(0)
        if len(line) == 0:
            out.append('')
            continue
        word_wrap(layer, line, width)
        balance_newlines(layer)
        out.append(get_markup(layer))
    # print out
    pdb.gimp_text_layer_set_markup(layer, '\n'.join(out))

def word_wrap_reverse(layer, width):
    text = pdb.gimp_text_layer_get_text(layer)
    if not text:
        text = get_markup(layer)
    words = text.split(' ')
    if not len(words):
        return ''
    txt = words[-1]
    for (i, word) in reversed(list(enumerate(words[:-1]))):
        txt1 = '%s %s' % (word, txt)
        pdb.gimp_text_layer_set_markup(layer, txt1)
        if layer.width > width:
            txt1 = '%s\n%s' % (word, txt)
            pdb.gimp_text_layer_set_markup(layer, txt1)
            width = max(width, layer.width)
        txt = txt1
    return ''

def bold_word_wrap(layer, text, width, max_height = None):
    return word_wrap(layer, text, width, max_height, start_tag='<b>', end_tag='</b>')

def blur_layer(image, layer, radius = 1.5):
    pdb.plug_in_gauss_rle2(image, layer, radius, radius)

def save_dds(image, filename, alpha, mipmaps=False):
    alpha = alpha and 3 or 1
    try:
        pdb.file_dds_save(
                image,
                image.active_layer,
                filename, # filename
                filename, # raw_filename
                alpha, # 1 = DXT1 (no alpha), 3 = DXT5 (alpha)
                mipmaps, # 1 = generate mipmaps <--- XXX Set this for in-game objects
                0, # 0 = save current layer
                0, # format
                -1, # transparent-index
                0, # DXT compression color-type (Tweaking may help in some cases)
                0, # Dither
                0, # mipmap-filter - maybe try tweaking this for in-game objects
                0, # gamma-correct
                2.2, # gamma
        )
    except:
        # Try newer API
        pdb.file_dds_save(
                image,
                image.active_layer,
                filename, # filename
                filename, # raw_filename
                alpha, # 1 = DXT1 (no alpha), 3 = DXT5 (alpha)
                mipmaps, # 1 = generate mipmaps <--- XXX Set this for in-game objects
                0, # 0 = save current layer
                0, # format
                -1, # transparent-index
                0, # mipmap-filter - maybe try tweaking this for in-game objects
                0, # mipmap-wrap
                0, # gamma-correct
                0, # use srgb colorspace for gamma correction
                2.2, # gamma
                0, # use perceptual error metric during DXT compression
                0, # preserve alpha coverage
                0.5, # alpha test threshold
        )

def save_png(image, filename):
    pdb.file_png_save2(image, image.active_layer, filename, filename,
            0, # interlace
            9, # compression
            0, # save background colour
            0, # save gamma
            0, # save layer offset
            1, # save pHYs (resolution?)
            1, # save creation time
            1, # save comment
            1, # preserve colour of transparent pixels
    )

def save_jpg(image, filename):
    pdb.file_jpeg_save(image, image.active_layer, filename, filename,
            0.9, # quality
            0.0, # smoothing
            1, # optimize
            0, # progressive
            "Generated by DarkStarSword's Miasmata translation scripts", # comment
            0, # Subsampling option number. 0 = 4:4:4?
            1, # baseline
            0, # restart
            1, # dct algorithm. 1 = Integer?
    )

def save_xcf(image, filename):
    pdb.gimp_xcf_save(0, image, image.active_layer, filename, filename)
    image.clean_all()

def save(image, output_basename, alpha=False, png=False, mipmaps=False):
    save_xcf(image, '%s.xcf' % output_basename)
    image2 = pdb.gimp_image_duplicate(image)
    image2.merge_visible_layers(CLIP_TO_IMAGE)
    save_dds(image2, '%s.dds' % output_basename, alpha, mipmaps)
    if alpha or png:
        save_png(image2, '%s.png' % output_basename)
    else:
        save_jpg(image2, '%s.jpg' % output_basename)

# vi:et:sw=4:ts=4
