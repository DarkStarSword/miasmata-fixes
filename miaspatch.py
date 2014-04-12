#!/usr/bin/env python

import sys, os
from glob import glob

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import miasutil
import rs5archive

from ui_utils import catch_error

class PatchListModel(QtCore.QAbstractTableModel):
	def __init__(self, patch_list):
		QtCore.QAbstractTableModel.__init__(self)
		self.patch_list = patch_list

	def rowCount(self, parent):
		return len(self.patch_list)

	def columnCount(self, parent):
		return 2

	def data(self, index, role):
		patch = self.patch_list[index.row()]
		if role == Qt.DisplayRole:
			if index.column() == 1:
				return patch
		# if role == Qt.ToolTipRole:
		if role == Qt.CheckStateRole:
			if index.column() == 0:
				return Qt.CheckState.Checked

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			if section == 0:
				return 'Install'
			if section == 1:
				return 'Mod Path'

	def flags(self, index):
		if not index.isValid():
			return
		flags = Qt.ItemIsEnabled
		if index.column() == 0:
			return flags | Qt.ItemIsUserCheckable
		return flags

class MiasPatch(QtGui.QDialog):
	from miaspatch_ui import Ui_Dialog
	def __init__(self, parent=None):
		super(MiasPatch, self).__init__(parent)

		self.ui = self.Ui_Dialog()
		self.ui.setupUi(self)

		self.find_install_path()

	def process_install_path(self, path):
		self.ui.groupBox.setEnabled(False)

		def bad_install_path(file):
			dialog = QtGui.QMessageBox()
			dialog.setWindowTitle(self.tr('Miasmata Patcher'))
			dialog.setIcon(QtGui.QMessageBox.Warning)
			dialog.setText(self.tr('{0} does not appear to be a Miasmata install: {1} not found').format(path, file))
			return dialog.exec_()

		for file in ('main.rs5', 'Miasmata.exe'):
			if not os.path.exists(os.path.join(path, file)):
				return bad_install_path(file)

		self.install_path = path
		self.ui.install_path.setText(path)
		self.ui.groupBox.setEnabled(True)
		self.enumerate_patches()

	def enumerate_patches(self):
		patch_list = []
		for path in glob('*.rs5mod'):
			patch_list.append(path)
		for path in glob('*.miasmod'):
			patch_list.append(path)

		self.patch_list = PatchListModel(patch_list)
		self.ui.patch_list.setModel(self.patch_list)
		self.ui.patch_list.resizeColumnsToContents()

        @QtCore.Slot()
        @catch_error
        def on_browse_clicked(self):
		dialog = QtGui.QFileDialog(self,
                            caption = self.tr("Select Miasmata Install Location..."))
		dialog.setFileMode(QtGui.QFileDialog.Directory)
		if not dialog.exec_():
			return
		path = dialog.selectedFiles()[0]
		self.process_install_path(path)

        @QtCore.Slot()
        @catch_error
	def on_install_path_returnPressed(self):
		path = self.ui.install_path.text()
		self.process_install_path(path)

	def find_install_path(self):
		try:
			path = miasutil.find_miasmata_install()
		except Exception as e:
			return self.on_browse_clicked()
		self.process_install_path(path)

        @QtCore.Slot()
        @catch_error
	def on_change_mods_clicked(self):
		raise Exception('change mods clicked')

        @QtCore.Slot()
        @catch_error
	def on_patch_game_clicked(self):
		raise Exception('patch game clicked')

        @QtCore.Slot()
        @catch_error
	def on_remove_all_mods_clicked(self):
		raise Exception('remove all mods clicked')

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
