'''
Type
    + PrimitiveType
        + Int8
        + Int16
        + Int32
        + Int64
        + UInt8
        + UInt16
        + UInt32
        + UInt64
        + Float
        + Double
        + Bool(Int8)
        + Void
        + VaList
    + UserType
        + Pointer
            + Array
        + Function(extern "C", __declspec(dllexport))
        + NamedType(export)
            + Enum(Int32)
            + Typedef
            + Struct

TypeRef
    + is_const
    + type: Type

Field: for Struct
    + ref: TypeRef
    + name

Param: for Function
    + ref: TypeRef
    + name
'''

import re
import copy
from typing import List, NamedTuple, Dict, Optional, Union


class Type:
    def __init__(self):
        self.file = ''
        self.line = -1

    def to_ref(self) -> 'TypeRef':
        return TypeRef(self)

    def to_const(self) -> 'TypeRef':
        return TypeRef(self, True)


class PrimitiveType(Type):
    '''
    Type that has not TypeRef
    '''
    def __str__(self):
        return self.__class__.__name__

    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return False
        return True


class Int8(PrimitiveType):
    def __hash__(self):
        return 2


class Int16(PrimitiveType):
    def __hash__(self):
        return 3


class Int32(PrimitiveType):
    def __hash__(self):
        return 4


class Int64(PrimitiveType):
    def __hash__(self):
        return 5


class UInt8(PrimitiveType):
    def __hash__(self):
        return 6


class UInt16(PrimitiveType):
    def __hash__(self):
        return 7


class UInt32(PrimitiveType):
    def __hash__(self):
        return 8


class UInt64(PrimitiveType):
    def __hash__(self):
        return 9


class Float(PrimitiveType):
    def __hash__(self):
        return 10


class Double(PrimitiveType):
    def __hash__(self):
        return 11


class Bool(PrimitiveType):
    '''
    may Int8
    '''
    def __hash__(self):
        return 12


class Void(PrimitiveType):
    def __hash__(self):
        return 1


class VaList(PrimitiveType):
    def __hash__(self):
        return 13


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


# class TypeRef:
#     def __init__(self, ref: Type, is_const=False):
#         self.ref = ref
#         self.is_const = is_const
class TypeRef(NamedTuple):
    ref: Type
    is_const: bool = False

    def __eq__(self, value):
        if isinstance(value, Type):
            return self.ref == value
        elif isinstance(value, TypeRef):
            if self.is_const != value.is_const:
                return False
            return self.ref == value.ref

    def __str__(self) -> str:
        if self.is_const:
            return f'const {self.ref}'
        else:
            return str(self.ref)

    def is_based(self, based: Type) -> bool:
        if self.ref == based:
            return True
        if isinstance(self.ref, UserType):
            return self.ref.is_based(based)
        else:
            return False

    def replace_based(self, based: Type, replace: Type) -> Optional['TypeRef']:
        if self.ref != based:
            return None
        return TypeRef(replace, self.is_const)

    def resolve(self, typedef: 'Typedef') -> 'TypeRef':
        if self.ref != typedef:
            return self
        return TypeRef(typedef.typeref.ref, self.is_const)

    def get_concrete_type(self) -> Type:
        current = self.ref
        while isinstance(current, Typedef):
            current = current.typeref.ref
        return current


class UserType(Type):
    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return False
        return True

    def __str__(self):
        return self.type_name

    def clone(self):
        return copy.copy(self)

    def is_based(self, based: Type) -> bool:
        raise NotImplementedError()

    def replace_based(self, based: Type, replace: Type) -> 'UserType':
        raise Exception()

    def resolve(self, target: 'Typedef'):
        pass


class NamedType(UserType):
    def __init__(self, type_name: str):
        if not type_name:
            raise Exception('no name')
        self.type_name = type_name
        self.file = ''
        self.line = -1
        # 型をNameSpaceに登録する
        if self.type_name and self.type_name not in STACK[-1].user_type_map:
            STACK[-1].user_type_map[self.type_name] = self

    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return False
        if self.type_name != value.type_name:
            return False
        return True


class Namespace:
    '''
    ユーザー定義型を管理する
    '''
    def __init__(self, name: str):
        self.name = name
        self.user_type_map: Dict[str, UserType] = {}
        self.children: List[Namespace] = []
        self.parent: Optional[Namespace] = None
        self.functions: List[Function] = []

    def __str__(self) -> str:
        return '::'.join([ns.name for ns in self.ancestors()])

    def get(self, src: str) -> Optional[Type]:
        user_type = self.user_type_map.get(src)
        if not user_type:
            return None
        return user_type

    def ancestors(self):
        yield self
        if self.parent:
            for x in self.parent.ancestors():
                yield x

    def traverse(self, level=0):
        yield self
        for child in self.children:
            for x in child.traverse(level + 1):
                if not isinstance(x, Struct):
                    yield x

    def resolve_typedef(self, name: str):
        '''
        typedefを削除する。
        型を破壊的に変更する
        '''
        while True:
            found = None
            for ns in self.traverse():
                decl = ns.user_type_map.get(name)
                if decl:
                    if isinstance(decl, Typedef):
                        found = decl
                        break
            if not found:
                break

            # remove
            for ns in self.traverse():
                for k, v in ns.user_type_map.items():
                    v.resolve(found)
                for v in ns.functions:
                    v.resolve(found)

            for ns in self.traverse():
                if found.type_name in ns.user_type_map:
                    print(f'remove {found}')
                    ns.user_type_map.pop(found.type_name)


STACK: List[Namespace] = []


def push_namespace(name='') -> Namespace:
    namespace = name if isinstance(name, Namespace) else Namespace(name)
    if STACK:
        STACK[-1].children.append(namespace)
        namespace.parent = STACK[-1]
    STACK.append(namespace)
    return namespace


def pop_namespace():
    STACK.pop()


NS_PATTERN = re.compile(r'(\w+)::(\w+)$')


def get_from_ns(src: str) -> Optional[Type]:
    primitive = primitive_type_map.get(src)
    if primitive:
        return primitive

    for namespace in reversed(STACK):
        decl = namespace.get(src)
        if decl:
            return decl

    return None


class Typedef(NamedType):
    def __init__(self, type_name: str, ref: Union[TypeRef, Type]):
        super().__init__(type_name)
        if isinstance(ref, Type):
            ref = ref.to_ref()
        self.typeref = ref

    def __str__(self) -> str:
        return f'typedef {self.type_name} = {self.typeref}'

    def __hash__(self):
        return hash(self.typeref)

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if self.type_name == value.type_name:
            if self.typeref != value.typeref:
                raise Exception()
        if self.typeref != value.typeref:
            return False
        return True

    def is_based(self, based: Type) -> bool:
        return self.typeref.is_based(based)

    def resolve(self, target: 'Typedef'):
        self.typeref = self.typeref.resolve(target)

    def get_concrete_type(self) -> Type:
        return self.typeref.get_concrete_type()


class Pointer(UserType):
    def __init__(self, ref: Union[TypeRef, Type]):
        if isinstance(ref, Type):
            ref = TypeRef(ref)
        self.typeref = ref
        self._hash = ref.__hash__() * 13 + 1

    def __hash__(self):
        return self._hash

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if self.typeref != value.typeref:
            return False
        return True

    def __str__(self):
        return f'Ptr({self.typeref})'

    def is_based(self, based: Type) -> bool:
        return self.typeref.is_based(based)

    def replace_based(self, based: Type, replace: Type):
        self.typeref.replace_based(based, replace)

    def resolve(self, target: Typedef):
        self.typeref = self.typeref.resolve(target)


class Array(Pointer):
    def __init__(self, ref: Union[Type, TypeRef],
                 length: Optional[int] = None):
        super().__init__(ref)
        self.length = length
        self._hash = ref.__hash__() * 13 + 2

    def __hash__(self):
        return self._hash

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if self.length != value.length:
            return False
        return True


class Field(NamedTuple):
    typeref: TypeRef
    name: str
    value: str = ''

    def resolve(self, typedef: Typedef) -> 'Field':
        if self.typeref == typedef:
            return Field(typedef.typeref, self.name, self.value)
        else:
            return self


class Struct(NamedType, Namespace):
    def __init__(self, type_name, fields: List[Field] = None):
        super().__init__(type_name)
        Namespace.__init__(self, type_name)
        global STACK

        self.fields: List[Field] = []
        if fields:
            for f in fields:
                if isinstance(f.typeref, Type):
                    f = Field(f.typeref.to_ref(), f.name, f.value)
                self.add_field(f)
        self.template_parameters: List[str] = []

    def is_forward_decl(self) -> bool:
        return len(self.fields) == 0

    def add_field(self, f: Field) -> None:
        if isinstance(f.typeref, Type):
            f = Field(f.typeref.to_ref(), f.name, f.value)
        self.fields.append(f)

    def add_template_parameter(self, t: str) -> None:
        self.template_parameters.append(t)
        self.user_type_map[t] = parse(f'struct {t}').ref

    def instantiate(self, template_params: List[Type]) -> 'Struct':
        decl = self.clone()

        based_params = [self.get(t) for t in self.template_parameters]

        for based, replace in zip(based_params, template_params):
            for i in range(len(self.fields)):
                f = self.fields[i]
                # if f.typeref.is_based(based):
                #     if f.type == based:
                #         self.fields[i] = Field(replace, f.name, f.value)
                #     else:
                #         clone = copy.copy(f.type)
                #         f.type.replace_based(clone, based, replace)
                #         self.fields[i] = Field(clone, f.name, f.value)

        decl.template_parameters.clear()

        return decl

    def is_based(self, based: Type) -> bool:
        for f in self.fields:
            if f.typeref.is_based(based):
                return True
        return False

    def resolve(self, target: Typedef):
        for i in range(len(self.fields)):
            self.fields[i] = self.fields[i].resolve(target)

    def __hash__(self):
        return hash(self.type_name)

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if self.type_name != value.type_name:
            return False
        if not self.is_forward_decl() and not value.is_forward_decl():
            if len(self.fields) != len(value.fields):
                return False
            for l, r in zip(self.fields, value.fields):
                if l != r:
                    return False
        if len(self.template_parameters) != len(value.template_parameters):
            return False
        for l, r in zip(self.template_parameters, value.template_parameters):
            if l != r:
                return False
        return True

    def __str__(self) -> str:
        return f'{self.type_name}'


class Param(NamedTuple):
    typeref: TypeRef
    name: str = ''
    value: str = ''

    def resolve(self, typedef: Typedef) -> 'Param':
        if self.typeref == typedef:
            return Param(typedef.typeref, self.name, self.value)
        else:
            return self


class Function(UserType):
    def __init__(self, result: Union[TypeRef, Type], params: List[Param]):
        super().__init__()
        self.name = ''
        if isinstance(result, Type):
            result = result.to_ref()
        self.result = result
        self.params: List[Param] = []
        for p in params:
            if isinstance(p.typeref, Type):
                p = Param(p.typeref.to_ref(), p.name, p.value)
            self.params.append(p)

        self._hash = hash(result)
        for p in self.params:
            self._hash += hash(p)

        STACK[-1].functions.append(self)

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
        params = ', '.join(str(p.typeref) for p in self.params)
        if self.name:
            return f'{self.name} = {self.result}({params})'
        else:
            return f'{self.result}({params})'

    def is_based(self, based: Type) -> bool:
        for p in self.params:
            if p.typeref.is_based(based):
                return True
        return False

    def resolve(self, typedef: Typedef):
        self.result = self.result.resolve(typedef)
        for i in range(len(self.params)):
            self.params[i] = self.params[i].resolve(typedef)


class EnumValue(NamedTuple):
    name: str
    value: int


class Enum(NamedType):
    def __init__(self, type_name: str, values: List[EnumValue]):
        super().__init__(type_name)
        self.values = values

    def __str__(self) -> str:
        return f'enum {self.type_name}'


SPLIT_PATTERN = re.compile(r'[*&]')
FUNC_PATTERN = re.compile(r'^(.*)\(.*\)\((.*)\)$')


def parse(src: str, is_const=False) -> TypeRef:
    src = src.strip()

    m = FUNC_PATTERN.match(src)
    if m:
        result = m.group(1)
        params = m.group(2).split(',')
        return TypeRef(
            Function(parse(result), [Param(typeref=parse(x)) for x in params]))

    if src[-1] == '>':
        # template
        pos = src.rfind('<')
        if pos == -1:
            raise Exception('< not found')
        template = get_from_ns(src[:pos].strip())
        if not template:
            raise Exception()
        template_params = [
            parse(t) for t in src[pos + 1:-1].strip().split(',')
        ]
        decl = template.instantiate(template_params)
        return TypeRef(decl, is_const)

    if src[-1] == ']':
        # array
        pos = src.rfind('[')
        if pos == -1:
            raise Exception('"[" not found')
        length_str = src[pos + 1:-1].strip()
        length = None
        if length_str:
            length = int(length_str)
        return TypeRef(Array(parse(src[0:pos]), length), is_const)

    found = [x for x in SPLIT_PATTERN.finditer(src)]
    if found:
        # pointer or reference
        last = found[-1].start()
        head, tail = src[0:last].strip(), src[last + 1:].strip()
        return TypeRef(Pointer(parse(head)), tail == 'const')

    else:
        splitted = src.split()
        if splitted[0] == 'const':
            return parse(' '.join(splitted[1:]), True)
        elif splitted[-1] == 'const':
            return parse(' '.join(splitted[:-1]), True)
        elif splitted[0] == 'struct' or splitted[0] == 'union':
            if len(splitted) != 2:
                raise Exception()

            decl = get_from_ns(splitted[1])
            if decl:
                return TypeRef(decl, is_const)

            return TypeRef(Struct(splitted[1]), is_const)
        else:
            # get struct local type
            ns_list = src.split('::')
            if len(ns_list) > 1:
                if len(ns_list) != 2:
                    raise NotImplementedError()
                current = STACK[-1]
                if isinstance(current, Struct):
                    if current.type_name != ns_list[0]:
                        raise Exception(f'is not {ns_list[0]}')
                    return parse(ns_list[1], is_const)
                else:
                    ns = get_from_ns(ns_list[0])
                    if not ns:
                        raise Exception(f'not found {ns_list[0]}')
                    if not isinstance(ns, Struct):
                        raise Exception(f'{ns} is not Struct')
                    decl = ns.get(ns_list[1])
                    if not decl:
                        raise Exception(f'{ns_list[1]} is not found in {ns}')
                    return TypeRef(decl, is_const)

            decl = get_from_ns(src)
            if decl:
                return TypeRef(decl, is_const)

            raise Exception(f'not found: {src}')


if __name__ == '__main__':
    push_namespace('')  # root
    assert (parse('int') == Int32())
    assert (parse('int') != UInt32())
    assert (parse('const int') == Int32().to_const())
    assert (parse('int') != Int32().to_const())
    assert (parse('char') == Int8())
    assert (parse('short') == Int16())
    assert (parse('long long') == Int64())
    assert (parse('unsigned int') == UInt32())
    assert (parse('const unsigned int') == UInt32().to_const())
    assert (parse('unsigned int') != TypeRef(UInt32(), True))
    assert (parse('unsigned char') == UInt8())
    assert (parse('unsigned short') == UInt16())
    assert (parse('unsigned long long') == UInt64())

    assert (parse('void*') == Pointer(Void()))
    assert (parse('const int*') == Pointer(Int32().to_const()))
    assert (parse('int const*') == Pointer(Int32().to_const()))
    assert (parse('int * const') == Pointer(Int32()).to_const())
    assert (parse('const int * const') == Pointer(
        Int32().to_const()).to_const())

    assert (parse('void**') == Pointer(Pointer(Void())))
    assert (parse('const void**') == Pointer(Pointer(Void().to_const())))
    assert (parse('const int&') == Pointer(Int32().to_const()))

    assert (parse('int[ ]') == Array(Int32()))
    assert (parse('int[5]') == Array(Int32(), 5))
    assert (parse('const int[5]') == Array(Int32().to_const(), 5))
    assert (parse('const int*[5]') == Array(Pointer(Int32().to_const()), 5))

    assert (parse('struct ImGuiInputTextCallbackData') == Struct(
        'ImGuiInputTextCallbackData'))
    assert (parse('int (*)(ImGuiInputTextCallbackData *)') == Function(
        Int32(), [Param(Pointer(Struct('ImGuiInputTextCallbackData')))]))

    vec2 = parse('struct ImVec2').ref
    vec2.add_field(Field(Float(), 'x'))
    vec2.add_field(Field(Float(), 'y'))
    assert (vec2 == Struct(
        'ImVec2',
        [Field(Float(), 'x'), Field(Float(), 'y')]))

    parsed = parse('const ImVec2 &')
    assert (parsed == Pointer(Struct('ImVec2').to_const()))
    pop_namespace()
