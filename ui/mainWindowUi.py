from PyQt6 import QtCore, QtGui, QtWidgets


class UiMainWindow:
    centralwidget = None
    inp_text = None
    outp_text = None
    vertical = None
    menubar = None
    view_menu = None
    statusbar = None
    blocks_action = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(825, 625)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.inp_text = QtWidgets.QPlainTextEdit(parent=self.centralwidget)
        self.outp_text = QtWidgets.QPlainTextEdit(parent=self.centralwidget)
        self.vertical = QtWidgets.QVBoxLayout()
        self.vertical.addWidget(self.inp_text)
        self.vertical.addWidget(self.outp_text)
        self.centralwidget.setLayout(self.vertical)
        self.inp_text.setReadOnly(True)
        self.inp_text.setObjectName("inp_text")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 807, 26))
        self.menubar.setObjectName("menubar")
        self.view_menu = QtWidgets.QMenu(parent=self.menubar)
        self.view_menu.setObjectName("view_menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.blocks_action = QtGui.QAction(parent=MainWindow)
        self.blocks_action.setObjectName("blocks_action")
        self.view_menu.addAction(self.blocks_action)
        self.menubar.addAction(self.view_menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Spintax"))
        self.view_menu.setTitle(_translate("MainWindow", "Просмотр"))
        self.blocks_action.setText(_translate("MainWindow", "Блоки"))
