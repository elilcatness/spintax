from random import randint, choice

from PyQt6.QtWidgets import QMainWindow, QPlainTextEdit

from src.block import Node, Block
from src.constants import PUNCTUATION


def loadCfg(window: QMainWindow, filename: str = 'cfg.txt'):
    with open(filename, encoding='utf-8') as f:
        for line in f:
            try:
                attr, value = line.strip().split('=')
            except ValueError:
                continue
            if not hasattr(window, attr):
                print(f'Invalid attr: {attr}')
                continue
            if ',' in value:
                value = [val.strip() for val in value.split(',')]
            setattr(window, attr, value)


def safeGet(lst: list, idx, default=None):
    try:
        return lst[idx]
    except IndexError:
        return default


def highlight(textField: QPlainTextEdit):
    cursor = textField.textCursor()
    if not cursor.hasSelection():
        return
    doc = textField.document()
    charsCount = doc.characterCount()
    edges = [cursor.selectionStart(), cursor.selectionEnd()]
    prevEdges = edges[:]
    for i, step in enumerate(range(-1, 2, 2)):
        while doc.characterAt(edges[i]) not in PUNCTUATION and 0 < edges[i] < charsCount:
            edges[i] += step
    edges[0] = edges[0] + 1 if edges[0] > 0 else 0
    edges[1] = edges[1] - 1 if edges[1] == charsCount else edges[1]
    for pos in range(min(min(prevEdges), min(edges)), max(max(prevEdges), max(edges))):
        cursor.setPosition(pos)
        if cursor.charFormat().background().color().getRgb() != (0, 0, 0, 255):
            cursor.clearSelection()
            textField.setTextCursor(cursor)
            return
    start, end = edges
    cursor.setPosition(start)
    cursor.setPosition(end, cursor.MoveMode.KeepAnchor)
    text = cursor.selectedText()
    cursor.clearSelection()
    textField.setTextCursor(cursor)
    return text, start


def moveBlocks(blocks, fromPos: int, offset: int) -> bool:
    if fromPos < 0 or not blocks:
        return False
    for block in blocks:
        blockPos = block.getPos()
        if blockPos >= fromPos:
            block.setPos(blockPos + offset)
    return True


def expand(ancestor):
    q = [ancestor]
    texts = set()
    while q:
        node = q.pop(0)
        for block in node.getBlocks():
            for blockNode in block.getNodes(skipOriginal=False):
                parts = node.getParts()
                for i in range(len(parts)):
                    if parts[i] == block:
                        subParts = blockNode.getParts()
                        parts[i:] = subParts + parts[i + 1:]
                        break
                subNode = Node(*parts)
                q.append(subNode)
                if (text := subNode.getOriginal()) not in texts:
                    q.append(subNode)
                    texts.add(text)
                    yield text
    # return texts


def changeStyleProperty(style: str, prop: str, val: str) -> str:
    styleBlocks = style.split(';')
    for i in range(len(styleBlocks)):
        styleBlocks[i] = styleBlocks[i].strip()
        if styleBlocks[i].split(':')[0] == prop:
            styleBlocks[i] = f'{prop}: {val}'
            break
    else:
        styleBlocks.append(f'{prop}: {val}')
    return '; '.join(styleBlocks) + (';' if not styleBlocks[-1].endswith(';') else '')


def getStyleProperty(style: str, prop: str, default: str = None):
    styleBlocks = style.split(';')
    for i in range(len(styleBlocks)):
        if styleBlocks[i].strip() == prop:
            return styleBlocks[-1].split(':')[-1].strip()
    return default
