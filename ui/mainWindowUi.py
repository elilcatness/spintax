from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QListWidget

from src.constants import TEXT_FIELD_STYLE, EXPORT_RESOURCE_SHORTCUT, OPEN_SHORTCUT, EXPORT_SHORTCUT
from src.customClasses import InputTextField


class UiMainWindow:
    centralwidget = None
    inpText = None
    samplesList = None
    outpText = None
    vertical = None
    menubar = None
    mainMenu = None
    openAction = None
    exportMenu = None
    resourceAction = None
    exportAction = None
    viewMenu = None
    blocksAction = None
    statusbar = None

    def setupUi(self, MainWindow):
        MainWindow.resize(825, 625)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.inpText = InputTextField(MainWindow, parent=self.centralwidget)
        self.inpText.setStyleSheet(TEXT_FIELD_STYLE)
        # self.samplesList = QListWidget(parent=self.centralwidget)

        self.outpText = QtWidgets.QPlainTextEdit(parent=self.centralwidget)
        self.outpText.setStyleSheet(TEXT_FIELD_STYLE)
        self.outpText.setReadOnly(True)
        self.vertical = QtWidgets.QVBoxLayout()
        self.vertical.addWidget(self.inpText)
        self.vertical.addWidget(self.outpText)
        self.centralwidget.setLayout(self.vertical)
        self.inpText.setReadOnly(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 807, 26))
        self.mainMenu = QtWidgets.QMenu(parent=self.menubar)
        self.openAction = QtGui.QAction(parent=MainWindow)
        self.openAction.setShortcut(OPEN_SHORTCUT)
        self.mainMenu.addAction(self.openAction)
        self.menubar.addMenu(self.mainMenu)
        self.exportMenu = QtWidgets.QMenu(parent=self.menubar)
        self.resourceAction = QtGui.QAction(parent=MainWindow)
        self.resourceAction.setShortcut(EXPORT_RESOURCE_SHORTCUT)
        self.exportMenu.addAction(self.resourceAction)
        self.exportAction = QtGui.QAction(parent=MainWindow)
        self.exportAction.setShortcut(EXPORT_SHORTCUT)
        self.exportMenu.addAction(self.exportAction)
        self.viewMenu = QtWidgets.QMenu(parent=self.menubar)
        self.blocksAction = QtGui.QAction(parent=MainWindow)
        self.viewMenu.addAction(self.blocksAction)
        self.menubar.addAction(self.viewMenu.menuAction())
        self.menubar.addMenu(self.viewMenu)
        self.menubar.addMenu(self.exportMenu)

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Spintax"))
        self.mainMenu.setTitle(_translate("MainWindow", "Программа"))
        self.openAction.setText(_translate("MainWindow", "Открыть файл"))
        self.exportMenu.setTitle(_translate("MainWindow", "Экспорт"))
        self.resourceAction.setText(_translate("MainWindow", "Ресурса"))
        self.viewMenu.setTitle(_translate("MainWindow", "Просмотр"))
        self.blocksAction.setText(_translate("MainWindow", "Блоки"))
