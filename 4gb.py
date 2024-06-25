#!/usr/bin/env python

# Fix print function for Python 2 deficiency regarding non-ascii encoded text files:
from __future__ import print_function
import utf8file
print = utf8file.print

from PySide import QtGui
from mmap import *
import os
import struct

IMAGE_FILE_LARGE_ADDRESS_AWARE = 0x0020

name = QtGui.QApplication.translate('4GB patch', '4GB patch', None, QtGui.QApplication.UnicodeUTF8)
txt_scanning = QtGui.QApplication.translate('4GB patch', 'Scanning Miasmata.exe...', None, QtGui.QApplication.UnicodeUTF8)
txt_already_patched = QtGui.QApplication.translate('4GB patch', 'The game is already patched', None, QtGui.QApplication.UnicodeUTF8)
txt_bad_header = QtGui.QApplication.translate('4GB patch', 'Invalid PE header', None, QtGui.QApplication.UnicodeUTF8)
txt_success = QtGui.QApplication.translate('4GB patch', 'Patch successful', None, QtGui.QApplication.UnicodeUTF8)
txt_err = QtGui.QApplication.translate('4GB patch', 'Error writing to Miasmata.exe', None, QtGui.QApplication.UnicodeUTF8)

version = '1.0'

class PatchFailed(Exception): pass

# Adapted from https://github.com/pyinstaller/pyinstaller/issues/1288
def _apply_patch(filename, print=print, apply=True):
    with open(filename, 'rb+') as f:
        m = mmap(f.fileno(), 0, access=ACCESS_WRITE)
        print(txt_scanning)
        # Get PE header location
        m.seek(0x3c, 0)
        (pe_header_loc,) = struct.unpack('<H', m.read(2))
        # Get PE header, check it
        m.seek(pe_header_loc, 0)
        if m.read(4) != b'PE\0\0':
            print(txt_bad_header)
            raise PatchFailed()
        # Get Characteristics, check if IMAGE_FILE_LARGE_ADDRESS_AWARE bit is set
        charac_offset = pe_header_loc + 22
        m.seek(charac_offset, 0)
        (bits,) = struct.unpack('h', m.read(2))
        m.seek(charac_offset, 0)
        if (bits & IMAGE_FILE_LARGE_ADDRESS_AWARE) == IMAGE_FILE_LARGE_ADDRESS_AWARE:
            # Patch is installed
            if apply:
                # Do nothing if requesting installation
                print(txt_already_patched)
            else:
                # Unapply patch if we are requesting uninstallation
                bytes = struct.pack('h', (bits ^ IMAGE_FILE_LARGE_ADDRESS_AWARE))
                m.write(bytes)
        else:
            m.seek(charac_offset)
            # Patch is not installed
            if apply:
                # Apply patch if requesting installation
                bytes = struct.pack('h', (bits | IMAGE_FILE_LARGE_ADDRESS_AWARE))
                m.write(bytes)
            else:
                # Do nothing if requesting uninstallation
                print(txt_already_patched)
        rc = m.flush()
        m.close()
    if os.name == 'nt' and rc == 0:
        print(txt_err)
        raise PatchFailed()
    print(txt_success)

def apply_patch(filename, print=print):
    return _apply_patch(filename, print)

def remove_patch(filename, print=print):
    return _apply_patch(filename, print, apply=False)

def check_status(filename):
    import miaspatch

    with open(filename, 'rb') as f:
        m = mmap(f.fileno(), 0, access=ACCESS_READ)
        # Get PE header location
        m.seek(0x3c, 0)
        (pe_header_loc,) = struct.unpack('<H', m.read(2))
        # Get PE header, check it
        m.seek(pe_header_loc, 0)
        if m.read(4) != b'PE\0\0':
            m.close()
            return miaspatch.STATUS_NOT_INSTALLABLE
        # Get Characteristics, check if IMAGE_FILE_LARGE_ADDRESS_AWARE bit is set
        charac_offset = pe_header_loc + 22
        m.seek(charac_offset, 0)
        (bits,) = struct.unpack('h', m.read(2))
        m.close()
        if (bits & IMAGE_FILE_LARGE_ADDRESS_AWARE) == IMAGE_FILE_LARGE_ADDRESS_AWARE:
            return miaspatch.STATUS_INSTALLED
        else:
            return miaspatch.STATUS_NOT_INSTALLED
        return miaspatch.STATUS_NOT_INSTALLABLE

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    apply_patch(filename)
