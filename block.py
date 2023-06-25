from exceptions import NodeException


def assert_node_types(func):
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

    @assert_node_types
    def set_part(self, part, idx: int):
        if not isinstance(part, (str, Block)):
            raise NodeException(f'Invalid part type: {type(part)}')
        if not (0 <= idx < len(self.parts)):
            raise IndexError
        self.parts[idx] = part

    def remove_part(self, idx: int):
        if not (0 <= idx < len(self.parts)):
            raise IndexError
        self.parts.pop(idx)

    @assert_node_types
    def add_part(self, part):
        self.parts.append(part)

    def get_parts(self):
        return self.parts

    def get_blocks(self):
        return [p for p in self.get_parts() if isinstance(p, Block)]

    def get_original(self):
        return self.delimiter.join([p.get_original() if isinstance(p, Block) else p
                                    for p in self.get_parts()])

    @assert_node_types
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

    def get_original(self):
        return self.original

    def get_pos(self):
        return self.pos

    def get_end(self):
        return self.get_pos() + len(self.get_original())

    def get_nodes(self, skip_original: bool = False):
        return self.nodes[skip_original:]

    def set_nodes(self, nodes: list):
        self.nodes[1:] = [Node(n) if not isinstance(n, Node) else n for n in nodes]

    def set_node(self, idx: int, node):
        if 0 <= idx < len(self.nodes) and isinstance(node, (str, Block)):
            self.nodes[idx] = node

    def add_node(self, node):
        self.nodes.append(Node(node) if not isinstance(node, Node) else node)

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    # def set_start_pos(self, pos: int):
    #     self.start_pos = pos
    #
    # def set_end_pos(self, pos):
    #     self.end_pos = pos

    def get_chars_count(self):
        return len(self.__repr__())

    # def __add__(self, nodes):
    #     if all(isinstance(node, (str, Block)) for node in nodes):
    #         self.nodes.extend([node for node in nodes if node not in self.nodes])

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
