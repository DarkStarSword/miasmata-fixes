#!/usr/bin/env python

# Fix print function for Python 2 deficiency regarding non-ascii encoded text files:
from __future__ import print_function
import utf8file
print = utf8file.print

import sys, os
from glob import glob
import ConfigParser
import shutil
import time
import copy
import json

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import miasutil
import miasmod
import environment
import rs5archive
import rs5mod
import data

from ui_utils import catch_error

STATUS_NOT_INSTALLABLE = 0
STATUS_NOT_INSTALLED   = 1
STATUS_OLD_VERSION     = 2
STATUS_INSTALLED       = 3
STATUS_NEWER_VERSION   = 4
STATUS_DESYNC          = 5

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
			STATUS_DESYNC:          (QtGui.QApplication.translate('Mod Status', 'alocalmod.rs5 not synchronised', None, QtGui.QApplication.UnicodeUTF8), Qt.red),
		}[status]
		if version is not None:
			self.status = QtGui.QApplication.translate('Mod Status', 'Version {0} installed', None, QtGui.QApplication.UnicodeUTF8).format(version)
		self.installable = status != STATUS_NOT_INSTALLABLE
		self.install = (status in (STATUS_NOT_INSTALLED, STATUS_OLD_VERSION, STATUS_DESYNC))

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
		if v == -1:
			return self.update_status(STATUS_NEWER_VERSION, version)
		if v == 1:
			return self.update_status(STATUS_OLD_VERSION, version)
		return self.update_status(STATUS_INSTALLED, version)

	def __lt__(self, other):
		return self.name < other.name

	def install_mod(self, *args, **kwargs):
		raise NotImplementedError()

	def steps(self):
		return 1

	def __str__(self):
		return self.name

class BinMod(Mod):
	def __init__(self, mod, exe_filename):
		self.mod = mod
		self.exe_filename = exe_filename

	def refresh(self, **kwargs):
		self.update_status(self.mod.check_status(self.exe_filename))

	@catch_error
	def install_mod(self, progress_cb, **kwargs):
		self.mod.apply_patch(self.exe_filename, progress_cb)

	@catch_error
	def remove_mod(self, progress_cb):
		self.mod.remove_patch(self.exe_filename, progress_cb)

	@property
	def name(self):
		return self.mod.name
	@property
	def version(self):
		return self.mod.version

class EnvMod(Mod):
	installable = True

	def __init__(self, path):
		self.mod_name = os.path.splitext(os.path.basename(path))[0]
		self.name = '%s (env)' % self.mod_name
		self.path = path
		self.mod = data.json_decode_diff(open(path, 'rb'))
		if 'version' in self.mod:
			self.version = self.mod['version']

	def refresh(self, miasmod_global_stat = None, miasmod_installed = {}, **kwargs):
		if miasmod_global_stat is not None:
			return self.update_status(miasmod_global_stat, None)
		installed = miasmod_installed.get(self.mod_name, None)
		if installed is None:
			return self.update_status(STATUS_NOT_INSTALLED)
		self.update_status_version(installed.get('version', None))

class Rs5Mod(Mod):
	installable = True

	def __init__(self, path):
		self.rs5 = rs5archive.Rs5ArchiveDecoder(open(path, 'rb'))
		self.path = path
		self.mod_name = rs5mod.get_mod_name(self.rs5, path)
		self.name = '%s (main.rs5)' % self.mod_name
		self.version = rs5mod.get_mod_version(self.rs5)

	def refresh(self, main_rs5 = None, **kwargs):
		try:
			mod_info = rs5mod.get_mod_meta(main_rs5, self.mod_name)
		except KeyError as e:
			return self.update_status(STATUS_NOT_INSTALLED)
		self.update_status_version(rs5mod.do_get_mod_version(mod_info))

	@catch_error
	def install_mod(self, progress_cb, main_rs5 = None, **kwargs):
		rs5mod.do_add_mod(main_rs5, self.rs5, self.path, progress=progress_cb)

	def steps(self):
		return len(self.rs5)

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

	def process_install_path(self, path):
		self.ui.groupBox.setEnabled(False)

		def bad_install_path(file):
			dialog = QtGui.QMessageBox()
			dialog.setWindowTitle(self.tr('Miasmata Patcher'))
			dialog.setIcon(QtGui.QMessageBox.Warning)
			dialog.setText(self.tr('{0} does not appear to be a Miasmata install: {1} not found').format(path, file))
			return dialog.exec_()

		for file in ('main.rs5', 'environment.rs5', 'Miasmata.exe'):
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
		# TODO: Perhaps display a message about running as admin if we
		# get a permission denied IOError?

	def load_environment_rs5(self, progress=None):
		if progress is None:
			progress = self.progress
		progress(msg=self.tr('Loading environment.rs5...'))
		path = os.path.join(self.install_path, 'environment.rs5')
		self.environment = environment.parse_from_archive(path)

	def enable_install_button(self):
		self.ui.patch_game.setStyleSheet('background-color: rgb(0, 170, 0);')
		self.ui.patch_game.setEnabled(True)
	def disable_install_button(self):
		self.ui.patch_game.setStyleSheet('background-color: rgb(135, 170, 135);')
		self.ui.patch_game.setEnabled(False)
	def update_install_button(self):
		for mod in self.patch_list:
			if mod.installable and mod.install:
				return self.enable_install_button()
		self.disable_install_button()

	@QtCore.Slot()
	@catch_error
	def dataChanged(self, topLeft, bottomRight):
		self.update_install_button()

	def enumerate_rs5mod(self):
		patch_list = []

		for path in glob('*.rs5mod'):
			patch_list.append(Rs5Mod(path))

		return patch_list

	def get_miasmod_global_status(self):
		# Check for global status (no alocalmod.rs5, or out of sync)
		global_stat = None
		if not os.path.isfile(os.path.join(self.install_path, 'alocalmod.rs5')):
			return (STATUS_NOT_INSTALLED, {})
		return self.check_installed_miasmods()

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
		self.progress(percent=0)
		patch_list.extend(self.enumerate_rs5mod())
		self.progress(percent=3)
		patch_list.extend(self.enumerate_miasmod())
		self.progress(percent=6)
		patch_list.extend(self.enumerate_bin_patch())
		self.progress(percent=9)

		self.patch_list = PatchListModel(sorted(patch_list))
		self.patch_list.dataChanged.connect(self.dataChanged)
		self.ui.patch_list.setModel(self.patch_list)
		self.resize_patch_list()

		self.progress(percent=20)
		self.load_main_rs5()
		self.progress(percent=50)
		self.load_environment_rs5()
		self.progress(percent=80)
		self.refresh_patch_list()
		self.progress(percent=100)

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

	def progress(self, msg=None, percent=None):
		if percent is not None:
			self.ui.progress.setValue(percent)
		if msg is not None:
			print(msg)
			self.ui.lbl_progress.setText(msg)
			self.ui.lbl_progress.repaint()
			self.repaint()

	def progress_extra(self, prefix='', min=0, max=100, progress=None):
		if progress is None:
			progress = self.progress
		def foo(msg=None, percent=None):
			if msg is not None:
				msg = '%s%s' % (prefix, msg)
			if percent is not None:
				percent = int(min + percent * (max - min) / 100)
			progress(msg=msg, percent=percent)
		progress(percent=min)
		return foo

	def delete_files(self, files):
		for file in files:
			path = os.path.join(self.install_path, file)
			if os.path.isfile(path):
				self.progress(msg = self.tr('Removing {0}...').format(path))
				try:
					os.remove(path)
				except Exception as e:
					self.progress(msg = self.tr('{0} occurred while removing {1}: {2}').format(e.__class__.__name__, path, str(e)))

	def delete_files_from_config(self):
		try:
			delete = config.get('DEFAULT', 'delete')
		except:
			return
		return self.delete_files(delete.split())

	def refresh_patch_list(self):
		(global_stat, installed) = self.get_miasmod_global_status()
		self.patch_list.refresh(main_rs5 = self.main_rs5, miasmod_global_stat = global_stat, miasmod_installed = installed)
		self.update_install_button()
		self.resize_patch_list()
		self.progress(percent=0, msg=self.tr('Ready'))

	@catch_error
	def install_bin_mods(self, progress):
		mods = filter(lambda x: x.install and isinstance(x, BinMod), self.patch_list)
		steps = len(mods)
		for (i, mod) in enumerate(mods):
			p = self.progress_extra('%s: ' % mod.name, min=i*100/steps, max=(i+1)*100/steps, progress=progress)
			mod.install_mod(p, main_rs5 = self.main_rs5)

	@catch_error
	def install_rs5_mods(self, progress):
		mods = filter(lambda x: x.install and isinstance(x, Rs5Mod), self.patch_list)
		if len(mods) == 0:
			return

		rs5mod.do_add_undo(self.main_rs5, progress=progress)

		steps = sum([x.steps() for x in mods]); i = 0
		for mod in mods:
			p = self.progress_extra('%s: ' % mod.name, min=i*100/steps, max=(i+mod.steps())*100/steps, progress=progress)
			mod.install_mod(p, main_rs5 = self.main_rs5)
			i += mod.steps()

		try:
			prefix_order = config.get('DEFAULT', 'prefix_order').split()
		except:
			pass
		else:
			print('Prefixing mod order with: {0}'.format(prefix_order))
			try:
				order = rs5mod.ModOrderDecoder(self.main_rs5)
			except Exception as e:
				order = []
			print('Old mod order: {0}'.format(order))
			for mod in reversed(prefix_order):
				try:
					order.remove(mod)
				except ValueError:
					pass
				order.insert(0, mod)
			print('New mod order: {0}'.format(order))
			rs5mod.do_order_mods(self.main_rs5, order)

		progress(msg=self.tr('Applying main.rs5 mod order...'))
		rs5mod.apply_mod_order(self.main_rs5)
		self.main_rs5.save(progress=progress)
		self.main_rs5.truncate_eof()

	@catch_error
	def get_installed_miasmods(self):
		installed = glob(os.path.join(self.install_path, '*.miasmod'))
		mods = dict([ (os.path.splitext(os.path.basename(path))[0], path) for path in installed ])

		# Disregard ignored mods in miasmod.conf if it exists
		mod_states_path = miasmod.conf_path(self.install_path)
		mod_states = None
		try:
			mod_states = json.load(open(mod_states_path, 'rb'))
		except:
			pass
		else:
			for mod in mods.copy():
				if mod in mod_states and not mod_states[mod]:
					del mods[mod]
		return (mods, mod_states)

	@staticmethod
	def miasmod_order(mods):
		# Maintain order consistent with MiasMod, i.e.:
		# environment.rs5, communitypatch.miasmod, sorted(*.miasmod), alocalmod.miasmod
		order = sorted(mods)
		if 'communitypatch' in order:
			order.remove('communitypatch')
			order.insert(0, 'communitypatch')
		if 'alocalmod' in order:
			order.remove('alocalmod')
			order.append('alocalmod')
		return order

	def process_miasmods(self, mods, order, copy_mods, progress, env=None):
		if env is None:
			env = copy.deepcopy(self.environment)
		installed = {}

		steps = len(order)
		for (i, mod) in enumerate(order):
			progress(percent = i * 100 / steps, msg = self.tr('Processing {0}...').format(mod))

			path = mods[mod]
			if isinstance(path, EnvMod):
				assert(copy_mods)
				try:
					shutil.copyfile(path.path, os.path.join(self.install_path, '%s.miasmod' % mod))
				except:
					progress(msg=self.tr('{0} occurred while copying {1}: {2}').format(e.__class__.__name__, path.path, str(e)))
				path = path.path
			diff = data.json_decode_diff(open(path, 'rb'))
			try:
				data.apply_diff(env, diff)
			except:
				progress(msg=self.tr('{0} occurred while processing {1}: {2}').format(e.__class__.__name__, path, str(e)))
			else:
				name = os.path.splitext(os.path.basename(path))[0]
				installed[name] = diff
		progress(percent=100)
		return (env, installed)

	def check_installed_miasmods(self):
		(mods, mod_states) = self.get_installed_miasmods()
		order = self.miasmod_order(mods)
		self.progress(msg=self.tr('Processing installed miasmod files...'))

		# Check for deprecated communitypatch.rs5 - if it exists use it
		# to check if alocalmod.rs5 is synchronised
		env=None
		path = os.path.join(self.install_path, 'communitypatch.rs5')
		if os.path.isfile(path):
			env = environment.parse_from_archive(path)

		(env, installed) = self.process_miasmods(mods, order, False, self.progress, env)

		self.progress(msg=self.tr('Loading alocalmod.rs5...'))
		path = os.path.join(self.install_path, 'alocalmod.rs5')
		alocalmod = environment.parse_from_archive(path)

		if env != alocalmod:
			self.progress(msg=self.tr('alocalmod.rs5 is out of sync'))
			return (STATUS_DESYNC, installed)
		return (None, installed)

	@catch_error
	def install_env_mods(self, progress):
		bundled_mods = filter(lambda x: x.install and isinstance(x, EnvMod), self.patch_list)

		(mods, mod_states) = self.get_installed_miasmods()
		if len(mods) and not os.path.isfile(os.path.join(self.install_path, 'alocalmod.rs5')):
			# If alocalmod.rs5 does not exist we only want to
			# enable the mods we are installing now (if the user
			# wants any more they can use miasmod), so explictly
			# disable all installed mods.
			print('No alocalmod.rs5 - disabling all installed miasmods')
			print('Old mod states:', mod_states)
			mod_states.update(dict(zip(mods.keys(), [False]*len(mods))))

			# Keep alocalmod.miasmod if it exists - it should
			# always be enabled and we don't want to wipe out any
			# local changes.
			del mod_states['alocalmod']
			print('New mod states:', mod_states)
			if 'alocalmod' in mods:
				mods = {'alocalmod': mods['alocalmod']}
			else:
				mods = {}

		# Enable bundled mods we are installing in MiasMod
		if mod_states is not None:
			for mod in bundled_mods:
				mod_states[mod.mod_name] = True
			try:
				mod_states_path = miasmod.conf_path(self.install_path)
				json.dump(mod_states, open(mod_states_path, 'wb'), ensure_ascii=True)
			except IOError:
				progress(msg = self.tr('{0} occurred while writing to {1}: {2}').format(e.__class__.__name__, mod_states_path, str(e)))

		for mod in bundled_mods:
			mods[mod.mod_name] = mod
		if 'alocalmod' not in mods:
			# Create a blank alocalmod.miasmod so that MiasMod
			# knows the state that alocalmod.rs5 is in and doesn't
			# need to ask the user
			diff = data.null_diff()
			path = os.path.join(self.install_path, 'alocalmod.miasmod')
			data.json_encode_diff(data.null_diff(), open(path, 'wb'))

		order = self.miasmod_order(mods)

		print('Using these miasmod files:')
		print('\n'.join(map(str, mods.itervalues())))
		print('In this order: %s' % ' '.join(order))

		(env, installed) = self.process_miasmods(mods, order, True, progress)
		environment.encode_to_archive(env, os.path.join(self.install_path, 'alocalmod.rs5'))


        @QtCore.Slot()
        @catch_error
	def on_patch_game_clicked(self):
		self.disable_install_button()
		self.progress(percent=0, msg=self.tr('Patching game...'))

		self.delete_files_from_config()
		self.install_bin_mods(self.progress_extra(min=0, max=10))
		self.install_rs5_mods(self.progress_extra(min=10, max=90))
		self.install_env_mods(self.progress_extra(min=90, max=100))

		self.progress(percent=100, msg=self.tr('Mods installed'))
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
		self.progress(percent=33, msg=self.tr('Removing environment mods...'))
		# TODO: Maybe also remove french & communitypatch.miasmod?
		# Alternatively just mark them disabled in miasmod.conf?
		self.delete_files(('alocalmod.rs5', 'communitypatch.rs5'))
		self.progress(percent=66, msg=self.tr('Removing main.rs5 mods...'))
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
	sys.stdout = sys.stderr = utf8file.UTF8File('miaspatch.log', 'a')
	print(time.asctime())

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

	window.find_install_path()

	app.exec_()
	del window

if __name__ == '__main__':
	start_gui_process()

# vi:noexpandtab:sw=8:ts=8
