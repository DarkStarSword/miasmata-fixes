#!/usr/bin/env python

import sys, os
from glob import glob
import ConfigParser
import time

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import miasutil
import rs5archive
import rs5mod
import data

from ui_utils import catch_error

STATUS_NOT_INSTALLABLE = 0
STATUS_NOT_INSTALLED   = 1
STATUS_OLD_VERSION     = 2
STATUS_INSTALLED       = 3
STATUS_NEWER_VERSION   = 4

status_old_version = QtGui.QApplication.translate('Mod Status', 'Old version installed', None, QtGui.QApplication.UnicodeUTF8)
status_version_installed = QtGui.QApplication.translate('Mod Status', 'Version {0} installed', None, QtGui.QApplication.UnicodeUTF8)
status_installed = QtGui.QApplication.translate('Mod Status', 'Installed', None, QtGui.QApplication.UnicodeUTF8)
status_not_installed = QtGui.QApplication.translate('Mod Status', 'Not installed', None, QtGui.QApplication.UnicodeUTF8)
status_not_installable = QtGui.QApplication.translate('Mod Status', 'Unable to install', None, QtGui.QApplication.UnicodeUTF8)

status_txt = {
	STATUS_NOT_INSTALLABLE: (status_not_installable, Qt.red),
	STATUS_NOT_INSTALLED:   (status_not_installed, None),
	STATUS_OLD_VERSION:     (status_old_version, None),
	STATUS_INSTALLED:       (status_installed, Qt.darkGreen),
	STATUS_NEWER_VERSION:   (status_installed, Qt.darkGreen),
}

class Mod(object):
	installable = False
	install = False
	version = None
	status = None
	status_colour = None

	def update_status(self, status, version=None):
		(self.status, self.status_colour) = status_txt[status]
		if version is not None:
			self.status = status_version_installed.format(version)
		self.installable = status != STATUS_NOT_INSTALLABLE
		self.install = (status in (STATUS_NOT_INSTALLED, STATUS_OLD_VERSION))

	def __lt__(self, other):
		return self.name < other.name

	def install_mod(self, *args, **kwargs):
		raise NotImplementedError()
	def remove_mod(self, *args, **kwargs):
		raise NotImplementedError()

class BinMod(Mod):
	def __init__(self, mod, exe_filename):
		self.mod = mod
		self.exe_filename = exe_filename
		self.refresh()

	def refresh(self):
		self.update_status(self.mod.check_status(self.exe_filename))

	def print_cb(self, callback):
		def foo(msg):
			callback(msg='%s: %s' % (self.name, msg))
		return foo

	@catch_error
	def install_mod(self, progress_cb):
		self.mod.apply_patch(self.exe_filename, self.print_cb(progress_cb))

	@catch_error
	def remove_mod(self, progress_cb):
		self.mod.remove_patch(self.exe_filename, self.print_cb(progress_cb))

	@property
	def name(self):
		return self.mod.name
	@property
	def version(self):
		return self.mod.version

class EnvMod(Mod):
	installable = True

	def __init__(self, path):
		self.name = '%s (env)' % os.path.splitext(os.path.basename(path))[0]
		self.mod = data.json_decode_diff(open(path, 'rb'))
		if 'version' in self.mod:
			self.version = self.mod['version']

class Rs5Mod(Mod):
	installable = True

	def __init__(self, path):
		self.rs5 = rs5archive.Rs5ArchiveDecoder(open(path, 'rb'))
		self.name = '%s (main.rs5)' % rs5mod.get_mod_name(self.rs5, path)
		self.version = rs5mod.get_mod_version(self.rs5)

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
				1: mod.version,
				2: mod.status,
			}.get(index.column(), None)
		# if role == Qt.ToolTipRole:
		if role == Qt.ForegroundRole:
			if index.column() == 2 and mod.status_colour is not None:
				return QtGui.QBrush(mod.status_colour)
			if not mod.installable:
				return QtGui.QBrush(Qt.gray)
		if role == Qt.CheckStateRole:
			if index.column() == 0 and mod.installable:
				return mod.install and Qt.CheckState.Checked or Qt.CheckState.Unchecked

	def setData(self, index, value, role = Qt.EditRole):
		if role == Qt.CheckStateRole:
			mod = self.patch_list[index.row()]
			mod.install = value == Qt.CheckState.Checked and True or False
			self.dataChanged.emit(index, index)
			return True
		return False

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			return {
				0: self.tr('Mod'),
				1: self.tr('Version'),
				2: self.tr('Status'),
			}[section]

	def flags(self, index):
		if not index.isValid():
			return
		mod = self.patch_list[index.row()]
		flags = Qt.ItemIsEnabled
		if index.column() == 0 and mod.installable:
			return flags | Qt.ItemIsUserCheckable
		return flags

	def refresh(self):
		for (i, mod) in enumerate(self.patch_list):
			try:
				mod.refresh()
				start = self.createIndex(i, 0)
				end = self.createIndex(i, self.columnCount(None))
				self.dataChanged.emit(start, end)
			except (NotImplementedError, AttributeError):
				pass

	def __getitem__(self, item):
		return self.patch_list[item]

	def __len__(self):
		return len(self.patch_list)

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
			patches = config.get('DEFAULT', 'binary_patches')
		except:
			pass
		else:
			exe_path = os.path.join(self.install_path, 'Miasmata.exe')
			for patch in patches.split():
				mod = __import__(patch)
				patch_list.append(BinMod(mod, exe_path))

		self.patch_list = PatchListModel(sorted(patch_list))
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

	def progress(self, percent=None, msg=None):
		if percent is not None:
			self.ui.progress.setValue(percent)
		if msg is not None:
			print msg
			self.ui.lbl_progress.setText(msg)
			self.ui.lbl_progress.repaint()
			self.repaint()

        @QtCore.Slot()
        @catch_error
	def on_patch_game_clicked(self):
		self.progress(percent=0, msg=self.tr('Patching game...'))
		for mod in self.patch_list:
			if mod.install:
				mod.install_mod(self.progress)
		self.patch_list.refresh()
		self.progress(percent=100, msg=self.tr('Game patched'))

        @QtCore.Slot()
        @catch_error
	def on_remove_all_mods_clicked(self):
		self.progress(percent=0, msg=self.tr('Removing all mods...'))
		for mod in self.patch_list:
			try:
				mod.remove_mod(self.progress)
			except:
				pass
		self.patch_list.refresh()
		self.progress(percent=100, msg=self.tr('Mods removed'))

def start_gui_process(pipe=None):
	global config

	# HACK TO WORK AROUND CRASH ON CONSOLE OUTPUT WITH BBFREEZE GUI_ONLY
	sys.stdout = sys.stderr = open('miaspatch.log', 'a')
	print time.asctime()

	# Try to get some more useful info on crashes:
	import faulthandler
	faulthandler.enable()

	app = QtGui.QApplication(sys.argv)

	config = ConfigParser.RawConfigParser()
	config.read('miaspatch.cfg')
	try:
		language = config.get('DEFAULT', 'language')
	except:
		pass
	else:
		translator = QtCore.QTranslator()
		translator.load('miaspatch_i18l/%s' % language)
		app.installTranslator(translator)

	window = MiasPatch()
	window.show()
	app.exec_()
	del window

if __name__ == '__main__':
	start_gui_process()

# vi:noexpandtab:sw=8:ts=8
