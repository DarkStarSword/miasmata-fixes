#!/usr/bin/env python

# TODO:
#
# - When saving anything other than alocalmod, sync alocalmod
#   - More generally, sync to all rs5 files down the list
#
# - Play nice with rs5 archives that have other files inside them
# - Detect if saves.dat has been modified externally & ask to reload
# - Figure out why the dirty bold indicator isn't always being cleared on save.
#   Just rendering (no dataChanged emitted), or flag actually not cleared?
#   Could it be related to the undo deep copy?
#
#
# Raw data
#  - save/load file
#  - Various ways to interpret it

import sys, os
from glob import glob

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import collections
import json

import miasutil
import rs5archive
import rs5file
import rs5mod
import environment
import data

import miasmod_data

from ui_utils import catch_error

def conf_path(install_path):
	return os.path.join(install_path, 'miasmod.conf')

class ModList(object):
	class mod(object):
		def __init__(self, name, path, basename, type, note=None, include=True, version=None):
			self.rs5_name = None
			self.rs5_path = None
			self.miasmod_name = None
			self.miasmod_path = None
			self.name = name
			self.note = (None, None)
			self.include = include
			self.version = version

			self.add(path, basename, type, note, include)

		def add(self, path, basename, type, note=None, include=True, version=None):
			if type == 'rs5':
				basename = '%s/environment' % basename
			setattr(self, '%s_path' % type, path)
			setattr(self, '%s_name' % type, basename)
			self.note = note or self.note
			self.version = version or self.version
			if include is not None:
				self.include = include
		@property
		def basename(self):
			return self.miasmod_name or self.rs5_name
		@property
		def types(self):
			ret = []
			if self.miasmod_name:
				ret.append('miasmod')
			if self.rs5_name:
				ret.append('rs5')
			return ret
		@property
		def path(self):
			return self.miasmod_path or self.rs5_path

	def __init__(self):
		self.mods = collections.OrderedDict()
		self.mods_last = collections.OrderedDict()
		self.active = 'environment'

	def add(self, path, includes=None):
		basename = os.path.basename(path)
		(name, ext) = [ x.lower() for x in os.path.splitext(basename) ]
		ext = ext[1:]

		note = version = None
		if ext == 'rs5':
			if name < self.active:
				self.active = name
			if name < 'alocalmod':
				note = ('WARNING: Filename will override alocalmod.rs5!',
					'MiasMod combines mods into' \
					' alocalmod.rs5, which should come first' \
					' alphabetically to be used by Miasmata')
			if name > 'environment':
				note = ('WARNING: Filename may cause crash on load!',
					'To avoid crashes, environment.rs5' \
					' should come last alphabetically')
		else:
			diff = data.json_decode_diff(open(path, 'rb'))
			if 'version' in diff:
				version = diff['version']

		include=True
		if includes is not None and name in includes:
			include = includes[name]

		l = self.mods
		if name == 'alocalmod':
			l = self.mods_last
		if name in l:
			l[name].add(path, basename, ext, note, include, version)
		else:
			l[name] = ModList.mod(name, path, basename, ext, note, include, version)

	def extend(self, iterable, includes=None):
		for item in iterable:
			self.add(item, includes=includes)
	def __len__(self):
		return len(self.mods) + len(self.mods_last)
	def __getitem__(self, idx):
		return (self.mods.values() + self.mods_last.values())[idx]

class ModListModel(QtCore.QAbstractTableModel):
	def __init__(self, mod_list):
		QtCore.QAbstractTableModel.__init__(self)
		self.mod_list = mod_list

	def rowCount(self, parent):
		return len(self.mod_list)

	def columnCount(self, paretn):
		return 4

	def data(self, index, role):
		mod = self.mod_list[index.row()]
		if role == Qt.DisplayRole:
			if index.column() == 0:
				return mod.miasmod_name
			if index.column() == 1:
				return mod.rs5_name
			if index.column() == 2:
				return mod.version
			if index.column() == 3:
				note = mod.note[0]
				if note is None and mod.name == self.mod_list.active:
					return 'Active'
				return note
		if role == Qt.ToolTipRole:
			if index.column() == 3:
				note = mod.note[1]
				if note is None and mod.name == self.mod_list.active:
					return 'Based on the filename, Miasmata will use the environment found in this RS5 file'
				return note
		if role == Qt.ForegroundRole:
			if index.column() == 3 and mod.note[0]:
				return QtGui.QBrush(Qt.red)
		if role == Qt.FontRole:
			if index.column() == 3:
				return QtGui.QFont(None, italic=True)
		if role == Qt.CheckStateRole:
			if index.column() == 0 and \
					mod.miasmod_name is not None and \
					mod.rs5_name is None:
				return mod.include and Qt.CheckState.Checked or Qt.CheckState.Unchecked

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			if section == 0:
				return 'Environment Mods'
			if section == 1:
				return 'RS5 Files'
			if section == 2:
				return 'Version'
			if section == 3:
				return 'Notes'

	def setData(self, index, value, role = Qt.EditRole):
		if role == Qt.CheckStateRole:
			mod = self.mod_list[index.row()]
			mod.include = value == Qt.CheckState.Checked and True or False
			self.dataChanged.emit(index, index)
			return True
		return False

	def __getitem__(self, item):
		return self.mod_list[item]

	def __len__(self):
		return len(self.mod_list)

	def flags(self, index):
		if not index.isValid():
			return
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
		if index.column() == 0:
			return flags | Qt.ItemIsUserCheckable
		return flags

class Rs5ModListModel(QtCore.QAbstractTableModel):
	def __init__(self, rs5):
		QtCore.QAbstractTableModel.__init__(self)
		self.rs5 = rs5
		self.refresh()

	def refresh(self):
		try:
			mod_order = rs5mod.ModOrderDecoder(self.rs5)
		except Exception as e:
			mod_order = []
		self.mods = []
		for manifest in rs5mod.rs5_mods(self.rs5):
			name = manifest.rsplit('\\', 1)[1].rsplit('.', 1)[0]
			meta = version = None
			try:
				meta = rs5mod.get_mod_meta(self.rs5, name)
			except:
				pass
			else:
				version = rs5mod.do_get_mod_version(meta)
			order = None
			if name in mod_order:
				order = mod_order.index(name)
			self.mods.append((name, version, order))
		self.reset()

	def rowCount(self, parent):
		return len(self.mods)

	def columnCount(self, paretn):
		return 3

	def data(self, index, role):
		(name, version, order) = self.mods[index.row()]
		if role == Qt.DisplayRole:
			return {
				0: name,
				1: version,
				2: order,
			}.get(index.column(), None)

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			return {
				0: 'main.rs5 Mods',
				1: 'Version',
				2: 'Mod Order',
			}[section]

	def flags(self, index):
		if not index.isValid():
			return
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable

class MiasMod(QtGui.QMainWindow):
	from miasmod_ui import Ui_MainWindow
	def __init__(self, parent=None):
		super(MiasMod, self).__init__(parent)

		self.ui = self.Ui_MainWindow()
		self.ui.setupUi(self)

		self.ui.tabWidget.tabBar().tabButton(0, QtGui.QTabBar.RightSide).resize(0, 0)
		self.open_tabs = {}

		self.find_install_path()
		self.conf_path = conf_path(self.install_path)

		self.busy = False

	@catch_error
	def load_main_rs5(self):
		self.progress(self.tr('Loading main.rs5...'))
		path = os.path.join(self.install_path, 'main.rs5')
		self.main_rs5 = rs5mod.Rs5ModArchiveUpdater(open(path, 'rb+'))
		self.rs5_mod_list = Rs5ModListModel(self.main_rs5)
		self.ui.rs5_mod_list.setModel(self.rs5_mod_list)
		self.ui.rs5_mod_list.resizeColumnsToContents()
		self.done()

	@QtCore.Slot()
	@catch_error
	def on_revert_main_rs5_clicked(self):
		self.progress(self.tr('Removing main.rs5 mods...'))
		try:
			rs5mod.do_revert(self.main_rs5)
		except KeyError as e:
			pass
		self.load_main_rs5()

	@QtCore.Slot()
	@catch_error
	def on_install_rs5mod_clicked(self):
		path = QtGui.QFileDialog.getOpenFileName(self,
				"Select mod to install...",
				None, 'main.rs5 mods (*.rs5mod)')[0]
		if not path:
			return
		rs5 = rs5archive.Rs5ArchiveDecoder(open(path, 'rb'))
		rs5mod.do_add_one_mod(self.main_rs5, rs5, path, progress=self.progress)
		self.rs5_mod_list.refresh()
		self.done()

	def progress(self, msg=None, percent=None):
		if msg is None:
			return
		if not self.busy:
			QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
		print msg
		self.busy = True
		self.statusBar().showMessage(msg)
		self.repaint()

	def done(self):
		QtGui.QApplication.restoreOverrideCursor()
		self.busy = False
		self.statusBar().clearMessage()

	def find_install_path(self):
		try:
			self.install_path = miasutil.find_miasmata_install()
		except Exception as e:
			dialog = QtGui.QFileDialog(self,
					caption="Select Miasmata Install Location...")
			dialog.setFileMode(QtGui.QFileDialog.Directory)
			if not dialog.exec_():
				raise ValueError('Unable to locate Miasmata Install Location')
			self.install_path = dialog.selectedFiles()[0]

	@QtCore.Slot()
	@catch_error
	def on_open_saves_dat_clicked(self):
		if 'saves.dat' in self.open_tabs:
			return self.activate_tab('saves.dat')

		try:
			path = miasutil.find_miasmata_save()
		except Exception as e:
			path = 'saves.dat'
		try:
			saves = data.parse_data(open(path, 'rb'))
		except Exception as e:
			return

		saves.name = data.null_str('saves.dat')
		view = miasmod_data.MiasmataDataView(saves, sort=True, save_path = path, name='saves.dat')
		self.add_tab(view, 'saves.dat', 'saves.dat')

	def warn_bad_miasmata_path(self, path):
		dialog = QtGui.QMessageBox()
		dialog.setWindowTitle('MiasMod')
		dialog.setText("Unable to locate base rs5 file")
		dialog.setInformativeText("Please check that '%s' is the"
				" correct location of Miasmata" % path)
		return dialog.exec_()

	@QtCore.Slot()
	@catch_error
	def refresh_mod_list(self):
		mod_list = ModList()

		mod_states = None
		try:
			mod_states = json.load(open(self.conf_path, 'rb'))
		except:
			pass

		for path in sorted(glob(os.path.join(self.install_path, '*.rs5')), reverse=True):
			basename = os.path.basename(path)
			if basename.lower() == 'main.rs5':
				continue
			try:
				f = open(path, 'rb')
				archive = rs5archive.Rs5ArchiveDecoder(f)
			except:
				continue
			if 'environment' not in archive:
				continue
			mod_list.add(path)

		if not len(mod_list):
			self.warn_bad_miasmata_path(self.install_path)

		# Previously I was shipping communitypatch as an rs5 and I
		# expected it to get in the right order implicitly from the
		# above sort, however I no longer do that (and the patcher even
		# automatically deletes communitypatch.rs5 if it exists), so I
		# now set the order of the community patch explicitly here:
		path = os.path.join(self.install_path, 'communitypatch.miasmod')
		if os.path.isfile(path):
			mod_list.add(path, mod_states)

		mod_list.extend(sorted(glob(os.path.join(self.install_path, '*.miasmod'))), mod_states)

		self.mod_list = ModListModel(mod_list)
		self.mod_list.dataChanged.connect(self.dataChanged)
		self.ui.mod_list.setModel(self.mod_list)
		self.ui.mod_list.resizeColumnsToContents()

	@QtCore.Slot()
	@catch_error
	def dataChanged(self, topLeft, bottomRight):
		mod_states = { mod.name: mod.include for mod in self.mod_list }
		json.dump(mod_states, open(self.conf_path, 'wb'), ensure_ascii=True)
		# TODO: Delay this somehow, synchronise all following rs5s...
		self.synchronise_alocalmod()

	def __del__(self):
		self.ui.tabWidget.clear()
		del self.ui

	def ask_save(self, name):
		dialog = QtGui.QMessageBox()
		dialog.setWindowTitle('MiasMod')
		dialog.setText('%s has been modified, save?' % name)
		dialog.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
		dialog.setDefaultButton(QtGui.QMessageBox.Yes)
		return dialog.exec_()

	def ask_save_tab(self, tab_index):
		tab = self.ui.tabWidget.widget(tab_index)
		if tab.is_dirty():
			response = self.ask_save(self.ui.tabWidget.tabText(tab_index))
			if response == QtGui.QMessageBox.Yes:
				tab.save()
			return response

	def closeEvent(self, event):
		for i in range(1, self.ui.tabWidget.count()):
			if self.ask_save_tab(i) == QtGui.QMessageBox.Cancel:
				event.ignore()
				return
		event.accept()

	def keyPressEvent(self, event):
		if event.matches(QtGui.QKeySequence.Refresh):
			return self.refresh_mod_list()
		super(MiasMod, self).keyPressEvent(event)

	@QtCore.Slot(int)
	@catch_error
	def on_tabWidget_tabCloseRequested(self, index):
		if index == 0:
			return
		if self.ask_save_tab(index) == QtGui.QMessageBox.Cancel:
			return
		self.remove_tab(index)

	@QtCore.Slot(int)
	@catch_error
	def on_tabWidget_currentChanged(self, index):
		if index == 0:
			return self.refresh_mod_list()

	def ask_edit(self, mod, msg1, msg2, edit_mod, edit_rs5, detailed=None):
		dialog = QtGui.QMessageBox()
		dialog.setWindowTitle('MiasMod')
		dialog.setText(msg1)
		dialog.setInformativeText(msg2)
		if detailed is not None:
			dialog.setDetailedText(detailed)
		edit_mod = dialog.addButton(edit_mod, dialog.AcceptRole)
		if edit_rs5 is not None:
			edit_rs5 = dialog.addButton(edit_rs5, dialog.DestructiveRole)
		cancel = dialog.addButton(QtGui.QMessageBox.Cancel)
		dialog.exec_()
		return {
			edit_mod: 'edit_mod',
			edit_rs5: 'edit_rs5',
			cancel: 'cancel'
		}[dialog.clickedButton()]

	def confirm_edit_special_mod(self, mod):
		msg1 = 'Confirm editing %s' % mod.basename
		edit_mod = 'Edit alocalmod.miasmod'
		edit_rs5 = 'Edit %s (not recommended)' % mod.basename
		if mod.name == 'environment':
			msg2 = 'It is not recommended to directly edit' \
			' environment.rs5, rather it is suggested to work with' \
			' "miasmod" files that automatically get combined into' \
			' alocalmod.rs5/environment which is picked up by the' \
			" game. If you aren't sure you should probably edit" \
			' alocalmod.miasmod instead.\n\nWhat would you like to' \
			' do?'
		else:
			assert(mod.name == 'communitypatch')
			msg2 ='Are you sure you wish to edit the community' \
			' patch? Unless you know what you are doing you probably' \
			' should edit a local mod (e.g. alocalmod.miasmod)' \
			' instead.'

		return self.ask_edit(mod, msg1, msg2, edit_mod, edit_rs5)

	def find_diff_base(self, row):
		i = row - 1
		while i >= 0:
			mod = self.mod_list[i]
			if 'rs5' in mod.types:
				return (i, mod)
			i -= 1
		return (None, None)

	def guess_rs5_source_diffs(self, row, mod, include_cur_row):
		(diff_base_row, diff_base) = self.find_diff_base(row)
		if diff_base is None:
			return None, []
		ret = diff_base, filter(lambda x: x.include, self.mod_list[diff_base_row + 1 : row + include_cur_row])
		return ret

	def ask_generate_mod_diff(self, row, mod, open=True):
		rs5_base, include_mods = self.guess_rs5_source_diffs(row, mod, False)
		if rs5_base is None:
			return 'edit_rs5'
		sources = [rs5_base.rs5_name] + [ x.miasmod_name for x in include_mods ] + [mod.rs5_name]
		mod_name = '%s.miasmod' % mod.name

		msg1 = 'Generate %s?' % mod_name
		msg2 = 'No miasmod file exists for "%s". Would you' \
			' like to create "%s" based on the the differences' \
			' between these files?:\n\n%s' \
			% (mod.name, mod_name, '\n'.join(sources))

		# env1 = self.generate_env_from_diffs(row, mod, False)
		# env2 = environment.parse_from_archive(mod.rs5_path)
		# diff = data.diff_data(env1, env2)
		# msg3 = data.pretty_fmt_diff(data.diff_data(env1, env2), ' + '.join(sources), mod.rs5_name)
		msg3 = None

		edit_mod = 'Generate %s' % mod_name
		edit_rs5 = 'Edit %s' % mod.basename
		if not open:
			edit_rs5 = None
		return self.ask_edit(mod, msg1, msg2, edit_mod, edit_rs5, msg3)

	def ask_resolve_mod_sync(self, row, mod):
		rs5_base, include_mods = self.guess_rs5_source_diffs(row, mod, True)
		if rs5_base is None:
			raise ValueError('No preceding mods found')
		include_mods = [rs5_base.rs5_name] + [ x.miasmod_name for x in include_mods ]

		msg1 = '%s appears to be out of sync!' % mod.rs5_name
		msg2 = 'Would to like to synchronise it from the following' \
			' files?\nIf you recently installed or updated any mods' \
			' listed below, or removed a different mod, you should' \
			' choose "synchronise %s". However, if you updated %s' \
			' itself you should choose "Discard %s"\n\n%s' \
			% (mod.rs5_name, os.path.basename(mod.rs5_path),
				mod.miasmod_name, '\n'.join(include_mods))
		msg3 = mod.diff_txt
		edit_mod = 'Synchronise %s' % mod.rs5_name
		edit_rs5 = 'Discard %s' % mod.miasmod_name
		return self.ask_edit(mod, msg1, msg2, edit_mod, edit_rs5, msg3)

	def generate_env_from_diffs(self, row, mod, include_cur_row):
		rs5_base, include_mods = self.guess_rs5_source_diffs(row, mod, include_cur_row)
		env = environment.parse_from_archive(rs5_base.rs5_path)
		for m in include_mods:
			try:
				diff = data.json_decode_diff(open(m.miasmod_path, 'rb'))
			except ValueError:
				m.note = ('WARNING: Corrupt miasmod file detected!', None)
				self.ui.mod_list.resizeColumnsToContents()
				raise
			else:
				data.apply_diff(env, diff)
		return env

	def generate_env_from_single_diff(self, row, mod):
		(diff_base_row, diff_base) = self.find_diff_base(row)
		env1 = environment.parse_from_archive(diff_base.rs5_path)
		env2 = env1.copy()
		diff = data.json_decode_diff(open(mod.miasmod_path, 'rb'))
		data.apply_diff(env2, diff)
		return (env1, env2)

	def generate_mod_diff(self, row, mod):
		mod.miasmod_name = '%s.miasmod' % mod.name
		self.progress('Generating %s...' % mod.miasmod_name)
		env1 = self.generate_env_from_diffs(row, mod, False)
		env2 = environment.parse_from_archive(mod.rs5_path)
		diff = data.diff_data(env1, env2)
		mod.miasmod_path = os.path.join(self.install_path, mod.miasmod_name)
		data.json_encode_diff(diff, open(mod.miasmod_path, 'wb'))
		self.refresh_mod_list()
		self.done()

	def rs5_synched(self, row, mod):
		self.progress('Checking if %s is synched...' % mod.rs5_name)
		env1 = self.generate_env_from_diffs(row, mod, True)
		env2 = environment.parse_from_archive(mod.rs5_path)
		if env1 != env2:
			rs5_base, include_mods = self.guess_rs5_source_diffs(row, mod, True)
			sources = [rs5_base.rs5_name] + [ x.miasmod_name for x in include_mods ]
			mod.diff_txt = data.pretty_fmt_diff(data.diff_data(env2, env1), mod.rs5_name, ' + '.join(sources))
		self.done()
		return env1 == env2

	def sync_rs5(self, row, mod):
		env = self.generate_env_from_diffs(row, mod, True)
		environment.encode_to_archive(env, mod.rs5_path)
		self.refresh_mod_list()

	def add_tab(self, view, name, mod_name):
		if mod_name not in ('saves.dat', 'alocalmod'):
			view.saved.connect(self.synchronise_alocalmod)
		self.ui.tabWidget.addTab(view, unicode(name))
		self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 1)
		self.open_tabs[mod_name] = view

	def remove_tab(self, index):
		view = self.ui.tabWidget.widget(index)
		if view.name in self.open_tabs:
			del self.open_tabs[view.name]
		self.ui.tabWidget.removeTab(index)

	def activate_tab(self, mod_name):
		view = self.open_tabs[mod_name]
		tab = self.ui.tabWidget.indexOf(view)
		self.ui.tabWidget.setCurrentIndex(tab)

	def open_mod_rs5_only(self, row, mod):
		self.progress('Opening %s...' % mod.rs5_name)
		env = environment.parse_from_archive(mod.rs5_path)
		env.name = mod.rs5_name
		view = miasmod_data.MiasmataDataView(env, name = mod.name, rs5_path = mod.rs5_path, version=mod.version)
		self.add_tab(view, mod.rs5_name, mod.name)
		self.done()

	def open_mod_both(self, row, mod):
		name = '%s + %s' % (mod.miasmod_name, mod.rs5_name)
		self.progress('Opening %s...' % name)
		diff_base = self.generate_env_from_diffs(row, mod, False)
		env = environment.parse_from_archive(mod.rs5_path)
		env.name = mod.name

		view = miasmod_data.MiasmataDataView(env, name = mod.name, diff_base = diff_base, miasmod_path = mod.miasmod_path, rs5_path = mod.rs5_path, version=mod.version)
		self.add_tab(view, mod.name, mod.name)
		self.done()

	def open_mod_miasmod_only(self, row, mod):
		self.progress('Opening %s...' % mod.miasmod_name)
		(diff_base, env) = self.generate_env_from_single_diff(row, mod)
		env.name = mod.miasmod_name

		view = miasmod_data.MiasmataDataView(env, name = mod.name, diff_base = diff_base, miasmod_path = mod.miasmod_path, version=mod.version)
		self.add_tab(view, mod.miasmod_name, mod.name)
		self.done()

	def _generate_new_alocalmod(self, row):
		self.progress('Creating alocalmod...')

		path = os.path.join(self.install_path, 'alocalmod.miasmod')
		mod = ModList.mod('alocalmod', path, os.path.basename(path), 'miasmod')
		path = os.path.join(self.install_path, 'alocalmod.rs5')
		mod.add(path, os.path.basename(path), 'rs5')

		env = self.generate_env_from_diffs(row, mod, True)
		# self.done() - Caller must clear status!

		return (row, mod, env)

	def generate_new_alocalmod(self):
		row = len(self.mod_list) - 1
		mod = self.mod_list[row]
		if mod.name == 'alocalmod':
			return (row, mod, None)

		# Does not exist at all, create it:
		return self._generate_new_alocalmod(row + 1)

	@QtCore.Slot()
	@catch_error
	def open_alocalmod(self):
		if 'alocalmod' in self.open_tabs:
			return self.activate_tab('alocalmod')

		(row, mod, env1) = self.generate_new_alocalmod()
		if env1 is None: # Exists
			return self.open_mod(row)

		env2 = env1.copy()
		env2.name = 'alocalmod'

		view = miasmod_data.MiasmataDataView(env2, name = mod.name, diff_base = env1, miasmod_path = mod.miasmod_path, rs5_path = mod.rs5_path)
		self.add_tab(view, mod.name, mod.name)
		self.done()

	@QtCore.Slot()
	@catch_error
	def synchronise_alocalmod(self):
		self.refresh_mod_list()
		if not len(self.mod_list):
			return

		(row, mod, env) = self.generate_new_alocalmod()
		if mod.rs5_path is None: # miasmod exists, but rs5 does not
			(row, mod, env) = self._generate_new_alocalmod(row)
		elif env is None: # Exists
			return self.open_mod(row, open=False)
		else:
			diff = data.diff_data(env, env)
			data.json_encode_diff(diff, open(mod.miasmod_path, 'wb'))
		environment.encode_to_archive(env, mod.rs5_path)
		self.refresh_mod_list()
		self.done()

	@QtCore.Slot()
	@catch_error
	def on_new_mod_clicked(self):
		(path, filter) = QtGui.QFileDialog.getSaveFileName(self,
			caption="New Miasmata mod...",
			dir=self.install_path,
			filter="MiasMod files (*.miasmod)")
		if not path:
			return
		basename = os.path.basename(path)
		(name, ext) = os.path.splitext(basename)

		row = len(self.mod_list)
		mod = self.mod_list[row - 1]
		if mod.name == 'alocalmod':
			row -= 1
		(diff_base_row, diff_base) = self.find_diff_base(row)

		env1 = environment.parse_from_archive(diff_base.rs5_path)
		env2 = env1.copy()
		env2.name = basename

		# TODO: on tab changed / window got focus - refresh_mod_list()

		view = miasmod_data.MiasmataDataView(env2, name = name, diff_base = env1, miasmod_path = path)
		self.add_tab(view, name, name)
		self.done()

	@QtCore.Slot(QtCore.QModelIndex)
	@catch_error
	def on_mod_list_activated(self, index):
		row = index.row()
		return self.open_mod(row)

	def open_mod(self, row, open=True):
		mod = self.mod_list[row]

		if open and mod.name in self.open_tabs:
			return self.activate_tab(mod.name)

		if mod.name in ('environment', 'communitypatch'):
			answer = self.confirm_edit_special_mod(mod)
			if answer == 'cancel':
				return
			if answer == 'edit_mod':
				return self.open_alocalmod()

		if 'miasmod' not in mod.types: # rs5 only
			answer = self.ask_generate_mod_diff(row, mod, open)
			if answer == 'cancel':
				return
			if answer == 'edit_mod':
				self.generate_mod_diff(row, mod)
				return open and self.open_mod_both(row, mod)
			return open and self.open_mod_rs5_only(row, mod)

		if 'rs5' in mod.types: # Both rs5 + miasmod
			if not self.rs5_synched(row, mod):
				answer = self.ask_resolve_mod_sync(row, mod)
				if answer == 'cancel':
					return
				if answer == 'edit_rs5':
					self.generate_mod_diff(row, mod)
					return open and self.open_mod_both(row, mod)
				self.sync_rs5(row, mod)
			return open and self.open_mod_both(row, mod)

		# miasmod only
		return open and self.open_mod_miasmod_only(row, mod)


def start_gui_process(pipe=None):
	# HACK TO WORK AROUND CRASH ON CONSOLE OUTPUT WITH BBFREEZE GUI_ONLY
	sys.stdout = sys.stderr = open('miasmod.log', 'w')

	# Try to get some more useful info on crashes:
	import faulthandler
	faulthandler.enable()

	app = QtGui.QApplication(sys.argv)

	window = MiasMod()

	window.show()
	# window.open_saves_dat()
	# window.open_active_environment()
	# window.refresh_mod_list()
	window.load_main_rs5()
	window.synchronise_alocalmod()

	# import trace
	# t = trace.Trace()
	# t.runctx('app.exec_()', globals=globals(), locals=locals())
	app.exec_()

	del window


if __name__ == '__main__':
	start_gui_process()

# vi:noexpandtab:sw=8:ts=8
