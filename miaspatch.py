#!/usr/bin/env python

import sys, os
from glob import glob

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import miasutil
import rs5archive
import rs5mod
import data

from ui_utils import catch_error

class Mod(object):
	type = None
	install = False
	version = None

class BinMod(Mod):
	type = 'exe'

	def __init__(self, mod):
		self.mod = mod

	@property
	def name(self):
		return self.mod.name
	@property
	def version(self):
		return self.mod.version

class EnvMod(Mod):
	type = 'env'

	def __init__(self, path):
		self.name = os.path.splitext(os.path.basename(path))[0]
		self.mod = data.json_decode_diff(open(path, 'rb'))
		if 'version' in self.mod:
			self.version = self.mod['version']

class Rs5Mod(Mod):
	type = 'rs5'

	def __init__(self, path):
		self.rs5 = rs5archive.Rs5ArchiveDecoder(open(path, 'rb'))
		self.name = rs5mod.get_mod_name(self.rs5, path)
		self.version = rs5mod.get_mod_version(self.rs5)
		print self.version

class PatchListModel(QtCore.QAbstractTableModel):
	def __init__(self, patch_list):
		QtCore.QAbstractTableModel.__init__(self)
		self.patch_list = patch_list

	def rowCount(self, parent):
		return len(self.patch_list)

	def columnCount(self, parent):
		return 3

	def data(self, index, role):
		mod = self.patch_list[index.row()]
		if role == Qt.DisplayRole:
			return {
				0: mod.name,
				1: mod.type,
				2: mod.version,
			}.get(index.column(), None)
		# if role == Qt.ToolTipRole:
		if role == Qt.CheckStateRole:
			if index.column() == 0:
				return mod.install and Qt.CheckState.Checked or Qt.CheckState.Unchecked

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			return {
				0: self.tr('Mod'),
				1: self.tr('Type'),
				2: self.tr('Version'),
			}[section]

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
			patch_list.append(Rs5Mod(path))
		for path in glob('*.miasmod'):
			patch_list.append(EnvMod(path))
		try:
			mod = __import__('botanical')
		except:
			pass
		else:
			patch_list.append(BinMod(mod))

		self.patch_list = PatchListModel(patch_list)
		self.ui.patch_list.setModel(self.patch_list)
		self.resize_patch_list()

	def resize_patch_list(self):
		self.ui.patch_list.resizeRowsToContents()
		self.ui.patch_list.resizeColumnsToContents()

		def sizeHint():
			# Seems to be a fairly common use case, darned if I
			# know why Qt doesn't support this in an easier manner.

			# This seems to return a bogus size:
			# size = self.ui.patch_list.maximumViewportSize()

			head_size = self.ui.patch_list.horizontalHeader().size()
			# hbar_size = self.ui.patch_list.horizontalScrollBar().size()
			width = self.ui.patch_list.frameWidth()*2
			height = width + head_size.height() # + hbar_size.height()
			for row in range(self.patch_list.rowCount(None)):
				height += self.ui.patch_list.rowHeight(row)
			for col in range(self.patch_list.columnCount(None)):
				width += self.ui.patch_list.columnWidth(col)
			return QtCore.QSize(width, height)
		self.ui.patch_list.minimumSizeHint = sizeHint
		self.ui.patch_list.updateGeometry()

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
