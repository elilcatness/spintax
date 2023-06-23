import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QColor, QAction
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog,
                             QLabel, QPlainTextEdit, QVBoxLayout, QDialogButtonBox, QHBoxLayout, QPushButton,
                             QScrollBar, QScrollArea, QWidget)

from block import Block
from constants import PUNCTUATION, DEFAULT_FIELDS_COUNT
from custom_classes import TextAppearance
from ui.mainWindowUi import UiMainWindow
from utils import load_cfg, get_extension


class Alternatives(QDialog):
    def __init__(self, parent: QMainWindow, block: Block):
        super(Alternatives, self).__init__()
        self.parent = parent
        self.widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        self.setWindowTitle('Alternatives')
        self.vertical = QVBoxLayout()
        self.info_label = QLabel('Выбранный блок:')
        self.vertical.addWidget(self.info_label)
        self.info_text = QPlainTextEdit()
        self.info_text.setPlainText(block.get_original())
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(self.height() // 11)
        self.vertical.addWidget(self.info_text)
        self.fields_count = (DEFAULT_FIELDS_COUNT
                             if len(block) < DEFAULT_FIELDS_COUNT else len(block))
        nodes = block.get_nodes(skip_original=True)
        nodes_count = len(nodes)
        self.fields = []
        for i in range(self.fields_count):
            field_vertical = QVBoxLayout()
            field = QPlainTextEdit()
            if i < nodes_count:
                field.setPlainText(nodes[i].get_original())
            field.setMaximumHeight(self.height() // 11)
            field_vertical.addWidget(field)
            btn = QPushButton('Delete')
            btn.pressed.connect(lambda: self.delete_field(i))
            self.vertical.addWidget(field)
            self.vertical.addWidget(btn)
            self.fields.append(field)
        self.button_box = QDialogButtonBox()
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.vertical.addWidget(self.button_box)

        self.scroll = QScrollArea()
        # self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        # self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.scroll.setWidgetResizable(True)

        # self.scroll_area.setLayout(self.vertical)
        self.widget.setLayout(self.vertical)
        self.scroll.setWidget(self.widget)
        self.setLayout(layout)

    def delete_field(self, idx: int):
        btn = self.sender()
        self.vertical.removeWidget(btn)
        self.fields[idx].destroy()
        # layout.removeWidget(field)
        # idx = self.fields.index(field)
        # print(f'{idx=}')
        # self.fields[idx].deleteLater()

    def accept(self):
        fields = [self.info_text] + self.fields
        for i in range(len(fields)):
            for j in range(len(fields)):
                if i == j:
                    continue

        self.close()

    def reject(self):
        ...
        super(Alternatives, self).reject()


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
    colors = ['yellow', 'orange']
    filename = 'input.txt'

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('Spintax')
        self.inp_text.selectionChanged.connect(self.handle_selection)
        self.cancel_action = QAction()
        self.cancel_action.setShortcut('Ctrl+Z')
        self.cancel_action.triggered.connect(self.cancel_block)
        self.inp_text.addAction(self.cancel_action)
        self.text_appearance = TextAppearance()
        self.text_appearance.connect(self.highlight_text)
        self.alternative_wnd = None
        self.blocks = []
        self.blocks_chronology = []
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
                idx = i
                break
        else:
            self.blocks.append(cur_block)
            idx = len(self.blocks) - 1
        self.blocks_chronology.append(idx)
        self.repaint()
        self.alternative_wnd = Alternatives(self, cur_block)
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

    def cancel_block(self):
        self.blocks.pop(self.blocks_chronology.pop())
        self.repaint()

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
