# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'habitat.ui'
#
# Created: Tue Aug 11 01:33:11 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(975, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 191, 561))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.treeWidget = QtGui.QTreeWidget(self.verticalLayoutWidget)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.verticalLayout.addWidget(self.treeWidget)
        self.mainGraphicsView = QtGui.QGraphicsView(self.centralwidget)
        self.mainGraphicsView.setGeometry(QtCore.QRect(190, 0, 611, 551))
        self.mainGraphicsView.setObjectName(_fromUtf8("mainGraphicsView"))
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(220, 60, 281, 281))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(530, 40, 211, 221))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayoutWidget_3 = QtGui.QWidget(self.groupBox)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(10, 10, 183, 196))
        self.verticalLayoutWidget_3.setObjectName(_fromUtf8("verticalLayoutWidget_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.minButton = QtGui.QRadioButton(self.verticalLayoutWidget_3)
        self.minButton.setChecked(True)
        self.minButton.setObjectName(_fromUtf8("minButton"))
        self.verticalLayout_3.addWidget(self.minButton)
        self.maxButton = QtGui.QRadioButton(self.verticalLayoutWidget_3)
        self.maxButton.setObjectName(_fromUtf8("maxButton"))
        self.verticalLayout_3.addWidget(self.maxButton)
        self.avgButton = QtGui.QRadioButton(self.verticalLayoutWidget_3)
        self.avgButton.setObjectName(_fromUtf8("avgButton"))
        self.verticalLayout_3.addWidget(self.avgButton)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.timeLabel = QtGui.QLabel(self.verticalLayoutWidget_3)
        self.timeLabel.setObjectName(_fromUtf8("timeLabel"))
        self.horizontalLayout.addWidget(self.timeLabel)
        self.timeLineEdit = QtGui.QLineEdit(self.verticalLayoutWidget_3)
        self.timeLineEdit.setObjectName(_fromUtf8("timeLineEdit"))
        self.horizontalLayout.addWidget(self.timeLineEdit)
        self.minutesLabel = QtGui.QLabel(self.verticalLayoutWidget_3)
        self.minutesLabel.setObjectName(_fromUtf8("minutesLabel"))
        self.horizontalLayout.addWidget(self.minutesLabel)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.functionButton = QtGui.QPushButton(self.verticalLayoutWidget_3)
        self.functionButton.setObjectName(_fromUtf8("functionButton"))
        self.verticalLayout_3.addWidget(self.functionButton)
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(190, 0, 741, 481))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.dataTab = QtGui.QWidget()
        self.dataTab.setObjectName(_fromUtf8("dataTab"))
        self.verticalLayoutWidget_4 = QtGui.QWidget(self.dataTab)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(29, 20, 191, 271))
        self.verticalLayoutWidget_4.setObjectName(_fromUtf8("verticalLayoutWidget_4"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.attributeName = QtGui.QLabel(self.verticalLayoutWidget_4)
        self.attributeName.setObjectName(_fromUtf8("attributeName"))
        self.horizontalLayout_4.addWidget(self.attributeName)
        self.attributeValue = QtGui.QLabel(self.verticalLayoutWidget_4)
        self.attributeValue.setText(_fromUtf8(""))
        self.attributeValue.setObjectName(_fromUtf8("attributeValue"))
        self.horizontalLayout_4.addWidget(self.attributeValue)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.listWidget = QtGui.QListWidget(self.dataTab)
        self.listWidget.setGeometry(QtCore.QRect(30, 10, 201, 291))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.listWidget_2 = QtGui.QListWidget(self.dataTab)
        self.listWidget_2.setGeometry(QtCore.QRect(230, 10, 211, 291))
        self.listWidget_2.setObjectName(_fromUtf8("listWidget_2"))
        self.tabWidget.addTab(self.dataTab, _fromUtf8(""))
        self.summaryTab = QtGui.QWidget()
        self.summaryTab.setObjectName(_fromUtf8("summaryTab"))
        self.verticalLayoutWidget_5 = QtGui.QWidget(self.summaryTab)
        self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(30, 40, 481, 151))
        self.verticalLayoutWidget_5.setObjectName(_fromUtf8("verticalLayoutWidget_5"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.summaryLabel = QtGui.QLabel(self.verticalLayoutWidget_5)
        self.summaryLabel.setText(_fromUtf8(""))
        self.summaryLabel.setObjectName(_fromUtf8("summaryLabel"))
        self.horizontalLayout_5.addWidget(self.summaryLabel)
        self.summaryValue = QtGui.QLabel(self.verticalLayoutWidget_5)
        self.summaryValue.setText(_fromUtf8(""))
        self.summaryValue.setObjectName(_fromUtf8("summaryValue"))
        self.horizontalLayout_5.addWidget(self.summaryValue)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.summaryCB = QtGui.QComboBox(self.summaryTab)
        self.summaryCB.setGeometry(QtCore.QRect(30, 10, 191, 25))
        self.summaryCB.setObjectName(_fromUtf8("summaryCB"))
        self.summaryLW1 = QtGui.QListWidget(self.summaryTab)
        self.summaryLW1.setGeometry(QtCore.QRect(30, 40, 211, 271))
        self.summaryLW1.setObjectName(_fromUtf8("summaryLW1"))
        self.summaryLW2 = QtGui.QListWidget(self.summaryTab)
        self.summaryLW2.setGeometry(QtCore.QRect(240, 40, 211, 271))
        self.summaryLW2.setObjectName(_fromUtf8("summaryLW2"))
        self.tabWidget.addTab(self.summaryTab, _fromUtf8(""))
        self.graphTab = QtGui.QWidget()
        self.graphTab.setObjectName(_fromUtf8("graphTab"))
        self.graphicsView = PlotWidget(self.graphTab)
        self.graphicsView.setGeometry(QtCore.QRect(20, 50, 701, 331))
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.childrenBox = QtGui.QComboBox(self.graphTab)
        self.childrenBox.setGeometry(QtCore.QRect(20, 10, 179, 25))
        self.childrenBox.setObjectName(_fromUtf8("childrenBox"))
        self.verticalLayoutWidget_7 = QtGui.QWidget(self.graphTab)
        self.verticalLayoutWidget_7.setGeometry(QtCore.QRect(20, 380, 160, 61))
        self.verticalLayoutWidget_7.setObjectName(_fromUtf8("verticalLayoutWidget_7"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.verticalLayoutWidget_7)
        self.verticalLayout_7.setMargin(0)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.hour_label = QtGui.QLabel(self.verticalLayoutWidget_7)
        self.hour_label.setObjectName(_fromUtf8("hour_label"))
        self.horizontalLayout_2.addWidget(self.hour_label)
        self.hour_value = QtGui.QLabel(self.verticalLayoutWidget_7)
        self.hour_value.setText(_fromUtf8(""))
        self.hour_value.setObjectName(_fromUtf8("hour_value"))
        self.horizontalLayout_2.addWidget(self.hour_value)
        self.verticalLayout_7.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.minutes_label = QtGui.QLabel(self.verticalLayoutWidget_7)
        self.minutes_label.setObjectName(_fromUtf8("minutes_label"))
        self.horizontalLayout_3.addWidget(self.minutes_label)
        self.minutes_value = QtGui.QLabel(self.verticalLayoutWidget_7)
        self.minutes_value.setText(_fromUtf8(""))
        self.minutes_value.setObjectName(_fromUtf8("minutes_value"))
        self.horizontalLayout_3.addWidget(self.minutes_value)
        self.verticalLayout_7.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.graphTab, _fromUtf8(""))
        self.verticalLayoutWidget_6 = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget_6.setGeometry(QtCore.QRect(220, 60, 181, 51))
        self.verticalLayoutWidget_6.setObjectName(_fromUtf8("verticalLayoutWidget_6"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.verticalLayoutWidget_6)
        self.verticalLayout_6.setMargin(0)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.attrLabel = QtGui.QLabel(self.verticalLayoutWidget_6)
        self.attrLabel.setObjectName(_fromUtf8("attrLabel"))
        self.verticalLayout_6.addWidget(self.attrLabel)
        self.comboBox = QtGui.QComboBox(self.verticalLayoutWidget_6)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.verticalLayout_6.addWidget(self.comboBox)
        self.devicesListView = QtGui.QListView(self.centralwidget)
        self.devicesListView.setGeometry(QtCore.QRect(200, 40, 279, 246))
        self.devicesListView.setObjectName(_fromUtf8("devicesListView"))
        self.addBranchDevices = QtGui.QPushButton(self.centralwidget)
        self.addBranchDevices.setGeometry(QtCore.QRect(200, 290, 279, 27))
        self.addBranchDevices.setObjectName(_fromUtf8("addBranchDevices"))
        self.summaryNameLE = QtGui.QLineEdit(self.centralwidget)
        self.summaryNameLE.setGeometry(QtCore.QRect(200, 16, 251, 21))
        self.summaryNameLE.setObjectName(_fromUtf8("summaryNameLE"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 975, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionAddDevice = QtGui.QAction(MainWindow)
        self.actionAddDevice.setObjectName(_fromUtf8("actionAddDevice"))
        self.actionCreate_Branch = QtGui.QAction(MainWindow)
        self.actionCreate_Branch.setObjectName(_fromUtf8("actionCreate_Branch"))
        self.actionModify_Summary = QtGui.QAction(MainWindow)
        self.actionModify_Summary.setObjectName(_fromUtf8("actionModify_Summary"))
        self.actionDelete_Node = QtGui.QAction(MainWindow)
        self.actionDelete_Node.setObjectName(_fromUtf8("actionDelete_Node"))
        self.actionAdd_Summary = QtGui.QAction(MainWindow)
        self.actionAdd_Summary.setObjectName(_fromUtf8("actionAdd_Summary"))
        self.actionDelete_Summary = QtGui.QAction(MainWindow)
        self.actionDelete_Summary.setObjectName(_fromUtf8("actionDelete_Summary"))
        self.menuFile.addAction(self.actionAddDevice)
        self.menuFile.addAction(self.actionCreate_Branch)
        self.menuEdit.addAction(self.actionAdd_Summary)
        self.menuEdit.addAction(self.actionDelete_Summary)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionModify_Summary)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionDelete_Node)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Habitat Monitor", None))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Data Source", None))
        self.groupBox.setTitle(_translate("MainWindow", "Select a summary function", None))
        self.minButton.setText(_translate("MainWindow", "Minimum", None))
        self.maxButton.setText(_translate("MainWindow", "Maximum", None))
        self.avgButton.setText(_translate("MainWindow", "Average", None))
        self.timeLabel.setText(_translate("MainWindow", "Time: ", None))
        self.minutesLabel.setText(_translate("MainWindow", "(hh:mm:ss)", None))
        self.functionButton.setText(_translate("MainWindow", "Add Summary", None))
        self.attributeName.setText(_translate("MainWindow", "Attribute: ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dataTab), _translate("MainWindow", "Raw Data", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.summaryTab), _translate("MainWindow", "Summary", None))
        self.hour_label.setText(_translate("MainWindow", "Hours: ", None))
        self.minutes_label.setText(_translate("MainWindow", "Minutes", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.graphTab), _translate("MainWindow", "Graph", None))
        self.attrLabel.setText(_translate("MainWindow", "Select an attribute", None))
        self.addBranchDevices.setText(_translate("MainWindow", "Add Devices", None))
        self.summaryNameLE.setText(_translate("MainWindow", "Summary Name", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit", None))
        self.actionAddDevice.setText(_translate("MainWindow", "Add Device", None))
        self.actionCreate_Branch.setText(_translate("MainWindow", "Create Branch", None))
        self.actionModify_Summary.setText(_translate("MainWindow", "Modify Summary", None))
        self.actionDelete_Node.setText(_translate("MainWindow", "Delete Node", None))
        self.actionAdd_Summary.setText(_translate("MainWindow", "Add Summary", None))
        self.actionDelete_Summary.setText(_translate("MainWindow", "Delete Summary", None))

from pyqtgraph import PlotWidget
