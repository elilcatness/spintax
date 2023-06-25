from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QPushButton, QPlainTextEdit

from constants import TAB_CODE


class TextAppearance(QObject):
    signal = pyqtSignal()

    def __init__(self):
        super(TextAppearance, self).__init__()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.send_signal)

    def connect(self, *args, **kwargs):
        self.signal.connect(*args, **kwargs)

    def start(self):
        self.timer.start(500)

    def is_active(self):
        return self.timer.isActive()

    def stop(self):
        self.timer.stop()

    def send_signal(self):
        self.signal.emit()


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
        for block in self.parent.blocks:
            if block.get_pos() <= pos <= block.get_end():
                self.parent.show_block(block)
        super(InputTextField, self).mousePressEvent(event)


# class AlternativeTextEdit(QPlainTextEdit):
#     def keyPressEvent(self, event: QKeyEvent):
#         if event.key() == TAB_CODE:
#             nextWidget = self.nextInFocusChain()
#             print(f'{nextWidget=}')
#             print(f'{nextWidget.parent()=}')
#             nextWidget.setStyleSheet('background: red')
#             # if nextWidget:
#                 # self.clearFocus()
#                 # nextWidget.setFocus()
#         else:
#             super(AlternativeTextEdit, self).keyPressEvent(event)


__all__ = ['TextAppearance', 'FieldButton']