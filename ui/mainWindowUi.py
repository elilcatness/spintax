from PyQt6.QtCore import QRect, QMetaObject, QCoreApplication
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QListWidget, QWidget, QPlainTextEdit, QVBoxLayout, QMenuBar, QMenu, QStatusBar

from src.constants import TEXT_FIELD_STYLE, EXPORT_RESOURCE_SHORTCUT, OPEN_SHORTCUT, EXPORT_SHORTCUT, \
    PREVIEWS_COUNT_SHORTCUT
from src.customClasses import InputTextField


class UiMainWindow:
    centralwidget = None
    inpText = None
    previewList = None
    outpText = None
    vertical = None
    menubar = None
    mainMenu = None
    openAction = None
    previewsAction = None
    exportMenu = None
    resourceAction = None
    exportAction = None
    viewMenu = None
    blocksAction = None
    statusbar = None

    def setupUi(self, MainWindow):
        MainWindow.resize(825, 625)
        self.centralwidget = QWidget(parent=MainWindow)
        self.inpText = InputTextField(MainWindow, parent=self.centralwidget)
        self.inpText.setStyleSheet(TEXT_FIELD_STYLE)
        self.previewList = QListWidget(parent=self.centralwidget)
        self.previewList.setStyleSheet(TEXT_FIELD_STYLE)
        self.outpText = QPlainTextEdit(parent=self.centralwidget)
        self.outpText.setStyleSheet(TEXT_FIELD_STYLE)
        self.outpText.setReadOnly(True)
        self.vertical = QVBoxLayout()
        self.vertical.addWidget(self.inpText)
        self.vertical.addWidget(self.previewList)
        self.vertical.addWidget(self.outpText)
        self.centralwidget.setLayout(self.vertical)
        self.inpText.setReadOnly(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 807, 26))
        self.mainMenu = QMenu(parent=self.menubar)
        self.openAction = QAction(parent=MainWindow)
        self.openAction.setShortcut(OPEN_SHORTCUT)
        self.mainMenu.addAction(self.openAction)
        self.previewsAction = QAction(parent=MainWindow)
        self.previewsAction.setShortcut(PREVIEWS_COUNT_SHORTCUT)
        self.mainMenu.addAction(self.previewsAction)
        self.menubar.addMenu(self.mainMenu)
        self.exportMenu = QMenu(parent=self.menubar)
        self.resourceAction = QAction(parent=MainWindow)
        self.resourceAction.setShortcut(EXPORT_RESOURCE_SHORTCUT)
        self.exportMenu.addAction(self.resourceAction)
        self.exportAction = QAction(parent=MainWindow)
        self.exportAction.setShortcut(EXPORT_SHORTCUT)
        self.exportMenu.addAction(self.exportAction)

        self.viewMenu = QMenu(parent=self.menubar)
        self.blocksAction = QAction(parent=MainWindow)
        self.viewMenu.addAction(self.blocksAction)
        self.menubar.addAction(self.viewMenu.menuAction())
        self.menubar.addMenu(self.viewMenu)
        self.menubar.addMenu(self.exportMenu)

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(parent=MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Spintax"))
        self.mainMenu.setTitle(_translate("MainWindow", "Программа"))
        self.openAction.setText(_translate("MainWindow", "Открыть файл"))
        self.previewsAction.setText(_translate("MainWindow", "Настройки предпросмотра"))
        self.exportMenu.setTitle(_translate("MainWindow", "Экспорт"))
        self.resourceAction.setText(_translate("MainWindow", "Ресурса"))
        self.exportAction.setText(_translate("MainWindow", "Текстов"))
        self.viewMenu.setTitle(_translate("MainWindow", "Просмотр"))
        self.blocksAction.setText(_translate("MainWindow", "Блоки"))
