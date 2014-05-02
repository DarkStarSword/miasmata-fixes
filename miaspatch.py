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

class Mod(object):
	installable = False
	install = False
	version = None
	status = None
	status_colour = None

	def update_status(self, status, version=None):
		(self.status, self.status_colour) = {
			STATUS_NOT_INSTALLABLE: (QtGui.QApplication.translate('Mod Status', 'Not applicable', None, QtGui.QApplication.UnicodeUTF8), None),
			STATUS_NOT_INSTALLED:   (QtGui.QApplication.translate('Mod Status', 'Not installed', None, QtGui.QApplication.UnicodeUTF8), None),
			STATUS_OLD_VERSION:     (QtGui.QApplication.translate('Mod Status', 'Old version installed', None, QtGui.QApplication.UnicodeUTF8), None),
			STATUS_INSTALLED:       (QtGui.QApplication.translate('Mod Status', 'Installed', None, QtGui.QApplication.UnicodeUTF8), Qt.darkGreen),
			STATUS_NEWER_VERSION:   (QtGui.QApplication.translate('Mod Status', 'Installed', None, QtGui.QApplication.UnicodeUTF8), Qt.darkGreen),
		}[status]
		if version is not None:
			self.status = QtGui.QApplication.translate('Mod Status', 'Version {0} installed', None, QtGui.QApplication.UnicodeUTF8).format(version)
		self.installable = status != STATUS_NOT_INSTALLABLE
		self.install = (status in (STATUS_NOT_INSTALLED, STATUS_OLD_VERSION))

	@staticmethod
	def cmp_version(v1, v2):
		def conv(v):
			v = v.split('.')
			for i in range(len(v)):
				try:
					v[i] = int(v[i])
				except:
					pass
			return v
		v1 = conv(v1)
		v2 = conv(v2)
		return cmp(v1, v2)

	def update_status_version(self, version):
		if version == None:
			return self.update_status(STATUS_OLD_VERSION)
		v = self.cmp_version(self.version, version)
		if v == 1:
			return self.update_status(STATUS_NEWER_VERSION, version)
		if v == -1:
			return self.update_status(STATUS_OLD_VERSION, version)
		return self.update_status(STATUS_INSTALLED, version)

	def __lt__(self, other):
		return self.name < other.name

	def install_mod(self, *args, **kwargs):
		raise NotImplementedError()

class BinMod(Mod):
	def __init__(self, mod, exe_filename):
		self.mod = mod
		self.exe_filename = exe_filename
		self.refresh()

	def refresh(self, **kwargs):
		self.update_status(self.mod.check_status(self.exe_filename))

	def print_cb(self, callback):
		def foo(msg):
			callback(msg='%s: %s' % (self.name, msg))
		return foo

	@catch_error
	def install_mod(self, progress_cb, **kwargs):
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

	def __init__(self, path, main_rs5):
		self.rs5 = rs5archive.Rs5ArchiveDecoder(open(path, 'rb'))
		self.path = path
		self.mod_name = rs5mod.get_mod_name(self.rs5, path)
		self.name = '%s (main.rs5)' % self.mod_name
		self.version = rs5mod.get_mod_version(self.rs5)
		self.refresh(main_rs5 = main_rs5)

	def refresh(self, main_rs5 = None, **kwargs):
		try:
			mod_info = rs5mod.get_mod_meta(main_rs5, self.mod_name)
		except KeyError as e:
			return self.update_status(STATUS_NOT_INSTALLED)
		self.update_status_version(rs5mod.do_get_mod_version(mod_info))

	@catch_error
	def install_mod(self, progress_cb, main_rs5 = None, **kwargs):
		rs5mod.do_add_mod(main_rs5, self.rs5, self.path)

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
			if not mod.installable:
				return QtGui.QBrush(Qt.gray)
			if index.column() == 2 and mod.status_colour is not None:
				return QtGui.QBrush(mod.status_colour)
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

	def refresh(self, **kwargs):
		for (i, mod) in enumerate(self.patch_list):
			try:
				mod.refresh(**kwargs)
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

	def load_main_rs5(self):
		self.progress(msg=self.tr('Loading main.rs5...'))
		path = os.path.join(self.install_path, 'main.rs5')
		self.main_rs5 = rs5mod.Rs5ModArchiveUpdater(open(path, 'rb+'))

	def enumerate_rs5mod(self):
		patch_list = []
		self.load_main_rs5()

		for path in glob('*.rs5mod'):
			patch_list.append(Rs5Mod(path, self.main_rs5))

		return patch_list

	def enumerate_miasmod(self):
		patch_list = []
		for path in glob('*.miasmod'):
			patch_list.append(EnvMod(path))
		return patch_list

	def enumerate_bin_patch(self):
		patch_list = []
		try:
			patches = config.get('DEFAULT', 'binary_patches')
		except:
			return []
		exe_path = os.path.join(self.install_path, 'Miasmata.exe')
		for patch in patches.split():
			mod = __import__(patch)
			patch_list.append(BinMod(mod, exe_path))
		return patch_list

	def enumerate_patches(self):
		patch_list = []
		patch_list.extend(self.enumerate_rs5mod())
		patch_list.extend(self.enumerate_miasmod())
		patch_list.extend(self.enumerate_bin_patch())

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
			cols = self.patch_list.columnCount(None)
			for col in range(cols):
				col_width = self.ui.patch_list.columnWidth(col)
				if col == cols-1 and self.ui.patch_list.horizontalHeader().stretchLastSection():
					col_width = max(col_width, self.ui.patch_list.horizontalHeader().defaultSectionSize())
				width += col_width
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

	def delete_files(self, files):
		for file in files:
			path = os.path.join(self.install_path, file)
			if os.path.isfile(path):
				self.progress(msg = self.tr('Deleting {0}...').format(path))
				try:
					os.remove(path)
				except Exception as e:
					self.progress(msg = self.tr('{0} while deleting {1}: {2}').format(e.__class__.__name__, path, str(e)))

	def delete_files_from_config(self):
		try:
			delete = config.get('DEFAULT', 'delete')
		except:
			return
		return self.delete_files(delete.split())

	def refresh_patch_list(self):
		self.patch_list.refresh(main_rs5 = self.main_rs5)

        @QtCore.Slot()
        @catch_error
	def on_patch_game_clicked(self):
		self.progress(percent=0, msg=self.tr('Patching game...'))

		self.delete_files_from_config()

		for mod in self.patch_list:
			if mod.install:
				mod.install_mod(self.progress, main_rs5 = self.main_rs5)
		# TODO: config.get('DEFAULT', 'prefix_order')
		self.progress(percent=100, msg=self.tr('Game patched'))
		self.refresh_patch_list()

        @QtCore.Slot()
        @catch_error
	def on_remove_all_mods_clicked(self):
		self.progress(percent=0, msg=self.tr('Removing all mods...'))
		for mod in self.patch_list:
			if mod.installable and hasattr(mod, 'remove_mod'):
				try:
					mod.remove_mod(self.progress)
				except:
					pass
		self.progress(percent=25, msg=self.tr('Removing environment mods...'))
		self.delete_files(('alocalmod.rs5', 'communitypatch.rs5'))
		self.progress(percent=50, msg=self.tr('Removing main.rs5 mods...'))
		try:
			rs5mod.do_revert(self.main_rs5)
		except KeyError as e:
			pass
		self.load_main_rs5()
		self.progress(percent=100, msg=self.tr('Mods removed'))
		self.refresh_patch_list()

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
		translator.load('miaspatch_i18n/%s' % language)
		app.installTranslator(translator)

	window = MiasPatch()
	window.show()
	app.exec_()
	del window

if __name__ == '__main__':
	start_gui_process()

# vi:noexpandtab:sw=8:ts=8
