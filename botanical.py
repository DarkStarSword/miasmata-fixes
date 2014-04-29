#!/usr/bin/env python

from __future__ import print_function

from PySide import QtGui
from mmap import *

name = QtGui.QApplication.translate('Patch names', 'Botanical Bad A** fix', None, QtGui.QApplication.UnicodeUTF8)
version = '1.0'

class PatchFailed(Exception): pass

def apply_patch(filename, print=print):
    f = open(filename, 'rb+')
    m = mmap(f.fileno(), 0, access=ACCESS_WRITE)
    print('Searching for bug...')
    journal_allnotes = m.find('journal_allnotes')
    if journal_allnotes < 8:
        print('Unable to locate string "journal_allnotes"')
        raise PatchFailed()
    bug = m[journal_allnotes - 8, journal_allnotes]
    print(repr(bug))
    if buf == 'plants\0\0':
        print('The game has already been patched')
        return
    if buf != 'plant\0\0\0':
        print('Unable to locate bugged string')
        raise PatchFailed()
    m[journal_allnotes - 8, journal_allnotes] = 'plants\0\0'
    rc = m.flush()
    m.close()
    f.close()
    if os.name == 'nt' and rc == 0:
        # Who the fuck thought it was a good idea to have practically opposite
        # semantics for mmap.flush on Windows vs Unix? At least the Unix case
        # raises an Exception if it fails -- you know, like Python should do?
        print('Error flushing changes to %s!' % filename)
        raise PatchFailed()

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    apply_patch(filename)
