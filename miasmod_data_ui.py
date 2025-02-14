# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'miasmod_data.ui'
#
# Created: Tue Apr 29 18:40:05 2014
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MiasmataData(object):
    def setupUi(self, MiasmataData):
        MiasmataData.setObjectName("MiasmataData")
        MiasmataData.setWindowIcon(QtGui.QIcon('imageformats/miasmod.ico'))
        MiasmataData.resize(713, 490)
        self.verticalLayout_3 = QtGui.QVBoxLayout(MiasmataData)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.save = QtGui.QPushButton(MiasmataData)
        self.save.setEnabled(False)
        self.save.setObjectName("save")
        self.horizontalLayout_2.addWidget(self.save)
        self.show_diff = QtGui.QPushButton(MiasmataData)
        self.show_diff.setEnabled(False)
        self.show_diff.setObjectName("show_diff")
        self.horizontalLayout_2.addWidget(self.show_diff)
        self.lblVersion = QtGui.QLabel(MiasmataData)
        self.lblVersion.setEnabled(False)
        self.lblVersion.setObjectName("lblVersion")
        self.horizontalLayout_2.addWidget(self.lblVersion)
        self.version = QtGui.QLineEdit(MiasmataData)
        self.version.setEnabled(False)
        self.version.setMaximumSize(QtCore.QSize(84, 16777215))
        self.version.setObjectName("version")
        self.horizontalLayout_2.addWidget(self.version)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView = QtGui.QTreeView(MiasmataData)
        self.treeView.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setRootIsDecorated(False)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAllColumnsShowFocus(True)
        self.treeView.setObjectName("treeView")
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtGui.QLabel(MiasmataData)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.search = QtGui.QLineEdit(MiasmataData)
        self.search.setObjectName("search")
        self.horizontalLayout_3.addWidget(self.search)
        self.clear_search = QtGui.QPushButton(MiasmataData)
        self.clear_search.setObjectName("clear_search")
        self.horizontalLayout_3.addWidget(self.clear_search)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(MiasmataData)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.name = QtGui.QLineEdit(MiasmataData)
        self.name.setReadOnly(True)
        self.name.setObjectName("name")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.name)
        self.type = QtGui.QComboBox(MiasmataData)
        self.type.setEnabled(False)
        self.type.setObjectName("type")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.type)
        self.label_2 = QtGui.QLabel(MiasmataData)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(MiasmataData)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.value_line = QtGui.QLineEdit(MiasmataData)
        self.value_line.setObjectName("value_line")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.value_line)
        self.verticalLayout_2.addLayout(self.formLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.value_list = QtGui.QListView(MiasmataData)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.value_list.sizePolicy().hasHeightForWidth())
        self.value_list.setSizePolicy(sizePolicy)
        self.value_list.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.value_list.setAlternatingRowColors(True)
        self.value_list.setUniformItemSizes(True)
        self.value_list.setObjectName("value_list")
        self.verticalLayout_2.addWidget(self.value_list)
        self.value_hex = QtGui.QPlainTextEdit(MiasmataData)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.value_hex.sizePolicy().hasHeightForWidth())
        self.value_hex.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setWeight(75)
        font.setBold(True)
        self.value_hex.setFont(font)
        self.value_hex.setReadOnly(True)
        self.value_hex.setObjectName("value_hex")
        self.verticalLayout_2.addWidget(self.value_hex)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 2, 1, 1, 1)
        self.new_key = QtGui.QPushButton(MiasmataData)
        self.new_key.setEnabled(False)
        self.new_key.setObjectName("new_key")
        self.gridLayout_2.addWidget(self.new_key, 1, 0, 1, 1)
        self.delete_node = QtGui.QPushButton(MiasmataData)
        self.delete_node.setEnabled(False)
        self.delete_node.setObjectName("delete_node")
        self.gridLayout_2.addWidget(self.delete_node, 2, 2, 1, 1)
        self.new_value = QtGui.QPushButton(MiasmataData)
        self.new_value.setEnabled(False)
        self.new_value.setObjectName("new_value")
        self.gridLayout_2.addWidget(self.new_value, 2, 0, 1, 1)
        self.undo = QtGui.QPushButton(MiasmataData)
        self.undo.setEnabled(False)
        self.undo.setObjectName("undo")
        self.gridLayout_2.addWidget(self.undo, 1, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.actionNew_Key = QtGui.QAction(MiasmataData)
        self.actionNew_Key.setObjectName("actionNew_Key")
        self.actionNew_Value = QtGui.QAction(MiasmataData)
        self.actionNew_Value.setObjectName("actionNew_Value")
        self.actionUndo_Changes = QtGui.QAction(MiasmataData)
        self.actionUndo_Changes.setObjectName("actionUndo_Changes")
        self.actionDelete = QtGui.QAction(MiasmataData)
        self.actionDelete.setObjectName("actionDelete")
        self.actionInsert_Row = QtGui.QAction(MiasmataData)
        self.actionInsert_Row.setObjectName("actionInsert_Row")
        self.actionRemove_Row = QtGui.QAction(MiasmataData)
        self.actionRemove_Row.setObjectName("actionRemove_Row")
        self.lblVersion.setBuddy(self.version)
        self.label_4.setBuddy(self.search)
        self.label.setBuddy(self.name)
        self.label_2.setBuddy(self.type)
        self.label_3.setBuddy(self.value_line)

        self.retranslateUi(MiasmataData)
        QtCore.QObject.connect(self.actionNew_Key, QtCore.SIGNAL("triggered()"), MiasmataData.insert_key)
        QtCore.QObject.connect(self.actionNew_Value, QtCore.SIGNAL("triggered()"), MiasmataData.insert_value)
        QtCore.QObject.connect(self.new_key, QtCore.SIGNAL("clicked()"), MiasmataData.insert_key)
        QtCore.QObject.connect(self.new_value, QtCore.SIGNAL("clicked()"), MiasmataData.insert_value)
        QtCore.QObject.connect(self.delete_node, QtCore.SIGNAL("clicked()"), MiasmataData.delete_node)
        QtCore.QObject.connect(self.undo, QtCore.SIGNAL("clicked()"), MiasmataData.undo)
        QtCore.QObject.connect(self.actionUndo_Changes, QtCore.SIGNAL("triggered()"), MiasmataData.undo)
        QtCore.QObject.connect(self.actionDelete, QtCore.SIGNAL("triggered()"), MiasmataData.delete_node)
        QtCore.QObject.connect(self.clear_search, QtCore.SIGNAL("clicked()"), self.search.clear)
        QtCore.QMetaObject.connectSlotsByName(MiasmataData)
        MiasmataData.setTabOrder(self.treeView, self.search)
        MiasmataData.setTabOrder(self.search, self.clear_search)
        MiasmataData.setTabOrder(self.clear_search, self.name)
        MiasmataData.setTabOrder(self.name, self.type)
        MiasmataData.setTabOrder(self.type, self.value_line)
        MiasmataData.setTabOrder(self.value_line, self.value_list)
        MiasmataData.setTabOrder(self.value_list, self.value_hex)
        MiasmataData.setTabOrder(self.value_hex, self.new_key)
        MiasmataData.setTabOrder(self.new_key, self.new_value)
        MiasmataData.setTabOrder(self.new_value, self.undo)
        MiasmataData.setTabOrder(self.undo, self.delete_node)
        MiasmataData.setTabOrder(self.delete_node, self.save)
        MiasmataData.setTabOrder(self.save, self.show_diff)
        MiasmataData.setTabOrder(self.show_diff, self.version)

    def retranslateUi(self, MiasmataData):
        self.save.setText(QtGui.QApplication.translate("MiasmataData", "&Save...", None, QtGui.QApplication.UnicodeUTF8))
        self.show_diff.setText(QtGui.QApplication.translate("MiasmataData", "Show &mod changes...", None, QtGui.QApplication.UnicodeUTF8))
        self.lblVersion.setText(QtGui.QApplication.translate("MiasmataData", "&Version:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("MiasmataData", "&Search:", None, QtGui.QApplication.UnicodeUTF8))
        self.clear_search.setText(QtGui.QApplication.translate("MiasmataData", "&Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MiasmataData", "&Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MiasmataData", "&Type:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MiasmataData", "&Value:", None, QtGui.QApplication.UnicodeUTF8))
        self.new_key.setText(QtGui.QApplication.translate("MiasmataData", "New &Key", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_node.setText(QtGui.QApplication.translate("MiasmataData", "&Delete Node...", None, QtGui.QApplication.UnicodeUTF8))
        self.new_value.setText(QtGui.QApplication.translate("MiasmataData", "New V&alue", None, QtGui.QApplication.UnicodeUTF8))
        self.undo.setText(QtGui.QApplication.translate("MiasmataData", "&Undo Changes to Node", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew_Key.setText(QtGui.QApplication.translate("MiasmataData", "New Key", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew_Value.setText(QtGui.QApplication.translate("MiasmataData", "New Value", None, QtGui.QApplication.UnicodeUTF8))
        self.actionUndo_Changes.setText(QtGui.QApplication.translate("MiasmataData", "Undo Changes", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDelete.setText(QtGui.QApplication.translate("MiasmataData", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.actionInsert_Row.setText(QtGui.QApplication.translate("MiasmataData", "Insert Row", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRemove_Row.setText(QtGui.QApplication.translate("MiasmataData", "Remove Row", None, QtGui.QApplication.UnicodeUTF8))

