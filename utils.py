from PyQt6.QtWidgets import QMainWindow


def load_cfg(window: QMainWindow, filename: str = 'cfg.txt'):
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