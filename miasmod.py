#!/usr/bin/env python

# TODO:
# Handle editing mixed lists
# Handle changing data types
# Add context menu to add / remove items
# Raw data
#  - save/load file
#  - Various ways to interpret it
# Save saves.dat
# Save alocalmod.rs5
# Create x.miasmod files with diffs

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
		# int/float/str :-/
		def __init__(self, val):
			self.val = val

	def __init__(self, root):
		QtCore.QAbstractItemModel.__init__(self)
		self.root = data.data_tree((root.name, root))
		self.keepalive = set()

	def index_to_node(self, index):
		if not index.isValid():
			return self.root
		x = index.internalPointer()
		if isinstance(x, self.ThisIsNotAFuckingIntDamnit):
			return x.val
		return x



	def index(self, row, column, parent):
		if not self.hasIndex(row, column, parent):
			return QtCore.QModelIndex()
		parent_node = self.index_to_node(parent)
		child = parent_node.values()[row]
		if isinstance(child, (int, float, str)):
			child = self.ThisIsNotAFuckingIntDamnit(child)
			self.keepalive.add(child)
		return self.createIndex(row, column, child)

	def parent(self, index):
		child_node = self.index_to_node(index)
		parent_node = child_node.parent
		if parent_node == self.root:
			return QtCore.QModelIndex()
		parent_row = parent_node.parent.keys().index(parent_node.name)
		return self.createIndex(parent_row, 0, parent_node)

	def rowCount(self, parent):
		node = self.index_to_node(parent)
		if isinstance(node, data.data_tree):
			return len(node)
		return 0

	def columnCount(self, parent):
		return 2

	def data(self, index, role):
		if role in (Qt.DisplayRole, Qt.EditRole):
			node = self.index_to_node(index)
			if index.column() == 1:
				if isinstance(node, data.data_tree):
					return None
				if role == Qt.DisplayRole and hasattr(node, 'summary'):
					return node.summary()
				return str(node)
			return node.name
		if role == Qt.FontRole:
			node = self.index_to_node(index)
			if hasattr(node, 'dirty') and node.dirty:
				return QtGui.QFont(None, weight=QtGui.QFont.Bold)

	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return {0: 'Key', 1: 'Value'}[section]

	def row_updated(self, index):
		assert(index.column() == 0)
		# Update all columns - index will point at col 0
		sel_end = self.index(index.row(), 1, index.parent())
		self.dataChanged.emit(index, sel_end)

	def removeRows(self, row, count, parent):
		parent_node = self.index_to_node(parent)
		parent_node.dirty = True
		self.beginRemoveRows(parent, row, row + count - 1)
		while count:
			del parent_node[parent_node.keys()[row]]
			count -= 1
		self.endRemoveRows()
		return True

	# def insertRows(self, position, rows, parent):
	# 	parent_node = self.index_to_node(parent)
	# 	self.beginInsertRows(parent, position, position + rows - 1)
	# 	while rows:
	# 		# TODO: Add new NULL with unique name
	# 		rows -= 1
	# 	self.endInsertRows()

	def setDataValue(self, index, value, role = Qt.EditRole):
		if role == Qt.EditRole:
			old_node = self.index_to_node(index)
			parent_node = old_node.parent
			# XXX: Only handles int, float, str.
			new_node = old_node.__class__(value)
			new_node.dirty = True
			parent_node[old_node.name] = new_node
			self.row_updated(index)
			return True
		return False

	def setDataName(self, index, value, role = Qt.EditRole):
		if role == Qt.EditRole:
			node = self.index_to_node(index)
			if value in node.parent:
				return None
			parent_idx = self.parent(index)
			self.removeRows(index.row(), 1, parent_idx)
			node.name = value
			node.dirty = True
			insert_pos = len(node.parent)
			self.beginInsertRows(parent_idx, insert_pos, insert_pos)
			node.parent[node.name] = node
			self.endInsertRows()
			return self.index(insert_pos, 0, parent_idx)
		return None

class MiasmataDataSortProxy(QtGui.QSortFilterProxyModel):
	def index_to_node(self, index):
		return self.sourceModel().index_to_node(self.mapToSource(index))

	def setDataValue(self, index, value, role = Qt.EditRole):
		index = self.mapToSource(index)
		return self.sourceModel().setDataValue(index, value, role)

	def setDataName(self, index, value, role = Qt.EditRole):
		index = self.mapToSource(index)
		new_index = self.sourceModel().setDataName(index, value, role)
		if new_index is not None:
			return self.mapFromSource(new_index)

	def row_updated(self, index):
		return self.sourceModel().row_updated(self.mapToSource(index))

class MiasmataDataListModel(QtCore.QAbstractListModel):
	def __init__(self, node, parent_model, parent_selection):
		QtCore.QAbstractListModel.__init__(self)
		self.node = node
		self.parent_model = parent_model
		self.parent_selection = parent_selection

	def rowCount(self, parent):
		return len(self.node)

	def data(self, index, role):
		if role in (Qt.DisplayRole, Qt.EditRole):
			return str(self.node[index.row()])

	def flags(self, index):
		if not index.isValid():
			return
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

	def setData(self, index, value, role):
		if role == Qt.EditRole:
			row = index.row()
			old_item = self.node[row]
			try:
				new_item = old_item.__class__(value)
			except:
				return False
			self.node[row] = new_item
			self.node.dirty = True
			self.dataChanged.emit(index, index)
			self.parent_model.row_updated(self.parent_selection)
			return True
		return False

class MiasmataDataView(QtGui.QWidget):
	from miasmod_data_ui import Ui_MiasmataData
	def __init__(self, root, parent=None):
		super(MiasmataDataView, self).__init__(parent)
		self.ui = self.Ui_MiasmataData()
		self.ui.setupUi(self)

		self.current_node = None

		self.model = MiasmataDataModel(root)

		# self.ui.treeView.setModel(self.model)

		self.sort_proxy = MiasmataDataSortProxy(self)
		self.sort_proxy.setSourceModel(self.model)
		self.sort_proxy.sort(0, Qt.AscendingOrder)
		self.sort_proxy.setDynamicSortFilter(True)
		self.model = self.sort_proxy
		self.ui.treeView.setModel(self.sort_proxy)
		self.ui.treeView.expandToDepth(0)

		self.ui.treeView.setColumnWidth(0, 256)

		self.ui.treeView.addAction(self.ui.actionNew_Key)
		self.ui.treeView.addAction(self.ui.actionNew_Value)
		self.ui.treeView.addAction(self.ui.actionDelete)

		# Can this be done with the PySide auto signal/slot assign thingy?
		#
		# XXX: Known bug in PySide - https://bugreports.qt-project.org/browse/PYSIDE-79
		# Doing this in one line like this results in a crash due to
		# the selection model being prematurely garbage collected:
		# self.ui.treeView.selectionModel().currentChanged.connect(self.currentChanged)
		self.selection_model = self.ui.treeView.selectionModel()
		self.selection_model.currentChanged.connect(self.currentChanged)

		items = [ type.desc for type in data.data_types.values() ]
		self.ui.type.insertItems(0, items)

		self.ui.value_line.setVisible(False)
		self.ui.value_list.setVisible(False)
		self.ui.value_hex.setVisible(False)

	def __del__(self):
		del self.ui
		del self.model

	@QtCore.Slot()
	def currentChanged(self, current, previous):
		self.cur_node = node = self.model.index_to_node(current)

		self.ui.name.setText(node.name)
		self.ui.type.setCurrentIndex(data.data_types.keys().index(node.id))

		self.ui.value_line.setVisible(False)
		self.ui.value_line.setText('')
		self.ui.value_list.setVisible(False)
		self.ui.value_list.setModel(None)
		self.ui.value_hex.setVisible(False)
		self.ui.value_hex.setPlainText('')

		self.ui.actionNew_Key.setEnabled(False)
		self.ui.actionNew_Value.setEnabled(False)

		if current.parent().isValid():
			self.ui.name.setReadOnly(False)
			self.ui.actionDelete.setEnabled(True)
		else:
			self.ui.name.setReadOnly(True)
			self.ui.actionDelete.setEnabled(False)

		if isinstance(node, data.data_list):
			model = MiasmataDataListModel(node, self.model, current)
			self.ui.value_list.setModel(model)
			self.ui.value_list.setVisible(True)
		elif isinstance(node, data.data_raw):
			lines = [ node.raw[x:x+8] for x in range(0, len(node.raw), 8) ]
			lines = map(lambda line: ' '.join([ '%.2x' % ord(x) for x in line ]), lines)
			self.ui.value_hex.setPlainText('\n'.join(lines))
			self.ui.value_hex.setVisible(True)
		elif isinstance(node, (data.data_tree, data.data_null)):
			self.ui.actionNew_Key.setEnabled(True)
			self.ui.actionNew_Value.setEnabled(True)
		else:
			self.ui.value_line.setText(str(node))
			if isinstance(node, data.data_int):
				validator = QtGui.QIntValidator(self)
			elif isinstance(node, data.data_float):
				validator = QtGui.QDoubleValidator(self)
			else:
				validator = None
			self.ui.value_line.setValidator(validator)
			self.ui.value_line.setVisible(True)

	@QtCore.Slot()
	def on_value_line_editingFinished(self):
		text = self.ui.value_line.text()
		if str(self.cur_node) != text:
			selection = self.selection_model.currentIndex()
			self.model.setDataValue(selection, text)

	@QtCore.Slot()
	def on_name_editingFinished(self):
		name = self.ui.name.text()
		if self.cur_node.name != name:
			selection = self.selection_model.currentIndex()
			new_index = self.model.setDataName(selection, name)
			self.selection_model.setCurrentIndex(new_index, \
					QtGui.QItemSelectionModel.ClearAndSelect \
					| QtGui.QItemSelectionModel.Rows)

	@QtCore.Slot()
	def on_actionDelete_triggered(self):
		selection = self.selection_model.currentIndex()
		self.model.removeRows(selection.row(), 1, selection.parent())


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
			saves.name = 'saves.dat'
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

	# import trace
	# t = trace.Trace()
	# t.runctx('app.exec_()', globals=globals(), locals=locals())
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
