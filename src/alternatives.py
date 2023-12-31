import time

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QAction, QTextCharFormat, QColor, QTextCursor
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QMenuBar, QMenu, QScrollArea,
                             QDialogButtonBox, QStatusBar, QLabel, QMessageBox,
                             QStyle, QInputDialog, QPlainTextEdit, QWidget, QPushButton)

from src.block import Block, Node
from src.constants import (DEFAULT_FIELDS_COUNT, SCROLL_AREA_STYLE, MAX_FIELDS_COUNT,
                           TEXT_FIELD_STYLE, PUNCTUATION)
from src.customClasses import FieldButton, AlternativeTextField
from src.utils import safeGet, expand


class HighlightMixin:
    alternativeWnd = None
    generator = None
    node = None
    outpText = None
    savedText = None
    previews = None

    def repaint(self):
        pass

    def refreshPreviews(self):
        pass

    def showBlock(self, block: Block):
        # noinspection PyTypeChecker
        self.alternativeWnd = Alternatives(self, block)
        self.alternativeWnd.exec()
        if not isinstance(self, Alternatives):
            self.repaint()
            if (text := self.outpText.toPlainText()) != self.savedText:
                self.savedText = text
                self.generator = expand(self.node)
                self.previews = []
                self.refreshPreviews()

    def highlight(self, textField: QPlainTextEdit, node):
        cursor = textField.textCursor()
        if not cursor.hasSelection():
            return
        doc = textField.document()
        charsCount = doc.characterCount()
        edges = [cursor.selectionStart(), cursor.selectionEnd()]
        prevEdges = edges[:]
        for i, step in enumerate(range(-1, 2, 2)):
            while doc.characterAt(edges[i]) not in PUNCTUATION and 0 < edges[i] < charsCount:
                edges[i] += step
        edges[0] = edges[0] + 1 if edges[0] > 0 else 0
        edges[1] = edges[1] - 1 if edges[1] == charsCount else edges[1]
        for pos in range(min(min(prevEdges), min(edges)), max(max(prevEdges), max(edges))):
            cursor.setPosition(pos)
            if cursor.charFormat().background().color().getRgb() != (0, 0, 0, 255):
                cursor.clearSelection()
                textField.setTextCursor(cursor)
                return
        start, end = edges
        cursor.setPosition(start)
        cursor.setPosition(end, cursor.MoveMode.KeepAnchor)
        text = cursor.selectedText()
        cursor.clearSelection()
        textField.setTextCursor(cursor)
        curBlock = Block(text, start)
        node.insertBlock(curBlock)
        try:
            idx = node.getParts().index(curBlock)
        except ValueError:
            idx = None
        return curBlock, idx

    @staticmethod
    def paintBlocks(textField: QPlainTextEdit, blocks, colors: list):
        cursor = textField.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(textField.document().characterCount() - 1,
                           cursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        for i in range(len(blocks)):
            fmt = QTextCharFormat()
            fmt.setBackground(QColor(colors[i % 2]))
            pos = blocks[i].getPos()
            cursor.setPosition(pos)
            cursor.setPosition(pos + len(blocks[i].getOriginal()),
                               cursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(fmt)
            cursor.clearSelection()


class Alternatives(QDialog, HighlightMixin):
    colors = ['yellow', 'orange']

    def __init__(self, parent, block: Block,
                 fieldsCount: int = DEFAULT_FIELDS_COUNT):
        super(Alternatives, self).__init__()
        self.parent = parent
        self.setWindowIcon(self.parent.windowIcon())
        self.block = block
        self.deleteBlockOnClose = not bool(block.getNodes())

        w0, h0 = (0.5, 0.6) if not isinstance(self.parent, Alternatives) else (1, 1)
        self.resize(int(parent.width() * w0), int(parent.height() * h0))
        self.setWindowTitle('Alternatives')
        self.mainLayout = QVBoxLayout()
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(QRect(0, 0, 807, 26))
        self.menu = QMenu('Программа')
        self.highlightAction = QAction('Выделить текст')
        self.highlightAction.setShortcut('Ctrl+H')
        # noinspection PyUnresolvedReferences
        self.highlightAction.triggered.connect(self.highlight)
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
        self.node = None
        self.isSaving = False

        self.initWidget(fieldsCount, scrollToField=0)
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

        # self.chronologies = [[] for _ in range()]

    def initWidget(self, fieldsCount: int, scrollToBottom: bool = False,
                   scrollToField: int = None, textToFocus: str = None,
                   cursorStart: int = 0, cursorEnd: int = 0):
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
        nodes = self.block.getNodes()
        for i in range(fieldsCount):
            fieldVertical = QVBoxLayout()
            field = safeGet(self.fields, i)
            usePrevField = field is not None
            node = safeGet(nodes, i)
            if not usePrevField:
                field = AlternativeTextField(self, self)
                field.setStyleSheet(TEXT_FIELD_STYLE)
                if node is not None and node.getOriginal():
                    field.setPlainText(node.getOriginal())
                field.setMaximumHeight(self.height() // 11)
                self.fields.append(field)
            if node is not None:
                blocks = node.getBlocks()
                if blocks:
                    self.paintBlocks(field, blocks, self.colors)
            if textToFocus and field.toPlainText() == textToFocus:
                textToFocus = None
                scrollToField = i
            btn = FieldButton(field, 'Delete')
            btn.setStyleSheet('background: #FA5F55')
            # noinspection PyUnresolvedReferences
            btn.pressed.connect(self.deleteField)
            fieldVertical.addWidget(field)
            fieldVertical.addWidget(btn)
            fieldVertical.setSpacing(5)
            self.layout.addLayout(fieldVertical)
        if not self.savedTexts:
            self.savedTexts = [field.toPlainText() for field in self.fields]
        self.addFieldsBtn = QPushButton('Добавить поля')
        self.addFieldsBtn.setStyleSheet('background: white')
        # noinspection PyUnresolvedReferences
        self.addFieldsBtn.pressed.connect(self.addFields)
        self.layout.addWidget(self.addFieldsBtn)
        self.widget.setLayout(self.layout)
        self.scrollArea.setWidget(self.widget)
        if scrollToField is not None and fieldsCount:
            field = safeGet(self.fields, scrollToField, None)
            if field:
                self.scrollArea.ensureWidgetVisible(self.fields[scrollToField])
                self.fields[scrollToField].setFocus()
                if cursorStart and cursorEnd:
                    cursor = self.fields[scrollToField].textCursor()
                    cursor.setPosition(cursorStart)
                    cursor.setPosition(cursorEnd, cursor.MoveMode.KeepAnchor)
                    self.fields[scrollToField].setTextCursor(cursor)
            elif not scrollToBottom:
                scrollToBottom = True
        if scrollToBottom:
            self.scrollBar.setValue(self.scrollBar.maximum())

    def moveBlocks(self):
        # noinspection PyTypeChecker
        field: AlternativeTextField = self.sender()
        idx = self.fields.index(field)
        node = self.block.getNode(idx)
        if node is None:
            return
        text = field.toPlainText()
        original = node.getOriginal()
        if text == original:
            return
        pos = field.textCursor().position()
        for block in node.getBlocks():
            if block.getPos() >= pos:
                block.setPos(block.getPos() + 1)
        self.paintBlocks(field, node, self.colors)

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

    def highlight(self, *args):
        self.statusLabel.setText('')
        texts = []
        activeField = None
        for field in self.fields:
            if field.hasFocus():
                activeField = field
            texts.append(field.toPlainText())
        # well, yep, there are two saves, but what can you do to me?
        if activeField is None:
            return self.statusLabel.setText(
                'Для выделения должно быть активным одно из полей')
        if not activeField.toPlainText():
            return self.statusLabel.setText(
                'Поле, в котором Вы пытаетесь выделить текст, пустое!')
        if texts != self.savedTexts:
            cursor = activeField.textCursor()
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            self.preSave(textToFocus=activeField.toPlainText(),
                         cursorStart=start, cursorEnd=end)
            return self.highlight()
            # return self.statusLabel.setText('Поля были сохранены перед выделением')
        idx = self.fields.index(activeField)
        node = self.block.getNode(idx)
        highlightResults = super(Alternatives, self).highlight(activeField, node)
        if highlightResults is not None:
            block, _ = highlightResults
            self.paintBlocks(activeField, node.getBlocks(), self.colors)
            self.node = node
            self.showBlock(block)
            self.paintBlocks(activeField, node.getBlocks(), self.colors)

    def deleteField(self):
        if len(self.fields) == 1:
            return self.discard()
        # noinspection PyTypeChecker
        btn: FieldButton = self.sender()
        field = btn.field()
        idx = self.fields.index(field)
        node = safeGet(self.block.getNodes(), idx)
        if node is not None and node.getOriginal():
            self.block.removeNode(idx + 1)
        self.fields.pop(idx).destroy()
        btn.destroy()
        self.initWidget(len(self.fields), scrollToField=idx)
        self.statusLabel.setText(f'Поле #{idx + 1} удалено')

    def addFields(self):
        possibleCount = MAX_FIELDS_COUNT - len(self.fields)
        if possibleCount < 1:
            return self.statusLabel.setText('Больше полей нельзя добавить')
        fieldsCount, ok = QInputDialog.getInt(
            self, 'Add fields', 'Введите количество полей:', min=1, max=possibleCount)
        if not ok:
            return
        self.initWidget(len(self.fields) + fieldsCount)
        # for _ in range(fieldsCount):
        #     self.addField()
        self.statusLabel.setText(f'Добавлено полей: {fieldsCount}')

    def preSave(self, **kwargs):
        if not self.save():
            return
        fieldsCount = len(self.fields)
        self.fields = []
        self.initWidget(fieldsCount, **kwargs)
        self.save()

    def save(self):
        self.repaintFields()
        fields = [self.infoText] + self.fields
        nodes = self.block.getNodes()
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
                    # delimiter = ' ' if not isinstance(self.parent, Alternatives) else ''
                    if prevNode is None:
                        nodes.append(Node(text))
                    elif text != prevNode.getOriginal():
                        nodes[i - nodesOffset] = Node(text)
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
            if not isinstance(self.parent, Alternatives):
                self.parent.repaint()
            else:
                try:
                    idx = self.parent.block.getNodes().index(self.parent.node)
                except IndexError:
                    return self.parent.statusLabel.setText(
                        'Не удалось убрать выделение с блока после удаления')
                field = self.parent.fields[idx]
                self.parent.paintBlocks(field, self.parent.node.getBlocks(),
                                        self.parent.colors)
        super(Alternatives, self).reject()

    def repaintFields(self):
        if not self.painted:
            return
        fields = [self.infoText] + self.fields
        for idx in self.painted:
            fields[idx].setStyleSheet('')

    def _getNode(self, field):
        return safeGet(self.block.getNodes(), self.fields.index(field))
