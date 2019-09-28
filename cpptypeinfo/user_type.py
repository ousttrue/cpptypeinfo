import copy
from typing import Optional, Dict, List, Union, NamedTuple
from .base_type import Type, TypeRef


class UserType(Type):
    def __init__(self, namespace: Optional['Namespace']):
        '''
        namespaceに名前を登録する
        '''
        super().__init__()
        self.namespace = namespace

    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return False
        return True

    def clone(self) -> 'UserType':
        return copy.copy(self)

    def resolve(self, typedef: 'Typedef', replace: Type) -> None:
        pass


class Namespace:
    '''
    UserType を管理する
    '''
    def __init__(self, name: str = None):
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

    def get_name(self, user_type: UserType) -> str:
        for k, v in self.user_type_map:
            if v == user_type:
                return k
        raise KeyError()

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


class SingleTypeRef(UserType):
    def __init__(self, ref: TypeRef, namespace: Optional['Namespace']) -> None:
        super().__init__(namespace)
        if not ref:
            raise Exception('no TypeRef')
        self.typeref = ref

    def __eq__(self, value) -> bool:
        if not isinstance(value, self.__class__):
            return False
        if self.typeref != value.typeref:
            return False
        return True

    def __hash__(self):
        return hash(self.typeref)

    def replace_based(self, based: Type, replace: Type) -> 'UserType':
        raise Exception()

    def is_based(self, based: Type) -> bool:
        return self.typeref.is_based(based)

    def resolve(self, typedef: 'Typedef', replace: Type) -> None:
        ref = self.typeref
        if ref == typedef:
            if not replace:
                raise Exception()
            self.typeref = TypeRef(replace, ref.is_const)


class Typedef(SingleTypeRef):
    def __init__(self, ref: Union[TypeRef, Type],
                 namespace: Optional[Namespace]):
        if isinstance(ref, Type):
            ref = ref.to_ref()
        super().__init__(ref, namespace)

    def __str__(self) -> str:
        return f'typedef {self.namespace.get_name(self)} = {self.typeref}'

    def __hash__(self):
        return hash(self.typeref)

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if self.typeref != value.typeref:
            return False
        return True

    def get_concrete_type(self) -> Type:
        current = self.typeref.ref
        while isinstance(current, Typedef):
            current = current.typeref.ref
        return current


# def is_based(self, based: Type) -> bool:
#     if self.ref == based:
#         return True
#     if isinstance(self.ref, UserType):
#         return self.ref.is_based(based)
#     else:
#         return False


class Pointer(SingleTypeRef):
    def __init__(self, ref: Union[TypeRef, Type]):
        if isinstance(ref, Type):
            ref = TypeRef(ref)
        super().__init__(ref, None)
        self._hash = ref.__hash__() * 13 + 1

    def __hash__(self):
        return self._hash

    def __str__(self):
        return f'Ptr({self.typeref})'


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


class Struct(UserType):
    def __init__(self,
                 type_name: str,
                 fields: List[Field] = None,
                 namespace: Optional[Namespace] = None):
        super().__init__(namespace)
        self.type_name = type_name
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
        self.user_type_map[t] = self.parse(f'struct {t}').ref

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
    def __init__(self,
                 result: Union[TypeRef, Type],
                 params: List[Param],
                 namespace: Optional[Namespace] = None):
        super().__init__(namespace)
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
        # ret
        if self.result.ref == typedef:
            self.result = TypeRef(replace, self.result.is_const)
        elif isinstance(self.result.ref, UserType):
            self.result.ref.resolve(typedef, replace)

        ref = self.result
        if ref == typedef:
            if not replace:
                raise Exception()
        # params
        for i in range(len(self.params)):
            self.params[i] = self.params[i].resolve(typedef, replace)


class EnumValue(NamedTuple):
    name: str
    value: int


class Enum(UserType):
    def __init__(self, type_name: str, values: List[EnumValue],
                 namespace: Namespace):
        super().__init__(namespace)
        self.type_name = type_name
        self.values = values
        self.is_flag = False

    def __str__(self) -> str:
        return f'enum {self.type_name}'
