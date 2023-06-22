import sys

from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog,
                             QLabel, QPlainTextEdit, QVBoxLayout)

from constants import PUNCTUATION
from custom_classes import TextAppearance
from utils import load_cfg, get_extension
from block import Block

from ui.mainWindowUi import UiMainWindow


class Alternatives(QDialog):
    def __init__(self, info_text_str: str, blocks: list):
        super(Alternatives, self).__init__()
        self.setWindowTitle('Alternatives')
        self.vertical = QVBoxLayout()
        self.info_label = QLabel('Выбранный блок:')
        self.vertical.addWidget(self.info_label)
        self.info_text = QPlainTextEdit()
        self.info_text.setPlainText(info_text_str)
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(self.height() // 10)
        self.vertical.addWidget(self.info_text)
        self.setLayout(self.vertical)
        self.blocks = blocks


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


class Window(QMainWindow, UiMainWindow):
    colors = ['yellow', 'orange']  # any_colors
    filename = 'input.txt'

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('Spintax')
        self.inp_text.selectionChanged.connect(self.handle_selection)
        self.text_appearance = TextAppearance()
        self.text_appearance.connect(self.highlight_text)
        self.alternative_wnd = None
        self.blocks = []
        self.load_text(self.filename)
        self.inp_text.setReadOnly(True)

        self.blocks_action.triggered.connect(self.show_blocks)
        self.view_menu.addAction(self.blocks_action)
        
    def load_text(self, filename: str):
        ext = get_extension(filename)
        if ext == 'txt':
            with open(filename, encoding='utf-8') as f:
                self.inp_text.insertPlainText(f.read())
        elif ext in ('docx', 'doc'):
            pass
        else:
            raise Exception(f'Invalid extension of {filename}')

    def handle_selection(self):
        if self.text_appearance.is_active():
            self.text_appearance.stop()
        self.text_appearance.start()

    def highlight_text(self):
        cursor = self.inp_text.textCursor()
        if not cursor.hasSelection():
            return
        doc = self.inp_text.document()
        chars_count = self.inp_text.document().characterCount()
        edges = [cursor.selectionStart(), cursor.selectionEnd()]
        prev_edges = edges[:]
        for i, step in enumerate(range(-1, 2, 2)):
            while doc.characterAt(edges[i]) not in PUNCTUATION and 0 < edges[i] < chars_count:
                edges[i] += step
        edges[0] = edges[0] + 1 if edges[0] > 0 else 0
        edges[1] = edges[1] - 1 if edges[1] == chars_count else edges[1]
        # print(edges)
        for pos in edges + prev_edges + [edges[0] + 1]:
            cursor.setPosition(pos)
            # print(f'pos: {pos}, color: {cursor.charFormat().background().color().getRgb()}')
            if cursor.charFormat().background().color().getRgb() != (0, 0, 0, 255):
                # print('clearSelection')
                cursor.clearSelection()
                self.inp_text.setTextCursor(cursor)
                return
        # print()
        start, end = edges
        cursor.setPosition(start)
        cursor.setPosition(end, cursor.MoveMode.KeepAnchor)
        text = cursor.selectedText()
        cursor.clearSelection()
        self.inp_text.setTextCursor(cursor)
        cur_block = Block(text, start)
        for i in range(len(self.blocks)):
            if start < self.blocks[i].get_pos():
                self.blocks.insert(i, cur_block)
                break
        else:
            self.blocks.append(cur_block)
        self.repaint()
        self.alternative_wnd = Alternatives(text, self.blocks)
        self.alternative_wnd.exec()

    def repaint(self):
        cursor = self.inp_text.textCursor()
        cursor.setPosition(0)
        cursor.setPosition(self.inp_text.document().characterCount() - 1,
                           cursor.MoveMode.KeepAnchor)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        # self.inp_text.setTextCursor(cursor)
        # cursor = self.inp_text.textCursor()
        for i in range(len(self.blocks)):
            fmt = QTextCharFormat()
            fmt.setBackground(QColor(self.colors[i % 2]))
            pos = self.blocks[i].get_pos()
            cursor.setPosition(pos)
            cursor.setPosition(pos + len(self.blocks[i].get_original()),
                               cursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(fmt)
            cursor.clearSelection()

    def show_blocks(self):
        blocks_wnd = Blocks(self.blocks)
        blocks_wnd.exec()

    # def _choose_color(self, cursor, start: int, end: int):
    #     doc = self.inp_text.document()
    #     start = self._skip_spaces(doc, start, -1)
    #     end = self._skip_spaces(doc, end)
    #     if doc.characterAt(start) in ENDING_SYMBOLS and doc.characterAt(end) in ENDING_SYMBOLS:
    #         met_regular = False
    #         for pos in range(start + 1, end):
    #             ch = doc.characterAt(pos)
    #             if ch not in '?!.' and not met_regular:
    #                 met_regular = True
    #             elif ch in '?!.' and pos < end - 1:
    #                 return self.any_colors
    #         return self.sentence_colors
    #     if len(cursor.selectedText().split()) == 1:
    #         return self.word_colors
    #     return self.any_colors

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
