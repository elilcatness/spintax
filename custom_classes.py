from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QTextEdit, QApplication


class TextEdit(QTextEdit):
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        for action in menu.actions():
            if action.text() == 'Копировать':
                menu.removeAction(action)
                break
        cpy_txt_action = QAction('Копировать текст', self)
        cpy_txt_action.triggered.connect(self.copy_text)
        menu.addAction(cpy_txt_action)
        menu.exec(event.globalPos())

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.textCursor().selectedText(), clipboard.Mode.Clipboard)


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