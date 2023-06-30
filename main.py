import os
import sys
import ctypes

from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QTextCharFormat, QColor, QAction, QIcon
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QPlainTextEdit,
                             QVBoxLayout, QScrollArea, QWidget, QLabel, QDialogButtonBox,
                             QInputDialog, QPushButton, QStatusBar, QMessageBox, QStyle,
                             QMenu, QMenuBar)

from block import Block, Node
from constants import DEFAULT_FIELDS_COUNT, MAX_FIELDS_COUNT, MAIN_ICON, TEXT_FIELD_STYLE, SCROLL_AREA_STYLE
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
        # noinspection PyUnresolvedReferences
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

    def _getNode(self, _):
        return self.node

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
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(QRect(0, 0, 807, 26))
        self.menu = QMenu('Программа')
        self.highlightAction = QAction('Выделить текст')
        self.highlightAction.setShortcut('Ctrl+H')
        # noinspection PyUnresolvedReferences
        self.highlightAction.triggered.connect(self.highlightText)
        self.menu.addAction(self.highlightAction)
        self.menuBar.addMenu(self.menu)
        self.mainLayout.setMenuBar(self.menuBar)
        self.menuBar.raise_()
        self.scrollArea = QScrollArea()
        self.scrollArea.setStyleSheet(SCROLL_AREA_STYLE)
        self.scrollArea.setContentsMargins(0, 0, 0, 0)
        self.scrollBar = self.scrollArea.verticalScrollBar()

        self.widget = None
        self.layout = None
        self.infoText = None
        self.fields = []
        self.addFieldsBtn = None
        self.painted = []
        self.savedTexts = []

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
        # noinspection PyUnresolvedReferences
        discardBtn.clicked.connect(self.discard)
        # noinspection PyUnresolvedReferences
        buttonBox.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        buttonBox.rejected.connect(self.reject)
        statusBar = QStatusBar()
        self.statusLabel = QLabel()
        statusBar.addWidget(self.statusLabel)
        statusBar.setSizeGripEnabled(False)
        self.mainLayout.addWidget(statusBar)
        self.setLayout(self.mainLayout)

    # noinspection PyUnresolvedReferences
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
        self.infoText.setStyleSheet(TEXT_FIELD_STYLE)
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
                field = AlternativeTextField(self)
                field.setStyleSheet(TEXT_FIELD_STYLE)
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
        self.addFieldsBtn.setStyleSheet('background: white')
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

    def highlightText(self):
        self.statusLabel.setText('')
        texts = []
        activeField = None
        for field in self.fields:
            if field.hasFocus():
                activeField = field
            texts.append(field.toPlainText())
        # well, yep, there are two saves, but what can you do to me?
        if texts != self.savedTexts:
            self.save()
            fieldsCount = len(self.fields)
            self.fields = []
            self.initWidget(fieldsCount)
            self.save()
            return self.statusLabel.setText('Поля были сохранены перед выделением')
        if activeField is None:
            return self.statusLabel.setText(
                'Для выделения должно быть активным одно из полей')
        print(f'Highlighting at {self.fields.index(activeField)}')

    def deleteField(self):
        # noinspection PyTypeChecker
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

    def save(self):
        self.repaintFields()
        fields = [self.infoText] + self.fields
        nodes = self.block.getNodes(skip_original=True)
        emptyNodes = True
        nodesOffset = 1
        savedTexts = []
        for i in range(len(fields)):
            text = fields[i].toPlainText()
            if i > 0:
                savedTexts.append(text)
                prevNode = safeGet(nodes, i - nodesOffset)
                if text:
                    emptyNodes = False
                    if prevNode is None:
                        nodes.append(Node(text, delimiter=' '))
                    elif text != prevNode.getOriginal():
                        nodes[i - nodesOffset] = Node(text, delimiter=' ')
                elif prevNode is not None and prevNode.getOriginal():
                    del nodes[i - nodesOffset]
                    nodesOffset += 1
            for j in range(i + 1, len(fields)):
                if i != j and text == fields[j].toPlainText() != '':
                    fields[i].setStyleSheet(TEXT_FIELD_STYLE + 'background: red')
                    fields[j].setStyleSheet(TEXT_FIELD_STYLE + 'background: red')
                    self.painted += [i, j]
                    return False
        self.deleteBlockOnClose = emptyNodes
        if not emptyNodes and nodes:
            self.block.setNodes(nodes)
        self.savedTexts = savedTexts
        return True

    def accept(self):
        if self.save():
            self.reject()

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

    def _getNode(self, field):
        return safeGet(self.block.getNodes(skip_original=True), self.fields.index(field))


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
