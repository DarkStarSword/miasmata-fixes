#!/usr/bin/env python

# TODO:
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

dirty_objects = set()
def mark_dirty(object):
	object.dirty = True
	dirty_objects.add(object)

def clear_dirty():
	for object in dirty_objects:
		del object.dirty
	dirty_objects.clear()

def add_undo_data(object):
	import copy
	if hasattr(object, 'undo'):
		return
	parent = object.parent
	del object.parent
	object.undo = copy.deepcopy(object)
	object.parent = parent

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
		# Update all columns - index will point at a specific col
		sel_start = self.index(index.row(), 0, index.parent())
		sel_end   = self.index(index.row(), 1, index.parent())
		self.dataChanged.emit(sel_start, sel_end)

	def removeRows(self, row, count, parent):
		parent_node = self.index_to_node(parent)
		mark_dirty(parent_node)
		self.beginRemoveRows(parent, row, row + count - 1)
		while count:
			del parent_node[parent_node.keys()[row]]
			count -= 1
		self.endRemoveRows()
		return True

	def insert_row(self, node, parent):
		parent_node = self.index_to_node(parent)
		insert_pos = len(parent_node)
		self.beginInsertRows(parent, insert_pos, insert_pos)
		parent_node[node.name] = node
		self.endInsertRows()
		return self.index(insert_pos, 0, parent)

	def setDataValue(self, index, value, role = Qt.EditRole):
		if role == Qt.EditRole:
			old_node = self.index_to_node(index)
			parent_node = old_node.parent
			if not isinstance(value, data.MiasmataDataType):
				# XXX: Only handles int, float, str.
				value = old_node.__class__(value)
			mark_dirty(value)
			value.undo = old_node
			if hasattr(old_node, 'undo'):
				value.undo = old_node.undo
			parent_node[old_node.name] = value
			self.row_updated(index)
			return True
		return False

	def undo(self, index):
		new_node = self.index_to_node(index)
		if not hasattr(new_node, 'undo'):
			return False
		old_node = new_node.undo
		old_node.parent = parent_node = new_node.parent
		if old_node.name != new_node.name:
			if old_node.name in parent_node:
				return False
			parent_idx = self.parent(index)
			self.removeRows(index.row(), 1, parent_idx)
			return self.insert_row(old_node, parent_idx)
		parent_node[old_node.name] = old_node
		self.row_updated(index)
		return True

	def setDataName(self, index, value, role = Qt.EditRole):
		if role == Qt.EditRole:
			node = self.index_to_node(index)
			if value in node.parent:
				return None
			parent_node = node.parent
			parent_idx = self.parent(index)
			add_undo_data(node)
			self.removeRows(index.row(), 1, parent_idx)
			node.name = data.null_str(value)
			mark_dirty(node)
			return self.insert_row(node, parent_idx)
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

	def undo(self, index):
		ret = self.sourceModel().undo(self.mapToSource(index))
		if isinstance(ret, QtCore.QModelIndex):
			return self.mapFromSource(ret)
		return ret

	def insert_row(self, node, parent):
		ret = self.sourceModel().insert_row(node, self.mapToSource(parent))
		return self.mapFromSource(ret)

class MiasmataDataListModel(QtCore.QAbstractListModel):
	def __init__(self, node, parent_model, parent_selection):
		QtCore.QAbstractListModel.__init__(self)
		self.node = node
		self.parent_model = parent_model
		self.parent_selection = parent_selection

	def rowCount(self, parent):
		return len(self.node) + 1

	def data(self, index, role):
		if index.row() >= len(self.node):
			if role == Qt.DisplayRole:
				return 'New Entry...'
			if role == Qt.EditRole:
				return str(self.new_entry())
			if role == Qt.FontRole:
				return QtGui.QFont(None, italic=True)
		if role in (Qt.DisplayRole, Qt.EditRole):
			return str(self.node[index.row()])

	def flags(self, index):
		if not index.isValid():
			return
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

	def notify_parent_model(self):
		mark_dirty(self.node)
		self.parent_model.row_updated(self.parent_selection)

	def _setData(self, index, new_item):
		add_undo_data(self.node)
		self.node[index.row()] = new_item
		self.dataChanged.emit(index, index)
		self.notify_parent_model()
		return True

	def setData(self, index, value, role):
		if role == Qt.EditRole:
			if index.row() >= len(self.node):
				self.insertRows(index.row(), 1)
			old_item = self.node[index.row()]
			try:
				new_item = old_item.__class__(value)
			except:
				return False
			return self._setData(index, new_item)
		return False

	def new_entry(self):
		return self.node.type()

	def insertRows(self, row, count, parent = QtCore.QModelIndex()):
		add_undo_data(self.node)
		self.beginInsertRows(parent, row, row + count - 1)
		while count:
			self.node.insert(row, self.new_entry())
			count -= 1
		self.endInsertRows()
		self.notify_parent_model()
		return True

	def removeRows(self, row, count, parent = QtCore.QModelIndex()):
		add_undo_data(self.node)
		self.beginRemoveRows(parent, row, row + count - 1)
		while count:
			del self.node[row]
			count -= 1
		self.endRemoveRows()
		self.notify_parent_model()
		return True

class MiasmataDataMixedListModel(MiasmataDataListModel):
	def data(self, index, role):
		if role != Qt.EditRole:
			return MiasmataDataListModel.data(self, index, role)
		if index.row() >= len(self.node):
			return '""'
		item = self.node[index.row()]
		if isinstance(item, data.null_str):
			return '"%s"' % str(item)
		return str(item)

	def setData(self, index, value, role):
		if role != Qt.EditRole:
			return False
		if index.row() >= len(self.node):
			self.insertRows(index.row(), 1)
		if len(value) >= 2 and value[0] == value[-1] == '"':
			return self._setData(index, data.null_str(value[1:-1]))
		try:
			new_item = data.data_int(value)
		except ValueError:
			try:
				new_item = data.data_float(value)
			except ValueError:
				new_item = data.null_str(value)
		return self._setData(index, new_item)

	@staticmethod
	def new_entry():
		return data.null_str()


class MiasmataDataView(QtGui.QWidget):
	from miasmod_data_ui import Ui_MiasmataData
	def __init__(self, root, save_path=None, parent=None):
		super(MiasmataDataView, self).__init__(parent)
		self.ui = self.Ui_MiasmataData()
		self.ui.setupUi(self)

		self.cur_node = None
		self.save_path = save_path
		self.root = root

		self.model = MiasmataDataModel(root)
		# self.ui.treeView.setModel(self.model)
		self.sort_proxy = MiasmataDataSortProxy(self)
		self.sort_proxy.setSourceModel(self.model)
		self.sort_proxy.sort(0, Qt.AscendingOrder)
		self.sort_proxy.setDynamicSortFilter(True)
		self.model = self.sort_proxy
		self.ui.treeView.setModel(self.sort_proxy)
		self.model.dataChanged.connect(self.dataChanged)
		self.model.rowsInserted.connect(self.enable_save)
		self.model.rowsRemoved.connect(self.enable_save)
		self.ui.treeView.expandToDepth(0)
		self.ui.treeView.setColumnWidth(0, 256)

		self.ui.actionNew_Key.setEnabled(False)
		self.ui.actionNew_Value.setEnabled(False)
		self.ui.actionUndo_Changes.setEnabled(False)
		self.ui.actionDelete.setEnabled(False)
		self.ui.treeView.addAction(self.ui.actionNew_Key)
		self.ui.treeView.addAction(self.ui.actionNew_Value)
		self.ui.treeView.addAction(self.ui.actionUndo_Changes)
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

		self.ui.value_list.addAction(self.ui.actionInsert_Row)
		self.ui.value_list.addAction(self.ui.actionRemove_Row)

	def __del__(self):
		del self.ui
		del self.model

	def update_view(self, current, previous):
		self.cur_node = node = self.model.index_to_node(current)

		self.ui.name.setText(node.name)
		self.ui.type.setCurrentIndex(data.data_types.keys().index(node.id))

		if current.parent().isValid():
			self.ui.name.setReadOnly(False)
			self.ui.type.setEnabled(True)
			self.ui.actionDelete.setEnabled(True)
			self.ui.delete_node.setEnabled(True)
		else:
			self.ui.name.setReadOnly(True)
			self.ui.type.setEnabled(False)
			self.ui.actionDelete.setEnabled(False)
			self.ui.delete_node.setEnabled(False)

		if hasattr(self.cur_node, 'undo') and self.cur_node.undo is not None:
			self.ui.actionUndo_Changes.setEnabled(True)
			self.ui.undo.setEnabled(True)
		else:
			self.ui.actionUndo_Changes.setEnabled(False)
			self.ui.undo.setEnabled(False)

		if isinstance(node, data.data_list):
			if isinstance(node, data.data_mixed_list):
				model = MiasmataDataMixedListModel(node, self.model, current)
			else:
				model = MiasmataDataListModel(node, self.model, current)
			if self.cur_node != previous:
				self.ui.value_list.setModel(model)
			self.ui.value_list.setVisible(True)
		else:
			self.ui.value_list.setVisible(False)
			self.ui.value_list.setModel(None)

		if isinstance(node, data.data_raw):
			lines = [ node.raw[x:x+8] for x in range(0, len(node.raw), 8) ]
			lines = map(lambda line: ' '.join([ '%.2x' % ord(x) for x in line ]), lines)
			self.ui.value_hex.setPlainText('\n'.join(lines))
			self.ui.value_hex.setVisible(True)
		else:
			self.ui.value_hex.setVisible(False)
			self.ui.value_hex.setPlainText('')

		if isinstance(node, data.data_tree):
			self.ui.actionNew_Key.setEnabled(True)
			self.ui.actionNew_Value.setEnabled(True)
			self.ui.new_key.setEnabled(True)
			self.ui.new_value.setEnabled(True)
		else:
			self.ui.actionNew_Key.setEnabled(False)
			self.ui.actionNew_Value.setEnabled(False)
			self.ui.new_key.setEnabled(False)
			self.ui.new_value.setEnabled(False)

		if isinstance(node, (data.null_str, data.data_int, data.data_float)):
			self.ui.value_line.setText(str(node))
			if isinstance(node, data.data_int):
				validator = QtGui.QIntValidator(self)
			elif isinstance(node, data.data_float):
				validator = QtGui.QDoubleValidator(self)
			else:
				validator = None
			self.ui.value_line.setValidator(validator)
			self.ui.value_line.setVisible(True)
		else:
			self.ui.value_line.setVisible(False)
			self.ui.value_line.setText('')


	@QtCore.Slot()
	def currentChanged(self, current, previous):
		return self.update_view(current, self.model.index_to_node(previous))

	@QtCore.Slot()
	def dataChanged(self, topLeft, bottomRight):
		self.ui.save.setEnabled(True)
		return self.update_view(topLeft, self.cur_node)

	@QtCore.Slot()
	def enable_save(self, parent, start, end):
		self.ui.save.setEnabled(True)

	def verify(self, encoded):
		from StringIO import StringIO
		json1 = StringIO()
		json2 = StringIO()
		data.dump_json(self.root, json1)
		data.data2json(StringIO(encoded), json2)
		return json1.getvalue() == json2.getvalue()

	def write_saves_dat(self):
		import time, os
		try:
			buf = data.encode(self.root)
		except Exception as e:
			QtGui.QMessageBox.warning(self, 'MiasMod',
				'%s while encoding data\n\n%s\n\nRefusing to write saves.dat!\n\nThis means there is a bug in MiasMod, please report this to DarkStarSword!' \
				% (e.__class__.__name__, str(e)))
			return -1

		if not self.verify(buf):
			QtGui.QMessageBox.warning(self, 'MiasMod',
				'Verification pass failed, refusing to write saves.dat!\n\nThis means there is a bug in MiasMod, please report this to DarkStarSword!' \
				% (e.__class__.__name__, str(e)))
			return

                try:
			timestamp_str = time.strftime('%Y%m%d%H%M%S')
			backup = '%s~%s' % (self.save_path, timestamp_str)
			os.rename(self.save_path, backup)
		except Exception as e:
			QtGui.QMessageBox.warning(self, 'MiasMod',
				'%s while backing up saves.dat\n\n%s\n\nRefusing to write saves.dat!' \
				% (e.__class__.__name__, str(e)))
			return -1

                try:
			open(self.save_path, 'wb').write(buf)
		except Exception as e:
			QtGui.QMessageBox.warning(self, 'MiasMod',
				'%s while writing saves.dat\n\n%s\n\nWill attempt to restore backup %s...' \
				% (e.__class__.__name__, str(e), backup))
			try:
				os.remove(self.save_path)
			except:
				pass # May just not have been created yet
			try:
				os.rename(backup, self.save_path)
				QtGui.QMessageBox.information(self, 'MiasMod',
					'Succesfully restored backup')
			except:
				QtGui.QMessageBox.warning(self, 'MiasMod',
					'%s while restoring %s\n\n%s' \
					% (e.__class__.__name__, backup, str(e)))
			return -1

	@QtCore.Slot()
	def on_save_clicked(self):
		if self.write_saves_dat():
			return

		clear_dirty()
		self.ui.save.setEnabled(False)

	@QtCore.Slot()
	def on_value_line_editingFinished(self):
		text = self.ui.value_line.text()
		if str(self.cur_node) != text:
			selection = self.selection_model.currentIndex()
			self.model.setDataValue(selection, text)
			sys.stdout.flush()
			sys.stderr.flush()

	@QtCore.Slot()
	def on_name_editingFinished(self):
		name = self.ui.name.text()
		if self.cur_node.name != name:
			selection = self.selection_model.currentIndex()
			new_index = self.model.setDataName(selection, name)
			self.selection_model.setCurrentIndex(new_index,
					QtGui.QItemSelectionModel.ClearAndSelect \
					| QtGui.QItemSelectionModel.Rows)

	@QtCore.Slot()
	def on_type_activated(self):
		new_type = data.data_types.values()[self.ui.type.currentIndex()]
		if self.cur_node.__class__ == new_type:
			return
		new_item = new_type()
		if isinstance(self.cur_node, data.MiasmataDataCoercible) and \
		   issubclass(new_type,      data.MiasmataDataCoercible):
			try:
				new_item = new_type(self.cur_node)
			except:
				pass
		selection = self.selection_model.currentIndex()
		self.model.setDataValue(selection, new_item)


	def insert_node(self, node, name_prefix):
		parent_idx = self.selection_model.currentIndex()
		i = 0
		while True:
			name = data.null_str('%s_%i' % (name_prefix, i))
			if name not in self.cur_node:
				node.name = name
				break
			i += 1
		node.undo = None
		new_index = self.model.insert_row(node, parent_idx)
		self.selection_model.setCurrentIndex(new_index,
					QtGui.QItemSelectionModel.ClearAndSelect \
					| QtGui.QItemSelectionModel.Rows)
		self.ui.name.setFocus()
		self.ui.name.selectAll()

	@QtCore.Slot()
	def insert_value(self):
		node = data.data_null()
		return self.insert_node(node, 'Item')

	@QtCore.Slot()
	def insert_key(self):
		node = data.data_tree()
		return self.insert_node(node, 'Key')

	@QtCore.Slot()
	def undo(self):
		selection = self.selection_model.currentIndex()
		new_index = self.model.undo(selection)
		if isinstance(new_index, QtCore.QModelIndex):
			self.selection_model.setCurrentIndex(new_index,
					QtGui.QItemSelectionModel.ClearAndSelect \
					| QtGui.QItemSelectionModel.Rows)
	@QtCore.Slot()
	def delete_node(self):
		selection = self.selection_model.currentIndex()
		dialog = QtGui.QMessageBox()
		dialog.setWindowTitle('MiasMod')
		dialog.setText('Confirm Deletion')
		dialog.setInformativeText('Really delete "%s"?\nThis action cannot be undone.' % data.format_parent(self.cur_node))
		dialog.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		dialog.setDefaultButton(QtGui.QMessageBox.Yes)
		ret = dialog.exec_()
		if ret == QtGui.QMessageBox.Yes:
			self.model.removeRows(selection.row(), 1, selection.parent())

	@QtCore.Slot()
	def on_actionInsert_Row_triggered(self):
		index = self.ui.value_list.selectionModel().currentIndex()
		self.ui.value_list.model().insertRows(index.row(), 1)
		self.ui.value_list.edit(index, QtGui.QAbstractItemView.AllEditTriggers, None)

	@QtCore.Slot()
	def on_actionRemove_Row_triggered(self):
		index = self.ui.value_list.selectionModel().currentIndex()
		self.ui.value_list.model().removeRows(index.row(), 1)


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
			saves.name = data.null_str('saves.dat')
			self.ui.tabWidget.addTab(MiasmataDataView(saves, save_path = path), u"saves.dat")

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

	# m = PipeMonitor(pipe)
	# m.recv.connect(window.recv)
	# m.start()

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
