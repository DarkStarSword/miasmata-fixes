import sys, os

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

import rs5archive
import environment
import data

from ui_utils import catch_error

def add_undo_data(object):
	import copy
	if hasattr(object, 'undo'):
		return
	parent = object.parent
	del object.parent
	object.undo = copy.deepcopy(object)
	object.parent = parent

def warn_unsupported_encoding(orig, filtered, illegal):
	dialog = QtGui.QMessageBox()
	dialog.setWindowTitle('MiasMod')
	dialog.setText('Unsupported characters')
	dialog.setInformativeText('Some characters could not be encoded in'
			' Windows-1252 used by Miasmata and have been removed.'
			' Please refer to this page for a table of supported'
			' characters:'
			' https://en.wikipedia.org/wiki/Windows-1252')
	dialog.setDetailedText(u'Your text:\n{0}\ncontained the following'
			' unsupported characters:\n{1}\nIt was filtered'
			' to:\n{2}'.format(orig, u' '.join(illegal), filtered))
	ret = dialog.exec_()

def filter_cp1252(string):
	def f(c):
		try:
			c.encode('cp1252')
			return True
		except:
			return False
	def nf(c):
		return not f(c)
	bad = illegal = None
	new = string.__class__(filter(f, string))
	if string != new:
		bad = string
		illegal = string.__class__(filter(nf, string))
	return (new, bad, illegal)

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
		if parent_node is self.root:
			return QtCore.QModelIndex()
		parent_row = parent_node.parent.keys().index(parent_node.name)
		return self.createIndex(parent_row, 0, parent_node)

	def rowCount(self, parent):
		node = self.index_to_node(parent)
		if isinstance(node, data.data_tree):
			return len(node)
		return 0

	def hasChildren(self, parent):
		node = self.index_to_node(parent)
		return isinstance(node, data.data_tree)

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
				return unicode(node)
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
		self.mark_dirty(parent_node)
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
		self.mark_dirty(node)
		self.endInsertRows()
		index = self.index(insert_pos, 0, parent)
		return index

	def setDataValue(self, index, value, role = Qt.EditRole):
		if role == Qt.EditRole:
			old_node = self.index_to_node(index)
			parent_node = old_node.parent
			if not isinstance(value, data.MiasmataDataType):
				# XXX: Only handles int, float, str.
				value = old_node.__class__(value)
			value.undo = old_node
			if hasattr(old_node, 'undo'):
				value.undo = old_node.undo
			parent_node[old_node.name] = value
			self.mark_dirty(value)
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
			try:
				if value in node.parent:
					return None
			except:
				self.root.check_parent_invariant()
				sys.stderr.flush()
				raise
			parent_node = node.parent
			parent_idx = self.parent(index)
			add_undo_data(node)

			self.removeRows(index.row(), 1, parent_idx)
			node.name = data.null_str(value)
			self.mark_dirty(node)
			return self.insert_row(node, parent_idx)
		return None

	def setData(self, index, value, role = Qt.EditRole):
		if role == Qt.EditRole:
			if index.column() == 1:
				try:
					self.setDataValue(index, value, role)
				except:
					return False
				return True
		return False

	def flags(self, index):
		if not index.isValid():
			return
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
		if index.column() == 1:
			node = self.index_to_node(index)
			if isinstance(node, (data.null_str, data.data_int, data.data_float)):
				flags |= Qt.ItemIsEditable
		return flags

	def mark_dirty(self, object):
		if object is not None:
			object.dirty = True

	def clear_dirty(self):
		for dirty in self.root.clear_dirty_flags():
			index = QtCore.QModelIndex()
			for row in dirty:
				index = self.index(row, 0, index)
			self.row_updated(index)


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
			ret = self.mapFromSource(new_index)
			if ret.isValid():
				return ret
			self.setFilterFixedString(None)
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

	def hasChildren(self, parent):
		return self.sourceModel().hasChildren(self.mapToSource(parent))

	def mark_dirty(self, object):
		return self.sourceModel().mark_dirty(object)

	def clear_dirty(self):
		return self.sourceModel().clear_dirty()

	def filterAcceptsRow(self, sourceRow, sourceParent):
		if not sourceParent.isValid():
			# Don't ever filter out the root node
			return True
		s = self.filterRegExp().pattern().lower()
		if not s:
			return True
		index = self.sourceModel().index(sourceRow, 0, sourceParent)
		node = self.sourceModel().index_to_node(index)
		if node.name.lower().find(s) != -1:
			return True
		if hasattr(node, 'search'):
			return node.search(s)
		return False

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
				return unicode(self.new_entry())
			if role == Qt.FontRole:
				return QtGui.QFont(None, italic=True)
		if role in (Qt.DisplayRole, Qt.EditRole):
			return unicode(self.node[index.row()])

	def flags(self, index):
		if not index.isValid():
			return
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

	def notify_parent_model(self):
		self.parent_model.mark_dirty(self.node)
		self.parent_model.row_updated(self.parent_selection)

	def _setData(self, index, new_item):
		add_undo_data(self.node)
		if isinstance(new_item, unicode):
			(new_item, bad, illegal) = filter_cp1252(new_item)
			if bad is not None:
				warn_unsupported_encoding(bad, new_item, illegal)
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
			return '"%s"' % unicode(item)
		return unicode(item)

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

	saved = QtCore.Signal()

	def __init__(self, root, sort=True, save_path=None, diff_base=None, miasmod_path=None, rs5_path=None, parent=None, name=None, version=None):
		super(MiasmataDataView, self).__init__(parent)
		self.ui = self.Ui_MiasmataData()
		self.ui.setupUi(self)

		self.cur_node = None
		self.save_path = save_path
		self.diff_base = diff_base
		self.miasmod_path = miasmod_path
		self.rs5_path = rs5_path
		self.root = root
		self.name = name

		if self.diff_base is not None:
			self.ui.show_diff.setEnabled(True)
		if miasmod_path is not None:
			self.ui.lblVersion.setEnabled(True)
			self.ui.version.setEnabled(True)
		if version is not None:
			self.ui.version.setText(version)

		self.model = self.underlying_model = MiasmataDataModel(root)
		if sort:
			self.sort_proxy = MiasmataDataSortProxy(self)
			self.sort_proxy.setSourceModel(self.model)
			self.sort_proxy.sort(0, Qt.AscendingOrder)
			self.sort_proxy.setDynamicSortFilter(True)
			# self.ui.search.textChanged.connect(self.sort_proxy.setFilterFixedString)
			self.model = self.sort_proxy
			self.ui.treeView.setModel(self.sort_proxy)
		else:
			self.ui.treeView.setModel(self.model)
		self.model.dataChanged.connect(self.dataChanged)
		self.underlying_model.dataChanged.connect(self.underlyingDataChanged)
		self.underlying_model.rowsInserted.connect(self.enable_save)
		self.underlying_model.rowsRemoved.connect(self.enable_save)
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

	def keyPressEvent(self, event):
		if event.matches(QtGui.QKeySequence.Save):
			return self.save()
		super(MiasmataDataView, self).keyPressEvent(event)


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
			if self.cur_node is not previous:
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
			self.ui.value_line.setText(unicode(node))
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
	@catch_error
	def currentChanged(self, current, previous):
		return self.update_view(current, self.model.index_to_node(previous))

	@QtCore.Slot()
	@catch_error
	def dataChanged(self, topLeft, bottomRight):
		return self.update_view(topLeft, self.cur_node)

	@QtCore.Slot()
	@catch_error
	def underlyingDataChanged(self, topLeft, bottomRight):
		self.ui.save.setEnabled(True)

	@QtCore.Slot()
	@catch_error
	def on_version_editingFinished(self):
		self.ui.save.setEnabled(True)

	@QtCore.Slot()
	@catch_error
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
		import time
		try:
			buf = data.encode(self.root)
		except Exception as e:
			QtGui.QMessageBox.warning(self, 'MiasMod',
				'%s while encoding data\n\n%s\n\nRefusing to write saves.dat!\n\nThis means there is a bug in MiasMod, please report this to DarkStarSword!' \
				% (e.__class__.__name__, str(e)))
			return

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
			return

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
			return
		return True

	def write_miasmod(self):
		diff = data.diff_data(self.diff_base, self.root)
		version = self.ui.version.text() or None
		data.json_encode_diff(diff, open(self.miasmod_path, 'wb'), version)
		return True

	def write_rs5(self):
		environment.encode_to_archive(self.root, self.rs5_path)
		return True

	def is_dirty(self):
		return self.ui.save.isEnabled()

	def save(self):
		if self.save_path is not None:
			if self.write_saves_dat() != True:
				return

		if self.miasmod_path is not None and self.diff_base is not None:
			if self.write_miasmod() != True:
				return

		if self.rs5_path is not None:
			if self.write_rs5() != True:
				return

		self.model.clear_dirty()
		self.ui.save.setEnabled(False)
		self.saved.emit()

	@QtCore.Slot()
	@catch_error
	def on_save_clicked(self):
		self.save()

	@QtCore.Slot()
	@catch_error
	def on_show_diff_clicked(self):
		# dialog = QtGui.QMessageBox()
		# dialog.setWindowTitle('MiasMod')
		# dialog.setText(self.root.name)
		# diff = data.diff_data(self.diff_base, self.root)
		# dialog.setInformativeText(data.pretty_fmt_diff(diff))
		# ret = dialog.exec_()

		diff = data.diff_data(self.diff_base, self.root)
		txt = data.pretty_fmt_diff(diff)

		dialog = QtGui.QDialog()
		dialog.resize(600,800)
		dialog.setWindowTitle('MiasMod')
		layout = QtGui.QVBoxLayout(dialog)
		# dialog.setText(self.root.name)
		txtbox = QtGui.QPlainTextEdit(dialog)
		txtbox.setReadOnly(True)
		txtbox.setPlainText(txt)
		layout.addWidget(txtbox)
		# dialog.setInformativeText(data.pretty_fmt_diff(diff))
		dialog.exec_()

	@QtCore.Slot()
	@catch_error
	def on_search_editingFinished(self):
		t = self.ui.search.text()
		if not t:
			return self.sort_proxy.setFilterFixedString(None)
		self.sort_proxy.setFilterFixedString(t)

	@QtCore.Slot()
	@catch_error
	def on_clear_search_clicked(self):
		selection = self.selection_model.currentIndex()
		selection = self.sort_proxy.mapToSource(selection)
		self.sort_proxy.reset()
		self.ui.treeView.expandToDepth(0)
		self.sort_proxy.setFilterFixedString(None)
		selection = self.sort_proxy.mapFromSource(selection)
		self.selection_model.setCurrentIndex(selection, \
					QtGui.QItemSelectionModel.ClearAndSelect \
					| QtGui.QItemSelectionModel.Rows)

	@QtCore.Slot()
	@catch_error
	def on_value_line_editingFinished(self):
		text = self.ui.value_line.text()
		(text, bad, illegal) = filter_cp1252(text)
		if bad is not None:
			self.ui.value_line.setText(text)
			warn_unsupported_encoding(bad, text, illegal)
		if unicode(self.cur_node) != text:
			selection = self.selection_model.currentIndex()
			self.model.setDataValue(selection, text)

	@QtCore.Slot()
	@catch_error
	def on_name_editingFinished(self):
		name = self.ui.name.text()
		(name, bad, illegal) = filter_cp1252(name)
		if bad is not None:
			self.ui.name.setText(name)
			warn_unsupported_encoding(bad, name, illegal)
		if self.cur_node.name != name:
			selection = self.selection_model.currentIndex()
			new_index = self.model.setDataName(selection, name)
			self.selection_model.setCurrentIndex(new_index,
					QtGui.QItemSelectionModel.ClearAndSelect \
					| QtGui.QItemSelectionModel.Rows)

	@QtCore.Slot()
	@catch_error
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
	@catch_error
	def insert_value(self):
		node = data.data_null()
		return self.insert_node(node, 'Item')

	@QtCore.Slot()
	@catch_error
	def insert_key(self):
		node = data.data_tree()
		return self.insert_node(node, 'Key')

	@QtCore.Slot()
	@catch_error
	def undo(self):
		selection = self.selection_model.currentIndex()
		new_index = self.model.undo(selection)
		if isinstance(new_index, QtCore.QModelIndex):
			self.selection_model.setCurrentIndex(new_index,
					QtGui.QItemSelectionModel.ClearAndSelect \
					| QtGui.QItemSelectionModel.Rows)
	@QtCore.Slot()
	@catch_error
	def delete_node(self):
		selection = self.selection_model.currentIndex()
		dialog = QtGui.QMessageBox()
		dialog.setWindowTitle('MiasMod')
		dialog.setText('Confirm Deletion')
		dialog.setInformativeText('Really delete "%s"?\nThis action cannot be undone.' % data.format_parent(self.cur_node, skip=1))
		dialog.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		dialog.setDefaultButton(QtGui.QMessageBox.Yes)
		ret = dialog.exec_()
		if ret == QtGui.QMessageBox.Yes:
			self.model.removeRows(selection.row(), 1, selection.parent())

	@QtCore.Slot()
	@catch_error
	def on_actionInsert_Row_triggered(self):
		index = self.ui.value_list.selectionModel().currentIndex()
		self.ui.value_list.model().insertRows(index.row(), 1)
		self.ui.value_list.edit(index, QtGui.QAbstractItemView.AllEditTriggers, None)

	@QtCore.Slot()
	@catch_error
	def on_actionRemove_Row_triggered(self):
		index = self.ui.value_list.selectionModel().currentIndex()
		self.ui.value_list.model().removeRows(index.row(), 1)

# vi:noexpandtab:sw=8:ts=8
