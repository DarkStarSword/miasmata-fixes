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

import multiprocessing
import collections

import miasutil
import rs5archive
import rs5file
import environment
import data

import miasmod_data

# import re
# _re_dig = re.compile(r'\d+')
# def sort_alnum(val1, val2):
# 	if not val1 or not val2 or val1 == val2:
# 		return cmp(val1, val2)
# 	a = val1[0]
# 	b = val2[0]
# 	if a.isdigit() and b.isdigit():
# 		a = val1[:_re_dig.match(val1).end()]
# 		b = val2[:_re_dig.match(val2).end()]
# 		if a != b:
# 			return cmp(int(a), int(b))
# 	elif a != b:
# 		return cmp(a, b)
# 	return sort_alnum(val1[len(a):], val2[len(b):])

class ModList(object):
	class mod(object):
		def __init__(self, name, filename, basename, type, note=None):
			self.rs5_name = None
			self.rs5_filename = None
			self.miasmod_name = None
			self.miasmod_filename = None
			self.name = name
			self.note = (None, None)
			self.add(filename, basename, type, note)
		def add(self, filename, basename, type, note=None):
			if type == 'rs5':
				basename = '%s/environment' % basename
			setattr(self, '%s_filename' % type, filename)
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
		def filename(self):
			return self.miasmod_filename or self.rs5_filename

	def __init__(self):
		self.mods = collections.OrderedDict()
		self.mods_last = collections.OrderedDict()

	def add(self, filename):
		basename = os.path.basename(filename)
		(name, ext) = [ x.lower() for x in os.path.splitext(basename) ]
		ext = ext[1:]

		note = None
		if ext == 'rs5':
			if name < 'alocalmod':
				note = ('WARNING: Filename will override alocalmod.rs5!', 'MiasMod combines mods into alocalmod.rs5, which should come first alphabetically to be used by Miasmata')
			if name > 'environment':
				note = ('WARNING: Filename may cause crash on load!', 'To avoid crashes, environment.rs5 should come last alphabetically')

		l = self.mods
		if name == 'alocalmod':
			l = self.mods_last
		if name in l:
			l[name].add(filename, basename, ext, note)
		else:
			l[name] = ModList.mod(name, filename, basename, ext, note)

	def extend(self, iterable):
		for item in iterable:
			self.add(item)
	def __len__(self):
		return len(self.mods) + len(self.mods_last)
	def __getitem__(self, idx):
		if idx < 0:
			idx = len(self) - idx
		if idx < len(self.mods):
			return self.mods.values()[idx]
		return self.mods_last.values()[idx - len(self.mods)]

class ModListModel(QtCore.QAbstractTableModel):
	def __init__(self, mod_list):
		QtCore.QAbstractTableModel.__init__(self)
		self.mod_list = mod_list

	def rowCount(self, parent):
		return len(self.mod_list)

	def columnCount(self, paretn):
		return 3

	def data(self, index, role):
		if role == Qt.DisplayRole:
			if index.column() == 0:
				return self.mod_list[index.row()].miasmod_name
			if index.column() == 1:
				return self.mod_list[index.row()].rs5_name
			if index.column() == 2:
				return self.mod_list[index.row()].note[0]
		if role == Qt.ToolTipRole:
			if index.column() == 2:
				return self.mod_list[index.row()].note[1]
		if role == Qt.ForegroundRole:
			if index.column() == 2:
				return QtGui.QBrush(Qt.red)

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			if section == 0:
				return 'Environment Mods'
			if section == 1:
				return 'RS5 Files'
			if section == 2:
				return 'Warnings'

	def __getitem__(self, item):
		return self.mod_list[item]

class MiasMod(QtGui.QMainWindow):
	from miasmod_ui import Ui_MainWindow
	def __init__(self, parent=None):
		super(MiasMod, self).__init__(parent)

		self.ui = self.Ui_MainWindow()
		self.ui.setupUi(self)

		self.ui.tabWidget.tabBar().tabButton(0, QtGui.QTabBar.RightSide).resize(0, 0)

		self.find_install_path()

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
	def open_saves_dat(self):
		try:
			path = miasutil.find_miasmata_save()
		except Exception as e:
			path = 'saves.dat'
		try:
			saves = data.parse_data(open(path, 'rb'))
		except Exception as e:
			return

		saves.name = data.null_str('saves.dat')
		self.ui.tabWidget.addTab(miasmod_data.MiasmataDataView(saves, sort=True, save_path = path), u"saves.dat")
		self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 1)

	def open_environment(self, filename, save_path=None):
		env = environment.extract_from_archive(filename)
		if save_path == None:
			save_path = filename
		env.name = data.null_str('%s/environment' % os.path.basename(save_path))

		view = miasmod_data.MiasmataDataView(env, rs5_path = save_path)
		self.ui.tabWidget.addTab(view, unicode(env.name))
		self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 1)

	@QtCore.Slot()
	def refresh_mod_list(self):
		mod_list = ModList()

		for filename in sorted(glob(os.path.join(self.install_path, '*.rs5')), reverse=True):
			basename = os.path.basename(filename)
			if basename.lower() == 'main.rs5':
				continue
			try:
				f = open(filename, 'rb')
				archive = rs5archive.Rs5ArchiveDecoder(f)
			except:
				continue
			if 'environment' not in archive:
				continue
			mod_list.add(filename)

		mod_list.extend(sorted(glob(os.path.join(self.install_path, '*.miasmod'))))

		self.mod_list = ModListModel(mod_list)
		self.ui.mod_list.setModel(self.mod_list)
		self.ui.mod_list.resizeColumnsToContents()

	@QtCore.Slot()
	def open_active_environment(self):
		files = sorted([ os.path.basename(file).lower() for file in glob(os.path.join(self.install_path, '*.rs5')) ])
		if 'main.rs5' in files:
			files.remove('main.rs5')
		active = os.path.join(self.install_path, files[0])
		save_path = os.path.join(self.install_path, 'alocalmod.rs5')
		try:
			self.open_environment(active, save_path=save_path)
		except:
			return

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

	@QtCore.Slot(int)
	def on_tabWidget_tabCloseRequested(self, index):
		if index == 0:
			return
		if self.ask_save_tab(index) == QtGui.QMessageBox.Cancel:
			return
		self.ui.tabWidget.removeTab(index)

	@QtCore.Slot()
	def synchronise_alocalmod(self):
		pass

	def find_diff_base(self, row):
		i = row - 1
		while i >= 0:
			mod = self.mod_list[i]
			if 'rs5' in mod.types:
				return mod
			i -= 1

	def generate_miasmod_diff(self, f1, f2, output):
		(env1, env2) = [ environment.extract_from_archive(f) for f in (f1, f2) ]
		diff = data.diff_data(env1, env2)
		data.json_encode_diff(diff, open(output, 'wb'))
		self.refresh_mod_list()

	def open_mod(self, row, mod):
		if 'miasmod' not in mod.types and mod.name != 'environment':
			diff_base = self.find_diff_base(row)
			mod_name = '%s.miasmod' % mod.name
			dialog = QtGui.QMessageBox()
			dialog.setWindowTitle('MiasMod')
			dialog.setText('Generate %s?' % mod_name)
			dialog.setInformativeText('No "miasmod" file exists for the selected mod. Would you like to create "%s" based on the differences between "%s" and "%s"?' % (mod_name, diff_base.rs5_name, mod.rs5_name))
			create_mod = dialog.addButton('Generate %s' % mod_name, dialog.AcceptRole)
			edit_rs5 = dialog.addButton('Edit %s' % mod.basename, dialog.DestructiveRole)
			cancel = dialog.addButton(QtGui.QMessageBox.Cancel)
			dialog.exec_()

			if dialog.clickedButton() == cancel:
				return
			if dialog.clickedButton() == create_mod:
				self.generate_miasmod_diff(diff_base.rs5_filename, mod.rs5_filename, os.path.join(self.install_path, mod_name))

	@QtCore.Slot(QtCore.QModelIndex)
	def on_mod_list_activated(self, index):
		row = index.row()
		mod = self.mod_list[row]

		if mod.name == 'environment':
			msg = '''It is not recommended to directly edit envioronment.rs5, rather it is suggested to work with "miasmod" files that automatically get combined into alocalmod.rs5/environment which is picked up by the game. If you aren't sure you should probably edit alocalmod.miasmod instead.\n\nWhat would you like to do?'''
		elif mod.name == 'communitypatch':
			msg ='''Are you sure you wish to edit the community patch? Unless you know what you are doing you probably should edit a local mod (e.g. alocalmod.miasmod) instead.'''
		else:
			return self.open_mod(row, mod)

		dialog = QtGui.QMessageBox()
		dialog.setWindowTitle('MiasMod')
		dialog.setText('Confirm editing %s' % mod.basename)
		dialog.setInformativeText(msg)
		edit_mod = dialog.addButton('Edit alocalmod.miasmod', dialog.AcceptRole)
		edit_rs5 = dialog.addButton('Edit %s (not recommended)' % mod.basename, dialog.DestructiveRole)
		cancel = dialog.addButton(QtGui.QMessageBox.Cancel)
		dialog.exec_()

		if dialog.clickedButton() == cancel:
			return
		if dialog.clickedButton() == edit_mod:
			return self.open_miasmod(os.path.join(self.install_path, 'alocalmod.miasmod'))
		return self.open_mod(row, mod)

	# @QtCore.Slot(list)
	# def recv(self, v):
	# 	print v

# class PipeMonitor(QtCore.QObject):
# 	# Unnecessary on a Unix based environment - QSocketNotifier should work
# 	# with the pipe's fileno() and integrate with Qt's main loop like you
# 	# would expect with any select()/epoll() based event loop.
# 	#
# 	# On Windows however...
# 	#
# 	# For future reference - the "pipe" is implemented as a Windows Named
# 	# Pipe. Qt5 does have some mechanisms to deal with those, but AFAICT to
# 	# use Qt5 I would need to use PyQt (not PySide which is still Qt 4.8)
# 	# with Python 3, but some of the modules I'm using still depend on
# 	# Python 2 (certainly bbfreeze & I think py2exe as well).
# 
# 	import threading
# 	recv = QtCore.Signal(list)
# 
# 	def __init__(self, pipe):
# 		QtCore.QObject.__init__(self)
# 		self.pipe = pipe
# 
# 	def _start(self):
# 		while True:
# 			v = self.pipe.recv()
# 			self.recv.emit(v)
# 
# 	def start(self):
# 		self.thread = self.threading.Thread(target=self._start)
# 		self.thread.daemon = True
# 		self.thread.start()

def start_gui_process(pipe=None):
	app = QtGui.QApplication(sys.argv)

	window = MiasMod()

	# m = PipeMonitor(pipe)
	# m.recv.connect(window.recv)
	# m.start()

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
	multiprocessing.freeze_support()
	# if hasattr(multiprocessing, 'set_executable'):
		# Set python interpreter

	# (parent_conn, child_conn) = multiprocessing.Pipe()

	start_gui_process()

	# gui = multiprocessing.Process(target=start_gui_process, args=(child_conn,))
	# gui.daemon = True
	# gui.start()
	# child_conn.close()
	# parent_conn.send(['test',123,'ab'])
	# try:
	# 	print parent_conn.recv()
	# except EOFError:
	# 	print 'Child closed pipe'
