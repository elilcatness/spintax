from PyQt6 import QtCore, QtGui, QtWidgets

from customClasses import InputTextField


class UiMainWindow:
    centralwidget = None
    inpText = None
    outpText = None
    vertical = None
    menubar = None
    viewMenu = None
    statusbar = None
    blocksAction = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(825, 625)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.inpText = InputTextField(MainWindow, parent=self.centralwidget)
        self.outpText = QtWidgets.QPlainTextEdit(parent=self.centralwidget)
        self.vertical = QtWidgets.QVBoxLayout()
        self.vertical.addWidget(self.inpText)
        self.vertical.addWidget(self.outpText)
        self.centralwidget.setLayout(self.vertical)
        self.inpText.setReadOnly(True)
        self.inpText.setObjectName("inp_text")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 807, 26))
        self.menubar.setObjectName("menubar")
        self.viewMenu = QtWidgets.QMenu(parent=self.menubar)
        self.viewMenu.setObjectName("view_menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.blocksAction = QtGui.QAction(parent=MainWindow)
        self.blocksAction.setObjectName("blocks_action")
        self.viewMenu.addAction(self.blocksAction)
        self.menubar.addAction(self.viewMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Spintax"))
        self.viewMenu.setTitle(_translate("MainWindow", "Просмотр"))
        self.blocksAction.setText(_translate("MainWindow", "Блоки"))
