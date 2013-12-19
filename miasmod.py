#!/usr/bin/env python

import sys

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import multiprocessing

import miasutil

import data


import re
_re_dig = re.compile(r'\d+')
def sort_alnum(val1, val2):
	if not val1 or not val2 or val1 == val2:
		return cmp(val1, val2)
	a = val1[0]
	b = val2[0]
	if a.isdigit() and b.isdigit():
		a = val1[:_re_dig.match(val1).end()]
		b = val2[:_re_dig.match(val2).end()]
		if a != b:
			return cmp(int(a), int(b))
	elif a != b:
		return cmp(a, b)
	return sort_alnum(val1[len(a):], val2[len(b):])

class MiasmataDataModel(QtCore.QAbstractItemModel):
	class ThisIsNotAFuckingIntDamnit(object):
		# God damn fucking overloaded functions and type checking!
		# Guess I'll have to change these so they don't derive from
		# int/float :-/
		def __init__(self, val):
			self.val = val

	def __init__(self, root):
		QtCore.QAbstractItemModel.__init__(self)
		self.root = root
		self.keepalive = set()

	def index_to_node(self, index):
		# print '1'
		sys.stdout.flush()
		if not index.isValid():
			# print '2'
			sys.stdout.flush()
			return self.root
		# print '3'
		sys.stdout.flush()
		x = index.internalPointer()
		# print '..', repr(x)
		if isinstance(x, self.ThisIsNotAFuckingIntDamnit):
			return x.val
		return x



	def index(self, row, column, parent):
		# print 'index', row, column, repr(parent)
		sys.stdout.flush()
		if not self.hasIndex(row, column, parent):
			return QtCore.QModelIndex()
		parent_node = self.index_to_node(parent)
		# print '-index', row, column, parent_node.name
		sys.stdout.flush()
		child = sorted(parent_node.children.values(), cmp=sort_alnum, key=lambda x: x.name)[row]
		if isinstance(child, (int, float)):
			child = self.ThisIsNotAFuckingIntDamnit(child)
			self.keepalive.add(child)
		return self.createIndex(row, column, child)

	def parent(self, index):
		# print 'parent', repr(index)
		sys.stdout.flush()
		child_node = self.index_to_node(index)
		# print '-parent', child_node.name
		sys.stdout.flush()
		parent_node = child_node.parent
		if parent_node == self.root:
			return QtCore.QModelIndex()
		parent_row = sorted(parent_node.parent.children.keys(), cmp=sort_alnum).index(parent_node.name)
		return self.createIndex(parent_row, 0, parent_node)

	def rowCount(self, parent):
		# print 'rowCount', repr(parent)
		sys.stdout.flush()
		node = self.index_to_node(parent)
		# print '-rowCount', node.name
		if isinstance(node, data.data_tree):
			return len(node)
		return 0

	def columnCount(self, parent):
		# print 'columnCount', repr(parent)
		sys.stdout.flush()
		return 2

	def data(self, index, role):
		# print 'data', repr(index), repr(role)
		sys.stdout.flush()
		if role in (Qt.DisplayRole, Qt.EditRole):
			node = self.index_to_node(index)
			if index.column() == 1:
				if isinstance(node, data.data_tree):
					return None
				if role == Qt.DisplayRole and hasattr(node, 'summary'):
					return node.summary()
				return str(node)
			return node.name

	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return {0: 'Key', 1: 'Value'}[section]

	# def flags(self, index):
	# 	if not index.isValid():
	# 		return
	# 	return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

	# def insertRows(self, position, rows, index):
	# 	pass

class MiasmataDataView(QtGui.QWidget):
	from miasmod_data_ui import Ui_MiasmataData
	def __init__(self, root, parent=None):
		super(MiasmataDataView, self).__init__(parent)
		self.ui = self.Ui_MiasmataData()
		self.ui.setupUi(self)

		self.model = MiasmataDataModel(root)
		self.ui.treeView.setModel(self.model)
		self.ui.treeView.setColumnWidth(0, 256)

		# Can this be done with the PySide auto signal/slot assign thingy?
		#
		# XXX: Known bug in PySide - https://bugreports.qt-project.org/browse/PYSIDE-79
		# Doing this in one line like this results in a crash due to
		# the selection model being prematurely garbage collected:
		# self.ui.treeView.selectionModel().currentChanged.connect(self.currentChanged)
		selection_model = self.ui.treeView.selectionModel()
		selection_model.currentChanged.connect(self.currentChanged)

		items = [ type.desc for type in data.data_types.values() ]
		self.ui.type.insertItems(0, items)

		self.ui.value_line.setVisible(False)
		self.ui.value_list.setVisible(False)

	def __del__(self):
		del self.ui
		del self.model

	@QtCore.Slot()
	def currentChanged(self, current, previous):
		node = self.model.index_to_node(current)

		self.ui.name.setReadOnly(True)
		self.ui.name.setText(node.name)
		self.ui.type.setCurrentIndex(data.data_types.keys().index(node.id))

		self.ui.value_line.setVisible(False)
		self.ui.value_line.setText('')
		self.ui.value_list.setVisible(False)
		self.ui.value_list.clear()

		if isinstance(node, data.data_list):
			# for value in node:
			items = [ str(value) for value in node ]
			self.ui.value_list.insertItems(0, items)
			self.ui.value_list.setVisible(True)
		elif isinstance(node, data.data_raw):
			pass
		elif isinstance(node, data.data_tree):
			pass
		else:
			self.ui.value_line.setVisible(True)
			self.ui.value_line.setText(str(node))

class MiasMod(QtGui.QMainWindow):
	from miasmod_ui import Ui_MainWindow
	def __init__(self, parent=None):
		super(MiasMod, self).__init__(parent)

		self.ui = self.Ui_MainWindow()
		self.ui.setupUi(self)

		try:
			path = miasutil.find_miasmata_save()
		except Exception as e:
			path = 'saves.dat'
		try:
			saves = data.parse_data(open(path, 'rb'))
		except Exception as e:
				pass
		else:
			self.ui.tabWidget.addTab(MiasmataDataView(saves), u"saves.dat")

	def __del__(self):
		self.ui.tabWidget.clear()
		del self.ui

	@QtCore.Slot(list)
	def recv(self, v):
		print v

class PipeMonitor(QtCore.QObject):
	# Unnecessary on a Unix based environment - QSocketNotifier should work
	# with the pipe's fileno() and integrate with Qt's main loop like you
	# would expect with any select()/epoll() based event loop.
	#
	# On Windows however...
	#
	# For future reference - the "pipe" is implemented as a Windows Named
	# Pipe. Qt5 does have some mechanisms to deal with those, but AFAICT to
	# use Qt5 I would need to use PyQt (not PySide which is still Qt 4.8)
	# with Python 3, but some of the modules I'm using still depend on
	# Python 2 (certainly bbfreeze & I think py2exe as well).

	import threading
	recv = QtCore.Signal(list)

	def __init__(self, pipe):
		QtCore.QObject.__init__(self)
		self.pipe = pipe

	def _start(self):
		while True:
			v = self.pipe.recv()
			self.recv.emit(v)

	def start(self):
		self.thread = self.threading.Thread(target=self._start)
		self.thread.daemon = True
		self.thread.start()

def start_gui_process(pipe):
	app = QtGui.QApplication(sys.argv)

	window = MiasMod()

	m = PipeMonitor(pipe)
	m.recv.connect(window.recv)
	m.start()

	window.show()
	app.exec_()
	del window


if __name__ == '__main__':
	multiprocessing.freeze_support()
	# if hasattr(multiprocessing, 'set_executable'):
		# Set python interpreter

	(parent_conn, child_conn) = multiprocessing.Pipe()

	start_gui_process(child_conn)

	# gui = multiprocessing.Process(target=start_gui_process, args=(child_conn,))
	# gui.daemon = True
	# gui.start()
	# child_conn.close()
	# parent_conn.send(['test',123,'ab'])
	# try:
	# 	print parent_conn.recv()
	# except EOFError:
	# 	print 'Child closed pipe'
