import uuid
from typing import Dict, Optional, List, Set, NamedTuple, Union, Tuple
from enum import IntEnum, auto
import pathlib
from clang import cindex
import cpptypeinfo
from cpptypeinfo.usertype import (TypeRef, Typedef, Pointer, Array, UserType,
                                  StructType, Struct, Field, Function, Param,
                                  Enum, EnumValue)

d3d11_key = 'MIDL_INTERFACE("'
d2d1_key = 'DX_DECLARE_INTERFACE("'
dwrite_key = 'DWRITE_DECLARE_INTERFACE("'

extract_bytes_cache: Dict[pathlib.Path, bytes] = {}


def extract(x: cindex.Cursor) -> str:
    '''
    get str for cursor
    '''
    start = x.extent.start
    p = pathlib.Path(start.file.name)
    b = extract_bytes_cache.get(p)
    if not b:
        b = p.read_bytes()
        extract_bytes_cache[p] = b

    end = x.extent.end
    text = b[start.offset:end.offset]
    return text.decode('ascii')


def get_primitive_type(t: cindex.Type) -> Optional[TypeRef]:
    '''
    TypeKind.VOID = TypeKind(2)
    TypeKind.BOOL = TypeKind(3)
    TypeKind.CHAR_U = TypeKind(4)
    TypeKind.UCHAR = TypeKind(5)
    TypeKind.CHAR16 = TypeKind(6)
    TypeKind.CHAR32 = TypeKind(7)
    TypeKind.USHORT = TypeKind(8)
    TypeKind.UINT = TypeKind(9)
    TypeKind.ULONG = TypeKind(10)
    TypeKind.ULONGLONG = TypeKind(11)
    TypeKind.UINT128 = TypeKind(12)
    TypeKind.CHAR_S = TypeKind(13)
    TypeKind.SCHAR = TypeKind(14)
    TypeKind.WCHAR = TypeKind(15)
    TypeKind.SHORT = TypeKind(16)
    TypeKind.INT = TypeKind(17)
    TypeKind.LONG = TypeKind(18)
    TypeKind.LONGLONG = TypeKind(19)
    TypeKind.INT128 = TypeKind(20)
    TypeKind.FLOAT = TypeKind(21)
    TypeKind.DOUBLE = TypeKind(22)
    TypeKind.LONGDOUBLE = TypeKind(23)
    TypeKind.NULLPTR = TypeKind(24)
    '''
    # void
    if t.kind == cindex.TypeKind.VOID:  # void
        return TypeRef(cpptypeinfo.Void(), t.is_const_qualified())
    # bool
    elif t.kind == cindex.TypeKind.BOOL:  # void
        assert (t.get_size() == 1)
        return TypeRef(cpptypeinfo.Bool(), t.is_const_qualified())
    # int
    elif t.kind == cindex.TypeKind.CHAR_S:  # char
        assert (t.get_size() == 1)
        return TypeRef(cpptypeinfo.Int8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.SCHAR:  # signed char
        assert (t.get_size() == 1)
        return TypeRef(cpptypeinfo.Int8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.SHORT:  # short
        assert (t.get_size() == 2)
        return TypeRef(cpptypeinfo.Int16(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.INT:  # int
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.Int32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.LONG:  # long
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.Int32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.LONGLONG:  # long long
        assert (t.get_size() == 8)
        return TypeRef(cpptypeinfo.Int64(), t.is_const_qualified())
    # unsigned
    elif t.kind == cindex.TypeKind.UCHAR:  # unsigned char
        assert (t.get_size() == 1)
        return TypeRef(cpptypeinfo.UInt8(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.WCHAR:  # wchar_t
        assert (t.get_size() == 2)
        return TypeRef(cpptypeinfo.UInt16(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.USHORT:  # unsigned short
        assert (t.get_size() == 2)
        return TypeRef(cpptypeinfo.UInt16(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.UINT:  # unsigned int
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.UInt32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.ULONG:  # unsigned long
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.UInt32(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.ULONGLONG:  # unsigned __int64
        assert (t.get_size() == 8)
        return TypeRef(cpptypeinfo.UInt64(), t.is_const_qualified())
    # float
    elif t.kind == cindex.TypeKind.FLOAT:  # float
        assert (t.get_size() == 4)
        return TypeRef(cpptypeinfo.Float(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.DOUBLE:  # double
        assert (t.get_size() == 8)
        return TypeRef(cpptypeinfo.Double(), t.is_const_qualified())
    elif t.kind == cindex.TypeKind.LONGDOUBLE:  # double
        size = t.get_size()
        assert (size == 8)
        return TypeRef(cpptypeinfo.Double(), t.is_const_qualified())

    return None


class NestType(IntEnum):
    POINTER = auto()
    CONSTANTARRAY = auto()


class NestInfo(NamedTuple):
    type: NestType
    is_const: bool
    size: int = 0


def strip_nest_type(t: cindex.Type):
    '''
    pointer, reference, array の入れ子になった型を取り外す
    '''
    stack: List[NestInfo] = []
    current = t
    while True:
        if current.kind in (cindex.TypeKind.POINTER,
                            cindex.TypeKind.LVALUEREFERENCE):
            stack.append(
                NestInfo(NestType.POINTER, current.is_const_qualified()))
            current = current.get_pointee()
        elif current.kind == cindex.TypeKind.INCOMPLETEARRAY:
            stack.append(
                NestInfo(NestType.POINTER, current.is_const_qualified()))
            current = current.get_array_element_type()
        elif current.kind == cindex.TypeKind.CONSTANTARRAY:
            stack.append(
                NestInfo(NestType.CONSTANTARRAY, current.is_const_qualified(),
                         current.get_array_size()))
            current = current.get_array_element_type()
        else:
            break
    return current, stack


def strip_pointer(usertype: UserType
                  ) -> Tuple[cpptypeinfo.Type, List[NestInfo]]:
    stack: List[NestInfo] = []
    current: cpptypeinfo.Type = usertype
    while True:
        if isinstance(current, Pointer):
            stack.append(NestInfo(NestType.POINTER, current.typeref.is_const))
            current = current.typeref.ref
        else:
            break
    return current, stack


def restore_nest_type(ref: Union[TypeRef, cpptypeinfo.Type],
                      stack: List[NestInfo]) -> TypeRef:
    if isinstance(ref, TypeRef):
        current = ref
    elif isinstance(ref, cpptypeinfo.Type):
        current = TypeRef(ref)
    else:
        raise Exception()
    while stack:
        info = stack.pop()
        if info.type == NestType.POINTER:
            current = TypeRef(Pointer(current), info.is_const)
        elif info.type == NestType.CONSTANTARRAY:
            current = TypeRef(Array(current, info.size), info.is_const)
        else:
            raise Exception()
    return current


def deref_typedef(usertype: UserType) -> UserType:
    '''
    typedefを短縮する
    '''
    if isinstance(usertype, Typedef):
        ref = usertype.typeref.ref
        if isinstance(ref, Struct):
            if usertype.type_name == ref.type_name:
                return ref
            if not ref.type_name:
                ref.type_name = usertype.type_name

        if isinstance(ref, Enum):
            if usertype.type_name == ref.type_name:
                return ref
            if not ref.type_name:
                ref.type_name = usertype.type_name

        if isinstance(ref, Typedef):
            if usertype.type_name == ref.type_name:
                return deref_typedef(ref)
            if not ref.type_name:
                ref.type_name = usertype.type_name

        return ref

    return usertype


def is_nest_typedef(typedef: Typedef) -> bool:
    ref = typedef.typeref.ref
    if not isinstance(ref, Typedef):
        return False

    if typedef.type_name != ref.type_name:
        return False

    return True


def get_canonical(c: cindex.Cursor) -> cindex.Cursor:
    while c.hash != c.canonical.hash:
        if c.spelling != c.canonical.spelling:
            raise Exception()
        c = c.canonical
    return c


class DeclMap:
    def __init__(self, parser: cpptypeinfo.TypeParser, files):
        self.parser = parser
        self.decl_map: Dict[int, UserType] = {}
        self.used: Set[int] = set()
        self.files = files
        self.extern_c: List[bool] = [False]
        self.macro_definitions: List[cpptypeinfo.MacroDefinition] = []

    def has(self, _c: cindex.Cursor) -> bool:
        c = get_canonical(_c)
        return c.hash in self.decl_map

    def get(self, _c: cindex.Cursor) -> UserType:
        c = get_canonical(_c)
        return self.decl_map[c.hash]

    def add(self, _c: cindex.Cursor, usertype: UserType) -> None:
        c = get_canonical(_c)
        if c.hash in self.decl_map:
            raise Exception()
        concrete_type, stack = strip_pointer(usertype)
        inner_type = deref_typedef(concrete_type)
        restore = restore_nest_type(inner_type, stack).ref
        self.decl_map[c.hash] = restore

    def resolve_typedef(self) -> None:
        pass

    def parse_cursor(self, c: cindex.Cursor):
        '''
        namespaceレベルの要素。
        各種宣言が期待される。
        '''
        if c.hash in self.used:
            return
        self.used.add(c.hash)

        # if files and pathlib.Path(c.location.file.name) not in files:
        #     return
        if c.kind == cindex.CursorKind.TRANSLATION_UNIT:

            for child in c.get_children():
                self.parse_cursor(child)

        elif c.kind == cindex.CursorKind.NAMESPACE:
            # nested
            self.parser.push_namespace(c.spelling)
            for child in c.get_children():
                self.parse_cursor(child)
            self.parser.pop_namespace()

        elif c.kind == cindex.CursorKind.UNEXPOSED_DECL:
            extern_c = False
            try:
                it = c.get_tokens()
                t0 = next(it)
                t1 = next(it)
                if t0.spelling == 'extern' and t1.spelling == '"C"':
                    extern_c = True
            except StopIteration:
                pass
            if extern_c:
                self.extern_c.append(True)
            for child in c.get_children():
                self.parse_cursor(child)
            if extern_c:
                self.extern_c.pop()

        elif c.kind == cindex.CursorKind.UNION_DECL:
            self.parse_struct(c, StructType.UNION)

        elif c.kind == cindex.CursorKind.STRUCT_DECL:
            self.parse_struct(c, StructType.STRUCT)

        elif c.kind == cindex.CursorKind.CLASS_DECL:
            self.parse_struct(c, StructType.CLASS)

        elif c.kind == cindex.CursorKind.TYPEDEF_DECL:
            self.parse_typedef(c)

        elif c.kind == cindex.CursorKind.FUNCTION_DECL:
            function = self.parse_function(c)
            self.parser.get_current_namespace().functions.append(function)
            if not self.has(c):
                self.add(c, function)

        elif c.kind == cindex.CursorKind.ENUM_DECL:
            self.parse_enum(c)

        elif c.kind == cindex.CursorKind.VAR_DECL:
            # static variable
            pass

        elif c.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
            # enum_type hoge = 0;
            pass

        elif c.kind == cindex.CursorKind.CXX_UNARY_EXPR:
            pass

        elif c.kind == cindex.CursorKind.UNEXPOSED_EXPR:
            pass

        elif c.kind == cindex.CursorKind.UNEXPOSED_ATTR:
            pass

        elif c.kind == cindex.CursorKind.USING_DECLARATION:
            pass

        elif c.kind == cindex.CursorKind.FUNCTION_TEMPLATE:
            pass

        elif c.kind == cindex.CursorKind.CLASS_TEMPLATE:
            pass
            # parse_struct(c)

        elif c.kind == cindex.CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION:
            pass

        elif c.kind == cindex.CursorKind.MACRO_DEFINITION:
            if not c.location.file:
                # __llvm = 1
                return

            tokens = [t.spelling for t in c.get_tokens()]

            if len(tokens) == 1:
                # ex. #define __header__
                return

            if tokens in [
                ['IID_ID3DBlob', 'IID_ID3D10Blob'],
                ['INTERFACE', 'ID3DInclude'],
                ['D2D1_INVALID_TAG', 'ULONGLONG_MAX'],
                ['D2D1FORCEINLINE', 'FORCEINLINE'],
            ]:
                #define IID_ID3DBlob IID_ID3D10Blob
                #define INTERFACE ID3DInclude
                #define D2D1_INVALID_TAG ULONGLONG_MAX
                #define D2D1FORCEINLINE FORCEINLINE
                return

            if len(tokens) >= 3 and tokens[1] == '(' and tokens[2][0].isalpha(
            ):
                # maybe macro function
                return

            # if c.spelling == 'D3D11_SDK_VERSION':
            #     raise Exception()

            self.macro_definitions.append(
                cpptypeinfo.MacroDefinition(c.spelling,
                                            ' '.join(x for x in tokens[1:]),
                                            pathlib.Path(c.location.file.name),
                                            c.location.line))

        elif c.kind == cindex.CursorKind.MACRO_INSTANTIATION:
            pass

        elif c.kind == cindex.CursorKind.INCLUSION_DIRECTIVE:
            pass

        elif c.kind == cindex.CursorKind.STATIC_ASSERT:
            pass

        else:
            tokens = [x.spelling for x in c.get_tokens()]
            raise NotImplementedError(f'{c.kind}: {tokens}')

    def get_type_from_hash(self, t: cindex.Type, c: cindex.Cursor) -> TypeRef:
        '''
        登録済みの型をhashから取得する
        '''
        if t.kind in (cindex.TypeKind.ELABORATED, cindex.TypeKind.RECORD,
                      cindex.TypeKind.TYPEDEF, cindex.TypeKind.ENUM):
            # structなど
            children = [child for child in c.get_children()]
            for child in children:
                if child.kind in (cindex.CursorKind.STRUCT_DECL,
                                  cindex.CursorKind.UNION_DECL):
                    decl = self.get(child)
                    if decl:
                        return TypeRef(decl, t.is_const_qualified())
                    raise Exception()

                elif child.kind == cindex.CursorKind.TYPE_REF:
                    if not self.has(child.referenced):
                        self.parse_cursor(child.referenced)
                    decl = self.get(child.referenced)
                    if decl:
                        return TypeRef(decl, t.is_const_qualified())
                    raise Exception()

                elif child.kind in (cindex.CursorKind.UNEXPOSED_ATTR,
                                    cindex.CursorKind.DLLIMPORT_ATTR):
                    pass

                else:
                    raise Exception()
            raise Exception()

        if t.kind == cindex.TypeKind.FUNCTIONPROTO:
            return TypeRef(cpptypeinfo.Void(), t.is_const_qualified())

        children = [child for child in c.get_children()]
        raise Exception()

    def cindex_type_to_cpptypeinfo(self, t: cindex.Type,
                                   c: cindex.Cursor) -> TypeRef:
        # remove pointer
        base_type, stack = strip_nest_type(t)

        primitive = get_primitive_type(base_type)
        if primitive:
            return restore_nest_type(primitive, stack)

        nest = self.get_type_from_hash(base_type, c)
        if nest:
            return restore_nest_type(nest, stack)

        raise Exception(f'unknown type: {t.kind}')
        return None

    def parse_functionproto(self, c: cindex.Cursor) -> Function:
        children = [child for child in c.get_children()]

        def to_param(child):
            decl = self.cindex_type_to_cpptypeinfo(child.type, child)
            ref = TypeRef(decl, child.type.is_const_qualified())
            return Param(child.spelling, ref)

        params = []
        result: cpptypeinfo.Type = cpptypeinfo.Void()
        for child in children:
            if child.kind == cindex.CursorKind.TYPE_REF:
                result = self.get(child.referenced)
            elif child.kind == cindex.CursorKind.PARM_DECL:
                params.append(to_param(child))

        return Function(result, params)

    def typedef_elaborated_type(self, underlying: cindex.Type,
                                c: cindex.Cursor) -> Optional[TypeRef]:
        '''
        Typedefとともに型定義(struct, enum....)
        '''
        if underlying.kind != cindex.TypeKind.ELABORATED:
            return None

        children = [child for child in c.get_children()]
        for child in children:
            if child.kind in [
                    cindex.CursorKind.STRUCT_DECL,
                    cindex.CursorKind.UNION_DECL,
            ]:
                struct = self.get(child)
                if struct:
                    # decl = self.parser.typedef(c.spelling, struct)
                    # decl.file = pathlib.Path(c.location.file.name)
                    # decl.line = c.location.line
                    # self.add(child, decl)
                    return TypeRef(struct, underlying.is_const_qualified())
                raise Exception()

            if child.kind == cindex.CursorKind.ENUM_DECL:
                enum = self.get(child)
                if enum:
                    # decl = self.parser.typedef(c.spelling, enum)
                    # decl.file = pathlib.Path(c.location.file.name)
                    # decl.line = c.location.line
                    # self.add(child, decl)
                    return TypeRef(enum, underlying.is_const_qualified())
                raise Exception()

            if child.kind == cindex.CursorKind.TYPE_REF:
                ref = self.get(child.referenced)
                if ref:
                    # decl = self.parser.typedef(c.spelling, ref)
                    # decl.file = pathlib.Path(c.location.file.name)
                    # decl.line = c.location.line
                    # self.add(child, decl)
                    return TypeRef(ref, underlying.is_const_qualified())
                raise Exception()
            raise Exception()
        raise Exception()

    def parse_typedef(self, c: cindex.Cursor) -> None:
        if self.has(c):
            # already exists
            return

        underlying, stack = strip_nest_type(c.underlying_typedef_type)
        primitive = get_primitive_type(underlying)
        if primitive:
            typedef = self.parser.typedef(c.spelling,
                                          restore_nest_type(primitive, stack))
            typedef.file = pathlib.Path(c.location.file.name)
            typedef.line = c.location.line
            self.add(c, typedef)
            return

        elaborated = self.typedef_elaborated_type(underlying, c)
        if elaborated:
            typedef = self.parser.typedef(c.spelling,
                                          restore_nest_type(elaborated, stack))
            typedef.file = pathlib.Path(c.location.file.name)
            typedef.line = c.location.line
            self.add(c, typedef)
            return

        if underlying.kind == cindex.TypeKind.TYPEDEF:
            children = [child for child in c.get_children()]
            for child in children:
                if child.kind == cindex.CursorKind.TYPE_REF:
                    if not self.has(child.referenced):
                        self.parse_cursor(child.referenced)
                    usertype = self.get(child.referenced)
                    if usertype:
                        typedef = self.parser.typedef(
                            c.spelling, restore_nest_type(usertype, stack))
                        typedef.file = pathlib.Path(c.location.file.name)
                        typedef.line = c.location.line
                        self.add(c, typedef)
                        return

            raise Exception()

        if underlying.kind == cindex.TypeKind.FUNCTIONPROTO:
            function = self.parse_functionproto(c)
            typedef = self.parser.typedef(
                c.spelling, TypeRef(function, c.type.is_const_qualified()))
            typedef.file = pathlib.Path(c.location.file.name)
            typedef.line = c.location.line
            self.add(c, typedef)
            return

        if underlying.kind == cindex.TypeKind.UNEXPOSED:
            # typedef decltype(__nullptr) nullptr_t;
            children = [child for child in c.get_children()]
            if c.spelling == 'nullptr_t':
                typedef = self.parser.typedef(c.spelling,
                                              TypeRef(cpptypeinfo.Void()))
                typedef.file = pathlib.Path(c.location.file.name)
                typedef.line = c.location.line
                self.add(c, typedef)
                return

            raise Exception()

        raise Exception()

    def parse_enum(self, c: cindex.Cursor) -> Enum:
        name = c.type.spelling
        if not name:
            raise Exception(f'no name')
        values = []
        for child in c.get_children():
            if child.kind == cindex.CursorKind.ENUM_CONSTANT_DECL:
                values.append(EnumValue(child.spelling, child.enum_value))
            else:
                raise Exception(f'{child.kind}')
        decl = Enum(name, values)
        self.parser.get_current_namespace().register_type(name, decl)
        decl.file = pathlib.Path(c.location.file.name)
        decl.line = c.location.line
        self.add(c, decl)
        return decl

    def parse_function(self, c: cindex.Cursor) -> Function:
        result = self.cindex_type_to_cpptypeinfo(c.result_type, c)

        dll_export = False
        has_body = False
        params = []
        for child in c.get_children():
            if child.kind == cindex.CursorKind.PARM_DECL:
                if child.type.kind == cindex.TypeKind.CONSTANTARRAY:
                    param = self.cindex_type_to_cpptypeinfo(
                        child.type.get_array_element_type(), child)
                    param = TypeRef(Pointer(param),
                                    child.type.is_const_qualified())
                else:
                    param = self.cindex_type_to_cpptypeinfo(child.type, child)
                # ToDo:
                default_value = ''
                params.append(Param(param, child.spelling, default_value))

            elif child.kind == cindex.CursorKind.TYPE_REF:
                pass
            elif child.kind == cindex.CursorKind.UNEXPOSED_ATTR:
                # macro
                # tokens = [token.spelling for token in child.get_tokens()]
                pass
            # elif child.kind == cindex.CursorKind.UNEXPOSED_EXPR:
            #     pass

            elif child.kind == cindex.CursorKind.COMPOUND_STMT:
                # function body
                has_body = True

            elif child.kind == cindex.CursorKind.DLLEXPORT_ATTR:
                # __declspec(dllexport)
                dll_export = True

            elif child.kind == cindex.CursorKind.DLLIMPORT_ATTR:
                # __declspec(dllimport)
                dll_export = True

            elif child.kind == cindex.CursorKind.WARN_UNUSED_RESULT_ATTR:
                pass

            # elif child.kind == cindex.CursorKind.NAMESPACE_REF:
            #     pass
            # elif child.kind == cindex.CursorKind.TEMPLATE_REF:
            #     pass

            else:
                raise NotImplementedError(f'{child.kind}')

        decl = Function(result, params)
        decl.name = c.spelling
        # affected platform option: -target x86_64-windows-msvc
        decl.mangled_name = c.mangled_name
        decl.extern_c = self.extern_c[-1]
        decl.file = pathlib.Path(c.location.file.name)
        decl.line = c.location.line
        decl.dll_export = dll_export
        decl.has_body = has_body
        return decl

    def parse_field(self, c: cindex.Cursor) -> Field:
        '''
        structのfieldを処理する。
        配列の処理に注意。
        '''
        offset = c.get_field_offsetof() // 8
        # if not decl.template_parameters and offset < 0:
        #     # parseに失敗(特定のheaderが見つからないなど)
        #     # clang 環境が壊れているかも
        #     # VCのプレビュー版とか原因かも
        #     # プレビュー版をアンインストールして LLVM を入れたり消したらなおった
        #     raise Exception(f'struct {c.spelling}.{child.spelling}: offset error')

        field_type, stack = strip_nest_type(c.type)
        primitive = get_primitive_type(field_type)
        if primitive:
            # field
            return Field(restore_nest_type(primitive, stack), c.spelling,
                         offset)

        decl = self.get_type_from_hash(field_type, c)
        if decl:
            return Field(restore_nest_type(decl, stack), c.spelling)

        raise Exception()

    def parse_struct(self, c: cindex.Cursor,
                     struct_type: StructType) -> Struct:
        if self.has(c):
            decl = self.get(c)
        else:
            name = c.spelling
            # print(f'{name}: {c.hash}')
            decl = Struct(name)
            self.add(c, decl)
        decl.struct_type = struct_type
        decl.file = pathlib.Path(c.location.file.name)
        decl.line = c.location.line
        self.parser.push_namespace(decl.namespace)
        for child in c.get_children():
            if child.kind == cindex.CursorKind.FIELD_DECL:
                field = self.parse_field(child)
                decl.fields.append(field)

            elif child.kind == cindex.CursorKind.UNION_DECL and not child.spelling:
                # anonymous union
                union = self.parse_struct(child, StructType.UNION)
                field = Field(TypeRef(union, child.type.is_const_qualified()))
                decl.fields.append(field)

            elif child.kind == cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
                # public, private...
                pass

            elif child.kind == cindex.CursorKind.CXX_UNARY_EXPR:
                # some_template<sizeof(char)>
                pass

            elif child.kind == cindex.CursorKind.UNEXPOSED_EXPR:
                # some_template<1>
                pass

            elif child.kind in [
                    cindex.CursorKind.STRUCT_DECL,
                    cindex.CursorKind.UNION_DECL,
                    cindex.CursorKind.TYPEDEF_DECL,
                    cindex.CursorKind.FUNCTION_TEMPLATE,
            ]:
                # inner type
                self.parse_cursor(child)

            elif child.kind == cindex.CursorKind.ALIGNED_ATTR:
                # __declspec(align(x))
                # use newer llvm(9) and latest cindex
                # https://github.com/llvm-mirror/clang/blob/master/bindings/python/clang/cindex.py
                pass

            elif child.kind == cindex.CursorKind.CXX_BASE_SPECIFIER:
                # class some: public base_class
                for x in child.get_children():
                    if x.kind == cindex.CursorKind.TYPE_REF:
                        base = self.get(x.referenced)
                        if base:
                            decl.base = TypeRef(base)
                        else:
                            raise Exception()
                    else:
                        raise Exception()

            elif child.kind == cindex.CursorKind.CONSTRUCTOR:
                pass

            elif child.kind == cindex.CursorKind.DESTRUCTOR:
                pass

            elif child.kind == cindex.CursorKind.CXX_METHOD:
                # children = [x for x in child.get_children()]
                function = self.parse_function(child)
                decl.methods.append(function)

            elif child.kind == cindex.CursorKind.CONVERSION_FUNCTION:
                pass

            elif child.kind == cindex.CursorKind.UNEXPOSED_ATTR:
                # __declspec(uuid(x))
                tokens = [t for t in child.get_tokens()]
                # c: cindex.Cursor = child
                # http://clang-developers.42468.n3.nabble.com/source-code-string-from-SourceRange-td4032732.html

                value = extract(child)
                if value.startswith(d3d11_key):
                    decl.iid = uuid.UUID(value[len(d3d11_key):-2])
                elif value.startswith(d2d1_key):
                    decl.iid = uuid.UUID(value[len(d2d1_key):-2])
                elif value.startswith(dwrite_key):
                    decl.iid = uuid.UUID(value[len(dwrite_key):-2])
                else:
                    print(value)

            else:
                tokens = [t.spelling for t in child.get_tokens()]
                raise Exception()

        self.parser.pop_namespace()
        return decl
