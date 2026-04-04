# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'randomizer.ui'
#
# Manually written to match pyside-uic output style
#
# WARNING! All changes made in this file will be lost if regenerated!

from PySide import QtCore, QtGui


class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(820, 640)

		self.centralwidget = QtGui.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")

		self.verticalLayout_main = QtGui.QVBoxLayout(self.centralwidget)
		self.verticalLayout_main.setObjectName("verticalLayout_main")

		# ── Install path + status row ────────────────────────────────────
		self.gridLayout_top = QtGui.QGridLayout()
		self.gridLayout_top.setObjectName("gridLayout_top")

		self.label_7 = QtGui.QLabel(self.centralwidget)
		self.label_7.setObjectName("label_7")
		self.gridLayout_top.addWidget(self.label_7, 0, 0, 1, 2)

		self.install_path = QtGui.QLineEdit(self.centralwidget)
		self.install_path.setObjectName("install_path")
		self.gridLayout_top.addWidget(self.install_path, 1, 0, 1, 1)

		self.browse = QtGui.QPushButton(self.centralwidget)
		self.browse.setObjectName("browse")
		self.gridLayout_top.addWidget(self.browse, 1, 1, 1, 1)

		self.label_2 = QtGui.QLabel(self.centralwidget)
		self.label_2.setObjectName("label_2")
		self.gridLayout_top.addWidget(self.label_2, 2, 0, 1, 1)

		self.pushButton = QtGui.QPushButton(self.centralwidget)
		self.pushButton.setObjectName("pushButton")
		self.gridLayout_top.addWidget(self.pushButton, 2, 1, 1, 1)

		self.verticalLayout_main.addLayout(self.gridLayout_top)

		# ── Tab widget ────────────────────────────────────────────────────
		self.tabWidget = QtGui.QTabWidget(self.centralwidget)
		self.tabWidget.setObjectName("tabWidget")

		# ── Tab 0: Generate Randomizer ────────────────────────────────────
		self.tab = QtGui.QWidget()
		self.tab.setObjectName("tab")
		self.verticalLayout_tab1 = QtGui.QVBoxLayout(self.tab)
		self.verticalLayout_tab1.setObjectName("verticalLayout_tab1")

		self.label_8 = QtGui.QLabel(self.tab)
		self.label_8.setObjectName("label_8")
		self.label_8.setWordWrap(True)
		palette = self.label_8.palette()
		palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(180, 100, 0))
		self.label_8.setPalette(palette)
		self.verticalLayout_tab1.addWidget(self.label_8)

		# Settings form
		self.formLayout = QtGui.QFormLayout()
		self.formLayout.setObjectName("formLayout")
		self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)

		self.label = QtGui.QLabel(self.tab)
		self.label.setObjectName("label")
		self.lineEdit = QtGui.QLineEdit(self.tab)
		self.lineEdit.setObjectName("lineEdit")
		self.formLayout.addRow(self.label, self.lineEdit)

		self.label_3 = QtGui.QLabel(self.tab)
		self.label_3.setObjectName("label_3")
		self.comboBox = QtGui.QComboBox(self.tab)
		self.comboBox.setObjectName("comboBox")
		self.formLayout.addRow(self.label_3, self.comboBox)

		self.label_4 = QtGui.QLabel(self.tab)
		self.label_4.setObjectName("label_4")
		self.comboBox_2 = QtGui.QComboBox(self.tab)
		self.comboBox_2.setObjectName("comboBox_2")
		self.formLayout.addRow(self.label_4, self.comboBox_2)

		self.label_5 = QtGui.QLabel(self.tab)
		self.label_5.setObjectName("label_5")
		self.comboBox_3 = QtGui.QComboBox(self.tab)
		self.comboBox_3.setObjectName("comboBox_3")
		self.formLayout.addRow(self.label_5, self.comboBox_3)

		self.label_6 = QtGui.QLabel(self.tab)
		self.label_6.setObjectName("label_6")
		self.lineEdit_2 = QtGui.QLineEdit(self.tab)
		self.lineEdit_2.setObjectName("lineEdit_2")
		self.lineEdit_2.setMaximumWidth(100)
		self.lineEdit_2.setValidator(QtGui.QIntValidator(1, 9999))
		self.formLayout.addRow(self.label_6, self.lineEdit_2)

		self.verticalLayout_tab1.addLayout(self.formLayout)

		# Show Clusters button
		self.pushButton_3 = QtGui.QPushButton(self.tab)
		self.pushButton_3.setObjectName("pushButton_3")
		self.verticalLayout_tab1.addWidget(self.pushButton_3)

		# Checkboxes
		self.checkBox = QtGui.QCheckBox(self.tab)
		self.checkBox.setObjectName("checkBox")
		self.checkBox.setChecked(True)
		self.verticalLayout_tab1.addWidget(self.checkBox)

		self.checkBox_2 = QtGui.QCheckBox(self.tab)
		self.checkBox_2.setObjectName("checkBox_2")
		self.verticalLayout_tab1.addWidget(self.checkBox_2)

		self.checkBox_3 = QtGui.QCheckBox(self.tab)
		self.checkBox_3.setObjectName("checkBox_3")
		self.checkBox_3.setEnabled(False)
		self.verticalLayout_tab1.addWidget(self.checkBox_3)

		# Generate button (prominent)
		self.pushButton_4 = QtGui.QPushButton(self.tab)
		self.pushButton_4.setObjectName("pushButton_4")
		self.pushButton_4.setMinimumHeight(36)
		font = self.pushButton_4.font()
		font.setBold(True)
		self.pushButton_4.setFont(font)
		self.verticalLayout_tab1.addWidget(self.pushButton_4)

		# Log list view
		self.listView = QtGui.QListView(self.tab)
		self.listView.setObjectName("listView")
		self.listView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.verticalLayout_tab1.addWidget(self.listView)

		self.tabWidget.addTab(self.tab, "")

		# ── Tab 1: Spoiler Map ────────────────────────────────────────────
		self.tab_2 = QtGui.QWidget()
		self.tab_2.setObjectName("tab_2")
		self.horizontalLayout_tab2 = QtGui.QHBoxLayout(self.tab_2)
		self.horizontalLayout_tab2.setObjectName("horizontalLayout_tab2")

		# Left panel
		self.verticalLayout_tab2_left = QtGui.QVBoxLayout()
		self.verticalLayout_tab2_left.setObjectName("verticalLayout_tab2_left")

		self.label_10 = QtGui.QLabel(self.tab_2)
		self.label_10.setObjectName("label_10")
		self.label_10.setWordWrap(True)
		self.verticalLayout_tab2_left.addWidget(self.label_10)

		self.treeView = QtGui.QTreeView(self.tab_2)
		self.treeView.setObjectName("treeView")
		self.treeView.setHeaderHidden(True)
		self.verticalLayout_tab2_left.addWidget(self.treeView)

		self.horizontalLayout_spoiler_btns = QtGui.QHBoxLayout()
		self.pushButton_2 = QtGui.QPushButton(self.tab_2)
		self.pushButton_2.setObjectName("pushButton_2")
		self.horizontalLayout_spoiler_btns.addWidget(self.pushButton_2)

		self.pushButton_5 = QtGui.QPushButton(self.tab_2)
		self.pushButton_5.setObjectName("pushButton_5")
		self.horizontalLayout_spoiler_btns.addWidget(self.pushButton_5)
		self.verticalLayout_tab2_left.addLayout(self.horizontalLayout_spoiler_btns)

		self.horizontalLayout_tab2.addLayout(self.verticalLayout_tab2_left)

		# Scroll area for map image
		self.scrollArea = QtGui.QScrollArea(self.tab_2)
		self.scrollArea.setMinimumSize(QtCore.QSize(400, 0))
		self.scrollArea.setBaseSize(QtCore.QSize(1024, 1024))
		self.scrollArea.setWidgetResizable(False)
		self.scrollArea.setObjectName("scrollArea")

		self.scrollAreaWidgetContents = QtGui.QWidget()
		self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1024, 1024))
		self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(1024, 1024))
		self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

		self.map_label = QtGui.QLabel(self.scrollAreaWidgetContents)
		self.map_label.setGeometry(QtCore.QRect(0, 0, 1024, 1024))
		self.map_label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
		self.map_label.setObjectName("map_label")

		self.scrollArea.setWidget(self.scrollAreaWidgetContents)
		self.horizontalLayout_tab2.addWidget(self.scrollArea)

		self.tabWidget.addTab(self.tab_2, "")

		self.verticalLayout_main.addWidget(self.tabWidget)

		MainWindow.setCentralWidget(self.centralwidget)

		self.menubar = QtGui.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 820, 20))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)

		self.statusbar = QtGui.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def retranslateUi(self, MainWindow):
		_ = lambda s: QtGui.QApplication.translate("MainWindow", s, None, QtGui.QApplication.UnicodeUTF8)
		MainWindow.setWindowTitle(_("Miasmata Randomizer"))
		self.label_7.setText(_("Miasmata Install &Location:"))
		self.browse.setText(_("&Browse..."))
		self.label_2.setText(_("Installed Randomizer: (none)"))
		self.pushButton.setText(_("Uninstall"))
		self.label_8.setText(_("You must uninstall the current randomizer before generating a new one"))
		self.label.setText(_("Randomizer &Seed:"))
		self.label_3.setText(_("&Note Shuffle Mode:"))
		self.label_4.setText(_("&Plant Shuffle Mode:"))
		self.label_5.setText(_("&Fungus Shuffle Mode:"))
		self.label_6.setText(_("&Cluster Distance:"))
		self.pushButton_3.setText(_("Show Clusters (Spoilers!)"))
		self.checkBox.setText(_("Install Randomizer"))
		self.checkBox_2.setText(_("Save Spoiler Map"))
		self.checkBox_3.setText(_("Add hint notes (FUTURE)"))
		self.pushButton_4.setText(_("Generate Randomizer!"))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _("Generate Randomizer"))
		self.label_10.setText(_("The spoiler map shows the island map with the locations of selected "
			"plants/notes highlighted - either for the installed randomizer, or vanilla "
			"locations if no randomizer is installed."))
		self.pushButton_2.setText(_("Show Spoiler"))
		self.pushButton_5.setText(_("Save to File..."))
		self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _("Spoiler Map"))

# vi:noexpandtab:sw=8:ts=8
