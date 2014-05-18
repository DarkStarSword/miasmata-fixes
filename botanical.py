#!/usr/bin/env python

# Fix print function for Python 2 deficiency regarding non-ascii encoded text files:
from __future__ import print_function
import utf8file
print = utf8file.print

from PySide import QtGui
from mmap import *
import os

name = QtGui.QApplication.translate('Botanical Bad A** fix', 'Botanical Bad A** fix', None, QtGui.QApplication.UnicodeUTF8)
txt_scanning = QtGui.QApplication.translate('Botanical Bad A** fix', 'Scanning Miasmata.exe...', None, QtGui.QApplication.UnicodeUTF8)
txt_already_patched = QtGui.QApplication.translate('Botanical Bad A** fix', 'The game is already patched', None, QtGui.QApplication.UnicodeUTF8)
txt_no_bug = QtGui.QApplication.translate('Botanical Bad A** fix', 'Unable to locate bug', None, QtGui.QApplication.UnicodeUTF8)
txt_success = QtGui.QApplication.translate('Botanical Bad A** fix', 'Patch successful', None, QtGui.QApplication.UnicodeUTF8)
txt_err = QtGui.QApplication.translate('Botanical Bad A** fix', 'Error writing to Miasmata.exe', None, QtGui.QApplication.UnicodeUTF8)

version = '1.0'

class PatchFailed(Exception): pass

patch = ('plant\0\0\0', 'plants\0\0')

def _apply_patch(filename, print=print, (patch_from, patch_to) = patch):
    with open(filename, 'rb+') as f:
        m = mmap(f.fileno(), 0, access=ACCESS_WRITE)
        print(txt_scanning)
        journal_allnotes = m.find('journal_allnotes')
        if journal_allnotes < 8:
            print(txt_no_bug)
            raise PatchFailed()
        bug = m[journal_allnotes - 8:journal_allnotes]
        if bug == patch_to:
            print(txt_already_patched)
            return
        if bug != patch_from:
            print(txt_no_bug)
            raise PatchFailed()
        m[journal_allnotes - 8:journal_allnotes] = patch_to
        rc = m.flush()
        m.close()
    if os.name == 'nt' and rc == 0:
        # Who the fuck thought it was a good idea to have practically opposite
        # semantics for mmap.flush on Windows vs Unix? At least the Unix case
        # raises an Exception if it fails -- you know, like Python should do?
        print(txt_err)
        raise PatchFailed()
    print(txt_success)

def apply_patch(filename, print=print):
    return _apply_patch(filename, print)

def remove_patch(filename, print=print):
    return _apply_patch(filename, print, reversed(patch))

def check_status(filename):
    import miaspatch

    with open(filename, 'rb') as f:
        m = mmap(f.fileno(), 0, access=ACCESS_READ)
        journal_allnotes = m.find('journal_allnotes')
        if journal_allnotes < 8:
            m.close()
            return miaspatch.STATUS_NOT_INSTALLABLE
        bug = m[journal_allnotes - 8:journal_allnotes]
        m.close()
        if bug == patch[0]:
            return miaspatch.STATUS_NOT_INSTALLED
        if bug == patch[1]:
            return miaspatch.STATUS_INSTALLED
        return miaspatch.STATUS_NOT_INSTALLABLE

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    apply_patch(filename)
