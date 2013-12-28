#!/usr/bin/env python

# TODO:
#
# - Play nice with rs5 archives that have other files inside them
# - Detect if saves.dat has been modified externally & ask to reload
# - Menus to re-open saves.dat & arbitrary environment files
#   - Prevent opening same file multiple times
# - Figure out why the dirty bold indicator isn't always being cleared on save.
#   Just rendering (no dataChanged emitted), or flag actually not cleared?
#   Could it be related to the undo deep copy?
#
# - Ability to diff environments (save as *.miasmod files)
# - Merge all diffs into alocalmod.rs5
# - Detect if alocalmod.rs5 is out of sync from diffs
#
# Raw data
#  - save/load file
#  - Various ways to interpret it

import sys, os
from glob import glob

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import collections

import miasutil
import rs5archive
import rs5file
import environment
import data

import miasmod_data

def catch_error(f):
	import functools
	@functools.wraps(f)
	def catch_unhandled_exceptions(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:
			import traceback
			traceback.print_exc()
			sys.stderr.flush()
			dialog = QtGui.QMessageBox()
			dialog.setWindowTitle('MiasMod')
			dialog.setIcon(QtGui.QMessageBox.Critical)
			dialog.setText('Unhandled Exception')
			dialog.setInformativeText('%s: %s' % (e.__class__.__name__, str(e)))
			dialog.setDetailedText(traceback.format_exc())
			dialog.exec_()
			return
	return catch_unhandled_exceptions


class ModList(object):
	class mod(object):
		def __init__(self, name, path, basename, type, note=None):
			self.rs5_name = None
			self.rs5_path = None
			self.miasmod_name = None
			self.miasmod_path = None
			self.name = name
			self.note = (None, None)

			self.add(path, basename, type, note)

		def add(self, path, basename, type, note=None):
			if type == 'rs5':
				basename = '%s/environment' % basename
			setattr(self, '%s_path' % type, path)
			setattr(self, '%s_name' % type, basename)
			self.note = note or self.note
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

	def add(self, path):
		basename = os.path.basename(path)
		(name, ext) = [ x.lower() for x in os.path.splitext(basename) ]
		ext = ext[1:]

		note = None
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

		l = self.mods
		if name == 'alocalmod':
			l = self.mods_last
		if name in l:
			l[name].add(path, basename, ext, note)
		else:
			l[name] = ModList.mod(name, path, basename, ext, note)

	def extend(self, iterable):
		for item in iterable:
			self.add(item)
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
		return 3

	def data(self, index, role):
		mod = self.mod_list[index.row()]
		if role == Qt.DisplayRole:
			if index.column() == 0:
				return mod.miasmod_name
			if index.column() == 1:
				return mod.rs5_name
			if index.column() == 2:
				note = mod.note[0]
				if note is None and mod.name == self.mod_list.active:
					return 'Active'
				return note
		if role == Qt.ToolTipRole:
			if index.column() == 2:
				note = mod.note[1]
				if note is None and mod.name == self.mod_list.active:
					return 'Based on the filename, Miasmata will use the environment found in this RS5 file'
				return note
		if role == Qt.ForegroundRole:
			if index.column() == 2 and mod.note[0]:
				return QtGui.QBrush(Qt.red)
		if role == Qt.FontRole:
			if index.column() == 2:
				return QtGui.QFont(None, italic=True)

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			if section == 0:
				return 'Environment Mods'
			if section == 1:
				return 'RS5 Files'
			if section == 2:
				return 'Notes'

	def __getitem__(self, item):
		return self.mod_list[item]

	def __len__(self):
		return len(self.mod_list)

class MiasMod(QtGui.QMainWindow):
	from miasmod_ui import Ui_MainWindow
	def __init__(self, parent=None):
		super(MiasMod, self).__init__(parent)

		self.ui = self.Ui_MainWindow()
		self.ui.setupUi(self)

		self.ui.tabWidget.tabBar().tabButton(0, QtGui.QTabBar.RightSide).resize(0, 0)
		self.open_tabs = {}

		self.find_install_path()

		self.busy = False

	def progress(self, msg):
		if not self.busy:
			QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
		self.busy = True
		self.statusBar().showMessage(msg)

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
	def open_saves_dat(self):
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
		view = miasmod_data.MiasmataDataView(saves, sort=True, save_path = path)
		self.add_tab(view, 'saves.dat', 'saves.dat')

	@QtCore.Slot()
	@catch_error
	def refresh_mod_list(self):
		mod_list = ModList()

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

		mod_list.extend(sorted(glob(os.path.join(self.install_path, '*.miasmod'))))

		self.mod_list = ModListModel(mod_list)
		self.ui.mod_list.setModel(self.mod_list)
		self.ui.mod_list.resizeColumnsToContents()

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
		if event.key() == Qt.Key.Key_F5:
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

	@QtCore.Slot()
	@catch_error
	def synchronise_alocalmod(self):
		pass

	def ask_edit(self, mod, msg1, msg2, edit_mod, edit_rs5):
		dialog = QtGui.QMessageBox()
		dialog.setWindowTitle('MiasMod')
		dialog.setText(msg1)
		dialog.setInformativeText(msg2)
		edit_mod = dialog.addButton(edit_mod, dialog.AcceptRole)
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
			' envioronment.rs5, rather it is suggested to work with' \
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
		ret = diff_base, self.mod_list[diff_base_row + 1 : row + include_cur_row]
		return ret

	def ask_generate_mod_diff(self, row, mod):
		rs5_base, include_mods = self.guess_rs5_source_diffs(row, mod, False)
		if rs5_base is None:
			return 'edit_rs5'
		include_mods = [rs5_base.rs5_name] + [ x.miasmod_name for x in include_mods ] + [mod.rs5_name]
		mod_name = '%s.miasmod' % mod.name

		msg1 = 'Generate %s?' % mod_name
		msg2 = 'No miasmod file exists for the selected mod. Would you' \
			' like to create "%s" based on the the differences' \
			' between these files?:\n\n%s' \
			% (mod_name, '\n'.join(include_mods))
		edit_mod = 'Generate %s' % mod_name
		edit_rs5 = 'Edit %s' % mod.basename
		return self.ask_edit(mod, msg1, msg2, edit_mod, edit_rs5)

	def ask_resolve_mod_sync(self, row, mod):
		rs5_base, include_mods = self.guess_rs5_source_diffs(row, mod, True)
		if rs5_base is None:
			raise ValueError('No preceding mods found')
		include_mods = [rs5_base.rs5_name] + [ x.miasmod_name for x in include_mods ]

		msg1 = '%s appears to be out of sync!' % mod.rs5_name
		msg2 = 'Would to like to syncronise it from the following' \
			' files?\nIf you recently installed or updated any mods' \
			' listed below, or removed a different mod, you should' \
			' choose "synchronise %s". However, if you updated %s' \
			' itself you should choose "Discard %s"\n\n%s' \
			% (mod.rs5_name, os.path.basename(mod.rs5_path),
				mod.miasmod_name, '\n'.join(include_mods))
		edit_mod = 'Synchronise %s' % mod.rs5_name
		edit_rs5 = 'Discard %s' % mod.miasmod_name
		return self.ask_edit(mod, msg1, msg2, edit_mod, edit_rs5)

	def generate_env_from_diffs(self, row, mod, include_cur_row):
		rs5_base, include_mods = self.guess_rs5_source_diffs(row, mod, include_cur_row)
		env = environment.parse_from_archive(rs5_base.rs5_path)
		for m in include_mods:
			diff = data.json_decode_diff(open(m.miasmod_path, 'rb'))
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
		mod_name = '%s.miasmod' % mod.name
		self.progress('Generating %s...' % mod_name)
		env1 = self.generate_env_from_diffs(row, mod, False)
		env2 = environment.parse_from_archive(mod.rs5_path)
		diff = data.diff_data(env1, env2)
		mod_path = os.path.join(self.install_path, mod_name)
		data.json_encode_diff(diff, open(mod_path, 'wb'))
		self.refresh_mod_list()
		self.done()

	def rs5_synched(self, row, mod):
		self.progress('Checking if %s is synched...' % mod.rs5_name)
		env1 = self.generate_env_from_diffs(row, mod, True)
		env2 = environment.parse_from_archive(mod.rs5_path)
		self.done()
		return env1 == env2

	def sync_rs5(self, row, mod):
		env = self.generate_env_from_diffs(row, mod, True)
		environment.encode_to_archive(env, mod.rs5_path)
		self.refresh_mod_list()

	def add_tab(self, view, name, mod_name):
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
		view = miasmod_data.MiasmataDataView(env, name = mod.name, rs5_path = mod.rs5_path)
		self.add_tab(view, mod.rs5_name, mod.name)
		self.done()

	def open_mod_both(self, row, mod):
		name = '%s + %s' % (mod.miasmod_name, mod.rs5_name)
		self.progress('Opening %s...' % name)
		diff_base = self.generate_env_from_diffs(row, mod, False)
		env = environment.parse_from_archive(mod.rs5_path)
		env.name = mod.name

		view = miasmod_data.MiasmataDataView(env, name = mod.name, diff_base = diff_base, miasmod_path = mod.miasmod_path, rs5_path = mod.rs5_path)
		self.add_tab(view, mod.name, mod.name)
		self.done()

	def open_mod_miasmod_only(self, row, mod):
		self.progress('Opening %s...' % mod.miasmod_name)
		(diff_base, env) = self.generate_env_from_single_diff(row, mod)
		env.name = mod.miasmod_name

		view = miasmod_data.MiasmataDataView(env, name = mod.name, diff_base = diff_base, miasmod_path = mod.miasmod_path)
		self.add_tab(view, mod.miasmod_name, mod.name)
		self.done()


	@QtCore.Slot()
	@catch_error
	def open_active_environment(self):
		return self.open_alocalmod()

	def open_alocalmod(self):
		if 'alocalmod' in self.open_tabs:
			return self.activate_tab('alocalmod')

		row = len(self.mod_list) - 1
		mod = self.mod_list[row]
		if mod.name == 'alocalmod':
			return self.open_mod(row)
		self.progress('Opening alocalmod...')

		path = os.path.join(self.install_path, 'alocalmod.miasmod')
		mod = ModList.mod('alocalmod', path, os.path.basename(path), 'miasmod')
		path = os.path.join(self.install_path, 'alocalmod.rs5')
		mod.add('alocalmod', path, os.path.basename(path), 'rs5')

		env1 = self.generate_env_from_diffs(row, mod, True)
		env2 = env1.copy()
		env2.name = 'alocalmod'

		view = miasmod_data.MiasmataDataView(env2, name = mod.name, diff_base = env1, miasmod_path = mod.miasmod_path, rs5_path = mod.rs5_path)
		self.add_tab(view, mod.name, mod.name)
		self.done()

	@QtCore.Slot(QtCore.QModelIndex)
	@catch_error
	def on_mod_list_activated(self, index):
		row = index.row()
		return self.open_mod(row)

	def open_mod(self, row):
		mod = self.mod_list[row]

		if mod.name in self.open_tabs:
			return self.activate_tab(mod.name)

		if mod.name in ('environment', 'communitypatch'):
			answer = self.confirm_edit_special_mod(mod)
			if answer == 'cancel':
				return
			if answer == 'edit_mod':
				return self.open_alocalmod()

		if 'miasmod' not in mod.types: # rs5 only
			answer = self.ask_generate_mod_diff(row, mod)
			if answer == 'cancel':
				return
			if answer == 'edit_mod':
				self.generate_mod_diff(row, mod)
				return self.open_mod_both(row, mod)
			return self.open_mod_rs5_only(row, mod)

		if 'rs5' in mod.types: # Both rs5 + miasmod
			if not self.rs5_synched(row, mod):
				answer = self.ask_resolve_mod_sync(row, mod)
				if answer == 'cancel':
					return
				if answer == 'edit_rs5':
					self.generate_mod_diff(row, mod)
					return self.open_mod_both(row, mod)
				self.sync_rs5(row, mod)
			return self.open_mod_both(row, mod)

		# miasmod only
		return self.open_mod_miasmod_only(row, mod)

def start_gui_process(pipe=None):
	app = QtGui.QApplication(sys.argv)

	window = MiasMod()

	window.show()
	# window.open_saves_dat()
	# window.open_active_environment()
	window.refresh_mod_list()

	# import trace
	# t = trace.Trace()
	# t.runctx('app.exec_()', globals=globals(), locals=locals())
	app.exec_()

	del window


if __name__ == '__main__':
	start_gui_process()
