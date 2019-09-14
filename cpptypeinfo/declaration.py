import re
import copy
from typing import List, NamedTuple, Dict


class Declaration:
    def __init__(self, is_const=False):
        self.is_const = is_const

    def __eq__(self, value):
        return isinstance(value,
                          self.__class__) and self.is_const == value.is_const

    def __str__(self):
        if self.is_const:
            return f'const {self.__class__.__name__}'
        else:
            return self.__class__.__name__

    def clone(self):
        return copy.copy(self)


class Void(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 1


class Int8(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 2


class Int16(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 3


class Int32(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 4


class Int64(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 5


class UInt8(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 6


class UInt16(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 7


class UInt32(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 8


class UInt64(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 9


class Float(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 10


class Double(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 11


class Bool(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 12


class VaList(Declaration):
    def __init__(self, is_const=False):
        super().__init__(is_const)

    def __hash__(self):
        return 13


class Pointer(Declaration):
    def __init__(self, target: Declaration, is_const=False):
        super().__init__(is_const)
        self.target = target
        self._hash = target.__hash__() * 13 + 1

    def __hash__(self):
        return self._hash

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if self.target != value.target:
            return False
        return True

    def __str__(self):
        return f'Ptr({self.target})'


class Array(Declaration):
    def __init__(self, target: Declaration, length=None, is_const=False):
        super().__init__(is_const)
        self.target = target
        self.length = length
        self._hash = target.__hash__() * 12 + 1

    def __hash__(self):
        return self._hash

    def __eq__(self, value):
        return super().__eq__(value) and self.target == value.target


class Field(NamedTuple):
    type: Declaration
    name: str
    value: str = ''


class Struct(Declaration):
    def __init__(self, type_name, is_const=False, fields: List[Field] = None):
        super().__init__(is_const)
        self.type_name = type_name
        self.fields: List[Field] = []
        if fields:
            for f in fields:
                self.add_field(f)
        STACK[-1].user_type_map[self.type_name] = self

    def add_field(self, f: Field) -> None:
        self.fields.append(f)

    def __hash__(self):
        return hash(self.type_name)

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if self.type_name != value.type_name:
            return False
        for l, r in zip(self.fields, value.fields):
            if l != r:
                return False
        return True

    def __str__(self) -> str:
        return f'struct {self.type_name}'


class Param(NamedTuple):
    type: Declaration
    name: str = ''
    value: str = ''


class Function(Declaration):
    def __init__(self,
                 result: Declaration,
                 params: List[Param],
                 is_const=False):
        super().__init__(is_const=is_const)
        self.result = result
        self.params = params
        self._hash = hash(result)
        for p in self.params:
            self._hash += hash(p)

    def __hash__(self):
        return self._hash

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if not self.result == value.result:
            return False
        if (len(self.params) != len(value.params)):
            return False
        for l, r in zip(self.params, value.params):
            if (l != r):
                return False
        return True

    def __str__(self) -> str:
        params = ', '.join(str(p.type) for p in self.params)
        return f'{self.result}({params})'


class Typedef(Declaration):
    def __init__(self, type_name: str, src: Declaration):
        super().__init__(is_const=False)
        self.type_name = type_name
        self.src = src
        STACK[-1].user_type_map[self.type_name] = self

    def __hash__(self):
        return hash(self.src)

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        # if self.type_name!=value.type_name:
        #     return False
        if self.src != value.src:
            return False
        return True


class EnumValue(NamedTuple):
    name: str
    value: int


class Enum(Declaration):
    def __init__(self, type_name: str, values: List[EnumValue],
                 is_const=False):
        super().__init__(is_const=is_const)
        self.type_name = type_name
        self.values = values
        STACK[-1].user_type_map[self.type_name] = self


type_map = {
    'void': Void,
    'char': Int8,
    'signed char': Int8,
    'int': Int32,
    'short': Int16,
    'long long': Int64,
    'unsigned char': UInt8,
    'unsigned int': UInt32,
    'unsigned short': UInt16,
    'unsigned long long': UInt64,
    'size_t': UInt64,
    'float': Float,
    'double': Double,
    'bool': Bool,
    'va_list': VaList,
}


class Namespace:
    def __init__(self, name: str = ''):
        self.name = name
        self.user_type_map: Dict[str, Declaration] = {}

    def get(self, src: str, is_const: bool):
        user_type = self.user_type_map.get(src)
        if not user_type:
            return None
        if user_type.is_const != is_const:
            user_type = user_type.clone()
            user_type.is_const = is_const
        return user_type


STACK = [Namespace()]  # root namespace


def push_namespace(name: str):
    namespace = Namespace(name)
    STACK.append(namespace)
    return namespace


def pop_namespace():
    STACK.pop()


SPLIT_PATTERN = re.compile(r'[*&]')
FUNC_PATTERN = re.compile(r'^(.*)\(.*\)\((.*)\)$')


def parse(src: str, is_const=False) -> Declaration:
    src = src.strip()

    m = FUNC_PATTERN.match(src)
    if m:
        result = m.group(1)
        params = m.group(2).split(',')
        return Function(parse(result), [Param(type=parse(x)) for x in params])

    if src[-1] == ']':
        # array
        pos = src.rfind('[')
        if pos == -1:
            raise Exception('"[" not found')
        length_str = src[pos + 1:-2].strip()
        length = None
        if length_str:
            length = int(length_str)
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
        elif splitted[0] == 'struct':
            if len(splitted) != 2:
                raise Exception()
            return Struct(splitted[1])
        else:
            t = type_map.get(src)
            if t:
                return t(is_const)

            for namespace in reversed(STACK):
                decl = namespace.get(src, is_const)
                if decl:
                    return decl

            raise Exception(f'not found: {src}')


if __name__ == '__main__':
    assert (parse('int') == Int32())
    assert (parse('int') != UInt32())
    assert (parse('const int') == Int32(True))
    assert (parse('int') != Int32(True))
    assert (parse('char') == Int8())
    assert (parse('short') == Int16())
    assert (parse('long long') == Int64())
    assert (parse('unsigned int') == UInt32())
    assert (parse('const unsigned int') == UInt32(True))
    assert (parse('unsigned int') != UInt32(True))
    assert (parse('unsigned char') == UInt8())
    assert (parse('unsigned short') == UInt16())
    assert (parse('unsigned long long') == UInt64())

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

    assert (parse('struct ImGuiInputTextCallbackData') == Struct(
        'ImGuiInputTextCallbackData'))
    assert (parse('int (*)(ImGuiInputTextCallbackData *)') == Function(
        Int32(), [Param(Pointer(Struct('ImGuiInputTextCallbackData')))]))

    vec2 = parse('struct ImVec2')
    vec2.add_field(Field(Float(), 'x'))
    vec2.add_field(Field(Float(), 'y'))
    assert (vec2 == Struct(
        'ImVec2', False,
        [Field(Float(), 'x'), Field(Float(), 'y')]))

    parsed = parse('const ImVec2 &')
    assert (parsed == Pointer(Struct('ImVec2', True)))
