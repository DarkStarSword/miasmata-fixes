#!/usr/bin/env python

from bbfreeze import Freezer
from shutil import copyfile
from site import getsitepackages
from os import mkdir, environ, pathsep

# A necessary dll lives here, but this path isn't seen by default for some reason??
environ["PATH"] += pathsep + getsitepackages()[1] + "\\numpy\\.libs"

f = Freezer("miaschiev")
f.setIcon("miasmod.ico")
f.addScript("miaschiev.pyw", gui_only=True)
f()
mkdir("./miaschiev/imageformats")
copyfile("./miasmod.ico", "./miaschiev/imageformats/miasmod.ico")
copyfile(getsitepackages()[1] + "\\PySide\\plugins\\imageformats\\qico4.dll", "./miaschiev/imageformats/qico4.dll")

# vi:noexpandtab:sw=8:ts=8
