from PyQt6.QtWidgets import QMainWindow, QPlainTextEdit

from constants import PUNCTUATION, TEXT_FIELD_STYLE


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


def getExtension(filename: str):
    return filename.split('.')[-1]


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


def changeStyleProperty(style: str, prop: str, val: str):
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
