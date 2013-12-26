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

class ModListModel(QtCore.QAbstractTableModel):
	def __init__(self, mod_list):
		QtCore.QAbstractTableModel.__init__(self)
		self.mod_list = mod_list

	def rowCount(self, parent):
		return len(self.mod_list)

	def columnCount(self, paretn):
		return 1

	def data(self, index, role):
		if role == Qt.DisplayRole:
			return self.mod_list[index.row()][0]

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			return 'Environment Mods'

	def __getitem__(self, item):
		return self.mod_list[item]

class MiasMod(QtGui.QMainWindow):
	from miasmod_ui import Ui_MainWindow
	def __init__(self, parent=None):
		super(MiasMod, self).__init__(parent)

		self.ui = self.Ui_MainWindow()
		self.ui.setupUi(self)

		self.ui.tabWidget.tabBar().tabButton(0, QtGui.QTabBar.RightSide).resize(0, 0)

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
		try:
			install_path = miasutil.find_miasmata_install()
		except Exception as e:
			QtGui.QMessageBox.information(self, 'MiasMod',
					'Unable to locate Miasmata installation directory')
			return

		diff_list = glob(os.path.join(install_path, '*.miasmod'))
		diff_list = [ (os.path.basename(filename), 'mod', filename) for filename in diff_list ]
		diff_list = { os.path.splitext(x[0])[0] : x for x in diff_list }

		mod_list = []
		last_list = []

		for filename in sorted(glob(os.path.join(install_path, '*.rs5')), reverse=True):
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
			entry = []
			basename = os.path.splitext(basename)[0]
			if basename in diff_list:
				entry.append(diff_list[basename])
				del diff_list[basename]
			entry.append(('%s.rs5/environment' % basename, 'rs5', filename))
			if basename == 'alocalmod':
				last_list.extend(entry)
			else:
				mod_list.extend(entry)

		mod_list.extend(sorted(diff_list.itervalues()))
		mod_list.extend(last_list)

		self.mod_list = ModListModel(mod_list)
		self.ui.mod_list.setModel(self.mod_list)
		self.ui.mod_list.resizeColumnsToContents()

	@QtCore.Slot()
	def open_active_environment(self):
		try:
			install_path = miasutil.find_miasmata_install()
		except Exception as e:
			return

		files = sorted([ os.path.basename(file).lower() for file in glob(os.path.join(install_path, '*.rs5')) ])
		if 'main.rs5' in files:
			files.remove('main.rs5')
		active = os.path.join(install_path, files[0])
		save_path = os.path.join(install_path, 'alocalmod.rs5')
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

	def open_mod(self, row, (name, type, filename)):
		pass

	@QtCore.Slot(QtCore.QModelIndex)
	def on_mod_list_activated(self, index):
		row = index.row()
		(name, type, filename) = self.mod_list[row]
		if type == 'rs5':
			if name.lower() == 'environment.rs5/environment':
				msg = '''It is not recommended to directly edit envioronment.rs5, rather it is suggested to work with "miasmod" files which are automatically combined into alocalmod.rs5/environment for the game.\n\nWhat would you like to do?'''
			elif name.lower().startswith('communitypatch.'):
				msg ='''Are you sure you wish to edit the community patch? Unless you know what you are doing you probably should edit alocalmod.miasmod instead.'''
			else:
				return self.open_mod(row, (name, type, filename))

			dialog = QtGui.QMessageBox()
			dialog.setWindowTitle('MiasMod')
			dialog.setText('Confirm editing %s' % name)
			dialog.setInformativeText(msg)
			edit_mod = dialog.addButton('Edit alocalmod.miasmod', dialog.AcceptRole)
			edit_rs5 = dialog.addButton('Edit %s (not recommended)' % name, dialog.DestructiveRole)
			cancel = dialog.addButton(QtGui.QMessageBox.Cancel)
			dialog.exec_()

			if dialog.clickedButton() == cancel:
				return
			if dialog.clickedButton() == edit_mod:
				return self.open_miasmod(filename)
		return self.open_mod(row, (name, type, filename))

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
