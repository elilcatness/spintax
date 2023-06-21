import sys
from random import choice

from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QPlainTextEdit, QVBoxLayout

from constants import PUNCTUATION, ENDING_SYMBOLS
from custom_classes import TextEdit, TextAppearance
from utils import load_cfg


class Alternatives(QDialog):
    def __init__(self, info_text_str: str):
        super(Alternatives, self).__init__()
        self.setWindowTitle('Alternatives')
        self.vertical = QVBoxLayout()
        self.info_label = QLabel('Выбранная структура:')
        self.vertical.addWidget(self.info_label)
        self.info_text = QPlainTextEdit()
        self.info_text.setPlainText(info_text_str)
        self.info_text.setReadOnly(True)
        self.vertical.addWidget(self.info_text)
        self.setLayout(self.vertical)


class Window(QMainWindow):
    any_colors = ['yellow', 'orange']
    sentence_colors = ['#d4ebf2', '#adcfe6']
    word_colors = ['#cf9fff', 'violet']

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setWindowTitle('Spintax')
        self.text_widget = TextEdit()
        self.text_widget.selectionChanged.connect(self.handle_selection)
        self.setCentralWidget(self.text_widget)
        self.text_appearance = TextAppearance()
        self.text_appearance.connect(self.highlight_text)
        self.alternative_wnd = None

    def handle_selection(self):
        if self.text_appearance.is_active():
            self.text_appearance.stop()
        self.text_appearance.start()

    def highlight_text(self):
        cursor = self.text_widget.textCursor()
        if not cursor.hasSelection():
            return
        doc = self.text_widget.document()
        chars_count = self.text_widget.document().characterCount()
        edges = [cursor.selectionStart(), cursor.selectionEnd()]
        for i, step in enumerate(range(-1, 2, 2)):
            while doc.characterAt(edges[i]) not in PUNCTUATION and 0 < edges[i] < chars_count:
                edges[i] += step
        start, end = edges
        cursor.setPosition(start + 1 if start > 0 else 0)
        cursor.setPosition(end - 1 if end == chars_count else end, cursor.MoveMode.KeepAnchor)
        colors = self._choose_color(cursor, start, end)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(choice(colors)))
        cursor.mergeCharFormat(fmt)
        text = cursor.selectedText()
        cursor.clearSelection()
        self.text_widget.setTextCursor(cursor)
        self.alternative_wnd = Alternatives(text)
        self.alternative_wnd.exec()

    def _choose_color(self, cursor, start: int, end: int):
        doc = self.text_widget.document()
        start = self._skip_spaces(doc, start, -1)
        end = self._skip_spaces(doc, end)
        if doc.characterAt(start) in ENDING_SYMBOLS and doc.characterAt(end) in ENDING_SYMBOLS:
            met_regular = False
            for pos in range(start + 1, end):
                ch = doc.characterAt(pos)
                if ch not in '?!.' and not met_regular:
                    met_regular = True
                elif ch in '?!.' and pos < end - 1:
                    return self.any_colors
            return self.sentence_colors
        if len(cursor.selectedText().split()) == 1:
            return self.word_colors
        return self.any_colors

    @staticmethod
    def _skip_spaces(doc, pos: int, step: int = 1):
        ch_count = doc.characterCount()
        while 0 < pos < ch_count and doc.characterAt(pos) == ' ':
            pos += step
        return pos


def main():
    app = QApplication(sys.argv)
    window = Window()
    load_cfg(window)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
