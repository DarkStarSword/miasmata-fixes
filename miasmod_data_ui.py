# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'miasmod_data.ui'
#
# Created: Wed Dec 18 14:53:38 2013
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MiasmataData(object):
    def setupUi(self, MiasmataData):
        MiasmataData.setObjectName("MiasmataData")
        MiasmataData.resize(400, 300)
        self.horizontalLayout = QtGui.QHBoxLayout(MiasmataData)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.treeView = QtGui.QTreeView(MiasmataData)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAllColumnsShowFocus(True)
        self.treeView.setObjectName("treeView")
        self.horizontalLayout.addWidget(self.treeView)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboBox = QtGui.QComboBox(MiasmataData)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.addWidget(self.comboBox)
        self.listView = QtGui.QListView(MiasmataData)
        self.listView.setObjectName("listView")
        self.verticalLayout.addWidget(self.listView)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(MiasmataData)
        QtCore.QMetaObject.connectSlotsByName(MiasmataData)

    def retranslateUi(self, MiasmataData):
        pass

