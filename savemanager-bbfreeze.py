#!/usr/bin/env python

from bbfreeze import Freezer
f = Freezer("miasmata-save-manager")
f.addScript("savemanager.pyw", gui_only=True)
f()
