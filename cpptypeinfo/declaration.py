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
import pathlib
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

    def resolve(self, typedef: 'Typedef', replace: Type) -> 'TypeRef':
        if self.ref == typedef:
            if not replace:
                raise Exception()
            return TypeRef(replace, self.is_const)
        return self

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

    def resolve(self, target: 'Typedef', replace: Type):
        pass


class NamedType(UserType):
    def __init__(self, type_name: str):
        if not type_name:
            raise Exception('no name')
        self.type_name = type_name
        self.file: Optional[pathlib.Path] = None
        self.line = -1
        # 型をNameSpaceに登録する
        if self.type_name and self.type_name:
            if self.type_name in STACK[-1].user_type_map:
                print(
                    f'duplicate: {self.type_name} => {STACK[-1].user_type_map[self.type_name]}'
                )
                return
            STACK[-1].user_type_map[self.type_name] = self

    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return False
        if self.type_name != value.type_name:
            return False
        return True

    def __hash__(self):
        return hash(self.type_name)


class Namespace:
    '''
    ユーザー定義型を管理する
    '''
    def __init__(self, name: str):
        if name is None:
            name = ''
        self.name = name
        self.user_type_map: Dict[str, UserType] = {}
        self.children: List[Namespace] = []
        self.parent: Optional[Namespace] = None
        self.functions: List[Function] = []

    def __str__(self) -> str:
        ancestors = [ns.name for ns in self.ancestors()]
        return '::'.join(ancestors)

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

    def resolve(self, found: 'Typedef', replace: Type):
        if not replace:
            replace = found.typeref.ref
        for ns in self.traverse():
            for k, v in ns.user_type_map.items():
                v.resolve(found, replace)
            for v in ns.functions:
                v.resolve(found, replace)

        for ns in self.traverse():
            if found.type_name in ns.user_type_map:
                print(f'remove {found}')
                ns.user_type_map.pop(found.type_name)

    def resolve_typedef_by_name(self, name: str, replace: Type = None):
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
            self.resolve(found, replace)

    def resolve_typedef_void_p(self):
        while True:
            targets = []
            for ns in self.traverse():
                for k, v in ns.user_type_map.items():
                    if isinstance(v, Typedef):
                        if v.typeref.ref == Pointer(Void()):
                            targets.append(v)
            if not targets:
                return

            for target in targets:
                # remove
                self.resolve(target, target.typeref.ref)

    def resolve_typedef_struct_tag(self):
        '''
        remove
        typedef struct Some Some;
        '''
        targets = []
        for ns in self.traverse():
            for k, v in ns.user_type_map.items():
                if isinstance(v, Typedef):
                    if isinstance(v.typeref.ref, Struct):
                        if k == v.typeref.ref.type_name:
                            targets.append(v)

        for target in targets:
            # remove
            self.resolve(target, target.typeref.ref)


STACK: List[Namespace] = []


def indent():
    return '  ' * (len(STACK) - 1)


def push_namespace(name: Union[str, Namespace] = '') -> Namespace:
    namespace = name if isinstance(name, Namespace) else Namespace(name)
    print(f'{indent()}{namespace.name} {{')
    if STACK:
        STACK[-1].children.append(namespace)
        namespace.parent = STACK[-1]
    STACK.append(namespace)
    return namespace


def pop_namespace():
    STACK.pop()
    print(f'{indent()}}}')


NS_PATTERN = re.compile(r'(\w+)::(\w+)$')


class Typedef(NamedType):
    def __init__(self, type_name: str, ref: Union[TypeRef, Type]):
        super().__init__(type_name)
        if isinstance(ref, Type):
            ref = ref.to_ref()
        if not ref:
            raise Exception()
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

    def resolve(self, target: 'Typedef', replace: Type):
        self.typeref = self.typeref.resolve(target, replace)

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

    def resolve(self, target: Typedef, replace: Type):
        self.typeref = self.typeref.resolve(target, replace)


class Array(Pointer):
    def __init__(self, ref: Union[Type, TypeRef],
                 length: Optional[int] = None):
        super().__init__(ref)
        self.length = length
        self._hash = self.typeref.__hash__() * 13 + 2
        if self.length:
            self._hash += self.length

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
    offset: int = -1
    value: str = ''

    def resolve(self, typedef: Typedef, replace: Type) -> 'Field':
        return Field(self.typeref.resolve(typedef, replace), self.name,
                     self.offset, self.value)


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

    def instantiate(self, *template_params: List[Type]) -> 'Struct':
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

    def resolve(self, target: Typedef, replace: Type):
        for i in range(len(self.fields)):
            self.fields[i] = self.fields[i].resolve(target, replace)

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

    def resolve(self, typedef: Typedef, replace: Type) -> 'Param':
        return Param(self.typeref.resolve(typedef, replace), self.name,
                     self.value)


class Function(UserType):
    def __init__(self, result: Union[TypeRef, Type], params: List[Param]):
        super().__init__()
        self.name = ''
        self.mangled_name = ''
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

    def resolve(self, typedef: Typedef, replace: Type):
        self.result = self.result.resolve(typedef, replace)
        for i in range(len(self.params)):
            self.params[i] = self.params[i].resolve(typedef, replace)


class EnumValue(NamedTuple):
    name: str
    value: int


class Enum(NamedType):
    def __init__(self, type_name: str, values: List[EnumValue]):
        super().__init__(type_name)
        self.values = values
        self.is_flag = False

    def __str__(self) -> str:
        return f'enum {self.type_name}'


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
    # win32API
    'LRESULT': Pointer(Void()),
    'HWND': Pointer(Void()),
    'UINT': UInt32(),
    'WPARAM': Pointer(Void()),
    'LPARAM': Pointer(Void()),
}


def get_from_ns(src: str) -> Optional[Type]:
    primitive = primitive_type_map.get(src)
    if primitive:
        return primitive

    for namespace in reversed(STACK):
        decl = namespace.get(src)
        if decl:
            return decl

        if src == namespace.name:
            return namespace

    for namespace in STACK[0].children:
        decl = namespace.get(src)
        if decl:
            return decl

        if src == namespace.name:
            return namespace

    return None


SPLIT_PATTERN = re.compile(r'[*&]')
# void (const Im3d::DrawList &)
NAMED_FUNC_PATTERN = re.compile(r'^(.*)\(.*\)\((.*)\)$')
FUNC_PATTERN = re.compile(r'^(.*)\((.*)\)$')


def parse(src: str, is_const=False) -> TypeRef:
    src = src.strip()

    m = NAMED_FUNC_PATTERN.match(src)
    if m:
        result = m.group(1)
        params = m.group(2).split(',')
        return TypeRef(
            Function(parse(result), [Param(typeref=parse(x)) for x in params]))

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
        template_name = src[:pos].strip()
        template = parse(template_name, is_const).ref
        if not template:
            raise Exception(f'{template_name} not found')
        if isinstance(template, Struct):
            template_params = []
            for splitted in src[pos + 1:-1].strip().split(','):
                try:
                    num = int(splitted)
                    template_params.append(num)
                except Exception:
                    template_params.append(parse(splitted))
            decl = template.instantiate(template_params)
            return TypeRef(decl, is_const)
        else:
            raise Exception(f'{template_name} is not struct')

        # std::array<float, 16>
        raise Exception()

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
                # if len(ns_list) != 2:
                #     raise NotImplementedError()
                ns_list = ns_list[-2:]
                current = STACK[-1]
                if isinstance(current, Struct):
                    if current.type_name == ns_list[0]:
                        return parse(ns_list[1], is_const)

                ns = get_from_ns(ns_list[0])
                if not ns:
                    raise Exception(f'not found {ns_list[0]}')

                if isinstance(ns, Struct) or isinstance(ns, Namespace):
                    decl = ns.get(ns_list[1])
                    if decl:
                        return TypeRef(decl, is_const)

                    for ns in reversed(STACK):
                        for child in ns.children:
                            if child.name == ns_list[0]:
                                decl = child.get(ns_list[1])
                                if decl:
                                    return TypeRef(decl, is_const)
                                else:
                                    raise Exception(f'{src} not found')

                    raise Exception(f'{src} is not found')
                else:
                    raise Exception(f'{ns} is not Struct or Namespace')

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
