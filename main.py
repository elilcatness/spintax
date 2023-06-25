import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QColor, QAction, QMouseEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QPlainTextEdit,
                             QVBoxLayout, QScrollArea, QWidget, QLabel, QDialogButtonBox)

from block import Block, Node
from constants import PUNCTUATION, DEFAULT_FIELDS_COUNT
from custom_classes import *
from ui.mainWindowUi import UiMainWindow
from utils import load_cfg, get_extension, safe_get


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
        self.show_block(cur_block)

    def show_block(self, block: Block):
        self.alternative_wnd = Alternatives(self, block)
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


class Alternatives(QDialog):
    def __init__(self, parent: Window, block: Block):
        super(Alternatives, self).__init__()
        self.parent = parent
        self.block = block
        self.deleteBlockOnClose = not bool(block.get_nodes(skip_original=True))

        self.resize(int(parent.width() * 0.5), int(parent.height() * 0.6))
        self.setWindowTitle('Alternatives')
        mainLayout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        head = QVBoxLayout()
        head.addWidget(QLabel('Выбранный блок'))
        self.infoText = QPlainTextEdit(block.get_original())
        self.infoText.setMaximumHeight(self.height() // 7)
        self.infoText.setReadOnly(True)
        head.addWidget(self.infoText)
        head.setSpacing(5)
        self.layout.addLayout(head)
        self.layout.setSpacing(20)
        self.fields_count = (DEFAULT_FIELDS_COUNT
                             if len(block) < DEFAULT_FIELDS_COUNT else len(block))
        nodes = block.get_nodes(skip_original=True)
        nodes_count = len(nodes)
        self.fields = []
        for i in range(self.fields_count):
            fieldVertical = QVBoxLayout()
            field = QPlainTextEdit()
            if i < nodes_count:
                field.setPlainText(nodes[i].get_original())
            field.setMaximumHeight(self.height() // 11)
            btn = FieldButton(field, 'Delete')
            btn.pressed.connect(self.deleteField)
            fieldVertical.addWidget(field)
            fieldVertical.addWidget(btn)
            fieldVertical.setSpacing(5)
            self.layout.addLayout(fieldVertical)
            self.fields.append(field)
        self.widget.setLayout(self.layout)
        scroll_area.setWidget(self.widget)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(scroll_area)
        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(Qt.Orientation.Horizontal)
        buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        mainLayout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.setLayout(mainLayout)
        self.painted = []

    def deleteField(self):
        btn: FieldButton = self.sender()
        field = btn.field()
        idx = self.fields.index(field)
        nodes = self.block.get_nodes()
        node = safe_get(nodes, idx)
        if node is not None and node.get_original():
            del nodes[idx], node
        btn.deleteLater()
        field.deleteLater()
        del self.fields[idx], field, btn
        if not self.fields:
            self.deleteBlockOnClose = True
            self.reject()
        self.widget.adjustSize()
        self.repaintFields()

    def accept(self):
        self.repaintFields()
        fields = [self.infoText] + self.fields
        nodes = self.block.get_nodes(skip_original=True)
        if len(nodes) == 3:
            pass
        emptyAlternatives = True
        nodesOffset = 1
        for i in range(len(fields)):
            text = fields[i].toPlainText()
            if i > 0:
                prevNode = safe_get(nodes, i - nodesOffset)
                if text:
                    emptyAlternatives = False
                    if prevNode is None:
                        nodes.append(Node(text, delimiter=' '))
                    elif text != prevNode.get_original():
                        nodes[i - nodesOffset] = Node(text, delimiter=' ')
                elif prevNode is not None and prevNode.get_original():
                    del nodes[i - nodesOffset]
                    nodesOffset += 1
            for j in range(i + 1, len(fields)):
                if i != j and text == fields[j].toPlainText() != '':
                    fields[i].setStyleSheet('background: red')
                    fields[j].setStyleSheet('background: red')
                    self.painted += [i, j]
                    break
            else:
                continue
            break
        else:
            self.deleteBlockOnClose = emptyAlternatives
            if not emptyAlternatives and nodes:
                self.block.set_nodes(nodes)
            self.close()

    def reject(self):
        if self.deleteBlockOnClose:
            self.parent.blocks.remove(self.block)
            self.parent.repaint()
        super(Alternatives, self).reject()

    def repaintFields(self):
        if not self.painted:
            return
        fields = [self.infoText] + self.fields
        for idx in self.painted:
            fields[idx].setStyleSheet('')


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
    app = QApplication(sys.argv)
    window = Window()
    load_cfg(window)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
