import copy
import uuid
from typing import (Optional, Dict, List, Union, NamedTuple, Iterable)
from .basictype import Type, TypeRef


def replace_typeref(self: TypeRef, target: Type, replace: Type,
                    recursive) -> TypeRef:
    '''
    参照する型を置き換えたTypeRefを作りなおす
    '''
    ref = self.ref
    if ref == target:
        return TypeRef(replace, self.is_const)

    if isinstance(ref, UserType):
        # nested
        if ref in recursive:
            # raise Exception('recursive')
            pass
        else:
            recursive.append(ref)
            ref.replace(target, replace, recursive)

    # end
    return self


class UserType(Type):
    def __init__(self):
        super().__init__()

    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return False
        return True

    def clone(self) -> 'UserType':
        return copy.copy(self)

    def replace(self, target: Type, replace: Type, recursive) -> None:
        pass

    def is_based(self, based: Type) -> bool:
        raise Exception()


class Namespace:
    '''
    UserType を管理する
    '''
    def __init__(self, name: str = None, struct: Optional['Struct'] = None):
        if name is None:
            name = ''
        self.name = name
        self.user_type_map: Dict[str, UserType] = {}
        self._children: List[Namespace] = []
        self._parent: Optional[Namespace] = None
        self.functions: List[Function] = []
        self.struct: Optional[Struct] = struct

    def __str__(self) -> str:
        ancestors = [ns.name for ns in self.ancestors()]
        return '::'.join(ancestors)

    def register_type(self, name: str, usertype: UserType) -> None:
        self.user_type_map[name] = usertype

    # def get_name(self, usertype: UserType) -> str:
    #     for k, v in self.user_type_map.items():
    #         if v == usertype:
    #             return k
    #     raise KeyError()

    def get(self, src: str) -> Optional[Type]:
        usertype = self.user_type_map.get(src)
        if not usertype:
            return None
        return usertype

    def add_child(self, child: 'Namespace') -> None:
        self._children.append(child)
        child._parent = self

    def ancestors(self) -> Iterable['Namespace']:
        yield self
        if self._parent:
            for x in self._parent.ancestors():
                yield x

    def traverse(self, level=0):
        yield self
        for child in self._children:
            for x in child.traverse(level + 1):
                yield x


class SingleTypeRef(UserType):
    def __init__(self, ref: TypeRef) -> None:
        super().__init__()
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

    def is_based(self, based: Type) -> bool:
        ref = self.typeref.ref
        if ref == based:
            return True
        if isinstance(ref, UserType):
            return ref.is_based(based)
        else:
            return False

    def replace(self, target: Type, replace: Type, recursive) -> None:
        self.typeref = replace_typeref(self.typeref, target, replace,
                                       recursive)


class Typedef(SingleTypeRef):
    def __init__(self, type_name: str, ref: Union[TypeRef, Type]):
        if isinstance(ref, Type):
            ref = ref.to_ref()
        super().__init__(ref)
        self.type_name = type_name
        self.parent: Optional[Namespace] = None

    def __str__(self) -> str:
        return f'typedef {self.type_name} = {self.typeref}'

    def __hash__(self):
        return hash(self.typeref)

    def __eq__(self, value):
        if not super().__eq__(value):
            return False
        if self.typeref != value.typeref:
            return False
        if self.type_name != value.type_name:
            return False
        return True

    def get_concrete_type(self) -> Type:
        current = self.typeref.ref
        while isinstance(current, Typedef):
            current = current.typeref.ref
        return current


class Pointer(SingleTypeRef):
    def __init__(self, ref: Union[TypeRef, Type]):
        if isinstance(ref, Type):
            ref = TypeRef(ref)
        super().__init__(ref)
        self._hash = ref.__hash__() * 13 + 1

    def __hash__(self) -> int:
        return self._hash

    def __str__(self):
        return f'Ptr({self.typeref})'


class Array(Pointer):
    def __init__(self, ref: Union[Type, TypeRef],
                 length: Optional[int] = None):
        super().__init__(ref)
        self._hash += 1
        self.length = length
        if self.length:
            self._hash += self.length

    def __hash__(self) -> int:
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

    def replace(self, target: Type, replace: Type, recursive) -> 'Field':
        return Field(replace_typeref(self.typeref, target, replace, recursive),
                     self.name, self.offset, self.value)


class Struct(UserType):
    def __init__(
            self,
            type_name: str,
            fields: List[Field] = None,
    ):
        super().__init__()
        self.type_name = type_name
        self.parent: Optional[Namespace] = None
        self.namespace = Namespace(self.type_name, self)

        self.fields: List[Field] = []
        if fields:
            for f in fields:
                if isinstance(f.typeref, Type):
                    f = Field(f.typeref.to_ref(), f.name, f.value)
                self.add_field(f)
        self.template_parameters: List[str] = []

        self.iid: Optional[uuid.UUID] = None
        self.methods: List[Function] = []

    def is_forward_decl(self) -> bool:
        return len(self.fields) == 0

    def add_field(self, f: Field) -> None:
        if isinstance(f.typeref, Type):
            f = Field(f.typeref.to_ref(), f.name, f.value)
        self.fields.append(f)

    def add_template_parameter(self, t: str) -> None:
        self.template_parameters.append(t)
        self.namespace.user_type_map[t] = Struct(t)

    def instantiate(self, *template_params: List[Type]) -> 'Struct':
        decl = self.clone()

        based_params = [
            self.namespace.get(t) for t in self.template_parameters
        ]

        for based, replace in zip(based_params, template_params):
            for i in range(len(self.fields)):
                f = self.fields[i]  # noqa
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

    def replace(self, target: Type, replace: Type, recursive):
        for i in range(len(self.fields)):
            self.fields[i] = self.fields[i].replace(target, replace, recursive)

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
                if l != r:  # noqa
                    return False
        if len(self.template_parameters) != len(value.template_parameters):
            return False
        for l, r in zip(self.template_parameters, value.template_parameters):
            if l != r:  # noqa
                return False
        return True

    def __str__(self) -> str:
        if self.type_name:
            return f'struct {self.type_name}'
        else:
            return f'struct (anonymous)'


class Param(NamedTuple):
    typeref: TypeRef
    name: str = ''
    value: str = ''

    def replace(self, target: Type, replace: Type, recursive) -> 'Param':
        return Param(replace_typeref(self.typeref, target, replace, recursive),
                     self.name, self.value)


class Function(UserType):
    def __init__(
            self,
            result: Union[TypeRef, Type],
            params: List[Param],
    ):
        super().__init__()
        self.extern_c = False
        self.dll_export = False
        self.has_body = False
        self.parent: Optional[Namespace] = None
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

    def get_exportname(self):
        if self.extern_c:
            return self.name
        else:
            return self.mangled_name

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
            if l != r:  # noqa
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

    def replace(self, target: Type, replace: Type, recursive) -> None:
        # ret
        self.result = replace_typeref(self.result, target, replace, recursive)
        # params
        for i in range(len(self.params)):
            self.params[i] = self.params[i].replace(target, replace, recursive)


class EnumValue(NamedTuple):
    name: str
    value: int


class Enum(UserType):
    def __init__(self, type_name: str, values: List[EnumValue]):
        super().__init__()
        self.type_name = type_name
        self.values = values
        self.is_flag = False

    def __hash__(self):
        return self.type_name.__hash__()

    def __eq__(self, value) -> bool:
        if not super().__eq__(value):
            return False
        if self.type_name != value.type_name:
            return False
        return True

    def __str__(self) -> str:
        return f'enum {self.type_name}'
