#!/usr/bin/env python

from bbfreeze import Freezer
from shutil import copyfile
from site import getsitepackages
from os import mkdir
f = Freezer("miaschiev")
f.setIcon("miasmod.ico")
f.addScript("miaschiev.pyw", gui_only=True)
f()
mkdir("./miaschiev/imageformats")
copyfile("./miasmod.ico", "./miaschiev/imageformats/miasmod.ico")
copyfile(getsitepackages()[1] + "\\PySide\\plugins\\imageformats\\qico4.dll", "./miaschiev/imageformats/qico4.dll")

# vi:noexpandtab:sw=8:ts=8
