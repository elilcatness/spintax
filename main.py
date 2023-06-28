import os
import sys
import ctypes

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QTextCharFormat, QColor, QAction, QIcon
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QPlainTextEdit,
                             QVBoxLayout, QScrollArea, QWidget, QLabel, QDialogButtonBox,
                             QInputDialog, QPushButton, QStatusBar, QMessageBox, QStyle)

from block import Block, Node
from constants import DEFAULT_FIELDS_COUNT, MAX_FIELDS_COUNT, MAIN_ICON
from customClasses import *
from ui.mainWindowUi import UiMainWindow
from utils import getExtension, safeGet, highlight


class Window(QMainWindow, UiMainWindow):
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
        self.cancelAction.triggered.connect(self.cancelBlock)
        self.inpText.addAction(self.cancelAction)
        self.txtAppear = TextAppearance()
        self.txtAppear.connect(self.highlightText)
        self.alternativeWnd = None
        self.node = None
        # self.blocks = []
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

    def highlightText(self):
        # cursor = self.inpText.textCursor()
        # if not cursor.hasSelection():
        #     return
        # doc = self.inpText.document()
        # charsCount = self.inpText.document().characterCount()
        # edges = [cursor.selectionStart(), cursor.selectionEnd()]
        # prevEdges = edges[:]
        # for i, step in enumerate(range(-1, 2, 2)):
        #     while doc.characterAt(edges[i]) not in PUNCTUATION and 0 < edges[i] < charsCount:
        #         edges[i] += step
        # edges[0] = edges[0] + 1 if edges[0] > 0 else 0
        # edges[1] = edges[1] - 1 if edges[1] == charsCount else edges[1]
        # for pos in range(min(min(prevEdges), min(edges)), max(max(prevEdges), max(edges))):
        #     cursor.setPosition(pos)
        #     if cursor.charFormat().background().color().getRgb() != (0, 0, 0, 255):
        #         cursor.clearSelection()
        #         self.inpText.setTextCursor(cursor)
        #         return
        # start, end = edges
        # cursor.setPosition(start)
        # cursor.setPosition(end, cursor.MoveMode.KeepAnchor)
        # text = cursor.selectedText()
        # cursor.clearSelection()
        # self.inpText.setTextCursor(cursor)
        highlightResult = highlight(self.inpText)
        if highlightResult is None:
            return
        text, start = highlightResult
        if not text:
            return
        curBlock = Block(text, start)
        self.node.insertBlock(curBlock)
        try:
            self.blocksChronology.append(self.node.getParts().index(curBlock))
        except ValueError:
            pass
        self.repaint()
        self.showBlock(curBlock)

    def showBlock(self, block: Block):
        self.alternativeWnd = Alternatives(self, block)
        self.alternativeWnd.exec()

    def repaint(self):
        cursor = self.inpText.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(self.inpText.document().characterCount() - 1,
                           cursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        # self.inp_text.setTextCursor(cursor)
        # cursor = self.inp_text.textCursor()
        blocks = self.node.getBlocks()
        for i in range(len(blocks)):
            fmt = QTextCharFormat()
            fmt.setBackground(QColor(self.colors[i % 2]))
            pos = blocks[i].getPos()
            cursor.setPosition(pos)
            cursor.setPosition(pos + len(blocks[i].getOriginal()),
                               cursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(fmt)
            cursor.clearSelection()
        self.outpText.setPlainText(str(self.node))

    def showBlocks(self):
        blocks_wnd = Blocks(self.node.getBlocks())
        blocks_wnd.exec()

    def cancelBlock(self):
        self.node.removeBlock(self.blocksChronology.pop())
        self.repaint()

    @staticmethod
    def _skipSpaces(doc, pos: int, step: int = 1):
        ch_count = doc.characterCount()
        while 0 < pos < ch_count and doc.characterAt(pos) == ' ':
            pos += step
        return pos


class Alternatives(QDialog):
    def __init__(self, parent: Window, block: Block, fieldsCount: int = DEFAULT_FIELDS_COUNT):
        super(Alternatives, self).__init__()
        self.parent = parent
        self.block = block
        self.deleteBlockOnClose = not bool(block.getNodes(skip_original=True))

        self.resize(int(parent.width() * 0.5), int(parent.height() * 0.6))
        self.setWindowTitle('Alternatives')
        self.mainLayout = QVBoxLayout()
        self.scrollArea = QScrollArea()
        self.scrollArea.setContentsMargins(0, 0, 0, 0)
        self.scrollBar = self.scrollArea.verticalScrollBar()

        self.widget = None
        self.layout = None
        self.infoText = None
        self.fields = []
        self.addFieldsBtn = None

        self.initWidget(fieldsCount)
        self.scrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLayout.addWidget(self.scrollArea)

        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Discard |
            QDialogButtonBox.StandardButton.Ok)
        self.mainLayout.addWidget(buttonBox)
        discardBtn = buttonBox.button(QDialogButtonBox.StandardButton.Discard)
        discardBtn.clicked.connect(self.discard)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        statusBar = QStatusBar()
        self.statusLabel = QLabel()
        statusBar.addWidget(self.statusLabel)
        statusBar.setSizeGripEnabled(False)
        self.mainLayout.addWidget(statusBar)
        self.setLayout(self.mainLayout)
        self.painted = []

    def initWidget(self, fieldsCount: int, scrollToBottom: bool = False,
                   scrollToField: int = None):
        for obj in self.widget, self.layout, self.infoText:
            if obj:
                del obj
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        head = QVBoxLayout()
        head.addWidget(QLabel('Выбранный блок'))
        self.infoText = QPlainTextEdit(self.block.getOriginal())
        self.infoText.setMinimumHeight(self.height() // 7)
        self.infoText.setMaximumHeight(self.height() // 7)
        self.infoText.setReadOnly(True)
        head.addWidget(self.infoText)
        head.setSpacing(5)
        self.layout.addLayout(head)
        self.layout.setSpacing(20)
        nodesCount = len(self.block) - 1
        fieldsCount = fieldsCount if nodesCount < fieldsCount else nodesCount
        nodes = self.block.getNodes(skip_original=True)
        for i in range(fieldsCount):
            fieldVertical = QVBoxLayout()
            field = safeGet(self.fields, i)
            usePrevField = field is not None
            if not usePrevField:
                field = QPlainTextEdit()
                node = safeGet(nodes, i)
                if node is not None and node.getOriginal():
                    field.setPlainText(node.getOriginal())
                field.setMaximumHeight(self.height() // 11)
                self.fields.append(field)
            btn = FieldButton(field, 'Delete')
            btn.setStyleSheet('background: #FA5F55')
            btn.pressed.connect(self.deleteField)
            fieldVertical.addWidget(field)
            fieldVertical.addWidget(btn)
            fieldVertical.setSpacing(5)
            self.layout.addLayout(fieldVertical)
        self.addFieldsBtn = QPushButton('Добавить поля')
        self.addFieldsBtn.pressed.connect(self.addFields)
        self.layout.addWidget(self.addFieldsBtn)
        self.widget.setLayout(self.layout)
        self.scrollArea.setWidget(self.widget)
        if scrollToBottom:
            self.scrollBar.setValue(self.scrollBar.maximum())
        elif scrollToField is not None and fieldsCount:
            scrollFieldValue = self.scrollBar.maximum() // fieldsCount
            self.scrollBar.setValue(int(scrollToField * scrollFieldValue * 1.25))

    def discard(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('Confirm an action')
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        dlg.setWindowIcon(icon)
        dlg.setText('Вы уверены, что хотите удалить данный блок?')
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        button = dlg.exec()
        if button == QMessageBox.StandardButton.Yes:
            self.deleteBlockOnClose = True
            self.reject()

    def deleteField(self):
        btn: FieldButton = self.sender()
        field = btn.field()
        idx = self.fields.index(field)
        node = safeGet(self.block.getNodes(skip_original=True), idx)
        if node is not None and node.getOriginal():
            self.block.removeNode(idx + 1)
        self.fields.pop(idx).destroy()
        btn.destroy()
        self.discard() if not self.fields else self.initWidget(
            len(self.fields), scrollToField=idx)
        self.statusLabel.setText(f'Поле #{idx + 1} удалено')

    def addFields(self):
        possibleCount = MAX_FIELDS_COUNT - len(self.fields)
        if possibleCount < 1:
            return self.statusLabel.setText('Больше полей нельзя добавить')
        fieldsCount, ok = QInputDialog.getInt(
            self, 'Add fields', 'Введите количество полей:', min=1, max=possibleCount)
        if not ok:
            return
        self.initWidget(len(self.fields) + fieldsCount, scrollToBottom=True)
        # for _ in range(fieldsCount):
        #     self.addField()
        self.statusLabel.setText(f'Добавлено полей: {fieldsCount}')

    def accept(self):
        self.repaintFields()
        fields = [self.infoText] + self.fields
        nodes = self.block.getNodes(skip_original=True)
        if len(nodes) == 3:
            pass
        emptyAlternatives = True
        nodesOffset = 1
        for i in range(len(fields)):
            text = fields[i].toPlainText()
            if i > 0:
                prevNode = safeGet(nodes, i - nodesOffset)
                if text:
                    emptyAlternatives = False
                    if prevNode is None:
                        nodes.append(Node(text, delimiter=' '))
                    elif text != prevNode.getOriginal():
                        nodes[i - nodesOffset] = Node(text, delimiter=' ')
                elif prevNode is not None and prevNode.getOriginal():
                    del nodes[i - nodesOffset]
                    nodesOffset += 1
            for j in range(i + 1, len(fields)):
                if i != j and text == fields[j].toPlainText() != '':
                    fields[i].setStyleSheet('background: red')
                    fields[j].setStyleSheet('background: red')
                    self.painted += [i, j]
                    break
            else:
                continue
            break
        else:
            self.deleteBlockOnClose = emptyAlternatives
            if not emptyAlternatives and nodes:
                self.block.setNodes(nodes)
            self.close()
        self.parent.repaint()

    def reject(self):
        if self.deleteBlockOnClose:
            self.parent.node.removeBlock(self.block)
        self.parent.repaint()
        super(Alternatives, self).reject()

    def repaintFields(self):
        if not self.painted:
            return
        fields = [self.infoText] + self.fields
        for idx in self.painted:
            fields[idx].setStyleSheet('')


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
    myappid = u'mycompany.myproduct.subproduct.version'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    window = Window()
    # loadCfg(window)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
