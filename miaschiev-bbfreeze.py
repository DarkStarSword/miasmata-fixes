#!/usr/bin/env python

print 'To use gui_only with bbfreeze & multiprocessing:'
print '- Prevent console output - it will crash!'
print '- multiprocessing.freeze_support()'
print '- multiprocessing.set_executable(.../py.exe)'
print '- Hack bbfreeze freezer.py to change gui_only=True for py.py'
print
print 'Press Enter...'
raw_input()

from bbfreeze import Freezer
f = Freezer("miaschiev")
f.addScript("miaschiev.pyw", gui_only=True)
# f.addScript("miaschiev.pyw", gui_only=False)
f()
