# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'miasmod.ui'
#
# Created: Fri Dec 27 04:14:46 2013
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(935, 621)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setObjectName("tabWidget")
        self.mods_tab = QtGui.QWidget()
        self.mods_tab.setObjectName("mods_tab")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.mods_tab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.open_environment = QtGui.QPushButton(self.mods_tab)
        self.open_environment.setObjectName("open_environment")
        self.verticalLayout.addWidget(self.open_environment)
        self.new_mod = QtGui.QPushButton(self.mods_tab)
        self.new_mod.setObjectName("new_mod")
        self.verticalLayout.addWidget(self.new_mod)
        self.open_saves_dat = QtGui.QPushButton(self.mods_tab)
        self.open_saves_dat.setObjectName("open_saves_dat")
        self.verticalLayout.addWidget(self.open_saves_dat)
        self.refresh_mod_list = QtGui.QPushButton(self.mods_tab)
        self.refresh_mod_list.setObjectName("refresh_mod_list")
        self.verticalLayout.addWidget(self.refresh_mod_list)
        self.synchronise_local_mod = QtGui.QPushButton(self.mods_tab)
        self.synchronise_local_mod.setObjectName("synchronise_local_mod")
        self.verticalLayout.addWidget(self.synchronise_local_mod)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.mod_list = QtGui.QTableView(self.mods_tab)
        self.mod_list.setAlternatingRowColors(True)
        self.mod_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.mod_list.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.mod_list.setShowGrid(False)
        self.mod_list.setObjectName("mod_list")
        self.mod_list.verticalHeader().setVisible(False)
        self.horizontalLayout_2.addWidget(self.mod_list)
        self.tabWidget.addTab(self.mods_tab, "")
        self.verticalLayout_3.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 935, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.open_environment, QtCore.SIGNAL("clicked()"), MainWindow.open_active_environment)
        QtCore.QObject.connect(self.open_saves_dat, QtCore.SIGNAL("clicked()"), MainWindow.open_saves_dat)
        QtCore.QObject.connect(self.refresh_mod_list, QtCore.SIGNAL("clicked()"), MainWindow.refresh_mod_list)
        QtCore.QObject.connect(self.synchronise_local_mod, QtCore.SIGNAL("clicked()"), MainWindow.synchronise_alocalmod)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.tabWidget, self.open_environment)
        MainWindow.setTabOrder(self.open_environment, self.new_mod)
        MainWindow.setTabOrder(self.new_mod, self.refresh_mod_list)
        MainWindow.setTabOrder(self.refresh_mod_list, self.synchronise_local_mod)
        MainWindow.setTabOrder(self.synchronise_local_mod, self.mod_list)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Miasmata Advanced Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.open_environment.setText(QtGui.QApplication.translate("MainWindow", "Open local &environment...", None, QtGui.QApplication.UnicodeUTF8))
        self.new_mod.setText(QtGui.QApplication.translate("MainWindow", "&New Mod...", None, QtGui.QApplication.UnicodeUTF8))
        self.open_saves_dat.setText(QtGui.QApplication.translate("MainWindow", "Open &saves.dat...", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh_mod_list.setText(QtGui.QApplication.translate("MainWindow", "&Refresh Mod List", None, QtGui.QApplication.UnicodeUTF8))
        self.synchronise_local_mod.setText(QtGui.QApplication.translate("MainWindow", "&Synchronise alocalmod.rs5", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.mods_tab), QtGui.QApplication.translate("MainWindow", "Mod List", None, QtGui.QApplication.UnicodeUTF8))

