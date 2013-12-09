#!/usr/bin/env python

from bbfreeze import Freezer
f = Freezer("miaschiev")
f.addScript("miaschiev.pyw", gui_only=True)
f()
