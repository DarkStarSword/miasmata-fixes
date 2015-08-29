#!/usr/bin/env python

# Fix print function for Python 2 deficiency regarding non-ascii encoded text files:
from __future__ import print_function
import utf8file
print = utf8file.print

from PySide import QtGui
import pefile
import json

# These will be loaded from the translation file
name = 'Unnamed Translation'
version = '0.0'

txt_scanning = QtGui.QApplication.translate('exe patcher', 'Scanning Miasmata.exe for translatable strings...', None, QtGui.QApplication.UnicodeUTF8)
txt_success = QtGui.QApplication.translate('exe patcher', 'Patch successful', None, QtGui.QApplication.UnicodeUTF8)
txt_err = QtGui.QApplication.translate('exe patcher', '%s occurred writing to Miasmata.exe: %s', None, QtGui.QApplication.UnicodeUTF8)

all_translatables = []

class TranslatedStringTooLong(Exception): pass

class Translatable(object):
    def __init__(self, string):
        self.english = string
        self.translated = string
        all_translatables.append(self)

    def load_translation(self, translation):
        try:
            self.translated = translation[self.english]
        except:
            pass
        else:
            if len(self.translated) > self.max_len():
                raise TranslatedStringTooLong(self.english, self.translated)

    def max_len(self):
        # Strings are aligned to four byte boundaries. We need one byte for the
        # null terminator, so the max length can be found by rounding up to the
        # next multiple of four then subtracting one, or alternatively:
        return len(self.english) | 0x3

    def pad(self, string):
        return string + '\0' * (self.max_len() + 1 - len(string))

    @property
    def english_padded(self):
        return self.pad(self.english)

    @property
    def translated_padded(self):
        return self.pad(self.translated)


class Hunk(list):
    def scan(self, string, off):
        # NOTE: Must have at least one line of context
        if self[0] == string:
            return HunkMatch(self)

class HunkMatch(object):
    def __init__(self, hunk):
        self.hunk = hunk
        self.lineno = 1
        self.translatables = []
        self.english = True
        self.translated = True

    def scan(self, string, off):
        line = self.hunk[self.lineno]

        if isinstance(line, Translatable):
            self.lineno += 1
            self.translatables.append((line, off))
            if line.english != string:
                self.english = False
            if line.translated != string:
                self.translated = False
            return (self, self.lineno == len(self.hunk))

        if line == string:
            self.lineno += 1
            return (self, self.lineno == len(self.hunk))

        return (None, None)

    def apply_patch(self, fd):
        for (translatable, off) in self.translatables:
            fd.seek(off)
            fd.write(translatable.translated_padded.encode('cp1252'))

    def remove_patch(self, fd):
        for (translatable, off) in self.translatables:
            fd.seek(off)
            fd.write(translatable.english_padded.encode('cp1252'))

patch_hunks = (
    Hunk([
        'menu_bkg::device_reset()',
        'scene::device_reset()',
        'tutorials::device_reset()',
        '...',
        Translatable('%sOne Moment Please%s'),
        'menus',
        'fonts',
        'default',
    ]),Hunk([
        'inst_model::init_collision_data() : tree too deep(%s)',
        'pm',
        'am',
        Translatable('Day %d, %d%s'),
        'text_description',
        'inst_tree',
        'weather',
    ]),Hunk([
        'config',
        'text_description',
        'save%d',
        Translatable('Empty'),
        'save1',
        'save2',
        'save3',
    ]),Hunk([
        'color_alpha_ratio',
        'alpha_ref',
        'copy',
        Translatable('Saving...'),
        'source',
        'color',
        'color_alpha_ratio',
    ]),Hunk([
        'SLIDER',
        'GEN_MOUSE_INVY',
        Translatable('Inverted'),
        'DESCRIPTION',
        'GEN_MOUSE_INVY',
        Translatable('Normal'),
        'DESCRIPTION',
        'GEN_MOUSE_INVY',
    ]),Hunk([
        'GFX_TEX_DETAIL',
        Translatable('Low'),
        'DESCRIPTION',
        'GFX_TEX_DETAIL',
        Translatable('High'),
        'DESCRIPTION',
        'GFX_TEX_DETAIL',
        'SLIDER',
        'GFX_MDL_DETAIL',
        'SLIDER',
        'GFX_MDL_DETAIL',
        '%d%%',
        'DESCRIPTION',
        'GFX_MDL_DETAIL',
        Translatable('Low'),
        Translatable('High'),
        Translatable('Low'),
        Translatable('Medium'),
        Translatable('High'),
        Translatable('Low'),
        Translatable('Medium'),
        Translatable('High'),
        Translatable('Very High'),
        'SLIDER',
        'GFX_LIGHTSHAFTS',
    ]),Hunk([
        # These settings are not in older versions of the exe:
        'DESCRIPTION',
        'GFX_ANTIALIASING',
        Translatable('On'),
        Translatable('Off'),
        'DESCRIPTION',
        'GFX_VSYNC',
        Translatable('Windowed'),
        Translatable('Fullscreen'),
        'DESCRIPTION',
        'GFX_WINDOWED',
    ])
)

def load_translation(translation):
    global name, version

    (meta, patch) = json.load(translation, encoding='cp1252')
    for translatable in all_translatables:
        translatable.load_translation(patch)

    if 'name' in meta:
        name = meta['name']
    if 'version' in meta:
        version = meta['version']

def get_rdata(pe):
    return filter(lambda x: x.Name == '.rdata\0\0', pe.sections)[0]

def next_aligned(off):
    return (off & ~0x3) + 4

def iter_pe_strings(rdata):
    off = 0
    data = rdata.get_data()
    while off < len(data):
        string = data[off:data.find('\0', off)]

        # Check padding is NULL to eliminate any UTF16 strings and other garbage
        end = off + len(string)
        next_off = next_aligned(end)
        padding = data[end:next_off]

        try:
            ustring = string.decode('cp1252')
        except UnicodeDecodeError:
            pass
        else:
            if string and padding == '\0'*len(padding):
                yield (off, next_off - off - 1, next_off - end - 1, ustring)

        off = next_off

def find_hunks(pe, print=print):
    print(txt_scanning)
    rdata = get_rdata(pe)
    possible_hunks = []
    found_hunks = []
    for off, mx, padding, string in iter_pe_strings(rdata):
        # print('%08x (%i, %i): %s' % (off, mx, padding, string))

        last_hunks, possible_hunks = possible_hunks, []

        for hunk in last_hunks:
            (hunk, match) = hunk.scan(string, rdata.PointerToRawData + off)
            if hunk:
                if match:
                    found_hunks.append(hunk)
                    #print('--MATCH CONFIRMED--')
                else:
                    possible_hunks.append(hunk)
                    #print('--MATCH SCANNING--')
            else:
                #print('--NO MATCH--')
                pass

        for hunk in patch_hunks:
            match = hunk.scan(string, rdata.PointerToRawData + off)
            if match is not None:
                #print('--MATCH START--')
                possible_hunks.append(match)
    return found_hunks

def _apply_patch(filename, fn, print=print):
    try:
        hunks = find_hunks(pefile.PE(filename), print=print)
        fd = open(filename, 'rb+')
        for hunk in hunks:
            fn(hunk, fd)
        fd.close()
    except IOError as e:
        print(txt_err % (e.__class__.__name__, str(e)))
    else:
        print(txt_success)

def apply_patch(filename, print=print):
    return _apply_patch(filename, HunkMatch.apply_patch, print=print)

def remove_patch(filename, print=print):
    return _apply_patch(filename, HunkMatch.remove_patch, print=print)

def check_status(filename):
    import miaspatch

    try:
        hunks = find_hunks(pefile.PE(filename), print=print)
    except IOError as e:
        print(txt_err % (e.__class__.__name__, str(e)))
        return miaspatch.STATUS_NOT_INSTALLABLE
    if all([ x.english for x in hunks ]):
        return miaspatch.STATUS_NOT_INSTALLED
    if all([ x.translated for x in hunks ]):
        return miaspatch.STATUS_INSTALLED
    return miaspatch.STATUS_OLD_VERSION

def init(config):
    translation = config.get('DEFAULT', 'exe_translation')
    load_translation(open(translation, 'r'))

def dump_pe_strings(pe):
    rdata = get_rdata(pe)
    for off, mx, padding, string in iter_pe_strings(rdata):
        print('%08x (%i, %i): %s' % (off, mx, padding, string))

if __name__ == '__main__':
    import sys
    exe = len(sys.argv) > 1 and sys.argv[1] or 'Miasmata.exe'
    if len(sys.argv) > 2:
        load_translation(open(sys.argv[2], 'r'))
    else:
        load_translation(open('translate_exe_template.json', 'r'))

    dump_pe_strings(pefile.PE(exe))

    #hunks = find_hunks(pefile.PE(exe))
    #print([(x.english, x.translated) for x in hunks])

    #apply_patch(exe)

    #remove_patch(exe)

# vi:noexpandtab:sw=4:ts=4
