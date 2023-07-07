import os
import shutil
import sys
import ctypes

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QPlainTextEdit, QVBoxLayout, QFileDialog, QMessageBox, \
    QStyle, QInputDialog, QListWidgetItem

from src.alternatives import HighlightMixin
from src.block import Node
from src.constants import MAIN_ICON, EXPORT_RESOURCE_DIR, EXPORT_RESOURCE_DEFAULT_FILENAME, RESTRICTED_SYMBOLS, \
    DEFAULT_PREVIEWS_COUNT
from src.customClasses import *
from src.utils import expand
from ui.mainWindowUi import UiMainWindow


class Window(QMainWindow, UiMainWindow, HighlightMixin):
    colors = ['yellow', 'orange']

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('Spintax')
        self.setWindowIcon(QIcon(os.path.join('icons', MAIN_ICON)))
        self.inpText.selectionChanged.connect(self.handleSelection)
        self.previewList.itemClicked.connect(self.previewText)
        self.cancelAction = QAction()
        self.cancelAction.setShortcut('Ctrl+Z')
        # noinspection PyUnresolvedReferences
        self.cancelAction.triggered.connect(self.cancelBlock)
        self.inpText.addAction(self.cancelAction)
        self.txtAppear = TextAppearance()
        self.txtAppear.connect(self.highlight)

        self.alternativeWnd = None
        self.node = None
        self.blocksChronology = []
        self.previewsCount = DEFAULT_PREVIEWS_COUNT
        self.savedText = None
        self.savedResourceText = None
        self.generator = None
        self.previews = []

        self.loadText()
        self.inpText.setReadOnly(True)

        self.previewLabel.setText(f'Текстов показано: {len(self.previews)}\n'
                                  f'Лимит текстов: {self.previewsCount}')

        self.openAction.triggered.connect(self.loadText)
        self.previewsAction.triggered.connect(self.setPreviewsCount)
        self.resourceAction.triggered.connect(self.exportResource)
        self.exportAction.triggered.connect(self.export)
        self.blocksAction.triggered.connect(self.showBlocks)
        self.viewMenu.addAction(self.blocksAction)

    def loadText(self):
        if self.node is not None:
            self.exportResource(innerCall=True)
        path, group = QFileDialog.getOpenFileName(
            self, 'Выберите документ для загрузки', '',
            'Текстовые документы (*.txt);;Документы Microsoft Word (*.docx *.doc)')
        if not path:
            if self.savedText is None:
                exit()
            return
        if '*.txt' in group:
            with open(path, encoding='utf-8') as f:
                text = f.read()
        elif any(ext in group for ext in ('*docx', '*.doc')):
            print('word')
        if not text:
            return self.statusbar.showMessage(f'Файл {path} пуст!')
        if any(s in text for s in RESTRICTED_SYMBOLS):
            return self.statusbar.showMessage(
                f'Файл содержит запрещённые символы из набора: {RESTRICTED_SYMBOLS}')
        self.inpText.setPlainText(text)
        self.outpText.setPlainText(text)
        self.node = Node(text)
        if self.savedText is None:
            self.savedText = text

    def handleSelection(self):
        if self.txtAppear.is_active():
            self.txtAppear.stop()
        self.txtAppear.start()

    def highlight(self, *args):
        highlightResults = super(Window, self).highlight(self.inpText, self.node)
        if highlightResults is None:
            return
        block, idx = highlightResults
        self.repaint()
        self.showBlock(block)
        if idx is not None:
            self.blocksChronology.append(idx)

    def repaint(self):
        self.paintBlocks(self.inpText, self.node.getBlocks(), self.colors)
        self.outpText.setPlainText(str(self.node))

    def showBlocks(self):
        blocks_wnd = Blocks(self.node.getBlocks())
        blocks_wnd.exec()

    def cancelBlock(self):
        self.node.removeBlock(self.blocksChronology.pop())
        self.repaint()
        self.generator = expand(self.node)
        self.previews = []
        self.refreshPreviews()

    def exportResource(self, innerCall: bool = False):
        text = str(self.node)
        if not text:
            return self.statusbar.showMessage('Ресурсный текст пуст')
        if text == self.inpText.toPlainText():
            return (self.statusbar.showMessage('Ресурсный текст совпадает с исходным')
                    if not innerCall else None)
        if text == self.savedResourceText:
            return self.statusbar.showMessage('Данный ресурсный текст уже был сохранён')
        if not os.path.exists(EXPORT_RESOURCE_DIR):
            os.mkdir(EXPORT_RESOURCE_DIR)
        path, _ = QFileDialog.getSaveFileName(
            self, 'Сохраните ресурсный файл',
            os.path.join(EXPORT_RESOURCE_DIR, EXPORT_RESOURCE_DEFAULT_FILENAME),
            'Текстовые документы (*.txt)')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        except FileNotFoundError:
            return self.exportResource()
        self.savedResourceText = text
        self.statusbar.showMessage(f'Файл {path} был успешно сохранён!')

    def export(self):
        folder = 'texts'
        if os.path.exists(folder):
            dlg = QMessageBox(self)
            dlg.setWindowTitle('Confirm an action')
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            dlg.setWindowIcon(icon)
            dlg.setText('Вы уверены, что хотите провести экспорт текстов?\n'
                        f'Папка {folder} будет полностью перезаписана')
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if dlg.exec() != QMessageBox.StandardButton.Yes:
                return
            shutil.rmtree(folder)
        os.mkdir(folder)
        i = 0
        for i in range(len(self.previews)):
            with open(os.path.join(folder, f'{i + 1}.txt'), 'w', encoding='utf-8') as f:
                f.write(self.previews[i])
        self.statusbar.showMessage(f'Записано текстов: {i + 1}')

    def setPreviewsCount(self):
        previewsCount, ok = QInputDialog.getInt(
            self, 'Previews count', 'Введите количество текстов для предпросмотра:',
            min=1, value=self.previewList.count())
        if not ok or previewsCount == self.previewsCount:
            return
        self.previewsCount = previewsCount
        if self.previewsCount < (count := self.previewList.count()):
            offset = count - previewsCount
        else:
            offset = 0
            self.generator = expand(self.node)
            self.previews = []
        self.refreshPreviews(offset)

    def refreshPreviews(self, offset: int = 0):
        if offset > 0:
            for _ in range(abs(offset)):
                self.previewList.takeItem(self.previewList.count() - 1)
                self.previews.pop(-1)
            self.previewList.repaint()
        elif self.generator is None:
            return
        else:
            self.previewList.clear()
            for i in range(self.previewsCount):
                try:
                    text = next(self.generator)
                except StopIteration:
                    break
                self.previews.append(text)
                self.previewList.addItem(QListWidgetItem(f'Текст {i + 1}'))
        self.previewLabel.setText(f'Текстов показано: {self.previewList.count()}\n'
                                  f'Лимит текстов: {self.previewsCount}')

    def previewText(self):
        if len(selected := self.previewList.selectedItems()) > 1:
            return self.statusbar.showMessage(f'Выделите только один текст')
        if not selected:
            return
        idx = self.previewList.indexFromItem(selected[0]).row()
        dlg = QDialog(self)
        dlg.setWindowTitle(f'Текст {idx + 1}')
        size = self.inpText.size()
        dlg.resize(size)
        dlg.text = QPlainTextEdit(dlg)
        dlg.text.resize(size)
        dlg.text.setPlainText(self.previews[idx])
        dlg.text.setReadOnly(True)
        dlg.show()

    def _getNode(self, _):
        return self.node

    @staticmethod
    def _skipSpaces(doc, pos: int, step: int = 1):
        ch_count = doc.characterCount()
        while 0 < pos < ch_count and doc.characterAt(pos) == ' ':
            pos += step
        return pos


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
    myappid = u'elilcat.spintax.spintax.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    window = Window()
    # loadCfg(window)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
