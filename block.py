from exceptions import NodeException, BlockException


def assertNodeTypes(func):
    def wrapper(obj, var, *args):
        if not isinstance(var, (str, Block)):
            raise NodeException('Invalid type')
        return func(obj, var, *args)

    return wrapper


class Node:
    def __init__(self, *parts, delimiter: str = ''):
        if not all(isinstance(p, (str, Block)) for p in parts):
            raise NodeException('Invalid parts types')
        self.parts = list(parts)
        self.delimiter = delimiter if delimiter is not None else ''

    @assertNodeTypes
    def setPart(self, part, idx: int):
        print(part, idx)
        self.parts[idx] = part
        print(self.parts, end='\n\n')

    @assertNodeTypes
    def insertBlock(self, block):
        if not self.parts:
            return
        pos = block.getPos()
        idx = 0
        for i, part in enumerate(self.parts):
            if not isinstance(part, str):
                idx += len(part.getOriginal())
                continue
            if part == block.getOriginal():
                self.parts[i] = block
            elif idx <= pos <= idx + len(part):
                left, right = part[:pos - idx], part[block.getEnd() - idx:]
                self.parts[i] = block
                if left:
                    self.parts.insert(i, left)
                if right:
                    self.parts.insert(i + 1 + bool(left), right)
                break
            else:
                idx += len(part)
            idx += len(self.delimiter)

    # @assertNodeTypes
    def removeBlock(self, arg):
        if isinstance(arg, Block):
            idx = self.parts.index(arg)
            block = arg
        elif isinstance(arg, int):
            idx = arg
            block = self.parts[idx]
        else:
            raise BlockException('arg type should be either Block or int')
        start, end = idx, idx + 1
        left, right = '', ''
        if idx > 0 and isinstance(self.parts[idx - 1], str):
            left = self.parts[idx - 1]
            start -= 1
        if idx + 1 < len(self.parts) and isinstance(self.parts[idx + 1], str):
            right = self.parts[idx + 1]
            end += 1
        self.parts[start:end] = [left + block.getOriginal() + right]

    def removePart(self, idx: int):
        if not (0 <= idx < len(self.parts)):
            raise IndexError
        self.parts.pop(idx)

    @assertNodeTypes
    def addPart(self, part):
        self.parts.append(part)

    def getParts(self):
        return self.parts

    def getBlocks(self):
        return [p for p in self.getParts() if isinstance(p, Block)]

    def getOriginal(self):
        return self.delimiter.join([p.getOriginal() if isinstance(p, Block) else p
                                    for p in self.getParts()])

    @assertNodeTypes
    def __add__(self, part):
        return Node(*(self.parts + [part]))

    def __repr__(self):
        return self.delimiter.join([repr(p) if not isinstance(p, str) else p
                                    for p in self.parts])

    def __str__(self):
        return self.__repr__()


class Block:
    def __init__(self, original: str, pos: int, *nodes):
        self.original = original
        self.pos = pos
        self.nodes = [Node(self.original)] + [Node(n) for n in nodes if not isinstance(n, Node)]

    def getOriginal(self):
        return self.original

    def getPos(self):
        return self.pos

    def getEnd(self):
        return self.getPos() + len(self.getOriginal())

    def getNodes(self, skip_original: bool = False):
        return self.nodes[skip_original:]

    def setNodes(self, nodes: list):
        self.nodes[1:] = [Node(n) if not isinstance(n, Node) else n for n in nodes]

    def setNode(self, idx: int, node):
        if 0 <= idx < len(self.nodes) and isinstance(node, (str, Block)):
            self.nodes[idx] = node

    def removeNode(self, idx: int):
        self.nodes.pop(idx)

    def addNode(self, node):
        self.nodes.append(Node(node) if not isinstance(node, Node) else node)

    def addNodes(self, nodes):
        for node in nodes:
            self.addNode(node)

    def getCharsCount(self):
        return len(self.__repr__())

    def __len__(self):
        return len(self.nodes)

    def __repr__(self):
        return '{' + '|'.join([str(node) for node in self.nodes]) + '}'

    def __str__(self):
        return self.__repr__()


# noinspection PyArgumentList
def main():
    text = 'abc efg hij'
    node = Node(text)
    blockText = 'efg'
    block = Block(blockText, text.index(blockText), 'Efg', 'EFG')
    print(node)
    node.insertBlock(block)
    print(node)
    node.removeBlock(block)
    print(node)
    # blockPos = text.index('efg')
    # blockEnd = blockPos + len(blockText)

    # n = Node('abc', Block('efg', 2, 'EFG'), delimiter=' ')
    # print(n)


if __name__ == '__main__':
    main()
