"""TODO:
what if:
{abc|cde{fgh|hij}|cki}
"""

from exceptions import BlockException


class Block:
    _types = ['any', 'sentence', 'word']

    def __init__(self, elems: list, start_pos: int, end_pos: int,
                 _type: str = 'any'):
        self.elems = elems
        self.start_pos = start_pos
        self.end_pos = end_pos
        if _type not in self._types:
            raise BlockException('Invalid type passed')
        self._type = _type

    def set_elems(self, elems: list):
        if all(isinstance((str, Block), elem) for elem in elems):
            self.elems = elems

    def set_elem(self, idx: int, elem):
        if 0 <= idx < len(self.elems) and isinstance(elem, (str, Block)):
            self.elems[idx] = elem

    def set_start_pos(self, pos: int):
        self.start_pos = pos

    def set_end_pos(self, pos):
        self.end_pos = pos

    def get_chars_count(self):
        return len(self.__repr__())

    def get_type(self):
        return self._type

    # def __add__(self, elems):
    #     if all(isinstance(elem, (str, Block)) for elem in elems):
    #         self.elems.extend([elem for elem in elems if elem not in self.elems])

    def __len__(self):
        return len(self.elems)

    def __repr__(self):
        return ('{' + '|'.join([repr(elem) if isinstance(elem, Block)
                                else elem for elem in self.elems]) + '}')

    def __str__(self):
        return self.__repr__()


def main():
    b1 = Block(['abc', 'ijklmnop', 'efgh'], 0, 14)
    b2 = Block(['ijk', 'lmnop'], 5, 7)
    b1.set_elem(1, b2)
    print(b1, f'{len(b1)=}', f'{b1.get_chars_count()=}', sep='\n')
    print(f'{len("{abc|{ijk|lmnop}|efgh}")=}')


if __name__ == '__main__':
    main()
