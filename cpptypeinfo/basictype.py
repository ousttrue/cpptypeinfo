import pathlib
from typing import Optional, NamedTuple, Dict


class Type:
    def __init__(self) -> None:
        self.file: Optional[pathlib.Path] = None
        self.line = -1

    def __repr__(self) -> str:
        return str(self)

    def to_ref(self) -> 'TypeRef':
        return TypeRef(self)

    def to_const(self) -> 'TypeRef':
        return TypeRef(self, True)


class PrimitiveType(Type):
    '''
    Type that has not TypeRef
    '''
    def __str__(self) -> str:
        return self.__class__.__name__

    def __eq__(self, value) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return True


class Int8(PrimitiveType):
    def __hash__(self) -> int:
        return 2


class Int16(PrimitiveType):
    def __hash__(self) -> int:
        return 3


class Int32(PrimitiveType):
    def __hash__(self) -> int:
        return 4


class Int64(PrimitiveType):
    def __hash__(self) -> int:
        return 5


class UInt8(PrimitiveType):
    def __hash__(self) -> int:
        return 6


class UInt16(PrimitiveType):
    def __hash__(self) -> int:
        return 7


class UInt32(PrimitiveType):
    def __hash__(self) -> int:
        return 8


class UInt64(PrimitiveType):
    def __hash__(self) -> int:
        return 9


class Float(PrimitiveType):
    def __hash__(self):
        return 10


class Double(PrimitiveType):
    def __hash__(self) -> int:
        return 11


class Bool(PrimitiveType):
    '''
    may Int8
    '''
    def __hash__(self) -> int:
        return 12


class Void(PrimitiveType):
    def __hash__(self) -> int:
        return 1


class VaList(PrimitiveType):
    def __hash__(self) -> int:
        return 13


class TypeRef(NamedTuple):
    ref: Type
    is_const: bool = False

    def __eq__(self, value) -> bool:
        if isinstance(value, Type):
            return self.ref == value
        elif isinstance(value, TypeRef):
            if self.is_const != value.is_const:
                return False
            return self.ref == value.ref
        return False

    def __str__(self) -> str:
        if self.is_const:
            return f'const {self.ref}'
        else:
            return str(self.ref)


primitive_type_map: Dict[str, PrimitiveType] = {
    'void': Void(),
    #
    'int64_t': Int64(),
    'uint64_t': UInt64(),
    #
    'char': Int8(),
    'int': Int32(),
    'short': Int16(),
    'long long': Int64(),
    #
    'signed char': Int8(),
    'signed short': Int16(),
    'signed int': Int32(),
    'signed long long': Int64(),
    #
    'unsigned char': UInt8(),
    'unsigned int': UInt32(),
    'unsigned short': UInt16(),
    'unsigned long long': UInt64(),
    #
    'size_t': UInt64(),
    'float': Float(),
    'double': Double(),
    'bool': Bool(),
    'va_list': VaList(),
}
