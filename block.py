from exceptions import NodeException


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
        if not isinstance(part, (str, Block)):
            raise NodeException(f'Invalid part type: {type(part)}')
        if not (0 <= idx < len(self.parts)):
            raise IndexError
        self.parts[idx] = part

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


def main():
    n = Node('abc', Block('efg', 2, 'EFG'), delimiter=' ')
    print(n)


if __name__ == '__main__':
    main()
