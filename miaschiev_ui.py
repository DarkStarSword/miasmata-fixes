# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'miaschiev.ui'
#
# Created: Mon Dec 09 13:44:04 2013
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Miaschiev(object):
    def setupUi(self, Miaschiev):
        Miaschiev.setObjectName("Miaschiev")
        Miaschiev.resize(1215, 793)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(Miaschiev)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.install_path = QtGui.QLineEdit(Miaschiev)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.install_path.sizePolicy().hasHeightForWidth())
        self.install_path.setSizePolicy(sizePolicy)
        self.install_path.setObjectName("install_path")
        self.gridLayout.addWidget(self.install_path, 2, 0, 1, 1)
        self.save_browse = QtGui.QPushButton(Miaschiev)
        self.save_browse.setObjectName("save_browse")
        self.gridLayout.addWidget(self.save_browse, 4, 1, 1, 1)
        self.install_browse = QtGui.QPushButton(Miaschiev)
        self.install_browse.setObjectName("install_browse")
        self.gridLayout.addWidget(self.install_browse, 2, 1, 1, 1)
        self.save_path = QtGui.QLineEdit(Miaschiev)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.save_path.sizePolicy().hasHeightForWidth())
        self.save_path.setSizePolicy(sizePolicy)
        self.save_path.setObjectName("save_path")
        self.gridLayout.addWidget(self.save_path, 4, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Miaschiev)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)
        self.label = QtGui.QLabel(Miaschiev)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtGui.QSpacerItem(20, 32, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        self.verticalLayout.addItem(spacerItem)
        self.save0 = QtGui.QPushButton(Miaschiev)
        self.save0.setEnabled(False)
        self.save0.setMinimumSize(QtCore.QSize(0, 38))
        self.save0.setMaximumSize(QtCore.QSize(416, 16777215))
        self.save0.setObjectName("save0")
        self.verticalLayout.addWidget(self.save0)
        self.save1 = QtGui.QPushButton(Miaschiev)
        self.save1.setEnabled(False)
        self.save1.setMinimumSize(QtCore.QSize(0, 38))
        self.save1.setMaximumSize(QtCore.QSize(416, 16777215))
        self.save1.setObjectName("save1")
        self.verticalLayout.addWidget(self.save1)
        self.save2 = QtGui.QPushButton(Miaschiev)
        self.save2.setEnabled(False)
        self.save2.setMinimumSize(QtCore.QSize(0, 38))
        self.save2.setMaximumSize(QtCore.QSize(416, 16777215))
        self.save2.setObjectName("save2")
        self.verticalLayout.addWidget(self.save2)
        spacerItem1 = QtGui.QSpacerItem(20, 32, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        self.verticalLayout.addItem(spacerItem1)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.lbl_coast = QtGui.QLabel(Miaschiev)
        self.lbl_coast.setEnabled(False)
        self.lbl_coast.setObjectName("lbl_coast")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.lbl_coast)
        self.show_coast = QtGui.QPushButton(Miaschiev)
        self.show_coast.setEnabled(False)
        self.show_coast.setObjectName("show_coast")
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.show_coast)
        spacerItem2 = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        self.formLayout.setItem(3, QtGui.QFormLayout.SpanningRole, spacerItem2)
        self.lbl_urns = QtGui.QLabel(Miaschiev)
        self.lbl_urns.setEnabled(False)
        self.lbl_urns.setObjectName("lbl_urns")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.lbl_urns)
        self.urns = QtGui.QLabel(Miaschiev)
        self.urns.setText("")
        self.urns.setObjectName("urns")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.urns)
        self.show_urns = QtGui.QPushButton(Miaschiev)
        self.show_urns.setEnabled(False)
        self.show_urns.setObjectName("show_urns")
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.show_urns)
        spacerItem3 = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        self.formLayout.setItem(6, QtGui.QFormLayout.SpanningRole, spacerItem3)
        self.lbl_heads = QtGui.QLabel(Miaschiev)
        self.lbl_heads.setEnabled(False)
        self.lbl_heads.setObjectName("lbl_heads")
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.lbl_heads)
        self.heads = QtGui.QLabel(Miaschiev)
        self.heads.setEnabled(False)
        self.heads.setObjectName("heads")
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.heads)
        self.show_heads = QtGui.QPushButton(Miaschiev)
        self.show_heads.setEnabled(False)
        self.show_heads.setObjectName("show_heads")
        self.formLayout.setWidget(8, QtGui.QFormLayout.LabelRole, self.show_heads)
        self.reset_head = QtGui.QPushButton(Miaschiev)
        self.reset_head.setEnabled(False)
        self.reset_head.setObjectName("reset_head")
        self.formLayout.setWidget(8, QtGui.QFormLayout.FieldRole, self.reset_head)
        spacerItem4 = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        self.formLayout.setItem(9, QtGui.QFormLayout.SpanningRole, spacerItem4)
        self.lbl_notes = QtGui.QLabel(Miaschiev)
        self.lbl_notes.setEnabled(False)
        self.lbl_notes.setObjectName("lbl_notes")
        self.formLayout.setWidget(10, QtGui.QFormLayout.LabelRole, self.lbl_notes)
        self.notes = QtGui.QLabel(Miaschiev)
        self.notes.setText("")
        self.notes.setObjectName("notes")
        self.formLayout.setWidget(10, QtGui.QFormLayout.FieldRole, self.notes)
        self.reset_notezz = QtGui.QPushButton(Miaschiev)
        self.reset_notezz.setEnabled(False)
        self.reset_notezz.setObjectName("reset_notezz")
        self.formLayout.setWidget(11, QtGui.QFormLayout.SpanningRole, self.reset_notezz)
        spacerItem5 = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        self.formLayout.setItem(12, QtGui.QFormLayout.SpanningRole, spacerItem5)
        self.lbl_plants = QtGui.QLabel(Miaschiev)
        self.lbl_plants.setEnabled(False)
        self.lbl_plants.setObjectName("lbl_plants")
        self.formLayout.setWidget(13, QtGui.QFormLayout.LabelRole, self.lbl_plants)
        self.plants = QtGui.QLabel(Miaschiev)
        self.plants.setText("")
        self.plants.setObjectName("plants")
        self.formLayout.setWidget(13, QtGui.QFormLayout.FieldRole, self.plants)
        self.coast = QtGui.QLabel(Miaschiev)
        self.coast.setText("")
        self.coast.setObjectName("coast")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.coast)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem6 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem6)
        self.progress = QtGui.QLabel(Miaschiev)
        self.progress.setFrameShape(QtGui.QFrame.Panel)
        self.progress.setFrameShadow(QtGui.QFrame.Sunken)
        self.progress.setText("")
        self.progress.setObjectName("progress")
        self.verticalLayout.addWidget(self.progress)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.scrollArea = QtGui.QScrollArea(Miaschiev)
        self.scrollArea.setMinimumSize(QtCore.QSize(768, 0))
        self.scrollArea.setBaseSize(QtCore.QSize(1024, 1024))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1024, 1024))
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(1024, 1024))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.addWidget(self.scrollArea)

        self.retranslateUi(Miaschiev)
        QtCore.QMetaObject.connectSlotsByName(Miaschiev)
        Miaschiev.setTabOrder(self.install_path, self.install_browse)
        Miaschiev.setTabOrder(self.install_browse, self.save_path)
        Miaschiev.setTabOrder(self.save_path, self.save_browse)
        Miaschiev.setTabOrder(self.save_browse, self.save0)
        Miaschiev.setTabOrder(self.save0, self.save1)
        Miaschiev.setTabOrder(self.save1, self.save2)
        Miaschiev.setTabOrder(self.save2, self.show_coast)
        Miaschiev.setTabOrder(self.show_coast, self.show_urns)
        Miaschiev.setTabOrder(self.show_urns, self.show_heads)
        Miaschiev.setTabOrder(self.show_heads, self.reset_head)
        Miaschiev.setTabOrder(self.reset_head, self.reset_notezz)
        Miaschiev.setTabOrder(self.reset_notezz, self.scrollArea)

    def retranslateUi(self, Miaschiev):
        Miaschiev.setWindowTitle(QtGui.QApplication.translate("Miaschiev", "Mias(Achievement)mata", None, QtGui.QApplication.UnicodeUTF8))
        self.save_browse.setText(QtGui.QApplication.translate("Miaschiev", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.install_browse.setText(QtGui.QApplication.translate("Miaschiev", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Miaschiev", "Miasmata Saved Games Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Miaschiev", "Miasmata Install Location:", None, QtGui.QApplication.UnicodeUTF8))
        self.save0.setText(QtGui.QApplication.translate("Miaschiev", "Load Save Slot 1", None, QtGui.QApplication.UnicodeUTF8))
        self.save1.setText(QtGui.QApplication.translate("Miaschiev", "Load Save Slot 2", None, QtGui.QApplication.UnicodeUTF8))
        self.save2.setText(QtGui.QApplication.translate("Miaschiev", "Load Save Slot 3", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_coast.setText(QtGui.QApplication.translate("Miaschiev", "Coastline Mapped:", None, QtGui.QApplication.UnicodeUTF8))
        self.show_coast.setText(QtGui.QApplication.translate("Miaschiev", "Show Mapped Coastline", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_urns.setText(QtGui.QApplication.translate("Miaschiev", "Urns Lit:", None, QtGui.QApplication.UnicodeUTF8))
        self.show_urns.setText(QtGui.QApplication.translate("Miaschiev", "Show Lit Urns", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_heads.setText(QtGui.QApplication.translate("Miaschiev", "Head Statues Located:", None, QtGui.QApplication.UnicodeUTF8))
        self.heads.setText(QtGui.QApplication.translate("Miaschiev", "Coming Soon!", None, QtGui.QApplication.UnicodeUTF8))
        self.show_heads.setText(QtGui.QApplication.translate("Miaschiev", "Show", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_head.setText(QtGui.QApplication.translate("Miaschiev", "Reset one statue...", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_notes.setText(QtGui.QApplication.translate("Miaschiev", "Notes Found:", None, QtGui.QApplication.UnicodeUTF8))
        self.reset_notezz.setText(QtGui.QApplication.translate("Miaschiev", "Reset missing Sanchez #1 note...", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_plants.setText(QtGui.QApplication.translate("Miaschiev", "Plants Found:", None, QtGui.QApplication.UnicodeUTF8))
