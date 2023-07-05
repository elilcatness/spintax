import os
import sys
import ctypes

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QPlainTextEdit, QVBoxLayout

from alternatives import HighlightMixin
from block import Node
from constants import MAIN_ICON
from customClasses import *
from ui.mainWindowUi import UiMainWindow
from utils import getExtension


class Window(QMainWindow, UiMainWindow, HighlightMixin):
    colors = ['yellow', 'orange']
    filename = 'input.txt'

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('Spintax')
        self.setWindowIcon(QIcon(os.path.join('icons', MAIN_ICON)))
        self.inpText.selectionChanged.connect(self.handleSelection)
        self.cancelAction = QAction()
        self.cancelAction.setShortcut('Ctrl+Z')
        # noinspection PyUnresolvedReferences
        self.cancelAction.triggered.connect(self.cancelBlock)
        self.inpText.addAction(self.cancelAction)
        self.txtAppear = TextAppearance()
        self.txtAppear.connect(self.highlight)
        self.alternativeWnd = None
        self.node = None
        self.blocksChronology = []
        self.loadText(self.filename)
        self.inpText.setReadOnly(True)

        self.blocksAction.triggered.connect(self.showBlocks)
        self.viewMenu.addAction(self.blocksAction)

    def loadText(self, filename: str):
        ext = getExtension(filename)
        if ext == 'txt':
            with open(filename, encoding='utf-8') as f:
                text = f.read()
        elif ext in ('docx', 'doc'):
            pass
        else:
            raise Exception(f'Invalid extension of {filename}')
        self.inpText.insertPlainText(text)
        self.outpText.insertPlainText(text)
        self.node = Node(text)

    def handleSelection(self):
        if self.txtAppear.is_active():
            self.txtAppear.stop()
        self.txtAppear.start()

    def highlight(self, *args):
        highlightResults = super(Window, self).highlight(self.inpText, self.node)
        if highlightResults is None:
            return
        block, idx = highlightResults
        self.repaint()
        self.showBlock(block)
        if idx is not None:
            self.blocksChronology.append(idx)

    # def highlightText(self):
    #     highlightResult = highlight(self.inpText)
    #     if highlightResult is None:
    #         return
    #     text, start = highlightResult
    #     if not text:
    #         return
    #     curBlock = Block(text, start)
    #     self.node.insertBlock(curBlock)
    #     try:
    #         self.blocksChronology.append(self.node.getParts().index(curBlock))
    #     except ValueError:
    #         pass
    #     self.repaint()
    #     self.showBlock(curBlock)

    def repaint(self):
        self.paintBlocks(self.inpText, self.node.getBlocks(), self.colors)
        self.outpText.setPlainText(str(self.node))

    def showBlocks(self):
        blocks_wnd = Blocks(self.node.getBlocks())
        blocks_wnd.exec()

    def cancelBlock(self):
        self.node.removeBlock(self.blocksChronology.pop())
        self.repaint()

    def _getNode(self, _):
        return self.node

    @staticmethod
    def _skipSpaces(doc, pos: int, step: int = 1):
        ch_count = doc.characterCount()
        while 0 < pos < ch_count and doc.characterAt(pos) == ' ':
            pos += step
        return pos


class Blocks(QDialog):
    def __init__(self, blocks: list):
        super(Blocks, self).__init__()
        self.setWindowTitle('Блоки')
        self.vertical = QVBoxLayout()
        for block in blocks:
            text = QPlainTextEdit()
            text.setPlainText(str(block))
            text.setMaximumHeight(self.height() // 10)
            text.setReadOnly(True)
            self.vertical.addWidget(text)
        self.setLayout(self.vertical)


def main():
    myappid = u'elilcat.spintax.spintax.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    window = Window()
    # loadCfg(window)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
