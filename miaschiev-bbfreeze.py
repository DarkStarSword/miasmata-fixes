#!/usr/bin/env python

print 'To use gui_only with bbfreeze:'
print '- Prevent console output - it will crash!'
print
print 'Press Enter...'
raw_input()

from bbfreeze import Freezer
f = Freezer("miaschiev")
f.addScript("miaschiev.pyw", gui_only=True)
# f.addScript("miaschiev.pyw", gui_only=False)
f()

# vi:noexpandtab:sw=8:ts=8
