"""TODO:
what if:
{abc|cde{fgh|hij}|cki}
"""

from exceptions import NodeException


def assert_node_types(func):
    def wrapper(obj, var, *args):
        if not isinstance(var, (str, Block)):
            raise NodeException('Invalid type')
        return func(obj, var, *args)
    return wrapper


class Node:
    def __init__(self, *parts):
        if not all(isinstance(p, (str, Block)) for p in parts):
            raise NodeException('Invalid parts types')
        self.parts = list(parts)

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

    @assert_node_types
    def __add__(self, part):
        return Node(*(self.parts + [part]))

    def __repr__(self):
        return ''.join([repr(p) if not isinstance(p, str) else p for p in self.parts])

    def __str__(self):
        return self.__repr__()


class Block:
    def __init__(self, *nodes):
        self.nodes = [Node(n) for n in nodes if not isinstance(n, Node)]
        # self.start_pos = start_pos
        # self.end_pos = end_pos

    def set_nodes(self, nodes: list):
        if all(isinstance((str, Block), node) for node in nodes):
            self.nodes = nodes

    def set_node(self, idx: int, node):
        if 0 <= idx < len(self.nodes) and isinstance(node, (str, Block)):
            self.nodes[idx] = node

    def add_node(self, node):
        self.nodes.append(Node(node) if not isinstance(node, Node) else node)

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
        return '{' + '|'.join([repr(node) for node in self.nodes]) + '}'

    def __str__(self):
        return self.__repr__()


def main():
    n = Node('abc')
    b = Block('efg')
    b.add_node('eFg')
    n += b
    print(n)
    n.get_parts()[1].set_node(1, Block('EFG', 'EEFFGG'))
    print(n)


if __name__ == '__main__':
    main()