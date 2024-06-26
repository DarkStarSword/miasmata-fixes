#!/usr/bin/env python

from bbfreeze import Freezer
from shutil import copyfile
from site import getsitepackages
from os import mkdir
f = Freezer("miasmod")
f.setIcon("miasmod.ico")
f.addScript("miasmod.py", gui_only=True)
# f.addScript("miasmod.py", gui_only=False)
f()
mkdir("./miasmod/imageformats")
copyfile("./miasmod.ico", "./miasmod/imageformats/miasmod.ico")
copyfile(getsitepackages()[1] + "\\PySide\\plugins\\imageformats\\qico4.dll", "./miasmod/imageformats/qico4.dll")

# vi:noexpandtab:sw=8:ts=8
