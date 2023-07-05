import time

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QMouseEvent, QKeyEvent, QActionEvent, QClipboard
from PyQt6.QtWidgets import QPushButton, QPlainTextEdit, QApplication

from src.constants import TEXT_FIELD_STYLE
from src.utils import changeStyleProperty, getStyleProperty, safeGet, moveBlocks


class TextAppearance(QObject):
    signal = pyqtSignal()

    def __init__(self):
        super(TextAppearance, self).__init__()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.send_signal)

    def connect(self, *args, **kwargs):
        # noinspection PyUnresolvedReferences
        self.signal.connect(*args, **kwargs)

    def start(self):
        self.timer.start(500)

    def is_active(self):
        return self.timer.isActive()

    def stop(self):
        self.timer.stop()

    def send_signal(self):
        # noinspection PyUnresolvedReferences
        self.signal.emit()
        self.timer.stop()


class FieldButton(QPushButton):
    def __init__(self, field, *args, **kwargs):
        super(FieldButton, self).__init__(*args, **kwargs)
        self._field = field

    def field(self):
        return self._field


class InputTextField(QPlainTextEdit):
    def __init__(self, _parent, *args, **kwargs):
        super(InputTextField, self).__init__(*args, **kwargs)
        self.parent = _parent

    def mousePressEvent(self, event: QMouseEvent):
        pos = self.cursorForPosition(event.pos()).position()
        if self.parent.node is not None:
            for block in self.parent.node.getBlocks():
                if block.getPos() <= pos <= block.getEnd():
                    self.parent.showBlock(block)
        try:
            super(InputTextField, self).mousePressEvent(event)
        except RuntimeError:
            pass


class AlternativeTextField(InputTextField):
    focusInProcess = False

    def focusOutEvent(self, event):
        try:
            texts = [field.toPlainText() for field in self.parent.fields]
            if texts != self.parent.savedTexts:
                self.parent.preSave()
            defaultBorderColor = getStyleProperty(TEXT_FIELD_STYLE, 'border-color', 'white')
            style = changeStyleProperty(self.styleSheet(), 'border-color', defaultBorderColor)
            self.setStyleSheet(style)
            cursor = self.textCursor()
            if cursor.hasSelection():
                cursor.clearSelection()
                self.setTextCursor(cursor)
            super(AlternativeTextField, self).focusOutEvent(event)
        except RuntimeError:
            pass

    def focusInEvent(self, event):
        if self.focusInProcess:
            return
        try:
            print('focusInEvent')
            texts = [field.toPlainText() for field in self.parent.fields]
            if texts != self.parent.savedTexts:
                self.parent.preSave(textToFocus=self.toPlainText())
                return
            try:
                idx = self.parent.fields.index(self)
            except IndexError:
                print('IndexError occurred')
                exit()
            node = safeGet(self.parent.block.getNodes(), idx)
            if node is not None:
                self.parent.node = node
            else:
                self.parent.node = None
            style = changeStyleProperty(self.styleSheet(), 'border-color', '#0078D4')
            self.setStyleSheet(style)
            super(AlternativeTextField, self).focusInEvent(event)
        except RuntimeError:
            pass

    def keyPressEvent(self, event):
        repaintBlocks = False
        blocks = []
        if self.parent.node is not None and (blocks := self.parent.node.getBlocks()):
            modifiers = event.modifiers()
            text = event.text()
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                key = event.key()
                if key == Qt.Key.Key_V:
                    clipboard = QApplication.clipboard()
                    clipText = clipboard.text()
                    if clipText:
                        pos, offset = self.textCursor().position(), len(clipText)
                        self._handleBlocks(clipText, blocks, pos, offset)
                        repaintBlocks = True
                elif key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace, Qt.Key.Key_X):
                    cursor = self.textCursor()
                    if cursor.hasSelection() and (pos := cursor.selectionEnd()) > 0:
                        selectedText = cursor.selectedText()
                        offset = len(selectedText)
                        self._handleBlocks(self.toPlainText(), blocks, pos, -offset, action='remove')
                        repaintBlocks = True
            elif not modifiers and text and (pos := self.textCursor().selectionEnd()) > 0:
                start = self.textCursor().selectionStart()
                offset = 1 if pos - start <= 1 else pos - start
                print(f'{offset=}')
                if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                    cursor = self.textCursor()
                    # print(f'{cursor.selectionStart()=}, {cursor.selectionEnd()=}')
                    self._handleBlocks(text, blocks, pos, -offset, action='remove')
                else:
                    self._handleBlocks(text, blocks, pos, 1)
                repaintBlocks = True
        super(AlternativeTextField, self).keyPressEvent(event)
        if repaintBlocks and blocks:
            self.parent.paintBlocks(self, blocks, self.parent.colors)

    def _handleBlocks(self, text: str, blocks, pos: int, offset: int, action: str = 'add'):
        if not moveBlocks(blocks, pos, offset):
            statusText = 'Не удалось переместить блоки'
            try:
                idx = self.parent.fields.index(self)
                statusText += f' в поле #{idx}'
            except IndexError:
                pass
            self.parent.statusLabel.setText(statusText)
        else:
            newText = self.toPlainText()
            if action == 'add':
                newText = newText[:pos] + text + newText[pos:]
            elif action == 'remove':
                newText = newText[:pos + offset] + newText[pos:]
            else:
                raise Exception('Unknown action passed into _handleBlocks')
            self.parent.node.setParts(newText)
            for block in blocks:
                self.parent.node.insertBlock(block)

    # def keyPressEvent(self, event: QKeyEvent):
    #     if event.isInputEvent() and self.parent.node is not None:
    #         if event.key() == Qt.Key.Key_V and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
    #             pass
    #         # pos = self.textCursor().position()
    #         # blocks = self.parent.node.getBlocks()
    #         # for block in blocks:
    #         #     if block.getPos() >= pos:
    #         #         block.setPos(block.getPos() + 1)
    #         # self.parent.paintBlocks(self, blocks, self.parent.colors)
    #     super(AlternativeTextField, self).keyPressEvent(event)


__all__ = ['TextAppearance', 'FieldButton', 'AlternativeTextField', 'InputTextField']
