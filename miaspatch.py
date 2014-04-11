#!/usr/bin/env python

import sys, os
from glob import glob

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import miasutil
import rs5archive

from ui_utils import catch_error

class MiasPatch(QtGui.QDialog):
	from miaspatch_ui import Ui_Dialog
	def __init__(self, parent=None):
		super(MiasPatch, self).__init__(parent)

		self.ui = self.Ui_Dialog()
		self.ui.setupUi(self)

		self.find_install_path()

        @QtCore.Slot()
        @catch_error
        def on_browse_clicked(self):
		dialog = QtGui.QFileDialog(self,
                            caption = self.tr("Select Miasmata Install Location..."))
		dialog.setFileMode(QtGui.QFileDialog.Directory)
		if not dialog.exec_():
			raise ValueError('Unable to locate Miasmata Install Location')
		self.install_path = dialog.selectedFiles()[0]

	def find_install_path(self):
		try:
			self.install_path = miasutil.find_miasmata_install()
		except Exception as e:
			return self.on_browse_clicked()

def start_gui_process(pipe=None):
	# HACK TO WORK AROUND CRASH ON CONSOLE OUTPUT WITH BBFREEZE GUI_ONLY
	sys.stdout = sys.stderr = open('miaspatch.log', 'w')

	# Try to get some more useful info on crashes:
	import faulthandler
	faulthandler.enable()

	translator = QtCore.QTranslator()
	translator.load('miaspatch_i18n/fr_FR')
	app = QtGui.QApplication(sys.argv)
	app.installTranslator(translator)

	window = MiasPatch()
	window.show()
	app.exec_()
	del window

if __name__ == '__main__':
	start_gui_process()

# vi:noexpandtab:sw=8:ts=8
