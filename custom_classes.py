from PyQt6.QtCore import QObject, pyqtSignal, QTimer


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