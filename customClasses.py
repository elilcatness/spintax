from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QPushButton, QPlainTextEdit

from constants import TEXT_FIELD_STYLE
from utils import changeStyleProperty, getStyleProperty


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
        node = self.parent._getNode(self)
        if node is not None:
            for block in node.getBlocks():
                if block.getPos() <= pos <= block.getEnd():
                    self.parent.showBlock(block)
        super(InputTextField, self).mousePressEvent(event)


class AlternativeTextField(QPlainTextEdit):
    def focusOutEvent(self, event):
        defaultBorderColor = getStyleProperty(TEXT_FIELD_STYLE, 'border-color', 'white')
        style = changeStyleProperty(self.styleSheet(), 'border-color', defaultBorderColor)
        self.setStyleSheet(style)
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.clearSelection()
            self.setTextCursor(cursor)
        super(AlternativeTextField, self).focusOutEvent(event)

    def focusInEvent(self, event):
        style = changeStyleProperty(self.styleSheet(), 'border-color', '#0078D4')
        self.setStyleSheet(style)
        super(AlternativeTextField, self).focusInEvent(event)


__all__ = ['TextAppearance', 'FieldButton', 'AlternativeTextField']
