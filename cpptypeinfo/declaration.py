import re


class Declaration:
    def __init__(self, is_const=False):
        self.is_const = is_const

    def __eq__(self, value):
        return isinstance(value,
                          self.__class__) and self.is_const == value.is_const


class Void(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 1


class Int8(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 2


class Int16(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 3


class Int32(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 4


class Int64(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 5


class UInt8(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 6


class UInt16(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 7


class UInt32(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 8


class UInt64(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 9


class Float(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 10


class Double(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 11


class Bool(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const=is_const)

    def __hash__(self):
        return 12


class Pointer(Declaration):
    def __init__(self, target: Declaration, is_const=False):
        super().__init__(is_const=is_const)
        self.target = target
        self._hash = target.__hash__() * 12 + 1

    def __hash__(self):
        return self._hash

    def __eq__(self, value):
        return super().__eq__(value) and self.target == value.target


class Array(Declaration):
    def __init__(self, target: Declaration, length=None, is_const=False):
        super().__init__(is_const=is_const)
        self.target = target
        self.length = length
        self._hash = target.__hash__() * 12 + 1

    def __hash__(self):
        return self._hash

    def __eq__(self, value):
        return super().__eq__(value) and self.target == value.target


type_map = {
    'void': Void,
    'char': Int8,
    'int': Int32,
    'short': Int16,
    'long': Int64,
    'unsigned char': UInt8,
    'unsigned int': UInt32,
    'unsigned short': UInt16,
    'unsigned long': UInt64,
}

SPLIT_PATTERN = re.compile(r'[*&]')


def parse(src: str, is_const=False) -> Declaration:
    src = src.strip()

    if src[-1] == ']':
        # array
        pos = src.rfind('[')
        if pos == -1:
            raise Exception('"[" not found')
        length_str = src[pos + 1:-2].strip()
        if length_str:
            length = int(length_str)
        else:
            length = None
        return Array(parse(src[0:pos]), length, is_const)

    found = [x for x in SPLIT_PATTERN.finditer(src)]
    if found:
        # pointer or reference
        last = found[-1].start()
        head, tail = src[0:last].strip(), src[last + 1:].strip()
        return Pointer(parse(head), tail == 'const')

    else:
        splitted = src.split()
        if splitted[0] == 'const':
            return parse(' '.join(splitted[1:]), True)
        elif splitted[-1] == 'const':
            return parse(' '.join(splitted[:-1]), True)
        else:
            return type_map[src](is_const)


if __name__ == '__main__':
    assert (parse('int') == Int32())
    assert (parse('int') != UInt32())
    assert (parse('const int') == Int32(True))
    assert (parse('int') != Int32(True))
    assert (parse('char') == Int8())
    assert (parse('short') == Int16())
    assert (parse('long') == Int64())
    assert (parse('unsigned int') == UInt32())
    assert (parse('const unsigned int') == UInt32(True))
    assert (parse('unsigned int') != UInt32(True))
    assert (parse('unsigned char') == UInt8())
    assert (parse('unsigned short') == UInt16())
    assert (parse('unsigned long') == UInt64())

    assert (parse('void*') == Pointer(Void()))
    assert (parse('const int*') == Pointer(Int32(True)))
    assert (parse('int const*') == Pointer(Int32(True)))
    assert (parse('int * const') == Pointer(Int32(), True))
    assert (parse('const int * const') == Pointer(Int32(True), True))

    assert (parse('void**') == Pointer(Pointer(Void())))
    assert (parse('const void**') == Pointer(Pointer(Void(True))))
    assert (parse('const int&') == Pointer(Int32(True)))

    assert (parse('int[ ]') == Array(Int32()))
    assert (parse('int[5]') == Array(Int32(), 5))
    assert (parse('const int[5]') == Array(Int32(True), 5))
    assert (parse('const int*[5]') == Array(Pointer(Int32(True)), 5))
