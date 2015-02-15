#!/usr/bin/env python

from __future__ import print_function
import sys

# It's about now I wish I was working with Python 3 where files opened in text
# mode can have an encoding associated with them and everything just works.
# Unfortunately I'm working with Python 2, where print assumes that any file
# that is not a real terminal is encoded in 'ascii' :(
#
# To fix this I need two things - A subclass of file that advertises a utf8
# encoding, and an overridden print function that respects the file encoding
# (which of course implies I need from __future__ import print to allow it to
# be overridden).

_orig_print = print
def print(value = None, *args, **kwargs):
	file = sys.stdout
	if 'file' in kwargs:
		file = kwargs['file']
	if value is None:
		return _orig_print(**kwargs)
	if isinstance(value, unicode):
		value = value.encode(file.encoding)
	_orig_print(value, *args, **kwargs)

class UTF8File(file):
    encoding = 'UTF-8'

    # The read/write overrides here are NOT used by print(), they're just here
    # in case I call them directly

    def write(self, str):
        if isinstance(str, unicode):
            str = str.encode(self.encoding)
        return file.write(self, str)

    def read(self, *args):
        return file.read(self, *args).decode(self.encoding)
